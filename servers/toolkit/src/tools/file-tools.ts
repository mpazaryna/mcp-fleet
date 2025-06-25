import { z } from "zod";
import type { MCPTool } from "@packages/mcp-core/types.ts";

// Schemas for file operations
export const WriteFileInputSchema = z.object({
  file_path: z.string().describe("Path to the file to write"),
  content: z.string().describe("Content to write to the file"),
  create_dirs: z.boolean().optional().default(true).describe(
    "Create parent directories if they don't exist"
  ),
  encoding: z.enum(["utf8", "base64"]).optional().default("utf8").describe(
    "File encoding"
  ),
});

export const WriteFileOutputSchema = z.object({
  success: z.boolean(),
  file_path: z.string(),
  bytes_written: z.number(),
  created_dirs: z.array(z.string()).optional(),
});

export const ReadFileInputSchema = z.object({
  file_path: z.string().describe("Path to the file to read"),
  encoding: z.enum(["utf8", "base64"]).optional().default("utf8").describe(
    "File encoding"
  ),
});

export const ReadFileOutputSchema = z.object({
  success: z.boolean(),
  file_path: z.string(),
  content: z.string(),
  size: z.number(),
  modified: z.string(),
});

export const CreateDirectoryInputSchema = z.object({
  dir_path: z.string().describe("Path to the directory to create"),
  recursive: z.boolean().optional().default(true).describe(
    "Create parent directories if they don't exist"
  ),
});

export const CreateDirectoryOutputSchema = z.object({
  success: z.boolean(),
  dir_path: z.string(),
  created: z.boolean(),
  already_exists: z.boolean(),
});

export const ListFilesInputSchema = z.object({
  dir_path: z.string().describe("Path to the directory to list"),
  pattern: z.string().optional().describe("Glob pattern to filter files"),
  include_dirs: z.boolean().optional().default(true).describe(
    "Include directories in results"
  ),
  recursive: z.boolean().optional().default(false).describe(
    "List files recursively"
  ),
});

export const ListFilesOutputSchema = z.object({
  success: z.boolean(),
  dir_path: z.string(),
  files: z.array(z.object({
    name: z.string(),
    path: z.string(),
    type: z.enum(["file", "directory"]),
    size: z.number(),
    modified: z.string(),
  })),
  total: z.number(),
});

export const DeleteFileInputSchema = z.object({
  file_path: z.string().describe("Path to the file or directory to delete"),
  recursive: z.boolean().optional().default(false).describe(
    "Delete directories recursively"
  ),
});

export const DeleteFileOutputSchema = z.object({
  success: z.boolean(),
  file_path: z.string(),
  deleted: z.boolean(),
});

// Tool definitions
export const fileTools: MCPTool[] = [
  {
    name: "write_file",
    description: "Write content to a file, creating directories as needed",
    inputSchema: WriteFileInputSchema,
    outputSchema: WriteFileOutputSchema,
  },
  {
    name: "read_file",
    description: "Read content from a file",
    inputSchema: ReadFileInputSchema,
    outputSchema: ReadFileOutputSchema,
  },
  {
    name: "create_directory",
    description: "Create a directory with optional recursive creation",
    inputSchema: CreateDirectoryInputSchema,
    outputSchema: CreateDirectoryOutputSchema,
  },
  {
    name: "list_files",
    description: "List files and directories with optional filtering",
    inputSchema: ListFilesInputSchema,
    outputSchema: ListFilesOutputSchema,
  },
  {
    name: "delete_file",
    description: "Delete a file or directory",
    inputSchema: DeleteFileInputSchema,
    outputSchema: DeleteFileOutputSchema,
  },
];

// Helper functions
async function ensureDirectory(dirPath: string): Promise<string[]> {
  const createdDirs: string[] = [];
  try {
    await Deno.mkdir(dirPath, { recursive: true });
    createdDirs.push(dirPath);
  } catch (error) {
    if (!(error instanceof Deno.errors.AlreadyExists)) {
      throw error;
    }
  }
  return createdDirs;
}

function matchesPattern(filename: string, pattern?: string): boolean {
  if (!pattern) return true;
  
  // Simple glob pattern matching
  const regex = new RegExp(
    "^" + pattern.replace(/\*/g, ".*").replace(/\?/g, ".") + "$"
  );
  return regex.test(filename);
}

