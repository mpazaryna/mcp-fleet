"""
Integration test for the fixed memory storage system
Tests that MemoryData works correctly with JSONFileBackend
"""
import tempfile
import sys
from pathlib import Path
import pytest

# Add memry models to path  
sys.path.append(str(Path(__file__).parent.parent.parent / "servers" / "memry" / "src"))
from models.memory_models import MemoryData, CreateMemoryInput
from mcp_storage.backends.json_file import JSONFileBackend
from mcp_storage.entity import create_entity_storage


class TestMemoryStorageIntegration:
    """Test the integrated memory storage solution"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_memory_creation_with_consistent_storage(self):
        """Test that memory creation works with consistent file naming"""
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
        
        # Act
        memory = await memory_storage.create(memory_input)
        
        # Assert
        assert memory is not None
        
        # The storage backend should create a file that matches what MemoryData expects
        created_files = list(self.storage_path.glob("*.json"))
        assert len(created_files) == 1
        
        created_file = created_files[0]
        # The file should be identifiable by the memory ID
        assert created_file.name == f"{memory.id}.json"
        
        # The memory should have properties that make sense for JSON storage
        assert hasattr(memory, 'id')
        assert hasattr(memory, 'title')
        assert hasattr(memory, 'content')
        
        # The filename property should work for the display/API purposes
        # but the actual storage uses the ID-based naming
        display_filename = memory.filename
        assert display_filename.endswith('.md')  # For display purposes
        
        print(f"✅ Created memory with ID: {memory.id}")
        print(f"✅ Storage file: {created_file.name}")
        print(f"✅ Display filename: {display_filename}")

    @pytest.mark.asyncio
    async def test_memory_retrieval_after_creation(self):
        """Test that memories can be retrieved after creation"""
        # Arrange
        backend = JSONFileBackend(self.storage_path, entity_type=MemoryData)
        memory_storage = create_entity_storage(
            entity_type=MemoryData,
            backend=backend,
            id_field="id"
        )
        
        # Create a memory
        memory_input = CreateMemoryInput(
            title="Retrievable Memory",
            content="This should be retrievable",
            source="test",
            tags=["retrievable"]
        )
        created_memory = await memory_storage.create(memory_input)
        
        # Act - Retrieve the memory
        retrieved_memory = await memory_storage.get(created_memory.id)
        
        # Assert
        assert retrieved_memory is not None
        assert retrieved_memory.id == created_memory.id
        assert retrieved_memory.title == "Retrievable Memory"
        assert retrieved_memory.content == "This should be retrievable"
        assert retrieved_memory.source == "test"
        assert retrieved_memory.tags == ["retrievable"]