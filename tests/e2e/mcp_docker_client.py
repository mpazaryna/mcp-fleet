"""
MCP Docker Client for E2E Testing

Simulates how Claude Desktop would interact with MCP Docker containers.
"""

import asyncio
import json
import logging
import subprocess
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

logger = logging.getLogger(__name__)


class MCPDockerClient:
    """
    E2E test client for MCP Docker containers

    Simulates the MCP protocol interaction that Claude Desktop
    would have with a containerized MCP server.
    """

    def __init__(
        self,
        image_name: str,
        container_name: str,
        volumes: dict[str, str] | None = None,
        env_vars: dict[str, str] | None = None,
    ):
        """
        Initialize MCP Docker client

        Args:
            image_name: Docker image name (e.g., "pazland/mcp-fleet-memry:latest")
            container_name: Name for the container instance
            volumes: Volume mounts {host_path: container_path}
            env_vars: Environment variables {key: value}
        """
        self.image_name = image_name
        self.container_name = container_name
        self.volumes = volumes or {}
        self.env_vars = env_vars or {}
        self.process: subprocess.Popen | None = None
        self.request_id = 0

    def _get_docker_command(self) -> list[str]:
        """Build the docker run command"""
        cmd = ["docker", "run", "--rm", "-i", "--name", self.container_name]

        # Add environment variables
        for key, value in self.env_vars.items():
            cmd.extend(["-e", f"{key}={value}"])

        # Add volume mounts
        for host_path, container_path in self.volumes.items():
            cmd.extend(["-v", f"{host_path}:{container_path}"])

        cmd.append(self.image_name)
        return cmd

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator["MCPDockerClient", None]:
        """
        Context manager for MCP Docker container lifecycle

        Usage:
            async with client.connect() as mcp:
                result = await mcp.call_tool("create_memory", {...})
        """
        try:
            # Start container
            cmd = self._get_docker_command()
            logger.info(f"Starting container: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,  # Unbuffered for real-time communication
            )

            # Wait for container to start (basic MCP servers print startup messages)
            await asyncio.sleep(2)

            # Initialize MCP protocol
            await self._initialize()

            yield self

        finally:
            # Cleanup
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()

                # Stop any running container
                try:
                    subprocess.run(
                        ["docker", "stop", self.container_name],
                        check=False,
                        capture_output=True,
                    )
                except Exception:
                    pass  # Container might already be stopped

    async def _send_request(self, method: str, params: Any = None) -> dict[str, Any]:
        """Send MCP JSON-RPC request and get response"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP client not connected")

        self.request_id += 1
        request = {"jsonrpc": "2.0", "id": self.request_id, "method": method}

        if params is not None:
            request["params"] = params

        # Send request
        request_json = json.dumps(request) + "\n"
        logger.debug(f"Sending: {request_json.strip()}")

        try:
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
        except Exception as e:
            raise RuntimeError(f"Failed to send request: {e}")

        # Read response
        try:
            response_line = self.process.stdout.readline()
            if not response_line:
                stderr_output = (
                    self.process.stderr.read() if self.process.stderr else ""
                )
                raise RuntimeError(f"No response from server. Stderr: {stderr_output}")

            logger.debug(f"Received: {response_line.strip()}")
            response = json.loads(response_line)

            # Check for JSON-RPC errors
            if "error" in response:
                raise RuntimeError(f"MCP error: {response['error']}")

            return response

        except json.JSONDecodeError as e:
            stderr_output = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(
                f"Invalid JSON response: {e}. Response: {response_line}. Stderr: {stderr_output}"
            )

    async def _send_notification(self, method: str, params: Any = None) -> None:
        """Send MCP JSON-RPC notification (no response expected)"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP client not connected")

        notification = {"jsonrpc": "2.0", "method": method}

        if params is not None:
            notification["params"] = params

        # Send notification
        notification_json = json.dumps(notification) + "\n"
        logger.debug(f"Sending notification: {notification_json.strip()}")

        try:
            self.process.stdin.write(notification_json)
            self.process.stdin.flush()
        except Exception as e:
            raise RuntimeError(f"Failed to send notification: {e}")

    async def _initialize(self) -> dict[str, Any]:
        """Initialize MCP protocol connection"""
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp-e2e-test-client", "version": "1.0.0"},
        }

        response = await self._send_request("initialize", params)

        # Send initialized notification to complete the handshake
        await self._send_notification("notifications/initialized")

        logger.info("MCP protocol initialized")
        return response

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools from the MCP server"""
        response = await self._send_request("tools/list", {})
        return response.get("result", {}).get("tools", [])

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Call a tool on the MCP server

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool execution result
        """
        params = {"name": tool_name, "arguments": arguments}

        response = await self._send_request("tools/call", params)
        return response.get("result", {})

    async def get_server_info(self) -> dict[str, Any]:
        """Get server information"""
        try:
            response = await self._send_request(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"},
                },
            )
            return response.get("result", {})
        except Exception:
            return {}


def create_memry_client(storage_path: str = "/tmp/e2e-memry-test") -> MCPDockerClient:
    """
    Factory function to create MCP client for memry server testing

    Args:
        storage_path: Host path for memory storage (will be mounted to container)

    Returns:
        Configured MCPDockerClient for memry server
    """
    return MCPDockerClient(
        image_name="pazland/mcp-fleet-memry:latest",
        container_name="memry-e2e-test",
        volumes={storage_path: "/app/memories"},
        env_vars={"MEMRY_STORAGE_PATH": "/app/memories"},
    )
