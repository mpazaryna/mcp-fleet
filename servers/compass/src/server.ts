import { createMCPServer } from "@packages/mcp-core/mod.ts";
import { projectTools, projectHandlers } from "./tools/project-tools.ts";
import { explorationTools, explorationHandlers } from "./tools/exploration-tools.ts";

const serverInfo = {
  name: "compass",
  version: "1.0.0",
  description: "Systematic project methodology through exploration-to-execution phases",
};

export async function createCompassServer() {
  // Combine all tools
  const tools = [
    ...projectTools,
    ...explorationTools,
  ];
  
  // Combine all handlers
  const handlers = {
    ...projectHandlers,
    ...explorationHandlers,
  };
  
  const server = createMCPServer({
    serverInfo,
    tools,
    handlers,
  });

  return server;
}

export function getServerInfo() {
  return serverInfo;
}