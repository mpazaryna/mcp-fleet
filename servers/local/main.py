#!/usr/bin/env python3
"""
Local MCP Server

Native macOS system integrations for Apple Notes, Reminders, Calendar, and file operations.
Designed to run natively (not in Docker) for full system access via AppleScript.
"""
import asyncio
import logging
import sys

from mcp_core import create_mcp_server, StdioTransport, MCPServerConfig, MCPServerOptions
from src.tools.apple_notes_tools import notes_tools, notes_handlers


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)


async def main():
    """Main server function"""
    logger.info("🏠 Starting Local MCP Server...")
    
    try:
        # Server configuration
        server_config = MCPServerConfig(
            name="local",
            version="0.1.0",
            description="Native macOS system integrations for Apple Notes, Reminders, Calendar, and file operations"
        )
        
        # Combine all tools and handlers (starting with Apple Notes)
        all_tools = notes_tools
        all_handlers = notes_handlers
        
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
        
        logger.info("🏠 Local MCP Server connected and ready")
        logger.info(f"   📝 Apple Notes tools: {len(notes_tools)} tools available")
        
        # Keep the process running
        while True:
            await asyncio.sleep(1)
            
    except Exception as error:
        logger.error(f"❌ Failed to start Local MCP Server: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())