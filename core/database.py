
"""
Banco de dados central do BLACKOUT LAB 2.0.

Armazena campanhas e histórico de execuções usando SQLite.
"""

import sqlite3

from contextlib import contextmanager
from datetime import datetime, timezone

from core.config import DATA_DIR


DATABASE_PATH = DATA_DIR / "blackout_lab.db"


@contextmanager
def get_connection():
    """Abre, gerencia e fecha uma conexão com o banco."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10,
    )

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def initialize_database():
    """Cria as tabelas necessárias para a plataforma."""

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'created',
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                module TEXT NOT NULL,
                target TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                duration INTEGER,
                workers INTEGER,
                started_at TEXT,
                finished_at TEXT,
                result TEXT DEFAULT '',
                FOREIGN KEY (campaign_id)
                    REFERENCES campaigns(id)
                    ON DELETE SET NULL
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_executions_campaign
            ON executions(campaign_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_executions_status
            ON executions(status)
        """)


def create_campaign(name, description=""):
    """Registra uma nova campanha."""

    if not isinstance(name, str) or not name.strip():
        raise ValueError("O nome da campanha é obrigatório.")

    if not isinstance(description, str):
        raise ValueError("A descrição deve ser um texto.")

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO campaigns (
                name,
                description,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (name.strip(), description.strip(), created_at),
        )

        return cursor.lastrowid


def create_execution(
    module,
    target,
    campaign_id=None,
    duration=None,
    workers=None,
):
    """Registra uma execução."""

    if not isinstance(module, str) or not module.strip():
        raise ValueError("O módulo é obrigatório.")

    if not isinstance(target, str) or not target.strip():
        raise ValueError("O alvo é obrigatório.")

    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO executions (
                campaign_id,
                module,
                target,
                duration,
                workers
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                campaign_id,
                module.strip(),
                target.strip(),
                duration,
                workers,
            ),
        )

        return cursor.lastrowid


def update_execution(execution_id, status, result=""):
    """Atualiza o estado de uma execução."""

    allowed_statuses = {
        "pending",
        "running",
        "completed",
        "cancelled",
        "failed",
    }

    if status not in allowed_statuses:
        raise ValueError("Status de execução inválido.")

    if not isinstance(result, str):
        raise ValueError("O resultado deve ser um texto.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        if status == "running":
            cursor = connection.execute(
                """
                UPDATE executions
                SET status = ?, started_at = ?, result = ?
                WHERE id = ?
                """,
                (status, now, result, execution_id),
            )

        elif status in {"completed", "cancelled", "failed"}:
            cursor = connection.execute(
                """
                UPDATE executions
                SET status = ?, finished_at = ?, result = ?
                WHERE id = ?
                """,
                (status, now, result, execution_id),
            )

        else:
            cursor = connection.execute(
                """
                UPDATE executions
                SET status = ?, result = ?
                WHERE id = ?
                """,
                (status, result, execution_id),
            )

        return cursor.rowcount > 0


def list_campaigns():
    """Retorna as campanhas cadastradas."""

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM campaigns
            ORDER BY id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]


def list_executions(campaign_id=None):
    """Retorna o histórico de execuções."""

    with get_connection() as connection:

        if campaign_id is None:
            rows = connection.execute(
                """
                SELECT *
                FROM executions
                ORDER BY id DESC
                """
            ).fetchall()

        else:
            rows = connection.execute(
                """
                SELECT *
                FROM executions
                WHERE campaign_id = ?
                ORDER BY id DESC
                """,
                (campaign_id,),
            ).fetchall()

        return [dict(row) for row in rows]
