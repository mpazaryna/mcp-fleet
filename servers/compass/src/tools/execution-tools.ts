import { z } from "zod";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import type { MCPTool } from "@packages/mcp-core/mod.ts";

// Temporary local implementations
async function writeFile(args: { path: string; content: string }) {
  const dir = args.path.substring(0, args.path.lastIndexOf("/"));
  await Deno.mkdir(dir, { recursive: true });
  await Deno.writeTextFile(args.path, args.content);
}

async function readFile(path: string): Promise<string> {
  return await Deno.readTextFile(path);
}

// Task status enum
const TaskStatus = z.enum(["pending", "in_progress", "completed", "blocked"]);

// Task priority enum
const TaskPriority = z.enum(["low", "medium", "high", "critical"]);

// Task category enum
const TaskCategory = z.enum(["setup", "frontend", "backend", "database", "testing", "deployment", "documentation"]);

// Schema definitions
const StartExecutionInputSchema = z.object({
  projectName: z.string().describe("Project name"),
  workspacePath: z.string().optional().describe("Workspace path (for testing)")
});

const StartExecutionOutputSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  data: z.object({
    phase: z.string(),
    projectName: z.string(),
    executionPlanPath: z.string(),
    tasksPath: z.string(),
    tasks: z.array(z.object({
      id: z.string(),
      title: z.string(),
      description: z.string(),
      status: TaskStatus,
      priority: TaskPriority,
      category: TaskCategory,
      estimatedHours: z.number(),
      createdDate: z.string()
    }))
  }).optional(),
  error: z.string().optional()
});

const ListTasksInputSchema = z.object({
  projectName: z.string().describe("Project name"),
  workspacePath: z.string().optional().describe("Workspace path (for testing)"),
  status: TaskStatus.optional().describe("Filter by task status"),
  category: TaskCategory.optional().describe("Filter by task category")
});

const ListTasksOutputSchema = z.object({
  success: z.boolean(),
  data: z.object({
    projectName: z.string(),
    tasks: z.array(z.object({
      id: z.string(),
      title: z.string(),
      description: z.string(),
      status: TaskStatus,
      priority: TaskPriority,
      category: TaskCategory,
      estimatedHours: z.number(),
      createdDate: z.string(),
      completedDate: z.string().optional(),
      notes: z.string().optional()
    })),
    summary: z.object({
      total: z.number(),
      pending: z.number(),
      in_progress: z.number(),
      completed: z.number(),
      blocked: z.number()
    })
  }).optional(),
  error: z.string().optional()
});

const UpdateTaskStatusInputSchema = z.object({
  projectName: z.string().describe("Project name"),
  workspacePath: z.string().optional().describe("Workspace path (for testing)"),
  taskId: z.string().describe("Task ID to update"),
  status: TaskStatus.describe("New task status"),
  notes: z.string().optional().describe("Optional notes about the status change")
});

const UpdateTaskStatusOutputSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  data: z.object({
    task: z.object({
      id: z.string(),
      title: z.string(),
      status: TaskStatus,
      completedDate: z.string().optional(),
      notes: z.string().optional()
    })
  }).optional(),
  error: z.string().optional()
});

