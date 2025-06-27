#!/usr/bin/env python3
"""
Comprehensive TDD test suite for Apple Notes integration tools.

Following MCP Fleet TDD methodology:
1. Unit tests for AppleScript generation
2. Integration tests with mocked AppleScript execution
3. MCP tool schema validation
4. End-to-end tests with real Apple Notes app
5. Error handling and edge cases

This test suite establishes the contract before implementation.
"""
import pytest
import subprocess
import time
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add the server source to path for imports
server_root = Path(__file__).parent.parent
sys.path.insert(0, str(server_root))

try:
    from src.tools.apple_notes_tools import (
        create_note,
        list_notes,
        search_notes,
        update_note,
        delete_note,
        create_folder,
        list_folders,
        notes_tools,
        notes_handlers,
        generate_create_note_script,
        generate_list_notes_script,
        execute_applescript,
        validate_note_content
    )
    IMPLEMENTATION_AVAILABLE = True
except ImportError:
    # Expected for TDD - we'll implement these
    IMPLEMENTATION_AVAILABLE = False
    create_note = None
    list_notes = None
    search_notes = None
    update_note = None
    delete_note = None
    create_folder = None
    list_folders = None
    notes_tools = []
    notes_handlers = {}
    generate_create_note_script = None
    generate_list_notes_script = None
    execute_applescript = None
    validate_note_content = None


class TestAppleScriptGeneration:
    """Unit tests for AppleScript generation functions."""
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_generate_create_note_script_basic(self):
        """Test basic note creation AppleScript generation."""
        title = "Test Note"
        content = "This is a test note content."
        
        script = generate_create_note_script(title, content)
        
        # Verify script structure
        assert 'tell application "Notes"' in script
        assert 'make new note' in script
        assert 'Test Note' in script
        assert 'This is a test note content.' in script
        assert 'end tell' in script
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_generate_create_note_script_with_folder(self):
        """Test note creation with specific folder."""
        title = "Project Note"
        content = "Meeting notes from today"
        folder = "Work"
        
        script = generate_create_note_script(title, content, folder)
        
        assert 'folder "Work"' in script
        assert 'Project Note' in script
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_generate_create_note_script_escapes_quotes(self):
        """Test that quotes in content are properly escaped."""
        title = 'Note with "quotes"'
        content = 'Content with "nested quotes" and \'apostrophes\''
        
        script = generate_create_note_script(title, content)
        
        # Should not break AppleScript syntax
        assert 'tell application "Notes"' in script
        # Quotes should be escaped
        assert '\\"quotes\\"' in script or "quotes" not in script.split('"')[1::2]
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_generate_list_notes_script(self):
        """Test AppleScript generation for listing notes."""
        script = generate_list_notes_script()
        
        assert 'tell application "Notes"' in script
        assert 'get every note' in script or 'every note' in script
        assert 'name' in script
        assert 'end tell' in script
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_generate_list_notes_script_with_folder(self):
        """Test listing notes from specific folder."""
        folder = "Personal"
        script = generate_list_notes_script(folder)
        
        assert 'folder "Personal"' in script


class TestAppleScriptExecution:
    """Integration tests for AppleScript execution."""
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    @patch('subprocess.run')
    def test_execute_applescript_success(self, mock_run):
        """Test successful AppleScript execution."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success output",
            stderr=""
        )
        
        script = 'tell application "Notes" to get name of every note'
        result = execute_applescript(script)
        
        assert result['success'] is True
        assert result['output'] == "Success output"
        mock_run.assert_called_once_with(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30
        )
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    @patch('subprocess.run')
    def test_execute_applescript_failure(self, mock_run):
        """Test AppleScript execution failure handling."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="AppleScript error: syntax error"
        )
        
        script = 'invalid applescript'
        result = execute_applescript(script)
        
        assert result['success'] is False
        assert "syntax error" in result['error']
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    @patch('subprocess.run')
    def test_execute_applescript_timeout(self, mock_run):
        """Test AppleScript timeout handling."""
        mock_run.side_effect = subprocess.TimeoutExpired(
            ["osascript"], timeout=30
        )
        
        script = 'tell application "Notes" to wait for 60'
        result = execute_applescript(script)
        
        assert result['success'] is False
        assert "timeout" in result['error'].lower()


class TestNotesToolFunctions:
    """Integration tests for main tool functions."""
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    @patch('src.tools.apple_notes_tools.execute_applescript')
    def test_create_note_success(self, mock_execute):
        """Test successful note creation."""
        mock_execute.return_value = {
            'success': True,
            'output': 'note id "x-coredata://note-id-123"'
        }
        
        result = create_note(
            title="Test Note",
            content="Test content",
            folder="Work"
        )
        
        assert result['success'] is True
        assert result['title'] == "Test Note"
        assert result['folder'] == "Work"
        assert 'note_id' in result
        mock_execute.assert_called_once()
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    @patch('src.tools.apple_notes_tools.execute_applescript')
    def test_create_note_failure(self, mock_execute):
        """Test note creation failure handling."""
        mock_execute.return_value = {
            'success': False,
            'error': 'Notes app not available'
        }
        
        result = create_note("Test", "Content")
        
        assert result['success'] is False
        assert "Notes app not available" in result['error']
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    @patch('src.tools.apple_notes_tools.execute_applescript')
    def test_list_notes_success(self, mock_execute):
        """Test successful notes listing."""
        mock_execute.return_value = {
            'success': True,
            'output': 'Note 1, Note 2, Note 3'
        }
        
        result = list_notes()
        
        assert result['success'] is True
        assert isinstance(result['notes'], list)
        assert len(result['notes']) > 0
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_validate_note_content_valid(self):
        """Test note content validation for valid content."""
        title = "Valid Title"
        content = "Valid content with reasonable length."
        
        result = validate_note_content(title, content)
        
        assert result['valid'] is True
        assert 'error' not in result
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_validate_note_content_empty_title(self):
        """Test validation fails for empty title."""
        title = ""
        content = "Valid content"
        
        result = validate_note_content(title, content)
        
        assert result['valid'] is False
        assert "title" in result['error'].lower()
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_validate_note_content_too_long(self):
        """Test validation fails for extremely long content."""
        title = "Test"
        content = "x" * 100000  # Very long content
        
        result = validate_note_content(title, content)
        
        assert result['valid'] is False
        assert "long" in result['error'].lower()


