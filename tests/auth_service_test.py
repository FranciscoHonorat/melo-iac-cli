import json
import tempfile
import unittest
from pathlib import Path

import httpx

from melo_iac_cli.auth.auth_service import AuthService, InvalidCredentialsError
from melo_iac_cli.auth.token_store import TokenStore


class AuthServiceTest(unittest.TestCase):
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

    def test_logout_removes_saved_token(self) -> None:
        self.token_store.save("abcd1234")

        self.make_service(httpx.Response(200)).logout()

        self.assertIsNone(self.token_store.load())

    def test_login_saves_token_returned_by_server(self) -> None:
        service = self.make_service(
            httpx.Response(200, json={"token": "abcd1234"})
        )

        service.login(username="ed", password="secret")

        self.assertEqual(self.token_store.load(), "abcd1234")
        request = self.requests[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.url.path, "/v1/auth/login")
        self.assertEqual(
            json.loads(request.content),
            {"username": "ed", "password": "secret"},
        )

    def test_login_raises_when_credentials_are_invalid(self) -> None:
        service = self.make_service(httpx.Response(401))

        with self.assertRaises(InvalidCredentialsError):
            service.login(username="ed", password="wrong")

        self.assertIsNone(self.token_store.load())
