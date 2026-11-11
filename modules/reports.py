
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from core.config import APP_NAME, APP_VERSION


console = Console()

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
MAX_REPORT_BYTES = 2_000_000


def as_dict(value):
    """Retorna um dicionario seguro."""
    return value if isinstance(value, dict) else {}


def as_list(value):
    """Retorna uma lista segura."""
    return value if isinstance(value, list) else []


def load_reports():
    """Carrega somente relatorios JSON com estrutura basica valida."""

    try:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        paths = list(REPORT_DIR.glob("*.json"))
    except OSError:
        return []

    files = []

    for path in paths:
        try:
            if not path.is_file():
                continue

            stat = path.stat()

            if stat.st_size > MAX_REPORT_BYTES:
                continue

            files.append((stat.st_mtime, path))

        except OSError:
            continue

    reports = []

    for _, path in sorted(files, reverse=True):
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                continue

            module = data.get("module")
            target = data.get("target")

            if not isinstance(module, str) or not module.strip():
                continue

            if not isinstance(target, str):
                continue

            reports.append({
                "filename": path.name,
                "data": data,
            })

        except (OSError, UnicodeError, json.JSONDecodeError):
            continue

    return reports


def show_report_list(reports):
    """Exibe uma listagem segura de relatorios."""

    table = Table(title="Relatorios disponiveis")

    table.add_column("ID", style="cyan")
    table.add_column("Arquivo")
    table.add_column("Alvo", style="green")
    table.add_column("Modulo")

    for index, item in enumerate(as_list(reports), start=1):
        report = as_dict(item)
        data = as_dict(report.get("data"))

        table.add_row(
            str(index),
            str(report.get("filename", "N/A")),
            str(data.get("target", "N/A")),
            str(data.get("module", "N/A")),
        )

    console.print(table)


def show_report_details(data):
    """Exibe os detalhes de um relatorio."""

    data = as_dict(data)

    console.print(
        Panel(
            f"[bold]Alvo:[/bold] {data.get('target', 'N/A')}\n"
            f"[bold]Modulo:[/bold] {data.get('module', 'N/A')}\n"
            f"[bold]Data UTC:[/bold] {data.get('timestamp_utc', 'N/A')}",
            title="Detalhes da campanha",
            border_style="cyan",
        )
    )

    renderers = {
        "Reconnaissance": show_recon_results,
        "Traffic Generation": show_traffic_results,
        "Stress Testing": show_stress_results,
        "Exploitation Simulation": show_exploitation_results,
        "Web Reconnaissance": show_web_recon_results,
    }

    renderer = renderers.get(data.get("module"))

    if renderer is None:
        console.print(
            "[yellow]Formato de relatorio nao reconhecido.[/yellow]"
        )
        return

    renderer(data)


def show_recon_results(data):
    data = as_dict(data)

    addresses = as_list(data.get("resolved_addresses"))
    results = as_list(data.get("results"))

    console.print("\n[bold cyan]Enderecos encontrados[/bold cyan]")

    for address in addresses:
        console.print(f" - {address}")

    table = Table(title="Resultados do reconhecimento")

    table.add_column("Porta", style="cyan")
    table.add_column("Protocolo")
    table.add_column("Estado")
    table.add_column("Servico")

    for item in results:
        result = as_dict(item)

        status = str(result.get("status", "unknown")).upper()
        color = "green" if status == "OPEN" else "red"

        table.add_row(
            str(result.get("port", "N/A")),
            str(result.get("protocol", "N/A")),
            f"[{color}]{status}[/{color}]",
            str(result.get("service", "unknown")),
        )

    console.print(table)


