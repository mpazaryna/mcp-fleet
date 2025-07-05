"""Test suite for template engine following TDD methodology."""

import pytest
from tempfile import NamedTemporaryFile
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from templates import TemplateEngine, TemplateContext, TemplateResult


class TestTemplateEngine:
    """Test cases for the TemplateEngine class."""

    @pytest.fixture
    def engine(self):
        """Create a TemplateEngine instance for testing."""
        return TemplateEngine()

    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage backend."""
        mock = Mock()
        mock.read_file = AsyncMock()
        mock.write_file = AsyncMock()
        return mock

    @pytest.fixture
    def sample_template_content(self):
        """Sample template content for testing."""
        return """# ${title}

Duration: ${duration} minutes
Level: ${level}

## Instructions
${instructions}

## Notes
${notes}"""

    def test_template_engine_initialization(self, engine):
        """Test that TemplateEngine can be initialized."""
        assert engine is not None
        assert isinstance(engine, TemplateEngine)

    @pytest.mark.asyncio
    async def test_load_template_from_file(self, engine, sample_template_content):
        """Test loading a template from a file."""
        # Create a temporary file with template content
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
            tmp_file.write(sample_template_content)
            tmp_file_path = tmp_file.name

        try:
            # Load template from file
            template = await engine.load_template(tmp_file_path)
            
            assert template is not None
            assert template.content == sample_template_content
            assert template.path == tmp_file_path
            assert template.variables == {"title", "duration", "level", "instructions", "notes"}
        finally:
            # Clean up
            Path(tmp_file_path).unlink()

    @pytest.mark.asyncio
    async def test_load_template_from_string(self, engine, sample_template_content):
        """Test loading a template from a string."""
        template = await engine.load_template_from_string(sample_template_content)
        
        assert template is not None
        assert template.content == sample_template_content
        assert template.path is None
        assert template.variables == {"title", "duration", "level", "instructions", "notes"}

    def test_extract_variables_from_template(self, engine):
        """Test extracting variables from template content."""
        content = "Hello ${name}, you have ${count} messages. ${name} is great!"
        variables = engine.extract_variables(content)
        
        assert variables == {"name", "count"}

    def test_extract_variables_no_variables(self, engine):
        """Test extracting variables from content with no variables."""
        content = "This is a plain text without any variables."
        variables = engine.extract_variables(content)
        
        assert variables == set()

    def test_extract_variables_edge_cases(self, engine):
        """Test extracting variables handles edge cases."""
        # Test with special characters
        content = "${var_with_underscores} and ${var-with-dashes} and ${var123}"
        variables = engine.extract_variables(content)
        
        assert "var_with_underscores" in variables
        assert "var-with-dashes" in variables
        assert "var123" in variables

    def test_render_template_basic(self, engine):
        """Test basic template rendering."""
        template_content = "Hello ${name}, you are ${age} years old."
        context = TemplateContext({"name": "Alice", "age": "30"})
        
        result = engine.render(template_content, context)
        
        assert result.content == "Hello Alice, you are 30 years old."
        assert result.variables_used == {"name", "age"}
        assert result.missing_variables == set()

    def test_render_template_missing_variables(self, engine):
        """Test template rendering with missing variables."""
        template_content = "Hello ${name}, you are ${age} years old. Location: ${location}"
        context = TemplateContext({"name": "Alice", "age": "30"})
        
        result = engine.render(template_content, context)
        
        assert result.content == "Hello Alice, you are 30 years old. Location: ${location}"
        assert result.variables_used == {"name", "age"}
        assert result.missing_variables == {"location"}

    def test_render_template_extra_variables(self, engine):
        """Test template rendering with extra variables in context."""
        template_content = "Hello ${name}!"
        context = TemplateContext({"name": "Alice", "age": "30", "location": "NYC"})
        
        result = engine.render(template_content, context)
        
        assert result.content == "Hello Alice!"
        assert result.variables_used == {"name"}
        assert result.missing_variables == set()

    def test_render_template_empty_context(self, engine):
        """Test template rendering with empty context."""
        template_content = "Hello ${name}, you are ${age} years old."
        context = TemplateContext({})
        
        result = engine.render(template_content, context)
        
        assert result.content == "Hello ${name}, you are ${age} years old."
        assert result.variables_used == set()
        assert result.missing_variables == {"name", "age"}

    @pytest.mark.asyncio
    async def test_render_and_save_template(self, engine, mock_storage):
        """Test rendering and saving a template."""
        template_content = "Hello ${name}!"
        context = TemplateContext({"name": "Alice"})
        output_path = "/tmp/output.md"
        
        # Mock the storage write operation
        mock_storage.write_file.return_value = None
        
        result = await engine.render_and_save(
            template_content, context, output_path, mock_storage
        )
        
        assert result.content == "Hello Alice!"
        mock_storage.write_file.assert_called_once_with(output_path, "Hello Alice!")

    def test_template_context_validation(self):
        """Test TemplateContext validation."""
        # Valid context
        context = TemplateContext({"name": "Alice", "age": "30"})
        assert context.variables == {"name": "Alice", "age": "30"}
        
        # Empty context
        context = TemplateContext({})
        assert context.variables == {}

    def test_template_result_properties(self):
        """Test TemplateResult properties."""
        result = TemplateResult(
            content="Hello Alice!",
            variables_used={"name"},
            missing_variables={"age"},
            original_template="Hello ${name}! Age: ${age}"
        )
        
        assert result.content == "Hello Alice!"
        assert result.variables_used == {"name"}
        assert result.missing_variables == {"age"}
        assert result.original_template == "Hello ${name}! Age: ${age}"
        assert result.is_complete is False  # Has missing variables
        
        # Test complete template
        complete_result = TemplateResult(
            content="Hello Alice!",
            variables_used={"name"},
            missing_variables=set(),
            original_template="Hello ${name}!"
        )
        assert complete_result.is_complete is True