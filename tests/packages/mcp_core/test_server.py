"""
Tests for MCP Core server functionality
"""
import pytest
from unittest.mock import Mock, patch

from mcp_core.server import create_mcp_server, MCPServerFactory
from mcp_core.types import MCPServerConfig, MCPTool, MCPServerOptions


@pytest.fixture
def sample_server_options():
    """Create sample server options for testing"""
    config = MCPServerConfig(
        name="test-server",
        version="1.0.0",
        description="Test server"
    )
    
    tool = MCPTool(
        name="echo",
        description="Echo back the input",
        input_schema={"type": "object", "properties": {"message": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"result": {"type": "string"}}}
    )
    
    async def echo_handler(args):
        return {"result": args.get("message", "empty")}
    
    return MCPServerOptions(
        server_info=config,
        tools=[tool],
        handlers={"echo": echo_handler}
    )


@patch('mcp_core.server.Server')
def test_create_mcp_server(mock_server_class, sample_server_options):
    """Test create_mcp_server function"""
    mock_server = Mock()
    mock_server_class.return_value = mock_server
    
    server = create_mcp_server(sample_server_options)
    
    # Verify server was created with correct name
    mock_server_class.assert_called_once_with("test-server")
    assert server == mock_server


def test_mcp_server_factory_creation():
    """Test MCPServerFactory creation"""
    factory = MCPServerFactory()
    assert factory.logger is None
    
    mock_logger = Mock()
    factory_with_logger = MCPServerFactory(logger=mock_logger)
    assert factory_with_logger.logger == mock_logger


@patch('mcp_core.server.create_mcp_server')
def test_mcp_server_factory_create(mock_create_server, sample_server_options):
    """Test MCPServerFactory create method"""
    mock_server = Mock()
    mock_create_server.return_value = mock_server
    
    mock_logger = Mock()
    factory = MCPServerFactory(logger=mock_logger)
    
    result = factory.create(sample_server_options)
    
    # Verify logger was called
    mock_logger.info.assert_called_once_with(
        "Creating MCP server: test-server v1.0.0"
    )
    
    # Verify create_mcp_server was called
    mock_create_server.assert_called_once_with(sample_server_options)
    assert result == mock_server


@patch('mcp_core.server.create_mcp_server')
def test_mcp_server_factory_create_without_logger(mock_create_server, sample_server_options):
    """Test MCPServerFactory create method without logger"""
    mock_server = Mock()
    mock_create_server.return_value = mock_server
    
    factory = MCPServerFactory()
    result = factory.create(sample_server_options)
    
    # Verify create_mcp_server was called
    mock_create_server.assert_called_once_with(sample_server_options)
    assert result == mock_server