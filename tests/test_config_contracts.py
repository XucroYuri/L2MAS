import json
import unittest
from pathlib import Path


STANDARD_CAPABILITIES = {
    "script.plan",
    "character.generate",
    "model.live2d.generate",
    "voice.generate",
    "speech.transcribe",
    "voice.convert",
    "lip_sync.align",
    "motion.generate",
    "video.compose",
    "video.edit",
    "quality.review",
}


class ConfigContractTest(unittest.TestCase):
    def test_a2a_config_uses_standard_capability_names(self):
        config = json.loads(Path("config/a2a_config.json").read_text(encoding="utf-8"))

        for agent in config["agents"]:
            for capability in agent["capabilities"]:
                self.assertIn(capability, STANDARD_CAPABILITIES)

    def test_provider_statuses_are_documented_and_verified_claims_have_records(self):
        registry = json.loads(Path("config/provider_registry.example.json").read_text(encoding="utf-8"))
        verification_path = Path("docs/provider-verification.md")
        verification = verification_path.read_text(encoding="utf-8")
        allowed = {"verified", "experimental", "template", "mock"}

        for provider in registry["providers"]:
            status = provider.get("status")
            self.assertIn(status, allowed)
            if status == "verified":
                self.assertIn(f"| `{provider['provider_id']}` |", verification)
                self.assertIn("| verified |", verification)
                evidence_path = Path(provider["verification_evidence"])
                evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                self.assertEqual(evidence["provider_id"], provider["provider_id"])
                self.assertEqual(evidence["result"], "passed")

    def test_public_docs_do_not_overclaim_unverified_providers(self):
        registry = json.loads(Path("config/provider_registry.example.json").read_text(encoding="utf-8"))
        verified = {provider["provider_id"] for provider in registry["providers"] if provider.get("status") == "verified"}
        unverified = {
            provider["provider_id"]
            for provider in registry["providers"]
            if provider.get("status") in {"experimental", "template"}
        }
        docs = "\n".join(
            Path(path).read_text(encoding="utf-8")
            for path in ["README.md", "docs/provider-verification.md"]
            if Path(path).exists()
        )

        for provider_id in verified:
            self.assertIn(provider_id, docs)
        for provider_id in unverified:
            self.assertNotIn(f"`{provider_id}` | verified |", docs)


if __name__ == "__main__":
    unittest.main()
