
import unittest
import tempfile

from pathlib import Path
from unittest.mock import patch

from core import database
from core import campaigns


class TestCampaigns(unittest.TestCase):

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

    def test_create_campaign(self):
        campaign_id = campaigns.create_campaign(
            "Reconhecimento",
            "Campanha de laboratório",
        )

        self.assertGreater(campaign_id, 0)

    def test_list_campaigns(self):
        campaigns.create_campaign("Campanha A")
        campaigns.create_campaign("Campanha B")

        result = campaigns.list_campaigns()

        self.assertEqual(len(result), 2)

    def test_get_campaign(self):
        campaign_id = campaigns.create_campaign("Teste")

        result = campaigns.get_campaign(campaign_id)

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Teste")

    def test_get_missing_campaign(self):
        result = campaigns.get_campaign(999)

        self.assertIsNone(result)

    def test_rejects_invalid_campaign_id(self):
        for invalid_id in (0, -1, "1", True, None):
            with self.subTest(invalid_id=invalid_id):
                with self.assertRaises(ValueError):
                    campaigns.get_campaign(invalid_id)

    def test_create_campaign_execution(self):
        campaign_id = campaigns.create_campaign("Teste")

        execution_id = campaigns.create_campaign_execution(
            campaign_id,
            "reconnaissance",
            "127.0.0.1",
            duration=5,
            workers=1,
        )

        self.assertGreater(execution_id, 0)

    def test_rejects_execution_for_missing_campaign(self):
        with self.assertRaises(ValueError):
            campaigns.create_campaign_execution(
                999,
                "reconnaissance",
                "127.0.0.1",
            )

    def test_list_campaign_executions(self):
        campaign_id = campaigns.create_campaign("Teste")

        campaigns.create_campaign_execution(
            campaign_id,
            "reconnaissance",
            "127.0.0.1",
        )

        result = campaigns.list_campaign_executions(
            campaign_id
        )

        self.assertEqual(len(result), 1)

    def test_update_campaign_execution(self):
        campaign_id = campaigns.create_campaign("Teste")

        execution_id = campaigns.create_campaign_execution(
            campaign_id,
            "reconnaissance",
            "127.0.0.1",
        )

        result = campaigns.update_campaign_execution(
            execution_id,
            "completed",
            "Execução finalizada",
        )

        self.assertTrue(result)

    def test_rejects_invalid_execution_id(self):
        with self.assertRaises(ValueError):
            campaigns.update_campaign_execution(
                0,
                "completed",
            )


if __name__ == "__main__":
    unittest.main()
