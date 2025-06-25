export interface ClaudeMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ClaudeConfig {
  apiKey?: string;
  baseUrl?: string;
  model?: ClaudeModel;
  maxRetries?: number;
  retryDelay?: number;
}

export type ClaudeModel = 
  | "claude-3-opus-20240229"
  | "claude-3-sonnet-20240229"
  | "claude-3-haiku-20240307"
  | "claude-3-5-sonnet-20241022"
  | "claude-3-5-haiku-20241022";

export interface ClaudeResponse {
  id: string;
  type: string;
  role: string;
  content: Array<{
    type: string;
    text: string;
  }>;
  model: string;
  stop_reason: string | null;
  stop_sequence: string | null;
  usage: {
    input_tokens: number;
    output_tokens: number;
  };
}

export interface ClaudeError {
  type: string;
  error: {
    type: string;
    message: string;
  };
}

export type StreamHandler = (chunk: string) => void | Promise<void>;