"""Provider invocation adapters for local and mock MVP execution."""

from __future__ import annotations

import asyncio
import inspect
import json
import os
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path
from shutil import which
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from .provider_registry import Provider, ProviderRegistry

HttpTransport = Callable[[dict[str, Any]], Any]


@dataclass(frozen=True)
class ProviderInvocationResult:
    capability: str
    provider_id: str
    artifacts: dict[str, str]
    data: dict[str, object]
    status: str
    metadata: dict[str, object]
    warnings: tuple[str, ...] = ()
    raw_response_path: str | None = None


class ProviderAdapterError(RuntimeError):
    """Raised when a provider adapter cannot produce a valid result."""


class ProviderRouter:
    """Select a provider from the registry and invoke a local/mock adapter."""

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        output_dir: str | Path = "output/mvp",
        privacy_mode: str = "local-only",
        prefer_mock: bool = False,
        http_transport: HttpTransport | None = None,
    ):
        self.registry = registry or ProviderRegistry.default()
        self.output_dir = Path(output_dir)
        self.privacy_mode = privacy_mode
        self.prefer_mock = prefer_mock
        self.http_transport = http_transport

    def select(self, capability: str) -> Provider:
        return self.registry.select(
            capability,
            privacy_mode=self.privacy_mode,
            prefer_mock=self.prefer_mock,
        )

    async def invoke(self, capability: str, payload: dict[str, object]) -> ProviderInvocationResult:
        provider = self.select(capability)
        warnings: list[str] = []
        for candidate in [provider, *self._fallback_providers(provider, capability)]:
            try:
                result = await self._invoke_provider(candidate, capability, payload)
                if warnings:
                    return replace(result, warnings=tuple(warnings) + result.warnings)
                return result
            except ProviderAdapterError as exc:
                warnings.append(f"{candidate.provider_id}: {exc}")
        raise ProviderAdapterError("; ".join(warnings))

    async def _invoke_provider(
        self,
        provider: Provider,
        capability: str,
        payload: dict[str, object],
    ) -> ProviderInvocationResult:
        if provider.is_mock:
            return self._invoke_mock(provider, capability, payload)

        if capability == "video.compose" and provider.provider_id == "local-ffmpeg":
            return self._invoke_local_ffmpeg(provider, payload)

        if provider.protocol == "openai-compatible" and capability == "speech.transcribe":
            return await self._invoke_openai_transcription(provider, capability, payload)

        if provider.protocol in {"openai-compatible", "ollama"}:
            return await self._invoke_openai_chat(provider, capability, payload)

        if provider.protocol == "comfyui":
            return await self._invoke_comfyui(provider, capability, payload)

        if provider.protocol == "custom-rest":
            return await self._invoke_custom_rest(provider, capability, payload)

        if provider.protocol == "mcp":
            return self._invoke_mcp_template(provider, capability, payload)

        raise ProviderAdapterError(f"Unsupported provider protocol: {provider.protocol}")

    def _fallback_providers(self, provider: Provider, capability: str) -> list[Provider]:
        fallbacks: list[Provider] = []
        seen = {provider.provider_id}
        queue = list(provider.fallbacks)
        while queue:
            provider_id = queue.pop(0)
            if provider_id in seen:
                continue
            seen.add(provider_id)
            try:
                fallback = self.registry.get(provider_id)
            except ValueError:
                continue
            if capability not in fallback.capabilities or not self._privacy_allows(fallback):
                continue
            fallbacks.append(fallback)
            queue.extend(fallback.fallbacks)
        return fallbacks

    def _privacy_allows(self, provider: Provider) -> bool:
        if self.privacy_mode == "local-only":
            return provider.locality == "local"
        if self.privacy_mode == "remote":
            return provider.locality in {"cloud", "hybrid"}
        return True

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
                status=provider.status,
                metadata=self._metadata(provider),
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
                status=provider.status,
                metadata=self._metadata(provider),
            )

        artifact_path = run_dir / f"{capability.replace('.', '_')}_{uuid4().hex[:8]}.json"
        artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return ProviderInvocationResult(
            capability=capability,
            provider_id=provider.provider_id,
            artifacts={"artifact_path": str(artifact_path)},
            data={},
            status=provider.status,
            metadata=self._metadata(provider),
        )

    async def _invoke_openai_chat(
        self,
        provider: Provider,
        capability: str,
        payload: dict[str, object],
    ) -> ProviderInvocationResult:
        prompt = str(payload.get("prompt") or payload.get("text") or payload)
        body = {
            "model": provider.models[0] if provider.models else "default",
            "messages": [
                {"role": "system", "content": f"You are the L2MAS provider for {capability}."},
                {"role": "user", "content": prompt},
            ],
            "temperature": float(payload.get("temperature", 0.2)),
        }
        response = await self._send_http(
            provider,
            "POST",
            "/v1/chat/completions" if provider.protocol == "ollama" else "/chat/completions",
            json_body=body,
        )
        raw_response_path = self._write_raw_response(provider, capability, response)
        response_json = dict(response.get("json") or {})
        text = self._extract_openai_text(response_json)
        artifact_path = self._write_json_artifact(
            provider,
            capability,
            {"text": text, "response": response_json},
        )
        return ProviderInvocationResult(
            capability=capability,
            provider_id=provider.provider_id,
            artifacts={"artifact_path": artifact_path},
            data={"text": text},
            status=provider.status,
            metadata=self._metadata(provider),
            raw_response_path=raw_response_path,
        )

    async def _invoke_openai_transcription(
        self,
        provider: Provider,
        capability: str,
        payload: dict[str, object],
    ) -> ProviderInvocationResult:
        body = {
            "model": provider.models[0] if provider.models else "whisper",
            "audio_path": str(payload.get("audio_path", "")),
            "language": str(payload.get("language", "")),
        }
        response = await self._send_http(provider, "POST", "/audio/transcriptions", json_body=body)
        raw_response_path = self._write_raw_response(provider, capability, response)
        response_json = dict(response.get("json") or {})
        text = str(response_json.get("text", ""))
        artifact_path = self._write_json_artifact(
            provider,
            capability,
            {"text": text, "response": response_json},
        )
        return ProviderInvocationResult(
            capability=capability,
            provider_id=provider.provider_id,
            artifacts={"artifact_path": artifact_path},
            data={"text": text},
            status=provider.status,
            metadata=self._metadata(provider),
            raw_response_path=raw_response_path,
        )

    async def _invoke_comfyui(
        self,
        provider: Provider,
        capability: str,
        payload: dict[str, object],
    ) -> ProviderInvocationResult:
        workflow = payload.get("workflow") or {"prompt": payload.get("prompt", ""), "capability": capability}
        response = await self._send_http(provider, "POST", "/prompt", json_body={"prompt": workflow})
        response_json = dict(response.get("json") or {})
        prompt_id = str(response_json.get("prompt_id", ""))
        if not prompt_id:
            raise ProviderAdapterError("ComfyUI response did not include prompt_id")

        history = await self._send_http(provider, "GET", f"/history/{prompt_id}")
        history_path = self._write_json_artifact(
            provider,
            capability,
            {"prompt_id": prompt_id, "history": history.get("json") or {}},
            suffix="history",
        )
        raw_response_path = self._write_raw_response(provider, capability, response)
        return ProviderInvocationResult(
            capability=capability,
            provider_id=provider.provider_id,
            artifacts={"history_path": history_path},
            data={"prompt_id": prompt_id},
            status=provider.status,
            metadata=self._metadata(provider),
            raw_response_path=raw_response_path,
        )

    async def _invoke_custom_rest(
        self,
        provider: Provider,
        capability: str,
        payload: dict[str, object],
    ) -> ProviderInvocationResult:
        if provider.provider_id == "cloud-elevenlabs-voice":
            return await self._invoke_elevenlabs(provider, capability, payload)

        response = await self._send_http(
            provider,
            "POST",
            "/invoke",
            json_body={"capability": capability, "payload": payload, "model": provider.models[0] if provider.models else ""},
        )
        raw_response_path = self._write_raw_response(provider, capability, response)
        response_json = dict(response.get("json") or {})
        artifacts = {str(key): str(value) for key, value in dict(response_json.get("artifacts") or {}).items()}
        data = dict(response_json.get("data") or {})
        if not artifacts:
            artifacts["artifact_path"] = self._write_json_artifact(provider, capability, response_json or {"payload": payload})
        return ProviderInvocationResult(
            capability=capability,
            provider_id=provider.provider_id,
            artifacts=artifacts,
            data=data,
            status=provider.status,
            metadata=self._metadata(provider),
            raw_response_path=raw_response_path,
        )

    async def _invoke_elevenlabs(
        self,
        provider: Provider,
        capability: str,
        payload: dict[str, object],
    ) -> ProviderInvocationResult:
        voice_id = str(payload.get("voice_id", "default"))
        response = await self._send_http(
            provider,
            "POST",
            f"/v1/text-to-speech/{voice_id}",
            json_body={
                "text": str(payload.get("text", "")),
                "model_id": str(payload.get("model_id", provider.models[0] if provider.models else "eleven_v3")),
            },
            headers={"xi-api-key": self._require_auth(provider)},
        )
        run_dir = self.output_dir / "provider-router"
        run_dir.mkdir(parents=True, exist_ok=True)
        audio_path = run_dir / f"voice_{uuid4().hex[:8]}.mp3"
        audio_path.write_bytes(bytes(response.get("content") or b""))
        raw_response_path = self._write_raw_response(provider, capability, response)
        return ProviderInvocationResult(
            capability=capability,
            provider_id=provider.provider_id,
            artifacts={"audio_path": str(audio_path)},
            data={"duration": payload.get("duration", 0.0)},
            status=provider.status,
            metadata=self._metadata(provider),
            raw_response_path=raw_response_path,
        )

    def _invoke_mcp_template(
        self,
        provider: Provider,
        capability: str,
        payload: dict[str, object],
    ) -> ProviderInvocationResult:
        artifact_path = self._write_json_artifact(
            provider,
            capability,
            {
                "kind": "MCP adapter boundary",
                "endpoint": provider.endpoint,
                "capability": capability,
                "payload": payload,
            },
        )
        return ProviderInvocationResult(
            capability=capability,
            provider_id=provider.provider_id,
            artifacts={"artifact_path": artifact_path},
            data={"boundary": "mcp"},
            status=provider.status,
            metadata=self._metadata(provider),
            warnings=("MCP template boundary only; no live MCP request was sent.",),
        )

    def _invoke_local_ffmpeg(
        self,
        provider: Provider,
        payload: dict[str, object],
    ) -> ProviderInvocationResult:
        ffmpeg = which("ffmpeg")
        if not ffmpeg:
            fallback = self.registry.get("mock-render")
            return self._invoke_mock(fallback, "video.compose", payload)

        run_dir = self.output_dir / "provider-router"
        run_dir.mkdir(parents=True, exist_ok=True)
        video_path = run_dir / f"video_{uuid4().hex[:8]}.mp4"
        resolution = str(payload.get("resolution", "640x360"))
        fps = int(payload.get("fps", 24))
        duration = float(payload.get("duration", 1.0))
        duration = max(duration, 0.5)

        subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"testsrc=size={resolution}:rate={fps}",
                "-t",
                f"{duration:.3f}",
                "-pix_fmt",
                "yuv420p",
                str(video_path),
            ],
            check=True,
        )
        return ProviderInvocationResult(
            capability="video.compose",
            provider_id=provider.provider_id,
            artifacts={"video_path": str(video_path)},
            data={"duration": duration, "resolution": resolution, "fps": fps},
            status=provider.status,
            metadata=self._metadata(provider),
        )

    async def _send_http(
        self,
        provider: Provider,
        method: str,
        path: str,
        json_body: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        request = self._build_request(provider, method, path, json_body=json_body, headers=headers)
        transport = self.http_transport or self._default_http_transport
        response = transport(request)
        if inspect.isawaitable(response):
            response = await response
        normalized = self._normalize_response(response)
        status_code = int(normalized["status_code"])
        if status_code >= 400:
            raise ProviderAdapterError(f"Provider {provider.provider_id} returned HTTP {status_code}")
        return normalized

    def _build_request(
        self,
        provider: Provider,
        method: str,
        path: str,
        json_body: dict[str, object] | None,
        headers: dict[str, str] | None,
    ) -> dict[str, object]:
        outbound_headers = {"content-type": "application/json"}
        if provider.auth_env and provider.provider_id != "cloud-elevenlabs-voice":
            outbound_headers["authorization"] = f"Bearer {self._require_auth(provider)}"
        if headers:
            outbound_headers.update(headers)
        path = self._provider_path(provider, path)
        url = f"{provider.endpoint.rstrip('/')}{path}"
        return {
            "method": method,
            "url": url,
            "path": urlparse(url).path,
            "headers": outbound_headers,
            "json": json_body,
            "body": json.dumps(json_body).encode("utf-8") if json_body is not None else None,
        }

    def _provider_path(self, provider: Provider, path: str) -> str:
        if provider.protocol == "openai-compatible" and provider.endpoint.rstrip("/").endswith("/v1"):
            return path
        return path if path.startswith("/v1/") or provider.protocol != "ollama" else path

    async def _default_http_transport(self, request: dict[str, object]) -> dict[str, object]:
        return await asyncio.to_thread(self._blocking_http_transport, request)

    def _blocking_http_transport(self, request: dict[str, object]) -> dict[str, object]:
        try:
            url_request = Request(
                str(request["url"]),
                data=request.get("body"),
                headers=dict(request.get("headers") or {}),
                method=str(request["method"]),
            )
            with urlopen(url_request, timeout=30) as response:
                content = response.read()
                return self._response_from_bytes(response.status, content, response.headers.get("content-type", ""))
        except HTTPError as exc:
            return self._response_from_bytes(exc.code, exc.read(), exc.headers.get("content-type", ""))
        except URLError as exc:
            raise ProviderAdapterError(f"Provider HTTP request failed: {exc}") from exc

    def _response_from_bytes(self, status_code: int, content: bytes, content_type: str) -> dict[str, object]:
        response: dict[str, object] = {"status_code": status_code, "content": content, "content_type": content_type}
        if "json" in content_type.lower():
            try:
                response["json"] = json.loads(content.decode("utf-8"))
            except json.JSONDecodeError:
                response["json"] = {}
        return response

    def _normalize_response(self, response: object) -> dict[str, object]:
        if not isinstance(response, dict):
            raise ProviderAdapterError("HTTP transport must return a response dictionary")
        normalized = dict(response)
        normalized.setdefault("status_code", 200)
        if "json" not in normalized and normalized.get("content"):
            try:
                normalized["json"] = json.loads(bytes(normalized["content"]).decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                normalized["json"] = {}
        normalized.setdefault("json", {})
        normalized.setdefault("content", b"")
        return normalized

    def _require_auth(self, provider: Provider) -> str:
        if not provider.auth_env:
            return ""
        value = os.getenv(provider.auth_env)
        if not value:
            raise ProviderAdapterError(f"Provider {provider.provider_id} requires {provider.auth_env}")
        return value

    def _extract_openai_text(self, response_json: dict[str, object]) -> str:
        choices = response_json.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                message = first.get("message")
                if isinstance(message, dict) and message.get("content") is not None:
                    return str(message["content"])
                if first.get("text") is not None:
                    return str(first["text"])
        return json.dumps(response_json, ensure_ascii=False)

    def _write_json_artifact(
        self,
        provider: Provider,
        capability: str,
        payload: dict[str, object],
        suffix: str = "artifact",
    ) -> str:
        run_dir = self.output_dir / "provider-router"
        run_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = run_dir / f"{provider.provider_id}_{capability.replace('.', '_')}_{suffix}_{uuid4().hex[:8]}.json"
        artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(artifact_path)

    def _write_raw_response(
        self,
        provider: Provider,
        capability: str,
        response: dict[str, object],
    ) -> str:
        summary = {
            "status_code": response.get("status_code"),
            "json": response.get("json", {}),
            "content_length": len(bytes(response.get("content") or b"")),
        }
        return self._write_json_artifact(provider, capability, summary, suffix="raw")

    def _metadata(self, provider: Provider) -> dict[str, object]:
        parsed = urlparse(provider.endpoint)
        return {
            "locality": provider.locality,
            "protocol": provider.protocol,
            "status": provider.status,
            "models": list(provider.models),
            "endpoint_host": parsed.netloc,
            "live_test_env": provider.live_test_env,
            "auth_env": provider.auth_env,
        }