// Task generation from specification content
function generateTasksFromSpecification(specContent: string): Array<{
  id: string;
  title: string;
  description: string;
  status: "pending";
  priority: "high" | "medium" | "low";
  category: "setup" | "frontend" | "backend" | "database" | "testing" | "deployment" | "documentation";
  estimatedHours: number;
  createdDate: string;
}> {
  const tasks = [];
  const timestamp = new Date().toISOString();
  
  // Parse specification content and generate appropriate tasks
  const hasDatabase = specContent.toLowerCase().includes("database") || 
                     specContent.toLowerCase().includes("postgresql") ||
                     specContent.toLowerCase().includes("mysql");
  
  const hasFrontend = specContent.toLowerCase().includes("react") ||
                     specContent.toLowerCase().includes("frontend") ||
                     specContent.toLowerCase().includes("ui");
  
  const hasBackend = specContent.toLowerCase().includes("backend") ||
                    specContent.toLowerCase().includes("api") ||
                    specContent.toLowerCase().includes("server");
  
  // Always include setup tasks
  tasks.push({
    id: `task-${Date.now()}-1`,
    title: "Setup development environment",
    description: "Initialize project structure, install dependencies, and configure development tools",
    status: "pending" as const,
    priority: "high" as const,
    category: "setup" as const,
    estimatedHours: 4,
    createdDate: timestamp
  });
  
  if (hasDatabase) {
    tasks.push({
      id: `task-${Date.now()}-2`,
      title: "Design and implement database schema",
      description: "Create database tables, relationships, and initial data migrations",
      status: "pending" as const,
      priority: "high" as const,
      category: "database" as const,
      estimatedHours: 8,
      createdDate: timestamp
    });
  }
  
  if (hasBackend) {
    tasks.push({
      id: `task-${Date.now()}-3`,
      title: "Implement core API endpoints",
      description: "Create REST API endpoints for core functionality",
      status: "pending" as const,
      priority: "high" as const,
      category: "backend" as const,
      estimatedHours: 12,
      createdDate: timestamp
    });
  }
  
  if (hasFrontend) {
    tasks.push({
      id: `task-${Date.now()}-4`,
      title: "Build user interface components",
      description: "Create reusable UI components and implement user workflows",
      status: "pending" as const,
      priority: "medium" as const,
      category: "frontend" as const,
      estimatedHours: 16,
      createdDate: timestamp
    });
  }
  
  // Always include testing and documentation
  tasks.push({
    id: `task-${Date.now()}-5`,
    title: "Write unit and integration tests",
    description: "Implement comprehensive test coverage for all components",
    status: "pending" as const,
    priority: "medium" as const,
    category: "testing" as const,
    estimatedHours: 8,
    createdDate: timestamp
  });
  
  tasks.push({
    id: `task-${Date.now()}-6`,
    title: "Create deployment configuration",
    description: "Setup CI/CD pipeline and deployment infrastructure",
    status: "pending" as const,
    priority: "low" as const,
    category: "deployment" as const,
    estimatedHours: 6,
    createdDate: timestamp
  });
  
  return tasks;
}

// Tool definitions
export const executionTools: MCPTool[] = [
  {
    name: "start_execution",
    description: "Start the execution phase by creating an execution plan and task breakdown from the completed specification",
    inputSchema: StartExecutionInputSchema,
    outputSchema: StartExecutionOutputSchema,
  },
  {
    name: "list_tasks",
    description: "List all execution tasks with optional filtering by status or category",
    inputSchema: ListTasksInputSchema,
    outputSchema: ListTasksOutputSchema,
  },
  {
    name: "update_task_status",
    description: "Update the status of a specific execution task",
    inputSchema: UpdateTaskStatusInputSchema,
    outputSchema: UpdateTaskStatusOutputSchema,
  },
];

