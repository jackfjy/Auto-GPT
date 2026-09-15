from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    agent: str
    summary: str
    artifacts: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    """Implement this class, then add a matching entry in territories.yaml."""

    name: str = ""
    description: str = ""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls is Agent:
            return
        if not getattr(cls, "name", ""):
            cls.name = cls.__name__.removesuffix("Agent").lower()

    @abstractmethod
    def run(self, ctx: Any) -> AgentResult:
        """Do work using only ctx.write / ctx.read / ctx.publish."""
