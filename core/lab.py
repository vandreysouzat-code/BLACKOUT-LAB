
"""
Controles de segurança do laboratório BLACKOUT LAB.

Este módulo valida as condições necessárias antes de
permitir a preparação de um experimento autorizado.

Não executa nem gera tráfego de rede.
"""

import ipaddress

from core import config
from core.scope import is_allowed_ip


def validate_lab_target(target):
    """
    Aceita somente IPs literais privados ou locais.

    Hostnames não são aceitos para evitar depender de
    resoluções DNS durante a validação do laboratório.
    """

    if not isinstance(target, str) or not target.strip():
        raise ValueError("Informe o IP do alvo.")

    target = target.strip()

    try:
        address = ipaddress.ip_address(target)
    except ValueError as error:
        raise ValueError(
            "O laboratório aceita somente endereços IP literais."
        ) from error

    if not is_allowed_ip(address):
        raise ValueError(
            "O alvo precisa utilizar um endereço IP privado ou local."
        )

    return str(address)


def validate_lab_settings(
    target,
    duration,
    workers,
    authorization_confirmed=False,
    isolation_confirmed=False,
):
    """
    Valida as condições de segurança de um experimento.

    Não inicia conexões nem executa testes de tráfego.
    """

    if not config.DOS_LAB_ENABLED:
        raise RuntimeError(
            "Laboratório desabilitado na configuração."
        )

    if config.DOS_LAB_REQUIRE_EXPLICIT_SCOPE:
        if authorization_confirmed is not True:
            raise PermissionError(
                "É necessário confirmar a autorização do experimento."
            )

    if config.DOS_LAB_REQUIRE_ISOLATED_NETWORK:
        if isolation_confirmed is not True:
            raise PermissionError(
                "É necessário confirmar o isolamento da rede."
            )

    validated_target = validate_lab_target(target)

    if isinstance(duration, bool) or not isinstance(duration, int):
        raise ValueError("A duração deve ser um número inteiro.")

    if not 1 <= duration <= config.DOS_LAB_MAX_DURATION:
        raise ValueError(
            f"A duração deve estar entre 1 e "
            f"{config.DOS_LAB_MAX_DURATION} segundos."
        )

    if isinstance(workers, bool) or not isinstance(workers, int):
        raise ValueError("A quantidade de workers deve ser inteira.")

    if not 1 <= workers <= config.DOS_LAB_MAX_WORKERS:
        raise ValueError(
            f"A quantidade de workers deve estar entre 1 e "
            f"{config.DOS_LAB_MAX_WORKERS}."
        )

    return {
        "target": validated_target,
        "duration": duration,
        "workers": workers,
        "authorization_confirmed": True,
        "isolation_confirmed": True,
        "validated": True,
    }
