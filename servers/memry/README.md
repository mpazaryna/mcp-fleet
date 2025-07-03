# MCP-Memry Server

A Python-based memory storage system designed to store and retrieve information from Claude interactions using markdown files with YAML frontmatter.

## Overview

MCP-Memry provides a simple file-based approach to storing memories with the following features:

- **File Storage**: Filesystem-based storage using markdown files
- **YAML Frontmatter**: Structured metadata with title, date, source, and tags
- **Simple Search**: Find memories by date range, tags, or content
- **Automatic Naming**: Files follow the pattern `YYYY-MM-DD-topic-slug.md`

## Storage Structure

### Base Directory
```
~/Documents/memry/
```

### File Naming Convention
Files follow the pattern: `YYYY-MM-DD-topic-slug.md`

Examples:
- `2025-07-01-llm-names-it.md`
- `2025-07-03-context-protocol-design.md`

### Metadata Schema
Each markdown file contains YAML frontmatter:

```yaml
---
title: "Descriptive Title of Memory"
date: YYYY-MM-DD
source: "claude-desktop|claude-code|etc"
tags: ["tag1", "tag2", "tag3"]
---

Memory content goes here in markdown format.
```

## Available Tools

### create_memory
Create a new memory file with markdown content and YAML frontmatter.

**Parameters:**
- `title`: Title of the memory
- `content`: Content of the memory in markdown
- `source`: Source of the memory (defaults to "claude-code")
- `tags`: List of tags for categorizing (optional)
- `topic_slug`: Optional topic slug for filename (auto-generated if not provided)

### search_memories
Search memories by date range, tags, or content.

**Parameters:**
- `date_from`: Start date for search (YYYY-MM-DD format, optional)
- `date_to`: End date for search (YYYY-MM-DD format, optional)
- `tags`: List of tags to filter by (optional)
- `content_search`: Text to search for in memory content and titles (optional)

### list_all_memories
List all stored memories with summaries.

### get_memory_stats
Get statistics about stored memories including counts by source, tags, and dates.

## Environment Variables

- `MEMRY_STORAGE_PATH`: Override default storage path (default: `~/Documents/memry`)

## Usage Examples

### Creating a Memory
```python
# Create a memory about a conversation
create_memory(
    title="LLM Context Protocol Design",
    content="Discussion about implementing context protocols for better AI interactions...",
    source="claude-desktop",
    tags=["ai", "protocol", "design"]
)
```

### Searching Memories
```python
# Search by tags
search_memories(tags=["ai", "protocol"])

# Search by date range
search_memories(date_from="2025-07-01", date_to="2025-07-31")

# Search by content
search_memories(content_search="context protocol")
```

## Integration with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "memry": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-fleet",
        "run",
        "python",
        "servers/memry/main.py"
      ],
      "env": {
        "MEMRY_STORAGE_PATH": "~/Documents/memry"
      }
    }
  }
}
```

## Development

### Running Tests
```bash
# From workspace root
uv run pytest servers/memry/tests/ -v
```

### Starting the Server
```bash
# From workspace root
uv run python servers/memry/main.py
```

## Technical Details

- **Python Version**: 3.11+
- **Dependencies**: mcp-core, pydantic, pyyaml, aiofiles
- **Storage**: Local filesystem with markdown files
- **Protocol**: Model Context Protocol (MCP) for Claude integration