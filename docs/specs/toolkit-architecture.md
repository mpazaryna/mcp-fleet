# MCP Fleet Toolkit Architecture

The Toolkit server provides shared infrastructure and file I/O utilities for the entire MCP Fleet, enabling proper separation of concerns where each server focuses on its core domain while delegating infrastructure operations to the toolkit.

## Overview

The MCP Fleet follows a microservices architecture pattern where specialized servers handle domain-specific logic while sharing common infrastructure through the toolkit server.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Tides       │    │ Orchestration   │    │     Future      │
│     Server      │    │   Framework     │    │    Servers      │
│                 │    │     Server      │    │                 │
│ - Workflows     │    │ - Projects      │    │ - Domain        │
│ - Flow sessions │    │ - Patterns      │    │   Logic         │
│ - Tide reports  │    │ - Conversations │    │                 │
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
                    │ - Data persist. │
                    └─────────────────┘
```

## Architectural Benefits

### 1. **Separation of Concerns**
- **Domain Servers**: Focus exclusively on business logic (workflows, project management, etc.)
- **Toolkit Server**: Handles all cross-cutting infrastructure concerns
- **Clean Boundaries**: Each server has a single, well-defined responsibility

### 2. **Code Reuse**
- File operations standardized across all servers
- Consistent error handling and response patterns
- Shared utilities reduce duplication

### 3. **Maintainability**
- Infrastructure bugs fixed in one place
- Easier to add new capabilities to all servers
- Simplified testing and deployment

### 4. **Scalability**
- Servers can be deployed independently
- Infrastructure scaled separately from domain logic
- Future MCP-to-MCP communication ready

## Toolkit Server Implementation

### Core Tools

#### `write_file`
Save content to files with automatic directory creation.

**Features:**
- UTF-8 and Base64 encoding support
- Automatic parent directory creation
- Atomic file operations
- Detailed response with bytes written and created directories

**Usage Example:**
```json
{
  "file_path": "/app/reports/tides/daily/morning-routine.json",
  "content": "{\"name\": \"Morning Routine\", \"flows\": []}",
  "create_dirs": true,
  "encoding": "utf8"
}
```

#### `read_file`
Read file contents with encoding support.

**Features:**
- UTF-8 and Base64 encoding
- File metadata included (size, modification time)
- Error handling for missing files

#### `create_directory`
Create directories with recursive support.

**Features:**
- Recursive directory creation
- Proper handling of existing directories
- Clear success/already-exists feedback

#### `list_files`
List directory contents with advanced filtering.

**Features:**
- Glob pattern filtering (`*.json`, `report-*`, etc.)
- Recursive directory traversal
- File type distinction (file vs directory)
- Metadata for each entry (size, modification time)

**Pattern Examples:**
- `*.json` - All JSON files
- `report-*` - Files starting with "report-"
- `*` - All files (default)

#### `delete_file`
Safe file and directory deletion.

**Features:**
- Recursive directory deletion option
- Graceful handling of non-existent files
- Confirmation of deletion success

### Technical Implementation

#### File Structure
```
servers/toolkit/
├── deno.json              # Project configuration
├── mcp_main.ts           # MCP server entry point
├── USAGE.md              # Usage documentation
├── src/
│   └── tools/
│       └── file-tools.ts # Core file operation tools
└── tests/
    ├── unit/             # Unit tests for individual functions
    │   └── file-tools.test.ts
    └── integration/      # Integration tests for workflows
        └── toolkit-integration.test.ts
```

#### Schema Validation
All tools use Zod schemas for input/output validation:
- Type-safe tool definitions
- Automatic validation of parameters
- Clear error messages for invalid inputs

#### Error Handling
Consistent error handling patterns:
- Descriptive error messages
- Proper exception propagation
- Graceful degradation for non-critical errors

## Integration Patterns

### Current Implementation (Direct File I/O)
Currently, servers like `tides` still perform direct file operations for backward compatibility. This allows the system to function while the toolkit architecture is established.

### Future Implementation (MCP-to-MCP)
When MCP-to-MCP communication becomes available:

```typescript
// Future pattern: Tides server delegating to toolkit
const reportResult = await toolkitMCP.call('write_file', {
  file_path: reportPath,
  content: jsonReport,
  create_dirs: true
});
```

### Claude Desktop Configuration
Configure all servers together:

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

## Docker Deployment

### Individual Server Deployment
```bash
# Build toolkit image
deno task docker:build:toolkit

