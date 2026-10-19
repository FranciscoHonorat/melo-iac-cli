import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

import httpx

from melo_iac_cli.auth.auth_service import AuthService
from melo_iac_cli.auth.token_store import TokenStore
from melo_iac_cli.cli import run


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.token_store = TokenStore(path=Path(tmp.name) / "credentials")
        self.requests: list[httpx.Request] = []

    def make_service(self, response: httpx.Response) -> AuthService:
        def fake_server(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            return response

        client = httpx.Client(
            transport=httpx.MockTransport(fake_server),
            base_url="http://melo.test",
        )
        self.addCleanup(client.close)
        return AuthService(token_store=self.token_store, client=client)

    def test_auth_logout_removes_saved_token(self) -> None:
        self.token_store.save("abcd1234")

        exit_code = run(
            ["auth", "logout"],
            auth_service=self.make_service(httpx.Response(200)),
            env={},
        )

        self.assertEqual(exit_code, 0)
        self.assertIsNone(self.token_store.load())

    def test_auth_login_saves_token(self) -> None:
        exit_code = run(
            ["auth", "login", "--username", "ed", "--password", "secret"],
            auth_service=self.make_service(
                httpx.Response(200, json={"token": "abcd1234"})
            ),
            env={},
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(self.token_store.load(), "abcd1234")

    def test_auth_login_reads_credentials_from_env(self) -> None:
        exit_code = run(
            ["auth", "login"],
            auth_service=self.make_service(
                httpx.Response(200, json={"token": "abcd1234"})
            ),
            env={"MELO_IAC_USERNAME": "ed", "MELO_IAC_PASSWORD": "secret"},
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(self.token_store.load(), "abcd1234")

    def test_auth_login_prompts_for_password_when_missing(self) -> None:
        exit_code = run(
            ["auth", "login", "--username", "ed"],
            auth_service=self.make_service(
                httpx.Response(200, json={"token": "abcd1234"})
            ),
            env={},
            prompt_password=lambda prompt: "secret",
        )

        self.assertEqual(exit_code, 0)
        sent = json.loads(self.requests[0].content)
        self.assertEqual(sent["password"], "secret")

    def test_auth_login_fails_when_username_is_missing(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = run(
                ["auth", "login", "--password", "secret"],
                auth_service=self.make_service(httpx.Response(200)),
                env={},
            )

        self.assertEqual(exit_code, 2)
        self.assertIn("username is required", stderr.getvalue())
        self.assertEqual(self.requests, [])

    def test_auth_login_fails_when_credentials_are_invalid(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = run(
                ["auth", "login", "--username", "ed", "--password", "wrong"],
                auth_service=self.make_service(httpx.Response(401)),
                env={},
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("invalid username or password", stderr.getvalue())
        self.assertIsNone(self.token_store.load())
