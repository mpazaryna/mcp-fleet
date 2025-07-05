"""Test suite for yoga tools following TDD methodology."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os
from pathlib import Path

import sys
from pathlib import Path

# Add the yogateach server to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "servers" / "yogateach"))

from src.yoga_tools import (
    create_setlist,
    create_talk,
    CreateSetlistInputSchema,
    CreateTalkInputSchema,
    ContentCreationResult,
    yoga_tools,
    yoga_handlers,
)


class TestYogaTools:
    """Test cases for yoga tools functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def mock_template_engine(self):
        """Create a mock template engine."""
        mock = Mock()
        mock.load_template = AsyncMock()
        mock.render_and_save = AsyncMock()
        return mock

    @pytest.fixture
    def sample_setlist_args(self):
        """Sample arguments for setlist creation."""
        return {
            "name": "Morning Flow",
            "duration": 60,
            "level": "intermediate",
            "focus": "strength",
            "considerations": "No inversions due to neck injury",
            "theme": "Finding Balance"
        }

    @pytest.fixture
    def sample_talk_args(self):
        """Sample arguments for talk creation."""
        return {
            "name": "Mindful Living",
            "duration": 30,
            "topic": "mindfulness",
            "audience": "working professionals",
            "style": "contemporary",
            "message": "Being present in daily activities"
        }

    def test_create_setlist_input_schema_validation(self):
        """Test that CreateSetlistInputSchema validates input correctly."""
        valid_data = {
            "name": "Test Setlist",
            "duration": 45,
            "level": "beginner",
            "focus": "flexibility",
            "considerations": "Prenatal modifications needed"
        }
        
        schema = CreateSetlistInputSchema(**valid_data)
        assert schema.name == "Test Setlist"
        assert schema.duration == 45
        assert schema.level == "beginner"
        assert schema.focus == "flexibility"
        assert schema.considerations == "Prenatal modifications needed"
        assert schema.theme is None

    def test_create_talk_input_schema_validation(self):
        """Test that CreateTalkInputSchema validates input correctly."""
        valid_data = {
            "name": "Test Talk",
            "duration": 20,
            "topic": "compassion",
            "audience": "beginners",
            "style": "traditional",
            "message": "Loving-kindness starts with self"
        }
        
        schema = CreateTalkInputSchema(**valid_data)
        assert schema.name == "Test Talk"
        assert schema.duration == 20
        assert schema.topic == "compassion"
        assert schema.audience == "beginners"
        assert schema.style == "traditional"
        assert schema.message == "Loving-kindness starts with self"

    def test_content_creation_result_structure(self):
        """Test ContentCreationResult structure."""
        result = ContentCreationResult(
            success=True,
            content_id="test_123",
            name="Test Content",
            content_type="setlist",
            file_path="/path/to/file.md",
            created_at="2024-01-01T12:00:00"
        )
        
        assert result.success is True
        assert result.content_id == "test_123"
        assert result.name == "Test Content"
        assert result.content_type == "setlist"
        assert result.file_path == "/path/to/file.md"
        assert result.created_at == "2024-01-01T12:00:00"

    @pytest.mark.asyncio
    @patch('src.yoga_tools.template_engine')
    @patch('src.yoga_tools.storage')
    async def test_create_setlist_success(self, mock_storage, mock_template_engine, sample_setlist_args):
        """Test successful setlist creation."""
        # Mock template loading
        mock_template = Mock()
        mock_template.content = "Template content with ${name}"
        mock_template_engine.load_template.return_value = mock_template
        
        # Mock render and save
        mock_template_engine.render_and_save.return_value = Mock()
        
        # Call the function
        result = await create_setlist(sample_setlist_args)
        
        # Verify result
        assert isinstance(result, ContentCreationResult)
        assert result.success is True
        assert result.name == "Morning Flow"
        assert result.content_type == "setlist"
        assert result.content_id.startswith("setlist_")
        assert result.file_path.endswith(".md")
        
        # Verify template engine was called
        mock_template_engine.load_template.assert_called_once()
        mock_template_engine.render_and_save.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.yoga_tools.template_engine')
    @patch('src.yoga_tools.storage')
    async def test_create_talk_success(self, mock_storage, mock_template_engine, sample_talk_args):
        """Test successful talk creation."""
        # Mock template loading
        mock_template = Mock()
        mock_template.content = "Template content with ${name}"
        mock_template_engine.load_template.return_value = mock_template
        
        # Mock render and save
        mock_template_engine.render_and_save.return_value = Mock()
        
        # Call the function
        result = await create_talk(sample_talk_args)
        
        # Verify result
        assert isinstance(result, ContentCreationResult)
        assert result.success is True
        assert result.name == "Mindful Living"
        assert result.content_type == "talk"
        assert result.content_id.startswith("talk_")
        assert result.file_path.endswith(".md")
        
        # Verify template engine was called
        mock_template_engine.load_template.assert_called_once()
        mock_template_engine.render_and_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_setlist_invalid_input(self):
        """Test setlist creation with invalid input."""
        invalid_args = {
            "name": "Test",
            "duration": "invalid",  # Should be int
            "level": "beginner",
            "focus": "strength",
            "considerations": "None"
        }
        
        with pytest.raises(Exception):  # Should raise validation error
            await create_setlist(invalid_args)

    @pytest.mark.asyncio
    async def test_create_talk_invalid_input(self):
        """Test talk creation with invalid input."""
        invalid_args = {
            "name": "Test",
            "duration": 30,
            "topic": "mindfulness",
            "audience": "beginners",
            "style": "traditional"
            # Missing required 'message' field
        }
        
        with pytest.raises(Exception):  # Should raise validation error
            await create_talk(invalid_args)

    def test_yoga_tools_definition(self):
        """Test that yoga tools are properly defined."""
        assert len(yoga_tools) == 2
        
        # Check setlist tool
        setlist_tool = next(tool for tool in yoga_tools if tool["name"] == "create_setlist")
        assert setlist_tool["name"] == "create_setlist"
        assert "description" in setlist_tool
        assert "inputSchema" in setlist_tool
        
        # Check talk tool
        talk_tool = next(tool for tool in yoga_tools if tool["name"] == "create_talk")
        assert talk_tool["name"] == "create_talk"
        assert "description" in talk_tool
        assert "inputSchema" in talk_tool

    def test_yoga_handlers_definition(self):
        """Test that yoga handlers are properly defined."""
        assert len(yoga_handlers) == 2
        assert "create_setlist" in yoga_handlers
        assert "create_talk" in yoga_handlers
        assert callable(yoga_handlers["create_setlist"])
        assert callable(yoga_handlers["create_talk"])

    @pytest.mark.asyncio
    @patch('src.yoga_tools.template_engine')
    async def test_template_path_resolution(self, mock_template_engine):
        """Test that template paths are resolved correctly."""
        mock_template = Mock()
        mock_template.content = "Template content"
        mock_template_engine.load_template.return_value = mock_template
        mock_template_engine.render_and_save.return_value = Mock()
        
        # Test setlist template path
        args = {
            "name": "Test", "duration": 30, "level": "beginner",
            "focus": "flexibility", "considerations": "None"
        }
        
        await create_setlist(args)
        
        # Verify template path ends with setlist.md
        call_args = mock_template_engine.load_template.call_args[0]
        assert call_args[0].endswith("setlist.md")

    @pytest.mark.asyncio
    @patch('src.yoga_tools.template_engine')
    async def test_template_context_creation(self, mock_template_engine):
        """Test that template context is created correctly."""
        mock_template = Mock()
        mock_template.content = "Template content"
        mock_template_engine.load_template.return_value = mock_template
        mock_template_engine.render_and_save.return_value = Mock()
        
        args = {
            "name": "Test Setlist", "duration": 45, "level": "intermediate",
            "focus": "balance", "considerations": "No inversions", "theme": "Grounding"
        }
        
        await create_setlist(args)
        
        # Verify render_and_save was called with proper context
        render_call = mock_template_engine.render_and_save.call_args
        context = render_call[0][1]  # Second argument is the context
        
        assert context.variables["name"] == "Test Setlist"
        assert context.variables["duration"] == "45"
        assert context.variables["level"] == "intermediate"
        assert context.variables["focus"] == "balance"
        assert context.variables["considerations"] == "No inversions"
        assert context.variables["theme"] == "Grounding"