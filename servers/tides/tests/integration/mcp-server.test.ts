import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { createMCPServer } from "@packages/mcp-core/mod.ts";
import { tideHandlers, tideTools } from "../../src/tools/tide-tools.ts";
import { reportHandlers, reportTools } from "../../src/tools/report-tools.ts";

Deno.test("MCP Server Integration", async (t) => {
  await t.step("should create server with all tools", () => {
    const serverInfo = {
      name: "tides-test",
      version: "0.1.0",
      description: "Test server",
    };

    const server = createMCPServer({
      serverInfo,
      tools: [...tideTools, ...reportTools],
      handlers: { ...tideHandlers, ...reportHandlers },
    });

    assertExists(server);
  });

  await t.step("should have correct number of tools registered", () => {
    const allTools = [...tideTools, ...reportTools];
    // Verify we have tide tools + report tools
    assertEquals(allTools.filter(t => t.name === "save_tide_report").length, 1);
    assertEquals(allTools.filter(t => t.name === "export_all_tides").length, 1);
  });

  await t.step("should have all handlers registered", () => {
    const allHandlers = { ...tideHandlers, ...reportHandlers };
    assertExists(allHandlers.save_tide_report);
    assertExists(allHandlers.export_all_tides);
    assertExists(allHandlers.create_tide);
    assertExists(allHandlers.list_tides);
    assertExists(allHandlers.flow_tide);
  });
});

Deno.test("Tool Name Uniqueness", async (t) => {
  await t.step("should not have duplicate tool names", () => {
    const allTools = [...tideTools, ...reportTools];
    const toolNames = allTools.map(t => t.name);
    const uniqueNames = new Set(toolNames);
    
    assertEquals(toolNames.length, uniqueNames.size, "Duplicate tool names found");
  });
});