from __future__ import annotations

from boundlab.agents.base import Agent, AgentResult
from boundlab.context import Context
from boundlab.errors import BoundaryError, RuleError
from boundlab.llm.base import Brain
from boundlab.llm.echo import EchoBrain
from boundlab.tools.base import Tool, ToolError
from boundlab.tools.builtin import BUILTIN_TOOLS


class ToolLoopAgent(Agent):
    """Extension point: give a brain + tools, it will call them until finish."""

    name = "tool-loop"
    description = "Generic tool-using agent. Subclass and set name/plan."

    def __init__(self, brain: Brain | None = None, tools: list[Tool] | None = None) -> None:
        self.brain = brain or EchoBrain()
        self.tools = {item.spec.name: item for item in (tools or BUILTIN_TOOLS)}

    def run(self, ctx: Context) -> AgentResult:
        transcript: list[str] = [f"goal={ctx.goal}"]
        artifacts: list[str] = []
        summary = "stopped"
        specs = [tool.spec for tool in self.tools.values()]

        for _ in range(ctx.max_steps):
            decision = self.brain.decide(ctx, specs, transcript)
            ctx.log("think", decision.thought or decision.tool)
            tool = self.tools.get(decision.tool)
            if tool is None:
                raise ToolError(f"unknown tool {decision.tool!r}")
            try:
                result = tool(ctx, **decision.arguments)
            except (BoundaryError, RuleError, ToolError, TypeError, ValueError) as exc:
                ctx.log("error", str(exc), ok=False)
                transcript.append(f"{decision.tool} error: {exc}")
                continue
            transcript.append(f"{decision.tool} -> {result}")
            if decision.tool == "write_file" and "path" in decision.arguments:
                artifacts.append(decision.arguments["path"])
            if decision.tool == "finish":
                summary = result
                break
        else:
            summary = "max steps reached"

        return AgentResult(agent=self.name, summary=summary, artifacts=artifacts)
