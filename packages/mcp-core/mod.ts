/**
 * @packages/mcp-core - Core MCP server functionality
 * 
 * Provides standardized MCP server creation, transport utilities,
 * and common patterns for building MCP servers.
 */

export { createMCPServer, MCPServerFactory } from "./server.ts";
export { StdioTransport, SocketTransport } from "./transport.ts";
export type {
  MCPServerConfig,
  MCPTool,
  MCPToolHandler,
  MCPToolHandlers,
  MCPServerOptions,
  MCPTransport,
  MCPLogger,
} from "./types.ts";