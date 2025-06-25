import { assertEquals, assertExists } from "@std/assert";
import { exists } from "@std/fs";
import { setupTestProject, TestHelpers } from "../utils/test-helpers.ts";
import { PatternManager } from "../../src/pattern-manager.ts";
import { ProjectManager } from "../../src/project-manager.ts";

Deno.test("Pattern-based Specification Integration", async (t) => {
  const testProject = await setupTestProject("pattern-spec-test");
  const originalCwd = Deno.cwd();
  
  try {
    Deno.chdir(testProject.dir);

    await t.step("should generate PRD from exploration insights", async () => {
      // Create mock exploration conversation
      const explorationContent = `
# Exploration Session 1: pattern-spec-test

**Claude**: What are the main user pain points you're trying to solve?
**You**: Users struggle with slow loading times and confusing navigation in our current app.

**Claude**: What are the core features you want to build?
**You**: We need fast search, intuitive UI, mobile support, and offline sync capabilities.

**Claude**: What are your main constraints?
**You**: Limited budget, 3-month timeline, and need to integrate with existing legacy systems.

**Claude**: What does success look like for this project?
**You**: 50% reduction in user task completion time and 80% mobile user satisfaction score.
      `;
      
      await Deno.writeTextFile('exploration/conversation-1.md', explorationContent);
      
      // Generate pattern-based specification
      const patternManager = new PatternManager();
      const specification = await patternManager.generateSpecification(
        'product_requirement_doc',
        'pattern-spec-test',
        explorationContent
      );
      
      // Verify specification content
      assertExists(specification);
      assertEquals(specification.includes('pattern-spec-test'), true);
      assertEquals(specification.toLowerCase().includes('slow loading times'), true);
      assertEquals(specification.toLowerCase().includes('fast search'), true);
      assertEquals(specification.toLowerCase().includes('mobile support'), true);
      assertEquals(specification.includes('Problem Statement'), true);
      assertEquals(specification.includes('User Stories'), true);
      assertEquals(specification.includes('Technical Considerations'), true);
    });

    await t.step("should generate life skill plan from exploration insights", async () => {
      const explorationContent = `
# Exploration Session 1: Learn Data Science

**Claude**: What's your current background?
**You**: I have a marketing background but want to transition to data science.

**Claude**: What specific skills do you want to develop?
**You**: Python programming, statistics, machine learning, and data visualization.

**Claude**: What are your main constraints?
**You**: I can only study evenings and weekends, and I have a limited budget for courses.

**Claude**: What's your target timeline?
**You**: I want to be job-ready in 12 months and start applying for junior data scientist roles.
      `;
      
      const patternManager = new PatternManager();
      const specification = await patternManager.generateSpecification(
        'life_skill_development',
        'Learn Data Science',
        explorationContent
      );
      
      assertExists(specification);
      assertEquals(specification.includes('Learn Data Science'), true);
      assertEquals(specification.toLowerCase().includes('marketing background'), true);
      assertEquals(specification.toLowerCase().includes('python programming'), true);
      assertEquals(specification.includes('Current State Assessment'), true);
      assertEquals(specification.includes('Learning Curriculum'), true);
    });

    await t.step("should handle business process analysis pattern", async () => {
      const explorationContent = `
# Exploration Session 1: Sales Process Analysis

**Claude**: What process are you trying to improve?
**You**: Our sales process is taking too long and losing potential customers.

**Claude**: What are the main pain points?
**You**: Manual data entry, poor lead qualification, and lack of follow-up automation.

**Claude**: Who are the key stakeholders?
**You**: Sales team, marketing team, and customer success managers.

**Claude**: What would success look like?
**You**: 30% faster sales cycles and 20% higher conversion rates.
      `;
      
      const patternManager = new PatternManager();
      const specification = await patternManager.generateSpecification(
        'business_process_analysis',
        'Sales Process Analysis',
        explorationContent
      );
      
      assertExists(specification);
      assertEquals(specification.includes('Sales Process Analysis'), true);
      assertEquals(specification.toLowerCase().includes('manual data entry'), true);
      assertEquals(specification.toLowerCase().includes('lead qualification'), true);
      assertEquals(specification.includes('Current State Mapping'), true);
      assertEquals(specification.includes('Optimization Strategy'), true);
    });

    await t.step("should preserve exploration content and add structured sections", async () => {
      const explorationContent = `Simple exploration content for testing.`;
      
      const patternManager = new PatternManager();
      const specification = await patternManager.generateSpecification(
        'product_requirement_doc',
        'Test Project',
        explorationContent
      );
      
      // Should include original exploration content
      assertEquals(specification.includes('Simple exploration content'), true);
      
      // Should add structured sections
      assertEquals(specification.includes('## Problem Statement'), true);
      assertEquals(specification.includes('## User Stories'), true);
      assertEquals(specification.includes('## Technical Considerations'), true);
      assertEquals(specification.includes('## Success Metrics'), true);
    });

  } finally {
    Deno.chdir(originalCwd);
    await testProject.cleanup();
  }
});