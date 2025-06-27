# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MCP Fleet is a Python monorepo hosting multiple Model Context Protocol (MCP) servers for AI-assisted project management and productivity workflows. The codebase integrates with Claude Desktop to provide systematic methodology tools, rhythmic workflow management, and native system integrations.

## Essential Commands

### Development & Testing
```bash
# Monorepo-wide operations
uv sync                 # Sync workspace dependencies
uv run pytest          # Run all tests
uv run pytest -m e2e   # Run end-to-end tests only
uv run pytest -m 'not e2e'  # Run unit/integration tests

# Server development (from workspace root)
uv run python servers/local/mcp_main.py      # Start local server
uv run python servers/tides/main.py          # Start tides server  
uv run python servers/compass/main.py        # Start compass server
uv run python servers/toolkit/main.py        # Start toolkit server
```

### Testing Individual Components
```bash
# From workspace root
uv run pytest servers/local/tests/test_apple_notes_tools.py
uv run pytest packages/mcp_core/tests/
uv run pytest servers/tides/tests/ -v
```

## Architecture Overview

### Core Structure
- `/servers/` - Four main MCP servers (local, tides, compass, toolkit)
- `/packages/` - Three shared libraries (mcp_core, claude_client, common_tools)
- `/projects/` - Shared workspace for orchestration framework project data

### MCP Integration Pattern
All servers implement the Model Context Protocol for Claude Desktop integration:
- stdio transport for communication
- Tool-based architecture with schema validation using Pydantic
- Structured JSON tool calls and responses
- uv workspace for shared dependencies

### Key Technologies
- **Runtime**: Python 3.11+ with uv package management
- **AI Integration**: Anthropic Claude API via @anthropic-ai/sdk
- **Protocol**: mcp>=1.0.0 for MCP implementation
- **Schema Validation**: Pydantic for type-safe tool definitions

## Server Architectures

### Local (`/servers/local/`)
Native macOS system integrations that bypass Docker limitations for full system access.

**Core Tools:**
- `create_note` - Create notes in Apple Notes with title and content
- `list_notes` - List all notes or notes from specific folders
- `search_notes` - Search notes by title or content
- `create_folder` - Create new folders in Apple Notes
- `list_folders` - List all existing folders

**Integration Features:**
- **AppleScript-based** - Direct native macOS application control
- **No Docker needed** - Runs natively for full system access
- **TDD methodology** - Comprehensive test suite with E2E Apple Notes testing
- **Future expansion** - Architecture ready for Reminders and Calendar integration

### Tides (`/servers/tides/`)
Rhythmic workflow management based on natural tidal patterns for sustainable productivity cycles.

**Core Tools:**
- `create_tide` - Create new tidal workflows for different time scales
- `list_tides` - List and filter existing workflows with status
- `flow_tide` - Start focused flow sessions with intensity control
- `save_tide_report` - Export individual tide reports (JSON/Markdown/CSV)
- `export_all_tides` - Batch export with filtering and date ranges

**Report Features:**
- Multiple export formats with rich statistics and flow history
- Automatic file organization by flow type and date
- Docker volume mounting for persistent storage outside containers
- Reports saved to `~/Documents/TideReports/` when using recommended deployment

### Compass (`/servers/compass/`)
Systematic project methodology through exploration-to-execution phases. Enforces depth and prevents surface-level AI responses.

**Core Tools:**
- `init_project` - Initialize new project with structured workspace
- `start_exploration` - Begin systematic exploration sessions
- `save_exploration_session` - Preserve conversation context and insights
- `complete_exploration_phase` - Transition to specification with validation
- `generate_specification` - Create requirements documents from exploration
- `start_execution` - Break down specifications into actionable tasks
- `list_tasks` / `update_task_status` - Track execution progress

**Methodology Features:**
- **Phase enforcement** - Cannot skip phases, must complete prerequisites
- **Context preservation** - All conversations and decisions are preserved
- **Pattern-based specifications** - Professional requirements generation
- **Task breakdown** - Context-aware execution planning with priorities
- **File persistence** - Projects stored in structured workspace directories

