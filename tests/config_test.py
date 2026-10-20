import unittest
from pathlib import Path

from melo_iac_cli.config import Settings


class SettingsTest(unittest.TestCase):
    def test_from_env_reads_values_from_env(self) -> None:
        settings = Settings.from_env(
            {
                "MELO_API_URL": "http://melo.test",
                "MELO_IAC_USERNAME": "ed",
                "MELO_IAC_PASSWORD": "secret",
            }
        )

        self.assertEqual(settings.api_url, "http://melo.test")
        self.assertEqual(settings.username, "ed")
        self.assertEqual(settings.password, "secret")

    def test_from_env_uses_defaults_when_env_is_empty(self) -> None:
        settings = Settings.from_env({})

        self.assertEqual(settings.api_url, "http://localhost:8080")
        self.assertEqual(
            settings.token_path,
            Path.home() / ".config" / "melo-iac" / "credentials",
        )

        self.assertIsNone(settings.username)
        self.assertIsNone(settings.password)
