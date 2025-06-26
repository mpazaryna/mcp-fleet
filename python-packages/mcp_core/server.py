"""
MCP server creation and factory functionality
"""
import logging
from typing import Any, Dict, Optional
from mcp.server import Server
from mcp.types import Tool

from .types import MCPServerOptions, MCPLogger


logger = logging.getLogger(__name__)


def create_mcp_server(options: MCPServerOptions) -> Server:
    """
    Creates a standardized MCP server with error handling and logging
    """
    server_info = options.server_info
    tools = options.tools
    handlers = options.handlers
    
    # Create the MCP server
    server = Server(server_info.name)
    
    # Convert tools to MCP Tool format and register handlers
    for tool in tools:
        mcp_tool = Tool(
            name=tool.name,
            description=tool.description,
            inputSchema=tool.input_schema
        )
        
        # Get the handler for this tool
        if tool.name in handlers:
            handler = handlers[tool.name]
            
            # Wrap handler with error handling
            async def wrapped_handler(arguments: Dict[str, Any], 
                                     tool_name: str = tool.name,
                                     original_handler: Any = handler) -> Any:
                try:
                    result = await original_handler(arguments)
                    return result
                except Exception as error:
                    error_message = str(error)
                    logger.error(f"[MCP Server] Error in {tool_name}: {error_message}")
                    raise error
            
            # Register the tool and handler with the server
            @server.call_tool()
            async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
                if name == tool.name:
                    return await wrapped_handler(arguments)
    
    return server


class MCPServerFactory:
    """
    Standard MCP server factory with common setup
    """
    
    def __init__(self, logger: Optional[MCPLogger] = None):
        self.logger = logger
    
    def create(self, options: MCPServerOptions) -> Server:
        """Create an MCP server with the given options"""
        if self.logger:
            server_info = options.server_info
            self.logger.info(
                f"Creating MCP server: {server_info.name} v{server_info.version}"
            )
        
        return create_mcp_server(options)