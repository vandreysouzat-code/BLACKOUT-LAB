
"""
Gerenciador central de operações do BLACKOUT LAB 2.0.

Controla o registro, início, conclusão, cancelamento
e falha das operações no banco de dados.
"""

from core import database
from core.logger import get_logger


logger = get_logger("blackout.operations")


TERMINAL_STATUSES = {
    "completed",
    "cancelled",
    "failed",
}


def start_operation(
    module,
    target,
    campaign_id=None,
    duration=None,
    workers=None,
):
    """
    Registra e inicia uma operação.

    Retorna o ID da execução no banco de dados.
    """

    if not isinstance(module, str) or not module.strip():
        raise ValueError("O nome do módulo é obrigatório.")

    if not isinstance(target, str) or not target.strip():
        raise ValueError("O alvo é obrigatório.")

    execution_id = database.create_execution(
        module=module,
        target=target,
        campaign_id=campaign_id,
        duration=duration,
        workers=workers,
    )

    updated = database.update_execution(
        execution_id,
        "running",
        "Operação iniciada.",
    )

    if not updated:
        raise RuntimeError(
            "Não foi possível iniciar a operação."
        )

    logger.info(
        "Operação iniciada: ID=%s | Módulo=%s | Alvo=%s",
        execution_id,
        module,
        target,
    )

    return execution_id


def complete_operation(execution_id, result=""):
    """Finaliza uma operação com sucesso."""

    updated = database.update_execution(
        execution_id,
        "completed",
        result,
    )

    if updated:
        logger.info(
            "Operação concluída: ID=%s",
            execution_id,
        )

    return updated


def cancel_operation(execution_id, result=""):
    """Registra o cancelamento de uma operação."""

    updated = database.update_execution(
        execution_id,
        "cancelled",
        result,
    )

    if updated:
        logger.warning(
            "Operação cancelada: ID=%s",
            execution_id,
        )

    return updated


def fail_operation(execution_id, error):
    """Registra uma falha durante uma operação."""

    error_message = str(error)

    updated = database.update_execution(
        execution_id,
        "failed",
        error_message,
    )

    if updated:
        logger.error(
            "Falha na operação: ID=%s | Erro=%s",
            execution_id,
            error_message,
        )

    return updated
