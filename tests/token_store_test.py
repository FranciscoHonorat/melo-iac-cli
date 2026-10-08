import tempfile
import unittest
from pathlib import Path

from melo_iac_cli.token_store import TokenStore


class TokenStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "credentials"
        self.token = "abcd1234"

    def test_load_returns_saved_token(self) -> None:
        TokenStore(path=self.path).save(self.token)
        loaded_token = TokenStore(path=self.path).load()

        self.assertEqual(loaded_token, self.token)

    def test_load_returns_none_when_no_token_saved(self) -> None:
        loaded_token = TokenStore(path=self.path).load()

        self.assertIsNone(loaded_token)

    def test_load_returns_none_after_clear(self) -> None:
        TokenStore(path=self.path).save(self.token)
        TokenStore(path=self.path).clear()
        loaded_token = TokenStore(path=self.path).load()

        self.assertIsNone(loaded_token)
