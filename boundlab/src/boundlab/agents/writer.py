from __future__ import annotations

from boundlab.agents.base import Agent, AgentResult
from boundlab.context import Context


class WriterAgent(Agent):
    name = "writer"
    description = "Turns research into a draft. Writes only workspace/writer/."

    def run(self, ctx: Context) -> AgentResult:
        findings = _read_findings(ctx)
        draft = (
            f"# Draft\n\n"
            f"Goal: {ctx.goal}\n\n"
            f"## Source notes\n\n{findings}\n"
            f"## Proposal\n\n"
            f"Keep one owner per path. Run agents in parallel only after "
            f"territories.yaml lists non-overlapping owns globs.\n"
        )
        path = ctx.write("workspace/writer/draft.md", draft)
        ctx.publish("draft", "draft ready", path=path)
        return AgentResult(
            agent=self.name,
            summary="wrote writer draft",
            artifacts=[path],
        )


def _read_findings(ctx: Context) -> str:
    message = ctx.bus.latest("findings", sender="researcher")
    if message and isinstance(message.payload.get("path"), str):
        try:
            return ctx.read(str(message.payload["path"]))
        except (FileNotFoundError, OSError):
            pass
    if ctx.fs.exists("workspace/researcher/findings.md"):
        return ctx.read("workspace/researcher/findings.md")
    return "_No findings yet. Writer will still produce a standalone draft._\n"
