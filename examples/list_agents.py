#!/usr/bin/env python3
"""
List all registered agents in the A2A registry
"""

import asyncio
from a2a import AgentClient

async def main():
    # Connect to A2A registry
    registry_url = "http://localhost:50051"
    
    print("🔍 Discovering registered agents...")
    print()
    
    # List all agents
    agents = await AgentClient.list_agents(registry_url)
    
    print(f"📋 已注册的Agent ({len(agents)}):")
    print("-" * 60)
    
    for agent in agents:
        print(f"🔹 {agent.id}")
        print(f"   名称: {agent.name}")
        print(f"   描述: {agent.description}")
        print(f"   端点: {agent.endpoint}")
        print(f"   能力: {', '.join(agent.capabilities)}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
