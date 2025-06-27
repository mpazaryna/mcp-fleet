#!/usr/bin/env python3
"""
OF (Orchestration Framework) MCP Server

4-phase systematic methodology with template-driven AI guidance.
Provides project management through exploration, specification, execution, and feedback phases.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to the path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool
from src.tools.of_tools import of_tools, of_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)


async def main():
    """Main server function"""
    logger.info("🔮 Starting OF (Orchestration Framework) MCP Server...")
    
    # Create the MCP server
    server = Server("of")
    
    # Register tools
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools"""
        return [
            Tool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.input_schema
            )
            for tool in of_tools
        ]
    
    # Register tool call handler
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> dict:
        """Handle tool calls"""
        if name not in of_handlers:
            raise ValueError(f"Unknown tool: {name}")
        
        handler = of_handlers[name]
        try:
            result = await handler(arguments)
            return result
        except Exception as error:
            logger.error(f"Error in {name}: {error}")
            raise error
    
    logger.info("🔮 OF MCP Server connected and ready")
    logger.info("📋 Template system with external markdown files loaded")
    logger.info("🎯 4-phase methodology: Exploration → Specification → Execution → Feedback")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())