import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";

export interface Task {
  completed: boolean;
  text: string;
}

export interface TasksData {
  explorationTasks: Task[];
  currentPhase: string;
}

export interface ProjectMetadata {
  name: string;
  created: string;
  currentPhase: string;
  status: string;
  sessionCount: number;
  lastSessionDate?: string;
  explorationCompletedDate?: string;
  explorationCompletionReason?: string;
  [key: string]: any;
}

export class ProjectManager {
  constructor(private projectPath: string) {}
  
  async parseTasksFile(): Promise<TasksData> {
    const tasksPath = join(this.projectPath, "tasks.md");
    
    if (!await exists(tasksPath)) {
      throw new Error("tasks.md not found");
    }
    
    const content = await Deno.readTextFile(tasksPath);
    const lines = content.split('\n');
    
    const explorationTasks: Task[] = [];
    let inExplorationPhase = false;
    const currentPhase = "exploration"; // TODO: Detect from content
    
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
    
    return { explorationTasks, currentPhase };
  }
  
  async updateTasksFile(explorationTasks: Task[], projectName: string): Promise<void> {
    const tasksContent = `# ${projectName} - Project Tasks

## Phase 1: Exploration
${explorationTasks.map(task => `- [${task.completed ? 'x' : ' '}] ${task.text}`).join('\n')}

## Phase 2: Specification
*Tasks will be generated after exploration completion*

## Phase 3: Execution
*Tasks will be generated after specification completion*

## Phase 4: Feedback & Learning
*Tasks will be generated after execution completion*
`;
    
    await Deno.writeTextFile(join(this.projectPath, "tasks.md"), tasksContent);
  }
  
  async createInitialTasks(projectName: string): Promise<void> {
    const initialTasks: Task[] = [
      { completed: false, text: "Complete initial problem exploration" }
    ];
    
    await this.updateTasksFile(initialTasks, projectName);
  }
  
  async loadMetadata(): Promise<ProjectMetadata | null> {
    const metadataPath = join(this.projectPath, ".compass.json");
    
    if (!await exists(metadataPath)) {
      return null;
    }
    
    const content = await Deno.readTextFile(metadataPath);
    return JSON.parse(content);
  }
  
  async saveMetadata(metadata: ProjectMetadata): Promise<void> {
    const metadataPath = join(this.projectPath, ".compass.json");
    await Deno.writeTextFile(metadataPath, JSON.stringify(metadata, null, 2));
  }
  
  async createProjectStructure(projectName: string): Promise<void> {
    // Create directories
    const dirs = ["exploration", "specification", "execution", "feedback"];
    for (const dir of dirs) {
      await Deno.mkdir(join(this.projectPath, dir), { recursive: true });
    }
    
    // Create initial metadata
    const metadata: ProjectMetadata = {
      name: projectName,
      created: new Date().toISOString(),
      currentPhase: "exploration",
      status: "active",
      sessionCount: 0,
    };
    
    await this.saveMetadata(metadata);
    
    // Create initial tasks
    await this.createInitialTasks(projectName);
  }
  
  getCurrentStatus(explorationTasks: Task[]): string {
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
}