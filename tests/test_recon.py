
import unittest

from pathlib import Path
from unittest.mock import patch

from modules import recon


class TestReconnaissance(unittest.TestCase):

    @patch("modules.recon.validate_host")
    def test_validate_target(self, mock_validate):
        mock_validate.return_value = ["127.0.0.1"]

        result = recon.validate_target("127.0.0.1")

        self.assertEqual(result, ["127.0.0.1"])

    @patch("modules.recon.validate_host")
    def test_rejects_invalid_target(self, mock_validate):
        mock_validate.side_effect = ValueError("IP público")

        with self.assertRaises(ValueError):
            recon.validate_target("192.0.2.1")

    @patch("modules.recon.socket.create_connection")
    def test_scan_port_open(self, mock_connection):
        from unittest.mock import MagicMock

        mock_connection.return_value.__enter__ = MagicMock()
        mock_connection.return_value.__exit__ = MagicMock(
            return_value=False
        )

        result = recon.scan_port("127.0.0.1", 80)

        self.assertEqual(result["status"], "open")
        self.assertEqual(result["protocol"], "TCP")

    @patch("modules.recon.socket.create_connection")
    def test_scan_port_closed(self, mock_connection):
        mock_connection.side_effect = ConnectionRefusedError

        result = recon.scan_port("127.0.0.1", 80)

        self.assertEqual(result["status"], "closed")

    @patch("modules.recon.get_service")
    @patch("modules.recon.scan_port")
    def test_scan_ports(self, mock_scan, mock_service):
        mock_scan.side_effect = [
            {"port": 443, "status": "open"},
            {"port": 80, "status": "closed"},
        ]

        mock_service.return_value = "unknown"

        result = recon.scan_ports(
            "127.0.0.1",
            [443, 80],
        )

        self.assertEqual(
            [item["port"] for item in result],
            [80, 443],
        )

    @patch("modules.recon.REPORT_DIR")
    def test_save_report(self, mock_report_dir):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            with patch.object(
                recon,
                "REPORT_DIR",
                Path(temp_dir),
            ):
                report_path = recon.save_report(
                    "127.0.0.1",
                    ["127.0.0.1"],
                    [{"port": 80, "status": "open"}],
                )

                self.assertTrue(report_path.exists())

                import json

                with report_path.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    report = json.load(file)

                self.assertEqual(
                    report["module"],
                    "Reconnaissance",
                )

                self.assertEqual(
                    report["version"],
                    "2.0.0",
                )

    @patch("modules.recon.operations.complete_operation")
    @patch("modules.recon.operations.start_operation")
    @patch("modules.recon.save_report")
    @patch("modules.recon.scan_ports")
    @patch("modules.recon.select_campaign")
    @patch("modules.recon.validate_target")
    @patch("builtins.input")
    def test_reconnaissance_completes_operation(
        self,
        mock_input,
        mock_validate,
        mock_campaign,
        mock_scan,
        mock_report,
        mock_start,
        mock_complete,
    ):
        mock_input.side_effect = [
            "127.0.0.1",
            "80",
        ]

        mock_validate.return_value = ["127.0.0.1"]
        mock_campaign.return_value = None

        mock_start.return_value = 42

        mock_scan.return_value = [
            {
                "port": 80,
                "protocol": "TCP",
                "status": "open",
                "service": "http",
            }
        ]

        mock_report.return_value = Path("teste.json")

        recon.reconnaissance()

        mock_start.assert_called_once()
        mock_complete.assert_called_once()

        self.assertEqual(
            mock_start.call_args.kwargs["module"],
            "reconnaissance",
        )

        self.assertEqual(
            mock_complete.call_args.args[0],
            42,
        )

    @patch("modules.recon.operations.fail_operation")
    @patch("modules.recon.operations.start_operation")
    @patch("modules.recon.select_campaign")
    @patch("modules.recon.validate_target")
    @patch("builtins.input")
    def test_reconnaissance_records_failure(
        self,
        mock_input,
        mock_validate,
        mock_campaign,
        mock_start,
        mock_fail,
    ):
        mock_input.side_effect = [
            "127.0.0.1",
            "80",
        ]

        mock_validate.return_value = ["127.0.0.1"]
        mock_campaign.return_value = None
        mock_start.return_value = 99

        with patch(
            "modules.recon.scan_ports",
            side_effect=RuntimeError("Erro simulado"),
        ):
            recon.reconnaissance()

        mock_fail.assert_called_once()

        self.assertEqual(
            mock_fail.call_args.args[0],
            99,
        )


if __name__ == "__main__":
    unittest.main()
