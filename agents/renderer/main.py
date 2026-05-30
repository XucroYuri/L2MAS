"""
Renderer Agent - Composes all shots into final video
"""

import asyncio
import logging
import os
from typing import List, Dict, Any
from uuid import uuid4

from pydantic import BaseModel
from a2a import agent_task, AgentCapability

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)

class ShotResult(BaseModel):
    """Result from a single shot processing"""
    shot_id: str
    video_path: str
    audio_path: str
    duration: float

class RenderInput(BaseModel):
    """Input for rendering"""
    shots: List[ShotResult]
    resolution: str = "1920x1080"
    fps: int = 60
    add_transitions: bool = True

class RenderOutput(BaseModel):
    """Output from rendering"""
    final_video_path: str
    total_duration: float
    generation_time: float

class RendererAgent(BaseAgent):
    agent_id = "renderer@tools.example.com"
    name = "渲染合成Agent"
    description = "将所有动画片段合成最终视频，添加转场和特效"
    
    capabilities = [
        AgentCapability(
            name="compose_video",
            description="将多个镜头合成最终视频",
            input_schema=RenderInput,
            output_schema=RenderOutput
        )
    ]
    
    @agent_task
    async def compose_video(self, input: RenderInput) -> RenderOutput:
        """
        Compose all shots into the final video.
        Uses FFmpeg to concatenate videos and add transitions.
        """
        logger.info(f"Composing final video from {len(input.shots)} shots")
        
        start_time = asyncio.get_event_loop().time()
        
        # Get FFmpeg MCP tool
        ffmpeg_tool = self.get_mcp_tool("concat_videos")
        
        # Collect video paths
        video_paths = [shot.video_path for shot in input.shots]
        
        # Call FFmpeg concat tool
        result = await ffmpeg_tool.ainvoke({
            "video_paths": video_paths,
            "output_path": "/tmp/temp.mp4",
            "resolution": input.resolution,
            "fps": input.fps,
            "add_transitions": input.add_transitions,
            "transition_duration": 0.3
        })
        
        # Add background music and effects
        final_result = await self._add_post_processing(
            result["output_path"],
            input.shots
        )
        
        generation_time = asyncio.get_event_loop().time() - start_time
        
        total_duration = sum(shot.duration for shot in input.shots)
        
        logger.info(f"Final video composed in {generation_time:.1f}s")
        
        video_id = str(uuid4())[:8]
        final_path = f"/output/final_{video_id}.mp4"
        
        # Move to final location
        os.rename(final_result["output_path"], final_path)
        
        return RenderOutput(
            final_video_path=final_path,
            total_duration=total_duration,
            generation_time=generation_time
        )
    
    async def _add_post_processing(self, video_path: str, shots: List[ShotResult]) -> Dict[str, Any]:
        """Add post-processing effects"""
        # Get video processing MCP tool
        process_tool = self.get_mcp_tool("process_video")
        
        # Mix audio from all shots
        audio_paths = [shot.audio_path for shot in shots if shot.audio_path]
        
        return await process_tool.ainvoke({
            "video_path": video_path,
            "audio_paths": audio_paths,
            "normalize_audio": True,
            "add_fade": True,
            "fade_duration": 0.5
        })

async def main():
    """Main entry point for the agent"""
    agent = RendererAgent()
    await agent.initialize()
    
    # Register with A2A registry
    await agent.register()
    
    logger.info("Renderer Agent started and registered")
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
