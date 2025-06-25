#!/usr/bin/env deno run --allow-all

/**
 * Diagnostic script to verify tides server tools
 */

import { tideTools, tideHandlers } from "../src/tools/tide-tools.ts";
import { reportTools, reportHandlers } from "../src/tools/report-tools.ts";

console.log("🔍 Tides Server Diagnostic Report");
console.log("=================================\n");

console.log("📋 Available Tide Tools:");
tideTools.forEach((tool, index) => {
  console.log(`${index + 1}. ${tool.name} - ${tool.description}`);
});

console.log("\n📊 Available Report Tools:");
reportTools.forEach((tool, index) => {
  console.log(`${index + 1}. ${tool.name} - ${tool.description}`);
});

console.log("\n🔧 Handler Functions:");
console.log("Tide Handlers:", Object.keys(tideHandlers));
console.log("Report Handlers:", Object.keys(reportHandlers));

console.log("\n✅ Total Tools:", tideTools.length + reportTools.length);
console.log("✅ Total Handlers:", Object.keys({...tideHandlers, ...reportHandlers}).length);

// Test tool schemas
console.log("\n🧪 Testing Tool Schemas:");
const testInputs = {
  save_tide_report: {
    tide_id: "test_tide_123",
    format: "json",
    include_history: true
  },
  export_all_tides: {
    format: "markdown",
    filter: {
      active_only: true
    }
  }
};

reportTools.forEach(tool => {
  try {
    const testInput = testInputs[tool.name];
    if (testInput) {
      const result = tool.inputSchema.safeParse(testInput);
      console.log(`- ${tool.name}: ${result.success ? "✅ Valid schema" : "❌ Invalid schema"}`);
      if (!result.success) {
        console.log(`  Error: ${JSON.stringify(result.error.errors)}`);
      }
    }
  } catch (error) {
    console.log(`- ${tool.name}: ❌ Error testing schema:`, error.message);
  }
});

console.log("\n🚀 Server Status: Ready");
console.log("\nIf tools are not appearing in Claude Desktop:");
console.log("1. Check Claude Desktop configuration includes the tides server");
console.log("2. Restart Claude Desktop after adding the server");
console.log("3. Verify the Docker container is running and healthy");
console.log("4. Check Claude Desktop logs for connection errors");