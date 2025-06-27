#!/usr/bin/env python3
"""
Toolkit MCP Server

Essential file operations and utility tools for MCP servers.
"""
import asyncio
import logging
import sys

from mcp_core import create_mcp_server, StdioTransport, MCPServerConfig, MCPServerOptions, MCPTool
from src.tools.file_tools import file_tools, file_handlers
from src.tools.drafts_tools import draft_tools, draft_handlers


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)


async def main():
    """Main server function"""
    logger.info("🔧 Starting Toolkit MCP Server...")
    
    try:
        # Server configuration
        server_config = MCPServerConfig(
            name="toolkit",
            version="0.1.0",
            description="Essential file operations and utility tools for MCP servers, including Drafts app integration"
        )
        
        # Convert dictionary tools to MCPTool objects
        all_tool_dicts = file_tools + draft_tools
        logger.info(f"📊 Raw tool dicts: {len(all_tool_dicts)} tools")
        
        all_tools = [
            MCPTool(
                name=tool["name"],
                description=tool["description"],
                input_schema=tool["input_schema"],
                output_schema=tool["output_schema"]
            )
            for tool in all_tool_dicts
        ]
        logger.info(f"🔧 Converted to MCPTool objects: {len(all_tools)} tools")
        for tool in all_tools:
            logger.info(f"  - {tool.name}: {tool.description}")
        
        all_handlers = {**file_handlers, **draft_handlers}
        logger.info(f"🎯 Handlers registered: {list(all_handlers.keys())}")
        
        # Create server options
        server_options = MCPServerOptions(
            server_info=server_config,
            tools=all_tools,
            handlers=all_handlers
        )
        
        # Create the MCP server
        server = create_mcp_server(server_options)
        
        # Connect to stdio transport
        transport = StdioTransport()
        await transport.connect(server)
        
        logger.info("🔧 Toolkit MCP Server connected and ready")
        
        # Keep the process running
        while True:
            await asyncio.sleep(1)
            
    except Exception as error:
        logger.error(f"❌ Failed to start Toolkit MCP Server: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())