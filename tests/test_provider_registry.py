import unittest
import json
import tempfile
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

    def test_loads_v02_provider_metadata(self):
        registry = ProviderRegistry.from_file(Path("config/provider_registry.example.json"))

        ffmpeg = registry.get("local-ffmpeg")
        self.assertEqual(ffmpeg.status, "verified")
        self.assertEqual(ffmpeg.live_test_env, "L2MAS_LIVE_FFMPEG")
        self.assertIsNone(ffmpeg.auth_env)
        self.assertEqual(ffmpeg.healthcheck["type"], "binary")
        self.assertEqual(ffmpeg.verification_evidence, "docs/verification/local-ffmpeg.json")

        elevenlabs = registry.get("cloud-elevenlabs-voice")
        self.assertEqual(elevenlabs.status, "experimental")
        self.assertEqual(elevenlabs.auth_env, "ELEVENLABS_API_KEY")
        self.assertEqual(elevenlabs.live_test_env, "L2MAS_LIVE_ELEVENLABS")

    def test_preserves_v01_registry_compatibility_for_optional_metadata(self):
        payload = {
            "providers": [
                {
                    "provider_id": "legacy-mock",
                    "locality": "local",
                    "protocol": "custom-rest",
                    "capabilities": ["voice.generate"],
                    "endpoint": "mock://legacy",
                    "models": ["deterministic"],
                    "hardware_profile": "none",
                    "priority": 1,
                    "fallbacks": [],
                    "privacy_mode": "local-only",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            provider = ProviderRegistry.from_file(path).get("legacy-mock")

        self.assertEqual(provider.status, "mock")
        self.assertIsNone(provider.live_test_env)
        self.assertIsNone(provider.auth_env)
        self.assertEqual(provider.healthcheck, {})
        self.assertIsNone(provider.verification_evidence)

    def test_rejects_unknown_provider_status(self):
        payload = {
            "providers": [
                {
                    "provider_id": "bad-status",
                    "locality": "local",
                    "protocol": "custom-rest",
                    "capabilities": ["voice.generate"],
                    "endpoint": "mock://bad",
                    "models": ["deterministic"],
                    "hardware_profile": "none",
                    "priority": 1,
                    "fallbacks": [],
                    "privacy_mode": "local-only",
                    "status": "available",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Unsupported provider status"):
                ProviderRegistry.from_file(path)


if __name__ == "__main__":
    unittest.main()
