"""Provider invocation adapters for local and mock MVP execution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .provider_registry import Provider, ProviderRegistry


@dataclass(frozen=True)
class ProviderInvocationResult:
    capability: str
    provider_id: str
    artifacts: dict[str, str]
    data: dict[str, object]


class ProviderRouter:
    """Select a provider from the registry and invoke a local/mock adapter."""

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        output_dir: str | Path = "output/mvp",
        privacy_mode: str = "local-only",
        prefer_mock: bool = False,
    ):
        self.registry = registry or ProviderRegistry.default()
        self.output_dir = Path(output_dir)
        self.privacy_mode = privacy_mode
        self.prefer_mock = prefer_mock

    def select(self, capability: str) -> Provider:
        return self.registry.select(
            capability,
            privacy_mode=self.privacy_mode,
            prefer_mock=self.prefer_mock,
        )

    async def invoke(self, capability: str, payload: dict[str, object]) -> ProviderInvocationResult:
        provider = self.select(capability)
        if provider.is_mock:
            return self._invoke_mock(provider, capability, payload)

        return ProviderInvocationResult(
            capability=capability,
            provider_id=provider.provider_id,
            artifacts={},
            data={"provider": provider.provider_id, "payload": payload},
        )

    def _invoke_mock(
        self,
        provider: Provider,
        capability: str,
        payload: dict[str, object],
    ) -> ProviderInvocationResult:
        run_dir = self.output_dir / "provider-router"
        run_dir.mkdir(parents=True, exist_ok=True)

        if capability == "voice.generate":
            audio_path = run_dir / f"voice_{uuid4().hex[:8]}.txt"
            audio_path.write_text(str(payload.get("text", "")), encoding="utf-8")
            return ProviderInvocationResult(
                capability=capability,
                provider_id=provider.provider_id,
                artifacts={"audio_path": str(audio_path)},
                data={"duration": 1.0, "phonemes": []},
            )

        if capability == "video.compose":
            video_path = run_dir / f"video_{uuid4().hex[:8]}.mp4"
            video_path.write_text(
                json.dumps(
                    {"kind": "L2MAS mock composed video", "payload": payload},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            return ProviderInvocationResult(
                capability=capability,
                provider_id=provider.provider_id,
                artifacts={"video_path": str(video_path)},
                data={"duration": 0.0},
            )

        artifact_path = run_dir / f"{capability.replace('.', '_')}_{uuid4().hex[:8]}.json"
        artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return ProviderInvocationResult(
            capability=capability,
            provider_id=provider.provider_id,
            artifacts={"artifact_path": str(artifact_path)},
            data={},
        )
