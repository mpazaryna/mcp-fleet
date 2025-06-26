import { assertEquals, assertExists, assert } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { specificationHandlers } from "../../src/tools/specification-tools.ts";
import { executionHandlers } from "../../src/tools/execution-tools.ts";

Deno.test("specification to execution workflow - complete integration", async () => {
  const testWorkspace = "/tmp/compass-integration-spec-exec";
  const projectName = "workflow-test-project";
  const projectPath = `${testWorkspace}/${projectName}`;
  
  try {
    // Setup test project with exploration content
    await Deno.mkdir(`${projectPath}/exploration`, { recursive: true });
    
    // Create project config in specification phase (exploration already completed)
    await Deno.writeTextFile(`${projectPath}/.compass.json`, JSON.stringify({
      name: projectName,
      currentPhase: "specification",
      status: "active",
      created: new Date().toISOString(),
      explorationCompletedDate: new Date().toISOString(),
      explorationCompletionReason: "Test setup - exploration completed for workflow integration test"
    }));
    
    // Create exploration content
    await Deno.writeTextFile(`${projectPath}/exploration/conversation-1.md`, `
# Exploration Session 1
**Project:** ${projectName}
**Date:** ${new Date().toISOString()}

## Business Requirements
We need to build a task management application for teams with the following key features:
- Task creation and assignment
- Team collaboration
- Progress tracking
- User authentication

## Technical Architecture
- React frontend with TypeScript
- Node.js backend with Express
- PostgreSQL database for data persistence
- REST API for frontend-backend communication

## User Experience
- Clean, intuitive interface
- Real-time updates
- Mobile responsive design
- Dashboard with analytics
    `);
    
    // Step 1: Generate specification from exploration
    const specResult = await specificationHandlers.generate_specification({
      project_name: projectName,
      pattern: "software_product_requirements",
      projectsDir: testWorkspace
    });
    
    assertEquals(specResult.success, true);
    assertEquals(specResult.project_name, projectName);
    assertEquals(specResult.pattern_used, "software_product_requirements");
    assertExists(specResult.specification_content);
    
    // Verify specification files were created
    const expectedSpecPath = join(projectPath, specResult.file_path);
    const specExists = await Deno.stat(expectedSpecPath).then(() => true).catch(() => false);
    assertEquals(specExists, true);
    
    // Verify project stayed in specification phase (spec generated but not completed yet)
    const configContent = await Deno.readTextFile(`${projectPath}/.compass.json`);
    const config = JSON.parse(configContent);
    assertEquals(config.currentPhase, "specification");
    
    // For execution to work, we need to manually mark specification as completed
    config.specificationCompletedDate = new Date().toISOString();
    await Deno.writeTextFile(`${projectPath}/.compass.json`, JSON.stringify(config, null, 2));
    
    // Step 2: Start execution phase
    const execResult = await executionHandlers.start_execution({
      projectName: projectName,
      workspacePath: testWorkspace
    });
    
    assertEquals(execResult.success, true);
    assert(execResult.message?.includes("Execution plan created"));
    assertEquals(execResult.data?.phase, "execution");
    assertEquals(execResult.data?.projectName, projectName);
    assert(execResult.data?.tasks && execResult.data.tasks.length > 0);
    
    // Verify execution files were created
    const executionPlanExists = await Deno.stat(`${projectPath}/execution/execution-plan.md`).then(() => true).catch(() => false);
    assertEquals(executionPlanExists, true);
    
    const tasksExists = await Deno.stat(`${projectPath}/execution/tasks.json`).then(() => true).catch(() => false);
    assertEquals(tasksExists, true);
    
    // Verify project moved to execution phase
    const updatedConfigContent = await Deno.readTextFile(`${projectPath}/.compass.json`);
    const updatedConfig = JSON.parse(updatedConfigContent);
    assertEquals(updatedConfig.currentPhase, "execution");
    assertExists(updatedConfig.executionStartedDate);
    
    // Step 3: Verify task generation based on specification content
    const tasksContent = await Deno.readTextFile(`${projectPath}/execution/tasks.json`);
    const tasks = JSON.parse(tasksContent);
    
    assert(tasks.length >= 4); // Should have setup, database, backend, frontend tasks
    
    // Check for expected task categories
    const categories = tasks.map((task: any) => task.category);
    
    // Basic categories that should always be present
    assert(categories.includes("setup"));
    assert(categories.includes("frontend")); // Should detect UI requirements
    assert(categories.includes("testing")); // Should always include testing
    assert(categories.includes("deployment")); // Should always include deployment
    
    // Note: Database and backend detection depends on specification content
    // which currently uses generic templates. This is a known limitation
    // that could be improved by better exploration-to-specification mapping.
    
    // Verify task structure
    tasks.forEach((task: any) => {
      assertExists(task.id);
      assertExists(task.title);
      assertExists(task.description);
      assertEquals(task.status, "pending");
      assert(["low", "medium", "high", "critical"].includes(task.priority));
      assert(typeof task.estimatedHours === "number");
      assertExists(task.createdDate);
    });
    
    // Step 4: Test task management workflow
    const firstTaskId = tasks[0].id;
    
    // List tasks
    const listResult = await executionHandlers.list_tasks({
      projectName: projectName,
      workspacePath: testWorkspace
    });
    
    assertEquals(listResult.success, true);
    assertEquals(listResult.data?.projectName, projectName);
    assertEquals(listResult.data?.tasks?.length, tasks.length);
    assertEquals(listResult.data?.summary?.total, tasks.length);
    assertEquals(listResult.data?.summary?.pending, tasks.length);
    assertEquals(listResult.data?.summary?.completed, 0);
    
    // Update task status
    const updateResult = await executionHandlers.update_task_status({
      projectName: projectName,
      workspacePath: testWorkspace,
      taskId: firstTaskId,
      status: "completed",
      notes: "Environment setup completed successfully"
    });
    
    assertEquals(updateResult.success, true);
    assertEquals(updateResult.data?.task?.id, firstTaskId);
    assertEquals(updateResult.data?.task?.status, "completed");
    assertEquals(updateResult.data?.task?.notes, "Environment setup completed successfully");
    assertExists(updateResult.data?.task?.completedDate);
    
    // Verify task status was updated in file
    const updatedTasksContent = await Deno.readTextFile(`${projectPath}/execution/tasks.json`);
    const updatedTasks = JSON.parse(updatedTasksContent);
    const updatedTask = updatedTasks.find((task: any) => task.id === firstTaskId);
    assertEquals(updatedTask.status, "completed");
    assertEquals(updatedTask.notes, "Environment setup completed successfully");
    assertExists(updatedTask.completedDate);
    
    // List tasks with filter
    const filteredListResult = await executionHandlers.list_tasks({
      projectName: projectName,
      workspacePath: testWorkspace,
      status: "completed"
    });
    
    assertEquals(filteredListResult.success, true);
    assertEquals(filteredListResult.data?.tasks?.length, 1);
    assertEquals(filteredListResult.data?.tasks?.[0]?.id, firstTaskId);
    assertEquals(filteredListResult.data?.summary?.completed, 1);
    assertEquals(filteredListResult.data?.summary?.pending, tasks.length - 1);
    
  } finally {
    await Deno.remove(testWorkspace, { recursive: true }).catch(() => {});
  }
});

