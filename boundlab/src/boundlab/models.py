from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

AccessMode = Literal["read", "write"]


@dataclass(frozen=True)
class AgentTerritory:
    name: str
    role: str
    owns: tuple[str, ...]
    may_read: tuple[str, ...]


@dataclass(frozen=True)
class TerritoryMap:
    version: int
    agents: dict[str, AgentTerritory]
    shared_readonly: tuple[str, ...] = ()
    forbidden: tuple[str, ...] = ()

    def get(self, name: str) -> AgentTerritory:
        try:
            return self.agents[name]
        except KeyError as exc:
            raise KeyError(f"unknown agent territory: {name}") from exc


@dataclass(frozen=True)
class Message:
    sender: str
    topic: str
    body: str
    payload: dict[str, object] = field(default_factory=dict)


@dataclass
class StepRecord:
    agent: str
    action: str
    detail: str
    ok: bool = True


@dataclass
class RunReport:
    goal: str
    root: Path
    results: dict[str, object]
    steps: list[StepRecord]
    errors: list[str]
