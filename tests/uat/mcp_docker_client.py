#!/usr/bin/env python3
"""
MCP Docker Client for UAT Testing

A robust client that communicates with MCP servers running in Docker containers
using the proper MCP JSON-RPC protocol. Supports all MCP Fleet servers.
"""
import subprocess
import json
import time
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MCPServerInfo:
    """Information about an MCP server"""
    name: str
    docker_image: str
    port: Optional[int] = None
    volume_mappings: Optional[Dict[str, str]] = None
    env_vars: Optional[Dict[str, str]] = None
    startup_delay: float = 2.0
    
    
class MCPDockerClient:
    """
    Docker-based MCP client for UAT testing
    
    Provides a clean interface for testing MCP servers in Docker containers
    with proper protocol handling and timeout management.
    """
    
    def __init__(self, server_info: MCPServerInfo, debug: bool = False):
        self.server_info = server_info
        self.debug = debug
        self.process = None
        self.request_id = 0
        
        # Setup logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
    
    def get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    def _build_docker_command(self) -> List[str]:
        """Build the Docker command for this server"""
        cmd = ["docker", "run", "--rm", "-i"]
        
        # Add volume mappings
        if self.server_info.volume_mappings:
            for host_path, container_path in self.server_info.volume_mappings.items():
                cmd.extend(["-v", f"{host_path}:{container_path}"])
        
        # Add environment variables
        if self.server_info.env_vars:
            for key, value in self.server_info.env_vars.items():
                cmd.extend(["-e", f"{key}={value}"])
        
        # Add port mapping if specified
        if self.server_info.port:
            cmd.extend(["-p", f"{self.server_info.port}:{self.server_info.port}"])
        
        # Add the image
        cmd.append(self.server_info.docker_image)
        
        return cmd
    
    def start(self) -> None:
        """Start the Docker container and initialize MCP protocol"""
        if self.process:
            raise RuntimeError("Client already started")
        
        docker_cmd = self._build_docker_command()
        logger.info(f"🚀 Starting {self.server_info.name} Docker container...")
        logger.debug(f"Docker command: {' '.join(docker_cmd)}")
        
        self.process = subprocess.Popen(
            docker_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered for real-time communication
        )
        
        # Wait for container startup
        logger.info(f"⏳ Waiting {self.server_info.startup_delay}s for container startup...")
        time.sleep(self.server_info.startup_delay)
        
        # Initialize MCP protocol
        self._initialize_protocol()
    
    def _initialize_protocol(self) -> Dict[str, Any]:
        """Initialize the MCP protocol"""
        logger.info("📡 Initializing MCP protocol...")
        
        # Step 1: Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "uat-client", "version": "1.0.0"}
            }
        }
        
        self._send_request(init_request)
        init_response = self._read_response()
        
        if "error" in init_response:
            raise RuntimeError(f"Initialize failed: {init_response['error']}")
        
        server_info = init_response["result"]["serverInfo"]
        logger.info(f"✅ Initialized: {server_info['name']} v{server_info['version']}")
        
        # Step 2: Send initialized notification
        logger.debug("📨 Sending initialized notification...")
        init_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        self._send_request(init_notification)
        
        return init_response["result"]
    
    def _send_request(self, request: Dict[str, Any]) -> None:
        """Send a JSON-RPC request to the server"""
        if not self.process:
            raise RuntimeError("Client not started")
        
        request_json = json.dumps(request)
        logger.debug(f"📤 Sending: {request_json}")
        
        self.process.stdin.write(request_json + '\n')
        self.process.stdin.flush()
    
    def _read_response(self) -> Dict[str, Any]:
        """Read a JSON-RPC response from the server"""
        if not self.process:
            raise RuntimeError("Client not started")
        
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response received from server")
        
        logger.debug(f"📥 Received: {response_line.strip()}")
        return json.loads(response_line)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the server"""
        logger.info("🔧 Listing available tools...")
        
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/list"
        }
        
        self._send_request(request)
        response = self._read_response()
        
        if "error" in response:
            raise RuntimeError(f"List tools failed: {response['error']}")
        
        tools = response["result"]["tools"]
        logger.info(f"✅ Found {len(tools)} tools")
        
        for tool in tools:
            logger.info(f"   • {tool['name']}: {tool['description']}")
        
        return tools
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server"""
        logger.info(f"🔧 Calling tool: {tool_name}")
        logger.debug(f"Arguments: {arguments}")
        
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        self._send_request(request)
        response = self._read_response()
        
        if "error" in response:
            logger.error(f"❌ Tool call failed: {response['error']}")
            raise RuntimeError(f"Tool call failed: {response['error']}")
        
        result = response["result"]
        logger.info(f"✅ Tool call successful!")
        
        # Log structured content if available
        if "content" in result:
            for content_item in result["content"]:
                if content_item.get("type") == "text":
                    logger.debug(f"Response: {content_item.get('text', '')[:200]}...")
        
        return result
    
    def stop(self) -> None:
        """Stop the Docker container"""
        if self.process:
            logger.info("🛑 Stopping Docker container...")
            try:
                self.process.stdin.close()
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("⚠️  Container didn't stop gracefully, killing...")
                self.process.kill()
                self.process.wait()
            finally:
                self.process = None
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# Predefined server configurations
COMPASS_SERVER = MCPServerInfo(
    name="compass",
    docker_image="pazland/mcp-fleet-compass:latest",
    volume_mappings={},  # Will be set per test
    startup_delay=3.0
)

TIDES_SERVER = MCPServerInfo(
    name="tides", 
    docker_image="pazland/mcp-fleet-tides:latest",
    env_vars={},  # Will be set per test if needed
    volume_mappings={},  # Will be set per test
    startup_delay=2.5
)

MEMRY_SERVER = MCPServerInfo(
    name="memry",
    docker_image="pazland/mcp-fleet-memry:latest", 
    volume_mappings={},  # Will be set per test
    startup_delay=2.0
)



def create_test_workspace() -> Path:
    """Create a temporary workspace for UAT testing"""
    workspace = Path.home() / "Documents" / "mcp-fleet-uat" / f"test-{int(time.time())}"
    workspace.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Created test workspace: {workspace}")
    return workspace


if __name__ == "__main__":
    # Quick test of the client framework
    print("🧪 Testing MCP Docker Client Framework")
    
    workspace = create_test_workspace()
    
    # Test with memry server
    memry_config = MEMRY_SERVER
    memry_config.volume_mappings = {str(workspace): "/app/memories"}
    
    with MCPDockerClient(memry_config, debug=True) as client:
        tools = client.list_tools()
        
        if any(tool["name"] == "create_memory" for tool in tools):
            result = client.call_tool("create_memory", {
                "title": "Test Memory",
                "content": "This is a test memory from the UAT framework",
                "source": "uat-test",
                "tags": ["test", "uat", "framework"]
            })
            print(f"✅ Created memory successfully!")
        else:
            print("❌ create_memory tool not found")
    
    print("🎉 Framework test completed!")