import type { ClaudeConfig, ClaudeMessage, ClaudeResponse, ClaudeError, ClaudeModel } from "./types.ts";

export class ClaudeClient {
  private apiKey: string;
  private baseUrl: string;
  private model: ClaudeModel;
  private maxRetries: number;
  private retryDelay: number;

  constructor(config: ClaudeConfig = {}) {
    this.apiKey = config.apiKey || Deno.env.get("ANTHROPIC_API_KEY") || "";
    if (!this.apiKey) {
      throw new Error("ANTHROPIC_API_KEY environment variable or apiKey config required");
    }
    
    this.baseUrl = config.baseUrl || "https://api.anthropic.com/v1/messages";
    this.model = config.model || "claude-3-5-sonnet-20241022";
    this.maxRetries = config.maxRetries || 3;
    this.retryDelay = config.retryDelay || 1000;
  }

  async chat(
    messages: ClaudeMessage[], 
    systemPrompt?: string,
    maxTokens: number = 4096
  ): Promise<string> {
    const response = await this.sendRequest(messages, systemPrompt, maxTokens);
    return response.content[0].text;
  }

  async chatWithResponse(
    messages: ClaudeMessage[], 
    systemPrompt?: string,
    maxTokens: number = 4096
  ): Promise<ClaudeResponse> {
    return this.sendRequest(messages, systemPrompt, maxTokens);
  }

  private async sendRequest(
    messages: ClaudeMessage[],
    systemPrompt?: string,
    maxTokens: number = 4096
  ): Promise<ClaudeResponse> {
    let lastError: Error | null = null;
    
    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const response = await fetch(this.baseUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-api-key": this.apiKey,
            "anthropic-version": "2023-06-01"
          },
          body: JSON.stringify({
            model: this.model,
            max_tokens: maxTokens,
            system: systemPrompt,
            messages: messages
          })
        });

        if (!response.ok) {
          const errorData = await response.json() as ClaudeError;
          const errorMessage = errorData.error?.message || response.statusText;
          
          // Check if rate limited
          if (response.status === 429) {
            const retryAfter = response.headers.get("retry-after");
            const delay = retryAfter ? parseInt(retryAfter) * 1000 : this.retryDelay * (attempt + 1);
            
            if (attempt < this.maxRetries - 1) {
              await this.sleep(delay);
              continue;
            }
          }
          
          throw new Error(`Claude API error (${response.status}): ${errorMessage}`);
        }

        return await response.json() as ClaudeResponse;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (attempt < this.maxRetries - 1) {
          await this.sleep(this.retryDelay * (attempt + 1));
          continue;
        }
      }
    }
    
    throw lastError || new Error("Failed to communicate with Claude API");
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  updateModel(model: ClaudeModel): void {
    this.model = model;
  }

  getModel(): ClaudeModel {
    return this.model;
  }
}