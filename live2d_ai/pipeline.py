"""Deterministic local MVP pipeline for smoke tests and examples."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from .provider_registry import ProviderRegistry
from .providers import ProviderRouter

HttpTransport = Callable[[dict[str, Any]], Any]


@dataclass(frozen=True)
class Live2DModelResult:
    model_path: str
    parameters: dict[str, float]
    preview_url: str
    generation_time: float
    provider_id: str


@dataclass(frozen=True)
class ShotArtifact:
    shot_id: str
    dialogue: str
    video_path: str
    audio_path: str
    duration: float


@dataclass(frozen=True)
class AnimationResult:
    task_id: str
    video_path: str
    model_path: str
    total_time: float
    shots: list[ShotArtifact]
    provider_trace: dict[str, str]
    provider_warnings: dict[str, list[str]]
    output_dir: str


class Live2DModelGenerator:
    def __init__(
        self,
        api_endpoint: str = "http://localhost:8080",
        provider_registry_path: str | Path | None = None,
        output_dir: str | Path = "output/mvp",
        privacy_mode: str = "local-only",
        use_mock: bool = True,
    ):
        self.api_endpoint = api_endpoint
        self.registry = (
            ProviderRegistry.from_file(provider_registry_path)
            if provider_registry_path
            else ProviderRegistry.default()
        )
        self.output_dir = Path(output_dir)
        self.privacy_mode = privacy_mode
        self.use_mock = use_mock

    async def text_to_live2d(
        self,
        text_description: str,
        style: str = "anime",
        auto_rig: bool = True,
        generate_physics: bool = True,
    ) -> Live2DModelResult:
        start = time.perf_counter()
        provider = self.registry.select(
            "model.live2d.generate",
            privacy_mode=self.privacy_mode,
            prefer_mock=self.use_mock,
        )
        model_dir = self.output_dir / "models" / uuid4().hex[:8]
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / "model.model3.json"
        payload = {
            "Version": 3,
            "FileReferences": {},
            "Meta": {
                "description": text_description,
                "style": style,
                "auto_rig": auto_rig,
                "generate_physics": generate_physics,
                "provider_id": provider.provider_id,
            },
        }
        model_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        await asyncio.sleep(0)

        return Live2DModelResult(
            model_path=str(model_path),
            parameters={
                "ParamEyeLOpen": 1.0,
                "ParamEyeROpen": 1.0,
                "ParamMouthForm": 0.2,
            },
            preview_url=model_path.with_name("preview.png").as_posix(),
            generation_time=time.perf_counter() - start,
            provider_id=provider.provider_id,
        )


class AnimationGenerator:
    def __init__(
        self,
        api_endpoint: str = "http://localhost:8080",
        api_key: str | None = None,
        provider_registry_path: str | Path | None = None,
        output_dir: str | Path = "output/mvp",
        privacy_mode: str = "local-only",
        use_mock: bool = True,
        http_transport: HttpTransport | None = None,
    ):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.provider_registry_path = provider_registry_path
        self.registry = (
            ProviderRegistry.from_file(provider_registry_path)
            if provider_registry_path
            else ProviderRegistry.default()
        )
        self.output_dir = Path(output_dir)
        self.privacy_mode = privacy_mode
        self.use_mock = use_mock
        self.http_transport = http_transport
        self.last_result: AnimationResult | None = None

    async def health_check(self) -> dict[str, object]:
        return {
            "status": "healthy",
            "mode": "mock" if self.use_mock else "local",
            "agents": await self.list_agents(),
        }

    async def list_agents(self) -> list[dict[str, str]]:
        return [
            {"id": "director@local", "name": "Director", "status": "ready", "description": "Mock storyboard planner"},
            {"id": "modeling@local", "name": "Modeling", "status": "ready", "description": "Mock Live2D artifact writer"},
            {"id": "voice@local", "name": "Voice", "status": "ready", "description": "Mock audio artifact writer"},
            {"id": "animation@local", "name": "Animation", "status": "ready", "description": "Mock shot artifact writer"},
            {"id": "renderer@local", "name": "Renderer", "status": "ready", "description": "Mock final video writer"},
        ]

    async def generate(
        self,
        script: str,
        character_description: str,
        resolution: str = "1920x1080",
        fps: int = 60,
    ) -> AnimationResult:
        start = time.perf_counter()
        task_id = uuid4().hex[:12]
        run_dir = self.output_dir / task_id
        run_dir.mkdir(parents=True, exist_ok=True)

        provider_trace = self.registry.trace_for(
            [
                "script.plan",
                "model.live2d.generate",
                "voice.generate",
                "motion.generate",
                "video.compose",
            ],
            privacy_mode=self.privacy_mode,
            prefer_mock=self.use_mock,
        )
        provider_warnings: dict[str, list[str]] = {}
        router = ProviderRouter(
            registry=self.registry,
            output_dir=run_dir,
            privacy_mode=self.privacy_mode,
            prefer_mock=self.use_mock,
            http_transport=self.http_transport,
        )

        storyboard = self._storyboard_from_script(script)
        (run_dir / "storyboard.json").write_text(
            json.dumps({"shots": storyboard, "provider_id": provider_trace["script.plan"]}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        model = await Live2DModelGenerator(
            provider_registry_path=self.provider_registry_path,
            output_dir=run_dir,
            privacy_mode=self.privacy_mode,
            use_mock=self.use_mock,
        ).text_to_live2d(character_description)
        provider_trace["model.live2d.generate"] = model.provider_id

        shots = []
        for index, shot in enumerate(storyboard):
            shot_id = f"shot_{index + 1:02d}"
            voice_result = await router.invoke(
                "voice.generate",
                {
                    "text": str(shot["dialogue"]),
                    "emotion": str(shot["emotion"]),
                    "shot_id": shot_id,
                },
            )
            provider_trace["voice.generate"] = voice_result.provider_id
            if voice_result.warnings:
                provider_warnings.setdefault("voice.generate", []).extend(voice_result.warnings)

            motion_result = await router.invoke(
                "motion.generate",
                {
                    "shot": shot,
                    "model_path": model.model_path,
                    "audio_path": voice_result.artifacts.get("audio_path", ""),
                    "resolution": resolution,
                    "fps": fps,
                },
            )
            provider_trace["motion.generate"] = motion_result.provider_id
            if motion_result.warnings:
                provider_warnings.setdefault("motion.generate", []).extend(motion_result.warnings)
            video_path = motion_result.artifacts.get("video_path") or motion_result.artifacts.get("artifact_path", "")
            shots.append(
                ShotArtifact(
                    shot_id=shot_id,
                    dialogue=shot["dialogue"],
                    video_path=str(video_path),
                    audio_path=str(voice_result.artifacts.get("audio_path", "")),
                    duration=float(shot["duration"]),
                )
            )

        compose_result = await router.invoke(
            "video.compose",
            {
                "shots": [asdict(shot) for shot in shots],
                "resolution": resolution,
                "fps": fps,
                "duration": sum(shot.duration for shot in shots),
            },
        )
        final_path = Path(compose_result.artifacts["video_path"])
        provider_trace["video.compose"] = compose_result.provider_id
        if compose_result.warnings:
            provider_warnings.setdefault("video.compose", []).extend(compose_result.warnings)
        await asyncio.sleep(0)

        self.last_result = AnimationResult(
            task_id=task_id,
            video_path=str(final_path),
            model_path=model.model_path,
            total_time=time.perf_counter() - start,
            shots=shots,
            provider_trace=provider_trace,
            provider_warnings=provider_warnings,
            output_dir=str(run_dir),
        )
        return self.last_result

    async def generate_stream(
        self,
        script: str,
        character_description: str,
        resolution: str = "1920x1080",
        fps: int = 60,
    ):
        yield {"stage": "script.plan", "percent": 10}
        yield {"stage": "model.live2d.generate", "percent": 30}
        yield {"stage": "voice.generate", "percent": 55}
        yield {"stage": "motion.generate", "percent": 75}
        result = await self.generate(script, character_description, resolution=resolution, fps=fps)
        yield {"stage": "complete", "percent": 100, "result": result}

    def _storyboard_from_script(self, script: str) -> list[dict[str, object]]:
        lines = [line.strip() for line in script.splitlines() if line.strip()]
        if not lines:
            lines = [script.strip() or "Hello from L2MAS."]

        shots = []
        for index, line in enumerate(lines, start=1):
            dialogue = line.split(":", 1)[-1].strip() if ":" in line else line
            dialogue = dialogue.split("：", 1)[-1].strip() if "：" in dialogue else dialogue
            shots.append(
                {
                    "id": f"shot_{index:02d}",
                    "duration": 3.0,
                    "dialogue": dialogue,
                    "action": "talk" if index > 1 else "wave",
                    "emotion": "neutral" if index > 1 else "happy",
                }
            )
        return shots
