import { createToolsServer } from "@mizchi/mcp-helper";
import type { MCPServerOptions, MCPLogger } from "./types.ts";

/**
 * Creates a standardized MCP server with error handling and logging
 */
export function createMCPServer(options: MCPServerOptions) {
  const { serverInfo, tools, handlers } = options;
  
  // Wrap handlers with error handling
  const wrappedHandlers: Record<string, any> = {};
  
  for (const [toolName, handler] of Object.entries(handlers)) {
    wrappedHandlers[toolName] = async (args: any) => {
      try {
        return await handler(args);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error(`[MCP Server] Error in ${toolName}:`, errorMessage);
        throw error;
      }
    };
  }
  
  return createToolsServer(serverInfo, tools, wrappedHandlers);
}

/**
 * Standard MCP server factory with common setup
 */
export class MCPServerFactory {
  constructor(private logger?: MCPLogger) {}
  
  create(options: MCPServerOptions) {
    if (this.logger) {
      this.logger.info(`Creating MCP server: ${options.serverInfo.name} v${options.serverInfo.version}`);
    }
    
    return createMCPServer(options);
  }
}