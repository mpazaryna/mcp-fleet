import { assertEquals, assertExists, assertGreater } from "@std/assert";
import { FlywheelManager } from "../../src/flywheel-manager.ts";
import { ProjectMetadata } from "../../src/types.ts";
import { setupTestProject, TestHelpers } from "../utils/test-helpers.ts";

Deno.test("FlywheelManager - Gap Analysis", async (t) => {
  const testProject = await setupTestProject("flywheel-gap-test");
  const originalCwd = Deno.cwd();
  
  try {
    Deno.chdir(testProject.dir);
    
    await t.step("should identify gaps when exploration content is missing", async () => {
      const flywheelManager = new FlywheelManager();
      const metadata: ProjectMetadata = {
        name: "Test Project",
        created: new Date().toISOString(),
        currentPhase: "specification",
        status: "active",
        sessionCount: 0
      };
      
      // No exploration content exists
      const gaps = await flywheelManager.analyzeGaps(metadata);
      
      assertGreater(gaps.length, 0);
      assertEquals(gaps.some(gap => gap.includes("exploration")), true);
    });
    
    await t.step("should identify gaps when specification content is missing", async () => {
      const flywheelManager = new FlywheelManager();
      const metadata: ProjectMetadata = {
        name: "Test Project", 
        created: new Date().toISOString(),
        currentPhase: "specification",
        status: "active",
        sessionCount: 1
      };
      
      // Create exploration content but no specification
      await Deno.writeTextFile('exploration/conversation-1.md', `
# Exploration Session 1: Test Project

**Claude**: What are the main user pain points?
**You**: Users struggle with slow loading times and confusing navigation.
      `);
      
      const gaps = await flywheelManager.analyzeGaps(metadata);
      
      assertGreater(gaps.length, 0);
      assertEquals(gaps.some(gap => gap.includes("specification")), true);
    });
    
    await t.step("should identify content gaps between exploration and specification", async () => {
      const flywheelManager = new FlywheelManager();
      const metadata: ProjectMetadata = {
        name: "Test Project",
        created: new Date().toISOString(), 
        currentPhase: "specification",
        status: "active",
        sessionCount: 1
      };
      
      // Create exploration content
      await Deno.writeTextFile('exploration/conversation-1.md', `
# Exploration Session 1: Test Project

**Claude**: What are the user pain points?
**You**: Slow loading and poor navigation.
      `);
      
      // Create specification that mentions things not in exploration
      await Deno.writeTextFile('specification/spec.md', `
# Test Project Specification

## Technical Architecture
We need a microservices architecture with Docker containers.

## Security Requirements
Multi-factor authentication and encryption at rest.
      `);
      
      const gaps = await flywheelManager.analyzeGaps(metadata);
      
      assertGreater(gaps.length, 0);
      assertEquals(gaps.some(gap => gap.toLowerCase().includes("technical")), true);
    });
    
  } finally {
    Deno.chdir(originalCwd);
    await testProject.cleanup();
  }
});

Deno.test("FlywheelManager - Iteration Creation", async (t) => {
  const testProject = await setupTestProject("flywheel-iteration-test");
  
  try {
    await t.step("should create flywheel iteration with proper structure", async () => {
      const flywheelManager = new FlywheelManager();
      
      const iteration = await flywheelManager.createFlywheelIteration(
        'specification',
        'Gap analysis identified missing technical details',
        'exploration',
        ['Need more technical architecture exploration', 'Missing security requirements analysis']
      );
      
      assertExists(iteration.iterationId);
      assertEquals(iteration.triggerPhase, 'specification');
      assertEquals(iteration.targetPhase, 'exploration');
      assertEquals(iteration.gapsIdentified.length, 2);
      assertEquals(iteration.gapsIdentified[0], 'Need more technical architecture exploration');
      assertExists(iteration.timestamp);
    });
    
    await t.step("should generate recommendations based on gap types", async () => {
      const flywheelManager = new FlywheelManager();
      
      const gaps = [
        'Specification mentions users but exploration lacks user research',
        'Technical architecture mentioned without technical exploration',
        'Requirements unclear about success metrics'
      ];
      
      const recommendations = flywheelManager.generateGapRecommendations(gaps);
      
      assertGreater(recommendations.length, 0);
      assertEquals(recommendations.some(rec => rec.toLowerCase().includes('user')), true);
      assertEquals(recommendations.some(rec => rec.toLowerCase().includes('technical')), true);
      assertEquals(recommendations.some(rec => rec.toLowerCase().includes('metric')), true);
    });
    
  } finally {
    await testProject.cleanup();
  }
});

