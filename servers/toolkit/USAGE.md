# Toolkit MCP Server Usage

The Toolkit server provides shared file I/O utilities for the entire MCP Fleet. This allows other servers to focus on their core domain logic while delegating infrastructure concerns to the toolkit.

## Architecture Pattern

Instead of each MCP server implementing its own file operations, they delegate to the toolkit:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Tides       │    │ Orchestration   │    │     Future      │
│     Server      │    │   Framework     │    │    Servers      │
│                 │    │     Server      │    │                 │
│ - Workflows     │    │ - Projects      │    │ - Domain        │
│ - Flow sessions │    │ - Patterns      │    │   Logic         │
│ - Reports*      │    │ - Conversations │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Toolkit     │
                    │     Server      │
                    │                 │
                    │ - File I/O      │
                    │ - Directory ops │
                    │ - Data persistence
                    └─────────────────┘
```

*Note: Currently, tides still has direct file I/O for backward compatibility. In a full implementation, it would use the toolkit via MCP-to-MCP communication.

## Available Tools

### write_file
Save content to a file with automatic directory creation.

**Input:**
- `file_path` (string): Path to the file
- `content` (string): Content to write
- `create_dirs` (boolean, optional): Create parent directories (default: true)
- `encoding` (string, optional): "utf8" or "base64" (default: "utf8")

**Example:**
```json
{
  "file_path": "/app/reports/tides/daily/morning-routine.json",
  "content": "{\"name\": \"Morning Routine\", \"flows\": []}",
  "create_dirs": true,
  "encoding": "utf8"
}
```

### read_file
Read content from a file.

**Input:**
- `file_path` (string): Path to the file
- `encoding` (string, optional): "utf8" or "base64" (default: "utf8")

### create_directory
Create directories with recursive support.

**Input:**
- `dir_path` (string): Directory path to create
- `recursive` (boolean, optional): Create parent directories (default: true)

### list_files
List files and directories with pattern filtering.

**Input:**
- `dir_path` (string): Directory to list
- `pattern` (string, optional): Glob pattern to filter files
- `include_dirs` (boolean, optional): Include directories in results (default: true)
- `recursive` (boolean, optional): List recursively (default: false)

**Example with pattern:**
```json
{
  "dir_path": "/app/reports",
  "pattern": "*.json",
  "include_dirs": false,
  "recursive": true
}
```

### delete_file
Delete files or directories.

**Input:**
- `file_path` (string): Path to delete
- `recursive` (boolean, optional): Delete directories recursively (default: false)

## Claude Desktop Configuration

To use multiple MCP servers together, configure Claude Desktop with all servers:

```json
{
  "mcpServers": {
    "tides": {
      "command": "deno",
      "args": ["run", "--allow-all", "/path/to/servers/tides/mcp_main.ts"]
    },
    "toolkit": {
      "command": "deno", 
      "args": ["run", "--allow-all", "/path/to/servers/toolkit/mcp_main.ts"]
    },
    "orchestration-framework": {
      "command": "deno",
      "args": ["run", "--allow-all", "/path/to/servers/orchestration-framework/mcp_main.ts"]
    }
  }
}
```

## Docker Usage

The toolkit can be run as a Docker container:

```bash
# Build the toolkit image
deno task docker:build:toolkit

# Run with Docker Compose (includes all MCP Fleet servers)
deno task docker:up

# Run toolkit standalone
docker run -v toolkit-data:/app/data mcp-fleet:toolkit
```

## Benefits of This Architecture

1. **Separation of Concerns**: Each server focuses on its domain
2. **Code Reuse**: Shared file operations across all servers
3. **Consistency**: Standardized file handling patterns
4. **Security**: Centralized file access control
5. **Testing**: Easier to mock file operations in tests
6. **Maintenance**: File I/O bugs fixed in one place

## Future Enhancements

- MCP-to-MCP communication for true service composition
- Advanced file operations (compression, encryption, backup)
- Configuration management utilities
- Database abstraction layer
- Network utilities for HTTP requests
- JSON/YAML/CSV parsing utilities