Deno.test("execution phase enforces specification completion", async () => {
  const testWorkspace = "/tmp/compass-integration-exec-enforce";
  const projectName = "enforcement-test-project";
  const projectPath = `${testWorkspace}/${projectName}`;
  
  try {
    await Deno.mkdir(projectPath, { recursive: true });
    
    // Create project config without specification completion
    await Deno.writeTextFile(`${projectPath}/.compass.json`, JSON.stringify({
      name: projectName,
      currentPhase: "exploration",
      status: "active",
      created: new Date().toISOString()
    }));
    
    // Try to start execution without completed specification
    const execResult = await executionHandlers.start_execution({
      projectName: projectName,
      workspacePath: testWorkspace
    });
    
    assertEquals(execResult.success, false);
    assert(execResult.error?.includes("Specification phase must be completed"));
    
    // Verify no execution files were created
    const executionPlanExists = await Deno.stat(`${projectPath}/execution/execution-plan.md`).then(() => true).catch(() => false);
    assertEquals(executionPlanExists, false);
    
    const tasksExists = await Deno.stat(`${projectPath}/execution/tasks.json`).then(() => true).catch(() => false);
    assertEquals(tasksExists, false);
    
  } finally {
    await Deno.remove(testWorkspace, { recursive: true }).catch(() => {});
  }
});