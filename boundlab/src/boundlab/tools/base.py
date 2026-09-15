from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

from boundlab.context import Context


class ToolError(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    arguments: dict[str, str]


class Tool(Protocol):
    spec: ToolSpec

    def __call__(self, ctx: Context, **kwargs: Any) -> str: ...


def tool(name: str, description: str, **arguments: str) -> Callable[[Callable[..., str]], Tool]:
    def decorator(func: Callable[..., str]) -> Tool:
        func.spec = ToolSpec(name=name, description=description, arguments=arguments)  # type: ignore[attr-defined]
        return func  # type: ignore[return-value]

    return decorator
