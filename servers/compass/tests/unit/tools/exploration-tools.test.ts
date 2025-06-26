import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import { explorationTools, explorationHandlers } from "../../../src/tools/exploration-tools.ts";
import { projectHandlers } from "../../../src/tools/project-tools.ts";

Deno.test("exploration tools are properly defined", () => {
  assertEquals(explorationTools.length, 4);
  
  const toolNames = explorationTools.map(t => t.name);
  assertEquals(toolNames, [
    "start_exploration",
    "save_exploration_session", 
    "get_project_context",
    "complete_exploration_phase"
  ]);
});

Deno.test("start_exploration tool has correct schema", () => {
  const tool = explorationTools.find(t => t.name === "start_exploration");
  assertExists(tool);
  assertEquals(tool.description, "Begin or continue systematic exploration phase for a project");
  assertExists(tool.inputSchema);
  assertExists(tool.outputSchema);
});

Deno.test({
  name: "start_exploration initializes first session correctly",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "test-project";
    
    try {
      // First create a project
      await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      // Start exploration
      const result = await explorationHandlers.start_exploration({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(result.project_name, projectName);
      assertEquals(result.session_number, 1);
      assertEquals(result.ready_for_conversation, true);
      assertExists(result.focus_task);
      assertExists(result.guidance);
      assertEquals(result.previous_context, "No previous sessions.");
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "save_exploration_session creates conversation file",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "test-project";
    
    try {
      // Create project
      await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      // Save exploration session
      const conversationContent = "User: What is the main problem?\nAssistant: Let me help explore that...";
      const result = await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: conversationContent,
        session_summary: "Initial problem exploration",
        projectsDir: testDir,
      });
      
      assertEquals(result.conversation_saved, true);
      assertEquals(result.session_number, 1);
      assertEquals(result.file_path, "exploration/conversation-1.md");
      
      // Verify file exists and contains content
      const projectPath = join(testDir, projectName);
      const conversationPath = join(projectPath, "exploration", "conversation-1.md");
      assertEquals(await exists(conversationPath), true);
      
      const savedContent = await Deno.readTextFile(conversationPath);
      assertEquals(savedContent.includes(conversationContent), true);
      assertEquals(savedContent.includes("Initial problem exploration"), true);
      
      // Verify metadata updated
      const metadata = JSON.parse(await Deno.readTextFile(join(projectPath, ".compass.json")));
      assertEquals(metadata.sessionCount, 1);
      assertExists(metadata.lastSessionDate);
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "get_project_context loads conversation history",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "test-project";
    
    try {
      // Create project
      await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      // Save two exploration sessions
      await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: "First conversation",
        projectsDir: testDir,
      });
      
      await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: "Second conversation",
        projectsDir: testDir,
      });
      
      // Get project context
      const result = await explorationHandlers.get_project_context({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(result.project_name, projectName);
      assertEquals(result.total_sessions, 2);
      assertEquals(result.conversation_history.length, 2);
      assertEquals(result.conversation_history[0].session_number, 1);
      assertEquals(result.conversation_history[1].session_number, 2);
      assertExists(result.current_context);
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "complete_exploration_phase marks all tasks complete",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "test-project";
    
    try {
      // Create project
      await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      // Complete exploration phase
      const result = await explorationHandlers.complete_exploration_phase({
        project_name: projectName,
        completion_reason: "Sufficient understanding achieved",
        projectsDir: testDir,
      });
      
      assertEquals(result.exploration_completed, true);
      assertEquals(result.completion_reason, "Sufficient understanding achieved");
      
      // Verify metadata updated
      const projectPath = join(testDir, projectName);
      const metadata = JSON.parse(await Deno.readTextFile(join(projectPath, ".compass.json")));
      assertEquals(metadata.currentPhase, "specification");
      assertExists(metadata.explorationCompletedDate);
      
      // Verify completion record created
      const completionPath = join(projectPath, "exploration", "completion-override.md");
      assertEquals(await exists(completionPath), true);
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});