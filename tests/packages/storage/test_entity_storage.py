"""
Tests for storage package entity storage functionality
"""
import pytest
import pytest_asyncio
import sys
from pathlib import Path
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Add packages to path for testing
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir / "packages"))

from storage.entity import EntityStorage, create_entity_storage
from storage.backends.json_file import JSONFileBackend
from storage.config import StorageConfig
from storage.types import EntityFilter


# Test entity model - Rename to avoid pytest collection warning  
class SampleEntity(BaseModel):
    id: str
    name: str
    value: int
    created_at: str  # Store as ISO string
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create_with_timestamp(cls, id: str, name: str, value: int, metadata: Optional[Dict[str, Any]] = None):
        """Create entity with current timestamp"""
        return cls(
            id=id,
            name=name,
            value=value,
            created_at=datetime.now().isoformat(),
            metadata=metadata
        )


class TestEntityStorage:
    """Test EntityStorage with a simple test entity"""
    
    @pytest_asyncio.fixture
    async def storage(self):
        """Create a temporary storage instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONFileBackend(
                storage_path=Path(tmpdir),
                entity_type=SampleEntity
            )
            storage = create_entity_storage(
                entity_type=SampleEntity,
                backend=backend
            )
            yield storage
    
    @pytest.mark.asyncio
    async def test_create_entity(self, storage):
        """Test creating an entity"""
        entity = SampleEntity.create_with_timestamp(
            id="test-1",
            name="Test Entity",
            value=42,
            metadata={"key": "value"}
        )
        
        created = await storage.create(entity)
        assert created.id == "test-1"
        assert created.name == "Test Entity"
        assert created.value == 42
        assert created.metadata == {"key": "value"}
    
    @pytest.mark.asyncio
    async def test_get_entity(self, storage):
        """Test retrieving an entity"""
        entity = SampleEntity.create_with_timestamp(
            id="test-2",
            name="Get Test",
            value=100
        )
        
        await storage.create(entity)
        retrieved = await storage.get("test-2")
        
        assert retrieved is not None
        assert retrieved.id == "test-2"
        assert retrieved.name == "Get Test"
        assert retrieved.value == 100
    
    @pytest.mark.asyncio
    async def test_list_entities(self, storage):
        """Test listing entities"""
        # Create multiple entities
        for i in range(3):
            entity = SampleEntity.create_with_timestamp(
                id=f"list-test-{i}",
                name=f"Entity {i}",
                value=i * 10
            )
            await storage.create(entity)
        
        # List all
        entities = await storage.list()
        assert len(entities) == 3
        
        # Verify all entities are returned (order not guaranteed)
        entity_ids = {e.id for e in entities}
        assert entity_ids == {"list-test-0", "list-test-1", "list-test-2"}
    
    @pytest.mark.asyncio
    async def test_update_entity(self, storage):
        """Test updating an entity"""
        entity = SampleEntity.create_with_timestamp(
            id="update-test",
            name="Original Name",
            value=50
        )
        
        await storage.create(entity)
        
        # Update the entity
        updates = {
            "name": "Updated Name",
            "value": 75
        }
        
        updated = await storage.update("update-test", updates)
        assert updated.name == "Updated Name"
        assert updated.value == 75
        
        # Verify persistence
        retrieved = await storage.get("update-test")
        assert retrieved.name == "Updated Name"
        assert retrieved.value == 75
    
    @pytest.mark.asyncio
    async def test_delete_entity(self, storage):
        """Test deleting an entity"""
        entity = SampleEntity.create_with_timestamp(
            id="delete-test",
            name="To Delete",
            value=999
        )
        
        await storage.create(entity)
        
        # Verify it exists
        assert await storage.get("delete-test") is not None
        
        # Delete it
        await storage.delete("delete-test")
        
        # Verify it's gone
        assert await storage.get("delete-test") is None
    
    @pytest.mark.asyncio
    async def test_entity_not_found(self, storage):
        """Test getting non-existent entity returns None"""
        result = await storage.get("non-existent")
        assert result is None


def test_create_entity_storage():
    """Test the create_entity_storage factory function"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = JSONFileBackend(
            storage_path=Path(tmpdir),
            entity_type=SampleEntity
        )
        
        storage = create_entity_storage(
            entity_type=SampleEntity,
            backend=backend
        )
        assert isinstance(storage, EntityStorage)
        assert isinstance(storage.backend, JSONFileBackend)
        assert storage.entity_type == SampleEntity