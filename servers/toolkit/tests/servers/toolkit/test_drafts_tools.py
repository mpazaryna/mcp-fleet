"""
Test suite for Drafts app integration tools.

This includes unit tests, integration tests, and end-to-end tests
that create real drafts in the Drafts app.
"""
import pytest
import urllib.parse
from unittest.mock import patch, MagicMock
import webbrowser
import time
from typing import List, Optional

# Import the tools we're testing (will fail initially - TDD!)
import sys
from pathlib import Path

# Add the servers directory to path
servers_path = Path(__file__).parent.parent.parent.parent / "servers"
sys.path.insert(0, str(servers_path))

# Use absolute path to drafts_tools
drafts_tools_path = Path("/Users/mpaz/workspace/mcp-fleet/servers/toolkit/src/tools/drafts_tools.py")

# Import drafts_tools directly to bypass __init__.py issues
import importlib.util
print(f"Looking for drafts_tools at: {drafts_tools_path}")
print(f"File exists: {drafts_tools_path.exists()}")

try:
    spec = importlib.util.spec_from_file_location("drafts_tools", drafts_tools_path)
    drafts_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(drafts_module)
    
    create_draft = drafts_module.create_draft
    create_draft_with_template = drafts_module.create_draft_with_template
    send_to_url_scheme = drafts_module.send_to_url_scheme
    draft_tools = drafts_module.draft_tools
    draft_handlers = drafts_module.draft_handlers
    encode_draft_params = drafts_module.encode_draft_params
    validate_draft_content = drafts_module.validate_draft_content
    print(f"Successfully imported drafts_tools directly from {drafts_tools_path}")
except Exception as e:
    print(f"Import failed: {e}")
    # Expected for TDD - we'll implement these
    create_draft = None
    create_draft_with_template = None
    send_to_url_scheme = None
    draft_tools = []
    draft_handlers = {}
    encode_draft_params = None
    validate_draft_content = None


