"""
Modeling Agent - Generates Live2D models from text or images using Textoon
"""

import asyncio
import logging
import os
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from a2a import agent_task, AgentCapability

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)

class ModelingInput(BaseModel):
    """Input for modeling agent"""
    text_description: str
    image_path: Optional[str] = None
    style: str = "anime"
    quality: str = "high"
    auto_rig: bool = True
    generate_physics: bool = True

class ModelingOutput(BaseModel):
    """Output from modeling agent"""
    model_path: str
    parameters: dict
    preview_url: str
    generation_time: float

class ModelingAgent(BaseAgent):
    agent_id = "modeling@tools.example.com"
    name = "Live2D建模专家"
    description = "从文本或图片自动生成高质量Live2D模型，使用Textoon技术"
    
    capabilities = [
        AgentCapability(
            name="text_to_live2d",
            description="从文本描述生成完整的Live2D角色模型",
            input_schema=ModelingInput,
            output_schema=ModelingOutput
        ),
        AgentCapability(
            name="image_to_live2d",
            description="从单张图片生成完整的Live2D角色模型",
            input_schema=ModelingInput,
            output_schema=ModelingOutput
        )
    ]
    
    @agent_task
    async def text_to_live2d(self, input: ModelingInput) -> ModelingOutput:
        """
        Generate a complete Live2D model from text description using Textoon.
        """
        logger.info(f"Generating Live2D model from text: {input.text_description}")
        
        start_time = asyncio.get_event_loop().time()
        
        # Get Textoon MCP tool
        textoon_tool = self.get_mcp_tool("textoon_generate")
        
        # Call Textoon service through MCP
        result = await textoon_tool.ainvoke({
            "prompt": input.text_description,
            "style": input.style,
            "quality": input.quality,
            "auto_rig": input.auto_rig,
            "generate_physics": input.generate_physics,
            "output_format": "cubism5"
        })
        
        generation_time = asyncio.get_event_loop().time() - start_time
        
        logger.info(f"Live2D model generated in {generation_time:.1f}s")
        
        model_id = str(uuid4())[:8]
        model_path = f"/models/{model_id}/model.model3.json"
        
        return ModelingOutput(
            model_path=model_path,
            parameters=result.get("parameters", {}),
            preview_url=result.get("preview_url", ""),
            generation_time=generation_time
        )
    
    @agent_task
    async def image_to_live2d(self, input: ModelingInput) -> ModelingOutput:
        """
        Generate a complete Live2D model from an image.
        """
        logger.info(f"Generating Live2D model from image: {input.image_path}")
        
        start_time = asyncio.get_event_loop().time()
        
        # Get image to Live2D MCP tool
        image_to_live2d_tool = self.get_mcp_tool("image_to_live2d")
        
        # Call the tool
        result = await image_to_live2d_tool.ainvoke({
            "image_path": input.image_path,
            "style": input.style,
            "quality": input.quality,
            "auto_rig": input.auto_rig,
            "generate_physics": input.generate_physics,
            "output_format": "cubism5"
        })
        
        generation_time = asyncio.get_event_loop().time() - start_time
        
        logger.info(f"Live2D model from image generated in {generation_time:.1f}s")
        
        model_id = str(uuid4())[:8]
        model_path = f"/models/{model_id}/model.model3.json"
        
        return ModelingOutput(
            model_path=model_path,
            parameters=result.get("parameters", {}),
            preview_url=result.get("preview_url", ""),
            generation_time=generation_time
        )

async def main():
    """Main entry point for the agent"""
    agent = ModelingAgent()
    await agent.initialize()
    
    # Register with A2A registry
    await agent.register()
    
    logger.info("Modeling Agent started and registered")
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
