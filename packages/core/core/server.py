"""
MCP server creation and factory functionality
"""

import logging
from typing import Any

from mcp.server import Server
from mcp.types import Tool

from .types import MCPLogger, MCPServerOptions

logger = logging.getLogger(__name__)


def create_mcp_server(options: MCPServerOptions) -> Server[Any]:
    """
    Creates a standardized MCP server with error handling and logging
    """
    server_info = options.server_info
    tools = options.tools
    handlers = options.handlers

    # Create the MCP server
    server: Server[Any] = Server(server_info.name)

    # Register the tool call handler
    @server.call_tool()  # type: ignore
    async def handle_tool_call(name: str, arguments: dict[str, Any]) -> Any:
        if name in handlers:
            handler = handlers[name]
            try:
                result = await handler(arguments)
                return result
            except Exception as error:
                error_message = str(error)
                logger.error(f"[MCP Server] Error in {name}: {error_message}")
                raise error
        else:
            raise ValueError(f"Unknown tool: {name}")

    # Register all tools
    @server.list_tools()  # type: ignore
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.input_schema,
            )
            for tool in tools
        ]

    return server


class MCPServerFactory:
    """
    Standard MCP server factory with common setup
    """

    def __init__(self, logger: MCPLogger | None = None):
        self.logger = logger

    def create(self, options: MCPServerOptions) -> Server[Any]:
        """Create an MCP server with the given options"""
        if self.logger:
            server_info = options.server_info
            self.logger.info(
                f"Creating MCP server: {server_info.name} v{server_info.version}"
            )

        return create_mcp_server(options)
