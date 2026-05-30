#!/usr/bin/env python3
"""
End-to-end test script for the Live2D Multi-Agent Animation System
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from live2d_ai import AnimationGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    print("🎬 Live2D Multi-Agent Animation System - End-to-End Test")
    print("=" * 60)
    
    # Initialize the generator
    generator = AnimationGenerator(
        api_endpoint="http://localhost:8080",
        api_key="your_api_key"  # Replace with your actual API key
    )
    
    print("✅ Generator initialized")
    
    # Check service health
    print("\n🔍 Checking service health...")
    health = await generator.health_check()
    
    if health["status"] == "healthy":
        print("✅ All services healthy!")
        print(f"   - Registered agents: {len(health['agents'])}")
        for agent in health['agents']:
            print(f"     - {agent['name']}: {agent['status']}")
    else:
        print(f"❌ Services unhealthy: {health}")
        return
    
    # List available agents
    print("\n🤖 Available Agents:")
    agents = await generator.list_agents()
    for agent in agents:
        print(f"   - {agent['name']}: {agent['description']}")
    
    # Run a test generation
    print("\n🎨 Running test animation generation...")
    
    script = """
    镜头1：角色微笑着向观众挥手，说："大家好，欢迎来到我的频道！"
    镜头2：角色兴奋地说："今天我要给大家介绍一个非常有趣的技术！"
    镜头3：角色指着旁边，说："这就是AI驱动的Live2D动画生成系统！"
    """
    
    character = "一个可爱的猫娘，蓝发，猫耳，穿着JK制服"
    
    print(f"📝 Script: {script.strip()}")
    print(f"👤 Character: {character}")
    
    # Start generation
    print("\n⚡ Starting generation...")
    
    result = None
    async for progress in generator.generate_stream(
        script=script,
        character_description=character,
        resolution="1920x1080",
        fps=60
    ):
        print(f"   Progress: {progress['stage']} - {progress['percent']}%")
        if progress["stage"] == "complete":
            result = progress["result"]
    
    if result is None:
        raise RuntimeError("Generation stream finished without a final result")
    
    print("\n✅ Generation complete!")
    print(f"📁 Video file: {result.video_path}")
    print(f"📦 Live2D model: {result.model_path}")
    print(f"⏱️  Total time: {result.total_time:.1f} seconds")
    
    print("\n🎉 Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
