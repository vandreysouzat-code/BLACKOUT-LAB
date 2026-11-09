
import io
import json
import socket
import tempfile
import unittest

from pathlib import Path
from unittest.mock import MagicMock, patch

from modules import web_recon


class FakeRaw(io.BytesIO):
    """Simula a resposta HTTP do urllib3."""

    def read(self, amount=-1, decode_content=False):
        return super().read(amount)


class TestTitleParser(unittest.TestCase):

    def test_extract_title(self):
        html = (
            "<html><head><title>BLACKOUT LAB</title></head></html>"
        )

        self.assertEqual(
            web_recon.get_page_title(html),
            "BLACKOUT LAB"
        )

    def test_missing_title(self):
        html = "<html><body>Laboratorio</body></html>"

        self.assertEqual(
            web_recon.get_page_title(html),
            "Não identificado"
        )


class TestTargetValidation(unittest.TestCase):

    def test_accept_localhost(self):
        result = web_recon.validate_target(
            "http://localhost:8000"
        )

        self.assertEqual(
            result,
            "http://localhost:8000"
        )

    def test_reject_invalid_scheme(self):
        with self.assertRaises(ValueError):
            web_recon.validate_target("ftp://localhost")

    def test_reject_missing_hostname(self):
        with self.assertRaises(ValueError):
            web_recon.validate_target("http:///")

    def test_reject_credentials(self):
        with self.assertRaises(ValueError):
            web_recon.validate_target(
                "http://admin:password@localhost"
            )

    def test_reject_invalid_port(self):
        with self.assertRaises(ValueError):
            web_recon.validate_target(
                "http://localhost:99999"
            )

    @patch("modules.web_recon.socket.getaddrinfo")
    def test_accept_private_ip(self, mock_dns):
        mock_dns.return_value = [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("192.168.1.10", 80)
            )
        ]

        result = web_recon.validate_target(
            "http://192.168.1.10"
        )

        self.assertEqual(
            result,
            "http://192.168.1.10"
        )

    @patch("modules.web_recon.socket.getaddrinfo")
    def test_reject_public_ip(self, mock_dns):
        mock_dns.return_value = [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("8.8.8.8", 80)
            )
        ]

        with self.assertRaises(ValueError):
            web_recon.validate_target(
                "http://example.com"
            )


class TestHeaderAnalysis(unittest.TestCase):

    def test_detect_present_headers(self):
        headers = {
            "Content-Security-Policy": "default-src 'self'",
            "X-Frame-Options": "DENY"
        }

        results = web_recon.analyze_headers(headers)

        csp = next(
            item for item in results
            if item["header"] == "Content-Security-Policy"
        )

        frame = next(
            item for item in results
            if item["header"] == "X-Frame-Options"
        )

        self.assertTrue(csp["present"])
        self.assertTrue(frame["present"])

    def test_detect_missing_headers(self):
        results = web_recon.analyze_headers({})

        self.assertEqual(len(results), 6)

        self.assertTrue(
            all(not item["present"] for item in results)
        )


class TestEndpointInspection(unittest.TestCase):

    @patch("modules.web_recon.requests.get")
    def test_inspect_endpoint(self, mock_get):
        response = MagicMock()

        response.status_code = 200

        response.headers = {
            "Server": "TestServer",
            "Content-Type": "text/html",
            "Content-Length": "50"
        }

        response.encoding = "utf-8"

        response.raw = FakeRaw(
            b"<html><head><title>Test Page</title></head></html>"
        )

        mock_get.return_value = response

        result = web_recon.inspect_endpoint(
            "http://localhost:8000"
        )

        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["title"], "Test Page")
        self.assertEqual(result["server"], "TestServer")

        self.assertFalse(
            result["response_truncated"]
        )

        response.close.assert_called_once()


class TestHTTPMethods(unittest.TestCase):

    @patch("modules.web_recon.requests.options")
    def test_inspect_methods(self, mock_options):
        response = MagicMock()

        response.headers = {
            "Allow": "GET, POST, OPTIONS"
        }

        mock_options.return_value = response

        result = web_recon.inspect_methods(
            "http://localhost:8000"
        )

        self.assertEqual(
            result,
            "GET, POST, OPTIONS"
        )

        response.close.assert_called_once()


class TestRobotsInspection(unittest.TestCase):

    @patch("modules.web_recon.requests.get")
    def test_inspect_robots(self, mock_get):
        response = MagicMock()

        response.status_code = 200

        response.raw = FakeRaw(
            b"User-agent: *\nDisallow: /admin"
        )

        mock_get.return_value = response

        result = web_recon.inspect_robots(
            "http://localhost:8000"
        )

        self.assertEqual(result["status_code"], 200)

        self.assertIn(
            "Disallow: /admin",
            result["content"]
        )

        self.assertEqual(
            result["url"],
            "http://localhost:8000/robots.txt"
        )

        response.close.assert_called_once()


class TestReportSaving(unittest.TestCase):

    def test_save_report(self):
        results = {
            "page": {
                "status_code": 200,
                "title": "BLACKOUT LAB"
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:

            with patch.object(
                web_recon,
                "REPORT_DIR",
                Path(temp_dir)
            ):

                report_path = web_recon.save_report(
                    "http://localhost:8000",
                    results
                )

                self.assertTrue(report_path.exists())

                with report_path.open(
                    "r",
                    encoding="utf-8"
                ) as file:
                    report = json.load(file)

        self.assertEqual(
            report["module"],
            "Web Reconnaissance"
        )

        self.assertEqual(
            report["target"],
            "http://localhost:8000"
        )

        self.assertIn(
            "timestamp_utc",
            report
        )


if __name__ == "__main__":
    unittest.main()
