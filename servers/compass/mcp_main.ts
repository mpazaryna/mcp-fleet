#!/usr/bin/env deno run --allow-all

/**
 * Compass MCP Server
 * 
 * Systematic project methodology through exploration-to-execution phases.
 * Guides projects through: Exploration → Specification → Execution → Feedback
 */

import { StdioTransport } from "@packages/mcp-core/mod.ts";
import { createCompassServer } from "./src/server.ts";

async function main() {
  console.error("Starting Compass MCP Server...");
  console.error(`Working directory: ${Deno.cwd()}`);

  try {
    const server = await createCompassServer();
    const transport = new StdioTransport();
    
    await transport.connect(server);
    
    console.error("Compass MCP Server connected and ready");
    
    // Keep the process running
    await new Promise(() => {});
  } catch (error) {
    console.error(`Failed to start Compass MCP Server: ${error}`);
    Deno.exit(1);
  }
}

if (import.meta.main) {
  main();
}