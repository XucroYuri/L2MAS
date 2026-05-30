import tempfile
import unittest
from pathlib import Path
from shutil import which

from live2d_ai import Provider, ProviderRegistry
from live2d_ai.providers import ProviderRouter


class ProviderRouterTest(unittest.IsolatedAsyncioTestCase):
    async def test_invokes_mock_voice_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            router = ProviderRouter(output_dir=tmp, prefer_mock=True)

            result = await router.invoke("voice.generate", {"text": "hello"})

            self.assertEqual(result.provider_id, "mock-voice")
            self.assertTrue(Path(result.artifacts["audio_path"]).exists())

    async def test_invokes_mock_video_compose_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            router = ProviderRouter(output_dir=tmp, prefer_mock=True)

            result = await router.invoke("video.compose", {"shots": []})

            self.assertEqual(result.provider_id, "mock-render")
            self.assertTrue(Path(result.artifacts["video_path"]).exists())

    @unittest.skipUnless(which("ffmpeg"), "ffmpeg is not available")
    async def test_invokes_local_ffmpeg_video_compose_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            router = ProviderRouter(output_dir=tmp, prefer_mock=False)

            result = await router.invoke(
                "video.compose",
                {"shots": [], "resolution": "320x180", "fps": 12, "duration": 1.0},
            )

            video_path = Path(result.artifacts["video_path"])
            self.assertEqual(result.provider_id, "local-ffmpeg")
            self.assertTrue(video_path.exists())
            self.assertGreater(video_path.stat().st_size, 1000)

    async def test_falls_back_to_declared_provider_when_adapter_fails(self):
        async def failing_transport(request):
            return {"status_code": 503, "json": {"error": "service unavailable"}}

        primary = Provider.from_dict(
            {
                "provider_id": "local-tts",
                "locality": "local",
                "protocol": "custom-rest",
                "capabilities": ["voice.generate"],
                "endpoint": "http://tts.test",
                "models": ["local-tts"],
                "hardware_profile": "test",
                "priority": 1,
                "fallbacks": ["mock-voice"],
                "privacy_mode": "local-only",
                "status": "template",
            }
        )
        fallback = Provider.from_dict(
            {
                "provider_id": "mock-voice",
                "locality": "local",
                "protocol": "custom-rest",
                "capabilities": ["voice.generate"],
                "endpoint": "mock://voice",
                "models": ["silent-audio"],
                "hardware_profile": "none",
                "priority": 100,
                "fallbacks": [],
                "privacy_mode": "local-only",
                "status": "mock",
            }
        )
        registry = ProviderRegistry([primary, fallback])

        with tempfile.TemporaryDirectory() as tmp:
            result = await ProviderRouter(
                registry=registry,
                output_dir=tmp,
                http_transport=failing_transport,
            ).invoke("voice.generate", {"text": "fallback please"})

            self.assertEqual(result.provider_id, "mock-voice")
            self.assertTrue(Path(result.artifacts["audio_path"]).exists())
            self.assertIn("local-tts", result.warnings[0])


if __name__ == "__main__":
    unittest.main()
