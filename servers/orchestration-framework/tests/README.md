# Orchestration Framework Test Suite

This directory contains comprehensive tests for the Orchestration Framework using Deno's built-in testing framework.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
├── integration/             # Integration tests for workflows  
├── e2e/                     # End-to-end tests for complete user flows
├── utils/                   # Test utilities and mocks
└── fixtures/                # Test data and sample projects
```

## Running Tests

```bash
# Run all tests
deno task test

# Run specific test categories
deno task test:unit
deno task test:integration  
deno task test:e2e

# Run tests in watch mode
deno task test:watch

# Run specific test file
deno test tests/unit/project-manager.test.ts --allow-read --allow-write
```

## Test Categories

### Unit Tests (`tests/unit/`)
Test individual components in isolation:
- **ProjectManager**: Task parsing, metadata management, conversation loading
- **ClaudeClient**: API communication (mocked)
- **Templates**: Content generation
- **Logger**: Logging functionality

### Integration Tests (`tests/integration/`)
Test component interactions and workflows:
- **Project Initialization**: Full project setup workflow
- **File Operations**: Reading/writing project files
- **Task Management**: Updating and tracking task completion

### End-to-End Tests (`tests/e2e/`)
Test complete user workflows:
- **Exploration Sessions**: Complete exploration flow with simulated user input
- **Specification Generation**: Moving from exploration to specification
- **Multi-Session Workflows**: Testing session continuity and context

## Test Utilities

### MockClaudeClient
Simulates Claude API responses without making actual API calls:
```typescript
import { MockClaudeClient, ConversationFlows } from "../utils/mock-claude-client.ts";

const mockClaude = new MockClaudeClient(ConversationFlows.explorationFlow());
```

### TestHelpers
Provides utilities for test setup and cleanup:
```typescript
import { setupTestProject, TestHelpers } from "../utils/test-helpers.ts";

const testProject = await setupTestProject("my-test-project");
// ... run tests
await testProject.cleanup();
```

## Testing Strategy

### 1. **Isolation**: Each test runs in a temporary directory to avoid conflicts
### 2. **Mocking**: External dependencies (Claude API, file system) are mocked appropriately  
### 3. **Realistic Data**: Tests use realistic project structures and conversation flows
### 4. **Coverage**: Tests cover happy paths, edge cases, and error conditions

## Key Test Scenarios

### Project Lifecycle Testing
1. **Initialization**: `deno task init "Project Name"`
2. **Exploration**: Multiple sessions with task completion
3. **Specification**: Converting exploration insights to specs
4. **State Management**: Session continuity and metadata updates

### Conversation Flow Testing
- Single exploration session completion
- Multi-session workflows with context preservation
- Dynamic task addition during exploration
- Transition management between phases

### Error Handling Testing
- Missing project files
- Corrupted metadata
- API failures (simulated)
- File system permission issues

## Contributing to Tests

When adding new features, please add corresponding tests:

1. **Unit tests** for new functions/classes
2. **Integration tests** for new workflows
3. **E2E tests** for new user-facing features

Follow the existing patterns for test organization and use the provided utilities for consistency.