### Toolkit (`/servers/toolkit/`)
Essential file operations and utilities for other workflows and general productivity tasks.

**Core Tools:**
- File operations (read, write, list directories)
- Text processing and manipulation
- Data export and formatting utilities
- Development workflow support

**Note on Drafts Integration:**
The toolkit server includes Drafts app integration tools, but these have a known limitation: Docker containerization prevents URL schemes from opening host GUI applications. For Drafts-like functionality, use the **local** server's Apple Notes integration instead.

## Shared Packages

### mcp_core (`/packages/mcp_core/`)
- MCP server creation factory with transport utilities
- Type-safe tool definition helpers using Pydantic
- Standardized error handling patterns
- Official MCP protocol implementation wrapper

### claude_client (`/packages/claude_client/`)
- Enhanced Anthropic API client with retry logic
- Conversation management and streaming support
- Rate limiting and error recovery
- Async/await patterns for Python integration

### common_tools (`/packages/common_tools/`)
- File operations (read, write, list directories)
- Git operations and project discovery
- Shared utilities used across servers
- Cross-platform compatibility helpers

## Environment Setup

Requires `ANTHROPIC_API_KEY` environment variable for Claude API integration (tides server only).

### Native Development Setup (Recommended)

Claude Desktop configuration:
```json
{
  "mcpServers": {
    "local": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-fleet",
        "run",
        "python",
        "servers/local/mcp_main.py"
      ],
      "env": {}
    },
    "tides": {
      "command": "uv",
      "args": [
        "--directory", 
        "/path/to/mcp-fleet",
        "run",
        "python",
        "servers/tides/main.py"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    },
    "compass": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-fleet", 
        "run",
        "python",
        "servers/compass/main.py"
      ],
      "env": {}
    },
    "toolkit": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-fleet",
        "run", 
        "python",
        "servers/toolkit/main.py"
      ],
      "env": {}
    }
  }
}
```

### Server Descriptions

- **local**: Native macOS system integrations (Apple Notes, future Reminders/Calendar) - bypasses Docker limitations for full system access
- **tides**: Rhythmic workflow management based on natural tidal patterns for sustainable productivity
- **compass**: Systematic project methodology through exploration-to-execution phases with enforced depth
- **toolkit**: Essential file operations, utilities, and development workflow support

### Docker Deployment (Legacy)

Docker deployment is available but has limitations:
- GUI applications (like Drafts) cannot be opened from containers
- Native system integrations (like Apple Notes) don't work in containers
- For full functionality, use native development setup

## Testing Strategy

Comprehensive three-tier testing approach:
- **Unit tests** - Individual component behavior with mocking
- **Integration tests** - Cross-component workflows and API testing
- **E2E tests** - Full MCP protocol testing with real system integration

### Running Tests
```bash
# All tests
uv run pytest

# Specific test categories
uv run pytest -m e2e                    # End-to-end tests only
uv run pytest -m 'not e2e'              # Unit/integration only
uv run pytest servers/local/tests/ -v   # Specific server tests

# Apple Notes E2E testing (creates real notes)
uv run pytest servers/local/tests/test_apple_notes_tools.py -m e2e -s
```

## Key Conventions

- All servers implement MCP protocol with schema validation using Pydantic
- Python async/await patterns for all server implementations  
- uv workspace for dependency management and execution
- Comprehensive TDD methodology with test-first development
- Native system integration preferred over containerized solutions
- Import paths use workspace dependencies for shared packages

## Development Notes

### Python Migration
This project was migrated from TypeScript/Deno to Python to:
- Provide better system integration capabilities
- Support native macOS application control via AppleScript
- Leverage Python's rich ecosystem for AI and productivity tools
- Enable easier local development without container limitations

### Local Server Rationale  
The local server was created specifically to bypass Docker GUI limitations discovered during Drafts integration attempts. It provides a template for future native system integrations while maintaining the same MCP protocol standards as other servers.