"""
Test to identify the storage format mismatch issue
The MemoryData model expects .md files but JSONFileBackend creates .json files
"""
import tempfile
import sys
from pathlib import Path
import pytest

# Add memry models to path  
sys.path.append(str(Path(__file__).parent.parent.parent / "servers" / "memry" / "src"))
from models.memory_models import MemoryData, CreateMemoryInput


class TestMemoryStorageFormatMismatch:
    """Test that identifies the storage format mismatch"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_memory_data_filename_property(self):
        """Test that MemoryData.filename returns .md extension"""
        # Arrange
        memory_data = MemoryData(
            id="test-123",
            title="Test Memory",
            content="Test content",
            source="test",
            tags=["test"]
        )
        
        # Act
        filename = memory_data.filename
        
        # Assert
        assert filename.endswith(".md"), f"Expected .md file, got {filename}"
        assert "test-memory" in filename.lower()
        
    def test_jsonfile_backend_creates_json_files(self):
        """Test that JSONFileBackend creates .json files"""
        from mcp_storage.backends.json_file import JSONFileBackend
        
        # Arrange
        backend = JSONFileBackend(self.storage_path, entity_type=MemoryData)
        memory_data = MemoryData(
            id="test-123",
            title="Test Memory", 
            content="Test content",
            source="test",
            tags=["test"]
        )
        
        # Act
        import asyncio
        asyncio.run(backend.create(memory_data))
        
        # Assert
        json_files = list(self.storage_path.glob("*.json"))
        md_files = list(self.storage_path.glob("*.md"))
        
        assert len(json_files) == 1, "JSONFileBackend should create .json files"
        assert len(md_files) == 0, "JSONFileBackend should not create .md files"
        assert json_files[0].name == "test-123.json"
        
    def test_format_mismatch_issue(self):
        """Test that demonstrates the format mismatch issue"""
        # This test demonstrates the core issue:
        # MemoryData.filename expects .md files but JSONFileBackend creates .json files
        
        memory_data = MemoryData(
            id="test-123",
            title="Test Memory",
            content="Test content", 
            source="test",
            tags=["test"]
        )
        
        expected_filename = memory_data.filename  # Returns .md file
        actual_json_filename = f"{memory_data.id}.json"  # JSONFileBackend creates this
        
        # This mismatch causes issues in the handler
        assert expected_filename != actual_json_filename
        assert expected_filename.endswith(".md")
        assert actual_json_filename.endswith(".json")
        
        print(f"Expected: {expected_filename}")
        print(f"Actual: {actual_json_filename}")
        print("❌ Format mismatch identified!")