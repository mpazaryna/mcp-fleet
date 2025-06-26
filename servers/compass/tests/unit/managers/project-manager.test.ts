import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { ProjectManager } from "../../../src/managers/project-manager.ts";

Deno.test({
  name: "ProjectManager parses tasks correctly",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    
    try {
      // Create a test tasks.md file
      const tasksContent = `# Test Project - Project Tasks

## Phase 1: Exploration
- [x] Complete initial problem exploration
- [ ] Explore technical requirements
- [ ] Understand user needs

## Phase 2: Specification
- [ ] Create requirements document
`;
      
      await Deno.writeTextFile(join(testDir, "tasks.md"), tasksContent);
      
      const manager = new ProjectManager(testDir);
      const tasks = await manager.parseTasksFile();
      
      assertEquals(tasks.explorationTasks.length, 3);
      assertEquals(tasks.explorationTasks[0].completed, true);
      assertEquals(tasks.explorationTasks[0].text, "Complete initial problem exploration");
      assertEquals(tasks.explorationTasks[1].completed, false);
      assertEquals(tasks.explorationTasks[1].text, "Explore technical requirements");
      assertEquals(tasks.currentPhase, "exploration");
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "ProjectManager updates tasks correctly",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    
    try {
      const manager = new ProjectManager(testDir);
      
      // Create initial tasks
      const projectName = "Test Project";
      await manager.createInitialTasks(projectName);
      
      // Parse the created tasks
      const tasks = await manager.parseTasksFile();
      assertEquals(tasks.explorationTasks.length, 1);
      assertEquals(tasks.explorationTasks[0].completed, false);
      
      // Update a task to completed
      tasks.explorationTasks[0].completed = true;
      await manager.updateTasksFile(tasks.explorationTasks, projectName);
      
      // Parse again to verify
      const updatedTasks = await manager.parseTasksFile();
      assertEquals(updatedTasks.explorationTasks[0].completed, true);
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "ProjectManager loads and updates metadata",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    
    try {
      const manager = new ProjectManager(testDir);
      
      // Create initial metadata
      const metadata = {
        name: "test-project",
        created: new Date().toISOString(),
        currentPhase: "exploration",
        status: "active",
        sessionCount: 0,
      };
      
      await manager.saveMetadata(metadata);
      
      // Load metadata
      const loaded = await manager.loadMetadata();
      assertExists(loaded);
      assertEquals(loaded.name, "test-project");
      assertEquals(loaded.currentPhase, "exploration");
      assertEquals(loaded.sessionCount, 0);
      
      // Update metadata
      loaded.sessionCount = 1;
      loaded.lastSessionDate = new Date().toISOString();
      await manager.saveMetadata(loaded);
      
      // Verify update
      const updated = await manager.loadMetadata();
      assertEquals(updated?.sessionCount, 1);
      assertExists(updated?.lastSessionDate);
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "ProjectManager creates correct project structure",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectPath = join(testDir, "test-project");
    
    try {
      const manager = new ProjectManager(projectPath);
      await manager.createProjectStructure("test-project");
      
      // Verify all directories exist
      const dirs = ["exploration", "specification", "execution", "feedback"];
      for (const dir of dirs) {
        const dirPath = join(projectPath, dir);
        const stat = await Deno.stat(dirPath);
        assertEquals(stat.isDirectory, true);
      }
      
      // Verify metadata exists
      const metadata = await manager.loadMetadata();
      assertExists(metadata);
      assertEquals(metadata.name, "test-project");
      
      // Verify tasks.md exists
      const tasksPath = join(projectPath, "tasks.md");
      const tasksStat = await Deno.stat(tasksPath);
      assertEquals(tasksStat.isFile, true);
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});