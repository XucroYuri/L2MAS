"""
Voice Agent - Generates voice-over using TTS
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import uuid4

from a2a import agent_task, AgentCapability

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)

@dataclass
class VoiceInput:
    """Input for voice generation"""
    text: str
    emotion: str = "neutral"
    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: float = 1.0
    pitch: float = 0.0

@dataclass
class VoiceOutput:
    """Output from voice generation"""
    audio_path: str
    duration: float
    phonemes: List[Dict[str, Any]]
    generation_time: float

class VoiceAgent(BaseAgent):
    agent_id = "voice@tools.example.com"
    name = "Voice Agent"
    description = "Generates dialogue audio and speech timing artifacts"
    
    capabilities = [
        AgentCapability(
            name="voice.generate",
            description="为台词生成配音，支持情感调整",
            input_schema=VoiceInput,
            output_schema=VoiceOutput
        )
    ]
    
    @agent_task
    async def generate_voice(self, input: VoiceInput) -> VoiceOutput:
        """
        Generate voice-over for the dialogue.
        Uses emotion-aware TTS with phoneme extraction.
        """
        logger.info(f"Generating voice for text: {input.text}, emotion: {input.emotion}")
        
        start_time = asyncio.get_event_loop().time()
        
        # Adjust voice parameters based on emotion
        voice_params = self._adjust_for_emotion(input, input.emotion)
        
        # Get TTS MCP tool
        tts_tool = self.get_mcp_tool("elevenlabs_tts")
        
        # Call TTS service
        result = await tts_tool.ainvoke({
            "text": input.text,
            "voice_id": voice_params["voice"],
            "model_id": "eleven_multilingual_v3",
            "rate": voice_params["rate"],
            "pitch": voice_params["pitch"],
            "extract_phonemes": True
        })
        
        generation_time = asyncio.get_event_loop().time() - start_time
        
        logger.info(f"Voice generated in {generation_time:.1f}s, duration: {result['duration']:.1f}s")
        
        audio_id = str(uuid4())[:8]
        audio_path = f"/output/audio/{audio_id}.mp3"
        
        return VoiceOutput(
            audio_path=audio_path,
            duration=result["duration"],
            phonemes=result.get("phonemes", []),
            generation_time=generation_time
        )
    
    def _adjust_for_emotion(self, input: VoiceInput, emotion: str) -> Dict[str, Any]:
        """Adjust TTS parameters based on emotion"""
        adjustments = {
            "happy": {"rate": 1.1, "pitch": 0.1},
            "excited": {"rate": 1.2, "pitch": 0.2},
            "thinking": {"rate": 0.9, "pitch": -0.05},
            "sad": {"rate": 0.85, "pitch": -0.1},
            "surprised": {"rate": 1.15, "pitch": 0.15},
            "angry": {"rate": 1.1, "pitch": 0.1},
            "neutral": {"rate": 1.0, "pitch": 0.0},
        }
        
        adj = adjustments.get(emotion.lower(), adjustments["neutral"])
        
        return {
            "voice": input.voice,
            "rate": input.rate * adj["rate"],
            "pitch": input.pitch + adj["pitch"],
        }

async def main():
    """Main entry point for the agent"""
    agent = VoiceAgent()
    await agent.initialize()
    
    # Register with A2A registry
    await agent.register()
    
    logger.info("Voice Agent started and registered")
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
