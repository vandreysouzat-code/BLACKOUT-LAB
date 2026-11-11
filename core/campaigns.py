
"""
Serviço de gerenciamento de campanhas do BLACKOUT LAB 2.0.

Centraliza as operações de campanhas e suas execuções,
utilizando a camada de banco de dados.
"""

from core import database


def _validate_id(value, field_name):
    """Valida identificadores numéricos positivos."""

    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise ValueError(
            f"{field_name} deve ser um número inteiro positivo."
        )


def create_campaign(name, description=""):
    """Cria uma campanha."""

    return database.create_campaign(
        name=name,
        description=description,
    )


def list_campaigns():
    """Lista todas as campanhas."""

    return database.list_campaigns()


def get_campaign(campaign_id):
    """Busca uma campanha pelo identificador."""

    _validate_id(campaign_id, "ID da campanha")

    campaigns = database.list_campaigns()

    for campaign in campaigns:
        if campaign["id"] == campaign_id:
            return campaign

    return None


def create_campaign_execution(
    campaign_id,
    module,
    target,
    duration=None,
    workers=None,
):
    """Registra uma execução vinculada a uma campanha."""

    _validate_id(campaign_id, "ID da campanha")

    campaign = get_campaign(campaign_id)

    if campaign is None:
        raise ValueError("Campanha não encontrada.")

    return database.create_execution(
        module=module,
        target=target,
        campaign_id=campaign_id,
        duration=duration,
        workers=workers,
    )


def list_campaign_executions(campaign_id):
    """Lista as execuções de uma campanha."""

    _validate_id(campaign_id, "ID da campanha")

    return database.list_executions(
        campaign_id=campaign_id,
    )


def update_campaign_execution(
    execution_id,
    status,
    result="",
):
    """Atualiza uma execução."""

    _validate_id(execution_id, "ID da execução")

    return database.update_execution(
        execution_id=execution_id,
        status=status,
        result=result,
    )
