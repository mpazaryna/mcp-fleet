import { assertEquals, assertExists } from "@std/assert";
import { exists } from "@std/fs";
import { join } from "@std/path";
import { TestHelpers } from "../utils/test-helpers.ts";

// Import the initProject function - we'll need to refactor explore.ts to export this
// For now, let's create a simplified version for testing

async function testInitProject(projectName: string, baseDir: string) {
  const { ensureDir } = await import("@std/fs");
  const { FRAMEWORK_TEMPLATES } = await import("../../src/templates.ts");
  
  const projectDir = join(baseDir, 'projects', projectName.toLowerCase().replace(/\s+/g, '-'));
  
  if (await exists(projectDir)) {
    throw new Error(`Project '${projectDir}' already exists`);
  }

  await ensureDir(`${projectDir}/exploration`);
  await ensureDir(`${projectDir}/specification`);
  await ensureDir(`${projectDir}/execution`);
  await ensureDir(`${projectDir}/feedback`);

  const tasksContent = FRAMEWORK_TEMPLATES.tasks
    .replace(/{{PROJECT_NAME}}/g, projectName)
    .replace(/{{STATUS}}/g, "Project initialized - Ready for exploration")
    .replace(/{{NEXT_ACTION}}/g, "deno task explore");
  
  await Deno.writeTextFile(`${projectDir}/tasks.md`, tasksContent);

  const questionsContent = FRAMEWORK_TEMPLATES.explorationQuestions
    .replace(/{{PROJECT_NAME}}/g, projectName);
  await Deno.writeTextFile(`${projectDir}/exploration/questions.md`, questionsContent);

  const metadata = {
    name: projectName,
    created: new Date().toISOString(),
    currentPhase: "exploration",
    status: "initialized",
    sessionCount: 0
  };
  await Deno.writeTextFile(`${projectDir}/.orchestration.json`, JSON.stringify(metadata, null, 2));

  return projectDir;
}

Deno.test("Project Initialization Workflow", async (t) => {
  const tempDir = await TestHelpers.createTempTestDir();
  
  try {
    await t.step("should create project structure correctly", async () => {
      const projectName = "Test Project Initiative";
      const projectDir = await testInitProject(projectName, tempDir);
      
      // Verify directory structure
      assertEquals(await exists(`${projectDir}/exploration`), true);
      assertEquals(await exists(`${projectDir}/specification`), true);
      assertEquals(await exists(`${projectDir}/execution`), true);
      assertEquals(await exists(`${projectDir}/feedback`), true);
      
      // Verify core files
      assertEquals(await exists(`${projectDir}/tasks.md`), true);
      assertEquals(await exists(`${projectDir}/exploration/questions.md`), true);
      assertEquals(await exists(`${projectDir}/.orchestration.json`), true);
    });

    await t.step("should generate proper tasks.md content", async () => {
      const projectName = "Content Test Project";
      const projectDir = await testInitProject(projectName, tempDir);
      
      const tasksContent = await Deno.readTextFile(`${projectDir}/tasks.md`);
      assertEquals(tasksContent.includes(projectName), true);
      assertEquals(tasksContent.includes("## Phase 1: Exploration"), true);
      assertEquals(tasksContent.includes("## Phase 2: Specification"), true);
      assertEquals(tasksContent.includes("## Phase 3: Execution"), true);
      assertEquals(tasksContent.includes("## Phase 4: Feedback & Learning"), true);
    });

    await t.step("should create valid project metadata", async () => {
      const projectName = "Metadata Test";
      const projectDir = await testInitProject(projectName, tempDir);
      
      const metadataContent = await Deno.readTextFile(`${projectDir}/.orchestration.json`);
      const metadata = JSON.parse(metadataContent);
      
      assertEquals(metadata.name, projectName);
      assertEquals(metadata.currentPhase, "exploration");
      assertEquals(metadata.status, "initialized");
      assertEquals(metadata.sessionCount, 0);
      assertExists(metadata.created);
    });

    await t.step("should create exploration questions template", async () => {
      const projectName = "Questions Test";
      const projectDir = await testInitProject(projectName, tempDir);
      
      const questionsContent = await Deno.readTextFile(`${projectDir}/exploration/questions.md`);
      assertEquals(questionsContent.includes(projectName), true);
      assertEquals(questionsContent.includes("## Core Problem Definition"), true);
      assertEquals(questionsContent.includes("## Context & Assumptions"), true);
      assertEquals(questionsContent.includes("## Hidden Complexity"), true);
    });

    await t.step("should handle project name normalization", async () => {
      const projectName = "My Complex Project Name!";
      const projectDir = await testInitProject(projectName, tempDir);
      
      // Project directory should be normalized but metadata should preserve original name
      assertEquals(projectDir.includes("my-complex-project-name"), true);
      
      const metadata = JSON.parse(await Deno.readTextFile(`${projectDir}/.orchestration.json`));
      assertEquals(metadata.name, projectName);
    });

  } finally {
    await TestHelpers.cleanupTestDir(tempDir);
  }
});

Deno.test("Project Initialization Edge Cases", async (t) => {
  const tempDir = await TestHelpers.createTempTestDir();
  
  try {
    await t.step("should prevent duplicate project creation", async () => {
      const projectName = "Duplicate Test";
      
      // Create project first time
      await testInitProject(projectName, tempDir);
      
      // Attempt to create again should fail
      let errorThrown = false;
      try {
        await testInitProject(projectName, tempDir);
      } catch (error) {
        errorThrown = true;
        assertEquals(error instanceof Error && error.message.includes("already exists"), true);
      }
      assertEquals(errorThrown, true);
    });

  } finally {
    await TestHelpers.cleanupTestDir(tempDir);
  }
});