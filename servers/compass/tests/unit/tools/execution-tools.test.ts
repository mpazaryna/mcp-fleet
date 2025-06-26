import { assertEquals, assertExists, assert } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { executionTools, executionHandlers } from "../../../src/tools/execution-tools.ts";

Deno.test("execution tools are properly defined", () => {
  assertEquals(executionTools.length, 3);
  
  const toolNames = executionTools.map(t => t.name);
  assertEquals(toolNames, [
    "start_execution",
    "list_tasks", 
    "update_task_status"
  ]);
  
  // Verify all tools have required properties
  executionTools.forEach(tool => {
    assertExists(tool.name);
    assertExists(tool.description);
    assertExists(tool.inputSchema);
  });
});

Deno.test("execution handlers are properly defined", () => {
  assertEquals(Object.keys(executionHandlers).length, 3);
  
  const handlerNames = Object.keys(executionHandlers);
  assertEquals(handlerNames, [
    "start_execution",
    "list_tasks",
    "update_task_status"
  ]);
  
  // Verify all handlers are functions
  Object.values(executionHandlers).forEach(handler => {
    assertEquals(typeof handler, "function");
  });
});

Deno.test("start_execution tool creates execution plan and tasks", async () => {
  // Setup test project with completed specification
  const testWorkspace = "/tmp/compass-test-execution";
  const projectPath = `${testWorkspace}/test-project`;
  
  try {
    await Deno.mkdir(projectPath, { recursive: true });
    await Deno.mkdir(`${projectPath}/specification`, { recursive: true });
    await Deno.mkdir(`${projectPath}/execution`, { recursive: true });
    
    // Create project config
    await Deno.writeTextFile(`${projectPath}/.compass.json`, JSON.stringify({
      name: "test-project",
      currentPhase: "specification",
      status: "active",
      created: new Date().toISOString(),
      specificationCompletedDate: new Date().toISOString()
    }));
    
    // Create specification document
    await Deno.writeTextFile(`${projectPath}/specification/software_product_requirements.md`, `
# Product Requirements Document
## Overview
A task management application for teams
## User Stories
- As a user, I can create tasks
- As a user, I can assign tasks to team members
## Technical Specifications
- React frontend with TypeScript
- Node.js backend with Express
- PostgreSQL database
## Acceptance Criteria
- Tasks can be created, updated, and deleted
- User authentication and authorization
    `);
    
    const result = await executionHandlers.start_execution({
      projectName: "test-project",
      workspacePath: testWorkspace
    });
    
    assertEquals(result.success, true);
    assert(result.message?.includes("Execution plan created"));
    assertEquals(result.data?.phase, "execution");
    assert(result.data?.tasks && result.data.tasks.length > 0);
    
    // Verify execution plan file was created
    const executionPlanExists = await Deno.stat(`${projectPath}/execution/execution-plan.md`).then(() => true).catch(() => false);
    assertEquals(executionPlanExists, true);
    
    // Verify tasks file was created
    const tasksExists = await Deno.stat(`${projectPath}/execution/tasks.json`).then(() => true).catch(() => false);
    assertEquals(tasksExists, true);
    
    // Verify project config was updated
    const configContent = await Deno.readTextFile(`${projectPath}/.compass.json`);
    const config = JSON.parse(configContent);
    assertEquals(config.currentPhase, "execution");
    assertExists(config.executionStartedDate);
    
  } finally {
    await Deno.remove(testWorkspace, { recursive: true }).catch(() => {});
  }
});

Deno.test("start_execution fails if specification not completed", async () => {
  const testWorkspace = "/tmp/compass-test-execution-fail";
  const projectPath = `${testWorkspace}/test-project`;
  
  try {
    await Deno.mkdir(projectPath, { recursive: true });
    
    // Create project config without specification completion
    await Deno.writeTextFile(`${projectPath}/.compass.json`, JSON.stringify({
      name: "test-project",
      currentPhase: "specification",
      status: "active",
      created: new Date().toISOString()
    }));
    
    const result = await executionHandlers.start_execution({
      projectName: "test-project",
      workspacePath: testWorkspace
    });
    
    assertEquals(result.success, false);
    assert(result.error?.includes("Specification phase must be completed"));
    
  } finally {
    await Deno.remove(testWorkspace, { recursive: true }).catch(() => {});
  }
});

Deno.test("list_tasks returns execution tasks", async () => {
  const testWorkspace = "/tmp/compass-test-list-tasks";
  const projectPath = `${testWorkspace}/test-project`;
  
  try {
    await Deno.mkdir(`${projectPath}/execution`, { recursive: true });
    
    // Create tasks file
    const tasks = [
      {
        id: "task-1",
        title: "Setup development environment",
        description: "Install Node.js, React, and dependencies",
        status: "pending",
        priority: "high",
        category: "setup",
        estimatedHours: 4,
        createdDate: new Date().toISOString()
      },
      {
        id: "task-2", 
        title: "Create database schema",
        description: "Design and implement PostgreSQL schema",
        status: "in_progress",
        priority: "high",
        category: "backend",
        estimatedHours: 8,
        createdDate: new Date().toISOString()
      }
    ];
    
    await Deno.writeTextFile(`${projectPath}/execution/tasks.json`, JSON.stringify(tasks, null, 2));
    
    const result = await executionHandlers.list_tasks({
      projectName: "test-project",
      workspacePath: testWorkspace
    });
    
    assertEquals(result.success, true);
    assertEquals(result.data?.tasks?.length, 2);
    assertEquals(result.data?.tasks?.[0]?.title, "Setup development environment");
    assertEquals(result.data?.tasks?.[1]?.status, "in_progress");
    
  } finally {
    await Deno.remove(testWorkspace, { recursive: true }).catch(() => {});
  }
});

Deno.test("update_task_status modifies task status", async () => {
  const testWorkspace = "/tmp/compass-test-update-task";
  const projectPath = `${testWorkspace}/test-project`;
  
  try {
    await Deno.mkdir(`${projectPath}/execution`, { recursive: true });
    
    // Create tasks file
    const tasks = [
      {
        id: "task-1",
        title: "Setup development environment",
        description: "Install Node.js, React, and dependencies",
        status: "pending",
        priority: "high",
        category: "setup",
        estimatedHours: 4,
        createdDate: new Date().toISOString()
      }
    ];
    
    await Deno.writeTextFile(`${projectPath}/execution/tasks.json`, JSON.stringify(tasks, null, 2));
    
    const result = await executionHandlers.update_task_status({
      projectName: "test-project",
      workspacePath: testWorkspace,
      taskId: "task-1",
      status: "completed",
      notes: "Environment setup completed successfully"
    });
    
    assertEquals(result.success, true);
    assertEquals(result.data?.task?.status, "completed");
    assertEquals(result.data?.task?.notes, "Environment setup completed successfully");
    assertExists(result.data?.task?.completedDate);
    
    // Verify file was updated
    const updatedTasksContent = await Deno.readTextFile(`${projectPath}/execution/tasks.json`);
    const updatedTasks = JSON.parse(updatedTasksContent);
    assertEquals(updatedTasks[0].status, "completed");
    assertEquals(updatedTasks[0].notes, "Environment setup completed successfully");
    
  } finally {
    await Deno.remove(testWorkspace, { recursive: true }).catch(() => {});
  }
});