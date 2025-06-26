import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import { projectHandlers } from "../../src/tools/project-tools.ts";
import { explorationHandlers } from "../../src/tools/exploration-tools.ts";

Deno.test({
  name: "complete project initialization and exploration workflow",
  permissions: { read: true, write: true, env: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "workflow-test";
    
    try {
      // Step 1: Initialize project
      const initResult = await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(initResult.success, true);
      assertEquals(initResult.project_name, projectName);
      
      // Verify project structure
      const projectPath = join(testDir, projectName);
      assertEquals(await exists(projectPath), true);
      assertEquals(await exists(join(projectPath, ".compass.json")), true);
      
      // Step 2: Start exploration
      const explorationResult = await explorationHandlers.start_exploration({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(explorationResult.project_name, projectName);
      assertEquals(explorationResult.session_number, 1);
      assertEquals(explorationResult.ready_for_conversation, true);
      
      // Step 3: Save exploration session
      const saveResult = await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: "User: What are the main challenges?\nAssistant: Let's explore that systematically...",
        session_summary: "Identified key challenges",
        projectsDir: testDir,
      });
      
      assertEquals(saveResult.conversation_saved, true);
      assertEquals(saveResult.session_number, 1);
      
      // Step 4: Get project context
      const contextResult = await explorationHandlers.get_project_context({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(contextResult.total_sessions, 1);
      assertEquals(contextResult.conversation_history.length, 1);
      
      // Step 5: Start second exploration session
      const secondExploration = await explorationHandlers.start_exploration({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(secondExploration.session_number, 2);
      assertEquals(secondExploration.previous_context.includes("SESSION 1 INSIGHTS"), true);
      
      // Step 6: Complete exploration phase
      const completeResult = await explorationHandlers.complete_exploration_phase({
        project_name: projectName,
        completion_reason: "All key areas explored",
        projectsDir: testDir,
      });
      
      assertEquals(completeResult.exploration_completed, true);
      
      // Verify phase transition
      const metadata = JSON.parse(await Deno.readTextFile(join(projectPath, ".compass.json")));
      assertEquals(metadata.currentPhase, "specification");
      assertExists(metadata.explorationCompletedDate);
      
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "list projects shows correct status after exploration",
  permissions: { read: true, write: true, env: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    
    try {
      // Create two projects
      await projectHandlers.init_project({
        name: "project-1",
        projectsDir: testDir,
      });
      
      await projectHandlers.init_project({
        name: "project-2",
        projectsDir: testDir,
      });
      
      // Add exploration to project-1
      await explorationHandlers.save_exploration_session({
        project_name: "project-1",
        conversation_content: "Exploration content",
        projectsDir: testDir,
      });
      
      // Complete exploration for project-1
      await explorationHandlers.complete_exploration_phase({
        project_name: "project-1",
        projectsDir: testDir,
      });
      
      // List projects
      const listResult = await projectHandlers.list_projects({
        projectsDir: testDir,
      });
      
      assertEquals(listResult.total, 2);
      
      const project1 = listResult.projects.find(p => p.name === "project-1");
      const project2 = listResult.projects.find(p => p.name === "project-2");
      
      assertExists(project1);
      assertExists(project2);
      
      assertEquals(project1.current_phase, "specification");
      assertEquals(project2.current_phase, "exploration");
      
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});