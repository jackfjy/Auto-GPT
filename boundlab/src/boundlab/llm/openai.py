from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from boundlab.context import Context
from boundlab.llm.base import Decision
from boundlab.tools.base import ToolSpec

DEFAULT_URL = "https://api.openai.com/v1/chat/completions"


def available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


class OpenAIBrain:
    """Optional OpenAI-compatible brain. Unused unless OPENAI_API_KEY is set."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", DEFAULT_URL)

    def decide(self, ctx: Context, tools: list[ToolSpec], transcript: list[str]) -> Decision:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        catalog = [
            {"name": tool.name, "description": tool.description, "arguments": tool.arguments}
            for tool in tools
        ]
        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a bounded agent. Reply with JSON only: "
                        '{"tool": "...", "arguments": {}, "thought": "..."}. '
                        "You must not write files outside your territory."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "goal": ctx.goal,
                            "agent": ctx.agent_name,
                            "owns": list(ctx.fs.agent.owns),
                            "tools": catalog,
                            "transcript": transcript[-12:],
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        request = urllib.request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"openai request failed: {exc}") from exc
        content = body["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return Decision(
            tool=str(parsed.get("tool") or "finish"),
            arguments={str(k): str(v) for k, v in (parsed.get("arguments") or {}).items()},
            thought=str(parsed.get("thought") or ""),
        )
