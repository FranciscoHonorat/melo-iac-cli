import stat
import tempfile
import unittest
from pathlib import Path

from melo_iac_cli.auth.token_store import TokenStore


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

    def test_clear_does_not_fail_when_no_token_saved(self) -> None:
        TokenStore(path=self.path).clear()
        loaded_token = TokenStore(path=self.path).load()

        self.assertIsNone(loaded_token)

    def test_save_creates_file_readable_only_by_owner(self) -> None:
        TokenStore(path=self.path).save(self.token)

        mode = stat.S_IMODE(self.path.stat().st_mode)
        self.assertEqual(mode, 0o600)

    def test_save_creates_missing_parent_directory(self) -> None:
        path = self.path.parent / "melo-iac" / "credentials"

        TokenStore(path=path).save(self.token)

        self.assertEqual(TokenStore(path=path).load(), self.token)
