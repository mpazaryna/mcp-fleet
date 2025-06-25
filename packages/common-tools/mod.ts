/**
 * @packages/common-tools - Shared MCP tools
 * 
 * Provides reusable MCP tools for file operations, project discovery,
 * and git operations that can be used across multiple MCP servers.
 */

export {
  fileTools,
  fileHandlers,
  ReadFileInputSchema,
  ReadFileOutputSchema,
  WriteFileInputSchema,
  WriteFileOutputSchema,
  ListDirectoryInputSchema,
  ListDirectoryOutputSchema,
  FileExistsInputSchema,
  FileExistsOutputSchema,
} from "./file-tools.ts";

export {
  projectTools,
  projectHandlers,
  FindProjectsInputSchema,
  FindProjectsOutputSchema,
  GetProjectInfoInputSchema,
  GetProjectInfoOutputSchema,
  CreateProjectInputSchema,
  CreateProjectOutputSchema,
} from "./project-tools.ts";

export {
  gitTools,
  gitHandlers,
  GitStatusInputSchema,
  GitStatusOutputSchema,
  GitLogInputSchema,
  GitLogOutputSchema,
  GitCommitInputSchema,
  GitCommitOutputSchema,
  GitBranchInputSchema,
  GitBranchOutputSchema,
} from "./git-tools.ts";

// Combined exports for convenience
export const allTools = [
  ...fileTools,
  ...projectTools,
  ...gitTools,
];

export const allHandlers = {
  ...fileHandlers,
  ...projectHandlers,
  ...gitHandlers,
};