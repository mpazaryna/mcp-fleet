import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import { projectHandlers } from "../../src/tools/project-tools.ts";
import { explorationHandlers } from "../../src/tools/exploration-tools.ts";
import { specificationHandlers } from "../../src/tools/specification-tools.ts";

Deno.test({
  name: "complete exploration to specification workflow",
  permissions: { read: true, write: true, env: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "integration-test";
    
    try {
      // PHASE 1: Project Initialization
      const initResult = await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(initResult.success, true);
      
      // PHASE 2: Exploration Workflow
      const explorationResult = await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: "User: I want to build a customer management system\nAssistant: Let's explore your customer management requirements systematically...",
        session_summary: "Initial customer management exploration",
        projectsDir: testDir,
      });
      
      assertEquals(explorationResult.conversation_saved, true);
      assertEquals(explorationResult.session_number, 1);
      
      // Add a second exploration session
      const exploration2Result = await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: "User: The system needs contact management, sales tracking, and reporting\nAssistant: Excellent! Those are core CRM features. Let's dive deeper...",
        session_summary: "Feature requirements and technical exploration",
        projectsDir: testDir,
      });
      
      assertEquals(exploration2Result.session_number, 2);
      
      // Check project status before completion
      const statusBefore = await projectHandlers.get_project_status({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(statusBefore.current_phase, "exploration");
      assertEquals(statusBefore.next_action, "start_exploration");
      
      // Complete exploration phase
      const completeResult = await explorationHandlers.complete_exploration_phase({
        project_name: projectName,
        completion_reason: "Core customer management requirements explored",
        projectsDir: testDir,
      });
      
      assertEquals(completeResult.exploration_completed, true);
      
      // PHASE 3: Specification Workflow
      
      // Check specification status
      const specStatus1 = await specificationHandlers.get_specification_status({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(specStatus1.current_phase, "specification");
      assertEquals(specStatus1.ready_for_specification, true);
      assertEquals(specStatus1.specifications_generated, 0);
      assertEquals(specStatus1.next_action, "generate_specification");
      
      // List available patterns
      const patternsResult = await specificationHandlers.list_patterns({});
      
      assertEquals(patternsResult.success, true);
      assertEquals(patternsResult.total > 0, true);
      
      const softwarePattern = patternsResult.patterns.find(p => p.name === "software_product_requirements");
      assertExists(softwarePattern);
      assertEquals(softwarePattern.domain, "software");
      
      // Generate specification using software pattern
      const specResult = await specificationHandlers.generate_specification({
        project_name: projectName,
        pattern: "software_product_requirements",
        projectsDir: testDir,
      });
      
      assertEquals(specResult.success, true);
      assertEquals(specResult.pattern_used, "software_product_requirements");
      assertExists(specResult.specification_content);
      assertExists(specResult.file_path);
      
      // Verify specification file was created
      const projectPath = join(testDir, projectName);
      const specPath = join(projectPath, specResult.file_path);
      assertEquals(await exists(specPath), true);
      
      const specContent = await Deno.readTextFile(specPath);
      assertEquals(specContent.includes("Product Requirements Document"), true);
      assertEquals(specContent.includes("integration-test"), true);
      assertEquals(specContent.includes("User Stories"), true);
      
      // Check insights extraction
      assertEquals(specResult.insights_extracted.user_pain_points.length > 0, true);
      assertEquals(specResult.insights_extracted.core_features.length > 0, true);
      
      // Generate a second specification with different pattern
      const specResult2 = await specificationHandlers.generate_specification({
        project_name: projectName,
        pattern: "business_process_analysis",
        projectsDir: testDir,
      });
      
      assertEquals(specResult2.success, true);
      assertEquals(specResult2.pattern_used, "business_process_analysis");
      
      // Check final specification status
      const specStatus2 = await specificationHandlers.get_specification_status({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(specStatus2.specifications_generated, 2);
      assertEquals(specStatus2.specifications.length, 2);
      
      const patterns = specStatus2.specifications.map(s => s.pattern);
      assertEquals(patterns.includes("software_product_requirements"), true);
      assertEquals(patterns.includes("business_process_analysis"), true);
      
      // Verify final project structure
      const finalDirs = ["exploration", "specification", "execution", "feedback"];
      for (const dir of finalDirs) {
        const dirPath = join(projectPath, dir);
        assertEquals(await exists(dirPath), true);
      }
      
      // Verify exploration files
      assertEquals(await exists(join(projectPath, "exploration", "conversation-1.md")), true);
      assertEquals(await exists(join(projectPath, "exploration", "conversation-2.md")), true);
      assertEquals(await exists(join(projectPath, "exploration", "completion-override.md")), true);
      
      // Verify specification files
      const specFiles = specStatus2.specifications.map(s => join(projectPath, s.file_path));
      for (const specFile of specFiles) {
        assertEquals(await exists(specFile), true);
      }
      
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});

Deno.test({
  name: "specification workflow enforces exploration completion",
  permissions: { read: true, write: true, env: true },
  fn: async () => {
    const testDir = await Deno.makeTempDir();
    const projectName = "enforcement-test";
    
    try {
      // Create project but don't complete exploration
      await projectHandlers.init_project({
        name: projectName,
        projectsDir: testDir,
      });
      
      // Try to generate specification without completing exploration
      const specResult = await specificationHandlers.generate_specification({
        project_name: projectName,
        pattern: "software_product_requirements",
        projectsDir: testDir,
      });
      
      assertEquals(specResult.success, false);
      assertEquals(specResult.error.includes("Exploration phase not completed"), true);
      
      // Check specification status shows not ready
      const specStatus = await specificationHandlers.get_specification_status({
        project_name: projectName,
        projectsDir: testDir,
      });
      
      assertEquals(specStatus.current_phase, "exploration");
      assertEquals(specStatus.ready_for_specification, false);
      assertEquals(specStatus.next_action, "complete_exploration");
      
    } finally {
      await Deno.remove(testDir, { recursive: true });
    }
  },
});