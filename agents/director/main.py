"""
Director Agent - The overall orchestrator of the animation production
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from a2a import agent_task, AgentCapability
from langchain_openai import ChatOpenAI

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)

class Shot(BaseModel):
    """Single shot in storyboard"""
    id: str
    duration: float
    dialogue: str
    action: str
    emotion: str
    camera_angle: str = "front"

class Storyboard(BaseModel):
    """Complete storyboard"""
    shots: List[Shot]
    total_duration: float
    title: str
    style: str

class DirectorInput(BaseModel):
    """Input for director agent"""
    script: str
    character_info: Dict[str, Any]
    style: str = "anime"

class DirectorOutput(BaseModel):
    """Output from director agent"""
    storyboard: Storyboard
    task_id: str
    estimated_time: float

class DirectorAgent(BaseAgent):
    agent_id = "director@studio.example.com"
    name = "总导演Agent"
    description = "全局任务编排，将剧本分解为分镜，协调所有Agent工作"
    
    capabilities = [
        AgentCapability(
            name="create_storyboard",
            description="从剧本和角色信息创建分镜脚本",
            input_schema=DirectorInput,
            output_schema=DirectorOutput
        )
    ]
    
    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model="qwen3.7-max",
            base_url=os.getenv("QWEN_API_BASE", "https://api.qwen.ai/v1"),
            api_key=os.getenv("QWEN_API_KEY"),
            temperature=0.7,
            model_kwargs={"mcp_native": True}
        )
    
    @agent_task
    async def create_storyboard(self, input: DirectorInput) -> DirectorOutput:
        """
        Create a complete storyboard from the script.
        Breaks down the script into individual shots with timing and emotions.
        """
        logger.info(f"Creating storyboard for script: {input.script[:100]}...")
        
        # Use LLM to analyze script and create storyboard
        prompt = f"""
        你是一位专业的动画导演。请分析以下剧本，将其分解为详细的分镜脚本。
        
        剧本内容:
        {input.script}
        
        角色信息:
        {input.character_info}
        
        风格: {input.style}
        
        请按照以下规则分解:
        1. 每个镜头控制在2-5秒
        2. 为每个镜头指定情绪标签
        3. 为每个镜头指定动作描述
        4. 考虑镜头语言和节奏
        5. 输出JSON格式，包含shots数组
        
        每个shot需要包含:
        - id: 镜头ID
        - duration: 时长(秒)
        - dialogue: 台词
        - action: 动作描述
        - emotion: 情绪(happy/excited/thinking/sad/etc)
        - camera_angle: 镜头角度
        """
        
        response = await self.llm.ainvoke(prompt)
        
        # Parse response into structured storyboard
        # (In production, we use structured output parsing)
        import json
        try:
            # Extract JSON from response
            content = response.content
            # Find JSON block
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            data = json.loads(json_str)
            
            shots = [Shot(**shot) for shot in data["shots"]]
            total_duration = sum(shot.duration for shot in shots)
            
            storyboard = Storyboard(
                shots=shots,
                total_duration=total_duration,
                title=data.get("title", "Untitled"),
                style=input.style
            )
            
            logger.info(f"Storyboard created: {len(shots)} shots, {total_duration:.1f}s total")
            
            return DirectorOutput(
                storyboard=storyboard,
                task_id=str(uuid4()),
                estimated_time=total_duration * 3  # 3x for processing
            )
            
        except Exception as e:
            logger.error(f"Failed to parse storyboard: {e}")
            # Fallback to simple parsing
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
