import { assertEquals, assertExists, assertGreater } from "@std/assert";
import { exists } from "@std/fs";
import { setupTestProject, TestHelpers } from "../utils/test-helpers.ts";
import { FlywheelManager } from "../../src/flywheel-manager.ts";
import { ProjectManager } from "../../src/project-manager.ts";
import { ProjectMetadata } from "../../src/types.ts";

Deno.test("Flywheel Integration - End-to-End Cycle", async (t) => {
  const testProject = await setupTestProject("flywheel-e2e-test");
  const originalCwd = Deno.cwd();
  
  try {
    Deno.chdir(testProject.dir);
    
    await t.step("should complete full flywheel cycle from gap detection to task creation", async () => {
      // Initialize project metadata
      const metadata: ProjectMetadata = {
        name: "Flywheel Test Project",
        created: new Date().toISOString(),
        currentPhase: "specification",
        status: "active",
        sessionCount: 1
      };
      
      await Deno.writeTextFile('.orchestration.json', JSON.stringify(metadata, null, 2));
      
      // Create initial tasks file
      const initialTasks = `# Task Management: Flywheel Test Project

## Exploration Tasks
- [x] Initial problem exploration
- [x] User research basics

## Phase Status
- **Current Phase**: specification
- **Status**: Ready for specification
- **Next Action**: deno task specify
`;
      
      await Deno.writeTextFile('tasks.md', initialTasks);
      
      // Create exploration content with some gaps
      await Deno.writeTextFile('exploration/conversation-1.md', `
# Exploration Session 1: Flywheel Test Project

**Claude**: What problem are you trying to solve?
**You**: Users struggle with organizing their daily tasks efficiently.

**Claude**: Who are your target users?
**You**: Busy professionals and students who need better productivity tools.
      `);
      
      // Create specification that goes beyond exploration
      await Deno.writeTextFile('specification/spec.md', `
# Flywheel Test Project Specification

## Problem Statement
Users need an advanced task management system with real-time collaboration.

## Technical Architecture
- Microservices backend with Kubernetes
- React frontend with TypeScript
- PostgreSQL database with Redis caching
- WebSocket connections for real-time features

## Security Requirements
- OAuth 2.0 authentication
- End-to-end encryption for sensitive data
- RBAC authorization system

## Performance Requirements
- Sub-100ms response times
- Support for 10,000+ concurrent users
- 99.9% uptime SLA
      `);
      
      // Analyze gaps using FlywheelManager
      const flywheelManager = new FlywheelManager();
      const gaps = await flywheelManager.analyzeGaps(metadata);
      
      // Should identify gaps between simple exploration and detailed specification
      assertGreater(gaps.length, 0);
      
      // Create flywheel iteration
      const iteration = await flywheelManager.createFlywheelIteration(
        'specification',
        'Gap analysis identified areas needing additional exploration',
        'exploration',
        gaps
      );
      
      assertExists(iteration.iterationId);
      assertEquals(iteration.gapsIdentified.length, gaps.length);
      
      // Record iteration in metadata
      await flywheelManager.recordFlywheelIteration(iteration);
      
      // Verify metadata was updated
      const updatedMetadata = await ProjectManager.getProjectMetadata();
      assertExists(updatedMetadata);
      assertExists(updatedMetadata.flywheelIterations);
      assertEquals(updatedMetadata.flywheelIterations!.length, 1);
      assertEquals(updatedMetadata.flywheelIterations![0].iterationId, iteration.iterationId);
      assertEquals(updatedMetadata.cycleCount, 1);
      
      // Simulate adding new exploration tasks based on gaps
      const { explorationTasks } = await ProjectManager.parseTasksFile();
      const originalTaskCount = explorationTasks.length;
      
      // Add tasks for identified gaps (simulate what CLI would do)
      for (const gap of gaps.slice(0, 2)) { // Just add first 2 gaps for test
        explorationTasks.push({
          completed: false,
          text: `Address gap: ${gap}`
        });
      }
      
      await ProjectManager.updateTasksFile(explorationTasks);
      
      // Verify tasks were added
      const { explorationTasks: updatedTasks } = await ProjectManager.parseTasksFile();
      assertGreater(updatedTasks.length, originalTaskCount);
      
      // Verify new tasks contain gap references
      const newTasks = updatedTasks.slice(originalTaskCount);
      assertEquals(newTasks.every(task => task.text.includes('Address gap:')), true);
    });
    
    await t.step("should handle multiple flywheel iterations", async () => {
      const flywheelManager = new FlywheelManager();
      
      // Create second iteration
      const iteration2 = await flywheelManager.createFlywheelIteration(
        'exploration',
        'Additional gaps found during second exploration session',
        'specification',
        ['Need clearer API specifications', 'Missing error handling requirements']
      );
      
      await flywheelManager.recordFlywheelIteration(iteration2);
      
      // Verify multiple iterations are tracked
      const metadata = await ProjectManager.getProjectMetadata();
      assertExists(metadata);
      assertExists(metadata.flywheelIterations);
      assertEquals(metadata.flywheelIterations.length, 2);
      assertEquals(metadata.cycleCount, 2);
      
      // Verify iterations have unique IDs
      const ids = metadata.flywheelIterations.map(iter => iter.iterationId);
      assertEquals(new Set(ids).size, 2); // All unique
    });
    
  } finally {
    Deno.chdir(originalCwd);
    await testProject.cleanup();
  }
});

