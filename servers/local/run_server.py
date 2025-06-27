#!/usr/bin/env python3
"""
Standalone Local MCP Server Runner

This script can run the local server independently for testing and development.
It doesn't rely on the complex workspace setup and can be used directly.
"""
import asyncio
import json
import sys
import logging
from pathlib import Path

# Add the src directory to Python path
server_root = Path(__file__).parent
sys.path.insert(0, str(server_root / "src"))

# Import our tools
from tools.apple_notes_tools import notes_tools, notes_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)


class SimpleStdioServer:
    """A simple stdio-based MCP server for testing"""
    
    def __init__(self, tools, handlers):
        self.tools = tools
        self.handlers = handlers
        self.request_id = 0
    
    def send_response(self, result):
        """Send a response to stdout"""
        response = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "result": result
        }
        print(json.dumps(response))
        sys.stdout.flush()
    
    def send_error(self, error_msg):
        """Send an error response"""
        response = {
            "jsonrpc": "2.0", 
            "id": self.request_id,
            "error": {
                "code": -1,
                "message": error_msg
            }
        }
        print(json.dumps(response))
        sys.stdout.flush()
    
    async def handle_list_tools(self):
        """Handle tools/list request"""
        logger.info("Handling tools/list request")
        return {
            "tools": self.tools
        }
    
    async def handle_tool_call(self, tool_name, arguments):
        """Handle tools/call request"""
        logger.info(f"Handling tool call: {tool_name} with args: {arguments}")
        
        if tool_name not in self.handlers:
            raise Exception(f"Unknown tool: {tool_name}")
        
        handler = self.handlers[tool_name]
        result = await handler(arguments)
        
        return {
            "content": [
                {
                    "type": "text", 
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    
    async def handle_initialize(self):
        """Handle initialize request"""
        logger.info("Handling initialize request")
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "local",
                "version": "0.1.0"
            }
        }
    
    async def process_request(self, request):
        """Process a single JSON-RPC request"""
        try:
            self.request_id = request.get("id", 0)
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                result = await self.handle_initialize()
            elif method == "tools/list":
                result = await self.handle_list_tools()
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = await self.handle_tool_call(tool_name, arguments)
            else:
                raise Exception(f"Unknown method: {method}")
            
            self.send_response(result)
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.send_error(str(e))


async def main():
    """Main server function"""
    logger.info("🏠 Starting Local MCP Server (Standalone Mode)...")
    logger.info(f"   📝 Apple Notes tools: {len(notes_tools)} tools available")
    
    server = SimpleStdioServer(notes_tools, notes_handlers)
    
    # For testing, just show server info and available tools
    logger.info("\n" + "="*60)
    logger.info("LOCAL MCP SERVER - APPLE NOTES INTEGRATION")
    logger.info("="*60)
    logger.info(f"Available tools: {len(notes_tools)}")
    for tool in notes_tools:
        logger.info(f"  • {tool['name']}: {tool['description']}")
    logger.info("="*60)
    
    # Test a simple tool call
    logger.info("\nTesting Apple Notes integration...")
    try:
        test_result = await server.handle_tool_call("create_note", {
            "title": "MCP Local Server Test",
            "content": "This note was created by the MCP Local Server to test Apple Notes integration.\n\nFeatures:\n- Native AppleScript integration\n- Python-based MCP server\n- Standalone operation (no Docker needed)\n\nIf you see this note in Apple Notes, the integration is working perfectly!"
        })
        logger.info("✅ Apple Notes integration test successful!")
        logger.info("Check your Apple Notes app for the test note.")
    except Exception as e:
        logger.error(f"❌ Apple Notes integration test failed: {e}")
    
    logger.info("\n🏠 Local MCP Server ready for Claude Desktop integration")
    logger.info("To connect to Claude Desktop, use this server configuration:")
    logger.info(f"Command: python3 {Path(__file__).absolute()}")
    
    # Keep running for stdio communication
    logger.info("\nListening for MCP requests on stdin...")
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        
        while True:
            line = await reader.readline()
            if not line:
                break
            line = line.decode('utf-8').strip()
            if line:
                try:
                    request = json.loads(line)
                    await server.process_request(request)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    server.send_error("Invalid JSON")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error in stdin loop: {e}")


if __name__ == "__main__":
    asyncio.run(main())