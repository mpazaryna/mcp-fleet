import { z } from "zod";
import { exists } from "@std/fs";
import { join } from "@std/path";
import type { MCPTool } from "@packages/mcp-core/types.ts";

// Schemas
export const ReadFileInputSchema = z.object({
  path: z.string().describe("Path to the file to read"),
});

export const ReadFileOutputSchema = z.object({
  content: z.string(),
  size: z.number(),
  exists: z.boolean(),
});

export const WriteFileInputSchema = z.object({
  path: z.string().describe("Path to the file to write"),
  content: z.string().describe("Content to write to the file"),
  create_dirs: z.boolean().optional().describe("Create directories if they don't exist"),
});

export const WriteFileOutputSchema = z.object({
  success: z.boolean(),
  path: z.string(),
  size: z.number(),
});

export const ListDirectoryInputSchema = z.object({
  path: z.string().describe("Path to the directory to list"),
  include_hidden: z.boolean().optional().describe("Include hidden files/directories"),
});

export const ListDirectoryOutputSchema = z.object({
  entries: z.array(z.object({
    name: z.string(),
    type: z.enum(["file", "directory"]),
    size: z.number().optional(),
  })),
  total: z.number(),
});

export const FileExistsInputSchema = z.object({
  path: z.string().describe("Path to check"),
});

export const FileExistsOutputSchema = z.object({
  exists: z.boolean(),
  type: z.enum(["file", "directory", "unknown"]).optional(),
});

// Tool definitions
export const fileTools: MCPTool[] = [
  {
    name: "read_file",
    description: "Read the contents of a file",
    inputSchema: ReadFileInputSchema,
    outputSchema: ReadFileOutputSchema,
  },
  {
    name: "write_file", 
    description: "Write content to a file",
    inputSchema: WriteFileInputSchema,
    outputSchema: WriteFileOutputSchema,
  },
  {
    name: "list_directory",
    description: "List contents of a directory",
    inputSchema: ListDirectoryInputSchema,
    outputSchema: ListDirectoryOutputSchema,
  },
  {
    name: "file_exists",
    description: "Check if a file or directory exists",
    inputSchema: FileExistsInputSchema,
    outputSchema: FileExistsOutputSchema,
  },
];

// Tool handlers
export const fileHandlers = {
  read_file: async (args: z.infer<typeof ReadFileInputSchema>) => {
    const { path } = args;
    
    try {
      if (!await exists(path)) {
        return {
          content: "",
          size: 0,
          exists: false,
        };
      }
      
      const content = await Deno.readTextFile(path);
      const stat = await Deno.stat(path);
      
      return {
        content,
        size: stat.size,
        exists: true,
      };
    } catch (error) {
      throw new Error(`Failed to read file ${path}: ${error instanceof Error ? error.message : String(error)}`);
    }
  },

  write_file: async (args: z.infer<typeof WriteFileInputSchema>) => {
    const { path, content, create_dirs = false } = args;
    
    try {
      if (create_dirs) {
        const dir = path.substring(0, path.lastIndexOf("/"));
        if (dir) {
          await Deno.mkdir(dir, { recursive: true });
        }
      }
      
      await Deno.writeTextFile(path, content);
      const stat = await Deno.stat(path);
      
      return {
        success: true,
        path,
        size: stat.size,
      };
    } catch (error) {
      throw new Error(`Failed to write file ${path}: ${error instanceof Error ? error.message : String(error)}`);
    }
  },

  list_directory: async (args: z.infer<typeof ListDirectoryInputSchema>) => {
    const { path, include_hidden = false } = args;
    
    try {
      if (!await exists(path)) {
        throw new Error(`Directory ${path} does not exist`);
      }
      
      const entries = [];
      
      for await (const entry of Deno.readDir(path)) {
        if (!include_hidden && entry.name.startsWith(".")) {
          continue;
        }
        
        let size: number | undefined;
        try {
          const stat = await Deno.stat(join(path, entry.name));
          size = entry.isFile ? stat.size : undefined;
        } catch {
          // Ignore stat errors
        }
        
        entries.push({
          name: entry.name,
          type: entry.isFile ? "file" as const : "directory" as const,
          size,
        });
      }
      
      return {
        entries,
        total: entries.length,
      };
    } catch (error) {
      throw new Error(`Failed to list directory ${path}: ${error instanceof Error ? error.message : String(error)}`);
    }
  },

  file_exists: async (args: z.infer<typeof FileExistsInputSchema>) => {
    const { path } = args;
    
    try {
      if (!await exists(path)) {
        return {
          exists: false,
        };
      }
      
      const stat = await Deno.stat(path);
      
      return {
        exists: true,
        type: stat.isFile ? "file" : stat.isDirectory ? "directory" : "unknown",
      };
    } catch {
      return {
        exists: false,
      };
    }
  },
};