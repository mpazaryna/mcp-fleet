# @packages/mcp-core

Core MCP (Model Context Protocol) server functionality for building standardized MCP servers.

## Features

- Server creation factory with error handling
- Standard transport utilities (stdio, socket)
- Type-safe tool definitions
- Consistent error handling and logging

## Usage

```typescript
import { createMCPServer, StdioTransport } from "@packages/mcp-core/mod.ts";
import { z } from "zod";

// Define your tools
const tools = [
  {
    name: "example_tool",
    description: "An example tool",
    inputSchema: z.object({
      message: z.string(),
    }),
    outputSchema: z.object({
      result: z.string(),
    }),
  },
];

// Define handlers
const handlers = {
  example_tool: async (args: { message: string }) => {
    return { result: `Processed: ${args.message}` };
  },
};

// Create server
const server = createMCPServer({
  serverInfo: {
    name: "my-mcp-server",
    version: "1.0.0",
  },
  tools,
  handlers,
});

// Connect transport
const transport = new StdioTransport();
await server.connect(transport);
```

## API

### `createMCPServer(options)`

Creates a new MCP server with standardized setup.

- `options.serverInfo` - Server metadata (name, version)
- `options.tools` - Array of tool definitions
- `options.handlers` - Object mapping tool names to handler functions

### Transport Classes

- `StdioTransport` - Standard input/output transport for Claude Desktop
- `SocketTransport` - Socket-based transport for testing/development

### Types

- `MCPServerConfig` - Server configuration interface
- `MCPTool` - Tool definition with schemas
- `MCPToolHandler` - Handler function type
- `MCPTransport` - Transport interface