#!/usr/bin/env deno run --allow-all

/**
 * Toolkit MCP Server
 *
 * Shared infrastructure and file I/O utilities for the MCP Fleet.
 * Provides common tools for file operations across all servers.
 */

import { createMCPServer, StdioTransport } from "@packages/mcp-core/mod.ts";
import { fileTools, fileHandlers } from "./src/tools/file-tools.ts";

// Server configuration
const serverInfo = {
  name: "toolkit",
  version: "1.0.0",
  description: "Shared toolkit providing file I/O and utilities for MCP Fleet servers",
};

async function main() {
  console.error("🔧 Starting Toolkit MCP Server...");

  try {
    // Create the MCP server
    const server = createMCPServer({
      serverInfo,
      tools: [...fileTools],
      handlers: { ...fileHandlers },
    });

    // Connect to stdio transport
    const transport = new StdioTransport();
    await transport.connect(server);

    console.error("🔧 Toolkit MCP Server connected and ready");

    // Keep the process running
    await new Promise(() => {}); // Run forever
  } catch (error) {
    console.error("❌ Failed to start Toolkit MCP Server:", error);
    Deno.exit(1);
  }
}

if (import.meta.main) {
  main();
}