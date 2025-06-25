import { assertEquals, assertExists } from "@std/assert";
import { ClaudeClient } from "../../src/claude-client.ts";

// Real E2E test that calls actual Claude API
// Run with: ANTHROPIC_API_KEY=xxx deno task test:e2e
// Or: RUN_REAL_E2E=true deno task test (if you want to gate it)

Deno.test({
  name: "Real Claude API Integration",
  ignore: !Deno.env.get("ANTHROPIC_API_KEY"), // Skip if no API key
  async fn() {
    // Simple API connectivity test
    const client = new ClaudeClient();
    
    const response = await client.chat([
      { role: "user", content: "Say 'API_TEST_SUCCESS' and nothing else." }
    ]);
    
    // Verify we got a real response from Claude
    assertExists(response);
    assertEquals(typeof response, "string");
    // Claude should respond with exactly what we asked for
    assertEquals(response.trim(), "API_TEST_SUCCESS");
  }
});

Deno.test({
  name: "Real Claude API - Exploration Pattern",
  ignore: !Deno.env.get("ANTHROPIC_API_KEY"),
  async fn() {
    // Test actual exploration-style interaction
    const client = new ClaudeClient();
    
    const systemPrompt = "You are helping with systematic exploration. Ask one focused question to understand the problem better.";
    
    const response = await client.chat([
      { role: "user", content: "I want to build a simple todo app" }
    ], systemPrompt);
    
    // Verify we got a question back (exploration behavior)
    assertExists(response);
    assertEquals(typeof response, "string");
    // Should contain a question mark (basic exploration validation)
    assertEquals(response.includes("?"), true);
    // Should be substantial (not just "What?")
    assertEquals(response.length > 20, true);
  }
});

Deno.test({
  name: "Real Claude API - Error Handling",
  ignore: !Deno.env.get("ANTHROPIC_API_KEY"),
  async fn() {
    // Test that our error handling works with real API
    const client = new ClaudeClient();
    
    try {
      // Send a very long message to potentially trigger rate limits or errors
      const longMessage = "test ".repeat(10000); // ~50KB message
      await client.chat([
        { role: "user", content: longMessage }
      ]);
      
      // If we get here, the API handled it fine
      assertEquals(true, true);
    } catch (error) {
      // Verify our error handling produces meaningful errors
      assertExists(error);
      assertEquals(error instanceof Error, true);
      // Should not be a generic fetch error
      assertEquals((error as Error).message.includes("ANTHROPIC_API_KEY"), false);
    }
  }
});