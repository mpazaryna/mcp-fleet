"""
Tests for Claude client
"""
import pytest
from unittest.mock import AsyncMock, patch, Mock
import os

from claude_client.client import ClaudeClient
from claude_client.types import ClaudeConfig, ClaudeMessage, ClaudeResponse, ClaudeContentBlock, ClaudeUsage


@pytest.fixture
def sample_response_data():
    """Sample Claude API response data"""
    return {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Hello there!"}],
        "model": "claude-3-sonnet-20240229",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 10, "output_tokens": 5}
    }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client"""
    with patch('claude_client.client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        yield mock_client


def test_claude_client_creation():
    """Test ClaudeClient creation"""
    config = ClaudeConfig(api_key="test-key")
    
    with patch('claude_client.client.httpx.AsyncClient'):
        client = ClaudeClient(config)
        
        assert client.api_key == "test-key"
        assert client.model == "claude-3-5-sonnet-20241022"


def test_claude_client_env_api_key():
    """Test ClaudeClient using environment variable for API key"""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key"}):
        with patch('claude_client.client.httpx.AsyncClient'):
            client = ClaudeClient()
            assert client.api_key == "env-key"


def test_claude_client_missing_api_key():
    """Test ClaudeClient raises error when API key is missing"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            ClaudeClient()


@pytest.mark.asyncio
async def test_chat_success(mock_httpx_client, sample_response_data):
    """Test successful chat request"""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_response_data
    mock_httpx_client.post.return_value = mock_response
    
    config = ClaudeConfig(api_key="test-key")
    client = ClaudeClient(config)
    
    messages = [ClaudeMessage(role="user", content="Hello")]
    result = await client.chat(messages)
    
    assert result == "Hello there!"
    mock_httpx_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_chat_with_response(mock_httpx_client, sample_response_data):
    """Test chat request returning full response"""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_response_data
    mock_httpx_client.post.return_value = mock_response
    
    config = ClaudeConfig(api_key="test-key")
    client = ClaudeClient(config)
    
    messages = [ClaudeMessage(role="user", content="Hello")]
    result = await client.chat_with_response(messages)
    
    assert isinstance(result, ClaudeResponse)
    assert result.id == "msg_123"
    assert result.content[0].text == "Hello there!"


@pytest.mark.asyncio
async def test_chat_with_system_prompt(mock_httpx_client, sample_response_data):
    """Test chat request with system prompt"""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_response_data
    mock_httpx_client.post.return_value = mock_response
    
    config = ClaudeConfig(api_key="test-key")
    client = ClaudeClient(config)
    
    messages = [ClaudeMessage(role="user", content="Hello")]
    await client.chat(messages, system_prompt="You are helpful")
    
    # Verify system prompt was included in request
    call_args = mock_httpx_client.post.call_args
    request_data = call_args[1]["json"]
    assert request_data["system"] == "You are helpful"


@pytest.mark.asyncio
async def test_chat_error_response(mock_httpx_client):
    """Test chat request with error response"""
    # Setup mock error response
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "error": {"type": "invalid_request", "message": "Invalid request"}
    }
    mock_response.text = "Bad Request"
    mock_httpx_client.post.return_value = mock_response
    
    config = ClaudeConfig(api_key="test-key")
    client = ClaudeClient(config)
    
    messages = [ClaudeMessage(role="user", content="Hello")]
    
    with pytest.raises(Exception, match="Claude API error \\(400\\)"):
        await client.chat(messages)


@pytest.mark.asyncio
async def test_rate_limit_retry(mock_httpx_client, sample_response_data):
    """Test retry logic for rate limiting"""
    config = ClaudeConfig(api_key="test-key", max_retries=2, retry_delay=10)
    client = ClaudeClient(config)
    
    # Setup mock responses: first call rate limited, second succeeds
    rate_limit_response = Mock()
    rate_limit_response.status_code = 429
    rate_limit_response.headers = {"retry-after": "1"}
    rate_limit_response.json.return_value = {
        "error": {"type": "rate_limit", "message": "Rate limited"}
    }
    
    success_response = Mock()
    success_response.status_code = 200
    success_response.json.return_value = sample_response_data
    
    mock_httpx_client.post.side_effect = [rate_limit_response, success_response]
    
    messages = [ClaudeMessage(role="user", content="Hello")]
    
    with patch('asyncio.sleep') as mock_sleep:
        result = await client.chat(messages)
        
        assert result == "Hello there!"
        assert mock_httpx_client.post.call_count == 2
        mock_sleep.assert_called_once()


def test_update_model():
    """Test updating model"""
    config = ClaudeConfig(api_key="test-key")
    
    with patch('claude_client.client.httpx.AsyncClient'):
        client = ClaudeClient(config)
        
        client.update_model("claude-3-haiku-20240307")
        assert client.get_model() == "claude-3-haiku-20240307"


@pytest.mark.asyncio
async def test_close():
    """Test closing client"""
    config = ClaudeConfig(api_key="test-key")
    
    with patch('claude_client.client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        client = ClaudeClient(config)
        await client.close()
        
        mock_client.aclose.assert_called_once()