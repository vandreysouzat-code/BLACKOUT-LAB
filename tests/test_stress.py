
import unittest

from unittest.mock import MagicMock, patch

from modules import stress


class FakeClock:

    def __init__(self):
        self.current = 0.0

    def monotonic(self):
        return self.current

    def sleep(self, duration):
        self.current += duration


class TestURLValidation(unittest.TestCase):

    def test_accept_localhost(self):
        self.assertEqual(
            stress.validate_url("http://localhost:8000"),
            "http://localhost:8000"
        )

    def test_accept_private_ip(self):
        self.assertEqual(
            stress.validate_url("http://192.168.1.10:8000"),
            "http://192.168.1.10:8000"
        )

    def test_reject_public_ip(self):
        with self.assertRaises(ValueError):
            stress.validate_url("http://8.8.8.8")

    def test_reject_hostname(self):
        with self.assertRaises(ValueError):
            stress.validate_url("http://example.com")

    def test_reject_ftp(self):
        with self.assertRaises(ValueError):
            stress.validate_url("ftp://localhost")

    def test_reject_credentials(self):
        with self.assertRaises(ValueError):
            stress.validate_url(
                "http://admin:password@localhost"
            )


class TestProfileValidation(unittest.TestCase):

    def test_accept_existing_profiles(self):
        for profile in stress.PROFILES.values():
            with self.subTest(profile=profile["name"]):
                duration = stress.validate_profile(profile)
                self.assertGreater(duration, 0)
                self.assertLessEqual(duration, stress.MAX_DURATION)

    def test_reject_empty_stages(self):
        with self.assertRaises(ValueError):
            stress.validate_profile({"stages": []})

    def test_reject_invalid_profile_type(self):
        with self.assertRaises(ValueError):
            stress.validate_profile(None)

    def test_reject_invalid_stage_type(self):
        with self.assertRaises(ValueError):
            stress.validate_profile({"stages": ["invalid"]})

    def test_reject_rps_above_limit(self):
        with self.assertRaises(ValueError):
            stress.validate_profile({
                "stages": [
                    {"rps": stress.MAX_RPS + 1, "seconds": 2}
                ]
            })

    def test_reject_zero_rps(self):
        with self.assertRaises(ValueError):
            stress.validate_profile({
                "stages": [{"rps": 0, "seconds": 2}]
            })

    def test_reject_duration_above_limit(self):
        with self.assertRaises(ValueError):
            stress.validate_profile({
                "stages": [
                    {"rps": 1, "seconds": stress.MAX_DURATION + 1}
                ]
            })

    def test_reject_total_duration_above_limit(self):
        with self.assertRaises(ValueError):
            stress.validate_profile({
                "stages": [
                    {"rps": 1, "seconds": 6},
                    {"rps": 1, "seconds": 5}
                ]
            })

    def test_reject_boolean_rps(self):
        with self.assertRaises(ValueError):
            stress.validate_profile({
                "stages": [{"rps": True, "seconds": 2}]
            })

    def test_reject_boolean_duration(self):
        with self.assertRaises(ValueError):
            stress.validate_profile({
                "stages": [{"rps": 1, "seconds": True}]
            })


class TestMetrics(unittest.TestCase):

    def test_calculate_metrics(self):
        results = [
            {"status": 200, "latency_ms": 100},
            {"status": 404, "latency_ms": 200},
            {"status": "ERROR", "latency_ms": None}
        ]

        metrics = stress.calculate_metrics(results, 3.0)

        self.assertEqual(metrics["total_requests"], 3)
        self.assertEqual(metrics["http_responses"], 2)
        self.assertEqual(metrics["errors"], 1)
        self.assertEqual(metrics["average_latency_ms"], 150)
        self.assertEqual(metrics["elapsed_seconds"], 3.0)

    def test_calculate_metrics_without_responses(self):
        metrics = stress.calculate_metrics([], 1.0)

        self.assertEqual(metrics["total_requests"], 0)
        self.assertEqual(metrics["http_responses"], 0)
        self.assertEqual(metrics["errors"], 0)
        self.assertIsNone(metrics["average_latency_ms"])

    def test_boolean_status_is_not_http_response(self):
        results = [
            {"status": True, "latency_ms": 100},
            {"status": 200, "latency_ms": 50}
        ]

        metrics = stress.calculate_metrics(results, 1.0)

        self.assertEqual(metrics["total_requests"], 2)
        self.assertEqual(metrics["http_responses"], 1)
        self.assertEqual(metrics["errors"], 1)
        self.assertEqual(metrics["average_latency_ms"], 50)


class TestStageExecution(unittest.TestCase):

    @patch("modules.stress.time.sleep")
    @patch("modules.stress.time.monotonic", return_value=0.0)
    @patch("modules.stress.requests.get")
    def test_execute_stage(
        self,
        mock_get,
        mock_monotonic,
        mock_sleep
    ):
        response = MagicMock()
        response.status_code = 200
        mock_get.return_value = response

        results, summary = stress.execute_stage(
            "http://localhost:8000",
            1,
            2,
            1
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(summary["stage"], 1)
        self.assertEqual(summary["rps"], 1)
        self.assertEqual(summary["metrics"]["http_responses"], 2)
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(response.close.call_count, 2)

    def test_slow_requests_do_not_cause_catch_up_bursts(self):
        clock = FakeClock()
        request_starts = []

        response = MagicMock()
        response.status_code = 200

        def slow_request(*args, **kwargs):
            request_starts.append(clock.monotonic())
            clock.current += 0.75
            return response

        with (
            patch(
                "modules.stress.time.monotonic",
                side_effect=clock.monotonic
            ),
            patch(
                "modules.stress.time.sleep",
                side_effect=clock.sleep
            ),
            patch(
                "modules.stress.requests.get",
                side_effect=slow_request
            )
        ):
            results, summary = stress.execute_stage(
                "http://localhost:8000",
                2,
                2,
                1
            )

        self.assertGreaterEqual(len(request_starts), 2)

        for previous, current in zip(
            request_starts,
            request_starts[1:]
        ):
            self.assertGreaterEqual(
                current - previous,
                0.5
            )

        self.assertEqual(
            len(results),
            summary["metrics"]["total_requests"]
        )

        self.assertTrue(
            all(result["status"] == 200 for result in results)
        )

    def test_reject_rps_above_limit(self):
        with self.assertRaises(ValueError):
            stress.execute_stage(
                "http://localhost:8000",
                stress.MAX_RPS + 1,
                2,
                1
            )

    def test_reject_invalid_duration(self):
        with self.assertRaises(ValueError):
            stress.execute_stage(
                "http://localhost:8000",
                1,
                0,
                1
            )

    def test_reject_boolean_rps(self):
        with self.assertRaises(ValueError):
            stress.execute_stage(
                "http://localhost:8000",
                True,
                2,
                1
            )

    def test_reject_boolean_duration(self):
        with self.assertRaises(ValueError):
            stress.execute_stage(
                "http://localhost:8000",
                1,
                True,
                1
            )


if __name__ == "__main__":
    unittest.main()
