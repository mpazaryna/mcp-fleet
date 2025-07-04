"""
core - Core MCP server functionality

Provides standardized MCP server creation, transport utilities,
and common patterns for building MCP servers.
"""

from .server import create_mcp_server, MCPServerFactory
from .transport import StdioTransport, SocketTransport
from .types import (
    MCPServerConfig,
    MCPTool,
    MCPToolHandler,
    MCPToolHandlers,
    MCPServerOptions,
    MCPTransport,
    MCPLogger,
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