def show_web_recon_results(data):
    data = as_dict(data)

    results = as_dict(data.get("results"))
    page = as_dict(results.get("page"))

    console.print("\n[bold cyan]Informacoes da pagina[/bold cyan]")

    table = Table(title="Web Reconnaissance")

    table.add_column("Item", style="cyan")
    table.add_column("Resultado", style="green")

    table.add_row("HTTP Status", str(page.get("status_code", "N/A")))
    table.add_row("Page Title", str(page.get("title", "N/A")))
    table.add_row("Server", str(page.get("server", "N/A")))
    table.add_row("Content-Type", str(page.get("content_type", "N/A")))
    table.add_row("Content-Length", str(page.get("content_length", "N/A")))
    table.add_row(
        "HTTP Methods",
        str(results.get("allowed_methods", "N/A")),
    )

    robots = as_dict(results.get("robots_txt"))

    table.add_row(
        "robots.txt",
        str(robots.get("status_code", "N/A")),
    )

    console.print(table)

    headers = as_list(page.get("security_headers"))

    header_table = Table(title="Security Headers")

    header_table.add_column("Header", style="cyan")
    header_table.add_column("Status")
    header_table.add_column("Descricao")

    for item in headers:
        item = as_dict(item)
        present = item.get("present") is True

        status = (
            "[green]Present[/green]"
            if present
            else "[yellow]Missing[/yellow]"
        )

        header_table.add_row(
            str(item.get("header", "N/A")),
            status,
            str(item.get("description", "N/A")),
        )

    console.print(header_table)

    console.print("\n[bold cyan]robots.txt content[/bold cyan]")
    console.print(str(robots.get("content", "Nao disponivel.")))

    if page.get("response_truncated") is True:
        console.print(
            "\n[yellow]A resposta foi parcialmente analisada.[/yellow]"
        )


def show_metrics_table(metrics, title):
    metrics = as_dict(metrics)

    table = Table(title=title)

    table.add_column("Metrica")
    table.add_column("Resultado", style="green")

    table.add_row(
        "Total de requisicoes",
        str(metrics.get("total_requests", 0)),
    )

    table.add_row(
        "Respostas HTTP",
        str(metrics.get("http_responses", 0)),
    )

    table.add_row(
        "Erros",
        str(metrics.get("errors", 0)),
    )

    average = metrics.get("average_latency_ms")

    table.add_row(
        "Latencia media",
        f"{average} ms" if average is not None else "N/A",
    )

    table.add_row(
        "Tempo decorrido",
        f"{metrics.get('elapsed_seconds', 'N/A')} s",
    )

    console.print(table)


def show_traffic_results(data):
    data = as_dict(data)
    configuration = as_dict(data.get("configuration"))

    console.print("\n[bold cyan]Configuracao do teste[/bold cyan]")

    config_table = Table()

    config_table.add_column("Parametro")
    config_table.add_column("Valor", style="green")

    config_table.add_row(
        "Duracao",
        f"{configuration.get('duration_seconds', 'N/A')} segundos",
    )

    config_table.add_row(
        "Limite de requisicoes",
        f"{configuration.get('maximum_requests_per_second', 'N/A')} RPS",
    )

    console.print(config_table)

    show_metrics_table(
        data.get("metrics"),
        "Metricas da execucao",
    )

    results = as_list(data.get("results"))

    if results:
        table = Table(title="Detalhes das requisicoes")

        table.add_column("#", style="cyan")
        table.add_column("Status")
        table.add_column("Latencia")

        for index, item in enumerate(results, start=1):
            result = as_dict(item)
            latency = result.get("latency_ms")

            table.add_row(
                str(index),
                str(result.get("status", "ERROR")),
                f"{latency} ms" if latency is not None else "N/A",
            )

        console.print(table)


