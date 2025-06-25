import { ensureDir } from "@std/fs";
import { join } from "@std/path";

/**
 * Test utilities for the orchestration framework
 */

export class TestHelpers {
  static async createTempTestDir(): Promise<string> {
    const tempDir = await Deno.makeTempDir({ prefix: "orchestration_test_" });
    return tempDir;
  }

  static async cleanupTestDir(testDir: string): Promise<void> {
    try {
      await Deno.remove(testDir, { recursive: true });
    } catch (error) {
      console.warn(`Failed to cleanup test directory: ${testDir}`, error);
    }
  }

  static async createMockProject(testDir: string, projectName: string): Promise<string> {
    const projectDir = join(testDir, 'projects', projectName);
    await ensureDir(`${projectDir}/exploration`);
    await ensureDir(`${projectDir}/specification`);
    await ensureDir(`${projectDir}/execution`);
    await ensureDir(`${projectDir}/feedback`);

    // Create minimal project metadata
    const metadata = {
      name: projectName,
      created: new Date().toISOString(),
      currentPhase: "exploration",
      status: "initialized",
      sessionCount: 0
    };
    await Deno.writeTextFile(`${projectDir}/.orchestration.json`, JSON.stringify(metadata, null, 2));

    // Create minimal tasks.md
    const tasksContent = `# ${projectName} - Orchestration Framework Tasks

## Phase 1: Exploration ⏳
- [ ] Test exploration task 1
- [ ] Test exploration task 2
- **Artifacts**: \`exploration/questions.md\`, \`exploration/conversation-*.md\`

## Phase 2: Specification 📋
- [ ] Transform insights into structured specifications
- **Artifacts**: \`specification/requirements.md\`

---
**Current Status**: Test project initialized
**Next Action**: \`deno task explore\`
`;
    await Deno.writeTextFile(`${projectDir}/tasks.md`, tasksContent);

    return projectDir;
  }

  static mockPrompt(responses: string[]): void {
    let responseIndex = 0;
    // @ts-ignore - Mock the global prompt function
    globalThis.prompt = (message?: string) => {
      const response = responses[responseIndex] || "";
      responseIndex++;
      return response;
    };
  }

  static restorePrompt(): void {
    // @ts-ignore - Restore original prompt if available
    delete globalThis.prompt;
  }

  static async createMockConversation(projectDir: string, sessionNum: number, content: string): Promise<void> {
    const conversationFile = `${projectDir}/exploration/conversation-${sessionNum}.md`;
    const conversationContent = `# Exploration Session ${sessionNum}: Test Project

**Focus**: Mock exploration session

## Session Start: ${new Date().toISOString()}

${content}
`;
    await Deno.writeTextFile(conversationFile, conversationContent);
  }
}

export interface TestProject {
  name: string;
  dir: string;
  tempDir: string;
  cleanup: () => Promise<void>;
}

export async function setupTestProject(projectName: string = "test-project"): Promise<TestProject> {
  const tempDir = await TestHelpers.createTempTestDir();
  const projectDir = await TestHelpers.createMockProject(tempDir, projectName);
  
  return {
    name: projectName,
    dir: projectDir,
    tempDir,
    cleanup: () => TestHelpers.cleanupTestDir(tempDir)
  };
}