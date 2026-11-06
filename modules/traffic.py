
import time
import json
import ipaddress
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

from rich.console import Console
from rich.table import Table

console = Console()

MAX_DURATION = 10
MAX_RPS = 2

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"


def validate_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Use uma URL HTTP ou HTTPS.")

    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL inválida.")

    host = parsed.hostname

    if host == "localhost":
        return url

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        raise ValueError(
            "Use localhost ou um endereço IP privado."
        )

    if not (address.is_private or address.is_loopback):
        raise ValueError("Somente IPs privados são permitidos.")

    return url


def generate_traffic(url, duration):
    results = []
    interval = 1 / MAX_RPS
    total_requests = duration * MAX_RPS

    console.print(
        "\n[cyan]Iniciando geração controlada...[/cyan]"
    )

    start = time.monotonic()

    for _ in range(total_requests):
        request_start = time.monotonic()

        try:
            response = requests.get(
                url,
                timeout=2,
                allow_redirects=False,
                stream=True
            )

            latency = (
                time.monotonic() - request_start
            ) * 1000

            results.append({
                "status": response.status_code,
                "latency_ms": round(latency, 2)
            })

            response.close()

        except requests.RequestException as error:
            results.append({
                "status": "ERROR",
                "latency_ms": None,
                "error": str(error)
            })

        elapsed = time.monotonic() - request_start

        if elapsed < interval:
            time.sleep(interval - elapsed)

    total_time = time.monotonic() - start

    return results, total_time


def save_report(url, duration, results, elapsed):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    successful = [
        item for item in results
        if isinstance(item["status"], int)
    ]

    errors = len(results) - len(successful)

    latencies = [
        item["latency_ms"]
        for item in successful
    ]

    average_latency = (
        round(sum(latencies) / len(latencies), 2)
        if latencies else None
    )

    timestamp = datetime.now(timezone.utc)

    report = {
        "tool": "BLACKOUT LAB",
        "module": "Traffic Generation",
        "target": url,
        "timestamp_utc": timestamp.isoformat(),
        "configuration": {
            "duration_seconds": duration,
            "maximum_requests_per_second": MAX_RPS
        },
        "metrics": {
            "total_requests": len(results),
            "http_responses": len(successful),
            "errors": errors,
            "average_latency_ms": average_latency,
            "elapsed_seconds": round(elapsed, 2)
        },
        "results": results
    }

    filename = (
        f"traffic_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
    )

    report_path = REPORT_DIR / filename

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    return report_path


def traffic_generation():
    console.print(
        "\n=== BLACKOUT LAB | TRAFFIC GENERATION ==="
    )

    console.print(
        "Somente ambientes próprios ou autorizados.\n"
    )

    url = input("URL do laboratório: ").strip()

    try:
        validate_url(url)

        duration = int(
            input("Duração em segundos (1-10): ")
        )

        if not 1 <= duration <= MAX_DURATION:
            raise ValueError(
                "Duração permitida: 1 a 10 segundos."
            )

        results, elapsed = generate_traffic(
            url,
            duration
        )

        successful = [
            item for item in results
            if isinstance(item["status"], int)
        ]

        errors = len(results) - len(successful)

        latencies = [
            item["latency_ms"]
            for item in successful
        ]

        average_latency = (
            sum(latencies) / len(latencies)
            if latencies else None
        )

        table = Table(
            title="Traffic Generation Results"
        )

        table.add_column("Métrica", style="cyan")
        table.add_column("Resultado", style="green")

        table.add_row(
            "Requisições",
            str(len(results))
        )

        table.add_row(
            "Respostas HTTP",
            str(len(successful))
        )

        table.add_row(
            "Erros",
            str(errors)
        )

        table.add_row(
            "Latência média",
            f"{average_latency:.2f} ms"
            if average_latency is not None else "N/A"
        )

        table.add_row(
            "Tempo decorrido",
            f"{elapsed:.2f} s"
        )

        console.print(table)

        report_path = save_report(
            url,
            duration,
            results,
            elapsed
        )

        console.print(
            "\n[bold green]Relatório salvo com sucesso![/bold green]"
        )

        console.print(str(report_path))

    except ValueError as error:
        console.print(f"[red]Erro: {error}[/red]")

    except OSError as error:
        console.print(
            f"[red]Erro ao salvar relatório: {error}[/red]"
        )


if __name__ == "__main__":
    traffic_generation()

