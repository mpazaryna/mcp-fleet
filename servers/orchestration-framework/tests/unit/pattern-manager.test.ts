import { assertEquals, assertExists, assertRejects } from "@std/assert";
import { PatternManager } from "../../src/pattern-manager.ts";
import { setupTestProject, TestHelpers } from "../utils/test-helpers.ts";

Deno.test("PatternManager - Pattern Loading", async (t) => {
  const testProject = await setupTestProject("pattern-test");
  
  try {
    await t.step("should load available patterns from filesystem", async () => {
      const patternManager = new PatternManager();
      const patterns = await patternManager.loadAvailablePatterns();
      
      // Should have at least the built-in patterns
      assertEquals(patterns.length >= 3, true);
      
      const patternNames = patterns.map(p => p.name);
      assertEquals(patternNames.includes("product_requirement_doc"), true);
      assertEquals(patternNames.includes("life_skill_development"), true);
      assertEquals(patternNames.includes("business_process_analysis"), true);
    });

    await t.step("should validate pattern structure and required fields", async () => {
      const patternManager = new PatternManager();
      const patterns = await patternManager.loadAvailablePatterns();
      
      for (const pattern of patterns) {
        assertExists(pattern.name);
        assertExists(pattern.domain);
        assertExists(pattern.description);
        assertExists(pattern.template);
        assertEquals(Array.isArray(pattern.variables), true);
        assertEquals(Array.isArray(pattern.sections), true);
      }
    });

    await t.step("should handle missing or invalid patterns gracefully", async () => {
      const patternManager = new PatternManager();
      
      // Should not throw when pattern doesn't exist
      const result = await patternManager.loadPattern("nonexistent_pattern");
      assertEquals(result, null);
    });

  } finally {
    await testProject.cleanup();
  }
});

Deno.test("PatternManager - Template Processing", async (t) => {
  const testProject = await setupTestProject("template-test");
  
  try {
    await t.step("should substitute variables in pattern templates", async () => {
      const patternManager = new PatternManager();
      
      const template = "# {{PROJECT_NAME}} - {{PATTERN_TYPE}}\n\n{{EXPLORATION_INSIGHTS}}";
      const variables = {
        PROJECT_NAME: "Test Project",
        PATTERN_TYPE: "Product Requirements",
        EXPLORATION_INSIGHTS: "Key insights from exploration"
      };
      
      const result = patternManager.substituteVariables(template, variables);
      
      assertEquals(result.includes("Test Project"), true);
      assertEquals(result.includes("Product Requirements"), true);
      assertEquals(result.includes("Key insights from exploration"), true);
      assertEquals(result.includes("{{"), false); // No unreplaced variables
    });

    await t.step("should map exploration insights to pattern sections", async () => {
      const patternManager = new PatternManager();
      
      const explorationContent = `
# Exploration Session 1: Test Project

**Claude**: What are the main user pain points?
**You**: Users struggle with slow loading times and confusing navigation.
**Claude**: What are the core features needed?
**You**: Fast search, intuitive UI, and mobile support.
      `;
      
      const insights = await patternManager.extractInsights(explorationContent);
      
      assertEquals(insights.userPainPoints.toLowerCase().includes("slow loading times"), true);
      assertEquals(insights.coreFeatures.toLowerCase().includes("fast search"), true);
      assertEquals(insights.coreFeatures.toLowerCase().includes("mobile support"), true);
    });

    await t.step("should handle empty or malformed exploration content", async () => {
      const patternManager = new PatternManager();
      
      const emptyInsights = await patternManager.extractInsights("");
      assertExists(emptyInsights);
      assertEquals(typeof emptyInsights.userPainPoints, "string");
      assertEquals(typeof emptyInsights.coreFeatures, "string");
    });

  } finally {
    await testProject.cleanup();
  }
});

Deno.test("PatternManager - Pattern Generation", async (t) => {
  const testProject = await setupTestProject("generation-test");
  
  try {
    await t.step("should generate complete specification from pattern and insights", async () => {
      const patternManager = new PatternManager();
      
      const patternName = "product_requirement_doc";
      const projectName = "Mobile Task Manager";
      const explorationContent = `
# Exploration Session 1: Mobile Task Manager

**Claude**: What problem are you solving?
**You**: People need a simple way to manage tasks on mobile devices.
**Claude**: What are the key features?
**You**: Task creation, due dates, notifications, and offline sync.
      `;
      
      const specification = await patternManager.generateSpecification(
        patternName,
        projectName,
        explorationContent
      );
      
      assertExists(specification);
      assertEquals(specification.includes(projectName), true);
      assertEquals(specification.toLowerCase().includes("task creation"), true);
      assertEquals(specification.includes("Problem Statement"), true);
      assertEquals(specification.includes("User Stories"), true);
    });

    await t.step("should preserve exploration content and add pattern structure", async () => {
      const patternManager = new PatternManager();
      
      const result = await patternManager.generateSpecification(
        "life_skill_development",
        "Learn Data Science",
        "I want to transition to data science but lack math background."
      );
      
      assertEquals(result.includes("Learn Data Science"), true);
      assertEquals(result.toLowerCase().includes("math background"), true);
      assertEquals(result.includes("Current State Assessment"), true);
      assertEquals(result.includes("Learning Curriculum"), true);
    });

  } finally {
    await testProject.cleanup();
  }
});