import { z } from "zod";
import type { MCPTool } from "@packages/mcp-core/types.ts";

// Schemas
export const GitStatusInputSchema = z.object({
  path: z.string().optional().describe("Path to git repository (defaults to current directory)"),
});

export const GitStatusOutputSchema = z.object({
  branch: z.string(),
  ahead: z.number(),
  behind: z.number(),
  staged: z.array(z.string()),
  modified: z.array(z.string()),
  untracked: z.array(z.string()),
  clean: z.boolean(),
});

export const GitLogInputSchema = z.object({
  path: z.string().optional().describe("Path to git repository"),
  limit: z.number().optional().describe("Number of commits to show (default: 10)"),
  oneline: z.boolean().optional().describe("Show one line per commit"),
});

export const GitLogOutputSchema = z.object({
  commits: z.array(z.object({
    hash: z.string(),
    message: z.string(),
    author: z.string(),
    date: z.string(),
  })),
  total: z.number(),
});

export const GitCommitInputSchema = z.object({
  path: z.string().optional().describe("Path to git repository"),
  message: z.string().describe("Commit message"),
  files: z.array(z.string()).optional().describe("Specific files to commit (defaults to all staged)"),
});

export const GitCommitOutputSchema = z.object({
  success: z.boolean(),
  hash: z.string().optional(),
  message: z.string(),
  files_committed: z.number(),
});

export const GitBranchInputSchema = z.object({
  path: z.string().optional().describe("Path to git repository"),
  list_all: z.boolean().optional().describe("List all branches (local and remote)"),
});

export const GitBranchOutputSchema = z.object({
  current_branch: z.string(),
  branches: z.array(z.object({
    name: z.string(),
    current: z.boolean(),
    remote: z.boolean(),
  })),
});

// Tool definitions
export const gitTools: MCPTool[] = [
  {
    name: "git_status",
    description: "Get git status of a repository",
    inputSchema: GitStatusInputSchema,
    outputSchema: GitStatusOutputSchema,
  },
  {
    name: "git_log",
    description: "Get git commit history",
    inputSchema: GitLogInputSchema,
    outputSchema: GitLogOutputSchema,
  },
  {
    name: "git_commit",
    description: "Create a git commit",
    inputSchema: GitCommitInputSchema,
    outputSchema: GitCommitOutputSchema,
  },
  {
    name: "git_branches",
    description: "List git branches",
    inputSchema: GitBranchInputSchema,
    outputSchema: GitBranchOutputSchema,
  },
];

// Helper function to run git commands
async function runGitCommand(args: string[], cwd?: string): Promise<string> {
  const command = new Deno.Command("git", {
    args,
    cwd,
    stdout: "piped",
    stderr: "piped",
  });
  
  const { code, stdout, stderr } = await command.output();
  
  if (code !== 0) {
    const errorText = new TextDecoder().decode(stderr);
    throw new Error(`Git command failed: ${errorText}`);
  }
  
  return new TextDecoder().decode(stdout).trim();
}

// Tool handlers
export const gitHandlers = {
  git_status: async (args: z.infer<typeof GitStatusInputSchema>) => {
    const { path = Deno.cwd() } = args;
    
    try {
      // Get current branch
      const branch = await runGitCommand(["branch", "--show-current"], path);
      
      // Get status
      const statusOutput = await runGitCommand(["status", "--porcelain", "-b"], path);
      const lines = statusOutput.split("\n");
      
      let ahead = 0;
      let behind = 0;
      const staged: string[] = [];
      const modified: string[] = [];
      const untracked: string[] = [];
      
      for (const line of lines) {
        if (line.startsWith("##")) {
          // Parse ahead/behind from branch line
          const match = line.match(/\[ahead (\d+), behind (\d+)\]|\[ahead (\d+)\]|\[behind (\d+)\]/);
          if (match) {
            ahead = parseInt(match[1] || match[3] || "0");
            behind = parseInt(match[2] || match[4] || "0");
          }
        } else if (line.length > 0) {
          const status = line.substring(0, 2);
          const file = line.substring(3);
          
          if (status[0] !== " " && status[0] !== "?") {
            staged.push(file);
          }
          if (status[1] !== " ") {
            if (status[1] === "?") {
              untracked.push(file);
            } else {
              modified.push(file);
            }
          }
        }
      }
      
      return {
        branch,
        ahead,
        behind,
        staged,
        modified,
        untracked,
        clean: staged.length === 0 && modified.length === 0 && untracked.length === 0,
      };
    } catch (error) {
      throw new Error(`Failed to get git status: ${error instanceof Error ? error.message : String(error)}`);
    }
  },

  git_log: async (args: z.infer<typeof GitLogInputSchema>) => {
    const { path = Deno.cwd(), limit = 10, oneline = false } = args;
    
    try {
      const format = oneline ? "--oneline" : "--pretty=format:%H|%s|%an|%ad";
      const logOutput = await runGitCommand([
        "log",
        format,
        "--date=iso",
        `-${limit}`,
      ], path);
      
      const commits = [];
      
      if (logOutput) {
        for (const line of logOutput.split("\n")) {
          if (oneline) {
            const [hash, ...messageParts] = line.split(" ");
            commits.push({
              hash: hash || "",
              message: messageParts.join(" "),
              author: "",
              date: "",
            });
          } else {
            const [hash, message, author, date] = line.split("|");
            commits.push({
              hash: hash || "",
              message: message || "",
              author: author || "",
              date: date || "",
            });
          }
        }
      }
      
      return {
        commits,
        total: commits.length,
      };
    } catch (error) {
      throw new Error(`Failed to get git log: ${error instanceof Error ? error.message : String(error)}`);
    }
  },

  git_commit: async (args: z.infer<typeof GitCommitInputSchema>) => {
    const { path = Deno.cwd(), message, files } = args;
    
    try {
      // Add files if specified
      if (files && files.length > 0) {
        await runGitCommand(["add", ...files], path);
      }
      
      // Create commit
      await runGitCommand(["commit", "-m", message], path);
      
      // Get the commit hash
      const hash = await runGitCommand(["rev-parse", "HEAD"], path);
      
      // Get number of files committed
      const diffOutput = await runGitCommand(["diff", "--name-only", "HEAD~1", "HEAD"], path);
      const filesCommitted = diffOutput ? diffOutput.split("\n").length : 0;
      
      return {
        success: true,
        hash,
        message,
        files_committed: filesCommitted,
      };
    } catch (error) {
      throw new Error(`Failed to create git commit: ${error instanceof Error ? error.message : String(error)}`);
    }
  },

  git_branches: async (args: z.infer<typeof GitBranchInputSchema>) => {
    const { path = Deno.cwd(), list_all = false } = args;
    
    try {
      const branchArgs = list_all ? ["branch", "-a"] : ["branch"];
      const branchOutput = await runGitCommand(branchArgs, path);
      
      const branches = [];
      let currentBranch = "";
      
      for (const line of branchOutput.split("\n")) {
        if (line.trim()) {
          const isCurrent = line.startsWith("*");
          const isRemote = line.includes("remotes/");
          let name = line.replace(/^\*?\s+/, "").replace(/^remotes\//, "");
          
          if (isCurrent) {
            currentBranch = name;
          }
          
          branches.push({
            name,
            current: isCurrent,
            remote: isRemote,
          });
        }
      }
      
      return {
        current_branch: currentBranch,
        branches,
      };
    } catch (error) {
      throw new Error(`Failed to get git branches: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
};