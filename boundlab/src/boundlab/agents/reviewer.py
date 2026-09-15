from __future__ import annotations

from boundlab.agents.base import Agent, AgentResult
from boundlab.context import Context


class ReviewerAgent(Agent):
    name = "reviewer"
    description = "Reviews the draft. Writes only workspace/reviewer/."

    def run(self, ctx: Context) -> AgentResult:
        draft = _read_draft(ctx)
        has_territory = "territor" in draft.lower() or "owns" in draft.lower()
        verdict = "approve" if has_territory else "comment"
        review = (
            f"# Review\n\n"
            f"Goal: {ctx.goal}\n\n"
            f"Verdict: **{verdict}**\n\n"
            f"Checks:\n"
            f"- draft exists: {'yes' if draft.strip() else 'no'}\n"
            f"- mentions ownership/territory: {'yes' if has_territory else 'no'}\n"
        )
        path = ctx.write("workspace/reviewer/review.md", review)
        ctx.publish("review", verdict, path=path)
        return AgentResult(
            agent=self.name,
            summary=f"review {verdict}",
            artifacts=[path],
            extra={"verdict": verdict},
        )


def _read_draft(ctx: Context) -> str:
    message = ctx.bus.latest("draft", sender="writer")
    if message and isinstance(message.payload.get("path"), str):
        try:
            return ctx.read(str(message.payload["path"]))
        except (FileNotFoundError, OSError):
            pass
    if ctx.fs.exists("workspace/writer/draft.md"):
        return ctx.read("workspace/writer/draft.md")
    return ""
