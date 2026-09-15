from __future__ import annotations

from boundlab.agents.base import Agent, AgentResult
from boundlab.context import Context


class ResearcherAgent(Agent):
    name = "researcher"
    description = "Collects findings for the goal. Writes only workspace/researcher/."

    def run(self, ctx: Context) -> AgentResult:
        bullets = [
            f"- 目标：{ctx.goal}",
            "- 并行开发时每个 agent 只写自己的目录。",
            "- 交叉信息走消息总线，不直接改别人的文件。",
            "- territories.yaml 是唯一的所有权来源。",
        ]
        findings = "# Findings\n\n" + "\n".join(bullets) + "\n"
        path = ctx.write("workspace/researcher/findings.md", findings)
        ctx.memory.set("findings", findings)
        ctx.publish("findings", "research complete", path=path)
        return AgentResult(
            agent=self.name,
            summary="wrote researcher findings",
            artifacts=[path],
        )
