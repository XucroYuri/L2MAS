"""
Base Agent class for A2A protocol
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from a2a import Agent, agent_task, AgentCapability
from pydantic import BaseModel, Field
from mcp import MCPClient

logger = logging.getLogger(__name__)

class BaseAgent(Agent):
    """
    Base class for all agents in the system.
    Implements common functionality using A2A protocol.
    """
    
    def __init__(self):
        super().__init__()
        self.mcp_client: Optional[MCPClient] = None
        self.agent_id: str = ""
        self.name: str = ""
        self.description: str = ""
        self.capabilities: List[AgentCapability] = []
        
    async def initialize(self):
        """Initialize the agent, connect to MCP servers"""
        logger.info(f"Initializing agent: {self.name}")
        
        # Connect to MCP gateway
        self.mcp_client = MCPClient.from_config_file(
            "/app/config/mcp_config.json"
        )
        await self.mcp_client.initialize()
        
        logger.info(f"Agent {self.name} initialized successfully")
    
    async def shutdown(self):
        """Cleanup resources"""
        if self.mcp_client:
            await self.mcp_client.close()
        logger.info(f"Agent {self.name} shutdown complete")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "agent_id": self.agent_id,
            "name": self.name,
            "mcp_connected": self.mcp_client is not None,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def get_mcp_tool(self, tool_name: str):
        """Get MCP tool by name"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        
        tools = self.mcp_client.list_tools()
        for tool in tools:
            if tool.name == tool_name:
                return tool
        
        raise ValueError(f"Tool {tool_name} not found")
    
    async def wait_for_agent(self, agent_id: str, timeout: int = 30):
        """Wait for another agent to become available"""
        from a2a import AgentClient
        
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            try:
                agent = await AgentClient.discover(
                    agent_id,
                    registry_url=os.getenv("A2A_REGISTRY_URL", "http://a2a-registry:50051")
                )
                return agent
            except Exception:
                await asyncio.sleep(1)
        
        raise TimeoutError(f"Agent {agent_id} not available after {timeout}s")
