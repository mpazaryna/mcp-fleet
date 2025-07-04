"""
JSON file-based storage backend for MCP storage
"""

import builtins
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from ..types import BaseEntity, EntityFilter, EntityType, StorageBackend

logger = logging.getLogger(__name__)


class JSONFileBackend(StorageBackend[EntityType], Generic[EntityType]):
    """
    JSON file-based storage backend

    Stores entities as individual JSON files in a directory.
    Uses entity ID as filename with .json extension.
    """

    def __init__(self, storage_path: Path, entity_type: type[EntityType]):
        """
        Initialize JSON file backend

        Args:
            storage_path: Directory path for storing JSON files
            entity_type: Entity type for validation and deserialization
        """
        self.storage_path = Path(storage_path)
        self.entity_type = entity_type
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, entity_id: str) -> Path:
        """Get file path for entity ID"""
        return self.storage_path / f"{entity_id}.json"

    async def create(self, entity: EntityType) -> EntityType:
        """Create new entity and save to JSON file"""
        try:
            file_path = self._get_file_path(entity.id)

            # Check if file already exists
            if file_path.exists():
                raise ValueError(f"Entity with ID {entity.id} already exists")

            # Save entity to JSON file
            entity_data = entity.model_dump()
            with open(file_path, "w") as f:
                json.dump(entity_data, f, indent=2)

            logger.debug(f"Created entity {entity.id} at {file_path}")
            return entity

        except Exception as e:
            logger.error(f"Error creating entity {entity.id}: {e}")
            raise

    async def get(self, entity_id: str) -> EntityType | None:
        """Get entity by ID from JSON file"""
        try:
            file_path = self._get_file_path(entity_id)

            if not file_path.exists():
                return None

            with open(file_path) as f:
                entity_data = json.load(f)

            # Create entity instance using the entity type
            return self.entity_type(**entity_data)

        except Exception as e:
            logger.error(f"Error loading entity {entity_id}: {e}")
            return None

    async def list(self, filter_data: EntityFilter | None = None) -> list[EntityType]:
        """List entities from JSON files with optional filtering"""
        try:
            entities = []

            # Load all JSON files
            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path) as f:
                        entity_data = json.load(f)

                    # Create entity instance
                    entity = self.entity_type(**entity_data)

                    entities.append(entity)

                except Exception as e:
                    logger.warning(f"Error loading entity from {file_path}: {e}")
                    continue

            # Apply filtering if provided
            if filter_data:
                entities = self._apply_filter(entities, filter_data)

            return entities

        except Exception as e:
            logger.error(f"Error listing entities: {e}")
            return []

    def _apply_filter(
        self, entities: builtins.list[EntityType], filter_data: EntityFilter
    ) -> builtins.list[EntityType]:
        """Apply filtering to entity list"""
        filtered = entities

        # Apply custom filtering based on filter type
        if hasattr(filter_data, "date_from") and filter_data.date_from:
            filtered = [
                e for e in filtered if self._match_date_from(e, filter_data.date_from)
            ]

        if hasattr(filter_data, "date_to") and filter_data.date_to:
            filtered = [
                e for e in filtered if self._match_date_to(e, filter_data.date_to)
            ]

        if hasattr(filter_data, "tags") and filter_data.tags:
            filtered = [e for e in filtered if self._match_tags(e, filter_data.tags)]

        if hasattr(filter_data, "content_search") and filter_data.content_search:
            filtered = [
                e
                for e in filtered
                if self._match_content_search(e, filter_data.content_search)
            ]

        if hasattr(filter_data, "source") and filter_data.source:
            filtered = [
                e for e in filtered if self._match_source(e, filter_data.source)
            ]

        # Apply pagination
        if filter_data.offset:
            filtered = filtered[filter_data.offset :]

        if filter_data.limit:
            filtered = filtered[: filter_data.limit]

        return filtered

    def _match_date_from(self, entity: EntityType, date_from: str) -> bool:
        """Check if entity date is >= date_from"""
        try:
            if hasattr(entity, "date_slug"):
                date_slug = getattr(entity, "date_slug", "")
                return bool(date_slug >= date_from)
            elif hasattr(entity, "created_at"):
                created_at = getattr(entity, "created_at", "")
                entity_date = created_at.split("T")[0]  # Extract date part
                return bool(entity_date >= date_from)
        except Exception:
            pass
        return True

    def _match_date_to(self, entity: EntityType, date_to: str) -> bool:
        """Check if entity date is <= date_to"""
        try:
            if hasattr(entity, "date_slug"):
                date_slug = getattr(entity, "date_slug", "")
                return bool(date_slug <= date_to)
            elif hasattr(entity, "created_at"):
                created_at = getattr(entity, "created_at", "")
                entity_date = created_at.split("T")[0]  # Extract date part
                return bool(entity_date <= date_to)
        except Exception:
            pass
        return True

    def _match_tags(self, entity: EntityType, tags: builtins.list[str]) -> bool:
        """Check if entity has any of the specified tags"""
        try:
            if hasattr(entity, "tags") and entity.tags:
                return any(tag in entity.tags for tag in tags)
        except Exception:
            pass
        return False

    def _match_content_search(self, entity: EntityType, search_term: str) -> bool:
        """Check if entity content or title contains search term"""
        try:
            search_lower = search_term.lower()

            # Check title
            if hasattr(entity, "title") and entity.title:
                if search_lower in entity.title.lower():
                    return True

            # Check content
            if hasattr(entity, "content") and entity.content:
                if search_lower in entity.content.lower():
                    return True

        except Exception:
            pass
        return False

    def _match_source(self, entity: EntityType, source: str) -> bool:
        """Check if entity source matches"""
        try:
            if hasattr(entity, "source"):
                entity_source = getattr(entity, "source", "")
                return bool(entity_source == source)
        except Exception:
            pass
        return False

    async def update(
        self, entity_id: str, updates: dict[str, Any]
    ) -> EntityType | None:
        """Update entity with partial data"""
        try:
            # Get existing entity
            entity = await self.get(entity_id)
            if not entity:
                return None

            # Apply updates
            entity_data = entity.model_dump()
            entity_data.update(updates)

            # Update timestamp if available
            if "updated_at" in entity_data:
                entity_data["updated_at"] = datetime.now().isoformat()

            # Create updated entity
            updated_entity = self.entity_type(**entity_data)

            # Save to file
            file_path = self._get_file_path(entity_id)
            with open(file_path, "w") as f:
                json.dump(entity_data, f, indent=2)

            logger.debug(f"Updated entity {entity_id}")
            return updated_entity

        except Exception as e:
            logger.error(f"Error updating entity {entity_id}: {e}")
            return None

    async def delete(self, entity_id: str) -> bool:
        """Delete entity JSON file"""
        try:
            file_path = self._get_file_path(entity_id)

            if not file_path.exists():
                return False

            file_path.unlink()
            logger.debug(f"Deleted entity {entity_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting entity {entity_id}: {e}")
            return False

    async def exists(self, entity_id: str) -> bool:
        """Check if entity JSON file exists"""
        file_path = self._get_file_path(entity_id)
        return file_path.exists()
