"""
Animation Agent - Generates animation clips for each shot
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4

from pydantic import BaseModel
from a2a import agent_task, AgentCapability

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)

class AnimationShotInput(BaseModel):
    """Input for a single animation shot"""
    model_path: str
    duration: float
    action_description: str
    emotion: str
    audio_path: Optional[str] = None
    auto_lip_sync: bool = True

class AnimationShotOutput(BaseModel):
    """Output for a single animation shot"""
    video_path: str
    parameter_sequence: List[Dict[str, float]]
    generation_time: float

class AnimationAgent(BaseAgent):
    agent_id = "animator@tools.example.com"
    name = "动画导演Agent"
    description = "根据分镜生成动画片段，自动生成动作序列和表情变化"
    
    capabilities = [
        AgentCapability(
            name="generate_animation",
            description="为单个镜头生成动画片段",
            input_schema=AnimationShotInput,
            output_schema=AnimationShotOutput
        )
    ]
    
    @agent_task
    async def generate_animation(self, input: AnimationShotInput) -> AnimationShotOutput:
        """
        Generate animation for a single shot.
        Takes the Live2D model and generates the animation based on action and emotion.
        """
        logger.info(f"Generating animation for action: {input.action_description}, emotion: {input.emotion}")
        
        start_time = asyncio.get_event_loop().time()
        
        # Get Live2D animation MCP tool
        animate_tool = self.get_mcp_tool("animate_live2d_model")
        
        # Map emotion to Live2D parameters
        emotion_params = self._get_emotion_parameters(input.emotion)
        
        # Get action parameters from action library
        action_params = await self._get_action_parameters(input.action_description)
        
        # Call the animation tool
        result = await animate_tool.ainvoke({
            "model_path": input.model_path,
            "duration": input.duration,
            "base_parameters": emotion_params,
            "action_parameters": action_params,
            "audio_path": input.audio_path,
            "auto_lip_sync": input.auto_lip_sync,
            "fps": 60,
            "resolution": "1920x1080"
        })
        
        generation_time = asyncio.get_event_loop().time() - start_time
        
        logger.info(f"Animation generated in {generation_time:.1f}s")
        
        shot_id = str(uuid4())[:8]
        video_path = f"/output/shots/{shot_id}.mp4"
        
        return AnimationShotOutput(
            video_path=video_path,
            parameter_sequence=result.get("parameter_sequence", []),
            generation_time=generation_time
        )
    
    def _get_emotion_parameters(self, emotion: str) -> Dict[str, float]:
        """Map emotion name to Live2D parameter values"""
        emotions = {
            "happy": {
                "ParamEyeLOpen": 1.0,
                "ParamEyeROpen": 1.0,
                "ParamBrowLY": -0.3,
                "ParamBrowRY": -0.3,
                "ParamMouthForm": 0.5,
            },
            "excited": {
                "ParamEyeLOpen": 1.0,
                "ParamEyeROpen": 1.0,
                "ParamBrowLY": -0.5,
                "ParamBrowRY": -0.5,
                "ParamMouthForm": 0.8,
            },
            "thinking": {
                "ParamEyeLOpen": 0.7,
                "ParamEyeROpen": 0.7,
                "ParamBrowLY": 0.3,
                "ParamBrowRY": 0.3,
                "ParamAngleY": 0.2,
            },
            "sad": {
                "ParamEyeLOpen": 0.6,
                "ParamEyeROpen": 0.6,
                "ParamBrowLY": 0.4,
                "ParamBrowRY": 0.4,
                "ParamMouthForm": -0.3,
            },
            "surprised": {
                "ParamEyeLOpen": 1.0,
                "ParamEyeROpen": 1.0,
                "ParamBrowLY": -0.8,
                "ParamBrowRY": -0.8,
                "ParamMouthOpenY": 0.8,
            },
            "neutral": {
                "ParamEyeLOpen": 0.8,
                "ParamEyeROpen": 0.8,
                "ParamBrowLY": 0.0,
                "ParamBrowRY": 0.0,
                "ParamMouthForm": 0.0,
            }
        }
        return emotions.get(emotion.lower(), emotions["neutral"])
    
    async def _get_action_parameters(self, action: str) -> Dict[str, Any]:
        """Get action parameters from action library"""
        # Search action library MCP tool
        action_tool = self.get_mcp_tool("search_action_library")
        
        result = await action_tool.ainvoke({
            "query": action,
            "limit": 1,
            "threshold": 0.7
        })
        
        if result["matches"]:
            return result["matches"][0]["parameters"]
        
        # Fallback to default talking animation
        return {
            "ParamAngleX": {"keyframes": [0, 0.5, 1.0], "values": [-0.1, 0.1, -0.1]},
            "ParamBodyAngleX": {"keyframes": [0, 0.5, 1.0], "values": [-0.05, 0.05, -0.05]},
        }

async def main():
    """Main entry point for the agent"""
    agent = AnimationAgent()
    await agent.initialize()
    
    # Register with A2A registry
    await agent.register()
    
    logger.info("Animation Agent started and registered")
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
