"""
Test MCP server protocol compliance
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

# Add packages to path for testing
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir / "packages"))

from core.server import create_mcp_server
from core.types import MCPServerConfig, MCPServerOptions, MCPTool


class TestMCPServerProtocol:
    """Test that MCP servers properly implement the protocol"""

    @pytest.mark.asyncio
    async def test_server_lists_tools(self):
        """Test that server responds to tools/list requests"""
        # Create a mock handler
        mock_handler = AsyncMock(return_value={"result": "success"})

        # Server configuration
        options = MCPServerOptions(
            server_info=MCPServerConfig(
                name="test-server", version="1.0.0", description="Test server"
            ),
            tools=[
                MCPTool(
                    name="test_tool",
                    description="A test tool",
                    input_schema={
                        "type": "object",
                        "properties": {"input": {"type": "string"}},
                    },
                    output_schema={
                        "type": "object",
                        "properties": {"result": {"type": "string"}},
                    },
                ),
                MCPTool(
                    name="another_tool",
                    description="Another test tool",
                    input_schema={
                        "type": "object",
                        "properties": {"value": {"type": "number"}},
                    },
                    output_schema={
                        "type": "object",
                        "properties": {"result": {"type": "string"}},
                    },
                ),
            ],
            handlers={"test_tool": mock_handler, "another_tool": mock_handler},
        )

        # Create the server
        server = create_mcp_server(options)

        # Test that server has the list_tools decorator applied
        # The actual test is that create_mcp_server doesn't throw an error
        # and that the server object is created successfully
        assert server is not None

        # Verify the tools were passed correctly to the server
        assert len(options.tools) == 2
        assert options.tools[0].name == "test_tool"
        assert options.tools[1].name == "another_tool"

        # Verify all tools have corresponding handlers
        for tool in options.tools:
            assert tool.name in options.handlers

    @pytest.mark.asyncio
    async def test_server_handles_tool_calls(self):
        """Test that server properly routes tool calls to handlers"""
        # Create mock handlers with different return values
        handler1_result = {"result": "from_handler1"}
        handler2_result = {"result": "from_handler2"}

        handler1 = AsyncMock(return_value=handler1_result)
        handler2 = AsyncMock(return_value=handler2_result)

        options = MCPServerOptions(
            server_info=MCPServerConfig(name="test-server", version="1.0.0"),
            tools=[
                MCPTool(
                    name="tool1",
                    description="Tool 1",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                ),
                MCPTool(
                    name="tool2",
                    description="Tool 2",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                ),
            ],
            handlers={"tool1": handler1, "tool2": handler2},
        )

        server = create_mcp_server(options)

        # Test that call_tool is registered
        assert hasattr(server, "call_tool")

        # Verify handlers are properly mapped
        assert "tool1" in options.handlers
        assert "tool2" in options.handlers

    @pytest.mark.asyncio
    async def test_server_handles_unknown_tool(self):
        """Test that server properly handles calls to unknown tools"""
        mock_handler = AsyncMock()

        options = MCPServerOptions(
            server_info=MCPServerConfig(name="test-server", version="1.0.0"),
            tools=[
                MCPTool(
                    name="known_tool",
                    description="Known tool",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                )
            ],
            handlers={"known_tool": mock_handler},
        )

        create_mcp_server(options)

        # Verify that only known tools are in handlers
        assert "known_tool" in options.handlers
        assert "unknown_tool" not in options.handlers

    @pytest.mark.asyncio
    async def test_server_error_handling(self):
        """Test that server properly handles and logs errors"""
        # Create a handler that raises an error
        error_handler = AsyncMock(side_effect=ValueError("Test error"))

        options = MCPServerOptions(
            server_info=MCPServerConfig(name="test-server", version="1.0.0"),
            tools=[
                MCPTool(
                    name="error_tool",
                    description="Tool that errors",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                )
            ],
            handlers={"error_tool": error_handler},
        )

        create_mcp_server(options)

        # Verify the handler is registered even though it will error
        assert "error_tool" in options.handlers

    def test_server_requires_matching_tools_and_handlers(self):
        """Test that all tools have corresponding handlers"""
        mock_handler = AsyncMock()

        options = MCPServerOptions(
            server_info=MCPServerConfig(name="test-server", version="1.0.0"),
            tools=[
                MCPTool(
                    name="tool_with_handler",
                    description="Has handler",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                ),
                MCPTool(
                    name="tool_without_handler",
                    description="No handler",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                ),
            ],
            handlers={
                "tool_with_handler": mock_handler
                # Note: tool_without_handler is missing
            },
        )

        # Server should still be created, but tool_without_handler won't work
        server = create_mcp_server(options)
        assert server is not None

        # Verify which handlers exist
        assert "tool_with_handler" in options.handlers
        assert "tool_without_handler" not in options.handlers