def show_stress_results(data):
    data = as_dict(data)
    configuration = as_dict(data.get("configuration"))

    console.print("\n[bold cyan]Configuracao do teste[/bold cyan]")

    config_table = Table()

    config_table.add_column("Parametro")
    config_table.add_column("Valor", style="green")

    config_table.add_row(
        "Perfil",
        str(configuration.get("profile", "N/A")),
    )

    config_table.add_row(
        "Descricao",
        str(configuration.get("description", "N/A")),
    )

    config_table.add_row(
        "Limite de RPS",
        str(configuration.get("maximum_rps", "N/A")),
    )

    console.print(config_table)

    stages = as_list(configuration.get("stages"))

    if stages:
        planned_table = Table(title="Etapas planejadas")

        planned_table.add_column("Etapa")
        planned_table.add_column("RPS")
        planned_table.add_column("Duracao planejada")

        for index, item in enumerate(stages, start=1):
            stage = as_dict(item)

            planned_table.add_row(
                str(index),
                str(stage.get("rps", "N/A")),
                f"{stage.get('seconds', 'N/A')} s",
            )

        console.print(planned_table)

    show_metrics_table(
        data.get("metrics"),
        "Metricas gerais do teste",
    )

    stage_results = as_list(data.get("stage_results"))

    if stage_results:
        stage_table = Table(title="Desempenho por etapa")

        stage_table.add_column("Etapa")
        stage_table.add_column("RPS")
        stage_table.add_column("Respostas")
        stage_table.add_column("Erros")
        stage_table.add_column("Latencia media")
        stage_table.add_column("Duracao real")

        for item in stage_results:
            stage = as_dict(item)
            metrics = as_dict(stage.get("metrics"))
            average = metrics.get("average_latency_ms")

            stage_table.add_row(
                str(stage.get("stage", "N/A")),
                str(stage.get("rps", "N/A")),
                str(metrics.get("http_responses", 0)),
                str(metrics.get("errors", 0)),
                f"{average} ms" if average is not None else "N/A",
                f"{metrics.get('elapsed_seconds', 'N/A')} s",
            )

        console.print(stage_table)

    results = as_list(data.get("results"))

    if results:
        request_table = Table(title="Detalhes das requisicoes")

        request_table.add_column("#", style="cyan")
        request_table.add_column("Etapa")
        request_table.add_column("RPS")
        request_table.add_column("Status")
        request_table.add_column("Latencia")

        for index, item in enumerate(results, start=1):
            result = as_dict(item)
            latency = result.get("latency_ms")

            request_table.add_row(
                str(index),
                str(result.get("stage", "N/A")),
                str(result.get("rps", "N/A")),
                str(result.get("status", "ERROR")),
                f"{latency} ms" if latency is not None else "N/A",
            )

        console.print(request_table)


def show_exploitation_results(data):
    data = as_dict(data)

    console.print("\n[bold cyan]SQL Injection Analysis[/bold cyan]")

    results = as_dict(data.get("test_results"))
    vulnerable = as_dict(results.get("vulnerable_query"))
    secure = as_dict(results.get("parameterized_query"))

    table = Table(title="Resultados da exploracao")

    table.add_column("Metrica")
    table.add_column("Consulta vulneravel")
    table.add_column("Consulta segura")

    table.add_row(
        "Registros retornados",
        str(vulnerable.get("returned_records", 0)),
        str(secure.get("returned_records", 0)),
    )

    table.add_row(
        "Bypass de autenticacao",
        "Sim" if vulnerable.get("authentication_bypassed") is True else "Nao",
        "Sim" if secure.get("authentication_bypassed") is True else "Nao",
    )

    console.print(table)

    if data.get("vulnerability_detected") is True:
        console.print(
            "\n[bold red]VULNERABILIDADE CONFIRMADA[/bold red]"
        )
    else:
        console.print(
            "\n[bold green]Nenhuma injecao confirmada[/bold green]"
        )

    evidence = as_dict(data.get("evidence"))
    accounts = as_list(evidence.get("returned_accounts"))

    if accounts:
        evidence_table = Table(
            title="Registros retornados como evidencia"
        )

        evidence_table.add_column("ID")
        evidence_table.add_column("Usuario")
        evidence_table.add_column("Perfil")

        for item in accounts:
            account = as_dict(item)

            evidence_table.add_row(
                str(account.get("id", "N/A")),
                str(account.get("username", "N/A")),
                str(account.get("role", "N/A")),
            )

        console.print(evidence_table)

    console.print(
        "\n[bold]Conclusao:[/bold] "
        + str(data.get("conclusion", "Sem conclusao registrada."))
    )


def show_reports():
    console.print(
        Panel(
            f"[bold cyan]CAMPAIGN REPORTS[/bold cyan]\n"
            f"[white]{APP_NAME}[/white]\n"
            f"[dim]Version {APP_VERSION}[/dim]",
            border_style="cyan",
        )
    )

    reports = load_reports()

    if not reports:
        console.print(
            "[yellow]Nenhum relatorio valido encontrado.[/yellow]"
        )
        return

    show_report_list(reports)

    choice = Prompt.ask(
        "\nDigite o ID para visualizar ou 0 para voltar",
        default="0",
    )

    if choice == "0":
        return

    if (
        not choice.isdigit()
        or not 1 <= int(choice) <= len(reports)
    ):
        console.print("[red]ID invalido.[/red]")
        return

    selected = as_dict(reports[int(choice) - 1])

    show_report_details(selected.get("data"))


if __name__ == "__main__":
    show_reports()
