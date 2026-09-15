from __future__ import annotations

from pathlib import Path
from threading import Lock

from boundlab.errors import BoundaryError
from boundlab.models import AccessMode, AgentTerritory, TerritoryMap
from boundlab.paths import matches_any, normalize_rel, resolve_inside


class BoundedFS:
    """Filesystem proxy that only allows an agent to touch its own territory."""

    def __init__(
        self,
        root: Path,
        territory: TerritoryMap,
        agent: AgentTerritory,
    ) -> None:
        self.root = root.resolve()
        self.territory = territory
        self.agent = agent
        self._lock = Lock()

    def read_text(self, rel_path: str) -> str:
        path = self._checked_path(rel_path, "read")
        if not path.is_file():
            raise FileNotFoundError(rel_path)
        return path.read_text(encoding="utf-8")

    def write_text(self, rel_path: str, content: str) -> str:
        path = self._checked_path(rel_path, "write")
        with self._lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return normalize_rel(rel_path)

    def exists(self, rel_path: str) -> bool:
        try:
            return self._checked_path(rel_path, "read").exists()
        except (BoundaryError, ValueError):
            return False

    def list_dir(self, rel_path: str = ".") -> list[str]:
        path = self._checked_path(rel_path, "read")
        if not path.exists():
            return []
        if not path.is_dir():
            raise NotADirectoryError(rel_path)
        items: list[str] = []
        for child in sorted(path.iterdir()):
            child_rel = child.relative_to(self.root).as_posix()
            if self.allows(child_rel, "read"):
                suffix = "/" if child.is_dir() else ""
                items.append(child_rel + suffix)
        return items

    def allows(self, rel_path: str, mode: AccessMode) -> bool:
        try:
            self.check(rel_path, mode)
        except (BoundaryError, ValueError):
            return False
        return True

    def check(self, rel_path: str, mode: AccessMode) -> str:
        rel = normalize_rel(rel_path)
        if rel == "." and mode == "read":
            return rel
        if matches_any(rel, self.territory.forbidden):
            raise BoundaryError(
                f"{self.agent.name} cannot {mode} forbidden path {rel!r}"
            )
        if mode == "write":
            if not matches_any(rel, self.agent.owns):
                raise BoundaryError(
                    f"{self.agent.name} cannot write {rel!r}; owns {list(self.agent.owns)}"
                )
            return rel
        readable = self.agent.owns + self.agent.may_read
        if not matches_any(rel, readable):
            raise BoundaryError(
                f"{self.agent.name} cannot read {rel!r}; may_read {list(self.agent.may_read)}"
            )
        return rel

    def _checked_path(self, rel_path: str, mode: AccessMode) -> Path:
        rel = self.check(rel_path, mode)
        return resolve_inside(self.root, rel)
