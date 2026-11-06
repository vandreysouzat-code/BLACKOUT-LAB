
import socket
import ipaddress
import json
import re

from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
MAX_PORTS = 20
MAX_WORKERS = 20


def validate_target(target):
    target = target.strip()

    if not target or "://" in target or "/" in target:
        raise ValueError("Informe somente um IP ou hostname.")

    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(
                target, None, type=socket.SOCK_STREAM
            )
        }
    except socket.gaierror:
        raise ValueError("Não foi possível resolver o alvo.")

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
                "Este módulo aceita somente IPs locais "
                "ou redes privadas do laboratório."
            )

    return sorted(addresses)


def get_service(port):
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def scan_port(target, port, timeout=1):
    try:
        with socket.create_connection(
            (target, port),
            timeout=timeout
        ):
            status = "open"
    except (socket.timeout, ConnectionRefusedError, OSError):
        status = "closed"

    return {
        "port": port,
        "protocol": "TCP",
        "status": status,
        "service": get_service(port)
    }


def scan_ports(target, ports):
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
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc)

    safe_target = re.sub(r"[^a-zA-Z0-9_-]", "_", target)

    report = {
        "tool": "BLACKOUT LAB",
        "module": "Reconnaissance",
        "target": target,
        "resolved_addresses": addresses,
        "timestamp_utc": timestamp.isoformat(),
        "results": results
    }

    filename = (
        f"recon_{safe_target}_"
        f"{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    )

    report_path = REPORT_DIR / filename

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    return report_path


def reconnaissance():
    print("\n=== BLACKOUT LAB | RECONNAISSANCE ===")
    print("Somente alvos próprios ou autorizados.")
    print("Escopo: localhost e redes privadas.\n")

    target = input("IP ou hostname: ").strip()

    try:
        addresses = validate_target(target)

        print("\nEndereços encontrados:")
        for address in addresses:
            print(f" - {address}")

        ports_input = input(
            "\nPortas TCP (exemplo: 80,443,5000): "
        ).strip()

        ports = sorted(set(
            int(port.strip())
            for port in ports_input.split(",")
        ))

        if not ports or any(
            port < 1 or port > 65535 for port in ports
        ):
            raise ValueError("Portas inválidas.")

        if len(ports) > MAX_PORTS:
            raise ValueError(
                f"Limite de {MAX_PORTS} portas por análise."
            )

        print(f"\nAnalisando {target}...\n")

        results = scan_ports(target, ports)

        for result in results:
            print(
                f"TCP {result['port']}: "
                f"{result['status'].upper()} | "
                f"Serviço: {result['service']}"
            )

        report_path = save_report(
            target,
            addresses,
            results
        )

        print("\n[+] Relatório salvo:")
        print(report_path)

    except ValueError as error:
        print(f"\n[!] Erro: {error}")


if __name__ == "__main__":
    reconnaissance()
