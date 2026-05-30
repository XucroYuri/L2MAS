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


if __name__ == "__main__":
    unittest.main()
