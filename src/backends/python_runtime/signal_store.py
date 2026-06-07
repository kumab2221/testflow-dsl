from __future__ import annotations

from typing import Any


class SignalStore:
    """DSL内部の信号値を保持するストア。"""

    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        self._store: dict[str, Any] = dict(initial or {})

    def get(self, signal: str) -> Any:
        return self._store.get(signal)

    def set(self, signal: str, value: Any) -> None:
        self._store[signal] = value

    def update(self, values: dict[str, Any]) -> None:
        self._store.update(values)
