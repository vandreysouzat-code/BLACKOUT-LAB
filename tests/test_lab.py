
import unittest
from unittest.mock import patch

from core import config
from core.lab import validate_lab_target, validate_lab_settings


class TestLabTarget(unittest.TestCase):

    def test_accepts_loopback(self):
        self.assertEqual(
            validate_lab_target("127.0.0.1"),
            "127.0.0.1"
        )

    def test_accepts_private_ip(self):
        self.assertEqual(
            validate_lab_target("192.168.56.10"),
            "192.168.56.10"
        )

    def test_rejects_public_ip(self):
        with self.assertRaises(ValueError):
            validate_lab_target("8.8.8.8")

    def test_rejects_hostname(self):
        with self.assertRaises(ValueError):
            validate_lab_target("localhost")

    def test_rejects_empty_target(self):
        with self.assertRaises(ValueError):
            validate_lab_target("")


class TestLabSettings(unittest.TestCase):

    @patch("core.lab.config.DOS_LAB_ENABLED", False)
    def test_rejects_disabled_lab(self):
        with self.assertRaises(RuntimeError):
            validate_lab_settings(
                "127.0.0.1", 5, 1, True, True
            )

    @patch("core.lab.config.DOS_LAB_ENABLED", True)
    def test_requires_authorization(self):
        with self.assertRaises(PermissionError):
            validate_lab_settings(
                "127.0.0.1", 5, 1, False, True
            )

    @patch("core.lab.config.DOS_LAB_ENABLED", True)
    def test_requires_isolation(self):
        with self.assertRaises(PermissionError):
            validate_lab_settings(
                "127.0.0.1", 5, 1, True, False
            )

    @patch("core.lab.config.DOS_LAB_ENABLED", True)
    def test_accepts_valid_settings(self):
        result = validate_lab_settings(
            "127.0.0.1", 5, 1, True, True
        )

        self.assertTrue(result["validated"])
        self.assertEqual(result["target"], "127.0.0.1")

    @patch("core.lab.config.DOS_LAB_ENABLED", True)
    def test_accepts_maximum_duration(self):
        result = validate_lab_settings(
            "127.0.0.1",
            config.DOS_LAB_MAX_DURATION,
            1,
            True,
            True
        )

        self.assertEqual(
            result["duration"],
            config.DOS_LAB_MAX_DURATION
        )

    @patch("core.lab.config.DOS_LAB_ENABLED", True)
    def test_rejects_excessive_duration(self):
        with self.assertRaises(ValueError):
            validate_lab_settings(
                "127.0.0.1",
                config.DOS_LAB_MAX_DURATION + 1,
                1,
                True,
                True
            )

    @patch("core.lab.config.DOS_LAB_ENABLED", True)
    def test_rejects_excessive_workers(self):
        with self.assertRaises(ValueError):
            validate_lab_settings(
                "127.0.0.1", 5, config.DOS_LAB_MAX_WORKERS + 1,
                True, True
            )

    @patch("core.lab.config.DOS_LAB_ENABLED", True)
    def test_rejects_boolean_duration(self):
        with self.assertRaises(ValueError):
            validate_lab_settings(
                "127.0.0.1", True, 1, True, True
            )

    @patch("core.lab.config.DOS_LAB_ENABLED", True)
    def test_rejects_public_target(self):
        with self.assertRaises(ValueError):
            validate_lab_settings(
                "8.8.8.8", 5, 1, True, True
            )


if __name__ == "__main__":
    unittest.main()
