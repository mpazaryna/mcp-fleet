"""
Memory models for MCP-Memry using shared storage abstractions
"""

from pydantic import BaseModel, Field
from storage.types import BaseEntity, EntityFilter
from storage.utils import get_current_timestamp


class MemoryData(BaseEntity):
    """Core memory entity with all required fields"""

    title: str = Field(description="Memory title")
    content: str = Field(description="Memory content in markdown")
    source: str = Field(
        description="Source of the memory (claude-desktop, claude-code, etc.)"
    )
    tags: list[str] = Field(default_factory=list, description="List of tags")
    created_at: str = Field(
        default_factory=get_current_timestamp, description="Creation timestamp"
    )
    updated_at: str = Field(
        default_factory=get_current_timestamp, description="Last update timestamp"
    )

    # Computed fields for file organization
    @property
    def date_slug(self) -> str:
        """Get date in YYYY-MM-DD format for filename"""
        return self.created_at.split("T")[0]  # Extract date part from ISO timestamp

    @property
    def topic_slug(self) -> str:
        """Generate topic slug from title"""
        import re

        slug = re.sub(r"[^a-zA-Z0-9\s-]", "", self.title.lower())
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    @property
    def filename(self) -> str:
        """Generate filename following YYYY-MM-DD-topic-slug.md pattern"""
        return f"{self.date_slug}-{self.topic_slug}.md"


class CreateMemoryInput(BaseModel):
    """Input model for creating memories"""

    title: str = Field(description="Memory title")
    content: str = Field(description="Memory content")
    source: str = Field(description="Source of the memory", default="claude-code")
    tags: list[str] = Field(default_factory=list, description="Tags for the memory")
    topic_slug: str | None = Field(
        default=None, description="Optional custom topic slug"
    )


class MemoryFilter(EntityFilter):
    """Filter model for searching memories"""

    date_from: str | None = Field(default=None, description="Start date (YYYY-MM-DD)")
    date_to: str | None = Field(default=None, description="End date (YYYY-MM-DD)")
    tags: list[str] | None = Field(default=None, description="Tags to filter by")
    content_search: str | None = Field(
        default=None, description="Text to search in content"
    )
    source: str | None = Field(default=None, description="Filter by source")


class MemorySummary(BaseModel):
    """Summary view of a memory for listing"""

    id: str
    filename: str
    title: str
    date: str
    source: str
    tags: list[str]
    content_preview: str
