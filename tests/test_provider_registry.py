import unittest
from pathlib import Path

from live2d_ai import ProviderRegistry


class ProviderRegistryTest(unittest.TestCase):
    def test_selects_mock_provider_for_capability_when_requested(self):
        registry = ProviderRegistry.from_file(Path("config/provider_registry.example.json"))

        provider = registry.select("voice.generate", privacy_mode="local-only", prefer_mock=True)

        self.assertEqual(provider.provider_id, "mock-voice")
        self.assertEqual(provider.endpoint, "mock://voice")

    def test_selects_local_provider_for_local_only_privacy(self):
        registry = ProviderRegistry.from_file(Path("config/provider_registry.example.json"))

        provider = registry.select("video.compose", privacy_mode="local-only")

        self.assertEqual(provider.provider_id, "local-ffmpeg")
        self.assertEqual(provider.locality, "local")

    def test_rejects_unknown_capability(self):
        registry = ProviderRegistry.from_file(Path("config/provider_registry.example.json"))

        with self.assertRaisesRegex(ValueError, "No provider supports capability"):
            registry.select("unknown.capability")


if __name__ == "__main__":
    unittest.main()
