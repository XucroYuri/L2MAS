import unittest

from agents.animation.main import AnimationAgent
from agents.director.main import DirectorAgent
from agents.modeling.main import ModelingAgent
from agents.renderer.main import RendererAgent
from agents.voice.main import VoiceAgent


class AgentCapabilityContractTest(unittest.TestCase):
    def test_base_agent_preserves_subclass_identity(self):
        agent = DirectorAgent()

        self.assertEqual(agent.agent_id, "director@studio.example.com")
        self.assertEqual(agent.name, "Director Agent")

    def test_agents_expose_standard_capability_names(self):
        agents = [
            (DirectorAgent(), {"script.plan"}),
            (ModelingAgent(), {"model.live2d.generate"}),
            (VoiceAgent(), {"voice.generate"}),
            (AnimationAgent(), {"motion.generate"}),
            (RendererAgent(), {"video.compose"}),
        ]

        for agent, expected in agents:
            with self.subTest(agent=agent.__class__.__name__):
                actual = {capability.name for capability in agent.capabilities}
                self.assertEqual(actual, expected)

    def test_agent_selects_provider_by_capability(self):
        agent = VoiceAgent()

        provider = agent.select_provider("voice.generate", prefer_mock=True)

        self.assertEqual(provider.provider_id, "mock-voice")


if __name__ == "__main__":
    unittest.main()