// Tool handlers
export const executionHandlers = {
  start_execution: async (args: z.infer<typeof StartExecutionInputSchema>) => {
    try {
      const workspacePath = args.workspacePath || "workspace";
      const projectPath = join(workspacePath, args.projectName);
      
      // Check if project exists and specification is completed
      const configPath = join(projectPath, ".compass.json");
      if (!await exists(configPath)) {
        return StartExecutionOutputSchema.parse({
          success: false,
          message: "Project not found",
          error: "Project configuration file not found"
        });
      }
      
      const configContent = await readFile(configPath);
      const config = JSON.parse(configContent);
      
      if (!config.specificationCompletedDate) {
        return StartExecutionOutputSchema.parse({
          success: false,
          message: "Specification phase must be completed before starting execution",
          error: "Specification phase must be completed before starting execution"
        });
      }
      
      // Read specification content to generate tasks
      const specPath = join(projectPath, "specification");
      const specFiles = [];
      try {
        for await (const entry of Deno.readDir(specPath)) {
          if (entry.isFile && entry.name.endsWith('.md')) {
            specFiles.push(entry.name);
          }
        }
      } catch {
        return StartExecutionOutputSchema.parse({
          success: false,
          message: "No specification files found",
          error: "No specification files found in specification directory"
        });
      }
      
      // Read the first specification file (main spec)
      const specContent = await readFile(join(specPath, specFiles[0]));
      
      // Generate tasks from specification
      const tasks = generateTasksFromSpecification(specContent);
      
      // Create execution directory
      const executionPath = join(projectPath, "execution");
      await Deno.mkdir(executionPath, { recursive: true });
      
      // Create execution plan
      const executionPlan = `# Execution Plan
**Project:** ${args.projectName}
**Started:** ${new Date().toISOString()}
**Total Tasks:** ${tasks.length}

## Overview
This execution plan breaks down the specification into actionable tasks organized by category and priority.

## Task Categories
- **Setup**: Environment and project initialization
- **Database**: Data schema and persistence layer
- **Backend**: API and business logic
- **Frontend**: User interface and experience  
- **Testing**: Quality assurance and validation
- **Deployment**: Infrastructure and CI/CD

## Execution Strategy
1. Complete setup tasks first to establish development environment
2. Implement core backend functionality and database schema
3. Build frontend components and user workflows
4. Add comprehensive testing coverage
5. Setup deployment and monitoring

## Task Breakdown
${tasks.map(task => `### ${task.title}
**ID:** ${task.id}
**Priority:** ${task.priority}
**Category:** ${task.category}
**Estimated Hours:** ${task.estimatedHours}
**Status:** ${task.status}

${task.description}
`).join('\n')}
`;

      const executionPlanPath = join(executionPath, "execution-plan.md");
      await writeFile({ path: executionPlanPath, content: executionPlan });
      
      // Save tasks as JSON for tracking
      const tasksPath = join(executionPath, "tasks.json");
      await writeFile({ path: tasksPath, content: JSON.stringify(tasks, null, 2) });
      
      // Update project config
      config.currentPhase = "execution";
      config.executionStartedDate = new Date().toISOString();
      await writeFile({ path: configPath, content: JSON.stringify(config, null, 2) });
      
      return StartExecutionOutputSchema.parse({
        success: true,
        message: `Execution plan created with ${tasks.length} tasks`,
        data: {
          phase: "execution",
          projectName: args.projectName,
          executionPlanPath,
          tasksPath,
          tasks
        }
      });
      
    } catch (error) {
      return StartExecutionOutputSchema.parse({
        success: false,
        message: "Failed to start execution phase",
        error: error instanceof Error ? error.message : String(error)
      });
    }
  },

  list_tasks: async (args: z.infer<typeof ListTasksInputSchema>) => {
    try {
      const workspacePath = args.workspacePath || "workspace";
      const projectPath = join(workspacePath, args.projectName);
      const tasksPath = join(projectPath, "execution", "tasks.json");
      
      if (!await exists(tasksPath)) {
        return ListTasksOutputSchema.parse({
          success: false,
          error: "Tasks file not found. Start execution phase first."
        });
      }
      
      const tasksContent = await readFile(tasksPath);
      let tasks = JSON.parse(tasksContent);
      
      // Apply filters
      if (args.status) {
        tasks = tasks.filter((task: any) => task.status === args.status);
      }
      
      if (args.category) {
        tasks = tasks.filter((task: any) => task.category === args.category);
      }
      
      // Calculate summary
      const allTasksContent = await readFile(tasksPath);
      const allTasks = JSON.parse(allTasksContent);
      const summary = {
        total: allTasks.length,
        pending: allTasks.filter((t: any) => t.status === "pending").length,
        in_progress: allTasks.filter((t: any) => t.status === "in_progress").length,
        completed: allTasks.filter((t: any) => t.status === "completed").length,
        blocked: allTasks.filter((t: any) => t.status === "blocked").length
      };
      
      return ListTasksOutputSchema.parse({
        success: true,
        data: {
          projectName: args.projectName,
          tasks,
          summary
        }
      });
      
    } catch (error) {
      return ListTasksOutputSchema.parse({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  },

  update_task_status: async (args: z.infer<typeof UpdateTaskStatusInputSchema>) => {
    try {
      const workspacePath = args.workspacePath || "workspace";
      const projectPath = join(workspacePath, args.projectName);
      const tasksPath = join(projectPath, "execution", "tasks.json");
      
      if (!await exists(tasksPath)) {
        return UpdateTaskStatusOutputSchema.parse({
          success: false,
          message: "Tasks file not found",
          error: "Tasks file not found. Start execution phase first."
        });
      }
      
      const tasksContent = await readFile(tasksPath);
      const tasks = JSON.parse(tasksContent);
      
      // Find and update the task
      const taskIndex = tasks.findIndex((task: any) => task.id === args.taskId);
      if (taskIndex === -1) {
        return UpdateTaskStatusOutputSchema.parse({
          success: false,
          message: "Task not found",
          error: `Task with ID ${args.taskId} not found`
        });
      }
      
      const task = tasks[taskIndex];
      task.status = args.status;
      if (args.notes) {
        task.notes = args.notes;
      }
      if (args.status === "completed") {
        task.completedDate = new Date().toISOString();
      }
      
      // Save updated tasks
      await writeFile({ path: tasksPath, content: JSON.stringify(tasks, null, 2) });
      
      return UpdateTaskStatusOutputSchema.parse({
        success: true,
        message: `Task ${args.taskId} status updated to ${args.status}`,
        data: {
          task: {
            id: task.id,
            title: task.title,
            status: task.status,
            completedDate: task.completedDate,
            notes: task.notes
          }
        }
      });
      
    } catch (error) {
      return UpdateTaskStatusOutputSchema.parse({
        success: false,
        message: "Failed to update task status",
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }
};