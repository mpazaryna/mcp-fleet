# MCP Fleet - Python Monorepo

A Python-based monorepo hosting multiple MCP (Model Context Protocol) servers with shared functionality for AI-assisted project management and productivity workflows.

## Structure

```
├── servers/                    # MCP servers
│   ├── tides/                 # Rhythmic workflow management
│   ├── compass/               # Systematic project methodology
│   └── toolkit/               # Essential file operations and utilities
├── packages/                  # Shared libraries
│   ├── mcp_core/              # Core MCP functionality
│   ├── claude_client/         # Anthropic API client
│   └── common_tools/          # Shared MCP tools
└── tests/                     # Comprehensive test suite
```

## Why Monorepo

MCP Fleet uses a monorepo architecture following the same proven pattern as enterprise-grade implementations like Cloudflare's MCP servers:

1. **Shared Infrastructure**: Common MCP protocol handling, utilities
2. **Coordinated Development**: Single repo for easier testing and CI/CD  
3. **Independent Deployment**: Each server can be deployed/versioned separately
4. **Workspace Benefits**: Dependency resolution across the entire ecosystem

## Quick Start

### Development

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Run tests for all packages and servers
uv run pytest

# Run specific server tests
uv run pytest tests/servers/tides/

# Format code
uv run black .

# Lint code
uv run ruff check .

# Type check
uv run mypy .
```

### Docker Deployment

```bash
# Build all servers
docker build -f Dockerfile.all-python --target tides -t mcp-fleet:tides .
docker build -f Dockerfile.all-python --target compass -t mcp-fleet:compass .
docker build -f Dockerfile.all-python --target toolkit -t mcp-fleet:toolkit .

# Run individual server
docker run -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" mcp-fleet:tides
```

## Servers

### Tides

Rhythmic workflow management based on natural tidal patterns for sustainable productivity cycles.

**Features:**
- Create tidal workflows for different time scales
- Flow session management with intensity control
- Report generation (JSON, Markdown, CSV)
- Persistent storage with Docker volume mounting

### Compass

Systematic project methodology through exploration-to-execution phases. Enforces depth and prevents surface-level AI responses.

**Features:**
- 4-phase methodology: Exploration → Specification → Execution → Feedback
- Context preservation and conversation history
- Pattern-based requirements generation
- Task breakdown with priority management

### Toolkit

Essential file operations and utility tools for MCP servers.

**Features:**
- File I/O operations (read, write, create, delete)
- Directory management and listing
- Shared infrastructure for other servers

## Packages

### mcp_core

Core MCP server functionality including:
- MCP server creation factory
- Transport utilities (stdio)
- Type-safe tool definition helpers
- Standardized error handling patterns

### claude_client

Enhanced Anthropic Claude API client with:
- Retry logic and error recovery
- Conversation management
- Streaming response support
- Rate limiting

### common_tools

Reusable MCP tools:
- File operations (read, write, list directories)
- Git operations and project discovery
- Shared utilities used across servers

## Testing

```bash
# Run all tests
uv run pytest

# Run package tests only
uv run pytest tests/packages/

# Run server tests only
uv run pytest tests/servers/

# Run specific tests with coverage
uv run pytest tests/servers/tides/ --cov=servers/tides

# Run integration tests
uv run pytest tests/servers/tides/test_mcp_integration.py
```

## Environment Setup

Requires `ANTHROPIC_API_KEY` environment variable for Claude API integration.

### Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "tides": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--name", "tides-mcp-session",
        "-e", "ANTHROPIC_API_KEY",
        "-v", "/Users/your-username/Documents/TideReports:/app/reports",
        "pazland/mcp-fleet-tides:main"
      ]
    }
  }
}
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make changes following the existing patterns
4. Ensure tests pass: `uv run pytest`
5. Submit a pull request

## License

MIT