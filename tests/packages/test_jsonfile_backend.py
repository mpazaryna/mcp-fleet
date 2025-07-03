"""
Unit tests for JSONFileBackend storage implementation
Following strict TDD methodology
"""
import asyncio
import tempfile
import sys
from pathlib import Path
import pytest
from mcp_storage.backends.json_file import JSONFileBackend
from mcp_storage.entity import create_entity_storage

# Add memry models to path
sys.path.append(str(Path(__file__).parent.parent.parent / "servers" / "memry" / "src"))
from models.memory_models import MemoryData, CreateMemoryInput


class TestJSONFileBackend:
    """Test JSONFileBackend with MemoryData entities"""
    
    def setup_method(self):
        """Set up test environment with temporary storage"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_create_memory_with_jsonfile_backend(self):
        """Test creating a memory using JSONFileBackend - should complete successfully"""
        # Arrange
        backend = JSONFileBackend(self.storage_path, entity_type=MemoryData)
        memory_storage = create_entity_storage(
            entity_type=MemoryData,
            backend=backend,
            id_field="id"
        )
        
        memory_input = CreateMemoryInput(
            title="Test Memory",
            content="Test content",
            source="test",
            tags=["test"]
        )
        
        # Act - This should complete without hanging
        memory = await memory_storage.create(memory_input)
        
        # Assert
        assert memory is not None
        assert memory.title == "Test Memory"
        assert memory.content == "Test content"
        assert memory.source == "test"
        assert memory.tags == ["test"]
        assert hasattr(memory, 'id')
        assert hasattr(memory, 'filename')
        
        # Verify file was created
        json_files = list(self.storage_path.glob("*.json"))
        assert len(json_files) == 1
        
        json_file = json_files[0]
        assert json_file.name == f"{memory.id}.json"

    @pytest.mark.asyncio
    async def test_list_memories_with_jsonfile_backend(self):
        """Test listing memories using JSONFileBackend"""
        # Arrange
        backend = JSONFileBackend(self.storage_path, entity_type=MemoryData)
        memory_storage = create_entity_storage(
            entity_type=MemoryData,
            backend=backend,
            id_field="id"
        )
        
        # Create test memories
        memory1 = await memory_storage.create(CreateMemoryInput(
            title="Memory 1", content="Content 1", source="test", tags=["tag1"]
        ))
        memory2 = await memory_storage.create(CreateMemoryInput(
            title="Memory 2", content="Content 2", source="test", tags=["tag2"]
        ))
        
        # Act
        memories = await memory_storage.list()
        
        # Assert
        assert len(memories) == 2
        memory_titles = [m.title for m in memories]
        assert "Memory 1" in memory_titles
        assert "Memory 2" in memory_titles