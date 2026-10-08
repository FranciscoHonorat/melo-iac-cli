from pathlib import Path


class TokenStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, token: str) -> None:
        self._path.write_text(token, encoding="utf-8")

    def load(self) -> str:
        return self._path.read_text(encoding="utf-8")
