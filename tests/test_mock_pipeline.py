import tempfile
import unittest
from pathlib import Path

from live2d_ai import AnimationGenerator, Live2DModelGenerator


class MockPipelineTest(unittest.IsolatedAsyncioTestCase):
    async def test_text_to_live2d_creates_deterministic_mock_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            generator = Live2DModelGenerator(output_dir=tmp, use_mock=True)

            result = await generator.text_to_live2d(
                text_description="blue-haired Live2D character",
                style="anime",
                auto_rig=True,
                generate_physics=True,
            )

            model_path = Path(result.model_path)
            self.assertTrue(model_path.exists())
            self.assertEqual(result.provider_id, "mock-live2d-model")
            self.assertIn("model.model3.json", result.model_path)

    async def test_animation_generator_runs_without_cloud_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            generator = AnimationGenerator(output_dir=tmp, use_mock=True)

            result = await generator.generate(
                script="Shot 1: Hello there.\nShot 2: Welcome to L2MAS.",
                character_description="friendly anime presenter",
                resolution="1280x720",
                fps=30,
            )

            self.assertTrue(Path(result.video_path).exists())
            self.assertTrue(Path(result.model_path).exists())
            self.assertGreaterEqual(len(result.shots), 2)
            self.assertEqual(result.provider_trace["voice.generate"], "mock-voice")
            self.assertEqual(result.provider_trace["video.compose"], "mock-render")

    async def test_generate_stream_emits_progress_and_final_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            generator = AnimationGenerator(output_dir=tmp, use_mock=True)

            events = []
            async for event in generator.generate_stream(
                script="Shot 1: Stream this.",
                character_description="streaming test character",
            ):
                events.append(event)

            self.assertEqual(events[-1]["stage"], "complete")
            self.assertEqual(events[-1]["percent"], 100)
            self.assertTrue(Path(events[-1]["result"].video_path).exists())


if __name__ == "__main__":
    unittest.main()
