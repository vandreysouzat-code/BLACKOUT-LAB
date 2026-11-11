
"""
Sistema central de logs do SOVIK 2.0.
"""

import logging

from logging.handlers import RotatingFileHandler

from core.config import LOGS_DIR, APP_NAME


LOG_FILE = LOGS_DIR / "sovik.log"

_logger = None


def get_logger(name="sovik"):
    """Retorna um logger configurado."""

    global _logger

    if _logger is not None and name == "sovik":
        return _logger

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if name == "sovik":
        _logger = logger

    return logger


def log_event(message, level="info"):
    """Registra um evento da plataforma."""

    logger = get_logger(APP_NAME)

    levels = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical,
    }

    selected_level = levels.get(level.lower())

    if selected_level is None:
        raise ValueError("Nível de log inválido.")

    selected_level(message)
