# MCP Fleet - Deno Monorepo

A Deno-based monorepo hosting multiple MCP (Model Context Protocol) servers with shared functionality.

## Structure

```
├── servers/                    # MCP servers
│   ├── orchestration-framework/  # Orchestration Framework MCP server
│   └── tides/                   # Tides MCP server
├── packages/                   # Shared libraries
│   ├── mcp-core/               # Core MCP functionality
│   ├── claude-client/          # Anthropic API client
│   └── common-tools/           # Shared MCP tools
└── projects/                   # Orchestration projects (shared data)
```

## Quick Start

### Development

```bash
# Install Deno (if not already installed)
curl -fsSL https://deno.land/install.sh | sh

# Run tests for all packages and servers
deno task test

# Run specific server
cd servers/orchestration-framework
deno task start

# Format code
deno task fmt

# Lint code
deno task lint

# Type check
deno task check
```

### Adding a New Server

1. Create directory: `mkdir -p servers/your-server/{src,tests}`
2. Add to workspace in root `deno.json`
3. Create `servers/your-server/deno.json` with server config
4. Implement `servers/your-server/mcp_main.ts`

## Servers

### Orchestration Framework

A systematic methodology for knowledge work that combines human strategic thinking with AI execution capabilities.

[Documentation](./servers/orchestration-framework/README.md)

### Tides

Coming soon - a new MCP server for tidal workflow management.

## Packages

### @packages/mcp-core

Core MCP server functionality including:
- Server creation factory
- Transport utilities (stdio, socket)
- Error handling middleware
- Common MCP tool patterns

### @packages/claude-client

Shared Anthropic Claude API client with:
- Retry logic and rate limiting
- Streaming response support
- Conversation management
- Multiple model support

### @packages/common-tools

Reusable MCP tools:
- File operations (read, write, list)
- Project discovery
- Git operations
- Directory management

## Testing

```bash
# Run all tests
deno task test

# Run package tests only
deno task test:packages

# Run server tests only
deno task test:servers

# Run specific package tests
deno test packages/mcp-core/

# Run with coverage
deno test --coverage
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make changes following the existing patterns
4. Ensure tests pass
5. Submit a pull request

## License

MIT