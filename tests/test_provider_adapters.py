import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from live2d_ai import Provider, ProviderRegistry
from live2d_ai.providers import ProviderRouter


def make_provider(**overrides):
    raw = {
        "provider_id": "test-openai",
        "locality": "local",
        "protocol": "openai-compatible",
        "capabilities": ["script.plan"],
        "endpoint": "http://provider.test/v1",
        "models": ["test-model"],
        "hardware_profile": "test",
        "priority": 1,
        "fallbacks": [],
        "privacy_mode": "local-only",
        "status": "experimental",
    }
    raw.update(overrides)
    return Provider.from_dict(raw)


class ProviderAdapterContractTest(unittest.IsolatedAsyncioTestCase):
    async def test_openai_compatible_chat_adapter_writes_summary_and_raw_response(self):
        requests = []

        async def handler(request):
            requests.append(request)
            self.assertEqual(request["path"], "/v1/chat/completions")
            body = request["json"]
            self.assertEqual(body["model"], "test-model")
            self.assertEqual(body["messages"][-1]["content"], "Plan a short shot.")
            return {"status_code": 200, "json": {"choices": [{"message": {"content": "{\"shots\": []}"}}]}}

        provider = make_provider()
        registry = ProviderRegistry([provider])
        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(registry, tmp, http_transport=handler).invoke(
                "script.plan",
                {"prompt": "Plan a short shot."},
            )

            self.assertEqual(len(requests), 1)
            self.assertEqual(result.provider_id, "test-openai")
            self.assertEqual(result.status, "experimental")
            self.assertEqual(result.data["text"], "{\"shots\": []}")
            self.assertTrue(Path(result.raw_response_path).exists())

    async def test_ollama_adapter_uses_openai_compatible_chat_endpoint(self):
        async def handler(request):
            self.assertEqual(request["path"], "/v1/chat/completions")
            body = request["json"]
            self.assertEqual(body["model"], "qwen3")
            return {"status_code": 200, "json": {"choices": [{"message": {"content": "ok"}}]}}

        provider = make_provider(
            provider_id="local-ollama-agent",
            protocol="ollama",
            endpoint="http://ollama.test",
            models=["qwen3"],
        )
        registry = ProviderRegistry([provider])
        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(registry, tmp, http_transport=handler).invoke(
                "script.plan",
                {"prompt": "hello"},
            )

        self.assertEqual(result.data["text"], "ok")

    async def test_openai_compatible_transcription_adapter_posts_audio_shape(self):
        async def handler(request):
            self.assertEqual(request["path"], "/v1/audio/transcriptions")
            body = request["json"]
            self.assertEqual(body["model"], "whisper-local")
            self.assertEqual(body["audio_path"], "speech.wav")
            return {"status_code": 200, "json": {"text": "hello transcript"}}

        provider = make_provider(
            provider_id="local-openai-transcribe",
            protocol="openai-compatible",
            capabilities=["speech.transcribe"],
            endpoint="http://asr.test/v1",
            models=["whisper-local"],
        )
        registry = ProviderRegistry([provider])
        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(registry, tmp, http_transport=handler).invoke(
                "speech.transcribe",
                {"audio_path": "speech.wav"},
            )

            self.assertEqual(result.data["text"], "hello transcript")
            self.assertTrue(Path(result.artifacts["artifact_path"]).exists())

    async def test_comfyui_adapter_submits_prompt_and_records_history_artifact(self):
        async def handler(request):
            if request["path"] == "/prompt":
                body = request["json"]
                self.assertIn("prompt", body)
                return {"status_code": 200, "json": {"prompt_id": "abc123"}}
            if request["path"] == "/history/abc123":
                return {"status_code": 200, "json": {"abc123": {"outputs": {"1": {"images": [{"filename": "frame.png"}]}}}}}
            return {"status_code": 404, "json": {}}

        provider = make_provider(
            provider_id="local-comfyui-visual",
            protocol="comfyui",
            capabilities=["character.generate"],
            endpoint="http://comfy.test",
            models=["workflow:character_generate"],
        )
        registry = ProviderRegistry([provider])
        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(registry, tmp, http_transport=handler).invoke(
                "character.generate",
                {"prompt": "blue hair"},
            )

            self.assertEqual(result.data["prompt_id"], "abc123")
            self.assertIn("history_path", result.artifacts)
            self.assertTrue(Path(result.artifacts["history_path"]).exists())

    async def test_elevenlabs_adapter_requires_auth_and_writes_audio_bytes(self):
        async def handler(request):
            self.assertEqual(request["path"], "/v1/text-to-speech/voice-1")
            self.assertEqual(request["headers"]["xi-api-key"], "test-key")
            body = request["json"]
            self.assertEqual(body["text"], "hello")
            return {"status_code": 200, "content": b"mp3-bytes"}

        provider = make_provider(
            provider_id="cloud-elevenlabs-voice",
            locality="cloud",
            protocol="custom-rest",
            capabilities=["voice.generate"],
            endpoint="http://eleven.test",
            models=["eleven_v3"],
            auth_env="ELEVENLABS_API_KEY",
            live_test_env="L2MAS_LIVE_ELEVENLABS",
            privacy_mode="remote",
        )
        registry = ProviderRegistry([provider])
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test-key"}, clear=False):
            with tempfile.TemporaryDirectory() as tmp:
                result = await ProviderRouter(
                    registry,
                    tmp,
                    privacy_mode="remote",
                    http_transport=handler,
                ).invoke(
                    "voice.generate",
                    {"text": "hello", "voice_id": "voice-1"},
                    )

                audio_path = Path(result.artifacts["audio_path"])
                self.assertEqual(audio_path.read_bytes(), b"mp3-bytes")

    async def test_generic_rest_adapter_posts_capability_payload(self):
        async def handler(request):
            self.assertEqual(request["path"], "/invoke")
            body = request["json"]
            self.assertEqual(body["capability"], "voice.convert")
            return {"status_code": 200, "json": {"data": {"converted": True}, "artifacts": {"audio_path": "out.wav"}}}

        provider = make_provider(
            provider_id="local-rvc",
            protocol="custom-rest",
            capabilities=["voice.convert"],
            endpoint="http://rvc.test",
            status="template",
        )
        registry = ProviderRegistry([provider])
        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(registry, tmp, http_transport=handler).invoke(
                "voice.convert",
                {"audio_path": "in.wav"},
            )

        self.assertEqual(result.status, "template")
        self.assertEqual(result.data["converted"], True)
        self.assertEqual(result.artifacts["audio_path"], "out.wav")

    async def test_mcp_template_boundary_records_request_without_network_call(self):
        provider = make_provider(
            provider_id="local-live2d-motion",
            protocol="mcp",
            capabilities=["motion.generate"],
            endpoint="http://motion.test/mcp",
            status="template",
        )
        registry = ProviderRegistry([provider])
        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(registry, tmp).invoke(
                "motion.generate",
                {"shot": "wave"},
            )

            self.assertEqual(result.provider_id, "local-live2d-motion")
            self.assertEqual(result.status, "template")
            self.assertIn("artifact_path", result.artifacts)
            self.assertIn("MCP adapter boundary", Path(result.artifacts["artifact_path"]).read_text())


if __name__ == "__main__":
    unittest.main()
