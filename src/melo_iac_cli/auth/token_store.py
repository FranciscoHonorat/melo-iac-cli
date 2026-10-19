from pathlib import Path


class TokenStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, token: str) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(token, encoding="utf-8")
        self._path.chmod(0o600)

    def load(self) -> str | None:
        try:
            return self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def clear(self) -> None:
        self._path.unlink(missing_ok=True)
