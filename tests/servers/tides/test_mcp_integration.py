"""
Test Tides server MCP protocol integration
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "servers" / "tides"))
sys.path.insert(0, str(project_root / "packages"))

from mcp_core.server import create_mcp_server
from mcp_core.types import MCPServerOptions, MCPServerConfig
from tides.src.tools.tide_tools import tide_tools, tide_handlers


class TestTidesMCPIntegration:
    """Test that Tides server properly implements MCP protocol"""
    
    @pytest.mark.asyncio
    async def test_tides_server_has_all_tools(self):
        """Test that all tide tools are properly registered"""
        # Create server options with actual tide tools
        options = MCPServerOptions(
            server_info=MCPServerConfig(
                name="tides",
                version="0.1.0",
                description="Rhythmic workflow management"
            ),
            tools=tide_tools,
            handlers=tide_handlers
        )
        
        # Create the server
        server = create_mcp_server(options)
        
        # Verify server was created
        assert server is not None
        
        # Verify all expected tools are present
        tool_names = [tool.name for tool in tide_tools]
        assert "create_tide" in tool_names
        assert "list_tides" in tool_names
        assert "flow_tide" in tool_names
        
        # Verify all tools have handlers
        for tool_name in tool_names:
            assert tool_name in tide_handlers
    
    @pytest.mark.asyncio 
    async def test_tides_tools_have_valid_schemas(self):
        """Test that all tide tools have valid input/output schemas"""
        for tool in tide_tools:
            # Check that tool has required fields
            assert tool.name is not None
            assert tool.description is not None
            assert tool.input_schema is not None
            
            # Check that input schema is a valid JSON schema
            assert isinstance(tool.input_schema, dict)
            assert "type" in tool.input_schema or "$ref" in tool.input_schema
    
    @pytest.mark.asyncio
    async def test_tides_server_initialization(self):
        """Test that Tides server initializes without errors"""
        # Test that we can create a server with tide tools
        options = MCPServerOptions(
            server_info=MCPServerConfig(
                name="tides",
                version="0.1.0",
                description="Rhythmic workflow management"
            ),
            tools=tide_tools,
            handlers=tide_handlers
        )
        
        # Create the server - this would fail if list_tools wasn't implemented
        server = create_mcp_server(options)
        
        # Verify server was created successfully
        assert server is not None
        
        # Verify the configuration
        assert options.server_info.name == "tides"
        assert options.server_info.version == "0.1.0"
        assert "workflow" in options.server_info.description.lower()
    
    @pytest.mark.asyncio
    async def test_create_tide_handler_integration(self):
        """Test that create_tide handler works with MCP server"""
        from tides.src.tools.tide_tools import create_tide_handler
        
        # Mock the storage
        with patch('tides.src.tools.tide_tools.tide_storage') as mock_storage:
            # Create a mock TideData object
            from tides.src.storage.tide_storage import TideData
            mock_tide = TideData(
                id="test-tide-123",
                name="Test Tide",
                flow_type="daily",
                status="active",
                created_at="2024-01-01T00:00:00Z",
                flow_history=[]
            )
            mock_storage.create_tide = AsyncMock(return_value=mock_tide)
            
            # Call the handler
            result = await create_tide_handler({
                "name": "Test Tide",
                "flow_type": "daily",
                "description": "Test description"
            })
            
            # Verify result
            assert result["success"] is True
            assert result["tide_id"] == "test-tide-123"
            assert result["name"] == "Test Tide"
            assert result["flow_type"] == "daily"
            
            # Verify storage was called
            mock_storage.create_tide.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_server_tools_match_handlers(self):
        """Test that every tool has a corresponding handler and vice versa"""
        tool_names = {tool.name for tool in tide_tools}
        handler_names = set(tide_handlers.keys())
        
        # Every tool should have a handler
        assert tool_names == handler_names, (
            f"Mismatch between tools and handlers. "
            f"Tools without handlers: {tool_names - handler_names}, "
            f"Handlers without tools: {handler_names - tool_names}"
        )