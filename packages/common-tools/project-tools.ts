import { z } from "zod";
import { exists } from "@std/fs";
import { join } from "@std/path";
import type { MCPTool } from "@packages/mcp-core/types.ts";

// Schemas
export const FindProjectsInputSchema = z.object({
  root_directory: z.string().optional().describe("Root directory to search for projects"),
  project_type: z.string().optional().describe("Type of projects to find (orchestration, npm, deno, etc.)"),
});

export const FindProjectsOutputSchema = z.object({
  projects: z.array(z.object({
    name: z.string(),
    path: z.string(),
    type: z.string(),
    metadata: z.record(z.any()).optional(),
  })),
  total: z.number(),
});

export const GetProjectInfoInputSchema = z.object({
  project_path: z.string().describe("Path to the project"),
});

export const GetProjectInfoOutputSchema = z.object({
  name: z.string(),
  path: z.string(),
  type: z.string(),
  config_files: z.array(z.string()),
  metadata: z.record(z.any()).optional(),
});

export const CreateProjectInputSchema = z.object({
  name: z.string().describe("Name of the project"),
  path: z.string().describe("Path where to create the project"),
  template: z.string().optional().describe("Project template to use"),
});

export const CreateProjectOutputSchema = z.object({
  success: z.boolean(),
  name: z.string(),
  path: z.string(),
  files_created: z.array(z.string()),
});

// Tool definitions
export const projectTools: MCPTool[] = [
  {
    name: "find_projects",
    description: "Find projects in a directory tree",
    inputSchema: FindProjectsInputSchema,
    outputSchema: FindProjectsOutputSchema,
  },
  {
    name: "get_project_info",
    description: "Get detailed information about a project",
    inputSchema: GetProjectInfoInputSchema,
    outputSchema: GetProjectInfoOutputSchema,
  },
  {
    name: "create_project",
    description: "Create a new project from template",
    inputSchema: CreateProjectInputSchema,
    outputSchema: CreateProjectOutputSchema,
  },
];

// Project type detectors
const projectDetectors = {
  orchestration: (path: string) => exists(join(path, ".orchestration.json")),
  npm: (path: string) => exists(join(path, "package.json")),
  deno: (path: string) => exists(join(path, "deno.json")),
  cargo: (path: string) => exists(join(path, "Cargo.toml")),
  python: async (path: string) => {
    return await exists(join(path, "pyproject.toml")) ||
           await exists(join(path, "requirements.txt")) ||
           await exists(join(path, "setup.py"));
  },
  git: (path: string) => exists(join(path, ".git")),
};

