import { z } from "zod";

export interface MCPServerConfig {
  name: string;
  version: string;
  description?: string;
}

export interface MCPTool<TInput = any, TOutput = any> {
  name: string;
  description: string;
  inputSchema: z.ZodSchema<TInput>;
  outputSchema: z.ZodSchema<TOutput>;
}

export type MCPToolHandler<TInput = any, TOutput = any> = (
  args: TInput
) => Promise<TOutput> | TOutput;

export interface MCPToolHandlers {
  [toolName: string]: MCPToolHandler;
}

export interface MCPServerOptions {
  serverInfo: MCPServerConfig;
  tools: MCPTool[];
  handlers: MCPToolHandlers;
}

export interface MCPTransport {
  connect(): Promise<void>;
  close(): Promise<void>;
}

export interface MCPLogger {
  info(message: string, ...args: any[]): void;
  warn(message: string, ...args: any[]): void;
  error(message: string, ...args: any[]): void;
  debug(message: string, ...args: any[]): void;
}