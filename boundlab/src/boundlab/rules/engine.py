from __future__ import annotations

from pathlib import Path

import yaml

from boundlab.errors import RuleError
from boundlab.models import TerritoryMap


class RuleEngine:
    def __init__(self, rules: list[dict[str, str]] | None = None) -> None:
        self.rules = rules or load_builtin_rules()

    def assert_unique_owners(self, territories: TerritoryMap) -> None:
        seen: dict[str, str] = {}
        for agent in territories.agents.values():
            for pattern in agent.owns:
                previous = seen.get(pattern)
                if previous:
                    raise RuleError(
                        f"rule one-owner violated: {pattern!r} owned by {previous} and {agent.name}"
                    )
                seen[pattern] = agent.name

    def descriptions(self) -> list[str]:
        return [f"{item['id']}: {item['description']}" for item in self.rules]


def load_builtin_rules() -> list[dict[str, str]]:
    path = Path(__file__).with_name("builtin.yaml")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rules = raw.get("rules") or []
    return [item for item in rules if isinstance(item, dict)]
