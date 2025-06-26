import { createMCPServer } from "@packages/mcp-core/mod.ts";

const serverInfo = {
  name: "compass",
  version: "1.0.0",
  description: "Systematic project methodology through exploration-to-execution phases",
};

export async function createCompassServer() {
  const server = createMCPServer({
    serverInfo,
    tools: [],
    handlers: {},
  });

  return server;
}

export function getServerInfo() {
  return serverInfo;
}