"""End-to-end tests for YogaTeach MCP Server."""

import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path

from tests.e2e.mcp_docker_client import MCPDockerClient


class TestYogaTeachE2E:
    """End-to-end tests for YogaTeach MCP Server using Docker."""

    @pytest.fixture
    async def mcp_client(self):
        """Create an MCP client connected to the YogaTeach server."""
        client = MCPDockerClient("yogateach")
        await client.connect()
        yield client
        await client.close()

    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary storage directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.mark.asyncio
    async def test_server_initialization(self, mcp_client):
        """Test that the YogaTeach server initializes correctly."""
        # Test initialize request
        initialize_response = await mcp_client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            }
        )
        
        assert initialize_response["protocolVersion"] == "2024-11-05"
        assert initialize_response["serverInfo"]["name"] == "yogateach"
        assert "capabilities" in initialize_response

    @pytest.mark.asyncio
    async def test_list_tools(self, mcp_client):
        """Test listing available tools."""
        # Initialize first
        await mcp_client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            }
        )
        
        # List tools
        tools_response = await mcp_client.send_request("tools/list", {})
        
        assert "tools" in tools_response
        tools = tools_response["tools"]
        assert len(tools) == 2
        
        # Check for expected tools
        tool_names = [tool["name"] for tool in tools]
        assert "create_setlist" in tool_names
        assert "create_talk" in tool_names
        
        # Verify tool structure
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool

    @pytest.mark.asyncio
    async def test_create_setlist_tool(self, mcp_client):
        """Test the create_setlist tool."""
        # Initialize server
        await mcp_client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            }
        )
        
        # Call create_setlist tool
        setlist_args = {
            "name": "E2E Test Setlist",
            "duration": 45,
            "level": "beginner",
            "focus": "flexibility",
            "considerations": "No inversions",
            "theme": "Relaxation"
        }
        
        tool_response = await mcp_client.send_request(
            "tools/call",
            {
                "name": "create_setlist",
                "arguments": setlist_args
            }
        )
        
        assert "content" in tool_response
        result = tool_response["content"][0]["text"]
        result_data = json.loads(result)
        
        assert result_data["success"] is True
        assert result_data["name"] == "E2E Test Setlist"
        assert result_data["content_type"] == "setlist"
        assert result_data["content_id"].startswith("setlist_")
        assert result_data["file_path"].endswith(".md")

    @pytest.mark.asyncio
    async def test_create_talk_tool(self, mcp_client):
        """Test the create_talk tool."""
        # Initialize server
        await mcp_client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            }
        )
        
        # Call create_talk tool
        talk_args = {
            "name": "E2E Test Talk",
            "duration": 30,
            "topic": "mindfulness",
            "audience": "beginners",
            "style": "contemporary",
            "message": "Present moment awareness"
        }
        
        tool_response = await mcp_client.send_request(
            "tools/call",
            {
                "name": "create_talk",
                "arguments": talk_args
            }
        )
        
        assert "content" in tool_response
        result = tool_response["content"][0]["text"]
        result_data = json.loads(result)
        
        assert result_data["success"] is True
        assert result_data["name"] == "E2E Test Talk"
        assert result_data["content_type"] == "talk"
        assert result_data["content_id"].startswith("talk_")
        assert result_data["file_path"].endswith(".md")

    @pytest.mark.asyncio
    async def test_create_setlist_invalid_input(self, mcp_client):
        """Test create_setlist with invalid input."""
        # Initialize server
        await mcp_client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            }
        )
        
        # Call create_setlist with invalid args (missing required fields)
        invalid_args = {
            "name": "Invalid Setlist",
            "duration": "invalid_duration",  # Should be int
            "level": "beginner"
            # Missing required fields
        }
        
        with pytest.raises(Exception):
            await mcp_client.send_request(
                "tools/call",
                {
                    "name": "create_setlist",
                    "arguments": invalid_args
                }
            )

    @pytest.mark.asyncio
    async def test_create_talk_invalid_input(self, mcp_client):
        """Test create_talk with invalid input."""
        # Initialize server
        await mcp_client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            }
        )
        
        # Call create_talk with invalid args (missing required fields)
        invalid_args = {
            "name": "Invalid Talk",
            "duration": 30,
            "topic": "mindfulness"
            # Missing required fields
        }
        
        with pytest.raises(Exception):
            await mcp_client.send_request(
                "tools/call",
                {
                    "name": "create_talk",
                    "arguments": invalid_args
                }
            )

    @pytest.mark.asyncio
    async def test_full_workflow_setlist_creation(self, mcp_client):
        """Test the complete workflow of creating a setlist."""
        # Initialize server
        await mcp_client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            }
        )
        
        # Create a comprehensive setlist
        setlist_args = {
            "name": "Full Workflow Test Setlist",
            "duration": 60,
            "level": "intermediate",
            "focus": "strength and balance",
            "considerations": "Lower back modifications available",
            "theme": "Building Inner Strength"
        }
        
        tool_response = await mcp_client.send_request(
            "tools/call",
            {
                "name": "create_setlist",
                "arguments": setlist_args
            }
        )
        
        # Verify response structure
        assert "content" in tool_response
        result = tool_response["content"][0]["text"]
        result_data = json.loads(result)
        
        # Verify all expected fields are present
        expected_fields = ["success", "content_id", "name", "content_type", "file_path", "created_at"]
        for field in expected_fields:
            assert field in result_data
        
        # Verify content matches input
        assert result_data["name"] == "Full Workflow Test Setlist"
        assert result_data["content_type"] == "setlist"
        assert result_data["success"] is True

    @pytest.mark.asyncio
    async def test_full_workflow_talk_creation(self, mcp_client):
        """Test the complete workflow of creating a dharma talk."""
        # Initialize server
        await mcp_client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            }
        )
        
        # Create a comprehensive talk
        talk_args = {
            "name": "Full Workflow Test Talk",
            "duration": 45,
            "topic": "compassion and loving-kindness",
            "audience": "experienced practitioners",
            "style": "traditional with contemporary applications",
            "message": "Cultivating compassion starts with self-acceptance"
        }
        
        tool_response = await mcp_client.send_request(
            "tools/call",
            {
                "name": "create_talk",
                "arguments": talk_args
            }
        )
        
        # Verify response structure
        assert "content" in tool_response
        result = tool_response["content"][0]["text"]
        result_data = json.loads(result)
        
        # Verify all expected fields are present
        expected_fields = ["success", "content_id", "name", "content_type", "file_path", "created_at"]
        for field in expected_fields:
            assert field in result_data
        
        # Verify content matches input
        assert result_data["name"] == "Full Workflow Test Talk"
        assert result_data["content_type"] == "talk"
        assert result_data["success"] is True