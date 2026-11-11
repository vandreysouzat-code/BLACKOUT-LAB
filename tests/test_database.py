
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from core import database


class TestDatabase(unittest.TestCase):

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

    def test_database_is_created(self):
        self.assertTrue(
            (self.temp_path / "test.db").exists()
        )

    def test_create_campaign(self):
        campaign_id = database.create_campaign(
            "Teste",
            "Campanha automatizada",
        )

        self.assertGreater(campaign_id, 0)

    def test_rejects_empty_campaign_name(self):
        with self.assertRaises(ValueError):
            database.create_campaign("")

    def test_rejects_invalid_description(self):
        with self.assertRaises(ValueError):
            database.create_campaign("Teste", 123)

    def test_list_campaigns(self):
        database.create_campaign("Campanha A")
        database.create_campaign("Campanha B")

        campaigns = database.list_campaigns()

        self.assertEqual(len(campaigns), 2)

    def test_create_execution(self):
        execution_id = database.create_execution(
            "reconnaissance",
            "127.0.0.1",
        )

        self.assertGreater(execution_id, 0)

    def test_rejects_empty_module(self):
        with self.assertRaises(ValueError):
            database.create_execution("", "127.0.0.1")

    def test_rejects_empty_target(self):
        with self.assertRaises(ValueError):
            database.create_execution("reconnaissance", "")

    def test_rejects_invalid_campaign_reference(self):
        with self.assertRaises(Exception):
            database.create_execution(
                "reconnaissance",
                "127.0.0.1",
                campaign_id=999,
            )

    def test_update_execution_status(self):
        execution_id = database.create_execution(
            "reconnaissance",
            "127.0.0.1",
        )

        self.assertTrue(
            database.update_execution(execution_id, "running")
        )

        self.assertTrue(
            database.update_execution(
                execution_id,
                "completed",
                "Teste concluído",
            )
        )

        execution = database.list_executions()[0]

        self.assertEqual(execution["status"], "completed")
        self.assertEqual(execution["result"], "Teste concluído")
        self.assertIsNotNone(execution["started_at"])
        self.assertIsNotNone(execution["finished_at"])

    def test_rejects_invalid_status(self):
        with self.assertRaises(ValueError):
            database.update_execution(1, "unknown")

    def test_returns_false_for_missing_execution(self):
        self.assertFalse(
            database.update_execution(999, "running")
        )

    def test_list_executions_by_campaign(self):
        campaign_a = database.create_campaign("Campanha A")
        campaign_b = database.create_campaign("Campanha B")

        database.create_execution(
            "reconnaissance",
            "127.0.0.1",
            campaign_a,
        )

        database.create_execution(
            "web_recon",
            "127.0.0.1",
            campaign_b,
        )

        executions = database.list_executions(campaign_a)

        self.assertEqual(len(executions), 1)
        self.assertEqual(
            executions[0]["campaign_id"],
            campaign_a,
        )

    def test_foreign_key_is_enabled(self):
        with database.get_connection() as connection:
            result = connection.execute(
                "PRAGMA foreign_keys"
            ).fetchone()[0]

        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
