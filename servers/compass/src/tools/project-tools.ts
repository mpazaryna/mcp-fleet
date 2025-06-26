import { z } from "zod";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
// Temporarily implement writeFile locally until import issues are resolved
async function writeFile(args: { path: string; content: string }) {
  const dir = args.path.substring(0, args.path.lastIndexOf("/"));
  await Deno.mkdir(dir, { recursive: true });
  await Deno.writeTextFile(args.path, args.content);
}
import type { MCPTool } from "@packages/mcp-core/mod.ts";

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
      
      // Create project structure
      await Deno.mkdir(projectPath, { recursive: true });
      await Deno.mkdir(join(projectPath, "exploration"), { recursive: true });
      await Deno.mkdir(join(projectPath, "specification"), { recursive: true });
      await Deno.mkdir(join(projectPath, "execution"), { recursive: true });
      await Deno.mkdir(join(projectPath, "feedback"), { recursive: true });
      
      // Create metadata
      const metadata = {
        name,
        created: new Date().toISOString(),
        currentPhase: "exploration",
        status: "active",
        sessionCount: 0,
      };
      
      await writeFile({
        path: join(projectPath, ".compass.json"),
        content: JSON.stringify(metadata, null, 2),
      });
      
      // Create initial tasks file
      const tasksContent = `# ${name} - Project Tasks

## Phase 1: Exploration
- [ ] Complete initial problem exploration

## Phase 2: Specification
*Tasks will be generated after exploration completion*

## Phase 3: Execution
*Tasks will be generated after specification completion*

## Phase 4: Feedback & Learning
*Tasks will be generated after execution completion*
`;
      
      await writeFile({
        path: join(projectPath, "tasks.md"),
        content: tasksContent,
      });
      
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
      
      const metadata = JSON.parse(await Deno.readTextFile(join(projectPath, ".compass.json")));
      
      // TODO: Parse tasks from tasks.md
      const explorationTasks = [
        { text: "Complete initial problem exploration", completed: false },
      ];
      
      return {
        project_name,
        current_phase: metadata.currentPhase || "exploration",
        status_summary: "Exploration phase - Ready to begin",
        exploration_tasks: explorationTasks,
        next_action: "start_exploration",
        recommendations: ["Begin systematic exploration phase"],
      };
    } catch (error) {
      throw error;
    }
  },
};