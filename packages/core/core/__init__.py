"""
core - Core MCP server functionality

Provides standardized MCP server creation, transport utilities,
and common patterns for building MCP servers.
"""

from .server import MCPServerFactory, create_mcp_server
from .transport import SocketTransport, StdioTransport
from .types import (
    MCPLogger,
    MCPServerConfig,
    MCPServerOptions,
    MCPTool,
    MCPToolHandler,
    MCPToolHandlers,
    MCPTransport,
)

__all__ = [
    "create_mcp_server",
    "MCPServerFactory",
    "StdioTransport",
    "SocketTransport",
    "MCPServerConfig",
    "MCPTool",
    "MCPToolHandler",
    "MCPToolHandlers",
    "MCPServerOptions",
    "MCPTransport",
    "MCPLogger",
]
