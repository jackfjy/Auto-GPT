from __future__ import annotations

from threading import Lock

from boundlab.models import Message


class MessageBus:
    """In-process pub/sub. Agents talk here instead of writing each other's files."""

    def __init__(self) -> None:
        self._messages: list[Message] = []
        self._lock = Lock()

    def publish(self, message: Message) -> None:
        with self._lock:
            self._messages.append(message)

    def history(self, topic: str | None = None) -> list[Message]:
        with self._lock:
            if topic is None:
                return list(self._messages)
            return [item for item in self._messages if item.topic == topic]

    def latest(self, topic: str, sender: str | None = None) -> Message | None:
        for message in reversed(self.history(topic)):
            if sender is None or message.sender == sender:
                return message
        return None