Deno.test("Flywheel Integration - Recommendation System", async (t) => {
  const testProject = await setupTestProject("flywheel-recommendation-test");
  const originalCwd = Deno.cwd();
  
  try {
    Deno.chdir(testProject.dir);
    
    await t.step("should provide appropriate recommendations based on gap types", async () => {
      const flywheelManager = new FlywheelManager();
      
      // Test different types of gaps
      const userGaps = ['Specification mentions users but exploration lacks user research'];
      const technicalGaps = ['Technical architecture mentioned without technical exploration'];
      const requirementGaps = ['Requirements unclear about functional specifications'];
      const riskGaps = ['Project risks not adequately explored'];
      const metricGaps = ['Success metrics undefined in exploration'];
      
      const userRecs = flywheelManager.generateGapRecommendations(userGaps);
      const technicalRecs = flywheelManager.generateGapRecommendations(technicalGaps);
      const requirementRecs = flywheelManager.generateGapRecommendations(requirementGaps);
      const riskRecs = flywheelManager.generateGapRecommendations(riskGaps);
      const metricRecs = flywheelManager.generateGapRecommendations(metricGaps);
      
      // Verify recommendations are relevant to gap types
      assertEquals(userRecs.some(rec => rec.toLowerCase().includes('user')), true);
      assertEquals(technicalRecs.some(rec => rec.toLowerCase().includes('technical')), true);
      assertEquals(requirementRecs.some(rec => rec.toLowerCase().includes('requirement')), true);
      assertEquals(riskRecs.some(rec => rec.toLowerCase().includes('risk')), true);
      assertEquals(metricRecs.some(rec => rec.toLowerCase().includes('metric')), true);
    });
    
    await t.step("should determine correct target phase for flywheel iteration", async () => {
      // Create project metadata
      const metadata: ProjectMetadata = {
        name: "Target Phase Test",
        created: new Date().toISOString(),
        currentPhase: "specification",
        status: "active",
        sessionCount: 1
      };
      
      await Deno.writeTextFile('.orchestration.json', JSON.stringify(metadata, null, 2));
      
      // Create exploration content
      await Deno.writeTextFile('exploration/conversation-1.md', `
# Exploration Session 1: Target Phase Test

**Claude**: What's the basic problem?
**You**: Need a simple app.
      `);
      
      // Create detailed specification
      await Deno.writeTextFile('specification/spec.md', `
# Target Phase Test Specification

## Detailed Requirements
- Complex user authentication system
- Advanced analytics dashboard
- Real-time notifications
- Multi-tenant architecture
      `);
      
      const flywheelManager = new FlywheelManager();
      const recommendation = await flywheelManager.recommendFlywheelIteration();
      
      assertEquals(recommendation.recommended, true);
      // Should recommend exploration phase since exploration is inadequate for detailed spec
      assertEquals(recommendation.targetPhase, 'exploration');
      assertExists(recommendation.reason);
    });
    
  } finally {
    Deno.chdir(originalCwd);
    await testProject.cleanup();
  }
});

Deno.test("Flywheel Integration - Error Handling", async (t) => {
  const testProject = await setupTestProject("flywheel-error-test");
  const originalCwd = Deno.cwd();
  
  try {
    Deno.chdir(testProject.dir);
    
    await t.step("should handle missing project metadata gracefully", async () => {
      // Create a fresh temp directory without any project setup
      const tempDir = await Deno.makeTempDir({ prefix: "flywheel_no_metadata_" });
      const currentDir = Deno.cwd();
      
      try {
        Deno.chdir(tempDir);
        
        const flywheelManager = new FlywheelManager();
        
        // No .orchestration.json file exists - this should return false with no gaps
        const recommendation = await flywheelManager.recommendFlywheelIteration();
        
        // When no project metadata exists, we can't recommend flywheel iteration
        assertEquals(recommendation.recommended, false);
        assertEquals(recommendation.gaps.length, 0);
        
      } finally {
        Deno.chdir(currentDir);
        await Deno.remove(tempDir, { recursive: true });
      }
    });
    
    await t.step("should handle missing exploration and specification directories", async () => {
      const metadata: ProjectMetadata = {
        name: "Error Test Project",
        created: new Date().toISOString(),
        currentPhase: "specification",
        status: "active",
        sessionCount: 0
      };
      
      await Deno.writeTextFile('.orchestration.json', JSON.stringify(metadata, null, 2));
      
      const flywheelManager = new FlywheelManager();
      const gaps = await flywheelManager.analyzeGaps(metadata);
      
      // Should identify lack of exploration content
      assertGreater(gaps.length, 0);
      assertEquals(gaps.some(gap => gap.includes('exploration')), true);
    });
    
    await t.step("should handle corrupted content files gracefully", async () => {
      const metadata: ProjectMetadata = {
        name: "Corrupted Content Test",
        created: new Date().toISOString(),
        currentPhase: "specification",
        status: "active",
        sessionCount: 1
      };
      
      await Deno.writeTextFile('.orchestration.json', JSON.stringify(metadata, null, 2));
      
      // Create directories but with unreadable content
      await Deno.mkdir('exploration', { recursive: true });
      await Deno.writeTextFile('exploration/conversation-1.md', '');
      
      const flywheelManager = new FlywheelManager();
      const gaps = await flywheelManager.analyzeGaps(metadata);
      
      // Should handle empty files without crashing
      assertExists(gaps);
    });
    
  } finally {
    Deno.chdir(originalCwd);
    await testProject.cleanup();
  }
});