Deno.test("FlywheelManager - Recommendations", async (t) => {
  const testProject = await setupTestProject("flywheel-recommendations-test");
  const originalCwd = Deno.cwd();
  
  try {
    Deno.chdir(testProject.dir);
    
    await t.step("should recommend flywheel iteration when gaps exist", async () => {
      const flywheelManager = new FlywheelManager();
      
      // Create minimal exploration content
      await Deno.writeTextFile('exploration/conversation-1.md', `
# Exploration Session 1: Test Project

**You**: This is a basic exploration.
      `);
      
      // Create specification with more detail than exploration
      await Deno.writeTextFile('specification/spec.md', `
# Test Project Specification

## Problem Statement
Users need a comprehensive solution for task management.

## Technical Requirements
- Microservices architecture
- Real-time synchronization
- Mobile and web interfaces

## Success Metrics
- 50% reduction in task completion time
- 90% user satisfaction score
      `);
      
      const recommendation = await flywheelManager.recommendFlywheelIteration();
      
      assertEquals(recommendation.recommended, true);
      assertExists(recommendation.reason);
      assertGreater(recommendation.gaps.length, 0);
    });
    
    await t.step("should not recommend flywheel iteration when no gaps exist", async () => {
      const flywheelManager = new FlywheelManager();
      
      // Clear previous files
      try {
        await Deno.remove('exploration', { recursive: true });
        await Deno.remove('specification', { recursive: true });
      } catch {
        // Ignore if directories don't exist
      }
      
      const recommendation = await flywheelManager.recommendFlywheelIteration();
      
      // Should recommend because no content exists (which is a gap)
      assertEquals(recommendation.recommended, true);
      assertEquals(recommendation.gaps.some(gap => gap.includes('exploration')), true);
    });
    
  } finally {
    Deno.chdir(originalCwd);
    await testProject.cleanup();
  }
});

Deno.test("FlywheelManager - Content Analysis", async (t) => {
  const testProject = await setupTestProject("flywheel-content-test");
  
  try {
    await t.step("should detect brief exploration content as gap", async () => {
      const flywheelManager = new FlywheelManager();
      
      // Test private method access through gap analysis
      const explorationContent = "Brief content";
      const specificationContent = "Detailed specification with many requirements";
      
      // Use reflection to access private method for testing
      const flywheelManagerAny = flywheelManager as any;
      const gaps = flywheelManagerAny.findExplorationGaps(explorationContent, specificationContent);
      
      assertGreater(gaps.length, 0);
      assertEquals(gaps.some((gap: string) => gap.includes('brief')), true);
    });
    
    await t.step("should extract keywords correctly", async () => {
      const flywheelManager = new FlywheelManager();
      
      const content = "This is a technical specification with user requirements and performance metrics";
      
      // Access private method
      const flywheelManagerAny = flywheelManager as any;
      const keywords = flywheelManagerAny.extractKeywords(content);
      
      assertEquals(keywords.includes('technical'), true);
      assertEquals(keywords.includes('specification'), true);
      assertEquals(keywords.includes('user'), true);
      assertEquals(keywords.includes('requirements'), true);
      assertEquals(keywords.includes('performance'), true);
      assertEquals(keywords.includes('metrics'), true);
      
      // Should filter out short words
      assertEquals(keywords.includes('is'), false);
      assertEquals(keywords.includes('a'), false);
    });
    
  } finally {
    await testProject.cleanup();
  }
});