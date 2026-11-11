
import unittest
from unittest.mock import Mock, patch

import requests

from modules import traffic


class TestTrafficValidation(unittest.TestCase):

    @patch("modules.traffic.validate_http_url")
    def test_validate_url_accepts_private_target(self, mock_validate):
        mock_validate.return_value = "http://127.0.0.1:8000"

        result = traffic.validate_url(
            "http://127.0.0.1:8000"
        )

        self.assertEqual(
            result,
            "http://127.0.0.1:8000"
        )

        mock_validate.assert_called_once_with(
            "http://127.0.0.1:8000",
            allow_hostname=False
        )

    @patch("modules.traffic.validate_http_url")
    def test_validate_url_rejects_invalid_target(self, mock_validate):
        mock_validate.side_effect = ValueError(
            "URL inválida."
        )

        with self.assertRaises(ValueError):
            traffic.validate_url("http://example.com")

    def test_validate_duration_accepts_valid_values(self):
        self.assertEqual(
            traffic.validate_duration(1),
            1
        )

        self.assertEqual(
            traffic.validate_duration(10),
            10
        )

    def test_validate_duration_rejects_zero(self):
        with self.assertRaises(ValueError):
            traffic.validate_duration(0)

    def test_validate_duration_rejects_excessive_value(self):
        with self.assertRaises(ValueError):
            traffic.validate_duration(11)

    def test_validate_duration_rejects_boolean(self):
        with self.assertRaises(ValueError):
            traffic.validate_duration(True)

    def test_validate_duration_rejects_string(self):
        with self.assertRaises(ValueError):
            traffic.validate_duration("5")


class TestTrafficMetrics(unittest.TestCase):

    def test_calculate_metrics(self):
        results = [
            {"status": 200, "latency_ms": 10.0},
            {"status": 404, "latency_ms": 20.0},
            {"status": "ERROR", "latency_ms": None}
        ]

        metrics = traffic.calculate_metrics(
            results,
            1.5
        )

        self.assertEqual(metrics["total_requests"], 3)
        self.assertEqual(metrics["http_responses"], 2)
        self.assertEqual(metrics["errors"], 1)
        self.assertEqual(metrics["average_latency_ms"], 15.0)
        self.assertEqual(metrics["elapsed_seconds"], 1.5)

    def test_calculate_metrics_without_success(self):
        results = [
            {"status": "ERROR", "latency_ms": None}
        ]

        metrics = traffic.calculate_metrics(
            results,
            1.0
        )

        self.assertEqual(metrics["total_requests"], 1)
        self.assertEqual(metrics["http_responses"], 0)
        self.assertEqual(metrics["errors"], 1)
        self.assertIsNone(metrics["average_latency_ms"])

    def test_boolean_status_is_not_http_response(self):
        results = [
            {"status": True, "latency_ms": 10.0}
        ]

        metrics = traffic.calculate_metrics(
            results,
            1.0
        )

        self.assertEqual(metrics["http_responses"], 0)
        self.assertEqual(metrics["errors"], 1)


class TestTrafficExecution(unittest.TestCase):

    @patch("modules.traffic.time.sleep")
    @patch("modules.traffic.requests.get")
    @patch("modules.traffic.validate_url")
    @patch("modules.traffic.time.monotonic", return_value=0.0)
    def test_generate_traffic(
        self,
        mock_monotonic,
        mock_validate,
        mock_get,
        mock_sleep
    ):
        response = Mock()
        response.status_code = 200

        mock_get.return_value = response

        results, elapsed = traffic.generate_traffic(
            "http://127.0.0.1:8000",
            1
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], 200)
        self.assertEqual(results[1]["status"], 200)

        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 2)

        self.assertEqual(response.close.call_count, 2)

        mock_validate.assert_called_once()

    @patch("modules.traffic.requests.get")
    @patch("modules.traffic.validate_url")
    @patch("modules.traffic.time.monotonic", return_value=0.0)
    def test_generate_traffic_records_request_error(
        self,
        mock_monotonic,
        mock_validate,
        mock_get
    ):
        mock_get.side_effect = requests.RequestException(
            "Connection error"
        )

        with patch("modules.traffic.time.sleep"):
            results, elapsed = traffic.generate_traffic(
                "http://127.0.0.1:8000",
                1
            )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "ERROR")
        self.assertIsNone(results[0]["latency_ms"])

    @patch("modules.traffic.requests.get")
    @patch("modules.traffic.validate_url")
    def test_generate_traffic_closes_response(
        self,
        mock_validate,
        mock_get
    ):
        response = Mock()
        response.status_code = 200
        mock_get.return_value = response

        with patch(
            "modules.traffic.time.monotonic",
            return_value=0.0
        ), patch("modules.traffic.time.sleep"):
            traffic.generate_traffic(
                "http://127.0.0.1:8000",
                1
            )

        self.assertEqual(response.close.call_count, 2)


class TestTrafficReports(unittest.TestCase):

    @patch("modules.traffic.REPORT_DIR")
    def test_save_report(self, mock_report_dir):
        mock_report_dir.mkdir = Mock()

        report_path = mock_report_dir.__truediv__.return_value
        report_file = Mock()

        report_path.open.return_value.__enter__.return_value = (
            report_file
        )

        results = [
            {"status": 200, "latency_ms": 10.0},
            {"status": "ERROR", "latency_ms": None}
        ]

        with patch(
            "modules.traffic.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = (
                "20261109_120000_000000"
            )

            mock_datetime.now.return_value.isoformat.return_value = (
                "2026-11-09T12:00:00+00:00"
            )

            result = traffic.save_report(
                "http://127.0.0.1:8000",
                1,
                results,
                1.0
            )

        self.assertEqual(result, report_path)

        self.assertGreater(
            report_file.write.call_count,
            0
        )


if __name__ == "__main__":
    unittest.main()
