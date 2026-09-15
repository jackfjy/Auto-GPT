from __future__ import annotations

from boundlab.context import Context
from boundlab.tools.base import tool


@tool("write_file", "Write text inside this agent's territory.", path="relative path", content="file body")
def write_file(ctx: Context, path: str, content: str) -> str:
    return ctx.write(path, content)


@tool("read_file", "Read a file this agent is allowed to see.", path="relative path")
def read_file(ctx: Context, path: str) -> str:
    return ctx.read(path)


@tool("publish", "Send a message to other agents.", topic="topic name", body="message body")
def publish(ctx: Context, topic: str, body: str) -> str:
    ctx.publish(topic, body)
    return f"published {topic}"


@tool("finish", "Stop the tool loop.", summary="short result")
def finish(ctx: Context, summary: str = "done") -> str:
    ctx.memory.set("finished", summary)
    ctx.log("finish", summary)
    return summary


BUILTIN_TOOLS = [write_file, read_file, publish, finish]
