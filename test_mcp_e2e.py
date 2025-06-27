#!/usr/bin/env python3
"""
End-to-end MCP protocol test for Drafts integration.
Tests the actual MCP server integration layer that we missed in unit tests.
"""
import asyncio
import json
import subprocess
import time
import sys
from pathlib import Path


async def test_mcp_server_startup():
    """Test that the MCP server starts without errors."""
    print("🚀 Testing MCP Server Startup...")
    
    # Start the toolkit server process
    process = subprocess.Popen([
        "docker", "run", "--rm", "-i",
        "--name", "toolkit-e2e-test",
        "-v", "/Users/mpaz/Documents/ToolkitData:/app/data",
        "mcp-fleet-toolkit-local:latest"
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    try:
        # Wait a moment for startup
        await asyncio.sleep(2)
        
        # Check if process is still running (not crashed)
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ Server crashed during startup!")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
        print("✅ MCP Server started successfully")
        return True, process
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        if process.poll() is None:
            process.terminate()
        return False


async def test_mcp_initialization(process):
    """Test MCP protocol initialization."""
    print("\n🔧 Testing MCP Protocol Initialization...")
    
    # Send initialization request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response with timeout
        response_line = await asyncio.wait_for(
            asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
            timeout=5.0
        )
        
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialization response: {response.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}")
            return True
        else:
            print("❌ No initialization response received")
            return False
            
    except asyncio.TimeoutError:
        print("❌ Initialization timed out")
        return False
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


async def test_tools_list(process):
    """Test that tools are properly registered."""
    print("\n📋 Testing Tools List...")
    
    # Try the correct MCP protocol format
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
        # Note: no params for tools/list
    }
    
    try:
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response_line = await asyncio.wait_for(
            asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
            timeout=5.0
        )
        
        if response_line:
            print(f"🔍 Raw response: {response_line.strip()}")
            response = json.loads(response_line.strip())
            print(f"🔍 Parsed response: {json.dumps(response, indent=2)}")
            tools = response.get('result', {}).get('tools', [])
            
            print(f"📊 Found {len(tools)} tools:")
            tool_names = []
            for tool in tools:
                name = tool.get('name', 'unknown')
                desc = tool.get('description', 'No description')
                print(f"  - {name}: {desc}")
                tool_names.append(name)
            
            # Check for our Drafts tools
            expected_tools = ['create_draft', 'create_draft_with_template']
            missing_tools = [tool for tool in expected_tools if tool not in tool_names]
            
            if missing_tools:
                print(f"❌ Missing expected tools: {missing_tools}")
                return False
            else:
                print("✅ All expected Drafts tools found")
                return True
                
        else:
            print("❌ No tools list response received")
            return False
            
    except Exception as e:
        print(f"❌ Tools list failed: {e}")
        return False


async def test_create_draft_tool(process):
    """Test actual create_draft tool call via MCP protocol."""
    print("\n✨ Testing create_draft Tool Call...")
    
    create_draft_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "create_draft",
            "arguments": {
                "content": "MCP E2E Test Draft - " + time.strftime('%Y-%m-%d %H:%M:%S'),
                "tags": ["mcp-test", "e2e", "automation"],
                "action": None
            }
        }
    }
    
    try:
        print(f"📤 Sending request: {json.dumps(create_draft_request, indent=2)}")
        process.stdin.write(json.dumps(create_draft_request) + "\n")
        process.stdin.flush()
        
        response_line = await asyncio.wait_for(
            asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
            timeout=10.0
        )
        
        if response_line:
            response = json.loads(response_line.strip())
            print(f"📥 Response: {json.dumps(response, indent=2)}")
            
            if 'error' in response:
                print(f"❌ Tool call failed with error: {response['error']}")
                return False
            
            result = response.get('result', {})
            if result.get('success'):
                print(f"✅ Draft created successfully!")
                print(f"🔗 URL: {result.get('url', 'No URL')}")
                return True
            else:
                print(f"❌ Draft creation failed: {result.get('error', 'Unknown error')}")
                return False
                
        else:
            print("❌ No response received for create_draft")
            return False
            
    except Exception as e:
        print(f"❌ create_draft test failed: {e}")
        return False


async def test_template_draft_tool(process):
    """Test create_draft_with_template tool call."""
    print("\n📝 Testing create_draft_with_template Tool Call...")
    
    template_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "create_draft_with_template",
            "arguments": {
                "template_name": "daily_note",
                "variables": {
                    "date": time.strftime('%Y-%m-%d'),
                    "mood": "productive",
                    "goals": ["Test MCP integration", "Verify E2E functionality", "Complete Drafts integration"]
                }
            }
        }
    }
    
    try:
        print(f"📤 Sending template request...")
        process.stdin.write(json.dumps(template_request) + "\n")
        process.stdin.flush()
        
        response_line = await asyncio.wait_for(
            asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
            timeout=10.0
        )
        
        if response_line:
            response = json.loads(response_line.strip())
            print(f"📥 Template response received")
            
            if 'error' in response:
                print(f"❌ Template tool call failed: {response['error']}")
                return False
            
            result = response.get('result', {})
            if result.get('success'):
                print(f"✅ Template draft created successfully!")
                return True
            else:
                print(f"❌ Template creation failed: {result.get('error', 'Unknown error')}")
                return False
                
        else:
            print("❌ No response for template draft")
            return False
            
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False


async def run_full_mcp_e2e_test():
    """Run the complete MCP E2E test suite."""
    print("🧪 MCP FLEET DRAFTS INTEGRATION - FULL E2E TEST")
    print("=" * 60)
    print("Testing the MCP protocol layer that unit tests missed!")
    print()
    
    # Using locally built image
    print("🐳 Using locally built Docker image...")
    print("✅ mcp-fleet-toolkit-local:latest")
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Server startup
    startup_result = await test_mcp_server_startup()
    if isinstance(startup_result, tuple):
        tests_passed += 1
        success, process = startup_result
    else:
        print("💥 Cannot continue - server failed to start")
        return
    
    try:
        # Test 2: MCP initialization
        if await test_mcp_initialization(process):
            tests_passed += 1
        
        # Test 3: Tools registration
        if await test_tools_list(process):
            tests_passed += 1
        
        # Test 4: create_draft tool
        if await test_create_draft_tool(process):
            tests_passed += 1
        
        # Test 5: template draft tool
        if await test_template_draft_tool(process):
            tests_passed += 1
            
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        if process.poll() is None:
            process.terminate()
            process.wait()
        subprocess.run(["docker", "stop", "toolkit-e2e-test"], 
                      capture_output=True, text=True)
    
    # Results
    print("\n" + "=" * 60)
    print(f"🎯 E2E TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! MCP Drafts integration is working!")
        print("✅ Ready for Claude Desktop integration")
        return True
    else:
        print(f"❌ {total_tests - tests_passed} tests failed")
        print("🔧 MCP integration needs fixes before Claude Desktop testing")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(run_full_mcp_e2e_test())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test framework error: {e}")
        sys.exit(1)