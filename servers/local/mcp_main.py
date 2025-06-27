#!/usr/bin/env python3
"""
Local MCP Server - Proper MCP Implementation

Native macOS system integrations for Apple Notes, Reminders, Calendar, and file operations.
Uses the standard MCP protocol implementation for Claude Desktop compatibility.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import MCP essentials
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Import our tools
from tools.apple_notes_tools import notes_tools, notes_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)


async def main():
    """Main server function using proper MCP protocol"""
    logger.info("🏠 Starting Local MCP Server...")
    logger.info(f"   📝 Apple Notes tools: {len(notes_tools)} tools available")
    
    # Create the MCP server
    server = Server("local")
    
    # Register tool call handler
    @server.call_tool()
    async def handle_tool_call(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls through MCP protocol"""
        logger.info(f"Tool call: {name} with args: {arguments}")
        
        if name not in notes_handlers:
            raise ValueError(f"Unknown tool: {name}")
        
        try:
            handler = notes_handlers[name]
            result = await handler(arguments)
            
            # Return result as TextContent
            import json
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error in tool {name}: {e}")
            raise
    
    # Register tools list handler
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools"""
        logger.info("Listing available tools")
        return [
            Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool["input_schema"]
            )
            for tool in notes_tools
        ]
    
    logger.info("🏠 Local MCP Server ready")
    
    # Run the server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())