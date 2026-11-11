
"""
Módulo de reconhecimento TCP do SOVIK 2.0.

Realiza reconhecimento limitado de portas TCP em alvos
validados pelo Core Engine e registra as operações.
"""

import json
import re
import socket

from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.scope import validate_host
from core import operations, campaigns
from core.logger import get_logger


REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"

MAX_PORTS = 20
MAX_WORKERS = 20

logger = get_logger("sovik.recon")


def validate_target(target):
    """Valida o alvo usando o escopo central do Core Engine."""

    try:
        return validate_host(target)

    except ValueError as error:
        raise ValueError(
            f"Alvo fora do escopo permitido: {error}"
        ) from error


def get_service(port):
    """Identifica o serviço associado a uma porta TCP."""

    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def scan_port(target, port, timeout=1):
    """Verifica uma porta TCP em um endereço IP validado."""

    try:
        with socket.create_connection(
            (target, port),
            timeout=timeout,
        ):
            status = "open"

    except (socket.timeout, ConnectionRefusedError, OSError):
        status = "closed"

    return {
        "port": port,
        "protocol": "TCP",
        "status": status,
        "service": get_service(port),
    }


def scan_ports(target, ports):
    """Executa uma análise limitada de portas TCP."""

    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = [
            executor.submit(scan_port, target, port)
            for port in ports
        ]

        for task in as_completed(tasks):
            results.append(task.result())

    return sorted(results, key=lambda item: item["port"])


def save_report(target, addresses, results):
    """Salva o relatório de reconhecimento em JSON."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc)

    safe_target = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        target,
    )

    report = {
        "tool": "SOVIK",
        "version": "2.0.0",
        "module": "Reconnaissance",
        "target": target,
        "resolved_addresses": addresses,
        "timestamp_utc": timestamp.isoformat(),
        "results": results,
    }

    filename = (
        f"recon_{safe_target}_"
        f"{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    )

    report_path = REPORT_DIR / filename

    with report_path.open("w", encoding="utf-8") as file:
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
        print("\nNenhuma campanha cadastrada.")
        return None

    print("\nCampanhas disponíveis:")

    for campaign in registered_campaigns:
        print(
            f" [{campaign['id']}] "
            f"{campaign['name']}"
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


def reconnaissance():
    """Executa o reconhecimento e registra sua operação."""

    print("\n=== SOVIK | RECONNAISSANCE ===")
    print("Somente alvos próprios ou autorizados.")
    print("Escopo: localhost e redes privadas.\n")

    execution_id = None

    try:
        target = input("IP ou hostname: ").strip()

        if not target:
            raise ValueError("O alvo é obrigatório.")

        addresses = validate_target(target)

        if not addresses:
            raise ValueError(
                "Nenhum endereço válido foi encontrado."
            )

        print("\nEndereços encontrados:")

        for address in addresses:
            print(f" - {address}")

        ports_input = input(
            "\nPortas TCP (exemplo: 80,443,5000): "
        ).strip()

        try:
            ports = sorted(set(
                int(port.strip())
                for port in ports_input.split(",")
            ))
        except ValueError as error:
            raise ValueError(
                "Informe somente números de portas válidos."
            ) from error

        if not ports or any(
            port < 1 or port > 65535 for port in ports
        ):
            raise ValueError("Portas inválidas.")

        if len(ports) > MAX_PORTS:
            raise ValueError(
                f"Limite de {MAX_PORTS} portas por análise."
            )

        campaign_id = select_campaign()

        execution_id = operations.start_operation(
            module="reconnaissance",
            target=target,
            campaign_id=campaign_id,
        )

        print(
            f"\nExecução registrada: #{execution_id}"
        )

        print(f"\nAnalisando {target}...\n")

        results = []

        for address in addresses:
            print(f"Analisando endereço: {address}")

            address_results = scan_ports(
                address,
                ports,
            )

            for result in address_results:
                result["address"] = address

                print(
                    f"TCP {result['port']}: "
                    f"{result['status'].upper()} | "
                    f"Serviço: {result['service']}"
                )

            results.extend(address_results)

        report_path = save_report(
            target,
            addresses,
            results,
        )

        operations.complete_operation(
            execution_id,
            f"Análise concluída. "
            f"{len(results)} verificações realizadas. "
            f"Relatório: {report_path.name}",
        )

        print("\n[+] Relatório salvo:")
        print(report_path)

        print(
            f"\n[+] Execução #{execution_id} concluída."
        )

    except ValueError as error:
        if execution_id is not None:
            operations.fail_operation(
                execution_id,
                error,
            )

        print(f"\n[!] Erro: {error}")

    except Exception as error:
        if execution_id is not None:
            operations.fail_operation(
                execution_id,
                error,
            )

        logger.exception(
            "Erro inesperado no módulo Reconnaissance."
        )

        print(
            "\n[!] Falha inesperada. "
            "Consulte os logs do SOVIK."
        )


if __name__ == "__main__":
    reconnaissance()
