# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MCP Fleet is a Deno TypeScript monorepo hosting multiple Model Context Protocol (MCP) servers for AI-assisted project management and productivity workflows. The codebase integrates with Claude Desktop to provide systematic methodology tools and rhythmic workflow management.

## Essential Commands

### Development & Testing
```bash
# Monorepo-wide operations
deno task test          # Run all tests (packages + servers)
deno task test:packages # Run package tests only
deno task test:servers  # Run server tests only
deno task lint          # Lint all code
deno task fmt           # Format all code
deno task check         # Type check all server entry points

# Server development (run from server directories)
deno task start         # Start MCP server
deno task dev           # Development mode with file watching
deno task test          # Run server-specific tests
```

### Testing Individual Components
```bash
# From root directory
deno test servers/orchestration-framework/tests/unit/project-manager.test.ts
deno test packages/claude-client/tests/
```

## Architecture Overview

### Core Structure
- `/servers/` - Two main MCP servers (orchestration-framework, tides)
- `/packages/` - Three shared libraries (mcp-core, claude-client, common-tools)
- `/projects/` - Shared workspace for orchestration framework project data

### MCP Integration Pattern
All servers implement the Model Context Protocol for Claude Desktop integration:
- stdio transport for communication
- Tool-based architecture with schema validation using Zod
- Structured JSON tool calls and responses
- Import mapping: `@packages/` for shared dependencies

### Key Technologies
- **Runtime**: Deno with TypeScript
- **AI Integration**: Anthropic Claude API via @anthropic-ai/sdk
- **Protocol**: @modelcontextprotocol/sdk for MCP implementation
- **Schema Validation**: Zod for type-safe tool definitions

## Server Architectures

### Orchestration Framework (`/servers/orchestration-framework/`)
Implements 4-phase systematic methodology: Exploration → Specification → Execution → Feedback

**Core Components:**
- `src/project-manager.ts` - Project lifecycle management with phase tracking
- `src/pattern-manager.ts` - Domain-specific specification templates
- `src/flywheel-manager.ts` - Iterative improvement and gap detection
- `src/claude-client.ts` - AI conversation management with context continuity

**Data Management:**
- Projects stored in `/projects/{project-name}/` with phase-specific directories
- Conversation history preserved for context continuity
- Pattern-based templates for business, software, and personal development domains

### Tides (`/servers/tides/`)
Rhythmic workflow management based on natural tidal patterns for sustainable productivity cycles.

## Shared Packages

### mcp-core (`/packages/mcp-core/`)
- MCP server creation factory with transport utilities
- Type-safe tool definition helpers
- Standardized error handling patterns

### claude-client (`/packages/claude-client/`)
- Enhanced Anthropic API client with retry logic
- Conversation management and streaming support
- Rate limiting and error recovery

### common-tools (`/packages/common-tools/`)
- File operations (read, write, list directories)
- Git operations and project discovery
- Shared utilities used across servers

## Environment Setup

Requires `ANTHROPIC_API_KEY` environment variable for Claude API integration.

### Docker Deployment (Recommended)

#### Prerequisites
- Docker Desktop with MCP Toolkit enabled
- Set `ANTHROPIC_API_KEY` environment variable

#### Build and Deploy
```bash
# Build all Docker images
deno task docker:build:all

# Start services with Docker Compose
deno task docker:up

# View logs
deno task docker:logs

# Stop services
deno task docker:down

# Clean up (removes containers and volumes)
deno task docker:clean
```

#### Docker Desktop MCP Toolkit Integration
1. Enable Docker MCP Toolkit in Docker Desktop settings (Beta features)
2. In Docker Desktop, go to MCP Toolkit → Catalog
3. Build and run the MCP Fleet containers locally
4. Connect to Claude Desktop via Docker MCP Toolkit interface

#### Manual Docker Commands
```bash
# Build base image
docker build -t mcp-fleet:base .

# Build server images
docker build -t mcp-fleet:orchestration-framework -f Dockerfile.orchestration .
docker build -t mcp-fleet:tides -f Dockerfile.tides .

# Run individual servers
docker run -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -v "$(pwd)/projects:/app/projects" \
  mcp-fleet:orchestration-framework

docker run -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  mcp-fleet:tides
```

### Native Development Setup

Claude Desktop configuration example:
```json
{
  "mcpServers": {
    "orchestration-framework": {
      "command": "deno",
      "args": ["run", "--allow-all", "/path/to/servers/orchestration-framework/mcp_main.ts"]
    }
  }
}
```

## Testing Strategy

Three-tier testing approach:
- **Unit tests** - Individual component behavior
- **Integration tests** - Cross-component workflows  
- **E2E tests** - Full API and MCP protocol testing
- Mock Claude client available for testing without API calls

## Key Conventions

- All servers export tools via MCP protocol with schema validation
- Project data follows systematic phase structure (exploration/specification/execution/feedback)
- Conversation histories are preserved as organizational knowledge assets
- Flywheel pattern used for iterative improvement and gap detection
- Import paths use `@packages/` workspace mapping for shared dependencies