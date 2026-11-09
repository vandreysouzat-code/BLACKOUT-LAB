
import ipaddress
import json
import re
import socket

from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import requests

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
TIMEOUT = 5
MAX_RESPONSE_SIZE = 500_000


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside_title = False
        self.title = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self.inside_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.inside_title = False

    def handle_data(self, data):
        if self.inside_title:
            self.title.append(data.strip())


def validate_target(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Use uma URL HTTP ou HTTPS.")

    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL inválida.")

    if parsed.port and not 1 <= parsed.port <= 65535:
        raise ValueError("Porta inválida.")

    host = parsed.hostname

    if host == "localhost":
        return url

    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(
                host, parsed.port or 80, type=socket.SOCK_STREAM
            )
        }
    except socket.gaierror:
        raise ValueError("Não foi possível resolver o endereço.")

    if not addresses:
        raise ValueError("Nenhum endereço IP encontrado.")

    for address in addresses:
        ip = ipaddress.ip_address(address)

        if not (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
        ):
            raise ValueError(
                "Este módulo aceita somente localhost "
                "e redes privadas de laboratório."
            )

    return url


def get_page_title(html):
    parser = TitleParser()
    parser.feed(html)
    return " ".join(filter(None, parser.title)) or "Não identificado"


def analyze_headers(headers):
    security_headers = {
        "Content-Security-Policy": "Proteção contra conteúdo não autorizado",
        "X-Content-Type-Options": "Reduz riscos de MIME sniffing",
        "X-Frame-Options": "Ajuda a prevenir clickjacking",
        "Strict-Transport-Security": "Política de HTTPS",
        "Referrer-Policy": "Controle de informações de referência",
        "Permissions-Policy": "Controle de recursos do navegador"
    }

    results = []

    for header, description in security_headers.items():
        results.append({
            "header": header,
            "present": header in headers,
            "description": description
        })

    return results


def inspect_endpoint(url):
    response = requests.get(
        url,
        timeout=TIMEOUT,
        allow_redirects=False,
        stream=True,
        headers={"User-Agent": "BLACKOUT-LAB/1.0"}
    )

    try:
        content = response.raw.read(
            MAX_RESPONSE_SIZE + 1,
            decode_content=True
        )

        truncated = len(content) > MAX_RESPONSE_SIZE
        content = content[:MAX_RESPONSE_SIZE]

        html = content.decode(
            response.encoding or "utf-8",
            errors="replace"
        )

        return {
            "status_code": response.status_code,
            "server": response.headers.get("Server", "Não informado"),
            "content_type": response.headers.get(
                "Content-Type", "Não informado"
            ),
            "content_length": response.headers.get(
                "Content-Length", "Não informado"
            ),
            "title": get_page_title(html),
            "security_headers": analyze_headers(response.headers),
            "response_truncated": truncated
        }
    finally:
        response.close()


def inspect_methods(url):
    response = requests.options(
        url,
        timeout=TIMEOUT,
        allow_redirects=False,
        headers={"User-Agent": "BLACKOUT-LAB/1.0"}
    )

    try:
        return response.headers.get("Allow", "Não informado")
    finally:
        response.close()


def inspect_robots(url):
    parsed = urlparse(url)
    robots_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        "/robots.txt",
        "",
        "",
        ""
    ))

    response = requests.get(
        robots_url,
        timeout=TIMEOUT,
        allow_redirects=False,
        stream=True,
        headers={"User-Agent": "BLACKOUT-LAB/1.0"}
    )

    try:
        if response.status_code != 200:
            return {
                "url": robots_url,
                "status_code": response.status_code,
                "content": "Arquivo não disponível."
            }

        content = response.raw.read(
            20_000,
            decode_content=True
        ).decode("utf-8", errors="replace")

        return {
            "url": robots_url,
            "status_code": response.status_code,
            "content": content
        }
    finally:
        response.close()


def save_report(url, results):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc)

    report = {
        "tool": "BLACKOUT LAB",
        "module": "Web Reconnaissance",
        "target": url,
        "timestamp_utc": timestamp.isoformat(),
        "results": results
    }

    filename = (
        f"web_recon_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
    )

    report_path = REPORT_DIR / filename

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    return report_path


def web_reconnaissance():
    console.print(Panel(
        "[bold cyan]BLACKOUT LAB[/bold cyan]\n"
        "[white]WEB RECONNAISSANCE[/white]\n"
        "[dim]Somente laboratórios próprios ou autorizados[/dim]",
        border_style="cyan"
    ))

    url = input("\nURL do laboratório: ").strip()

    try:
        validate_target(url)

        console.print("\n[cyan]Analisando página...[/cyan]")
        page = inspect_endpoint(url)

        console.print("[cyan]Verificando métodos HTTP...[/cyan]")
        methods = inspect_methods(url)

        console.print("[cyan]Consultando robots.txt...[/cyan]")
        robots = inspect_robots(url)

        results = {
            "page": page,
            "allowed_methods": methods,
            "robots_txt": robots
        }

        table = Table(title="Web Reconnaissance")
        table.add_column("Item", style="cyan")
        table.add_column("Resultado", style="green")

        table.add_row("HTTP Status", str(page["status_code"]))
        table.add_row("Page Title", page["title"])
        table.add_row("Server", page["server"])
        table.add_row("Content-Type", page["content_type"])
        table.add_row("HTTP Methods", methods)
        table.add_row("robots.txt", str(robots["status_code"]))

        console.print(table)

        header_table = Table(title="Security Headers")
        header_table.add_column("Header")
        header_table.add_column("Status")

        for item in page["security_headers"]:
            status = (
                "[green]Present[/green]"
                if item["present"]
                else "[yellow]Missing[/yellow]"
            )
            header_table.add_row(item["header"], status)

        console.print(header_table)

        report_path = save_report(url, results)

        console.print(
            f"\n[bold green]Relatório salvo:[/bold green]\n{report_path}"
        )

    except (ValueError, requests.RequestException, OSError) as error:
        console.print(f"\n[bold red]Erro:[/bold red] {error}")


if __name__ == "__main__":
    web_reconnaissance()
