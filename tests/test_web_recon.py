
import json
import unittest

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from modules import web_recon


class TestWebReconnaissance(unittest.TestCase):

    def test_get_page_title(self):
        html = "<html><head><title>SOVIK</title></head></html>"

        result = web_recon.get_page_title(html)

        self.assertEqual(result, "SOVIK")

    def test_get_page_title_missing(self):
        result = web_recon.get_page_title("<html></html>")

        self.assertEqual(result, "Não identificado")

    def test_analyze_headers(self):
        headers = {
            "Content-Security-Policy": "default-src 'self'",
            "X-Frame-Options": "DENY",
        }

        result = web_recon.analyze_headers(headers)

        self.assertEqual(len(result), 6)
        self.assertTrue(result[0]["present"])
        self.assertFalse(result[1]["present"])

    @patch("modules.web_recon.validate_http_url")
    def test_validate_target(self, mock_validate):
        mock_validate.return_value = "http://127.0.0.1"

        result = web_recon.validate_target("http://127.0.0.1")

        self.assertEqual(result, "http://127.0.0.1")
        mock_validate.assert_called_once()

    @patch("modules.web_recon.validate_http_url")
    def test_validate_target_rejects_invalid_url(self, mock_validate):
        mock_validate.side_effect = ValueError("URL inválida")

        with self.assertRaises(ValueError):
            web_recon.validate_target("http://example.com")

    @patch("modules.web_recon.requests.get")
    @patch("modules.web_recon.validate_target")
    def test_inspect_endpoint(self, mock_validate, mock_get):
        response = MagicMock()

        response.raw.read.return_value = (
            b"<html><title>Laboratorio</title></html>"
        )

        response.encoding = "utf-8"
        response.status_code = 200
        response.headers = {
            "Server": "Test Server",
            "Content-Type": "text/html",
        }

        mock_get.return_value = response

        result = web_recon.inspect_endpoint(
            "http://127.0.0.1"
        )

        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["title"], "Laboratorio")
        self.assertFalse(result["response_truncated"])

        response.close.assert_called_once()

    @patch("modules.web_recon.requests.options")
    @patch("modules.web_recon.validate_target")
    def test_inspect_methods(self, mock_validate, mock_options):
        response = MagicMock()
        response.headers = {
            "Allow": "GET, POST, OPTIONS"
        }

        mock_options.return_value = response

        result = web_recon.inspect_methods(
            "http://127.0.0.1"
        )

        self.assertEqual(result, "GET, POST, OPTIONS")
        response.close.assert_called_once()

    @patch("modules.web_recon.requests.get")
    @patch("modules.web_recon.validate_target")
    def test_inspect_robots(self, mock_validate, mock_get):
        response = MagicMock()

        response.status_code = 200
        response.raw.read.return_value = b"User-agent: *\nDisallow: /admin"

        mock_get.return_value = response

        result = web_recon.inspect_robots(
            "http://127.0.0.1"
        )

        self.assertEqual(result["status_code"], 200)
        self.assertIn("Disallow", result["content"])

        response.close.assert_called_once()

    def test_save_report(self):
        with TemporaryDirectory() as temp_dir:
            with patch.object(
                web_recon,
                "REPORT_DIR",
                Path(temp_dir),
            ):
                report_path = web_recon.save_report(
                    "http://127.0.0.1",
                    {"status": 200},
                )

                self.assertTrue(report_path.exists())

                with report_path.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    report = json.load(file)

                self.assertEqual(
                    report["module"],
                    "Web Reconnaissance",
                )

                self.assertEqual(
                    report["version"],
                    "2.0.0",
                )

    @patch("modules.web_recon.operations.complete_operation")
    @patch("modules.web_recon.operations.start_operation")
    @patch("modules.web_recon.display_results")
    @patch("modules.web_recon.save_report")
    @patch("modules.web_recon.inspect_robots")
    @patch("modules.web_recon.inspect_methods")
    @patch("modules.web_recon.inspect_endpoint")
    @patch("modules.web_recon.select_campaign")
    @patch("modules.web_recon.validate_target")
    @patch("builtins.input")
    def test_web_reconnaissance_completes_operation(
        self,
        mock_input,
        mock_validate,
        mock_campaign,
        mock_endpoint,
        mock_methods,
        mock_robots,
        mock_report,
        mock_display,
        mock_start,
        mock_complete,
    ):
        mock_input.return_value = "http://127.0.0.1"
        mock_campaign.return_value = None
        mock_start.return_value = 42

        mock_endpoint.return_value = {
            "status_code": 200,
            "title": "Laboratorio",
            "security_headers": [],
        }

        mock_methods.return_value = "GET"
        mock_robots.return_value = {
            "status_code": 200,
            "content": "User-agent: *",
        }

        mock_report.return_value = Path("teste.json")
        mock_complete.return_value = True

        web_recon.web_reconnaissance()

        mock_start.assert_called_once()
        mock_complete.assert_called_once()

        self.assertEqual(
            mock_start.call_args.kwargs["module"],
            "web_reconnaissance",
        )

        self.assertEqual(
            mock_complete.call_args.args[0],
            42,
        )

    @patch("modules.web_recon.operations.fail_operation")
    @patch("modules.web_recon.operations.start_operation")
    @patch("modules.web_recon.select_campaign")
    @patch("modules.web_recon.validate_target")
    @patch("builtins.input")
    def test_web_reconnaissance_records_failure(
        self,
        mock_input,
        mock_validate,
        mock_campaign,
        mock_start,
        mock_fail,
    ):
        mock_input.return_value = "http://127.0.0.1"
        mock_campaign.return_value = None
        mock_start.return_value = 99

        with patch(
            "modules.web_recon.inspect_endpoint",
            side_effect=RuntimeError("Erro simulado"),
        ):
            web_recon.web_reconnaissance()

        mock_fail.assert_called_once()

        self.assertEqual(
            mock_fail.call_args.args[0],
            99,
        )


if __name__ == "__main__":
    unittest.main()
