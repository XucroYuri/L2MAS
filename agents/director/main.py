"""
Director Agent - The overall orchestrator of the animation production
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import List, Dict, Any
from uuid import uuid4

from a2a import agent_task, AgentCapability

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)

@dataclass
class Shot:
    """Single shot in storyboard"""
    id: str
    duration: float
    dialogue: str
    action: str
    emotion: str
    camera_angle: str = "front"

@dataclass
class Storyboard:
    """Complete storyboard"""
    shots: List[Shot]
    total_duration: float
    title: str
    style: str

@dataclass
class DirectorInput:
    """Input for director agent"""
    script: str
    character_info: Dict[str, Any]
    style: str = "anime"

@dataclass
class DirectorOutput:
    """Output from director agent"""
    storyboard: Storyboard
    task_id: str
    estimated_time: float

class DirectorAgent(BaseAgent):
    agent_id = "director@studio.example.com"
    name = "Director Agent"
    description = "Plans storyboards and orchestrates the animation workflow"
    
    capabilities = [
        AgentCapability(
            name="script.plan",
            description="从剧本和角色信息创建分镜脚本",
            input_schema=DirectorInput,
            output_schema=DirectorOutput
        )
    ]
    
    def __init__(self):
        super().__init__()
    
    @agent_task
    async def create_storyboard(self, input: DirectorInput) -> DirectorOutput:
        """
        Create a complete storyboard from the script.
        Breaks down the script into individual shots with timing and emotions.
        """
        logger.info(f"Creating storyboard for script: {input.script[:100]}...")
        
        return self._fallback_storyboard(input)
    
    def _fallback_storyboard(self, input: DirectorInput) -> DirectorOutput:
        """Fallback simple storyboard creation"""
        lines = input.script.strip().split("\n")
        shots = []
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            if "镜头" in line:
                # Extract from line like "镜头1：角色说：xxx"
                parts = line.split("：", 2)
                dialogue = parts[-1] if len(parts) > 1 else line
                shots.append(Shot(
                    id=f"shot_{i}",
                    duration=3.0,
                    dialogue=dialogue,
                    action="wave" if i == 0 else "talk",
                    emotion="happy" if i == 0 else "neutral",
                ))
        
        if not shots:
            # Single shot for entire script
            shots.append(Shot(
                id="shot_0",
                duration=5.0,
                dialogue=input.script,
                action="talk",
                emotion="neutral",
            ))
        
        total_duration = sum(s.duration for s in shots)
        
        return DirectorOutput(
            storyboard=Storyboard(
                shots=shots,
                total_duration=total_duration,
                title="Animation",
                style=input.style
            ),
            task_id=str(uuid4()),
            estimated_time=60.0
        )

async def main():
    """Main entry point for the agent"""
    agent = DirectorAgent()
    await agent.initialize()
    
    # Register with A2A registry
    await agent.register()
    
    logger.info("Director Agent started and registered")
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
