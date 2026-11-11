
"""
Módulo Web Reconnaissance do SOVIK 2.0.

Analisa páginas HTTP/HTTPS em ambientes autorizados,
registra operações e gera relatórios JSON.
"""

import json

from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import requests

from core.scope import validate_http_url
from core import operations, campaigns
from core.logger import get_logger

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()
logger = get_logger("sovik.web_recon")

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"

TIMEOUT = 5
MAX_RESPONSE_SIZE = 500_000
MAX_ROBOTS_SIZE = 20_000

USER_AGENT = "SOVIK/2.0"


class TitleParser(HTMLParser):
    """Extrai o título de uma página HTML."""

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
    """Valida URL usando o escopo central do Core Engine."""

    try:
        return validate_http_url(
            url,
            allow_hostname=True,
        )

    except ValueError as error:
        raise ValueError(
            f"Alvo fora do escopo permitido: {error}"
        ) from error


def get_page_title(html):
    """Extrai o título HTML."""

    parser = TitleParser()
    parser.feed(html)

    return (
        " ".join(filter(None, parser.title))
        or "Não identificado"
    )


def analyze_headers(headers):
    """Verifica a presença de cabeçalhos HTTP de segurança."""

    security_headers = {
        "Content-Security-Policy":
            "Proteção contra conteúdo não autorizado",
        "X-Content-Type-Options":
            "Reduz riscos de MIME sniffing",
        "X-Frame-Options":
            "Ajuda a prevenir clickjacking",
        "Strict-Transport-Security":
            "Política de HTTPS",
        "Referrer-Policy":
            "Controle de informações de referência",
        "Permissions-Policy":
            "Controle de recursos do navegador",
    }

    results = []

    for header, description in security_headers.items():
        results.append({
            "header": header,
            "present": header in headers,
            "description": description,
        })

    return results


def inspect_endpoint(url):
    """Analisa uma página HTTP/HTTPS com limite de resposta."""

    validate_target(url)

    response = requests.get(
        url,
        timeout=TIMEOUT,
        allow_redirects=False,
        stream=True,
        headers={
            "User-Agent": USER_AGENT,
        },
    )

    try:
        content = response.raw.read(
            MAX_RESPONSE_SIZE + 1,
            decode_content=True,
        )

        truncated = len(content) > MAX_RESPONSE_SIZE
        content = content[:MAX_RESPONSE_SIZE]

        html = content.decode(
            response.encoding or "utf-8",
            errors="replace",
        )

        return {
            "status_code": response.status_code,
            "server": response.headers.get(
                "Server",
                "Não informado",
            ),
            "content_type": response.headers.get(
                "Content-Type",
                "Não informado",
            ),
            "content_length": response.headers.get(
                "Content-Length",
                "Não informado",
            ),
            "title": get_page_title(html),
            "security_headers": analyze_headers(
                response.headers
            ),
            "response_truncated": truncated,
        }

    finally:
        response.close()


def inspect_methods(url):
    """Consulta os métodos HTTP anunciados pelo servidor."""

    validate_target(url)

    response = requests.options(
        url,
        timeout=TIMEOUT,
        allow_redirects=False,
        headers={
            "User-Agent": USER_AGENT,
        },
    )

    try:
        return response.headers.get(
            "Allow",
            "Não informado",
        )

    finally:
        response.close()


def inspect_robots(url):
    """Consulta robots.txt após validar novamente a URL."""

    parsed = urlparse(url)

    robots_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        "/robots.txt",
        "",
        "",
        "",
    ))

    validate_target(robots_url)

    response = requests.get(
        robots_url,
        timeout=TIMEOUT,
        allow_redirects=False,
        stream=True,
        headers={
            "User-Agent": USER_AGENT,
        },
    )

    try:
        if response.status_code != 200:
            return {
                "url": robots_url,
                "status_code": response.status_code,
                "content": "Arquivo não disponível.",
                "response_truncated": False,
            }

        content = response.raw.read(
            MAX_ROBOTS_SIZE + 1,
            decode_content=True,
        )

        truncated = len(content) > MAX_ROBOTS_SIZE
        content = content[:MAX_ROBOTS_SIZE]

        return {
            "url": robots_url,
            "status_code": response.status_code,
            "content": content.decode(
                "utf-8",
                errors="replace",
            ),
            "response_truncated": truncated,
        }

    finally:
        response.close()


def save_report(url, results):
    """Salva o relatório de reconhecimento web em JSON."""

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(timezone.utc)

    report = {
        "tool": "SOVIK",
        "version": "2.0.0",
        "module": "Web Reconnaissance",
        "target": url,
        "timestamp_utc": timestamp.isoformat(),
        "results": results,
    }

    filename = (
        f"web_recon_"
        f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
    )

    report_path = REPORT_DIR / filename

    with report_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return report_path


