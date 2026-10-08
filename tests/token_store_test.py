import tempfile
import unittest
from pathlib import Path

from melo_iac_cli.token_store import TokenStore


class TokenStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp_dir = Path(tmp.name)

    def test_load_returns_saved_token(self) -> None:
        path = self.tmp_dir / "credentials"
        token = "abcd1234"

        TokenStore(path=path).save(token)
        loaded_token = TokenStore(path=path).load()

        self.assertEqual(loaded_token, token)
