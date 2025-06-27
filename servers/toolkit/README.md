# Toolkit - Essential Infrastructure Services

Toolkit is an MCP server that provides fundamental file operations and utilities needed by other MCP servers and workflows. It serves as the shared infrastructure layer, handling common tasks so that domain-specific servers can focus on their core functionality.

## Philosophy

Following microservices principles, Toolkit separates infrastructure concerns from business logic. Rather than every MCP server implementing its own file I/O, Toolkit provides reliable, tested, and consistent file operations as a service.

This creates cleaner separation of concerns and reduces duplication across the MCP Fleet ecosystem.

## Core Services

### File Operations
Comprehensive file management with proper error handling and encoding support:

**Reading Files**
- Text file reading with UTF-8 encoding
- Binary file reading with Base64 encoding
- Automatic encoding detection and conversion
- Large file handling with streaming support

**Writing Files**
- Safe file writing with atomic operations
- Automatic directory creation for file paths
- Backup creation for existing files
- Multiple encoding support (UTF-8, binary)

**File Management**
- File and directory deletion with safety checks
- File metadata retrieval (size, modification time, permissions)
- File existence checking and validation
- Safe file moving and copying operations

### Directory Operations
Robust directory management for organizing project files:

**Directory Creation**
- Recursive directory creation
- Permission setting and validation
- Path normalization and safety checks
- Cross-platform compatibility

**Directory Listing**
- Recursive and non-recursive directory traversal
- Pattern-based file filtering (glob patterns)
- Sorting options (name, date, size)
- Metadata inclusion (file sizes, dates, types)

### Utility Functions
Helper functions for common file system tasks:

**Path Operations**
- Path normalization and validation
- Relative and absolute path conversion
- Cross-platform path handling
- Safe path joining and manipulation

**Pattern Matching**
- Glob pattern support for file filtering
- Regular expression pattern matching
- File type detection and filtering
- Custom filtering predicates

## Use Cases

### MCP Server Support
Other MCP servers can delegate file operations to Toolkit:
- Tides uses Toolkit for report generation and export
- Compass uses Toolkit for project workspace management
- Custom servers can focus on domain logic, not file I/O

### Workflow Automation
File operations needed for productivity workflows:
- Batch file processing and organization
- Report generation and export
- Data backup and archival
- File synchronization between locations

### Development Support
Common development tasks made simple:
- Project file organization and cleanup
- Log file management and rotation
- Configuration file management
- Build artifact organization

### Data Management
Structured data handling for knowledge work:
- Document organization and categorization
- Research file management
- Note-taking system support
- Archive creation and maintenance

## MCP Tools

### Core File Tools
- `read_file`: Read file contents with encoding detection
- `write_file`: Write content to files with safety checks
- `delete_file`: Remove files and directories safely
- `create_directory`: Create directory structures

### Directory Tools
- `list_files`: Directory listing with filtering options
- `list_directories`: Directory-only listing and traversal

### Utility Tools
- `file_exists`: Check file/directory existence
- `get_file_info`: Retrieve file metadata and properties

## Design Principles

### Reliability
- Comprehensive error handling for all edge cases
- Atomic operations to prevent data corruption
- Graceful degradation when permissions are insufficient
- Detailed error messages for troubleshooting

### Safety
- Path validation to prevent directory traversal attacks
- Backup creation before destructive operations
- Confirmation prompts for dangerous operations
- Rollback capabilities for failed operations

### Performance
- Efficient file operations with minimal overhead
- Streaming support for large files
- Caching for frequently accessed file metadata
- Asynchronous operations where beneficial

### Compatibility
- Cross-platform file system support
- Unicode filename handling
- Various encoding support
- Standard file system conventions

## Integration Patterns

Toolkit is designed to work seamlessly with other MCP servers:

```python
# Example: Tides server using Toolkit for report export
def export_tide_report(tide_data, format='json'):
    # Format data
    content = format_tide_data(tide_data, format)
    
    # Use Toolkit to write file
    return toolkit_client.write_file(
        path=f"reports/tide-{tide_data.id}.{format}",
        content=content,
        create_dirs=True
    )
```

This pattern keeps domain servers focused on their core logic while ensuring consistent, reliable file operations across the entire MCP Fleet ecosystem.