from __future__ import annotations

from pathlib import Path

import yaml

from boundlab.errors import TerritoryError
from boundlab.models import AgentTerritory, TerritoryMap


def default_territory_path() -> Path:
    candidates = (
        Path.cwd() / "territories.yaml",
        Path(__file__).resolve().parents[2] / "territories.yaml",
    )
    for path in candidates:
        if path.is_file():
            return path
    return candidates[0]


def load_territories(path: Path | None = None) -> TerritoryMap:
    source = path or default_territory_path()
    if not source.is_file():
        raise TerritoryError(f"territory file not found: {source}")

    raw = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    agents_raw = raw.get("agents") or {}
    if not isinstance(agents_raw, dict) or not agents_raw:
        raise TerritoryError("territories.yaml must declare at least one agent")

    agents: dict[str, AgentTerritory] = {}
    owned: dict[str, str] = {}
    for name, spec in agents_raw.items():
        if not isinstance(spec, dict):
            raise TerritoryError(f"agent {name!r} must be a mapping")
        owns = _as_patterns(spec.get("owns"), field=f"agents.{name}.owns")
        may_read = _as_patterns(spec.get("may_read"), field=f"agents.{name}.may_read")
        if not owns:
            raise TerritoryError(f"agent {name!r} must own at least one path")
        for pattern in owns:
            previous = owned.get(pattern)
            if previous and previous != name:
                raise TerritoryError(
                    f"path {pattern!r} is owned by both {previous!r} and {name!r}"
                )
            owned[pattern] = name
        agents[name] = AgentTerritory(
            name=name,
            role=str(spec.get("role") or ""),
            owns=owns,
            may_read=may_read,
        )

    return TerritoryMap(
        version=int(raw.get("version") or 1),
        agents=agents,
        shared_readonly=_as_patterns(raw.get("shared_readonly"), field="shared_readonly"),
        forbidden=_as_patterns(raw.get("forbidden"), field="forbidden"),
    )


def _as_patterns(value: object, *, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TerritoryError(f"{field} must be a list of strings")
    return tuple(item.strip().replace("\\", "/") for item in value if item.strip())
