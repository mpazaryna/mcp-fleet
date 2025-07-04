"""
Core types and interfaces for MCP storage abstraction
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    """Base entity class with required ID field"""
    
    id: str = Field(description="Unique entity identifier")


# Generic type for entities with ID field
EntityType = TypeVar("EntityType", bound=BaseEntity)


class EntityFilter(BaseModel):
    """Base class for entity filtering"""

    limit: int | None = None
    offset: int | None = None


class StorageBackend(ABC, Generic[EntityType]):
    """Abstract storage backend interface"""

    @abstractmethod
    async def create(self, entity: EntityType) -> EntityType:
        """Create new entity and return the created entity with any generated fields"""

    @abstractmethod
    async def get(self, entity_id: str) -> EntityType | None:
        """Get entity by ID, returns None if not found"""

    @abstractmethod
    async def list(self, filter_data: EntityFilter | None = None) -> list[EntityType]:
        """List entities with optional filtering"""

    @abstractmethod
    async def update(
        self, entity_id: str, updates: dict[str, Any]
    ) -> EntityType | None:
        """Update entity with partial data, returns updated entity or None if not found"""

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity, returns True if deleted, False if not found"""

    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""
