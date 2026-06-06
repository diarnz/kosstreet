from typing import Protocol


class FileStorage(Protocol):
    def save_bytes(self, contents: bytes, *, suffix: str = ".jpg") -> str:
        """Persist bytes and return the relative path stored on the report row."""

    def url_for(self, path: str) -> str:
        """Return a browser-loadable URL for a stored relative path."""
