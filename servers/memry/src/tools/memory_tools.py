"""
Memory management tools for MCP-Memry
"""

import logging
import os

from mcp_core.types import MCPTool
from pydantic import BaseModel, Field

from ..storage.memory_storage import (
    CreateMemoryInput,
    MemoryStorage,
    SearchFilter,
)

logger = logging.getLogger(__name__)

# Initialize storage

storage_path = os.getenv("MEMRY_STORAGE_PATH", "~/Documents/memry")
memory_storage = MemoryStorage(storage_path)


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


class MemorySummary(BaseModel):
    """Summary of a memory for search results"""

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
    memories: list[MemorySummary]


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
async def create_memory_handler(
    input_data: CreateMemoryInputSchema,
) -> CreateMemoryOutputSchema:
    """Create a new memory"""
    try:
        logger.info(f"💾 Creating memory: {input_data.title}")

        # Create memory input
        memory_input = CreateMemoryInput(
            title=input_data.title,
            content=input_data.content,
            source=input_data.source,
            tags=input_data.tags,
            topic_slug=input_data.topic_slug,
        )

        # Create memory
        memory = memory_storage.create_memory(memory_input)

        return CreateMemoryOutputSchema(
            success=True,
            filename=memory.filename,
            file_path=memory.file_path,
            title=memory.metadata.title,
            date=memory.metadata.date,
            tags=memory.metadata.tags,
        )

    except Exception as e:
        logger.error(f"Error creating memory: {e}")
        return CreateMemoryOutputSchema(
            success=False, filename="", file_path="", title="", date="", tags=[]
        )


async def search_memories_handler(
    input_data: SearchMemoriesInputSchema,
) -> SearchMemoriesOutputSchema:
    """Search memories based on criteria"""
    try:
        logger.info(f"🔍 Searching memories with criteria: {input_data}")

        # Create search filter
        search_filter = SearchFilter(
            date_from=input_data.date_from,
            date_to=input_data.date_to,
            tags=input_data.tags,
            content_search=input_data.content_search,
        )

        # Search memories
        memories = memory_storage.search_memories(search_filter)

        # Create summaries
        memory_summaries = []
        for memory in memories:
            # Create content preview (first 200 chars)
            content_preview = memory.content[:200]
            if len(memory.content) > 200:
                content_preview += "..."

            memory_summaries.append(
                MemorySummary(
                    filename=memory.filename,
                    title=memory.metadata.title,
                    date=memory.metadata.date,
                    source=memory.metadata.source,
                    tags=memory.metadata.tags,
                    content_preview=content_preview,
                )
            )

        return SearchMemoriesOutputSchema(
            success=True, total_found=len(memories), memories=memory_summaries
        )

    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        return SearchMemoriesOutputSchema(success=False, total_found=0, memories=[])


async def list_all_memories_handler() -> SearchMemoriesOutputSchema:
    """List all memories"""
    try:
        logger.info("📋 Listing all memories")

        # Get all memories
        memories = memory_storage.list_all_memories()

        # Create summaries
        memory_summaries = []
        for memory in memories:
            content_preview = memory.content[:200]
            if len(memory.content) > 200:
                content_preview += "..."

            memory_summaries.append(
                MemorySummary(
                    filename=memory.filename,
                    title=memory.metadata.title,
                    date=memory.metadata.date,
                    source=memory.metadata.source,
                    tags=memory.metadata.tags,
                    content_preview=content_preview,
                )
            )

        return SearchMemoriesOutputSchema(
            success=True, total_found=len(memories), memories=memory_summaries
        )

    except Exception as e:
        logger.error(f"Error listing memories: {e}")
        return SearchMemoriesOutputSchema(success=False, total_found=0, memories=[])


async def get_memory_stats_handler() -> StatsOutputSchema:
    """Get memory statistics"""
    try:
        logger.info("📊 Getting memory statistics")

        stats = memory_storage.get_memory_stats()

        return StatsOutputSchema(
            success=True,
            total_memories=stats["total_memories"],
            sources=stats["sources"],
            tags=stats["tags"],
            dates=stats["dates"],
            storage_path=stats["storage_path"],
        )

    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return StatsOutputSchema(
            success=False,
            total_memories=0,
            sources={},
            tags={},
            dates={},
            storage_path="",
        )


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
