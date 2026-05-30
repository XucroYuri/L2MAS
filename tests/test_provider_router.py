import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
