# MCP-Memry Server

A Python-based memory storage system designed to store and retrieve information from Claude interactions using JSON files with the mcp-storage library.

## Overview

MCP-Memry provides a robust file-based approach to storing memories with the following features:

- **JSON Storage**: Structured storage using JSON files via mcp-storage library
- **Type-Safe Schema**: Pydantic models ensure data integrity and validation
- **Entity-Based Storage**: Each memory is stored as a separate JSON file with unique ID
- **Simple Search**: Find memories by date range, tags, source, or content
- **Automatic ID Generation**: Files are named by UUID for guaranteed uniqueness

## Storage Structure

### Base Directory
```
~/Documents/memry/
```

### File Naming Convention
Files are named by UUID with `.json` extension:
- `550e8400-e29b-41d4-a716-446655440000.json`
- `6ba7b810-9dad-11d1-80b4-00c04fd430c8.json`

### Memory Schema
Each JSON file contains structured memory data:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Descriptive Title of Memory",
  "content": "Memory content goes here",
  "source": "claude-desktop",
  "tags": ["tag1", "tag2", "tag3"],
  "date_slug": "2025-07-03",
  "topic_slug": "context-protocol-design",
  "filename": "2025-07-03-context-protocol-design"
}
```

### Benefits of JSON Storage

The switch from markdown to JSON provides several advantages:

1. **Structured Data**: JSON enforces a consistent schema across all memories
2. **Type Safety**: Pydantic models validate data before storage
3. **Better Querying**: Structured fields enable efficient filtering and searching
4. **Integration Ready**: JSON format is easily consumed by other tools and APIs
5. **Metadata Integrity**: All metadata is stored in a standardized format
6. **Future Extensibility**: Easy to add new fields without breaking existing data

## Available Tools

### create_memory
Create a new memory as a JSON file with structured data.

**Parameters:**
- `title`: Title of the memory
- `content`: Content of the memory (plain text or markdown formatting)
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
- **Dependencies**: mcp-core, mcp-storage, pydantic, pyyaml, aiofiles
- **Storage**: Local filesystem with JSON files via mcp-storage library
- **Protocol**: Model Context Protocol (MCP) for Claude integration
- **Data Integrity**: Type-safe Pydantic models with validation
- **Scalability**: Entity-based storage supports efficient querying and filtering