import { logger } from "./logger.ts";

export interface ClaudeMessage {
  role: "user" | "assistant";
  content: string;
}

export class ClaudeClient {
  private apiKey: string;
  private baseUrl = "https://api.anthropic.com/v1/messages";

  constructor() {
    this.apiKey = Deno.env.get("ANTHROPIC_API_KEY") || "";
    if (!this.apiKey) {
      throw new Error("ANTHROPIC_API_KEY environment variable required");
    }
    logger.debug("ClaudeClient initialized");
  }

  async chat(messages: ClaudeMessage[], systemPrompt?: string): Promise<string> {
    logger.debug(`Making API request with ${messages.length} messages`);
    
    try {
      const response = await fetch(this.baseUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": this.apiKey,
          "anthropic-version": "2023-06-01"
        },
        body: JSON.stringify({
          model: "claude-3-sonnet-20240229",
          max_tokens: 600,
          system: systemPrompt,
          messages: messages
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        logger.error(`Claude API error: ${response.status} ${response.statusText}`, errorText);
        throw new Error(`Claude API error: ${response.statusText}`);
      }

      const data = await response.json();
      logger.debug("API request successful");
      return data.content[0].text;
    } catch (error) {
      logger.error("Failed to chat with Claude", error);
      throw error;
    }
  }
}