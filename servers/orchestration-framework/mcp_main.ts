#!/usr/bin/env -S deno run --allow-all
/**
 * Orchestration Framework MCP Server CLI Entry Point
 * Enables conversational access to systematic project methodology through Claude Desktop
 */

import { createOrchestrationMCPServer } from "./src/mcp/server.ts";
import { StdioServerTransport } from "npm:@modelcontextprotocol/sdk/server/stdio.js";

async function main() {
  console.error("🎼 Starting Orchestration Framework MCP Server...");
  console.error(`📁 Working directory: ${Deno.cwd()}`);

  try {
    // Create the MCP server
    const server = await createOrchestrationMCPServer();

    // Create stdio transport for Claude Desktop
    const transport = new StdioServerTransport();

    // Connect the server to stdio
    await server.connect(transport);

    console.error("✅ Orchestration Framework MCP Server running on stdio");
    console.error("📡 Ready for Claude Desktop connections");
    console.error("🔄 Providing conversational access to systematic project methodology");
  } catch (error) {
    console.error(`❌ MCP Server startup failed: ${error}`);
    console.error(`Stack: ${error instanceof Error ? error.stack : 'No stack'}`);
    Deno.exit(1);
  }
}

if (import.meta.main) {
  main();
}