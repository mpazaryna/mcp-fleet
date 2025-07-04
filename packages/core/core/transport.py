"""
Transport implementations for MCP servers
"""

import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

logger = logging.getLogger(__name__)


class StdioTransport:
    """
    Standard stdio transport for MCP servers
    """

    def __init__(self) -> None:
        self.server: Server[Any] | None = None

    async def connect(self, server: Server[Any] | None = None) -> None:
        """Connect the transport with an MCP server"""
        if server:
            self.server = server
            # Run the stdio server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )

    async def close(self) -> None:
        """Close the transport"""
        if self.server:
            logger.info("Stdio transport closing")


class SocketTransport:
    """
    Socket transport for MCP servers (for testing/development)
    """

    def __init__(self, port: int) -> None:
        self.port = port
        self.server: Server[Any] | None = None

    async def connect(self, server: Server[Any] | None = None) -> None:
        """Connect the transport on the specified port"""
        if server:
            self.server = server
        logger.info(f"Socket transport would connect on port {self.port}")

    async def close(self) -> None:
        """Close the socket transport"""
        logger.info("Socket transport closing")
