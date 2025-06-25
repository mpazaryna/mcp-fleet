import type { ClaudeMessage } from "./types.ts";

export class ConversationManager {
  private messages: ClaudeMessage[] = [];
  private maxMessages: number;

  constructor(maxMessages: number = 50) {
    this.maxMessages = maxMessages;
  }

  addMessage(role: "user" | "assistant", content: string): void {
    this.messages.push({ role, content });
    
    // Trim old messages if exceeding limit
    if (this.messages.length > this.maxMessages) {
      // Keep system context by removing from middle
      const toRemove = this.messages.length - this.maxMessages;
      this.messages.splice(1, toRemove);
    }
  }

  addUserMessage(content: string): void {
    this.addMessage("user", content);
  }

  addAssistantMessage(content: string): void {
    this.addMessage("assistant", content);
  }

  getMessages(): ClaudeMessage[] {
    return [...this.messages];
  }

  getMessageCount(): number {
    return this.messages.length;
  }

  clear(): void {
    this.messages = [];
  }

  getConversationText(): string {
    return this.messages
      .map(msg => `${msg.role.toUpperCase()}: ${msg.content}`)
      .join("\n\n");
  }

  summarize(maxLength: number = 1000): string {
    const text = this.getConversationText();
    if (text.length <= maxLength) {
      return text;
    }
    
    // Get start and end of conversation
    const halfLength = Math.floor(maxLength / 2);
    const start = text.substring(0, halfLength);
    const end = text.substring(text.length - halfLength);
    
    return `${start}\n\n[... conversation truncated ...]\n\n${end}`;
  }

  exportToMarkdown(): string {
    let markdown = "# Conversation History\n\n";
    
    for (const msg of this.messages) {
      if (msg.role === "user") {
        markdown += `## User\n\n${msg.content}\n\n`;
      } else {
        markdown += `## Assistant\n\n${msg.content}\n\n`;
      }
    }
    
    return markdown;
  }

  importFromMarkdown(markdown: string): void {
    this.clear();
    
    // Simple markdown parser for conversation format
    const sections = markdown.split(/^##\s+(User|Assistant)/m);
    
    for (let i = 1; i < sections.length; i += 2) {
      const role = sections[i].toLowerCase() as "user" | "assistant";
      const content = sections[i + 1]?.trim();
      
      if (content) {
        this.addMessage(role, content);
      }
    }
  }
}