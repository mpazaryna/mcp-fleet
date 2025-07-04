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
uv run python servers/tides/main.py          # Start tides server  
uv run python servers/compass/main.py        # Start compass server
```

### Testing Individual Components
```bash
# From workspace root
uv run pytest packages/mcp_core/tests/
uv run pytest servers/tides/tests/ -v
```

## Architecture Overview

### Core Structure
- `/servers/` - Three main MCP servers (tides, compass, memry)
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
  }
}
```

### Server Descriptions

- **tides**: Rhythmic workflow management based on natural tidal patterns for sustainable productivity
- **compass**: Systematic project methodology through exploration-to-execution phases with enforced depth

### Docker Deployment (Legacy)

Docker deployment is available but has limitations:
- GUI applications (like Drafts) cannot be opened from containers
- For full functionality, use native development setup

## Testing Strategy

Comprehensive four-tier testing approach following TDD methodology:

### Testing Hierarchy
1. **Unit Tests** - Individual component behavior with mocking
2. **Integration Tests** - Cross-component workflows and API testing  
3. **E2E Tests** - Full MCP protocol testing with Docker containers
4. **UAT Tests** - Real-world user scenarios with actual file creation

### Running Tests
```bash
# All tests
uv run pytest

# Specific test categories
uv run pytest -m e2e                    # End-to-end tests only
uv run pytest -m 'not e2e'              # Unit/integration only

# Example server-specific tests
uv run pytest servers/memry/tests/ -v

# UAT - Final acceptance testing
python tests/uat/test_memry_docker_uat.py    # User acceptance test for memry
```

### Test Development Process
Follow strict TDD methodology:
1. **Red**: Write failing test that captures the requirement
2. **Green**: Write minimal code to make the test pass  
3. **Refactor**: Improve code while keeping tests passing
4. **Repeat**: Continue until feature is complete

### E2E Testing Framework
- **MCPDockerClient**: Simulates Claude Desktop interaction with Docker containers
- **Protocol Validation**: Tests complete MCP JSON-RPC communication flow
- **Real Storage**: Validates actual file creation and persistence
- **Timeout Handling**: Proper interactive communication prevents hangs

## Key Conventions

- All servers implement MCP protocol with schema validation using Pydantic
- Python async/await patterns for all server implementations  
- uv workspace for dependency management and execution
- Comprehensive TDD methodology with test-first development
- Native system integration preferred over containerized solutions
- Import paths use workspace dependencies for shared packages

## Claude Code Commands

Custom commands are available in `.claude/commands/` to streamline development workflow:

### GitHub Issue Management
- `/project:write-github-issue <planning_notes>` - Create well-structured GitHub issues from planning sessions
- `/project:fix-github-issue <issue_number>` - Systematically analyze and fix GitHub issues following TDD methodology

### Development Workflow
All development work should follow this systematic approach:
1. **Planning**: Use `/project:write-github-issue` to create issues for new features or fixes
2. **Implementation**: Use `/project:fix-github-issue <number>` to systematically address issues
3. **Quality**: Commands automatically include proper gitflow, testing, and code review integration
4. **Cleanup**: Branch cleanup is handled automatically after merge

This ensures consistent, trackable development with proper issue management and git hygiene.

## Development Notes

### Python Migration
This project was migrated from TypeScript/Deno to Python to:
- Provide better system integration capabilities
- Leverage Python's rich ecosystem for AI and productivity tools

