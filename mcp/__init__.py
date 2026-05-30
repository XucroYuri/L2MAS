"""Small local MCP compatibility layer for deterministic MVP runs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MCPTool:
    name: str

    async def ainvoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.name in {"textoon_generate", "image_to_live2d"}:
            return {"parameters": {"ParamEyeLOpen": 1.0, "ParamMouthForm": 0.2}, "preview_url": "mock://preview"}
        if self.name == "search_action_library":
            return {"matches": [{"parameters": {"ParamAngleX": {"keyframes": [0, 1], "values": [0.0, 0.1]}}}]}
        if self.name == "animate_live2d_model":
            return {"parameter_sequence": [{"ParamAngleX": 0.0}, {"ParamAngleX": 0.1}]}
        if self.name == "elevenlabs_tts":
            return {"duration": max(1.0, len(payload.get("text", "")) / 12), "phonemes": []}
        if self.name == "concat_videos":
            return {"output_path": payload.get("output_path", "/tmp/l2mas_mock_concat.mp4")}
        if self.name == "process_video":
            return {"output_path": payload.get("video_path", "/tmp/l2mas_mock_processed.mp4")}
        return {}


class MCPClient:
    def __init__(self, tools: list[MCPTool]):
        self._tools = tools

    @classmethod
    def from_config_file(cls, path: str | Path) -> "MCPClient":
        config_path = Path(path)
        if not config_path.exists():
            config_path = Path(__file__).resolve().parents[1] / "config" / "mcp_config.json"
        data = json.loads(config_path.read_text(encoding="utf-8"))
        tools = [MCPTool(item["name"]) for item in data.get("tools", [])]
        return cls(tools)

    async def initialize(self) -> None:
        return None

    async def close(self) -> None:
        return None

    def list_tools(self) -> list[MCPTool]:
        return list(self._tools)
