"""
Memory management tools for MCP-Memry
"""

import logging
import os
from pathlib import Path
from typing import Any

from core.types import MCPTool
from pydantic import BaseModel, Field
from storage.backends.json_file import JSONFileBackend
from storage.entity import create_entity_storage
from storage.utils import default_id_generator

from .memory_models import (
    CreateMemoryInput,
    MemoryData,
    MemoryFilter,
)

logger = logging.getLogger(__name__)

# Initialize storage
storage_path = Path(os.getenv("MEMRY_STORAGE_PATH", "~/Documents/memry")).expanduser()
storage_path.mkdir(parents=True, exist_ok=True)

# Create entity storage with JSON file backend
backend = JSONFileBackend(storage_path, entity_type=MemoryData)
memory_storage = create_entity_storage(
    entity_type=MemoryData,
    backend=backend,
    id_generator=default_id_generator,
    id_field="id",
)


# Schema definitions for tools
class CreateMemoryInputSchema(BaseModel):
    """Schema for creating a memory"""

    title: str = Field(description="Title of the memory")
    content: str = Field(description="Content of the memory")
    source: str = Field(
        description="Source of the memory (claude-desktop, claude-code, etc.)",
        default="claude-code",
    )
    tags: list[str] = Field(
        default_factory=list, description="List of tags for categorizing the memory"
    )
    topic_slug: str | None = Field(
        default=None,
        description="Optional topic slug for filename (auto-generated if not provided)",
    )


class CreateMemoryOutputSchema(BaseModel):
    """Schema for create memory output"""

    success: bool
    filename: str
    file_path: str
    title: str
    date: str
    tags: list[str]


class SearchMemoriesInputSchema(BaseModel):
    """Schema for searching memories"""

    date_from: str | None = Field(
        default=None, description="Start date for search (YYYY-MM-DD format)"
    )
    date_to: str | None = Field(
        default=None, description="End date for search (YYYY-MM-DD format)"
    )
    tags: list[str] | None = Field(
        default=None,
        description="Tags to filter by (will match memories with any of these tags)",
    )
    content_search: str | None = Field(
        default=None, description="Text to search for in memory content and titles"
    )
    source: str | None = Field(
        default=None, description="Filter by source of the memory"
    )
    limit: int | None = Field(default=None, description="Limit number of results")
    offset: int | None = Field(default=None, description="Offset for pagination")


class MemorySummarySchema(BaseModel):
    """Summary of a memory for search results"""

    id: str
    filename: str
    title: str
    date: str
    source: str
    tags: list[str]
    content_preview: str  # First 200 characters


class SearchMemoriesOutputSchema(BaseModel):
    """Schema for search memories output"""

    success: bool
    total_found: int
    memories: list[MemorySummarySchema]


class StatsOutputSchema(BaseModel):
    """Schema for memory statistics output"""

    success: bool
    total_memories: int
    sources: dict[str, int]
    tags: dict[str, int]
    dates: dict[str, int]
    storage_path: str


class EmptyInputSchema(BaseModel):
    """Empty schema for tools that don't require input"""

    pass


# Tool handlers
async def create_memory_handler(input_data: dict[str, Any]) -> dict[str, Any]:
    """Create a new memory"""
    try:
        # Parse input data into schema
        parsed_input = CreateMemoryInputSchema(**input_data)
        logger.info(f"💾 Creating memory: {parsed_input.title}")

        # Create memory input
        memory_input = CreateMemoryInput(
            title=parsed_input.title,
            content=parsed_input.content,
            source=parsed_input.source,
            tags=parsed_input.tags,
            topic_slug=parsed_input.topic_slug,
        )

        # Create memory using entity storage
        memory = await memory_storage.create(memory_input)

        result = CreateMemoryOutputSchema(
            success=True,
            filename=memory.filename,
            file_path=str(storage_path / f"{memory.id}.json"),
            title=memory.title,
            date=memory.date_slug,
            tags=memory.tags,
        )
        return result.model_dump()

    except Exception as e:
        logger.error(f"Error creating memory: {e}")
        result = CreateMemoryOutputSchema(
            success=False, filename="", file_path="", title="", date="", tags=[]
        )
        return result.model_dump()


