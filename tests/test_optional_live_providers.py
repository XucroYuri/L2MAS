import os
import tempfile
import unittest
from pathlib import Path

from live2d_ai.providers import ProviderRouter


class OptionalLiveProviderTest(unittest.IsolatedAsyncioTestCase):
    @unittest.skipUnless(os.getenv("L2MAS_LIVE_OLLAMA"), "set L2MAS_LIVE_OLLAMA=1 to run Ollama live test")
    async def test_live_ollama_script_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(output_dir=tmp, privacy_mode="local-only").invoke(
                "script.plan",
                {"prompt": "Return a one-shot storyboard for a wave greeting."},
            )

            self.assertEqual(result.provider_id, "local-ollama-agent")
            self.assertEqual(result.status, "experimental")
            self.assertTrue(Path(result.artifacts["artifact_path"]).exists())

    @unittest.skipUnless(os.getenv("L2MAS_LIVE_COMFYUI"), "set L2MAS_LIVE_COMFYUI=1 to run ComfyUI live test")
    async def test_live_comfyui_character_generate(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(output_dir=tmp, privacy_mode="local-only").invoke(
                "character.generate",
                {"prompt": "simple blue-haired Live2D character reference"},
            )

            self.assertEqual(result.provider_id, "local-comfyui-visual")
            self.assertEqual(result.status, "experimental")
            self.assertTrue(Path(result.artifacts["history_path"]).exists())

    @unittest.skipUnless(
        os.getenv("L2MAS_LIVE_OPENAI_WHISPER"),
        "set L2MAS_LIVE_OPENAI_WHISPER=1 to run OpenAI-compatible Whisper live test",
    )
    async def test_live_openai_whisper_transcribe(self):
        audio_path = os.getenv("L2MAS_LIVE_WHISPER_AUDIO", "speech.wav")
        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(output_dir=tmp, privacy_mode="local-only").invoke(
                "speech.transcribe",
                {"audio_path": audio_path},
            )

            self.assertEqual(result.provider_id, "local-openai-whisper")
            self.assertEqual(result.status, "template")
            self.assertTrue(Path(result.artifacts["artifact_path"]).exists())

    @unittest.skipUnless(
        os.getenv("L2MAS_LIVE_ELEVENLABS") and os.getenv("ELEVENLABS_API_KEY"),
        "set L2MAS_LIVE_ELEVENLABS=1 and ELEVENLABS_API_KEY to run ElevenLabs live test",
    )
    async def test_live_elevenlabs_voice_generate(self):
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(output_dir=tmp, privacy_mode="remote").invoke(
                "voice.generate",
                {"text": "Hello from L2MAS.", "voice_id": voice_id},
            )

            self.assertEqual(result.provider_id, "cloud-elevenlabs-voice")
            self.assertEqual(result.status, "experimental")
            self.assertGreater(Path(result.artifacts["audio_path"]).stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
