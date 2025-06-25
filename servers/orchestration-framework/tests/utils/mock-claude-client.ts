import { ClaudeMessage } from "../../src/claude-client.ts";

/**
 * Mock ClaudeClient for testing without making actual API calls
 */
export class MockClaudeClient {
  private responses: string[] = [];
  private responseIndex = 0;
  private callLog: Array<{ messages: ClaudeMessage[], systemPrompt?: string }> = [];

  constructor(mockResponses: string[] = []) {
    this.responses = mockResponses;
  }

  addResponse(response: string): void {
    this.responses.push(response);
  }

  addResponses(responses: string[]): void {
    this.responses.push(...responses);
  }

  async chat(messages: ClaudeMessage[], systemPrompt?: string): Promise<string> {
    // Log the call for test assertions
    this.callLog.push({ messages: [...messages], systemPrompt });

    if (this.responseIndex >= this.responses.length) {
      throw new Error(`MockClaudeClient: No more responses available. Called ${this.responseIndex + 1} times but only ${this.responses.length} responses configured.`);
    }

    const response = this.responses[this.responseIndex];
    this.responseIndex++;
    
    // Simulate some async delay
    await new Promise(resolve => setTimeout(resolve, 10));
    
    return response;
  }

  getCallLog(): Array<{ messages: ClaudeMessage[], systemPrompt?: string }> {
    return [...this.callLog];
  }

  getCallCount(): number {
    return this.callLog.length;
  }

  getLastCall(): { messages: ClaudeMessage[], systemPrompt?: string } | undefined {
    return this.callLog[this.callLog.length - 1];
  }

  reset(): void {
    this.responses = [];
    this.responseIndex = 0;
    this.callLog = [];
  }
}

/**
 * Predefined conversation flows for common test scenarios
 */
export class ConversationFlows {
  static explorationFlow(): string[] {
    return [
      "I'll help you explore this systematically. Let's start by understanding the core problem you're trying to solve. What initially prompted this project?",
      "That's interesting. Let me dig deeper into the underlying challenges. What assumptions are you making about this solution that we should examine?",
      "Good point. Let's consider the constraints and edge cases. What could go wrong with this approach, and what real-world factors might complicate implementation?",
      "Based on our exploration, I can see several key insights emerging. Would you like to continue exploring other aspects, or do you feel ready to move to the specification phase?"
    ];
  }

  static specificationFlow(): string[] {
    return [
      `Based on our exploration, I'll create the initial specification documents:

## Requirements Specification
1. Core functionality requirements
2. Performance and scalability needs  
3. Integration constraints
4. User experience requirements

## Acceptance Criteria
- Functional requirements must be met
- Performance benchmarks achieved
- Integration tests pass
- User acceptance criteria satisfied

This provides a structured foundation for implementation.`,
      "I've outlined the key specifications. Would you like me to elaborate on any particular section or add additional requirements?",
      "Perfect. The specifications are now complete and ready for the execution phase."
    ];
  }

  static quickExploration(): string[] {
    return [
      "Let's quickly explore the key aspects of this project. What's the main challenge you're trying to address?",
      "I see. Based on this brief exploration, we have enough context to move forward. Ready to create specifications?"
    ];
  }
}