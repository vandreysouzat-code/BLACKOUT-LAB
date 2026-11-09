
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from modules.recon import reconnaissance
from modules.reports import show_reports
from modules.traffic import traffic_generation
from modules.stress import stress_testing
from modules.exploitation import exploitation_simulation
from modules.web_recon import web_reconnaissance

console = Console()


def banner():
    console.print(
        Panel(
            "[bold cyan]BLACKOUT LAB[/bold cyan]\n"
            "[white]OFFENSIVE SECURITY PLATFORM[/white]\n"
            "[dim]Version 1.1.0[/dim]",
            border_style="cyan"
        )
    )


def menu():
    options = {
        "1": "Reconnaissance",
        "2": "Traffic Generation",
        "3": "Stress Testing",
        "4": "Exploitation Simulation",
        "5": "Campaign Reports",
        "6": "Web Reconnaissance",
        "0": "Exit"
    }

    console.print("\n[bold]MAIN MENU[/bold]\n")

    for key, value in options.items():
        console.print(f"[cyan][{key}][/cyan] {value}")

    choice = Prompt.ask(
        "\nSelect module",
        choices=list(options)
    )

    if choice == "0":
        console.print("[yellow]BLACKOUT LAB encerrado.[/yellow]")
        return False

    elif choice == "1":
        reconnaissance()

    elif choice == "2":
        traffic_generation()

    elif choice == "3":
        stress_testing()

    elif choice == "4":
        exploitation_simulation()

    elif choice == "5":
        show_reports()

    elif choice == "6":
        web_reconnaissance()

    return True


def main():
    banner()

    while True:
        if not menu():
            break

        Prompt.ask(
            "\nPressione ENTER para continuar",
            default=""
        )


if __name__ == "__main__":
    main()
