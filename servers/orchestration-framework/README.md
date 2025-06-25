# Orchestration Framework MCP Server

A systematic methodology for knowledge work that combines human strategic thinking with AI execution capabilities. This MCP server provides conversational access to the Orchestration Framework through Claude Desktop.

## Overview

The Orchestration Framework implements a **4-phase process**: Exploration → Specification → Execution → Feedback & Learning. Each phase has mandatory completion criteria that prevent "brilliant surface solutions" by ensuring thorough problem exploration before execution.

## Features

- **Project Management**: Initialize and manage framework projects
- **Exploration Phase**: AI-assisted exploration sessions with context continuity
- **Pattern System**: Domain-specific templates for specification generation
- **Flywheel System**: Recursive improvement cycles with gap detection
- **Context-Aware Sessions**: Conversation history preservation across sessions

## Quick Start

### Running the Server

```bash
# Start MCP server for Claude Desktop
deno task start

# Development mode with file watching
deno task dev

# Run tests
deno task test
```

### Claude Desktop Integration

Add to your Claude Desktop configuration:

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

## Available Tools

### Project Management
- `init_project(name)` - Initialize new framework project
- `list_projects()` - Show all projects with status
- `get_project_status(project?)` - Get detailed project status
- `get_project_context(project)` - Load conversation history

### Exploration Phase
- `start_exploration(project?, focus_area?)` - Begin/continue exploration
- `save_exploration_session(project, content, summary?)` - Save session
- `complete_exploration_phase(project, reason?)` - Mark exploration complete

### Specification Phase
- `generate_specification(project?, pattern?)` - Generate specs from exploration
- `list_patterns()` - Show available specification patterns

### Quality & Learning
- `check_flywheel_opportunities(project?)` - Analyze gaps and recommend iterations
- `write_feedback(project, content, type?, session?)` - Capture learnings
- `get_framework_lesson(topic?, level?)` - Interactive methodology lessons
- `get_man_page(section?)` - Comprehensive tool documentation

## Architecture

### Core Components

- **ProjectManager** (`src/project-manager.ts`) - Project lifecycle and metadata
- **PatternManager** (`src/pattern-manager.ts`) - Specification pattern system
- **FlywheelManager** (`src/flywheel-manager.ts`) - Gap analysis and improvement cycles
- **ClaudeClient** (`src/claude-client.ts`) - AI conversation integration

### Methodology Structure

Each project follows this structure:
- `tasks.md` - Phase progress tracking with completion criteria
- `exploration/` - AI-assisted exploration sessions and questions
- `specification/` - Detailed requirements and architecture
- `execution/` - Implementation artifacts
- `feedback/` - Learning capture and retrospectives

## Development

### Project Structure

```
servers/orchestration-framework/
├── src/                    # Core source code
│   ├── commands/          # CLI command implementations
│   ├── mcp/              # MCP server implementation
│   ├── project-manager.ts
│   ├── pattern-manager.ts
│   └── flywheel-manager.ts
├── docs/                  # Methodology documentation
├── patterns/              # Specification templates
├── prompts/              # AI prompt templates
├── tests/                # Test suite
└── mcp_main.ts           # MCP server entry point
```

### Testing

```bash
# Run all tests
deno task test

# Run specific test categories
deno test tests/unit/
deno test tests/integration/
deno test tests/e2e/
```

### Package Dependencies

This server uses shared packages from the monorepo:
- `@packages/mcp-core` - MCP server utilities
- `@packages/claude-client` - Enhanced Claude API client  
- `@packages/common-tools` - Shared MCP tools

## Methodology

### Four-Phase Process

1. **Exploration** - Systematic problem understanding before solutions
2. **Specification** - Transform insights into structured requirements  
3. **Execution** - Implement based on solid understanding
4. **Feedback & Learning** - Capture knowledge for future projects

### Key Principles

- **Time is Not an Artifact**: Phases complete when purpose is fulfilled
- **Systematic Before Reactive**: No shortcuts to execution without proper exploration
- **Real Integration from Start**: Production requirements from beginning
- **Documentation as Asset**: Conversations become organizational knowledge

## Configuration

Set environment variables:

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

The server uses `~/OrchestrationProjects/` for project storage by default.