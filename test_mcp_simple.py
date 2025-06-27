#!/usr/bin/env python3
"""
Simple MCP protocol test using the exact format Claude Desktop uses.
"""
import asyncio
import json
import subprocess
import time


async def test_mcp_with_real_client():
    """Test MCP server using the Python MCP client library like Claude Desktop does."""
    print("🧪 Testing MCP with Python MCP Client (like Claude Desktop)")
    print("=" * 60)
    
    try:
        # Import the MCP client library
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        print("✅ MCP client library available")
        
        # Create server parameters like Claude Desktop would
        server_params = StdioServerParameters(
            command="docker",
            args=[
                "run", "--rm", "-i",
                "--name", "toolkit-mcp-simple-test",
                "-v", "/Users/mpaz/Documents/ToolkitData:/app/data",
                "mcp-fleet-toolkit-local:latest"
            ]
        )
        
        print("🚀 Starting MCP client session...")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ MCP session established")
                
                # Initialize like Claude Desktop does
                print("🔧 Initializing MCP session...")
                await session.initialize()
                print("✅ MCP initialized")
                
                # List tools like Claude Desktop does
                print("📋 Listing tools...")
                tools = await session.list_tools()
                print(f"📊 Found {len(tools.tools)} tools:")
                
                drafts_tools = []
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                    if 'draft' in tool.name.lower():
                        drafts_tools.append(tool.name)
                
                # Test create_draft tool
                if 'create_draft' in drafts_tools:
                    print("\n✨ Testing create_draft tool...")
                    result = await session.call_tool(
                        "create_draft",
                        {
                            "content": f"MCP Simple Test - {time.strftime('%Y-%m-%d %H:%M:%S')}",
                            "tags": ["mcp-test", "simple-test", "working"],
                            "action": None
                        }
                    )
                    print(f"📥 Result: {result}")
                    
                    if hasattr(result, 'content') and result.content:
                        for content in result.content:
                            if hasattr(content, 'text'):
                                content_text = content.text
                                if 'success' in content_text.lower():
                                    print("✅ create_draft SUCCESS!")
                                    return True
                                else:
                                    print(f"❌ create_draft failed: {content_text}")
                                    return False
                else:
                    print("❌ create_draft tool not found")
                    return False
                    
    except ImportError:
        print("❌ MCP client library not available - installing...")
        subprocess.run(["uv", "add", "mcp"], check=True)
        print("🔄 Please run the test again after installation")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_mcp_with_real_client())
        if result:
            print("\n🎉 MCP INTEGRATION TEST PASSED!")
            print("✅ Ready for Claude Desktop!")
        else:
            print("\n❌ MCP integration needs fixes")
    except Exception as e:
        print(f"\n💥 Test error: {e}")