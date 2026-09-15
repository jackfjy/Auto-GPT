from __future__ import annotations

from boundlab.context import Context
from boundlab.llm.base import Decision
from boundlab.tools.base import ToolSpec


class EchoBrain:
    """No-API brain. Follows a fixed plan so the project runs offline."""

    def __init__(self, plan: list[Decision] | None = None) -> None:
        self.plan = list(plan or [])
        self._index = 0

    def decide(self, ctx: Context, tools: list[ToolSpec], transcript: list[str]) -> Decision:
        del ctx, tools, transcript
        if self._index >= len(self.plan):
            return Decision(tool="finish", arguments={"summary": "plan exhausted"})
        decision = self.plan[self._index]
        self._index += 1
        return decision
