from __future__ import annotations

from threading import Lock


class Memory:
    """Per-agent scratch notes. Shared facts go through the bus, not here."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._lock = Lock()

    def set(self, key: str, value: str) -> None:
        with self._lock:
            self._store[key] = value

    def get(self, key: str, default: str = "") -> str:
        with self._lock:
            return self._store.get(key, default)

    def items(self) -> dict[str, str]:
        with self._lock:
            return dict(self._store)
