"""
Tests for Claude client conversation management
"""
import pytest

from claude_client.conversation import ConversationManager


def test_conversation_manager_creation():
    """Test ConversationManager creation"""
    manager = ConversationManager()
    
    assert manager.get_message_count() == 0
    assert manager.max_messages == 50


def test_add_messages():
    """Test adding messages to conversation"""
    manager = ConversationManager()
    
    manager.add_user_message("Hello")
    manager.add_assistant_message("Hi there!")
    
    assert manager.get_message_count() == 2
    
    messages = manager.get_messages()
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"
    assert messages[1].role == "assistant"
    assert messages[1].content == "Hi there!"


def test_message_limit():
    """Test message limit enforcement"""
    manager = ConversationManager(max_messages=3)
    
    manager.add_user_message("Message 1")
    manager.add_assistant_message("Response 1")
    manager.add_user_message("Message 2")
    manager.add_assistant_message("Response 2")
    
    # Should only keep 3 messages (removes from middle)
    assert manager.get_message_count() == 3
    
    messages = manager.get_messages()
    assert messages[0].content == "Message 1"  # First kept
    assert messages[1].content == "Message 2"  # Second removed, third kept
    assert messages[2].content == "Response 2"  # Last kept


def test_clear():
    """Test clearing conversation"""
    manager = ConversationManager()
    
    manager.add_user_message("Hello")
    manager.add_assistant_message("Hi!")
    
    assert manager.get_message_count() == 2
    
    manager.clear()
    assert manager.get_message_count() == 0


def test_conversation_text():
    """Test getting conversation as text"""
    manager = ConversationManager()
    
    manager.add_user_message("Hello")
    manager.add_assistant_message("Hi there!")
    
    text = manager.get_conversation_text()
    expected = "USER: Hello\n\nASSISTANT: Hi there!"
    
    assert text == expected


def test_summarize():
    """Test conversation summarization"""
    manager = ConversationManager()
    
    # Add a long conversation
    long_content = "A" * 1000
    manager.add_user_message(long_content)
    manager.add_assistant_message("Response")
    
    summary = manager.summarize(max_length=100)
    
    assert len(summary) <= 200  # Should be around max_length with truncation message
    assert "[... conversation truncated ...]" in summary


def test_export_to_markdown():
    """Test exporting conversation to markdown"""
    manager = ConversationManager()
    
    manager.add_user_message("Hello")
    manager.add_assistant_message("Hi there!")
    
    markdown = manager.export_to_markdown()
    
    assert "# Conversation History" in markdown
    assert "## User" in markdown
    assert "## Assistant" in markdown
    assert "Hello" in markdown
    assert "Hi there!" in markdown


def test_import_from_markdown():
    """Test importing conversation from markdown"""
    manager = ConversationManager()
    
    markdown = """# Conversation History

## User

Hello Claude

## Assistant

Hi there! How can I help?

## User

Thanks!
"""
    
    manager.import_from_markdown(markdown)
    
    assert manager.get_message_count() == 3
    
    messages = manager.get_messages()
    assert messages[0].role == "user"
    assert messages[0].content == "Hello Claude"
    assert messages[1].role == "assistant"
    assert messages[1].content == "Hi there! How can I help?"
    assert messages[2].role == "user"
    assert messages[2].content == "Thanks!"