async function listDirectoryRecursive(
  files: Array<{
    name: string;
    path: string;
    type: "file" | "directory";
    size: number;
    modified: string;
  }>,
  currentPath: string,
  pattern?: string,
  includeDirectories?: boolean,
  recursive?: boolean
) {
  for await (const dirEntry of Deno.readDir(currentPath)) {
    const fullPath = `${currentPath}/${dirEntry.name}`;
    
    if (dirEntry.isFile) {
      if (matchesPattern(dirEntry.name, pattern)) {
        const stat = await Deno.stat(fullPath);
        files.push({
          name: dirEntry.name,
          path: fullPath,
          type: "file",
          size: stat.size,
          modified: stat.mtime?.toISOString() || "",
        });
      }
    } else if (dirEntry.isDirectory) {
      if (includeDirectories && matchesPattern(dirEntry.name, pattern)) {
        const stat = await Deno.stat(fullPath);
        files.push({
          name: dirEntry.name,
          path: fullPath,
          type: "directory",
          size: 0,
          modified: stat.mtime?.toISOString() || "",
        });
      }
      
      if (recursive) {
        await listDirectoryRecursive(files, fullPath, pattern, includeDirectories, recursive);
      }
    }
  }
}

// Tool handlers
export const fileHandlers = {
  write_file: async (args: z.infer<typeof WriteFileInputSchema>) => {
    const { file_path, content, create_dirs, encoding } = args;

    try {
      let createdDirs: string[] = [];

      if (create_dirs) {
        const dirPath = file_path.substring(0, file_path.lastIndexOf("/"));
        if (dirPath) {
          createdDirs = await ensureDirectory(dirPath);
        }
      }

      let bytesWritten: number;
      if (encoding === "base64") {
        const bytes = Uint8Array.from(atob(content), c => c.charCodeAt(0));
        await Deno.writeFile(file_path, bytes);
        bytesWritten = bytes.length;
      } else {
        await Deno.writeTextFile(file_path, content);
        bytesWritten = new TextEncoder().encode(content).length;
      }

      console.error(`📁 Wrote ${bytesWritten} bytes to ${file_path}`);

      return {
        success: true,
        file_path,
        bytes_written: bytesWritten,
        created_dirs: createdDirs.length > 0 ? createdDirs : undefined,
      };
    } catch (error) {
      throw new Error(
        `Failed to write file: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  },

  read_file: async (args: z.infer<typeof ReadFileInputSchema>) => {
    const { file_path, encoding } = args;

    try {
      const stat = await Deno.stat(file_path);
      
      let content: string;
      if (encoding === "base64") {
        const bytes = await Deno.readFile(file_path);
        content = btoa(String.fromCharCode(...bytes));
      } else {
        content = await Deno.readTextFile(file_path);
      }

      return {
        success: true,
        file_path,
        content,
        size: stat.size,
        modified: stat.mtime?.toISOString() || "",
      };
    } catch (error) {
      throw new Error(
        `Failed to read file: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  },

  create_directory: async (args: z.infer<typeof CreateDirectoryInputSchema>) => {
    const { dir_path, recursive } = args;

    try {
      let created = false;
      let alreadyExists = false;

      // Check if directory already exists first
      try {
        const stat = await Deno.stat(dir_path);
        if (stat.isDirectory) {
          alreadyExists = true;
        }
      } catch {
        // Directory doesn't exist, we'll create it
      }

      if (!alreadyExists) {
        try {
          await Deno.mkdir(dir_path, { recursive });
          created = true;
        } catch (error) {
          if (error instanceof Deno.errors.AlreadyExists) {
            alreadyExists = true;
          } else {
            throw error;
          }
        }
      }

      console.error(`📁 Directory ${created ? "created" : "already exists"}: ${dir_path}`);

      return {
        success: true,
        dir_path,
        created,
        already_exists: alreadyExists,
      };
    } catch (error) {
      throw new Error(
        `Failed to create directory: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  },

  list_files: async (args: z.infer<typeof ListFilesInputSchema>) => {
    const { dir_path, pattern, include_dirs, recursive } = args;

    try {
      const files: Array<{
        name: string;
        path: string;
        type: "file" | "directory";
        size: number;
        modified: string;
      }> = [];

      await listDirectoryRecursive(files, dir_path, pattern, include_dirs, recursive);

      return {
        success: true,
        dir_path,
        files,
        total: files.length,
      };
    } catch (error) {
      throw new Error(
        `Failed to list files: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  },

  delete_file: async (args: z.infer<typeof DeleteFileInputSchema>) => {
    const { file_path, recursive } = args;

    try {
      let deleted = false;

      try {
        await Deno.remove(file_path, { recursive });
        deleted = true;
        console.error(`🗑️ Deleted: ${file_path}`);
      } catch (error) {
        if (!(error instanceof Deno.errors.NotFound)) {
          throw error;
        }
      }

      return {
        success: true,
        file_path,
        deleted,
      };
    } catch (error) {
      throw new Error(
        `Failed to delete file: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  },
};