async def search_memories_handler(input_data: dict[str, Any]) -> dict[str, Any]:
    """Search memories based on criteria"""
    try:
        # Parse input data into schema
        parsed_input = SearchMemoriesInputSchema(**input_data)
        logger.info(f"🔍 Searching memories with criteria: {parsed_input}")

        # Create search filter
        search_filter = MemoryFilter(
            date_from=parsed_input.date_from,
            date_to=parsed_input.date_to,
            tags=parsed_input.tags,
            content_search=parsed_input.content_search,
            source=parsed_input.source,
            limit=parsed_input.limit,
            offset=parsed_input.offset,
        )

        # Search memories using entity storage
        memories = await memory_storage.list(search_filter)

        # Create summaries
        memory_summaries = []
        for memory in memories:
            # Create content preview (first 200 chars)
            content_preview = memory.content[:200]
            if len(memory.content) > 200:
                content_preview += "..."

            memory_summaries.append(
                MemorySummarySchema(
                    id=memory.id,
                    filename=memory.filename,
                    title=memory.title,
                    date=memory.date_slug,
                    source=memory.source,
                    tags=memory.tags,
                    content_preview=content_preview,
                )
            )

        result = SearchMemoriesOutputSchema(
            success=True, total_found=len(memories), memories=memory_summaries
        )
        return result.model_dump()

    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        result = SearchMemoriesOutputSchema(success=False, total_found=0, memories=[])
        return result.model_dump()


async def list_all_memories_handler(input_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """List all memories"""
    try:
        logger.info("📋 Listing all memories")

        # Get all memories using entity storage
        memories = await memory_storage.list()

        # Create summaries
        memory_summaries = []
        for memory in memories:
            content_preview = memory.content[:200]
            if len(memory.content) > 200:
                content_preview += "..."

            memory_summaries.append(
                MemorySummarySchema(
                    id=memory.id,
                    filename=memory.filename,
                    title=memory.title,
                    date=memory.date_slug,
                    source=memory.source,
                    tags=memory.tags,
                    content_preview=content_preview,
                )
            )

        result = SearchMemoriesOutputSchema(
            success=True, total_found=len(memories), memories=memory_summaries
        )
        return result.model_dump()

    except Exception as e:
        logger.error(f"Error listing memories: {e}")
        result = SearchMemoriesOutputSchema(success=False, total_found=0, memories=[])
        return result.model_dump()


async def get_memory_stats_handler(input_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Get memory statistics"""
    try:
        logger.info("📊 Getting memory statistics")

        # Get all memories
        memories = await memory_storage.list()

        # Calculate statistics
        total_memories = len(memories)
        sources: dict[str, int] = {}
        tags: dict[str, int] = {}
        dates: dict[str, int] = {}

        for memory in memories:
            # Count sources
            sources[memory.source] = sources.get(memory.source, 0) + 1

            # Count tags
            for tag in memory.tags:
                tags[tag] = tags.get(tag, 0) + 1

            # Count dates
            date_key = memory.date_slug
            dates[date_key] = dates.get(date_key, 0) + 1

        result = StatsOutputSchema(
            success=True,
            total_memories=total_memories,
            sources=sources,
            tags=tags,
            dates=dates,
            storage_path=str(storage_path),
        )
        return result.model_dump()

    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        result = StatsOutputSchema(
            success=False,
            total_memories=0,
            sources={},
            tags={},
            dates={},
            storage_path="",
        )
        return result.model_dump()


# Tool definitions
memory_tools: list[MCPTool] = [
    MCPTool(
        name="create_memory",
        description="Create memory file with markdown content and YAML frontmatter",
        input_schema=CreateMemoryInputSchema.model_json_schema(),
        output_schema=CreateMemoryOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="search_memories",
        description="Search memories by date range, tags, or content",
        input_schema=SearchMemoriesInputSchema.model_json_schema(),
        output_schema=SearchMemoriesOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="list_all_memories",
        description="List all stored memories",
        input_schema=EmptyInputSchema.model_json_schema(),
        output_schema=SearchMemoriesOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="get_memory_stats",
        description="Get statistics about stored memories",
        input_schema=EmptyInputSchema.model_json_schema(),
        output_schema=StatsOutputSchema.model_json_schema(),
    ),
]


# Handler mapping
memory_handlers = {
    "create_memory": create_memory_handler,
    "search_memories": search_memories_handler,
    "list_all_memories": list_all_memories_handler,
    "get_memory_stats": get_memory_stats_handler,
}
