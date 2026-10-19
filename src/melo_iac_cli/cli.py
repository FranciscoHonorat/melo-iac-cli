import argparse
import getpass
from collections.abc import Callable, Mapping

from melo_iac_cli.auth.auth_service import AuthService


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
        password = args.password or prompt_password("Password: ")
        auth_service.login(username=args.username, password=password)
    elif args.auth_command == "logout":
        auth_service.logout()
    return 0
