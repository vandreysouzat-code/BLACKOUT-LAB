import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"


def load_reports():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    reports = []

    for path in sorted(
        REPORT_DIR.glob("*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True
    ):
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            reports.append({
                "filename": path.name,
                "data": data
            })

        except (OSError, json.JSONDecodeError):
            continue

    return reports


def show_report_list(reports):
    table = Table(title="Relatórios disponíveis")

    table.add_column("ID", style="cyan")
    table.add_column("Arquivo")
    table.add_column("Alvo", style="green")
    table.add_column("Módulo")

    for index, report in enumerate(reports, start=1):
        data = report["data"]

        table.add_row(
            str(index),
            report["filename"],
            str(data.get("target", "N/A")),
            str(data.get("module", "N/A"))
        )

    console.print(table)


def show_report_details(data):
    console.print(
        Panel(
            f"[bold]Alvo:[/bold] {data.get('target', 'N/A')}\n"
            f"[bold]Módulo:[/bold] {data.get('module', 'N/A')}\n"
            f"[bold]Data UTC:[/bold] "
            f"{data.get('timestamp_utc', 'N/A')}",
            title="Detalhes da campanha",
            border_style="cyan"
        )
    )

    module = data.get("module", "")

    if module == "Reconnaissance":
        show_recon_results(data)

    elif module == "Traffic Generation":
        show_traffic_results(data)

    elif module == "Stress Testing":
        show_stress_results(data)

    elif module == "Exploitation Simulation":
        show_exploitation_results(data)

    else:
        console.print(
            "[yellow]Formato de relatório não reconhecido.[/yellow]"
        )


def show_recon_results(data):
    addresses = data.get("resolved_addresses", [])

    console.print("\n[bold cyan]Endereços encontrados[/bold cyan]")

    for address in addresses:
        console.print(f" - {address}")

    table = Table(title="Resultados do reconhecimento")

    table.add_column("Porta", style="cyan")
    table.add_column("Protocolo")
    table.add_column("Estado")
    table.add_column("Serviço")

    for result in data.get("results", []):
        status = str(
            result.get("status", "unknown")
        ).upper()

        color = "green" if status == "OPEN" else "red"

        table.add_row(
            str(result.get("port", "N/A")),
            str(result.get("protocol", "N/A")),
            f"[{color}]{status}[/{color}]",
            str(result.get("service", "unknown"))
        )

    console.print(table)


def show_metrics_table(metrics, title):
    table = Table(title=title)

    table.add_column("Métrica")
    table.add_column("Resultado", style="green")

    table.add_row(
        "Total de requisições",
        str(metrics.get("total_requests", 0))
    )

    table.add_row(
        "Respostas HTTP",
        str(metrics.get("http_responses", 0))
    )

    table.add_row(
        "Erros",
        str(metrics.get("errors", 0))
    )

    average = metrics.get("average_latency_ms")

    table.add_row(
        "Latência média",
        f"{average} ms" if average is not None else "N/A"
    )

    table.add_row(
        "Tempo decorrido",
        f"{metrics.get('elapsed_seconds', 'N/A')} s"
    )

    console.print(table)


def show_traffic_results(data):
    configuration = data.get("configuration", {})

    console.print("\n[bold cyan]Configuração do teste[/bold cyan]")

    config_table = Table()

    config_table.add_column("Parâmetro")
    config_table.add_column("Valor", style="green")

    config_table.add_row(
        "Duração",
        f"{configuration.get('duration_seconds', 'N/A')} segundos"
    )

    config_table.add_row(
        "Limite de requisições",
        f"{configuration.get('maximum_requests_per_second', 'N/A')} RPS"
    )

    console.print(config_table)

    show_metrics_table(
        data.get("metrics", {}),
        "Métricas da execução"
    )

    results = data.get("results", [])

    if results:
        table = Table(title="Detalhes das requisições")

        table.add_column("#", style="cyan")
        table.add_column("Status")
        table.add_column("Latência")

        for index, result in enumerate(results, start=1):
            latency = result.get("latency_ms")

            table.add_row(
                str(index),
                str(result.get("status", "ERROR")),
                f"{latency} ms" if latency is not None else "N/A"
            )

        console.print(table)


def show_stress_results(data):
    configuration = data.get("configuration", {})

    console.print("\n[bold cyan]Configuração do teste[/bold cyan]")

    config_table = Table()

    config_table.add_column("Parâmetro")
    config_table.add_column("Valor", style="green")

    config_table.add_row(
        "Perfil",
        str(configuration.get("profile", "N/A"))
    )

    config_table.add_row(
        "Descrição",
        str(configuration.get("description", "N/A"))
    )

    config_table.add_row(
        "Limite de RPS",
        str(configuration.get("maximum_rps", "N/A"))
    )

    console.print(config_table)

    stages = configuration.get("stages", [])

    if stages:
        planned_table = Table(title="Etapas planejadas")

        planned_table.add_column("Etapa")
        planned_table.add_column("RPS")
        planned_table.add_column("Duração planejada")

        for index, stage in enumerate(stages, start=1):
            planned_table.add_row(
                str(index),
                str(stage.get("rps", "N/A")),
                f"{stage.get('seconds', 'N/A')} s"
            )

        console.print(planned_table)

    show_metrics_table(
        data.get("metrics", {}),
        "Métricas gerais do teste"
    )

    stage_results = data.get("stage_results", [])

    if stage_results:
        stage_table = Table(title="Desempenho por etapa")

        stage_table.add_column("Etapa")
        stage_table.add_column("RPS")
        stage_table.add_column("Respostas")
        stage_table.add_column("Erros")
        stage_table.add_column("Latência média")
        stage_table.add_column("Duração real")

        for stage in stage_results:
            metrics = stage.get("metrics", {})
            average = metrics.get("average_latency_ms")

            stage_table.add_row(
                str(stage.get("stage", "N/A")),
                str(stage.get("rps", "N/A")),
                str(metrics.get("http_responses", 0)),
                str(metrics.get("errors", 0)),
                f"{average} ms" if average is not None else "N/A",
                f"{metrics.get('elapsed_seconds', 'N/A')} s"
            )

        console.print(stage_table)

    results = data.get("results", [])

    if results:
        request_table = Table(title="Detalhes das requisições")

        request_table.add_column("#", style="cyan")
        request_table.add_column("Etapa")
        request_table.add_column("RPS")
        request_table.add_column("Status")
        request_table.add_column("Latência")

        for index, result in enumerate(results, start=1):
            latency = result.get("latency_ms")

            request_table.add_row(
                str(index),
                str(result.get("stage", "N/A")),
                str(result.get("rps", "N/A")),
                str(result.get("status", "ERROR")),
                f"{latency} ms" if latency is not None else "N/A"
            )

        console.print(request_table)


def show_exploitation_results(data):
    console.print("\n[bold cyan]SQL Injection Analysis[/bold cyan]")

    results = data.get("test_results", {})
    vulnerable = results.get("vulnerable_query", {})
    secure = results.get("parameterized_query", {})

    table = Table(title="Resultados da exploração")

    table.add_column("Métrica")
    table.add_column("Consulta vulnerável")
    table.add_column("Consulta segura")

    table.add_row(
        "Registros retornados",
        str(vulnerable.get("returned_records", 0)),
        str(secure.get("returned_records", 0))
    )

    table.add_row(
        "Bypass de autenticação",
        "Sim" if vulnerable.get("authentication_bypassed") else "Não",
        "Sim" if secure.get("authentication_bypassed") else "Não"
    )

    console.print(table)

    detected = data.get("vulnerability_detected", False)

    if detected:
        console.print(
            "\n[bold red]VULNERABILIDADE CONFIRMADA[/bold red]"
        )
    else:
        console.print(
            "\n[bold green]Nenhuma injeção confirmada[/bold green]"
        )

    evidence = data.get("evidence", {})
    accounts = evidence.get("returned_accounts", [])

    if accounts:
        evidence_table = Table(
            title="Registros retornados como evidência"
        )

        evidence_table.add_column("ID")
        evidence_table.add_column("Usuário")
        evidence_table.add_column("Perfil")

        for account in accounts:
            evidence_table.add_row(
                str(account.get("id", "N/A")),
                str(account.get("username", "N/A")),
                str(account.get("role", "N/A"))
            )

        console.print(evidence_table)

    console.print(
        "\n[bold]Conclusão:[/bold] "
        + data.get("conclusion", "Sem conclusão registrada.")
    )


def show_reports():
    console.print(
        Panel(
            "[bold cyan]CAMPAIGN REPORTS 5.0[/bold cyan]\n"
            "[white]BLACKOUT LAB[/white]",
            border_style="cyan"
        )
    )

    reports = load_reports()

    if not reports:
        console.print(
            "[yellow]Nenhum relatório encontrado.[/yellow]"
        )
        return

    show_report_list(reports)

    choice = Prompt.ask(
        "\nDigite o ID para visualizar ou 0 para voltar",
        default="0"
    )

    if choice == "0":
        return

    if (
        not choice.isdigit()
        or not 1 <= int(choice) <= len(reports)
    ):
        console.print("[red]ID inválido.[/red]")
        return

    selected = reports[int(choice) - 1]

    show_report_details(selected["data"])


if __name__ == "__main__":
    show_reports()