def select_campaign():
    """Permite associar a análise a uma campanha existente."""

    registered_campaigns = campaigns.list_campaigns()

    if not registered_campaigns:
        console.print(
            "\n[yellow]Nenhuma campanha cadastrada.[/yellow]"
        )
        return None

    console.print("\n[cyan]Campanhas disponíveis:[/cyan]")

    for campaign in registered_campaigns:
        console.print(
            f" [{campaign['id']}] {campaign['name']}"
        )

    choice = input(
        "\nID da campanha (ENTER para análise avulsa): "
    ).strip()

    if not choice:
        return None

    try:
        campaign_id = int(choice)
    except ValueError as error:
        raise ValueError(
            "O ID da campanha deve ser numérico."
        ) from error

    campaign = campaigns.get_campaign(campaign_id)

    if campaign is None:
        raise ValueError("Campanha não encontrada.")

    return campaign_id


def display_results(page, methods, robots):
    """Exibe os resultados da análise no terminal."""

    table = Table(
        title="Web Reconnaissance",
    )

    table.add_column("Item", style="cyan")
    table.add_column("Resultado", style="green")

    table.add_row(
        "HTTP Status",
        str(page["status_code"]),
    )

    table.add_row(
        "Page Title",
        page["title"],
    )

    table.add_row(
        "Server",
        page["server"],
    )

    table.add_row(
        "Content-Type",
        page["content_type"],
    )

    table.add_row(
        "HTTP Methods",
        methods,
    )

    table.add_row(
        "robots.txt",
        str(robots["status_code"]),
    )

    console.print(table)

    header_table = Table(
        title="Security Headers",
    )

    header_table.add_column("Header")
    header_table.add_column("Status")

    for item in page["security_headers"]:
        status = (
            "[green]Present[/green]"
            if item["present"]
            else "[yellow]Missing[/yellow]"
        )

        header_table.add_row(
            item["header"],
            status,
        )

    console.print(header_table)


def web_reconnaissance():
    """Executa reconhecimento web e registra a operação."""

    console.print(
        Panel(
            "[bold cyan]SOVIK[/bold cyan]\n"
            "[white]WEB RECONNAISSANCE[/white]\n"
            "[dim]Somente laboratórios próprios ou autorizados[/dim]",
            border_style="cyan",
        )
    )

    execution_id = None

    try:
        url = input(
            "\nURL do laboratório: "
        ).strip()

        if not url:
            raise ValueError("A URL é obrigatória.")

        validate_target(url)

        campaign_id = select_campaign()

        execution_id = operations.start_operation(
            module="web_reconnaissance",
            target=url,
            campaign_id=campaign_id,
        )

        console.print(
            f"\n[dim]Execução registrada: #{execution_id}[/dim]"
        )

        console.print(
            "\n[cyan]Analisando página...[/cyan]"
        )

        page = inspect_endpoint(url)

        console.print(
            "[cyan]Verificando métodos HTTP...[/cyan]"
        )

        methods = inspect_methods(url)

        console.print(
            "[cyan]Consultando robots.txt...[/cyan]"
        )

        robots = inspect_robots(url)

        results = {
            "page": page,
            "allowed_methods": methods,
            "robots_txt": robots,
        }

        display_results(
            page,
            methods,
            robots,
        )

        report_path = save_report(
            url,
            results,
        )

        completed = operations.complete_operation(
            execution_id,
            (
                "Reconhecimento web concluído. "
                f"HTTP {page['status_code']}. "
                f"Relatório: {report_path.name}"
            ),
        )

        if not completed:
            raise RuntimeError(
                "Não foi possível registrar a conclusão da execução."
            )

        console.print(
            f"\n[bold green]Relatório salvo:[/bold green]\n"
            f"{report_path}"
        )

        console.print(
            f"\n[bold green]Execução #{execution_id} concluída.[/bold green]"
        )

        logger.info(
            "Web Reconnaissance concluído. Execução: %s",
            execution_id,
        )

    except Exception as error:
        if execution_id is not None:
            try:
                operations.fail_operation(
                    execution_id,
                    error,
                )
            except Exception:
                logger.exception(
                    "Não foi possível atualizar o status da execução."
                )

        logger.exception(
            "Falha no módulo Web Reconnaissance."
        )

        console.print(
            f"\n[bold red]Erro:[/bold red] {error}"
        )


if __name__ == "__main__":
    web_reconnaissance()
