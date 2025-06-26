import { z } from "zod";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import type { MCPTool } from "@packages/mcp-core/mod.ts";
import { ProjectManager } from "../managers/project-manager.ts";

// Temporary local implementations
async function writeFile(args: { path: string; content: string }) {
  const dir = args.path.substring(0, args.path.lastIndexOf("/"));
  await Deno.mkdir(dir, { recursive: true });
  await Deno.writeTextFile(args.path, args.content);
}

async function readFile(path: string): Promise<string> {
  return await Deno.readTextFile(path);
}

// Schema definitions
const StartExplorationInputSchema = z.object({
  project_name: z.string().describe("Project name"),
  focus_area: z.string().optional().describe("Specific area to explore"),
  projectsDir: z.string().optional().describe("Projects directory (for testing)"),
});

const StartExplorationOutputSchema = z.object({
  project_name: z.string(),
  session_number: z.number(),
  focus_task: z.string(),
  previous_context: z.string(),
  ready_for_conversation: z.boolean(),
  guidance: z.string(),
});

const SaveExplorationSessionInputSchema = z.object({
  project_name: z.string().describe("Project name"),
  conversation_content: z.string().describe("The exploration conversation content"),
  session_summary: z.string().optional().describe("Optional summary of the session"),
  projectsDir: z.string().optional().describe("Projects directory (for testing)"),
});

const SaveExplorationSessionOutputSchema = z.object({
  project_name: z.string(),
  session_number: z.number(),
  file_path: z.string(),
  conversation_saved: z.boolean(),
  message: z.string(),
  next_steps: z.array(z.string()),
});

const GetProjectContextInputSchema = z.object({
  project_name: z.string().describe("Project name"),
  projectsDir: z.string().optional().describe("Projects directory (for testing)"),
});

const GetProjectContextOutputSchema = z.object({
  project_name: z.string(),
  conversation_history: z.array(z.object({
    session_number: z.number(),
    file_name: z.string(),
    content: z.string(),
    summary: z.string(),
  })),
  total_sessions: z.number(),
  key_insights: z.array(z.string()),
  current_context: z.string(),
});

const CompleteExplorationPhaseInputSchema = z.object({
  project_name: z.string().describe("Project name"),
  completion_reason: z.string().optional().describe("Reason for completion"),
  projectsDir: z.string().optional().describe("Projects directory (for testing)"),
});

const CompleteExplorationPhaseOutputSchema = z.object({
  project_name: z.string(),
  exploration_completed: z.boolean(),
  remaining_tasks_count: z.number(),
  completion_reason: z.string().optional(),
  message: z.string(),
  next_steps: z.array(z.string()),
});

// Tool definitions
export const explorationTools: MCPTool[] = [
  {
    name: "start_exploration",
    description: "Begin or continue systematic exploration phase for a project",
    inputSchema: StartExplorationInputSchema,
    outputSchema: StartExplorationOutputSchema,
  },
  {
    name: "save_exploration_session",
    description: "Save exploration conversation content to project files",
    inputSchema: SaveExplorationSessionInputSchema,
    outputSchema: SaveExplorationSessionOutputSchema,
  },
  {
    name: "get_project_context",
    description: "Load full conversation history and context for a project",
    inputSchema: GetProjectContextInputSchema,
    outputSchema: GetProjectContextOutputSchema,
  },
  {
    name: "complete_exploration_phase",
    description: "Mark exploration phase as complete to enable specification",
    inputSchema: CompleteExplorationPhaseInputSchema,
    outputSchema: CompleteExplorationPhaseOutputSchema,
  },
];

// Helper functions
async function getProjectsDirectory(customDir?: string): Promise<string> {
  if (customDir) return customDir;
  
  // Check if running in Docker container with COMPASS_WORKSPACE env var
  const dockerWorkspace = Deno.env.get("COMPASS_WORKSPACE");
  if (dockerWorkspace) {
    await Deno.mkdir(dockerWorkspace, { recursive: true });
    return dockerWorkspace;
  }
  
  // Fall back to home directory for native installations
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
  if (!homeDir) {
    throw new Error("Unable to determine user home directory");
  }
  
  const projectsDir = join(homeDir, "CompassProjects");
  await Deno.mkdir(projectsDir, { recursive: true });
  return projectsDir;
}

