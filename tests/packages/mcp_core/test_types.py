"""
Tests for MCP Core types
"""
import pytest
import sys
from pathlib import Path
from pydantic import ValidationError

# Add packages to path for testing
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir / "packages"))

from mcp_core.types import MCPServerConfig, MCPTool, MCPServerOptions


def test_mcp_server_config_creation():
    """Test MCPServerConfig creation and validation"""
    config = MCPServerConfig(
        name="test-server",
        version="1.0.0",
        description="Test server"
    )
    
    assert config.name == "test-server"
    assert config.version == "1.0.0"
    assert config.description == "Test server"


def test_mcp_server_config_minimal():
    """Test MCPServerConfig with minimal required fields"""
    config = MCPServerConfig(
        name="minimal-server",
        version="0.1.0"
    )
    
    assert config.name == "minimal-server"
    assert config.version == "0.1.0"
    assert config.description is None


def test_mcp_server_config_validation():
    """Test MCPServerConfig validation errors"""
    with pytest.raises(ValidationError):
        MCPServerConfig()  # Missing required fields
    
    with pytest.raises(ValidationError):
        MCPServerConfig(name="test")  # Missing version


def test_mcp_tool_creation():
    """Test MCPTool creation"""
    tool = MCPTool(
        name="test_tool",
        description="A test tool",
        input_schema={"type": "object", "properties": {}},
        output_schema={"type": "object", "properties": {}}
    )
    
    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert isinstance(tool.input_schema, dict)
    assert isinstance(tool.output_schema, dict)


def test_mcp_server_options_creation():
    """Test MCPServerOptions creation"""
    config = MCPServerConfig(name="test", version="1.0.0")
    tool = MCPTool(
        name="test_tool",
        description="Test",
        input_schema={},
        output_schema={}
    )
    
    async def test_handler(args):
        return {"result": "test"}
    
    options = MCPServerOptions(
        server_info=config,
        tools=[tool],
        handlers={"test_tool": test_handler}
    )
    
    assert options.server_info == config
    assert len(options.tools) == 1
    assert "test_tool" in options.handlers