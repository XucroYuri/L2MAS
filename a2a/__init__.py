"""Small local A2A compatibility layer for the MVP prototype."""

from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable


@dataclass(frozen=True)
class AgentCapability:
    name: str
    description: str
    input_schema: Any
    output_schema: Any


def agent_task(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await func(*args, **kwargs)

    wrapper.is_agent_task = True
    return wrapper


class Agent:
    agent_id = ""
    name = ""
    description = ""
    capabilities: list[AgentCapability] = []

    async def register(self) -> dict[str, str]:
        return {"status": "registered", "agent_id": self.agent_id}


class AgentClient:
    @staticmethod
    async def discover(agent_id: str, registry_url: str = "http://localhost:50051") -> dict[str, str]:
        return {"id": agent_id, "registry_url": registry_url, "status": "available"}

    @staticmethod
    async def list_agents(registry_url: str = "http://localhost:50051") -> list[dict[str, str]]:
        return [
            {"id": "director@local", "name": "Director", "endpoint": registry_url, "capabilities": "script.plan"},
            {"id": "renderer@local", "name": "Renderer", "endpoint": registry_url, "capabilities": "video.compose"},
        ]
