
import ipaddress
import json
import time

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"

MAX_RPS = 2
MAX_DURATION = 10
TIMEOUT = 3

PROFILES = {
    "1": {
        "name": "Load Test",
        "description": "Aumento gradual da carga",
        "stages": [
            {"rps": 1, "seconds": 3},
            {"rps": 2, "seconds": 3}
        ]
    },
    "2": {
        "name": "Spike Test",
        "description": "Pico temporário de requisições",
        "stages": [
            {"rps": 1, "seconds": 3},
            {"rps": 2, "seconds": 2},
            {"rps": 1, "seconds": 3}
        ]
    },
    "3": {
        "name": "Endurance Test",
        "description": "Carga constante controlada",
        "stages": [
            {"rps": 1, "seconds": 10}
        ]
    }
}


def validate_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Use uma URL HTTP ou HTTPS.")

    if not parsed.hostname:
        raise ValueError("URL inválida.")

    if parsed.username or parsed.password:
        raise ValueError("Credenciais na URL não são permitidas.")

    host = parsed.hostname.lower()

    if host == "localhost":
        return url

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        raise ValueError(
            "Use localhost ou um endereço IP privado."
        )

    if not (address.is_private or address.is_loopback):
        raise ValueError(
            "Somente endereços privados são permitidos."
        )

    return url


def calculate_metrics(results, elapsed):
    successful = [
        item for item in results
        if isinstance(item.get("status"), int)
    ]

    errors = len(results) - len(successful)

    latencies = [
        item["latency_ms"]
        for item in successful
        if item.get("latency_ms") is not None
    ]

    average_latency = (
        round(sum(latencies) / len(latencies), 2)
        if latencies else None
    )

    return {
        "total_requests": len(results),
        "http_responses": len(successful),
        "errors": errors,
        "average_latency_ms": average_latency,
        "elapsed_seconds": round(elapsed, 2)
    }


def execute_stage(url, rps, seconds, stage_number):
    results = []
    interval = 1 / rps
    total_requests = rps * seconds

    console.print(
        f"\n[cyan]Etapa {stage_number}:[/cyan] "
        f"{rps} RPS durante {seconds} segundos"
    )

    stage_start = time.monotonic()

    for request_number in range(total_requests):
        scheduled_time = stage_start + (request_number * interval)

        wait_time = scheduled_time - time.monotonic()

        if wait_time > 0:
            time.sleep(wait_time)

        request_start = time.monotonic()

        try:
            response = requests.get(
                url,
                timeout=TIMEOUT,
                allow_redirects=False,
                stream=True
            )

            latency = (
                time.monotonic() - request_start
            ) * 1000

            results.append({
                "stage": stage_number,
                "rps": rps,
                "status": response.status_code,
                "latency_ms": round(latency, 2)
            })

            response.close()

        except requests.RequestException as error:
            results.append({
                "stage": stage_number,
                "rps": rps,
                "status": "ERROR",
                "latency_ms": None,
                "error": str(error)
            })

    planned_end = stage_start + seconds
    remaining = planned_end - time.monotonic()

    if remaining > 0:
        time.sleep(remaining)

    elapsed = time.monotonic() - stage_start

    metrics = calculate_metrics(results, elapsed)

    stage_summary = {
        "stage": stage_number,
        "rps": rps,
        "planned_seconds": seconds,
        "metrics": metrics
    }

    return results, stage_summary


def save_report(url, profile, results, stage_summaries, elapsed):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    metrics = calculate_metrics(results, elapsed)

    timestamp = datetime.now(timezone.utc)

    report = {
        "tool": "BLACKOUT LAB",
        "module": "Stress Testing",
        "target": url,
        "timestamp_utc": timestamp.isoformat(),
        "configuration": {
            "profile": profile["name"],
            "description": profile["description"],
            "maximum_rps": MAX_RPS,
            "maximum_duration_seconds": MAX_DURATION,
            "stages": profile["stages"]
        },
        "metrics": metrics,
        "stage_results": stage_summaries,
        "results": results
    }

    filename = (
        f"stress_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
    )

    report_path = REPORT_DIR / filename

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    return report_path, metrics


