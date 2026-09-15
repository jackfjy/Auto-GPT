from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from boundlab.context import Context
from boundlab.tools.base import ToolSpec


@dataclass
class Decision:
    tool: str
    arguments: dict[str, str] = field(default_factory=dict)
    thought: str = ""


class Brain(Protocol):
    def decide(self, ctx: Context, tools: list[ToolSpec], transcript: list[str]) -> Decision:
        ...
