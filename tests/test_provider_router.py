import tempfile
import unittest
from pathlib import Path
from shutil import which

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


if __name__ == "__main__":
    unittest.main()
