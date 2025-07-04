"""
Generic entity storage with type safety
"""

import logging
from collections.abc import Callable
from typing import Any, Generic

from pydantic import BaseModel

from .types import EntityFilter, EntityType, StorageBackend
from .utils import default_id_generator

logger = logging.getLogger(__name__)


class EntityStorage(Generic[EntityType]):
    """
    Generic entity storage with type safety

    Provides a high-level interface for entity CRUD operations
    with pluggable storage backends.
    """

    def __init__(
        self,
        entity_type: type[EntityType],
        storage_backend: StorageBackend[EntityType],
        id_generator: Callable[[], str] = default_id_generator,
        id_field: str = "id",
    ):
        """
        Initialize entity storage

        Args:
            entity_type: Pydantic model class for the entity
            storage_backend: Storage backend implementation
            id_generator: Function to generate new IDs
            id_field: Name of the ID field in the entity
        """
        self.entity_type = entity_type
        self.backend = storage_backend
        self.id_generator = id_generator
        self.id_field = id_field

    async def create(self, input_data: BaseModel) -> EntityType:
        """
        Create a new entity from input data

        Args:
            input_data: Pydantic model with entity creation data

        Returns:
            Created entity with generated ID and metadata
        """
        # Convert input data to dict
        entity_data = input_data.model_dump()

        # Generate ID if not provided
        if self.id_field not in entity_data or not entity_data[self.id_field]:
            entity_data[self.id_field] = self.id_generator()

        # Create entity instance
        entity = self.entity_type(**entity_data)

        # Save through backend
        return await self.backend.create(entity)

    async def get(self, entity_id: str) -> EntityType | None:
        """Get entity by ID"""
        return await self.backend.get(entity_id)

    async def list(self, filter_data: EntityFilter | None = None) -> list[EntityType]:
        """List entities with optional filtering"""
        return await self.backend.list(filter_data)

    async def update(
        self, entity_id: str, updates: dict[str, Any]
    ) -> EntityType | None:
        """Update entity with partial data"""
        return await self.backend.update(entity_id, updates)

    async def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        return await self.backend.delete(entity_id)

    async def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""
        return await self.backend.exists(entity_id)

    async def get_stats(self) -> dict[str, Any]:
        """Get basic statistics about stored entities"""
        entities = await self.list()
        return {
            "total_entities": len(entities),
            "entity_type": self.entity_type.__name__,
            "storage_backend": self.backend.__class__.__name__,
        }


def create_entity_storage(
    entity_type: type[EntityType],
    backend: StorageBackend[EntityType],
    id_generator: Callable[[], str] | None = None,
    id_field: str = "id",
) -> EntityStorage[EntityType]:
    """
    Factory function to create EntityStorage instances

    Args:
        entity_type: Pydantic model class for the entity
        backend: Storage backend implementation
        id_generator: Optional custom ID generator
        id_field: Name of the ID field in the entity

    Returns:
        Configured EntityStorage instance
    """
    generator = id_generator or default_id_generator
    return EntityStorage(
        entity_type=entity_type,
        storage_backend=backend,
        id_generator=generator,
        id_field=id_field,
    )
