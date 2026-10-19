import argparse
import getpass
import os
import sys
from collections.abc import Callable, Mapping
from pathlib import Path

import httpx

from melo_iac_cli.auth.auth_service import AuthService, InvalidCredentialsError
from melo_iac_cli.auth.token_store import TokenStore


def build_parser(env: Mapping[str, str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="melo-iac")
    commands = parser.add_subparsers(dest="command", required=True)

    auth = commands.add_parser("auth")
    auth_commands = auth.add_subparsers(dest="auth_command", required=True)

    login = auth_commands.add_parser("login")
    login.add_argument("--username", default=env.get("MELO_IAC_USERNAME"))
    login.add_argument("--password", default=env.get("MELO_IAC_PASSWORD"))

    auth_commands.add_parser("logout")

    return parser


def run(
    argv: list[str],
    auth_service: AuthService,
    env: Mapping[str, str],
    prompt_password: Callable[[str], str] = getpass.getpass,
) -> int:
    args = build_parser(env).parse_args(argv)
    if args.auth_command == "login":
        if not args.username:
            print(
                "error: username is required "
                "(use --username or MELO_IAC_USERNAME)",
                file=sys.stderr,
            )
            return 2
        password = args.password or prompt_password("Password: ")
        try:
            auth_service.login(username=args.username, password=password)
        except InvalidCredentialsError:
            print("error: invalid username or password", file=sys.stderr)
            return 1
    elif args.auth_command == "logout":
        auth_service.logout()
    return 0


def main() -> int:
    token_path = Path.home() / ".config" / "melo-iac" / "credentials"
    api_url = os.environ.get("MELO_API_URL", "http://localhost:8080")

    with httpx.Client(base_url=api_url) as client:
        auth_service = AuthService(
            token_store=TokenStore(path=token_path), client=client
        )
        return run(sys.argv[1:], auth_service=auth_service, env=os.environ)
