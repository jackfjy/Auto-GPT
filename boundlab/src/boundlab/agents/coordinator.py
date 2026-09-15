from __future__ import annotations

from boundlab.agents.base import Agent, AgentResult
from boundlab.context import Context


class CoordinatorAgent(Agent):
    name = "coordinator"
    description = "Merges inbox/bus artifacts into shared/. Does not edit worker files."

    def run(self, ctx: Context) -> AgentResult:
        lines = [f"# Shared report\n\nGoal: {ctx.goal}\n"]
        for topic in ("findings", "draft", "review"):
            message = ctx.bus.latest(topic)
            if message is None:
                lines.append(f"\n## {topic}\n\n_missing_\n")
                continue
            path = message.payload.get("path")
            excerpt = ""
            if isinstance(path, str) and ctx.fs.exists(path):
                excerpt = ctx.read(path).strip()
            lines.append(
                f"\n## {topic} ({message.sender})\n\n{excerpt or message.body}\n"
            )
        report = "".join(lines)
        shared = ctx.write("shared/report.md", report)
        inbox = ctx.write("inbox/coordinator.md", f"merged topics into {shared}\n")
        return AgentResult(
            agent=self.name,
            summary="merged shared report",
            artifacts=[shared, inbox],
        )
