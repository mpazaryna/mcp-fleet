"""
Core types and interfaces for MCP storage abstraction
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel

# Generic type for entities
EntityType = TypeVar("EntityType", bound=BaseModel)


class EntityFilter(BaseModel):
    """Base class for entity filtering"""
    limit: Optional[int] = None
    offset: Optional[int] = None


class StorageBackend(ABC, Generic[EntityType]):
    """Abstract storage backend interface"""

    @abstractmethod
    async def create(self, entity: EntityType) -> EntityType:
        """Create new entity and return the created entity with any generated fields"""

    @abstractmethod
    async def get(self, entity_id: str) -> Optional[EntityType]:
        """Get entity by ID, returns None if not found"""

    @abstractmethod
    async def list(self, filter_data: Optional[EntityFilter] = None) -> List[EntityType]:
        """List entities with optional filtering"""

    @abstractmethod
    async def update(self, entity_id: str, updates: Dict[str, Any]) -> Optional[EntityType]:
        """Update entity with partial data, returns updated entity or None if not found"""

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity, returns True if deleted, False if not found"""

    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""