# Tests now work since implementation is complete
class TestDraftsURLSchemeGeneration:
    """Unit tests for URL scheme generation."""
    
    def test_basic_draft_url_generation(self):
        """Test creating a basic draft URL."""
        content = "Hello, Drafts!"
        expected = "drafts://create?text=Hello%2C%20Drafts%21"
        
        url = encode_draft_params(content)
        assert url == expected
    
    def test_draft_with_tags(self):
        """Test creating a draft with tags."""
        content = "Meeting notes"
        tags = ["work", "meeting", "2024"]
        expected = "drafts://create?text=Meeting%20notes&tag=work&tag=meeting&tag=2024"
        
        url = encode_draft_params(content, tags=tags)
        assert url == expected
    
    def test_draft_with_action(self):
        """Test creating a draft with an action to run."""
        content = "Send to Obsidian"
        action = "Send to Obsidian"
        expected = "drafts://create?text=Send%20to%20Obsidian&action=Send%20to%20Obsidian"
        
        url = encode_draft_params(content, action=action)
        assert url == expected
    
    def test_draft_with_special_characters(self):
        """Test URL encoding of special characters."""
        content = "Test & verify: 100% working!\n#hashtag"
        url = encode_draft_params(content)
        
        # Verify URL is properly encoded
        assert "&" not in url.split("?")[1].replace("&tag=", "")
        assert ":" not in url.split("?")[1]
        assert "!" not in url.split("?")[1]
        assert "#" not in url.split("?")[1]
    
    def test_empty_content_raises_error(self):
        """Test that empty content raises an error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            encode_draft_params("")
    
    def test_invalid_tag_type(self):
        """Test that invalid tag types raise an error."""
        with pytest.raises(TypeError, match="Tags must be a list"):
            encode_draft_params("Test", tags="invalid")


# Tool definitions test
class TestDraftsToolDefinitions:
    """Test the MCP tool definitions."""
    
    def test_create_draft_tool_schema(self):
        """Test the create_draft tool has proper schema."""
        tool = next(t for t in draft_tools if t["name"] == "create_draft")
        
        assert tool["description"]
        assert "content" in tool["inputSchema"]["properties"]
        assert "tags" in tool["inputSchema"]["properties"]
        assert "action" in tool["inputSchema"]["properties"]
        assert tool["inputSchema"]["required"] == ["content"]
    
    def test_create_draft_with_template_tool_schema(self):
        """Test the template tool schema."""
        tool = next(t for t in draft_tools if t["name"] == "create_draft_with_template")
        
        assert tool["description"]
        assert "template_name" in tool["inputSchema"]["properties"]
        assert "variables" in tool["inputSchema"]["properties"]
        assert tool["inputSchema"]["required"] == ["template_name"]


# Handler tests
class TestDraftsHandlers:
    """Test the MCP tool handlers."""
    
    @patch('webbrowser.open')
    def test_create_draft_handler(self, mock_open):
        """Test the create_draft handler."""
        result = draft_handlers["create_draft"](
            content="Test draft",
            tags=["test", "mcp"],
            action=None
        )
        
        assert result["success"] is True
        assert "url" in result
        assert mock_open.called
        
        # Verify the URL structure
        called_url = mock_open.call_args[0][0]
        assert called_url.startswith("drafts://create?")
        assert "text=Test%20draft" in called_url
        assert "tag=test" in called_url
        assert "tag=mcp" in called_url
    
    @patch('webbrowser.open')
    def test_create_draft_with_template_handler(self, mock_open):
        """Test the template handler."""
        result = draft_handlers["create_draft_with_template"](
            template_name="meeting",
            variables={
                "title": "Team Standup",
                "date": "2024-12-27",
                "attendees": ["Alice", "Bob"]
            }
        )
        
        assert result["success"] is True
        assert mock_open.called
        
        # Verify template was processed
        called_url = mock_open.call_args[0][0]
        assert "Team%20Standup" in called_url
        assert "2024-12-27" in called_url


# Generic URL scheme tests
class TestGenericURLScheme:
    """Test the generic URL scheme functionality."""
    
    @patch('webbrowser.open')
    def test_send_to_url_scheme(self, mock_open):
        """Test generic URL scheme sending."""
        result = send_to_url_scheme(
            scheme="things",
            params={
                "add": "Buy milk",
                "when": "today"
            }
        )
        
        assert result["success"] is True
        mock_open.assert_called_once()
        
        called_url = mock_open.call_args[0][0]
        assert called_url.startswith("things://")
        assert "add=Buy%20milk" in called_url
        assert "when=today" in called_url


@pytest.mark.e2e
# E2E tests - will require manual verification
class TestDraftsEndToEnd:
    """
    End-to-end tests that create REAL drafts in the Drafts app.
    
    Run these with: pytest -m e2e -s tests/servers/toolkit/test_drafts_tools.py
    
    IMPORTANT: These tests will actually open your Drafts app and create notes!
    """
    
    def test_create_real_draft_basic(self):
        """Create a real draft and verify manually."""
        print("\n" + "="*60)
        print("E2E TEST: Creating basic draft")
        print("="*60)
        
        content = f"MCP Fleet Test Draft - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        result = create_draft(content)
        
        print(f"Created draft with content: {content}")
        print(f"URL: {result['url']}")
        print("\nPLEASE VERIFY: Check your Drafts app for this note!")
        print("="*60)
        
        # Give user time to check
        input("\nPress Enter after verifying the draft was created...")
        
        assert result["success"] is True
    
    def test_create_real_draft_with_tags(self):
        """Create a real draft with tags."""
        print("\n" + "="*60)
        print("E2E TEST: Creating draft with tags")
        print("="*60)
        
        content = f"Tagged Draft - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        tags = ["mcp-fleet", "test", "toolkit"]
        
        result = create_draft(content, tags=tags)
        
        print(f"Created draft: {content}")
        print(f"With tags: {', '.join(tags)}")
        print("\nPLEASE VERIFY: Check that the draft has all tags!")
        print("="*60)
        
        input("\nPress Enter after verifying the tags...")
        
        assert result["success"] is True
    
    @pytest.mark.skip(reason="Requires 'Send to Obsidian' action to be set up in Drafts")
    def test_create_real_draft_with_action(self):
        """Create a draft and run an action."""
        print("\n" + "="*60)
        print("E2E TEST: Creating draft with action")
        print("="*60)
        
        content = f"Action Test - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        action = "Send to Obsidian"  # This action must exist in your Drafts
        
        result = create_draft(content, action=action)
        
        print(f"Created draft: {content}")
        print(f"Running action: {action}")
        print("\nPLEASE VERIFY: Check that the action was executed!")
        print("="*60)
        
        input("\nPress Enter after verifying...")
        
        assert result["success"] is True
    
    def test_create_real_draft_from_template(self):
        """Create a draft from a template."""
        print("\n" + "="*60)
        print("E2E TEST: Creating draft from template")
        print("="*60)
        
        result = create_draft_with_template(
            template_name="daily_note",
            variables={
                "date": time.strftime('%Y-%m-%d'),
                "mood": "productive",
                "goals": ["Complete Drafts integration", "Test thoroughly", "Document well"]
            }
        )
        
        print("Created draft from 'daily_note' template")
        print("\nPLEASE VERIFY: Check the formatted template in Drafts!")
        print("="*60)
        
        input("\nPress Enter after verifying...")
        
        assert result["success"] is True


if __name__ == "__main__":
    # Run specific test categories
    print("Drafts Integration Test Suite")
    print("=============================")
    print("1. Run all tests: pytest tests/servers/toolkit/test_drafts_tools.py")
    print("2. Run E2E tests: pytest -m e2e -s tests/servers/toolkit/test_drafts_tools.py")
    print("3. Run unit tests only: pytest -m 'not e2e' tests/servers/toolkit/test_drafts_tools.py")