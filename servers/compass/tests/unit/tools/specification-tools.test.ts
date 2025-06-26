import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import { specificationTools, specificationHandlers } from "../../../src/tools/specification-tools.ts";
import { projectHandlers } from "../../../src/tools/project-tools.ts";
import { explorationHandlers } from "../../../src/tools/exploration-tools.ts";

Deno.test("specification tools are properly defined", () => {
  assertEquals(specificationTools.length, 3);
  
  const toolNames = specificationTools.map(t => t.name);
  assertEquals(toolNames, [
    "generate_specification",
    "list_patterns", 
    "get_specification_status"
  ]);
});

Deno.test("generate_specification tool has correct schema", () => {
  const tool = specificationTools.find(t => t.name === "generate_specification");
  assertExists(tool);
  assertEquals(tool.description, "Generate pattern-based specification from exploration insights");
  assertExists(tool.inputSchema);
  assertExists(tool.outputSchema);
});

Deno.test({
  name: "generate_specification creates spec from exploration",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "test-project";
    
    try {
      // Create project and complete exploration
      await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      // Add exploration content first  
      const saveResult = await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: "User: I need a task management app for my team\nAssistant: Let's explore your task management requirements. What are the core features you need for managing tasks effectively?",
        projectsDir: testDir,
      });
      
      // Complete exploration
      await explorationHandlers.complete_exploration_phase({
        project_name: projectName,
        completion_reason: "Basic requirements explored",
        projectsDir: testDir,
      });
      
      // Generate specification
      const result = await specificationHandlers.generate_specification({
        project_name: projectName,
        pattern: "software_product_requirements",
        projectsDir: testDir,
      });
      
      assertEquals(result.success, true);
      assertEquals(result.project_name, projectName);
      assertEquals(result.pattern_used, "software_product_requirements");
      assertExists(result.specification_content);
      assertExists(result.file_path);
      
      // Verify specification file was created
      const projectPath = join(testDir, projectName);
      const specPath = join(projectPath, result.file_path);
      assertEquals(await exists(specPath), true);
      
      const specContent = await Deno.readTextFile(specPath);
      assertEquals(specContent.includes("# Product Requirements"), true);
      assertEquals(specContent.includes("test-project"), true);
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "generate_specification fails if exploration not complete",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "incomplete-project";
    
    try {
      // Create project but don't complete exploration
      await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      // Try to generate specification
      const result = await specificationHandlers.generate_specification({
        project_name: projectName,
        pattern: "software_product_requirements",
        projectsDir: testDir,
      });
      
      assertEquals(result.success, false);
      assertEquals(result.error, "Exploration phase not completed. Complete exploration before generating specification.");
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "list_patterns returns available specification patterns",
  permissions: { read: true },
  fn: async () => {
    const result = await specificationHandlers.list_patterns({});
    
    assertEquals(result.success, true);
    assertExists(result.patterns);
    assertEquals(Array.isArray(result.patterns), true);
    assertEquals(result.total > 0, true);
    
    // Check that default patterns exist
    const patternNames = result.patterns.map(p => p.name);
    assertEquals(patternNames.includes("software_product_requirements"), true);
    assertEquals(patternNames.includes("business_process_analysis"), true);
    assertEquals(patternNames.includes("project_planning"), true);
  },
});

Deno.test({
  name: "get_specification_status shows specification state",
  permissions: { read: true, write: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "spec-status-test";
    
    try {
      // Create project and complete exploration
      await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      // Add some exploration content first
      await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: "User: Project planning needed\nAssistant: Let's define the scope...",
        projectsDir: testDir,
      });
      
      await explorationHandlers.complete_exploration_phase({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      // Check status before specification
      const status1 = await specificationHandlers.get_specification_status({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(status1.current_phase, "specification");
      assertEquals(status1.specifications_generated, 0);
      assertEquals(status1.ready_for_specification, true);
      
      // Generate a specification
      const specResult = await specificationHandlers.generate_specification({
        project_name: projectName,
        pattern: "software_product_requirements",
        projectsDir: testDir,
      });
      
      if (!specResult.success) {
        console.error("Specification generation failed in status test:", specResult.error);
      }
      
      // Check status after specification
      const status2 = await specificationHandlers.get_specification_status({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(status2.specifications_generated, 1);
      assertEquals(status2.specifications.length, 1);
      assertEquals(status2.specifications[0].pattern, "software_product_requirements");
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});