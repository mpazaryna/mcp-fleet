import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import { projectTools, projectHandlers } from "../../../src/tools/project-tools.ts";

Deno.test("project tools are properly defined", () => {
  assertEquals(projectTools.length, 3);
  
  const toolNames = projectTools.map(t => t.name);
  assertEquals(toolNames, ["init_project", "list_projects", "get_project_status"]);
});

Deno.test("init_project tool has correct schema", () => {
  const initTool = projectTools.find(t => t.name === "init_project");
  assertExists(initTool);
  assertEquals(initTool.description, "Initialize a new Compass project with systematic methodology structure");
  assertExists(initTool.inputSchema);
  assertExists(initTool.outputSchema);
});

Deno.test({
  name: "init_project creates correct directory structure",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "test-project";
    
    try {
      const result = await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(result.success, true);
      assertEquals(result.project_name, projectName);
      
      // Verify directory structure
      const projectPath = join(testDir, projectName);
      assertEquals(await exists(projectPath), true);
      assertEquals(await exists(join(projectPath, "exploration")), true);
      assertEquals(await exists(join(projectPath, "specification")), true);
      assertEquals(await exists(join(projectPath, "execution")), true);
      assertEquals(await exists(join(projectPath, "feedback")), true);
      
      // Verify metadata file
      assertEquals(await exists(join(projectPath, ".compass.json")), true);
      const metadata = JSON.parse(await Deno.readTextFile(join(projectPath, ".compass.json")));
      assertEquals(metadata.name, projectName);
      assertEquals(metadata.currentPhase, "exploration");
      
      // Verify tasks file
      assertEquals(await exists(join(projectPath, "tasks.md")), true);
      const tasksContent = await Deno.readTextFile(join(projectPath, "tasks.md"));
      assertEquals(tasksContent.includes("Phase 1: Exploration"), true);
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "init_project fails if project already exists",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "existing-project";
    
    try {
      // Create project first time
      await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      // Try to create again
      const result = await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(result.success, false);
      assertEquals(result.message.includes("already exists"), true);
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});