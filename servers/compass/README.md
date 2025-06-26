# Compass MCP Server

Systematic project methodology through exploration-to-execution phases. This server is an optimized reimplementation of the orchestration-framework server, built using Test-Driven Development (TDD) and leveraging the monorepo's shared packages.

## Overview

Compass guides projects through four systematic phases:
1. **Exploration** - Deep understanding of the problem space
2. **Specification** - Transform insights into structured requirements
3. **Execution** - Implement solutions based on solid understanding
4. **Feedback & Learning** - Capture knowledge for future projects

## Key Principles

- **Explore before executing** - Prevents surface-level solutions
- **Systematic methodology** - Enforced progression through phases
- **Knowledge preservation** - All exploration and insights are saved
- **Continuous improvement** - Flywheel pattern for iterative enhancement

## Development Approach

This server is built using strict TDD methodology:
- Every feature starts with a failing test
- Minimal implementation to pass tests
- Refactor for optimization while maintaining test coverage
- E2E tests verify real file operations

## Tools

### Project Management
- `init_project` - Initialize a new Compass project
- `list_projects` - List all available projects
- `get_project_status` - Get detailed project status

### Exploration (Coming Soon)
- `start_exploration` - Begin systematic exploration
- `save_exploration_session` - Save conversation content
- `get_project_context` - Load previous explorations

### Specification (Coming Soon)
- `generate_specification` - Create specs from insights
- `list_patterns` - Available specification patterns
- `complete_exploration_phase` - Mark exploration complete

### Feedback (Coming Soon)
- `check_flywheel_opportunities` - Detect improvement areas
- `write_feedback` - Record learnings and reflections

## Testing

```bash
# Run all tests
deno task test

# Run unit tests only
deno task test:unit

# Run integration tests
deno task test:integration

# Run E2E tests
deno task test:e2e

# Watch mode for development
deno task test:watch
```

## Architecture

The server is structured for maintainability:
- `/src/tools/` - Modular tool implementations
- `/src/managers/` - Business logic managers
- `/tests/unit/` - Unit tests for each component
- `/tests/integration/` - Cross-component tests
- `/tests/e2e/` - Full workflow tests with file I/O

## Usage

Start the server:
```bash
deno task start
```

The server runs on stdio transport for Claude Desktop integration.