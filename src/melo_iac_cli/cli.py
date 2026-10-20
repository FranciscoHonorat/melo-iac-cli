import argparse
import getpass
import os
import sys
from collections.abc import Callable
from typing import Final

import httpx

from melo_iac_cli.auth.auth_service import AuthService, InvalidCredentialsError
from melo_iac_cli.auth.token_store import TokenStore
from melo_iac_cli.config import ENV_USERNAME, Settings

EXIT_OK: Final = 0
EXIT_ERROR: Final = 1
EXIT_USAGE: Final = 2


def build_parser(settings: Settings) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="melo-iac")
    commands = parser.add_subparsers(dest="command", required=True)

    auth = commands.add_parser("auth")
    auth_commands = auth.add_subparsers(dest="auth_command", required=True)

    login = auth_commands.add_parser("login")
    login.add_argument("--username", default=settings.username)
    login.add_argument("--password", default=settings.password)

    auth_commands.add_parser("logout")

    return parser


def run(
    argv: list[str],
    auth_service: AuthService,
    settings: Settings,
    prompt_password: Callable[[str], str] = getpass.getpass,
) -> int:
    args = build_parser(settings).parse_args(argv)
    if args.auth_command == "login":
        if not args.username:
            print(
                "error: username is required "
                f"(use --username or {ENV_USERNAME})",
                file=sys.stderr,
            )
            return EXIT_USAGE
        password = args.password or prompt_password("Password: ")
        try:
            auth_service.login(username=args.username, password=password)
        except InvalidCredentialsError:
            print("error: invalid username or password", file=sys.stderr)
            return EXIT_ERROR
    elif args.auth_command == "logout":
        auth_service.logout()
    return EXIT_OK


def main() -> int:
    settings = Settings.from_env(os.environ)

    with httpx.Client(base_url=settings.api_url) as client:
        auth_service = AuthService(
            token_store=TokenStore(path=settings.token_path), client=client
        )
        return run(sys.argv[1:], auth_service=auth_service, settings=settings)
