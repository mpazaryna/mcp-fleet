"""
storage - Shared storage abstraction for MCP Fleet servers

Provides type-safe, async storage backends for entity persistence
with patterns extracted from the tides server implementation.
"""

from .backends.json_file import JSONFileBackend
from .config import StorageConfig
from .entity import EntityStorage, create_entity_storage
from .types import EntityFilter, StorageBackend

__all__ = [
    "EntityStorage",
    "create_entity_storage",
    "JSONFileBackend",
    "StorageConfig",
    "StorageBackend",
    "EntityFilter",
]
