#!/usr/bin/env python3
"""
YogaTeach MCP Server

A content generation system for yoga setlists and dharma talks using 
template-based interactive prompting and file generation.
"""
import asyncio
import logging
import sys

from core import MCPServerConfig, MCPServerOptions, StdioTransport, create_mcp_server
from src.yoga_tools import yoga_handlers, yoga_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main server function"""
    logger.info("🧘 Starting YogaTeach MCP Server...")

    try:
        # Server configuration
        server_config = MCPServerConfig(
            name="yogateach",
            version="0.1.0",
            description="Yoga instruction and dharma talk generation through templated content creation",
        )

        # Create server options
        server_options = MCPServerOptions(
            server_info=server_config, tools=yoga_tools, handlers=yoga_handlers
        )

        # Create the MCP server
        server = create_mcp_server(server_options)

        # Connect to stdio transport
        transport = StdioTransport()
        await transport.connect(server)

        logger.info("🧘 YogaTeach MCP Server connected and ready")

        # Keep the process running
        while True:
            await asyncio.sleep(1)

    except Exception as error:
        logger.error(f"❌ Failed to start YogaTeach MCP Server: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())