class TestMCPToolDefinitions:
    """Test MCP tool schema definitions."""
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_notes_tools_schema_structure(self):
        """Test that all note tools have proper MCP schema."""
        expected_tools = [
            'create_note',
            'list_notes', 
            'search_notes',
            'create_folder',
            'list_folders'
        ]
        
        tool_names = [tool['name'] for tool in notes_tools]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
        
        # Validate schema structure for create_note
        create_note_tool = next(
            tool for tool in notes_tools 
            if tool['name'] == 'create_note'
        )
        
        assert 'description' in create_note_tool
        assert 'input_schema' in create_note_tool
        assert 'output_schema' in create_note_tool
        
        input_schema = create_note_tool['input_schema']
        assert input_schema['type'] == 'object'
        assert 'title' in input_schema['properties']
        assert 'content' in input_schema['properties']
        assert 'folder' in input_schema['properties']
        assert input_schema['required'] == ['title', 'content']
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_notes_handlers_registration(self):
        """Test that all handlers are properly registered."""
        expected_handlers = [
            'create_note',
            'list_notes',
            'search_notes', 
            'create_folder',
            'list_folders'
        ]
        
        for handler_name in expected_handlers:
            assert handler_name in notes_handlers
            assert callable(notes_handlers[handler_name])


@pytest.mark.e2e
class TestAppleNotesEndToEnd:
    """
    End-to-end tests that create REAL notes in Apple Notes app.
    
    Run with: pytest -m e2e -s tests/test_apple_notes_tools.py
    
    IMPORTANT: These tests will actually create notes in your Notes app!
    """
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_create_real_note_basic(self):
        """Create a real note and verify manually."""
        print("\\n" + "="*60)
        print("E2E TEST: Creating basic Apple Note")
        print("="*60)
        
        title = f"MCP Fleet Test Note - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        content = """This is a test note created by the MCP Fleet Local Server.

Features being tested:
- Basic note creation via AppleScript
- Title and content handling
- Native macOS integration

If you can see this note in your Apple Notes app, the integration is working!
        """
        
        result = create_note(title, content)
        
        print(f"Created note: {title}")
        print(f"Success: {result.get('success', False)}")
        print("\\nPLEASE VERIFY: Check your Apple Notes app for this note!")
        print("="*60)
        
        # Give user time to check
        input("\\nPress Enter after verifying the note was created...")
        
        assert result['success'] is True
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready") 
    def test_create_real_note_with_folder(self):
        """Create a note in a specific folder."""
        print("\\n" + "="*60)
        print("E2E TEST: Creating note in specific folder")
        print("="*60)
        
        title = f"Folder Test Note - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        content = "This note should be created in the 'MCP Fleet' folder."
        folder = "MCP Fleet"
        
        result = create_note(title, content, folder)
        
        print(f"Created note: {title}")
        print(f"Target folder: {folder}")
        print(f"Success: {result.get('success', False)}")
        print("\\nPLEASE VERIFY: Check the 'MCP Fleet' folder in Notes!")
        print("="*60)
        
        input("\\nPress Enter after verifying...")
        
        assert result['success'] is True
    
    @pytest.mark.skipif(not IMPLEMENTATION_AVAILABLE, reason="Implementation not ready")
    def test_list_real_notes(self):
        """List actual notes from Apple Notes."""
        print("\\n" + "="*60)
        print("E2E TEST: Listing notes from Apple Notes")
        print("="*60)
        
        result = list_notes()
        
        print(f"Success: {result.get('success', False)}")
        if result.get('success'):
            notes = result.get('notes', [])
            print(f"Found {len(notes)} notes")
            if notes:
                print("First few notes:")
                for i, note in enumerate(notes[:5]):
                    print(f"  {i+1}. {note}")
        
        print("="*60)
        input("\\nPress Enter to continue...")
        
        assert result['success'] is True


if __name__ == "__main__":
    print("Apple Notes Integration Test Suite")
    print("=" * 50)
    print("Run options:")
    print("1. All tests: pytest tests/test_apple_notes_tools.py")
    print("2. E2E tests: pytest -m e2e -s tests/test_apple_notes_tools.py")
    print("3. Unit tests: pytest -m 'not e2e' tests/test_apple_notes_tools.py")
    print("\\nNote: E2E tests will create real notes in your Apple Notes app!")