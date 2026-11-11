
import unittest
from unittest.mock import patch
import socket

from core.scope import (
    is_allowed_ip,
    resolve_host,
    validate_host,
    validate_http_url,
)


class TestScope(unittest.TestCase):

    def test_private_ip_is_allowed(self):
        self.assertTrue(is_allowed_ip("192.168.1.10"))

    def test_loopback_ip_is_allowed(self):
        self.assertTrue(is_allowed_ip("127.0.0.1"))

    def test_public_ip_is_rejected(self):
        self.assertFalse(is_allowed_ip("8.8.8.8"))

    def test_multicast_ip_is_rejected(self):
        self.assertFalse(is_allowed_ip("224.0.0.1"))

    def test_private_hostname_is_allowed(self):
        fake_result = [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("192.168.1.20", 80),
            )
        ]

        with patch("core.scope.socket.getaddrinfo", return_value=fake_result):
            result = resolve_host("lab.example", 80)

        self.assertEqual(result, ["192.168.1.20"])

    def test_hostname_resolving_to_public_ip_is_rejected(self):
        fake_result = [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("8.8.8.8", 80),
            )
        ]

        with patch("core.scope.socket.getaddrinfo", return_value=fake_result):
            with self.assertRaises(ValueError):
                resolve_host("external.example", 80)

    def test_localhost_is_allowed(self):
        self.assertEqual(
            resolve_host("localhost"),
            ["127.0.0.1", "::1"]
        )

    def test_invalid_hostname_is_rejected(self):
        with patch(
            "core.scope.socket.getaddrinfo",
            side_effect=socket.gaierror
        ):
            with self.assertRaises(ValueError):
                resolve_host("invalid.example")

    def test_validate_host_rejects_url(self):
        with self.assertRaises(ValueError):
            validate_host("http://127.0.0.1")

    def test_http_url_is_allowed(self):
        result = validate_http_url("http://127.0.0.1:8000")
        self.assertEqual(result, "http://127.0.0.1:8000")

    def test_https_url_is_allowed(self):
        result = validate_http_url("https://localhost")
        self.assertEqual(result, "https://localhost")

    def test_ftp_url_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_http_url("ftp://127.0.0.1")

    def test_url_credentials_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_http_url("http://user:pass@127.0.0.1")

    def test_invalid_port_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_http_url("http://127.0.0.1:99999")

    def test_hostname_can_be_disabled(self):
        with self.assertRaises(ValueError):
            validate_http_url(
                "http://lab.example",
                allow_hostname=False
            )


if __name__ == "__main__":
    unittest.main()
