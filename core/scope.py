
import ipaddress
import socket

from urllib.parse import urlparse


ALLOWED_SCHEMES = {"http", "https"}


def is_allowed_ip(address):
    """Verifica se o IP pertence a uma faixa permitida para laboratorio."""

    ip = ipaddress.ip_address(address)

    if ip.is_multicast or ip.is_unspecified or ip.is_reserved:
        return False

    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
    )


def resolve_host(host, port=None):
    """Resolve um host e valida todos os enderecos encontrados."""

    if not isinstance(host, str) or not host.strip():
        raise ValueError("Hostname nao informado.")

    host = host.strip().lower()

    if host == "localhost":
        return ["127.0.0.1", "::1"]

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None

    if address is not None:
        if not is_allowed_ip(address):
            raise ValueError(
                "Somente IPs privados ou locais sao permitidos."
            )

        return [str(address)]

    try:
        results = socket.getaddrinfo(
            host,
            port,
            type=socket.SOCK_STREAM
        )
    except socket.gaierror as error:
        raise ValueError(
            "Nao foi possivel resolver o hostname."
        ) from error

    addresses = sorted({
        item[4][0]
        for item in results
    })

    if not addresses:
        raise ValueError("Nenhum endereco IP encontrado.")

    for address in addresses:
        if not is_allowed_ip(address):
            raise ValueError(
                "O hostname resolve para um endereco nao permitido."
            )

    return addresses


def validate_host(target):
    """Valida IP ou hostname para reconhecimento."""

    if not isinstance(target, str):
        raise ValueError("Informe um IP ou hostname valido.")

    target = target.strip()

    if not target or "://" in target or "/" in target:
        raise ValueError("Informe somente um IP ou hostname.")

    return resolve_host(target)


def validate_http_url(url, allow_hostname=True):
    """Valida URL HTTP/HTTPS para ambientes de laboratorio."""

    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL nao informada.")

    url = url.strip()

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as error:
        raise ValueError("URL ou porta invalida.") from error

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValueError("Use uma URL HTTP ou HTTPS.")

    if not hostname:
        raise ValueError("Hostname nao informado.")

    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Credenciais na URL nao sao permitidas.")

    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Porta invalida.")

    if not allow_hostname:
        if hostname.lower() != "localhost":
            try:
                ipaddress.ip_address(hostname)
            except ValueError as error:
                raise ValueError(
                    "Este modulo aceita somente IPs literais ou localhost."
                ) from error

    resolve_host(
        hostname,
        port or (443 if parsed.scheme.lower() == "https" else 80)
    )

    return url
