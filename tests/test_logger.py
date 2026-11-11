
import logging
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from core.logger import get_logger, log_event


class TestLogger(unittest.TestCase):

    def test_get_logger_returns_logger(self):
        logger = get_logger("test_logger")

        self.assertIsInstance(logger, logging.Logger)

    def test_logger_level_is_info(self):
        logger = get_logger("test_level")

        self.assertEqual(logger.level, logging.INFO)

    def test_logger_does_not_propagate(self):
        logger = get_logger("test_propagation")

        self.assertFalse(logger.propagate)

    def test_log_event_accepts_valid_levels(self):
        for level in (
            "debug",
            "info",
            "warning",
            "error",
            "critical",
        ):
            with self.subTest(level=level):
                log_event("Teste automatizado", level)

    def test_log_event_rejects_invalid_level(self):
        with self.assertRaises(ValueError):
            log_event("Teste inválido", "unknown")

    def test_log_event_rejects_empty_level(self):
        with self.assertRaises(ValueError):
            log_event("Teste inválido", "")

    def test_log_file_path_is_inside_logs_directory(self):
        from core.logger import LOG_FILE

        self.assertEqual(LOG_FILE.name, "blackout-lab.log")
        self.assertEqual(LOG_FILE.parent.name, "logs")


if __name__ == "__main__":
    unittest.main()
