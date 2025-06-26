import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { createCompassServer, getServerInfo } from "../../src/server.ts";

Deno.test("creates MCP server with correct configuration", async () => {
  const server = await createCompassServer();
  
  assertExists(server);
  assertExists(server.connect);
  assertEquals(typeof server.connect, "function");
});

Deno.test("server has correct name and version", () => {
  const serverInfo = getServerInfo();
  
  assertEquals(serverInfo.name, "compass");
  assertEquals(serverInfo.version, "1.0.0");
  assertEquals(serverInfo.description, "Systematic project methodology through exploration-to-execution phases");
});