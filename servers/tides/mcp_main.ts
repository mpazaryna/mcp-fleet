#!/usr/bin/env deno run --allow-all

/**
 * Tides MCP Server
 * 
 * A rhythmic workflow management system inspired by natural tidal patterns.
 * Helps create sustainable productivity cycles through tidal flows.
 */

import { createMCPServer, StdioTransport } from "@packages/mcp-core/mod.ts";
import { tideTools, tideHandlers } from "./src/tools/tide-tools.ts";

// Server configuration
const serverInfo = {
  name: "tides",
  version: "0.1.0",
  description: "Rhythmic workflow management through tidal patterns",
};

async function main() {
  console.error("🌊 Starting Tides MCP Server...");
  
  try {
    // Create the MCP server
    const server = createMCPServer({
      serverInfo,
      tools: tideTools,
      handlers: tideHandlers,
    });
    
    // Connect to stdio transport
    const transport = new StdioTransport();
    await transport.connect(server);
    
    console.error("🌊 Tides MCP Server connected and ready");
    
    // Keep the process running
    await new Promise(() => {}); // Run forever
  } catch (error) {
    console.error("❌ Failed to start Tides MCP Server:", error);
    Deno.exit(1);
  }
}

if (import.meta.main) {
  main();
}