
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from core import database
from core import operations


class TestOperations(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        self.data_patch = patch.object(
            database,
            "DATA_DIR",
            self.temp_path,
        )

        self.path_patch = patch.object(
            database,
            "DATABASE_PATH",
            self.temp_path / "test.db",
        )

        self.data_patch.start()
        self.path_patch.start()

        self.addCleanup(self.data_patch.stop)
        self.addCleanup(self.path_patch.stop)
        self.addCleanup(self.temp_dir.cleanup)

        database.initialize_database()

    def test_start_operation(self):
        execution_id = operations.start_operation(
            "reconnaissance",
            "127.0.0.1",
        )

        execution = database.list_executions()[0]

        self.assertGreater(execution_id, 0)
        self.assertEqual(execution["status"], "running")
        self.assertEqual(
            execution["result"],
            "Operação iniciada.",
        )

    def test_start_operation_with_campaign(self):
        campaign_id = database.create_campaign("Teste")

        execution_id = operations.start_operation(
            "reconnaissance",
            "127.0.0.1",
            campaign_id=campaign_id,
        )

        execution = database.list_executions()[0]

        self.assertEqual(
            execution["campaign_id"],
            campaign_id,
        )

    def test_rejects_empty_module(self):
        with self.assertRaises(ValueError):
            operations.start_operation(
                "",
                "127.0.0.1",
            )

    def test_rejects_empty_target(self):
        with self.assertRaises(ValueError):
            operations.start_operation(
                "reconnaissance",
                "",
            )

    def test_complete_operation(self):
        execution_id = operations.start_operation(
            "reconnaissance",
            "127.0.0.1",
        )

        result = operations.complete_operation(
            execution_id,
            "Análise concluída.",
        )

        execution = database.list_executions()[0]

        self.assertTrue(result)
        self.assertEqual(execution["status"], "completed")
        self.assertEqual(
            execution["result"],
            "Análise concluída.",
        )

    def test_cancel_operation(self):
        execution_id = operations.start_operation(
            "reconnaissance",
            "127.0.0.1",
        )

        result = operations.cancel_operation(
            execution_id,
            "Cancelado pelo usuário.",
        )

        execution = database.list_executions()[0]

        self.assertTrue(result)
        self.assertEqual(execution["status"], "cancelled")

    def test_fail_operation(self):
        execution_id = operations.start_operation(
            "reconnaissance",
            "127.0.0.1",
        )

        result = operations.fail_operation(
            execution_id,
            "Erro de conexão.",
        )

        execution = database.list_executions()[0]

        self.assertTrue(result)
        self.assertEqual(execution["status"], "failed")
        self.assertEqual(
            execution["result"],
            "Erro de conexão.",
        )

    def test_complete_missing_operation(self):
        self.assertFalse(
            operations.complete_operation(999)
        )

    def test_cancel_missing_operation(self):
        self.assertFalse(
            operations.cancel_operation(999)
        )

    def test_fail_missing_operation(self):
        self.assertFalse(
            operations.fail_operation(
                999,
                "Erro de teste.",
            )
        )


if __name__ == "__main__":
    unittest.main()
