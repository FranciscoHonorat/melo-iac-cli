from typing import Final

import httpx

from melo_iac_cli.auth.token_store import TokenStore

LOGIN_PATH: Final = "/v1/auth/login"


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, token_store: TokenStore, client: httpx.Client) -> None:
        self._token_store = token_store
        self._client = client

    def login(self, username: str, password: str) -> None:
        response = self._client.post(
            LOGIN_PATH,
            json={"username": username, "password": password},
        )
        if response.status_code == httpx.codes.UNAUTHORIZED:
            raise InvalidCredentialsError
        self._token_store.save(response.json()["token"])

    def logout(self) -> None:
        self._token_store.clear()
