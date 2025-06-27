#!/usr/bin/env python3
"""
Compass MCP Server

Systematic project methodology through exploration-to-execution phases.
Enforces depth and prevents surface-level AI responses.
"""
import asyncio
import logging
import sys

from mcp_core import create_mcp_server, StdioTransport, MCPServerConfig, MCPServerOptions
from src.tools.project_tools import project_tools, project_handlers
from src.tools.exploration_tools import exploration_tools, exploration_handlers


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)


async def main():
    """Main server function"""
    logger.info("🧭 Starting Compass MCP Server...")
    
    try:
        # Server configuration
        server_config = MCPServerConfig(
            name="compass",
            version="0.1.0",
            description="Systematic project methodology through exploration-to-execution phases"
        )
        
        # Combine all tools and handlers
        all_tools = project_tools + exploration_tools
        all_handlers = {**project_handlers, **exploration_handlers}
        
        # Create server options
        server_options = MCPServerOptions(
            server_info=server_config,
            tools=all_tools,
            handlers=all_handlers
        )
        
        # Create the MCP server
        server = create_mcp_server(server_options)
        
        # Connect to stdio transport
        transport = StdioTransport()
        await transport.connect(server)
        
        logger.info("🧭 Compass MCP Server connected and ready")
        
        # Keep the process running
        while True:
            await asyncio.sleep(1)
            
    except Exception as error:
        logger.error(f"❌ Failed to start Compass MCP Server: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())