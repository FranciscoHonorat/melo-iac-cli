from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Self

ENV_API_URL: Final = "MELO_API_URL"
ENV_USERNAME: Final = "MELO_IAC_USERNAME"
ENV_PASSWORD: Final = "MELO_IAC_PASSWORD"

DEFAULT_API_URL: Final = "http://localhost:8080"


@dataclass(frozen=True)
class Settings:
    api_url: str
    token_path: Path
    username: str | None
    password: str | None

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> Self:
        return cls(
            api_url=env.get(ENV_API_URL, DEFAULT_API_URL),
            token_path=Path.home() / ".config" / "melo-iac" / "credentials",
            username=env.get(ENV_USERNAME),
            password=env.get(ENV_PASSWORD),
        )
