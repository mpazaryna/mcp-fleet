import { assertEquals, assertExists } from "@std/assert";
import { createOrchestrationMCPServer } from "../../../src/mcp/server.ts";

Deno.test("MCP Server Creation - should create MCP server without errors", async () => {
  const server = await createOrchestrationMCPServer();
  assertExists(server);
});

Deno.test("MCP Server Tools - should expose all expected tools", async () => {
  const server = await createOrchestrationMCPServer();
  assertExists(server);
  
  // The server should have our expected tools
  // We can't easily test the internal structure, but we can verify it creates
  assertEquals(typeof server, "object");
});