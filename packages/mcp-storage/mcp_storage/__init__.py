"""
mcp_storage - Shared storage abstraction for MCP Fleet servers

Provides type-safe, async storage backends for entity persistence
with patterns extracted from the tides server implementation.
"""

from .entity import EntityStorage, create_entity_storage
from .backends.json_file import JSONFileBackend
from .config import StorageConfig
from .types import StorageBackend, EntityFilter

__all__ = [
    "EntityStorage",
    "create_entity_storage", 
    "JSONFileBackend",
    "StorageConfig",
    "StorageBackend",
    "EntityFilter",
]