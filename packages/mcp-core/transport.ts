import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import type { MCPTransport } from "./types.ts";

/**
 * Standard stdio transport for MCP servers
 */
export class StdioTransport implements MCPTransport {
  private transport: StdioServerTransport;
  private server?: Server;
  
  constructor() {
    this.transport = new StdioServerTransport();
  }
  
  async connect(server?: Server): Promise<void> {
    if (server) {
      this.server = server;
      await this.server.connect(this.transport);
    }
  }
  
  async close(): Promise<void> {
    if (this.server) {
      await this.server.close();
    }
  }
}

/**
 * Socket transport for MCP servers (for testing/development)
 */
export class SocketTransport implements MCPTransport {
  constructor(private port: number) {}
  
  async connect(): Promise<void> {
    // Implementation for socket-based transport
    console.log(`Socket transport would connect on port ${this.port}`);
  }
  
  async close(): Promise<void> {
    console.log("Socket transport closing");
  }
}