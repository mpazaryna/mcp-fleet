import { exists } from "@std/fs";
import { Task, ProjectMetadata } from "./types.ts";
import { logger } from "./logger.ts";

export class ProjectManager {
  // Parse tasks.md and return structured task data
  static async parseTasksFile(): Promise<{ explorationTasks: Task[], currentPhase: string }> {
    logger.debug("Parsing tasks.md file");
    
    try {
      const tasksContent = await Deno.readTextFile('tasks.md');
      const lines = tasksContent.split('\n');
      
      const explorationTasks: Task[] = [];
      let inExplorationPhase = false;
      const currentPhase = "exploration";
      
      for (const line of lines) {
        if (line.includes('## Phase 1: Exploration')) {
          inExplorationPhase = true;
          continue;
        }
        if (line.includes('## Phase 2:')) {
          inExplorationPhase = false;
        }
        
        if (inExplorationPhase && (line.includes('- [x]') || line.includes('- [ ]'))) {
          const completed = line.includes('- [x]');
          const text = line.replace(/- \[[x ]\]/, '').trim();
          explorationTasks.push({ completed, text });
        }
      }
      
      logger.debug(`Found ${explorationTasks.length} exploration tasks`);
      return { explorationTasks, currentPhase };
    } catch (error) {
      logger.error("Failed to parse tasks.md", error);
      throw error;
    }
  }

  // Update tasks.md with new or modified tasks
  static async updateTasksFile(explorationTasks: Task[], nextAction: string = "deno task explore"): Promise<void> {
    logger.debug("Updating tasks.md file");
    
    try {
      const metadata = JSON.parse(await Deno.readTextFile('.orchestration.json')) as ProjectMetadata;
      
      const tasksContent = `# ${metadata.name} - Orchestration Framework Tasks

## Phase 1: Exploration ⏳
${explorationTasks.map(task => `- [${task.completed ? 'x' : ' '}] ${task.text}`).join('\n')}
- **Artifacts**: \`exploration/questions.md\`, \`exploration/conversation-*.md\`, \`exploration/insights.md\`

## Phase 2: Specification 📋
- [ ] Process exploration inputs into insights document
- [ ] Transform insights into structured specifications
- [ ] Generate behavioral scenarios (Given/When/Then)
- [ ] Define system architecture and components
- **Artifacts**: \`specification/insights.md\`, \`specification/requirements.md\`, \`specification/scenarios.gherkin\`

## Phase 3: Execution 🎯
- [ ] Implement solution based on specifications
- [ ] Validate against acceptance criteria
- **Artifacts**: Working solution in \`execution/\`

## Phase 4: Feedback & Learning 🔄
- [ ] Analyze outcomes and lessons learned
- [ ] Update framework knowledge base
- **Artifacts**: \`feedback/lessons.md\`

---
**Current Status**: ${ProjectManager.getCurrentStatus(explorationTasks)}
**Next Action**: \`${nextAction}\`
`;

      await Deno.writeTextFile('tasks.md', tasksContent);
      logger.debug("tasks.md updated successfully");
    } catch (error) {
      logger.error("Failed to update tasks.md", error);
      throw error;
    }
  }

  static getCurrentStatus(explorationTasks: Task[]): string {
    const completed = explorationTasks.filter(t => t.completed).length;
    const total = explorationTasks.length;
    
    if (completed === 0) {
      return "Exploration phase - Ready to begin";
    } else if (completed === total) {
      return "Exploration phase - Complete, ready for specification";
    } else {
      return `Exploration phase - ${completed}/${total} areas explored`;
    }
  }

  static async loadPreviousConversations(sessionNum: number): Promise<string> {
    logger.debug(`Loading previous conversations for session ${sessionNum}`);
    
    const previousSessions: string[] = [];
    
    for (let i = 1; i < sessionNum; i++) {
      const sessionFile = `exploration/conversation-${i}.md`;
      if (await exists(sessionFile)) {
        try {
          const content = await Deno.readTextFile(sessionFile);
          // Extract key insights, skip the markdown headers and format nicely
          const cleanContent = content
            .replace(/^# .+$/gm, '') // Remove headers
            .replace(/^\*\*.+\*\*:?\s*/gm, '') // Remove bold labels
            .replace(/^## .+$/gm, '') // Remove subheaders
            .trim();
          
          if (cleanContent) {
            previousSessions.push(`SESSION ${i} INSIGHTS:\n${cleanContent}`);
          }
        } catch (error) {
          logger.warn(`Failed to read session ${i}`, error);
        }
      }
    }
    
    if (previousSessions.length === 0) {
      return "No previous sessions.";
    }
    
    logger.debug(`Loaded ${previousSessions.length} previous sessions`);
    return `PREVIOUS EXPLORATION CONTEXT:\n\n${previousSessions.join('\n\n---\n\n')}\n\nUse this context to build on previous insights rather than starting from scratch.`;
  }

  static async getProjectMetadata(): Promise<ProjectMetadata | null> {
    try {
      if (!await exists('.orchestration.json')) {
        return null;
      }
      
      const content = await Deno.readTextFile('.orchestration.json');
      return JSON.parse(content) as ProjectMetadata;
    } catch (error) {
      logger.error("Failed to load project metadata", error);
      return null;
    }
  }

  static async updateProjectMetadata(metadata: ProjectMetadata): Promise<void> {
    try {
      await Deno.writeTextFile('.orchestration.json', JSON.stringify(metadata, null, 2));
      logger.debug("Project metadata updated");
    } catch (error) {
      logger.error("Failed to update project metadata", error);
      throw error;
    }
  }
}