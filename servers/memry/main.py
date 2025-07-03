#!/usr/bin/env python3
"""
MCP-Memry Server

A Python-based memory storage system for storing and retrieving information
from Claude interactions using markdown files with YAML frontmatter.
"""
import asyncio
import logging
import sys

from mcp_core import (
    MCPServerConfig,
    MCPServerOptions,
    StdioTransport,
    create_mcp_server,
)
from src.tools.memory_tools import memory_handlers, memory_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

logger = logging.getLogger(__name__)


async def main():
    """Main server function"""
    logger.info("🧠 Starting MCP-Memry Server...")

    try:
        # Server configuration
        server_config = MCPServerConfig(
            name="memry",
            version="0.1.0",
            description="Memory storage system for Claude interactions",
        )

        # Create server options
        server_options = MCPServerOptions(
            server_info=server_config, tools=memory_tools, handlers=memory_handlers
        )

        # Create the MCP server
        server = create_mcp_server(server_options)

        # Connect to stdio transport
        transport = StdioTransport()
        await transport.connect(server)

        logger.info("🧠 MCP-Memry Server connected and ready")

        # Keep the process running
        while True:
            await asyncio.sleep(1)

    except Exception as error:
        logger.error(f"❌ Failed to start MCP-Memry Server: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