# Run toolkit standalone
docker run -v toolkit-data:/app/data mcp-fleet:toolkit
```

### Fleet Deployment
```bash
# Build all images
deno task docker:build:all

# Deploy entire fleet
deno task docker:up

# View logs
deno task docker:logs
```

### Volume Management
Each server has dedicated persistent storage:
- `orchestration-projects`: Project data for orchestration framework
- `tides-reports`: Report storage for tides server
- `toolkit-data`: General file storage for toolkit operations

## Testing Strategy

### Comprehensive Test Coverage
- **Unit Tests**: Individual function behavior
- **Integration Tests**: Complete workflow testing
- **Error Handling**: Edge cases and failure modes

### Test Features
- Pattern matching validation
- Base64 encoding/decoding
- Directory creation and deletion
- File existence and permissions
- Concurrent operations safety

### Test Results
All 24 test steps passing, covering:
- Tool schema validation
- Handler registration
- File operation workflows
- Error conditions
- Pattern filtering
- Encoding support

## Development Workflow

### Adding New Tools
1. Define schemas in `file-tools.ts`
2. Implement handler function
3. Add to tools and handlers exports
4. Write unit tests
5. Add integration tests
6. Update documentation

### Extending Functionality
Future toolkit enhancements could include:
- **Configuration Management**: Centralized config handling
- **Database Abstractions**: Common data persistence patterns
- **Network Utilities**: HTTP request helpers
- **Data Processing**: JSON/YAML/CSV parsing utilities
- **Security Tools**: Encryption, hashing, authentication helpers
- **Monitoring**: Logging, metrics, health checks

## Best Practices

### Tool Design
- **Single Responsibility**: Each tool does one thing well
- **Consistent Interface**: Standard input/output patterns
- **Error Transparency**: Clear error messages and codes
- **Resource Safety**: Proper cleanup and resource management

### Schema Design
- **Descriptive Parameters**: Clear parameter names and descriptions
- **Optional Defaults**: Sensible defaults for optional parameters
- **Validation**: Strict input validation with helpful error messages
- **Backward Compatibility**: Careful schema evolution

### Testing
- **TDD Approach**: Write tests before implementation
- **Edge Cases**: Test boundary conditions and error scenarios
- **Integration**: Test complete workflows end-to-end
- **Performance**: Validate file operations under load

## Security Considerations

### File System Access
- **Path Validation**: Prevent directory traversal attacks
- **Permission Checks**: Respect file system permissions
- **Resource Limits**: Prevent excessive disk usage
- **Audit Logging**: Track file operations for security review

### Data Protection
- **Encoding Safety**: Secure handling of binary data
- **Error Information**: Avoid leaking sensitive paths in errors
- **Access Control**: Future authentication and authorization
- **Encryption**: Future support for encrypted file storage

## Monitoring and Observability

### Logging
- **Structured Logging**: Consistent log format across operations
- **Error Tracking**: Detailed error information for debugging
- **Performance Metrics**: File operation timing and throughput
- **Usage Analytics**: Track tool usage patterns

### Health Checks
- **File System Health**: Monitor disk space and permissions
- **Tool Availability**: Verify all tools are functional
- **Performance Monitoring**: Track response times
- **Resource Usage**: Monitor memory and CPU consumption

## Conclusion

The MCP Fleet Toolkit architecture successfully achieves:

1. **Clean Separation**: Domain logic isolated from infrastructure
2. **Shared Infrastructure**: Common file operations across all servers
3. **Scalable Design**: Ready for future MCP-to-MCP communication
4. **Production Ready**: Comprehensive testing and Docker deployment
5. **Extensible Framework**: Easy to add new capabilities

This architecture embodies the "fleet with a shared toolkit" metaphor perfectly - specialized vessels (servers) for different purposes, all equipped with the same essential tools for navigation and maintenance.

The implementation provides a solid foundation for the MCP Fleet's continued evolution while maintaining clean architectural boundaries and operational excellence.