def display_results(profile, metrics, stage_summaries):
    table = Table(title="Stress Testing Results")

    table.add_column("Métrica", style="cyan")
    table.add_column("Resultado", style="green")

    table.add_row("Perfil", profile["name"])
    table.add_row(
        "Total de requisições",
        str(metrics["total_requests"])
    )
    table.add_row(
        "Respostas HTTP",
        str(metrics["http_responses"])
    )
    table.add_row("Erros", str(metrics["errors"]))

    average = metrics["average_latency_ms"]

    table.add_row(
        "Latência média",
        f"{average} ms" if average is not None else "N/A"
    )

    table.add_row(
        "Tempo decorrido",
        f"{metrics['elapsed_seconds']} s"
    )

    console.print(table)

    stage_table = Table(title="Métricas por etapa")

    stage_table.add_column("Etapa")
    stage_table.add_column("RPS")
    stage_table.add_column("Respostas")
    stage_table.add_column("Erros")
    stage_table.add_column("Latência média")
    stage_table.add_column("Duração real")

    for stage in stage_summaries:
        stage_metrics = stage["metrics"]
        average = stage_metrics["average_latency_ms"]

        stage_table.add_row(
            str(stage["stage"]),
            str(stage["rps"]),
            str(stage_metrics["http_responses"]),
            str(stage_metrics["errors"]),
            f"{average} ms" if average is not None else "N/A",
            f"{stage_metrics['elapsed_seconds']} s"
        )

    console.print(stage_table)


def stress_testing():
    console.print(
        Panel(
            "[bold cyan]STRESS TESTING[/bold cyan]\n"
            "[white]BLACKOUT LAB[/white]\n"
            "[dim]Controlled laboratory performance tests[/dim]",
            border_style="cyan"
        )
    )

    console.print(
        "\n[yellow]Somente ambientes próprios ou autorizados.[/yellow]"
    )

    console.print("\n[bold]Perfis disponíveis:[/bold]")

    for key, profile in PROFILES.items():
        total = sum(
            stage["seconds"]
            for stage in profile["stages"]
        )

        console.print(
            f"[cyan][{key}][/cyan] {profile['name']} "
            f"- {profile['description']} ({total}s)"
        )

    choice = Prompt.ask(
        "\nSelecione o perfil",
        choices=list(PROFILES.keys())
    )

    profile = PROFILES[choice]
    url = Prompt.ask("\nURL do laboratório").strip()

    try:
        validate_url(url)

        total_duration = sum(
            stage["seconds"]
            for stage in profile["stages"]
        )

        if total_duration > MAX_DURATION:
            raise ValueError("Duração máxima excedida.")

        console.print(
            f"\n[bold green]Iniciando {profile['name']}...[/bold green]"
        )

        all_results = []
        stage_summaries = []

        campaign_start = time.monotonic()

        for index, stage in enumerate(
            profile["stages"],
            start=1
        ):
            results, summary = execute_stage(
                url,
                stage["rps"],
                stage["seconds"],
                index
            )

            all_results.extend(results)
            stage_summaries.append(summary)

        total_elapsed = time.monotonic() - campaign_start

        report_path, metrics = save_report(
            url,
            profile,
            all_results,
            stage_summaries,
            total_elapsed
        )

        display_results(
            profile,
            metrics,
            stage_summaries
        )

        console.print(
            "\n[bold green]Relatório salvo![/bold green]"
        )

        console.print(str(report_path))

    except ValueError as error:
        console.print(f"\n[red]Erro: {error}[/red]")

    except OSError as error:
        console.print(
            f"\n[red]Erro ao salvar relatório: {error}[/red]"
        )


if __name__ == "__main__":
    stress_testing()
