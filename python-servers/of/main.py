#!/usr/bin/env python3
"""
OF (Orchestration Framework) MCP Server

4-phase systematic methodology with template-driven AI guidance.
Provides project management through exploration, specification, execution, and feedback phases.
"""
import asyncio
import logging
import sys
from pathlib import Path

from mcp_core import create_mcp_server, StdioTransport, MCPServerConfig, MCPServerOptions
from src.tools.of_tools import of_tools, of_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)


async def main():
    """Main server function"""
    logger.info("🔮 Starting OF (Orchestration Framework) MCP Server...")
    
    try:
        # Server configuration
        server_config = MCPServerConfig(
            name="of",
            version="0.1.0",
            description="4-phase systematic methodology with template-driven AI guidance"
        )
        
        # Create server options with OF tools
        server_options = MCPServerOptions(
            server_info=server_config,
            tools=of_tools,
            handlers=of_handlers
        )
        
        # Create the MCP server
        server = create_mcp_server(server_options)
        
        # Connect to stdio transport
        transport = StdioTransport()
        await transport.connect(server)
        
        logger.info("🔮 OF MCP Server connected and ready")
        logger.info("📋 Template system with external markdown files loaded")
        logger.info("🎯 4-phase methodology: Exploration → Specification → Execution → Feedback")
        
        # Keep the process running
        while True:
            await asyncio.sleep(1)
            
    except Exception as error:
        logger.error(f"❌ Failed to start OF MCP Server: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())