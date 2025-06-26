"""
Tests for Claude client types
"""
import pytest
from pydantic import ValidationError

from claude_client.types import (
    ClaudeMessage, ClaudeConfig, ClaudeResponse, ClaudeContentBlock, ClaudeUsage
)


def test_claude_message_creation():
    """Test ClaudeMessage creation and validation"""
    message = ClaudeMessage(role="user", content="Hello, Claude!")
    
    assert message.role == "user"
    assert message.content == "Hello, Claude!"


def test_claude_message_validation():
    """Test ClaudeMessage validation"""
    with pytest.raises(ValidationError):
        ClaudeMessage(role="invalid", content="test")  # Invalid role


def test_claude_config_creation():
    """Test ClaudeConfig creation"""
    config = ClaudeConfig(
        api_key="test-key",
        model="claude-3-sonnet-20240229",
        max_retries=5
    )
    
    assert config.api_key == "test-key"
    assert config.model == "claude-3-sonnet-20240229"
    assert config.max_retries == 5


def test_claude_config_defaults():
    """Test ClaudeConfig with defaults"""
    config = ClaudeConfig()
    
    assert config.api_key is None
    assert config.base_url is None
    assert config.model is None


def test_claude_response_creation():
    """Test ClaudeResponse creation"""
    content_block = ClaudeContentBlock(type="text", text="Hello!")
    usage = ClaudeUsage(input_tokens=10, output_tokens=5)
    
    response = ClaudeResponse(
        id="msg_123",
        type="message",
        role="assistant",
        content=[content_block],
        model="claude-3-sonnet-20240229",
        stop_reason="end_turn",
        stop_sequence=None,
        usage=usage
    )
    
    assert response.id == "msg_123"
    assert len(response.content) == 1
    assert response.content[0].text == "Hello!"
    assert response.usage.input_tokens == 10