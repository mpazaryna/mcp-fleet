import { z } from "zod";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import type { MCPTool } from "@packages/mcp-core/mod.ts";
import { ProjectManager } from "../managers/project-manager.ts";

// Schema definitions
const InitProjectInputSchema = z.object({
  name: z.string().describe("Name of the project to initialize"),
  projectsDir: z.string().optional().describe("Projects directory (for testing)"),
});

const InitProjectOutputSchema = z.object({
  success: z.boolean(),
  project_name: z.string(),
  project_path: z.string(),
  message: z.string(),
  next_steps: z.array(z.string()),
});

const ListProjectsInputSchema = z.object({
  projectsDir: z.string().optional().describe("Projects directory (for testing)"),
});

const ListProjectsOutputSchema = z.object({
  projects: z.array(z.object({
    name: z.string(),
    path: z.string(),
    status: z.string(),
    current_phase: z.string(),
    created: z.string(),
  })),
  total: z.number(),
});

const GetProjectStatusInputSchema = z.object({
  project_name: z.string().describe("Name of the project"),
  projectsDir: z.string().optional().describe("Projects directory (for testing)"),
});

const GetProjectStatusOutputSchema = z.object({
  project_name: z.string(),
  current_phase: z.string(),
  status_summary: z.string(),
  exploration_tasks: z.array(z.object({
    text: z.string(),
    completed: z.boolean(),
  })),
  next_action: z.string(),
  recommendations: z.array(z.string()),
});

// Tool definitions
export const projectTools: MCPTool[] = [
  {
    name: "init_project",
    description: "Initialize a new Compass project with systematic methodology structure",
    inputSchema: InitProjectInputSchema,
    outputSchema: InitProjectOutputSchema,
  },
  {
    name: "list_projects",
    description: "List all available Compass projects with status information",
    inputSchema: ListProjectsInputSchema,
    outputSchema: ListProjectsOutputSchema,
  },
  {
    name: "get_project_status",
    description: "Get detailed status of a specific project including tasks and recommendations",
    inputSchema: GetProjectStatusInputSchema,
    outputSchema: GetProjectStatusOutputSchema,
  },
];

// Helper functions
async function getProjectsDirectory(customDir?: string): Promise<string> {
  if (customDir) return customDir;
  
  // Check if running in Docker container with COMPASS_WORKSPACE env var
  const dockerWorkspace = Deno.env.get("COMPASS_WORKSPACE");
  if (dockerWorkspace) {
    await Deno.mkdir(dockerWorkspace, { recursive: true });
    return dockerWorkspace;
  }
  
  // Fall back to home directory for native installations
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
  if (!homeDir) {
    throw new Error("Unable to determine user home directory");
  }
  
  const projectsDir = join(homeDir, "CompassProjects");
  await Deno.mkdir(projectsDir, { recursive: true });
  return projectsDir;
}

// Tool handlers
export const projectHandlers = {
  init_project: async (args: z.infer<typeof InitProjectInputSchema>) => {
    const { name, projectsDir: customDir } = args;
    
    try {
      const projectsDir = await getProjectsDirectory(customDir);
      const projectPath = join(projectsDir, name);
      
      // Check if project already exists
      if (await exists(projectPath)) {
        return {
          success: false,
          project_name: name,
          project_path: projectPath,
          message: `Project '${name}' already exists`,
          next_steps: [],
        };
      }
      
      // Create project directory first
      await Deno.mkdir(projectPath, { recursive: true });
      
      // Use ProjectManager to create structure
      const manager = new ProjectManager(projectPath);
      await manager.createProjectStructure(name);
      
      return {
        success: true,
        project_name: name,
        project_path: projectPath,
        message: `COMPASS PROJECT INITIALIZED

Project '${name}' created with systematic 4-phase methodology:
• Phase 1: EXPLORATION (Current) - Understand the problem space  
• Phase 2: SPECIFICATION - Transform insights into structured requirements
• Phase 3: EXECUTION - Implement solutions based on solid understanding
• Phase 4: FEEDBACK & LEARNING - Capture knowledge for future projects

METHODOLOGY ENFORCEMENT: You must complete exploration before moving to specification or implementation.`,
        next_steps: [
          "Project structure created with 4-phase methodology",
          "Initial exploration tasks generated",
          "NEXT ACTION: Begin systematic exploration phase",
          `Project location: ${projectPath}`,
        ],
      };
    } catch (error) {
      return {
        success: false,
        project_name: name,
        project_path: "",
        message: `Failed to initialize project: ${error instanceof Error ? error.message : String(error)}`,
        next_steps: [],
      };
    }
  },
  
  list_projects: async (args: z.infer<typeof ListProjectsInputSchema>) => {
    const { projectsDir: customDir } = args;
    
    try {
      const projectsDir = await getProjectsDirectory(customDir);
      const projects = [];
      
      if (await exists(projectsDir)) {
        for await (const entry of Deno.readDir(projectsDir)) {
          if (entry.isDirectory) {
            const projectPath = join(projectsDir, entry.name);
            const metadataPath = join(projectPath, ".compass.json");
            
            if (await exists(metadataPath)) {
              const metadata = JSON.parse(await Deno.readTextFile(metadataPath));
              projects.push({
                name: entry.name,
                path: projectPath,
                status: metadata.status || "active",
                current_phase: metadata.currentPhase || "exploration",
                created: metadata.created || "unknown",
              });
            }
          }
        }
      }
      
      return {
        projects,
        total: projects.length,
      };
    } catch (error) {
      return {
        projects: [],
        total: 0,
      };
    }
  },
  
  get_project_status: async (args: z.infer<typeof GetProjectStatusInputSchema>) => {
    const { project_name, projectsDir: customDir } = args;
    
    try {
      const projectsDir = await getProjectsDirectory(customDir);
      const projectPath = join(projectsDir, project_name);
      
      if (!await exists(projectPath)) {
        throw new Error(`Project '${project_name}' not found`);
      }
      
      const manager = new ProjectManager(projectPath);
      const metadata = await manager.loadMetadata();
      
      if (!metadata) {
        throw new Error(`Invalid project metadata for '${project_name}'`);
      }
      
      const tasksData = await manager.parseTasksFile();
      const status = manager.getCurrentStatus(tasksData.explorationTasks);
      
      const incompleteTasks = tasksData.explorationTasks.filter(t => !t.completed);
      const recommendations = [];
      
      if (incompleteTasks.length > 0) {
        recommendations.push(`Continue exploration: ${incompleteTasks[0].text}`);
      } else {
        recommendations.push("Exploration complete - ready for specification phase");
      }
      
      return {
        project_name,
        current_phase: metadata.currentPhase || "exploration",
        status_summary: status,
        exploration_tasks: tasksData.explorationTasks,
        next_action: incompleteTasks.length > 0 ? "start_exploration" : "generate_specification",
        recommendations,
      };
    } catch (error) {
      throw error;
    }
  },
};