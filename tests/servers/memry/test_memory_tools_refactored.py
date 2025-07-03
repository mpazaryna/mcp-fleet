"""
Unit tests for refactored memory tools using shared storage
Following strict TDD methodology to identify the runtime issue
"""
import asyncio
import tempfile
import sys
from pathlib import Path
import pytest

# Add memry src to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "servers" / "memry" / "src"))
from tools.memory_tools import create_memory_handler


class TestRefactoredMemoryTools:
    """Test the refactored memory tools that use shared storage"""
    
    def setup_method(self):
        """Set up test environment with temporary storage"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        
        # Set the environment variable for storage path
        import os
        os.environ["MEMRY_STORAGE_PATH"] = str(self.storage_path)
        
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_create_memory_handler_completes(self):
        """Test that create_memory_handler completes without hanging"""
        # Arrange
        input_data = {
            "title": "Test Handler Memory",
            "content": "This tests the MCP handler directly",
            "source": "test-handler",
            "tags": ["test", "handler"]
        }
        
        # Act - This should complete without hanging
        result = await create_memory_handler(input_data)
        
        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success") == True
        assert "filename" in result
        assert result["title"] == "Test Handler Memory"
        
        # Verify file was created
        json_files = list(self.storage_path.glob("*.json"))
        assert len(json_files) == 1

    @pytest.mark.asyncio 
    async def test_create_memory_handler_error_handling(self):
        """Test error handling in create_memory_handler"""
        # Arrange - Invalid input (missing required fields)
        input_data = {
            "title": "",  # Empty title should cause error
            "content": "Test content"
            # Missing source
        }
        
        # Act
        result = await create_memory_handler(input_data)
        
        # Assert - Should handle error gracefully
        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success") == False