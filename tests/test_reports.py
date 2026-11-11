
import json
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch, MagicMock

from modules import reports


class TestReportHelpers(unittest.TestCase):

    def test_as_dict_with_dict(self):
        self.assertEqual(reports.as_dict({"a": 1}), {"a": 1})

    def test_as_dict_with_invalid_value(self):
        self.assertEqual(reports.as_dict(None), {})

    def test_as_list_with_list(self):
        self.assertEqual(reports.as_list([1, 2]), [1, 2])

    def test_as_list_with_invalid_value(self):
        self.assertEqual(reports.as_list(None), [])


class TestLoadReports(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.report_dir = Path(self.temp_dir.name)

        self.patcher = patch.object(
            reports,
            "REPORT_DIR",
            self.report_dir
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def create_report(self, filename, data):
        path = self.report_dir / filename

        path.write_text(
            json.dumps(data),
            encoding="utf-8"
        )

        return path

    def test_load_valid_report(self):
        self.create_report(
            "valid.json",
            {
                "module": "Reconnaissance",
                "target": "127.0.0.1"
            }
        )

        result = reports.load_reports()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["filename"], "valid.json")

    def test_ignore_invalid_json(self):
        path = self.report_dir / "invalid.json"
        path.write_text("{invalid json", encoding="utf-8")

        self.assertEqual(reports.load_reports(), [])

    def test_ignore_non_dictionary_json(self):
        path = self.report_dir / "list.json"
        path.write_text("[1, 2, 3]", encoding="utf-8")

        self.assertEqual(reports.load_reports(), [])

    def test_ignore_missing_module(self):
        self.create_report(
            "missing_module.json",
            {"target": "127.0.0.1"}
        )

        self.assertEqual(reports.load_reports(), [])

    def test_ignore_empty_module(self):
        self.create_report(
            "empty_module.json",
            {
                "module": "   ",
                "target": "127.0.0.1"
            }
        )

        self.assertEqual(reports.load_reports(), [])

    def test_ignore_non_string_module(self):
        self.create_report(
            "invalid_module.json",
            {
                "module": 123,
                "target": "127.0.0.1"
            }
        )

        self.assertEqual(reports.load_reports(), [])

    def test_ignore_non_string_target(self):
        self.create_report(
            "invalid_target.json",
            {
                "module": "Reconnaissance",
                "target": 123
            }
        )

        self.assertEqual(reports.load_reports(), [])

    def test_ignore_oversized_report(self):
        path = self.report_dir / "large.json"

        path.write_text(
            " " * (reports.MAX_REPORT_BYTES + 1),
            encoding="utf-8"
        )

        self.assertEqual(reports.load_reports(), [])

    def test_load_multiple_valid_reports(self):
        for index in range(3):
            self.create_report(
                f"report_{index}.json",
                {
                    "module": "Reconnaissance",
                    "target": "127.0.0.1"
                }
            )

        result = reports.load_reports()

        self.assertEqual(len(result), 3)

    def test_ignore_invalid_utf8(self):
        path = self.report_dir / "invalid_utf8.json"
        path.write_bytes(b"\xff\xfe\xfa")

        self.assertEqual(reports.load_reports(), [])

    def test_missing_directory_is_created(self):
        self.report_dir.rmdir()

        result = reports.load_reports()

        self.assertEqual(result, [])
        self.assertTrue(self.report_dir.exists())


class TestReportRendering(unittest.TestCase):

    def setUp(self):
        self.console_patcher = patch.object(
            reports,
            "console",
            MagicMock()
        )
        self.console_patcher.start()

    def tearDown(self):
        self.console_patcher.stop()

    def test_show_report_list_with_invalid_entries(self):
        reports.show_report_list([
            None,
            "invalid",
            {
                "filename": "test.json",
                "data": None
            }
        ])

    def test_show_report_list_with_invalid_container(self):
        reports.show_report_list(None)

    def test_show_report_details_with_invalid_data(self):
        reports.show_report_details(None)

    def test_show_report_details_with_unknown_module(self):
        reports.show_report_details({
            "module": "Unknown Module",
            "target": "localhost"
        })

    def test_render_recon_with_malformed_data(self):
        reports.show_recon_results({
            "resolved_addresses": None,
            "results": [
                None,
                "invalid"
            ]
        })

    def test_render_web_recon_with_malformed_data(self):
        reports.show_web_recon_results({
            "results": {
                "page": {
                    "security_headers": [
                        None,
                        "invalid"
                    ]
                },
                "robots_txt": None
            }
        })

    def test_render_traffic_with_malformed_data(self):
        reports.show_traffic_results({
            "configuration": None,
            "metrics": None,
            "results": [
                None,
                "invalid"
            ]
        })

    def test_render_stress_old_report(self):
        reports.show_stress_results({
            "configuration": {
                "profile": "Load Test"
            },
            "metrics": {},
            "results": []
        })

    def test_render_stress_with_malformed_data(self):
        reports.show_stress_results({
            "configuration": {
                "stages": [
                    None,
                    "invalid"
                ]
            },
            "metrics": None,
            "stage_results": [
                None,
                "invalid"
            ],
            "results": [
                None
            ]
        })

    def test_render_exploitation_with_malformed_data(self):
        reports.show_exploitation_results({
            "test_results": None,
            "evidence": {
                "returned_accounts": [
                    None,
                    "invalid"
                ]
            }
        })

    def test_show_reports_without_reports(self):
        with patch.object(
            reports,
            "load_reports",
            return_value=[]
        ):
            reports.show_reports()

    def test_show_reports_invalid_choice(self):
        sample = [
            {
                "filename": "test.json",
                "data": {
                    "module": "Reconnaissance",
                    "target": "127.0.0.1"
                }
            }
        ]

        with patch.object(
            reports,
            "load_reports",
            return_value=sample
        ):
            with patch.object(
                reports.Prompt,
                "ask",
                return_value="abc"
            ):
                reports.show_reports()

    def test_show_reports_back_option(self):
        sample = [
            {
                "filename": "test.json",
                "data": {
                    "module": "Reconnaissance",
                    "target": "127.0.0.1"
                }
            }
        ]

        with patch.object(
            reports,
            "load_reports",
            return_value=sample
        ):
            with patch.object(
                reports.Prompt,
                "ask",
                return_value="0"
            ):
                reports.show_reports()


if __name__ == "__main__":
    unittest.main()
