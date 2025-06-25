import { assertEquals, assertExists, assertRejects } from "@std/assert";
import { ProjectManager } from "../../src/project-manager.ts";
import { setupTestProject, TestHelpers } from "../utils/test-helpers.ts";

Deno.test("ProjectManager - parseTasksFile", async (t) => {
  const testProject = await setupTestProject("parse-tasks-test");
  const originalCwd = Deno.cwd();
  
  try {
    Deno.chdir(testProject.dir);

    await t.step("should parse exploration tasks correctly", async () => {
      const { explorationTasks, currentPhase } = await ProjectManager.parseTasksFile();
      
      assertEquals(currentPhase, "exploration");
      assertEquals(explorationTasks.length, 2);
      assertEquals(explorationTasks[0].text, "Test exploration task 1");
      assertEquals(explorationTasks[0].completed, false);
      assertEquals(explorationTasks[1].text, "Test exploration task 2");
      assertEquals(explorationTasks[1].completed, false);
    });

    await t.step("should handle completed tasks", async () => {
      // Update tasks.md to mark first task as completed
      const tasksContent = `# parse-tasks-test - Orchestration Framework Tasks

## Phase 1: Exploration ⏳
- [x] Test exploration task 1
- [ ] Test exploration task 2
- **Artifacts**: \`exploration/questions.md\`, \`exploration/conversation-*.md\`

## Phase 2: Specification 📋
- [ ] Transform insights into structured specifications
`;
      await Deno.writeTextFile("tasks.md", tasksContent);

      const { explorationTasks } = await ProjectManager.parseTasksFile();
      assertEquals(explorationTasks[0].completed, true);
      assertEquals(explorationTasks[1].completed, false);
    });

    await t.step("should throw error when tasks.md doesn't exist", async () => {
      await Deno.remove("tasks.md");
      await assertRejects(() => ProjectManager.parseTasksFile());
    });

  } finally {
    Deno.chdir(originalCwd);
    await testProject.cleanup();
  }
});

Deno.test("ProjectManager - updateTasksFile", async (t) => {
  const testProject = await setupTestProject("update-tasks-test");
  const originalCwd = Deno.cwd();
  
  try {
    Deno.chdir(testProject.dir);

    await t.step("should update tasks with new completion status", async () => {
      const tasks = [
        { completed: true, text: "Completed task" },
        { completed: false, text: "Pending task" }
      ];

      await ProjectManager.updateTasksFile(tasks);
      
      const updatedContent = await Deno.readTextFile("tasks.md");
      const { explorationTasks } = await ProjectManager.parseTasksFile();
      
      assertEquals(explorationTasks[0].completed, true);
      assertEquals(explorationTasks[0].text, "Completed task");
      assertEquals(explorationTasks[1].completed, false);
      assertEquals(explorationTasks[1].text, "Pending task");
    });

    await t.step("should include custom next action", async () => {
      const tasks = [{ completed: false, text: "Test task" }];
      await ProjectManager.updateTasksFile(tasks, "deno task custom");
      
      const content = await Deno.readTextFile("tasks.md");
      assertEquals(content.includes("**Next Action**: `deno task custom`"), true);
    });

  } finally {
    Deno.chdir(originalCwd);
    await testProject.cleanup();
  }
});

Deno.test("ProjectManager - getProjectMetadata", async (t) => {
  const testProject = await setupTestProject("metadata-test");
  const originalCwd = Deno.cwd();
  
  try {
    Deno.chdir(testProject.dir);

    await t.step("should load existing metadata", async () => {
      const metadata = await ProjectManager.getProjectMetadata();
      assertExists(metadata);
      assertEquals(metadata?.name, "metadata-test");
      assertEquals(metadata?.currentPhase, "exploration");
      assertEquals(metadata?.sessionCount, 0);
    });

    await t.step("should return null when no metadata file exists", async () => {
      await Deno.remove(".orchestration.json");
      const metadata = await ProjectManager.getProjectMetadata();
      assertEquals(metadata, null);
    });

  } finally {
    Deno.chdir(originalCwd);
    await testProject.cleanup();
  }
});

Deno.test("ProjectManager - loadPreviousConversations", async (t) => {
  const testProject = await setupTestProject("conversations-test");
  const originalCwd = Deno.cwd();
  
  try {
    Deno.chdir(testProject.dir);

    await t.step("should return no previous sessions for session 1", async () => {
      const context = await ProjectManager.loadPreviousConversations(1);
      assertEquals(context, "No previous sessions.");
    });

    await t.step("should load previous conversation content", async () => {
      // Create a mock conversation file
      await TestHelpers.createMockConversation(testProject.dir, 1, 
        "**Claude**: This is a test conversation about project exploration.\n\n**You**: What are the key challenges?\n\n**Claude**: The main challenges are X, Y, and Z.");

      const context = await ProjectManager.loadPreviousConversations(2);
      assertEquals(context.includes("SESSION 1 INSIGHTS:"), true);
      assertEquals(context.includes("test conversation"), true);
    });

  } finally {
    Deno.chdir(originalCwd);
    await testProject.cleanup();
  }
});

Deno.test("ProjectManager - getCurrentStatus", async (t) => {
  await t.step("should return correct status for no tasks completed", async () => {
    const tasks = [
      { completed: false, text: "Task 1" },
      { completed: false, text: "Task 2" }
    ];
    const status = ProjectManager.getCurrentStatus(tasks);
    assertEquals(status, "Exploration phase - Ready to begin");
  });

  await t.step("should return correct status for partial completion", async () => {
    const tasks = [
      { completed: true, text: "Task 1" },
      { completed: false, text: "Task 2" },
      { completed: false, text: "Task 3" }
    ];
    const status = ProjectManager.getCurrentStatus(tasks);
    assertEquals(status, "Exploration phase - 1/3 areas explored");
  });

  await t.step("should return correct status for all tasks completed", async () => {
    const tasks = [
      { completed: true, text: "Task 1" },
      { completed: true, text: "Task 2" }
    ];
    const status = ProjectManager.getCurrentStatus(tasks);
    assertEquals(status, "Exploration phase - Complete, ready for specification");
  });
});