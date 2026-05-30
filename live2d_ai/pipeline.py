"""Deterministic local MVP pipeline for smoke tests and examples."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from uuid import uuid4

from .provider_registry import ProviderRegistry


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
    ):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.registry = (
            ProviderRegistry.from_file(provider_registry_path)
            if provider_registry_path
            else ProviderRegistry.default()
        )
        self.output_dir = Path(output_dir)
        self.privacy_mode = privacy_mode
        self.use_mock = use_mock
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

        storyboard = self._storyboard_from_script(script)
        (run_dir / "storyboard.json").write_text(
            json.dumps({"shots": storyboard, "provider_id": provider_trace["script.plan"]}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        model = await Live2DModelGenerator(
            provider_registry_path=None,
            output_dir=run_dir,
            privacy_mode=self.privacy_mode,
            use_mock=self.use_mock,
        ).text_to_live2d(character_description)

        shots = []
        for index, shot in enumerate(storyboard):
            shot_id = f"shot_{index + 1:02d}"
            audio_path = run_dir / "audio" / f"{shot_id}.txt"
            video_path = run_dir / "shots" / f"{shot_id}.mp4"
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            video_path.parent.mkdir(parents=True, exist_ok=True)
            audio_path.write_text(
                f"provider={provider_trace['voice.generate']}\ndialogue={shot['dialogue']}\n",
                encoding="utf-8",
            )
            video_path.write_text(
                "\n".join(
                    [
                        "L2MAS mock shot artifact",
                        f"provider={provider_trace['motion.generate']}",
                        f"model={model.model_path}",
                        f"dialogue={shot['dialogue']}",
                        f"resolution={resolution}",
                        f"fps={fps}",
                    ]
                ),
                encoding="utf-8",
            )
            shots.append(
                ShotArtifact(
                    shot_id=shot_id,
                    dialogue=shot["dialogue"],
                    video_path=str(video_path),
                    audio_path=str(audio_path),
                    duration=float(shot["duration"]),
                )
            )

        final_path = run_dir / "final.mp4"
        final_path.write_text(
            json.dumps(
                {
                    "kind": "L2MAS mock final video",
                    "provider_id": provider_trace["video.compose"],
                    "shots": [asdict(shot) for shot in shots],
                    "resolution": resolution,
                    "fps": fps,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        await asyncio.sleep(0)

        self.last_result = AnimationResult(
            task_id=task_id,
            video_path=str(final_path),
            model_path=model.model_path,
            total_time=time.perf_counter() - start,
            shots=shots,
            provider_trace=provider_trace,
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
