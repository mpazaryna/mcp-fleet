"""
Type definitions for MCP Core functionality
"""

from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from pydantic import BaseModel


class MCPServerConfig(BaseModel):
    """Configuration for MCP server"""

    name: str
    version: str
    description: str | None = None


class MCPTool(BaseModel):
    """Definition of an MCP tool with input/output schemas"""

    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


# Type alias for tool handlers
MCPToolHandler = Callable[[dict[str, Any]], Any | Awaitable[Any]]

# Type alias for tool handler collections
MCPToolHandlers = dict[str, MCPToolHandler]


class MCPServerOptions(BaseModel):
    """Options for creating an MCP server"""

    server_info: MCPServerConfig
    tools: list[MCPTool]
    handlers: MCPToolHandlers

    class Config:
        arbitrary_types_allowed = True


class MCPTransport(Protocol):
    """Protocol for MCP transport implementations"""

    async def connect(self) -> None:
        """Connect the transport"""
        ...

    async def close(self) -> None:
        """Close the transport"""
        ...


class MCPLogger(Protocol):
    """Protocol for logging implementations"""

    def info(self, message: str, *args: Any) -> None:
        """Log info message"""
        ...

    def warn(self, message: str, *args: Any) -> None:
        """Log warning message"""
        ...

    def error(self, message: str, *args: Any) -> None:
        """Log error message"""
        ...

    def debug(self, message: str, *args: Any) -> None:
        """Log debug message"""
        ...
