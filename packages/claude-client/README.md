# @packages/claude-client

Enhanced Anthropic Claude API client with retry logic, rate limiting, conversation management, and streaming support.

## Features

- **Retry Logic**: Automatic retry with exponential backoff for failed requests
- **Rate Limiting**: Handles 429 rate limit responses automatically
- **Conversation Management**: Track and manage conversation history
- **Streaming Support**: Real-time response streaming
- **Multiple Models**: Support for all Claude 3 model variants
- **Error Handling**: Comprehensive error handling and reporting

## Usage

### Basic Chat

```typescript
import { ClaudeClient } from "@packages/claude-client/mod.ts";

const client = new ClaudeClient({
  model: "claude-3-5-sonnet-20241022",
  maxRetries: 3,
});

const response = await client.chat([
  { role: "user", content: "Hello, Claude!" }
], "You are a helpful assistant.");

console.log(response);
```

### Conversation Management

```typescript
import { ConversationManager } from "@packages/claude-client/mod.ts";

const conversation = new ConversationManager();

conversation.addUserMessage("What is the capital of France?");
conversation.addAssistantMessage("The capital of France is Paris.");
conversation.addUserMessage("What about Germany?");

// Get all messages for API call
const messages = conversation.getMessages();

// Export conversation
const markdown = conversation.exportToMarkdown();
```

### Streaming Chat

```typescript
import { StreamingClient } from "@packages/claude-client/mod.ts";

const streamingClient = new StreamingClient();

const fullResponse = await streamingClient.streamChat(
  [{ role: "user", content: "Tell me a story" }],
  "You are a creative storyteller.",
  (chunk) => {
    process.stdout.write(chunk); // Stream chunks as they arrive
  }
);

console.log("\n\nFull response:", fullResponse);
```

## Configuration

```typescript
const client = new ClaudeClient({
  apiKey: "your-api-key", // Optional, defaults to ANTHROPIC_API_KEY env var
  baseUrl: "https://api.anthropic.com/v1/messages", // Optional
  model: "claude-3-5-sonnet-20241022", // Optional
  maxRetries: 3, // Optional, default: 3
  retryDelay: 1000, // Optional, default: 1000ms
});
```

## Available Models

- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`
- `claude-3-5-sonnet-20241022`
- `claude-3-5-haiku-20241022`

## API Reference

### ClaudeClient

- `chat(messages, systemPrompt?, maxTokens?)` - Simple chat completion
- `chatWithResponse(messages, systemPrompt?, maxTokens?)` - Chat with full response details
- `updateModel(model)` - Change the model
- `getModel()` - Get current model

### ConversationManager

- `addMessage(role, content)` - Add a message to conversation
- `addUserMessage(content)` - Add user message
- `addAssistantMessage(content)` - Add assistant message
- `getMessages()` - Get all messages
- `clear()` - Clear conversation
- `exportToMarkdown()` - Export as markdown
- `importFromMarkdown(markdown)` - Import from markdown

### StreamingClient

- `streamChat(messages, systemPrompt, onChunk, model?, maxTokens?)` - Stream chat responses