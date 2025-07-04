#!/usr/bin/env python3
"""
Tides MCP Server

A rhythmic workflow management system inspired by natural tidal patterns.
Helps create sustainable productivity cycles through tidal flows.
"""
import asyncio
import logging
import sys

from core import MCPServerConfig, MCPServerOptions, StdioTransport, create_mcp_server
from src.tide_tools import tide_handlers, tide_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main server function"""
    logger.info("🌊 Starting Tides MCP Server...")

    try:
        # Server configuration
        server_config = MCPServerConfig(
            name="tides",
            version="0.1.0",
            description="Rhythmic workflow management through tidal patterns",
        )

        # Create server options
        server_options = MCPServerOptions(
            server_info=server_config, tools=tide_tools, handlers=tide_handlers
        )

        # Create the MCP server
        server = create_mcp_server(server_options)

        # Connect to stdio transport
        transport = StdioTransport()
        await transport.connect(server)

        logger.info("🌊 Tides MCP Server connected and ready")

        # Keep the process running
        while True:
            await asyncio.sleep(1)

    except Exception as error:
        logger.error(f"❌ Failed to start Tides MCP Server: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