async function loadPreviousConversations(projectPath: string, sessionNum: number): Promise<string> {
  const previousSessions: string[] = [];
  
  for (let i = 1; i < sessionNum; i++) {
    const sessionFile = join(projectPath, "exploration", `conversation-${i}.md`);
    if (await exists(sessionFile)) {
      try {
        const content = await readFile(sessionFile);
        // Extract key content
        const cleanContent = content
          .replace(/^# .+$/gm, '') // Remove headers
          .replace(/^\*\*.+\*\*:?\s*/gm, '') // Remove bold labels
          .trim();
        
        if (cleanContent) {
          previousSessions.push(`SESSION ${i} INSIGHTS:\n${cleanContent}`);
        }
      } catch {
        // Skip if can't read
      }
    }
  }
  
  if (previousSessions.length === 0) {
    return "No previous sessions.";
  }
  
  return `PREVIOUS EXPLORATION CONTEXT:\n\n${previousSessions.join('\n\n---\n\n')}`;
}

// Tool handlers
export const explorationHandlers = {
  start_exploration: async (args: z.infer<typeof StartExplorationInputSchema>) => {
    const { project_name, focus_area, projectsDir: customDir } = args;
    
    try {
      const projectsDir = await getProjectsDirectory(customDir);
      const projectPath = join(projectsDir, project_name);
      
      if (!await exists(projectPath)) {
        throw new Error(`Project '${project_name}' not found`);
      }
      
      const metadataPath = join(projectPath, ".compass.json");
      const metadata = JSON.parse(await readFile(metadataPath));
      
      // Load tasks from tasks.md
      const tasksPath = join(projectPath, "tasks.md");
      const tasksContent = await readFile(tasksPath);
      
      // Simple task parsing
      const taskLines = tasksContent.split('\n').filter(line => line.includes('- [ ]') || line.includes('- [x]'));
      const incompleteTasks = taskLines.filter(line => line.includes('- [ ]'));
      const nextTask = incompleteTasks.length > 0 
        ? incompleteTasks[0].replace('- [ ]', '').trim()
        : "All exploration tasks complete";
      
      const nextSessionNum = (metadata.sessionCount || 0) + 1;
      const previousContext = await loadPreviousConversations(projectPath, nextSessionNum);
      
      return {
        project_name,
        session_number: nextSessionNum,
        focus_task: focus_area || nextTask,
        previous_context: previousContext,
        ready_for_conversation: incompleteTasks.length > 0,
        guidance: nextSessionNum > 1 
          ? `Building on ${nextSessionNum - 1} previous session(s). Focus on: ${focus_area || nextTask}`
          : `First exploration session. Focus on: ${focus_area || nextTask}`,
      };
    } catch (error) {
      throw error;
    }
  },
  
  save_exploration_session: async (args: z.infer<typeof SaveExplorationSessionInputSchema>) => {
    const { project_name, conversation_content, session_summary, projectsDir: customDir } = args;
    
    try {
      const projectsDir = await getProjectsDirectory(customDir);
      const projectPath = join(projectsDir, project_name);
      
      if (!await exists(projectPath)) {
        throw new Error(`Project '${project_name}' not found`);
      }
      
      const metadataPath = join(projectPath, ".compass.json");
      const metadata = JSON.parse(await readFile(metadataPath));
      
      const nextSessionNum = (metadata.sessionCount || 0) + 1;
      const timestamp = new Date().toISOString();
      
      // Create conversation file
      const conversationFileName = `conversation-${nextSessionNum}.md`;
      const conversationPath = join(projectPath, "exploration", conversationFileName);
      
      const formattedContent = `# Exploration Session ${nextSessionNum}
**Project:** ${project_name}
**Date:** ${timestamp}
**Session:** ${nextSessionNum}
${session_summary ? `**Summary:** ${session_summary}` : ''}

---

${conversation_content}

---

**Session completed:** ${timestamp}
`;
      
      await writeFile({
        path: conversationPath,
        content: formattedContent,
      });
      
      // Update metadata
      const updatedMetadata = {
        ...metadata,
        sessionCount: nextSessionNum,
        lastSessionDate: timestamp,
      };
      
      await writeFile({
        path: metadataPath,
        content: JSON.stringify(updatedMetadata, null, 2),
      });
      
      return {
        project_name,
        session_number: nextSessionNum,
        file_path: `exploration/${conversationFileName}`,
        conversation_saved: true,
        message: `Exploration session ${nextSessionNum} saved successfully`,
        next_steps: [
          "Conversation captured in exploration files",
          "Session count updated in project metadata",
          "Content available for future specification generation",
        ],
      };
    } catch (error) {
      throw error;
    }
  },
  
  get_project_context: async (args: z.infer<typeof GetProjectContextInputSchema>) => {
    const { project_name, projectsDir: customDir } = args;
    
    try {
      const projectsDir = await getProjectsDirectory(customDir);
      const projectPath = join(projectsDir, project_name);
      
      if (!await exists(projectPath)) {
        throw new Error(`Project '${project_name}' not found`);
      }
      
      const metadata = JSON.parse(await readFile(join(projectPath, ".compass.json")));
      const conversationHistory = [];
      const keyInsights: string[] = [];
      const explorationDir = join(projectPath, "exploration");
      
      if (await exists(explorationDir)) {
        for await (const entry of Deno.readDir(explorationDir)) {
          if (entry.name.startsWith("conversation-") && entry.name.endsWith(".md")) {
            const sessionNumber = parseInt(entry.name.match(/conversation-(\d+)\.md/)?.[1] || "0");
            const content = await readFile(join(explorationDir, entry.name));
            
            conversationHistory.push({
              session_number: sessionNumber,
              file_name: entry.name,
              content: content.substring(0, 500) + (content.length > 500 ? "..." : ""),
              summary: `Session ${sessionNumber} exploration`,
            });
          }
        }
      }
      
      // Sort by session number
      conversationHistory.sort((a, b) => a.session_number - b.session_number);
      
      const nextSessionNum = (metadata.sessionCount || 0) + 1;
      const currentContext = await loadPreviousConversations(projectPath, nextSessionNum);
      
      return {
        project_name,
        conversation_history: conversationHistory,
        total_sessions: metadata.sessionCount || 0,
        key_insights: keyInsights,
        current_context: currentContext,
      };
    } catch (error) {
      throw error;
    }
  },
  
  complete_exploration_phase: async (args: z.infer<typeof CompleteExplorationPhaseInputSchema>) => {
    const { project_name, completion_reason, projectsDir: customDir } = args;
    
    try {
      const projectsDir = await getProjectsDirectory(customDir);
      const projectPath = join(projectsDir, project_name);
      
      if (!await exists(projectPath)) {
        throw new Error(`Project '${project_name}' not found`);
      }
      
      const metadataPath = join(projectPath, ".compass.json");
      const metadata = JSON.parse(await readFile(metadataPath));
      
      // Update metadata
      const updatedMetadata = {
        ...metadata,
        currentPhase: "specification",
        explorationCompletedDate: new Date().toISOString(),
        explorationCompletionReason: completion_reason || "User determined exploration sufficient",
      };
      
      await writeFile({
        path: metadataPath,
        content: JSON.stringify(updatedMetadata, null, 2),
      });
      
      // Create completion record if reason provided
      if (completion_reason) {
        const completionRecord = `# Exploration Phase Completion
**Project:** ${project_name}
**Completed:** ${new Date().toISOString()}
**Reason:** ${completion_reason}

The user determined that sufficient exploration has been conducted to proceed to specification generation.
`;
        
        await writeFile({
          path: join(projectPath, "exploration", "completion-override.md"),
          content: completionRecord,
        });
      }
      
      return {
        project_name,
        exploration_completed: true,
        remaining_tasks_count: 0, // TODO: Actually count remaining tasks
        completion_reason,
        message: "Exploration phase marked complete",
        next_steps: [
          "Exploration phase completed",
          "Ready to generate specification",
          "Use generate_specification to create specs",
        ],
      };
    } catch (error) {
      throw error;
    }
  },
};