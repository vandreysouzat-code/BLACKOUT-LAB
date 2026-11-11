
"""
Ponto de entrada principal do SOVIK 2.0.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from core import campaigns
from core.config import (
    APP_NAME,
    APP_VERSION,
    DOS_LAB_ENABLED,
    DOS_LAB_MAX_DURATION,
    DOS_LAB_MAX_WORKERS,
)
from core.database import (
    initialize_database,
    list_executions,
)
from core.logger import get_logger

from modules.recon import reconnaissance
from modules.reports import show_reports
from modules.traffic import traffic_generation
from modules.stress import stress_testing
from modules.exploitation import exploitation_simulation
from modules.web_recon import web_reconnaissance


console = Console()
logger = get_logger("sovik.main")


def banner():
    """Exibe a identidade visual da plataforma."""

    console.print(
        Panel(
            f"[bold cyan]{APP_NAME}[/bold cyan]\n"
            "[white]OFFENSIVE SECURITY PLATFORM[/white]\n"
            f"[dim]Version {APP_VERSION}[/dim]",
            border_style="cyan",
        )
    )


def show_campaigns():
    """Exibe as campanhas cadastradas."""

    registered_campaigns = campaigns.list_campaigns()

    table = Table(title="Campaign Manager")

    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Status", style="green")
    table.add_column("Created At", style="dim")

    for campaign in registered_campaigns:
        table.add_row(
            str(campaign["id"]),
            campaign["name"],
            campaign["status"],
            campaign["created_at"],
        )

    if not registered_campaigns:
        console.print("[yellow]Nenhuma campanha cadastrada.[/yellow]")
    else:
        console.print(table)

    choice = Prompt.ask(
        "\nDeseja criar uma campanha? (s/n)",
        choices=["s", "n"],
        default="n",
    )

    if choice == "s":
        name = Prompt.ask("Nome da campanha")
        description = Prompt.ask(
            "Descrição",
            default="",
        )

        try:
            campaign_id = campaigns.create_campaign(
                name,
                description,
            )

            console.print(
                f"[green]Campanha criada com ID {campaign_id}.[/green]"
            )

            logger.info(
                "Campanha criada: ID=%s",
                campaign_id,
            )

        except ValueError as error:
            console.print(f"[red]{error}[/red]")


def show_execution_history():
    """Exibe o histórico geral de execuções."""

    executions = list_executions()

    if not executions:
        console.print(
            "[yellow]Nenhuma execução registrada.[/yellow]"
        )
        return

    table = Table(title="Execution History")

    table.add_column("ID", style="cyan")
    table.add_column("Campaign", style="magenta")
    table.add_column("Module")
    table.add_column("Target")
    table.add_column("Status", style="green")

    for execution in executions:
        table.add_row(
            str(execution["id"]),
            str(execution["campaign_id"] or "-"),
            execution["module"],
            execution["target"],
            execution["status"],
        )

    console.print(table)


def show_system_information():
    """Exibe informações da configuração atual."""

    table = Table(title="System Information")

    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Application", APP_NAME)
    table.add_row("Version", APP_VERSION)
    table.add_row(
        "Isolated Lab",
        "Enabled" if DOS_LAB_ENABLED else "Disabled",
    )
    table.add_row(
        "Lab Maximum Duration",
        f"{DOS_LAB_MAX_DURATION} seconds",
    )
    table.add_row(
        "Lab Maximum Workers",
        str(DOS_LAB_MAX_WORKERS),
    )

    console.print(table)


def menu():
    """Exibe o menu principal e direciona as opções."""

    options = {
        "1": "Reconnaissance",
        "2": "Traffic Generation",
        "3": "Stress Testing",
        "4": "Exploitation Simulation",
        "5": "Campaign Reports",
        "6": "Web Reconnaissance",
        "7": "Campaign Manager",
        "8": "Execution History",
        "9": "System Information",
        "0": "Exit",
    }

    console.print("\n[bold cyan]MAIN MENU[/bold cyan]\n")

    for key, value in options.items():
        console.print(f"[cyan][{key}][/cyan] {value}")

    choice = Prompt.ask(
        "\nSelect module",
        choices=list(options),
    )

    actions = {
        "1": reconnaissance,
        "2": traffic_generation,
        "3": stress_testing,
        "4": exploitation_simulation,
        "5": show_reports,
        "6": web_reconnaissance,
        "7": show_campaigns,
        "8": show_execution_history,
        "9": show_system_information,
    }

    if choice == "0":
        console.print("[yellow]SOVIK encerrado.[/yellow]")
        return False

    try:
        actions[choice]()
    except Exception:
        logger.exception(
            "Erro durante a execução da opção %s",
            choice,
        )
        console.print(
            "[red]Ocorreu um erro. Consulte o arquivo de logs.[/red]"
        )

    return True


def main():
    """Inicializa a plataforma."""

    try:
        initialize_database()

        logger.info(
            "%s %s iniciado",
            APP_NAME,
            APP_VERSION,
        )

        banner()

        while True:
            if not menu():
                break

            Prompt.ask(
                "\nPressione ENTER para continuar",
                default="",
            )

    except KeyboardInterrupt:
        console.print(
            "\n[yellow]SOVIK interrompido pelo usuário.[/yellow]"
        )

    finally:
        logger.info("SOVIK encerrado")


if __name__ == "__main__":
    main()
