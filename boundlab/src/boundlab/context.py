from __future__ import annotations

from dataclasses import dataclass, field

from boundlab.bus import MessageBus
from boundlab.guard import BoundedFS
from boundlab.memory import Memory
from boundlab.models import Message, StepRecord


@dataclass
class Context:
    goal: str
    agent_name: str
    fs: BoundedFS
    bus: MessageBus
    memory: Memory
    max_steps: int = 8
    steps: list[StepRecord] = field(default_factory=list)

    def log(self, action: str, detail: str, ok: bool = True) -> None:
        self.steps.append(
            StepRecord(agent=self.agent_name, action=action, detail=detail, ok=ok)
        )

    def publish(self, topic: str, body: str, **payload: object) -> None:
        self.bus.publish(
            Message(sender=self.agent_name, topic=topic, body=body, payload=dict(payload))
        )
        self.log("publish", f"{topic}: {body}")

    def write(self, rel_path: str, content: str) -> str:
        written = self.fs.write_text(rel_path, content)
        self.log("write", written)
        return written

    def read(self, rel_path: str) -> str:
        text = self.fs.read_text(rel_path)
        self.log("read", rel_path)
        return text