// Tool handlers
export const projectHandlers = {
  find_projects: async (args: z.infer<typeof FindProjectsInputSchema>) => {
    const { root_directory = Deno.cwd(), project_type } = args;
    
    try {
      const projects = [];
      
      async function scanDirectory(dirPath: string, depth = 0) {
        if (depth > 3) return; // Limit recursion depth
        
        try {
          for await (const entry of Deno.readDir(dirPath)) {
            if (entry.isDirectory && !entry.name.startsWith(".")) {
              const entryPath = join(dirPath, entry.name);
              
              // Check each project type
              for (const [type, detector] of Object.entries(projectDetectors)) {
                if (project_type && type !== project_type) continue;
                
                if (await detector(entryPath)) {
                  let metadata;
                  
                  // Try to load project metadata
                  try {
                    if (type === "orchestration") {
                      const metaPath = join(entryPath, ".orchestration.json");
                      metadata = JSON.parse(await Deno.readTextFile(metaPath));
                    } else if (type === "npm") {
                      const pkgPath = join(entryPath, "package.json");
                      metadata = JSON.parse(await Deno.readTextFile(pkgPath));
                    } else if (type === "deno") {
                      const denoPath = join(entryPath, "deno.json");
                      metadata = JSON.parse(await Deno.readTextFile(denoPath));
                    }
                  } catch {
                    // Ignore metadata errors
                  }
                  
                  projects.push({
                    name: entry.name,
                    path: entryPath,
                    type,
                    metadata,
                  });
                  break; // Don't check other types for this directory
                }
              }
              
              // Recurse into subdirectories
              await scanDirectory(entryPath, depth + 1);
            }
          }
        } catch {
          // Ignore directories we can't read
        }
      }
      
      await scanDirectory(root_directory);
      
      return {
        projects,
        total: projects.length,
      };
    } catch (error) {
      throw new Error(`Failed to find projects: ${error instanceof Error ? error.message : String(error)}`);
    }
  },

  get_project_info: async (args: z.infer<typeof GetProjectInfoInputSchema>) => {
    const { project_path } = args;
    
    try {
      if (!await exists(project_path)) {
        throw new Error(`Project path ${project_path} does not exist`);
      }
      
      // Determine project type
      let projectType = "unknown";
      let metadata;
      const configFiles = [];
      
      for (const [type, detector] of Object.entries(projectDetectors)) {
        if (await detector(project_path)) {
          projectType = type;
          break;
        }
      }
      
      // Collect config files
      const commonConfigFiles = [
        ".orchestration.json",
        "package.json",
        "deno.json",
        "Cargo.toml",
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        ".gitignore",
        "README.md",
      ];
      
      for (const file of commonConfigFiles) {
        if (await exists(join(project_path, file))) {
          configFiles.push(file);
        }
      }
      
      // Load metadata based on project type
      try {
        if (projectType === "orchestration") {
          const metaPath = join(project_path, ".orchestration.json");
          metadata = JSON.parse(await Deno.readTextFile(metaPath));
        } else if (projectType === "npm") {
          const pkgPath = join(project_path, "package.json");
          metadata = JSON.parse(await Deno.readTextFile(pkgPath));
        } else if (projectType === "deno") {
          const denoPath = join(project_path, "deno.json");
          metadata = JSON.parse(await Deno.readTextFile(denoPath));
        }
      } catch {
        // Ignore metadata errors
      }
      
      const projectName = metadata?.name || project_path.split("/").pop() || "unknown";
      
      return {
        name: projectName,
        path: project_path,
        type: projectType,
        config_files: configFiles,
        metadata,
      };
    } catch (error) {
      throw new Error(`Failed to get project info: ${error instanceof Error ? error.message : String(error)}`);
    }
  },

  create_project: async (args: z.infer<typeof CreateProjectInputSchema>) => {
    const { name, path, template = "basic" } = args;
    
    try {
      const projectPath = join(path, name);
      
      if (await exists(projectPath)) {
        throw new Error(`Project directory ${projectPath} already exists`);
      }
      
      await Deno.mkdir(projectPath, { recursive: true });
      const filesCreated = [projectPath];
      
      // Create basic project structure based on template
      if (template === "deno" || template === "basic") {
        const denoConfig = {
          name,
          version: "1.0.0",
          tasks: {
            start: "deno run --allow-all main.ts",
            test: "deno test",
            fmt: "deno fmt",
            lint: "deno lint",
          },
        };
        
        await Deno.writeTextFile(
          join(projectPath, "deno.json"),
          JSON.stringify(denoConfig, null, 2)
        );
        filesCreated.push("deno.json");
        
        await Deno.writeTextFile(
          join(projectPath, "main.ts"),
          `// ${name} - Main entry point\n\nfunction main() {\n  console.log("Hello from ${name}!");\n}\n\nif (import.meta.main) {\n  main();\n}\n`
        );
        filesCreated.push("main.ts");
      }
      
      // Create README
      await Deno.writeTextFile(
        join(projectPath, "README.md"),
        `# ${name}\n\nA new project created with common-tools.\n\n## Getting Started\n\n\`\`\`bash\ncd ${name}\n# Add your instructions here\n\`\`\`\n`
      );
      filesCreated.push("README.md");
      
      return {
        success: true,
        name,
        path: projectPath,
        files_created: filesCreated,
      };
    } catch (error) {
      throw new Error(`Failed to create project: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
};