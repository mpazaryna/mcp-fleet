"""
Memory storage system for MCP-Memry

Handles filesystem-based storage using markdown files with YAML frontmatter.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MemoryMetadata(BaseModel):
    """Schema for memory metadata"""

    title: str = Field(description="Descriptive title of the memory")
    date: str = Field(description="Date in YYYY-MM-DD format")
    source: str = Field(
        description="Source of the memory (claude-desktop, claude-code, etc.)"
    )
    tags: list[str] = Field(default_factory=list, description="List of tags")


class Memory(BaseModel):
    """Complete memory with metadata and content"""

    metadata: MemoryMetadata
    content: str
    filename: str
    file_path: str


class CreateMemoryInput(BaseModel):
    """Input for creating a new memory"""

    title: str = Field(description="Title of the memory")
    content: str = Field(description="Content of the memory")
    source: str = Field(description="Source of the memory")
    tags: list[str] = Field(default_factory=list, description="Tags for the memory")
    topic_slug: str | None = Field(
        default=None, description="Optional topic slug for filename"
    )


class SearchFilter(BaseModel):
    """Filter for searching memories"""

    date_from: str | None = Field(default=None, description="Start date (YYYY-MM-DD)")
    date_to: str | None = Field(default=None, description="End date (YYYY-MM-DD)")
    tags: list[str] | None = Field(default=None, description="Tags to filter by")
    content_search: str | None = Field(
        default=None, description="Text to search in content"
    )


class MemoryStorage:
    """File-based storage for memories"""

    def __init__(self, base_path: str = "~/Documents/memry"):
        """Initialize storage with base path"""
        self.base_path = Path(base_path).expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Memory storage initialized at {self.base_path}")

    def _generate_filename(
        self, title: str, date: str, topic_slug: str | None = None
    ) -> str:
        """Generate filename following pattern: YYYY-MM-DD-topic-slug.md"""
        if topic_slug:
            slug = self._slugify(topic_slug)
        else:
            slug = self._slugify(title)

        return f"{date}-{slug}.md"

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r"[^a-zA-Z0-9\s-]", "", text.lower())
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    def _parse_memory_file(self, file_path: Path) -> Memory | None:
        """Parse a memory file and return Memory object"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Split frontmatter and content
            if content.startswith("---\n"):
                parts = content.split("---\n", 2)
                if len(parts) >= 3:
                    frontmatter_str = parts[1]
                    content_str = parts[2].strip()

                    # Parse YAML frontmatter
                    frontmatter = yaml.safe_load(frontmatter_str)

                    # Create metadata
                    metadata = MemoryMetadata(
                        title=frontmatter.get("title", ""),
                        date=frontmatter.get("date", ""),
                        source=frontmatter.get("source", ""),
                        tags=frontmatter.get("tags", []),
                    )

                    return Memory(
                        metadata=metadata,
                        content=content_str,
                        filename=file_path.name,
                        file_path=str(file_path),
                    )

            logger.warning(f"Invalid memory file format: {file_path}")
            return None

        except Exception as e:
            logger.error(f"Error parsing memory file {file_path}: {e}")
            return None

    def create_memory(self, input_data: CreateMemoryInput) -> Memory:
        """Create a new memory file"""
        try:
            # Use current date if not provided
            current_date = datetime.now().strftime("%Y-%m-%d")

            # Generate filename
            filename = self._generate_filename(
                input_data.title, current_date, input_data.topic_slug
            )

            file_path = self.base_path / filename

            # Check if file already exists
            if file_path.exists():
                # Add timestamp to make it unique
                timestamp = datetime.now().strftime("%H%M%S")
                base_name = filename.replace(".md", "")
                filename = f"{base_name}-{timestamp}.md"
                file_path = self.base_path / filename

            # Create metadata
            metadata = MemoryMetadata(
                title=input_data.title,
                date=current_date,
                source=input_data.source,
                tags=input_data.tags,
            )

            # Create file content with YAML frontmatter
            frontmatter = {
                "title": metadata.title,
                "date": metadata.date,
                "source": metadata.source,
                "tags": metadata.tags,
            }

            yaml_str = yaml.dump(frontmatter, default_flow_style=False)
            content = f"---\n{yaml_str}---\n\n{input_data.content}"

            # Write file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"💾 Created memory: {filename}")

            return Memory(
                metadata=metadata,
                content=input_data.content,
                filename=filename,
                file_path=str(file_path),
            )

        except Exception as e:
            logger.error(f"Error creating memory: {e}")
            raise

    def search_memories(self, filter_data: SearchFilter) -> list[Memory]:
        """Search memories based on filter criteria"""
        try:
            memories = []

            # Get all .md files
            for file_path in self.base_path.glob("*.md"):
                memory = self._parse_memory_file(file_path)
                if memory:
                    memories.append(memory)

            # Apply filters
            filtered_memories = []

            for memory in memories:
                # Date range filter
                if (
                    filter_data.date_from
                    and memory.metadata.date < filter_data.date_from
                ):
                    continue
                if filter_data.date_to and memory.metadata.date > filter_data.date_to:
                    continue

                # Tags filter
                if filter_data.tags:
                    if not any(tag in memory.metadata.tags for tag in filter_data.tags):
                        continue

                # Content search
                if filter_data.content_search:
                    search_text = filter_data.content_search.lower()
                    if (
                        search_text not in memory.content.lower()
                        and search_text not in memory.metadata.title.lower()
                    ):
                        continue

                filtered_memories.append(memory)

            # Sort by date (newest first)
            filtered_memories.sort(key=lambda m: m.metadata.date, reverse=True)

            logger.info(f"🔍 Found {len(filtered_memories)} memories matching criteria")
            return filtered_memories

        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            raise

    def list_all_memories(self) -> list[Memory]:
        """List all memories"""
        return self.search_memories(SearchFilter())

    def get_memory_stats(self) -> dict[str, Any]:
        """Get statistics about stored memories"""
        try:
            memories = self.list_all_memories()

            # Count by source
            sources = {}
            tags = {}
            dates = {}

            for memory in memories:
                # Count sources
                sources[memory.metadata.source] = (
                    sources.get(memory.metadata.source, 0) + 1
                )

                # Count tags
                for tag in memory.metadata.tags:
                    tags[tag] = tags.get(tag, 0) + 1

                # Count dates
                dates[memory.metadata.date] = dates.get(memory.metadata.date, 0) + 1

            return {
                "total_memories": len(memories),
                "sources": sources,
                "tags": tags,
                "dates": dates,
                "storage_path": str(self.base_path),
            }

        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            raise
