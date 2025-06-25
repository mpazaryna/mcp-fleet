import type { ClaudeMessage, StreamHandler } from "./types.ts";

export class StreamingClient {
  private apiKey: string;
  private baseUrl = "https://api.anthropic.com/v1/messages";

  constructor(apiKey?: string) {
    this.apiKey = apiKey || Deno.env.get("ANTHROPIC_API_KEY") || "";
    if (!this.apiKey) {
      throw new Error("ANTHROPIC_API_KEY required for streaming");
    }
  }

  async streamChat(
    messages: ClaudeMessage[],
    systemPrompt: string | undefined,
    onChunk: StreamHandler,
    model = "claude-3-5-sonnet-20241022",
    maxTokens = 4096
  ): Promise<string> {
    const response = await fetch(this.baseUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": this.apiKey,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "messages-2023-12-15"
      },
      body: JSON.stringify({
        model,
        max_tokens: maxTokens,
        system: systemPrompt,
        messages,
        stream: true
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Streaming error (${response.status}): ${errorText}`);
    }

    if (!response.body) {
      throw new Error("Response body is null");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullText = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") continue;

            try {
              const parsed = JSON.parse(data);
              
              if (parsed.type === "content_block_delta" && parsed.delta?.text) {
                const text = parsed.delta.text;
                fullText += text;
                await onChunk(text);
              }
            } catch (e) {
              // Skip invalid JSON lines
              continue;
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    return fullText;
  }
}