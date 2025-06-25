# @packages/common-tools

Shared MCP tools for file operations, project discovery, and git operations that can be used across multiple MCP servers.

## Features

### File Tools
- `read_file` - Read file contents
- `write_file` - Write file with optional directory creation
- `list_directory` - List directory contents with file types
- `file_exists` - Check if file/directory exists

### Project Tools
- `find_projects` - Discover projects in directory tree
- `get_project_info` - Get detailed project information
- `create_project` - Create new projects from templates

### Git Tools
- `git_status` - Get repository status
- `git_log` - View commit history
- `git_commit` - Create commits
- `git_branches` - List branches

## Usage

### Individual Tool Categories

```typescript
import { fileTools, fileHandlers } from "@packages/common-tools/file-tools.ts";
import { createMCPServer } from "@packages/mcp-core/mod.ts";

const server = createMCPServer({
  serverInfo: { name: "file-server", version: "1.0.0" },
  tools: fileTools,
  handlers: fileHandlers,
});
```

### All Tools Combined

```typescript
import { allTools, allHandlers } from "@packages/common-tools/mod.ts";
import { createMCPServer } from "@packages/mcp-core/mod.ts";

const server = createMCPServer({
  serverInfo: { name: "full-server", version: "1.0.0" },
  tools: allTools,
  handlers: allHandlers,
});
```

### Mixing with Custom Tools

```typescript
import { fileTools, fileHandlers, gitTools, gitHandlers } from "@packages/common-tools/mod.ts";

const myCustomTools = [
  {
    name: "custom_tool",
    description: "My custom tool",
    inputSchema: z.object({ input: z.string() }),
    outputSchema: z.object({ output: z.string() }),
  },
];

const myCustomHandlers = {
  custom_tool: async (args: { input: string }) => {
    return { output: `Processed: ${args.input}` };
  },
};

const server = createMCPServer({
  serverInfo: { name: "mixed-server", version: "1.0.0" },
  tools: [...fileTools, ...gitTools, ...myCustomTools],
  handlers: { ...fileHandlers, ...gitHandlers, ...myCustomHandlers },
});
```

## Project Type Detection

The project tools can detect various project types:

- **Orchestration Framework** - `.orchestration.json`
- **Node.js/npm** - `package.json`
- **Deno** - `deno.json`
- **Rust** - `Cargo.toml`
- **Python** - `pyproject.toml`, `requirements.txt`, `setup.py`
- **Git Repository** - `.git` directory

## API Reference

### File Tools

- `read_file(path)` - Returns `{ content, size, exists }`
- `write_file(path, content, create_dirs?)` - Returns `{ success, path, size }`
- `list_directory(path, include_hidden?)` - Returns `{ entries[], total }`
- `file_exists(path)` - Returns `{ exists, type? }`

### Project Tools

- `find_projects(root_directory?, project_type?)` - Returns `{ projects[], total }`
- `get_project_info(project_path)` - Returns project details and metadata
- `create_project(name, path, template?)` - Creates new project structure

### Git Tools

- `git_status(path?)` - Returns branch, files, ahead/behind counts
- `git_log(path?, limit?, oneline?)` - Returns commit history
- `git_commit(path?, message, files?)` - Creates commit
- `git_branches(path?, list_all?)` - Returns branch information