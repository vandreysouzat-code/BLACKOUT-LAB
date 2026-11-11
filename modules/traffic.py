
"""
Módulo Traffic Generation do BLACKOUT LAB 2.0.

Gera tráfego HTTP controlado em laboratórios autorizados,
com limites rígidos e registro centralizado das operações.
"""

import json
import time

from datetime import datetime, timezone
from pathlib import Path

import requests

from core.scope import validate_http_url
from core import operations, campaigns
from core.logger import get_logger

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt


console = Console()
logger = get_logger("blackout.traffic")

MAX_DURATION = 10
MAX_RPS = 2
TIMEOUT = 3

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"


def validate_url(url):
    """Valida o alvo usando o escopo central do Core Engine."""

    try:
        return validate_http_url(
            url,
            allow_hostname=False
        )

    except ValueError as error:
        raise ValueError(
            f"Alvo fora do escopo permitido: {error}"
        ) from error


def validate_duration(duration):
    """Valida a duração máxima da geração de tráfego."""

    if (
        not isinstance(duration, int)
        or isinstance(duration, bool)
        or not 1 <= duration <= MAX_DURATION
    ):
        raise ValueError(
            f"Duração permitida: 1 a {MAX_DURATION} segundos."
        )

    return duration


def select_campaign():
    """Permite associar a execução a uma campanha."""

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

    choice = Prompt.ask(
        "\nID da campanha (ENTER para execução avulsa)",
        default=""
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


def generate_traffic(url, duration):
    """Gera tráfego HTTP limitado para laboratório autorizado."""

    validate_url(url)
    validate_duration(duration)

    results = []

    interval = 1 / MAX_RPS
    total_requests = duration * MAX_RPS

    console.print(
        "\n[cyan]Iniciando geração controlada...[/cyan]"
    )

    start = time.monotonic()

    for _ in range(total_requests):
        request_start = time.monotonic()
        response = None

        try:
            response = requests.get(
                url,
                timeout=TIMEOUT,
                allow_redirects=False,
                stream=True,
                headers={
                    "User-Agent": "BLACKOUT-LAB/2.0"
                }
            )

            latency = (
                time.monotonic() - request_start
            ) * 1000

            results.append({
                "status": response.status_code,
                "latency_ms": round(latency, 2)
            })

        except requests.RequestException as error:
            results.append({
                "status": "ERROR",
                "latency_ms": None,
                "error": str(error)
            })

        finally:
            if response is not None:
                response.close()

        elapsed = time.monotonic() - request_start

        if elapsed < interval:
            time.sleep(interval - elapsed)

    total_time = time.monotonic() - start

    return results, total_time


def calculate_metrics(results, elapsed):
    """Calcula métricas da execução."""

    successful = [
        item for item in results
        if isinstance(item.get("status"), int)
        and not isinstance(item.get("status"), bool)
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


def save_report(
    url,
    duration,
    results,
    elapsed,
    campaign_id=None,
    execution_id=None
):
    """Salva o relatório JSON da geração de tráfego."""

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now(timezone.utc)

    metrics = calculate_metrics(
        results,
        elapsed
    )

    report = {
        "tool": "BLACKOUT LAB",
        "version": "2.0.0",
        "module": "Traffic Generation",
        "target": url,
        "timestamp_utc": timestamp.isoformat(),
        "campaign_id": campaign_id,
        "execution_id": execution_id,
        "configuration": {
            "duration_seconds": duration,
            "maximum_requests_per_second": MAX_RPS,
            "maximum_requests": duration * MAX_RPS
        },
        "metrics": metrics,
        "results": results
    }

    filename = (
        f"traffic_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
    )

    report_path = REPORT_DIR / filename

    with report_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    return report_path


def display_results(metrics):
    """Exibe os resultados da execução."""

    table = Table(
        title="Traffic Generation Results"
    )

    table.add_column(
        "Métrica",
        style="cyan"
    )

    table.add_column(
        "Resultado",
        style="green"
    )

    table.add_row(
        "Requisições",
        str(metrics["total_requests"])
    )

    table.add_row(
        "Respostas HTTP",
        str(metrics["http_responses"])
    )

    table.add_row(
        "Erros",
        str(metrics["errors"])
    )

    average_latency = metrics["average_latency_ms"]

    table.add_row(
        "Latência média",
        f"{average_latency:.2f} ms"
        if average_latency is not None else "N/A"
    )

    table.add_row(
        "Tempo decorrido",
        f"{metrics['elapsed_seconds']:.2f} s"
    )

    console.print(table)


def traffic_generation():
    """Interface interativa do módulo."""

    console.print(
        "\n=== BLACKOUT LAB 2.0 | TRAFFIC GENERATION ==="
    )

    console.print(
        "Somente ambientes próprios ou autorizados.\n"
    )

    execution_id = None

    try:
        url = input(
            "URL do laboratório: "
        ).strip()

        validate_url(url)

        duration_input = input(
            f"Duração em segundos (1-{MAX_DURATION}): "
        ).strip()

        try:
            duration = int(duration_input)

        except ValueError as error:
            raise ValueError(
                "Informe uma duração numérica válida."
            ) from error

        validate_duration(duration)

        campaign_id = select_campaign()

        execution_id = operations.start_operation(
            module="traffic_generation",
            target=url,
            campaign_id=campaign_id,
            duration=duration
        )

        console.print(
            f"\n[dim]Execução registrada: #{execution_id}[/dim]"
        )

        console.print(
            f"\n[cyan]Limite: {MAX_RPS} requisições por segundo.[/cyan]"
        )

        console.print(
            f"[cyan]Duração: {duration} segundos.[/cyan]"
        )

        results, elapsed = generate_traffic(
            url,
            duration
        )

        metrics = calculate_metrics(
            results,
            elapsed
        )

        display_results(metrics)

        report_path = save_report(
            url,
            duration,
            results,
            elapsed,
            campaign_id=campaign_id,
            execution_id=execution_id
        )

        completed = operations.complete_operation(
            execution_id,
            (
                f"Geração de tráfego concluída. "
                f"Requisições: {metrics['total_requests']}. "
                f"Erros: {metrics['errors']}. "
                f"Relatório: {report_path.name}"
            )
        )

        if not completed:
            raise RuntimeError(
                "Não foi possível registrar a conclusão da operação."
            )

        console.print(
            "\n[bold green]Relatório salvo com sucesso![/bold green]"
        )

        console.print(str(report_path))

        console.print(
            f"\n[bold green]Execução #{execution_id} concluída.[/bold green]"
        )

        logger.info(
            "Traffic Generation concluído. "
            "Execução=%s | Requisições=%s | Erros=%s",
            execution_id,
            metrics["total_requests"],
            metrics["errors"]
        )

    except ValueError as error:
        if execution_id is not None:
            operations.fail_operation(execution_id, error)

        console.print(
            f"[red]Erro: {error}[/red]"
        )

    except OSError as error:
        if execution_id is not None:
            operations.fail_operation(execution_id, error)

        logger.exception(
            "Erro de sistema no Traffic Generation."
        )

        console.print(
            f"[red]Erro ao salvar relatório ou acessar arquivo: {error}[/red]"
        )

    except Exception as error:
        if execution_id is not None:
            operations.fail_operation(execution_id, error)

        logger.exception(
            "Falha inesperada no Traffic Generation."
        )

        console.print(
            "[bold red]Falha inesperada. Consulte os logs.[/bold red]"
        )


if __name__ == "__main__":
    traffic_generation()
