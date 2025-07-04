"""
Tests for MCP Core transport functionality
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add packages to path for testing
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir / "packages"))

from core.transport import StdioTransport, SocketTransport


@pytest.mark.asyncio
async def test_stdio_transport_creation():
    """Test StdioTransport creation"""
    transport = StdioTransport()
    assert transport.server is None


@pytest.mark.asyncio
@patch('core.transport.stdio_server')
async def test_stdio_transport_connect(mock_stdio_server):
    """Test StdioTransport connect method"""
    # Mock the context manager
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = (Mock(), Mock())
    mock_context.__aexit__.return_value = None
    mock_stdio_server.return_value = mock_context
    
    mock_server = Mock()
    mock_server.run = AsyncMock()
    mock_server.create_initialization_options = Mock()
    
    transport = StdioTransport()
    await transport.connect(mock_server)
    
    assert transport.server == mock_server


@pytest.mark.asyncio
async def test_stdio_transport_close():
    """Test StdioTransport close method"""
    transport = StdioTransport()
    mock_server = Mock()
    transport.server = mock_server
    
    # Should not raise an exception
    await transport.close()


@pytest.mark.asyncio
async def test_socket_transport_creation():
    """Test SocketTransport creation"""
    transport = SocketTransport(8080)
    assert transport.port == 8080
    assert transport.server is None


@pytest.mark.asyncio
async def test_socket_transport_connect():
    """Test SocketTransport connect method"""
    transport = SocketTransport(8080)
    mock_server = Mock()
    
    await transport.connect(mock_server)
    assert transport.server == mock_server


@pytest.mark.asyncio
async def test_socket_transport_close():
    """Test SocketTransport close method"""
    transport = SocketTransport(8080)
    
    # Should not raise an exception
    await transport.close()