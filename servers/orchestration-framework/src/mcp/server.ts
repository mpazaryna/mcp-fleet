/**
 * Orchestration Framework MCP Server
 * Provides conversational access to systematic project methodology through Claude Desktop
 */

import { createToolsServer } from "@mizchi/mcp-helper";
import { z } from "zod";
import { exists } from "@std/fs";
import { join } from "@std/path";
import { ProjectManager } from "../project-manager.ts";
import { PatternManager } from "../pattern-manager.ts";
import { FlywheelManager } from "../flywheel-manager.ts";
import { logger } from "../logger.ts";

// Zod schemas for type safety and MCP compliance
const InitProjectInputSchema = z.object({
  name: z.string().describe("Name of the project to initialize"),
});

const InitProjectOutputSchema = z.object({
  success: z.boolean(),
  project_name: z.string(),
  project_path: z.string(),
  message: z.string(),
  next_steps: z.array(z.string()),
});

const ListProjectsInputSchema = z.object({});

const ListProjectsOutputSchema = z.object({
  projects: z.array(z.object({
    name: z.string(),
    path: z.string(),
    status: z.string(),
    current_phase: z.string(),
    session_count: z.number(),
    last_session: z.string().optional(),
    tasks_remaining: z.number(),
  })),
  total: z.number(),
});

const GetProjectStatusInputSchema = z.object({
  project_name: z.string().optional().describe("Project name (uses current directory if not specified)"),
});

const GetProjectStatusOutputSchema = z.object({
  project_name: z.string(),
  current_phase: z.string(),
  status_summary: z.string(),
  exploration_tasks: z.array(z.object({
    text: z.string(),
    completed: z.boolean(),
  })),
  session_count: z.number(),
  next_action: z.string(),
  recommendations: z.array(z.string()),
});

const GetProjectContextInputSchema = z.object({
  project_name: z.string().describe("Project name to load context for"),
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

const StartExplorationInputSchema = z.object({
  project_name: z.string().optional().describe("Project name (uses current directory if not specified)"),
  focus_area: z.string().optional().describe("Specific area to explore"),
});

const StartExplorationOutputSchema = z.object({
  project_name: z.string(),
  session_number: z.number(),
  focus_task: z.string(),
  previous_context: z.string(),
  ready_for_conversation: z.boolean(),
  guidance: z.string(),
});

const GenerateSpecificationInputSchema = z.object({
  project_name: z.string().optional().describe("Project name (uses current directory if not specified)"),
  pattern: z.string().optional().describe("Specification pattern to use"),
});

const GenerateSpecificationOutputSchema = z.object({
  project_name: z.string(),
  pattern_used: z.string(),
  specification_content: z.string(),
  file_path: z.string(),
  insights_extracted: z.object({
    user_pain_points: z.string(),
    core_features: z.string(),
    constraints: z.string(),
    goals: z.string(),
  }),
});

const ListPatternsInputSchema = z.object({});

const ListPatternsOutputSchema = z.object({
  patterns: z.array(z.object({
    name: z.string(),
    domain: z.string(),
    description: z.string(),
    variables: z.array(z.string()),
    sections: z.array(z.string()),
  })),
  total: z.number(),
});

const CheckFlywheelInputSchema = z.object({
  project_name: z.string().optional().describe("Project name (uses current directory if not specified)"),
});

const CheckFlywheelOutputSchema = z.object({
  project_name: z.string(),
  gaps_detected: z.array(z.string()),
  recommendations: z.array(z.string()),
  flywheel_recommended: z.boolean(),
  target_phase: z.string().optional(),
  reason: z.string().optional(),
});

const SaveExplorationSessionInputSchema = z.object({
  project_name: z.string().describe("Project name to save exploration session for"),
  conversation_content: z.string().describe("The exploration conversation content to save"),
  session_summary: z.string().optional().describe("Optional summary of the session"),
});

const SaveExplorationSessionOutputSchema = z.object({
  project_name: z.string(),
  session_number: z.number(),
  file_path: z.string(),
  conversation_saved: z.boolean(),
  message: z.string(),
  next_steps: z.array(z.string()),
});

const CompleteExplorationPhaseInputSchema = z.object({
  project_name: z.string().describe("Project name to complete exploration phase for"),
  completion_reason: z.string().optional().describe("Reason why exploration is sufficient (optional)"),
});

const CompleteExplorationPhaseOutputSchema = z.object({
  project_name: z.string(),
  exploration_completed: z.boolean(),
  remaining_tasks_count: z.number(),
  completion_reason: z.string().optional(),
  message: z.string(),
  next_steps: z.array(z.string()),
});

const GetFrameworkLessonInputSchema = z.object({
  lesson_topic: z.string().optional().describe("Lesson topic (methodology-overview, exploration-techniques, etc.) - defaults to methodology-overview"),
  lesson_level: z.string().optional().describe("Lesson level (beginner, intermediate, advanced) - defaults to beginner"),
});

const GetFrameworkLessonOutputSchema = z.object({
  lesson_title: z.string(),
  lesson_content: z.string(),
  lesson_level: z.string(),
  duration: z.string(),
  available_lessons: z.array(z.object({
    name: z.string(),
    title: z.string(),
    level: z.string(),
    description: z.string(),
  })),
  next_recommended: z.string().optional(),
});

const GetManPageInputSchema = z.object({
  section: z.string().optional().describe("Specific section to display (commands, examples, methodology, files) - shows full man page if not specified"),
});

const GetManPageOutputSchema = z.object({
  man_page_content: z.string(),
  section_requested: z.string().optional(),
  available_sections: z.array(z.string()),
  full_page: z.boolean(),
});

const WriteFeedbackInputSchema = z.object({
  project_name: z.string().describe("Project name to write feedback for"),
  feedback_content: z.string().describe("The feedback content to write (shutdown notes, reflections, learnings)"),
  feedback_type: z.string().optional().describe("Type of feedback (shutdown-note, retrospective, reflection, learning) - defaults to reflection"),
  session_reference: z.string().optional().describe("Reference to related session if applicable"),
});

const WriteFeedbackOutputSchema = z.object({
  project_name: z.string(),
  file_path: z.string(),
  feedback_type: z.string(),
  feedback_saved: z.boolean(),
  message: z.string(),
  next_steps: z.array(z.string()),
});

// Server configuration
const serverInfo = {
  name: "orchestration-framework",
  version: "1.0.0",
};

// Tool definitions
const tools = [
  {
    name: "init_project",
    description: "Initialize a new Orchestration Framework project with systematic methodology structure",
    inputSchema: InitProjectInputSchema,
    outputSchema: InitProjectOutputSchema,
  },
  {
    name: "list_projects",
    description: "List all available Orchestration Framework projects with status information",
    inputSchema: ListProjectsInputSchema,
    outputSchema: ListProjectsOutputSchema,
  },
  {
    name: "get_project_status",
    description: "Get detailed status of a specific project including tasks and recommendations",
    inputSchema: GetProjectStatusInputSchema,
    outputSchema: GetProjectStatusOutputSchema,
  },
  {
    name: "get_project_context",
    description: "Load full conversation history and context for a project to enable continuation",
    inputSchema: GetProjectContextInputSchema,
    outputSchema: GetProjectContextOutputSchema,
  },
  {
    name: "start_exploration",
    description: "Begin or continue systematic exploration phase for a project",
    inputSchema: StartExplorationInputSchema,
    outputSchema: StartExplorationOutputSchema,
  },
  {
    name: "generate_specification",
    description: "Generate pattern-based specification from exploration insights",
    inputSchema: GenerateSpecificationInputSchema,
    outputSchema: GenerateSpecificationOutputSchema,
  },
  {
    name: "list_patterns",
    description: "List available specification patterns for different domains",
    inputSchema: ListPatternsInputSchema,
    outputSchema: ListPatternsOutputSchema,
  },
  {
    name: "check_flywheel_opportunities",
    description: "Analyze project for gaps and recommend flywheel iterations",
    inputSchema: CheckFlywheelInputSchema,
    outputSchema: CheckFlywheelOutputSchema,
  },
  {
    name: "save_exploration_session",
    description: "Save exploration conversation content to project files for later specification generation",
    inputSchema: SaveExplorationSessionInputSchema,
    outputSchema: SaveExplorationSessionOutputSchema,
  },
  {
    name: "complete_exploration_phase",
    description: "Mark exploration phase as complete even with remaining tasks, enabling specification generation",
    inputSchema: CompleteExplorationPhaseInputSchema,
    outputSchema: CompleteExplorationPhaseOutputSchema,
  },
  {
    name: "get_framework_lesson",
    description: "Get interactive lesson content about the Orchestration Framework methodology using Feynman teaching method",
    inputSchema: GetFrameworkLessonInputSchema,
    outputSchema: GetFrameworkLessonOutputSchema,
  },
  {
    name: "get_man_page",
    description: "Display comprehensive manual page for the Orchestration Framework MCP server tools and methodology",
    inputSchema: GetManPageInputSchema,
    outputSchema: GetManPageOutputSchema,
  },
  {
    name: "write_feedback",
    description: "Write feedback, shutdown notes, or reflections to the project's feedback folder",
    inputSchema: WriteFeedbackInputSchema,
    outputSchema: WriteFeedbackOutputSchema,
  },
];

// Helper functions
function normalizeProjectName(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-');
}

async function findProjectsDirectory(): Promise<string> {
  // For MCP server, use a dedicated user directory for better reliability
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
  if (!homeDir) {
    throw new Error("Unable to determine user home directory");
  }
  
  const orchestrationDir = join(homeDir, "OrchestrationProjects");
  
  // Ensure the directory exists
  try {
    await Deno.mkdir(orchestrationDir, { recursive: true });
  } catch (error) {
    // Directory might already exist, that's OK
    if (!(error instanceof Deno.errors.AlreadyExists)) {
      logger.warn(`Could not create OrchestrationProjects directory: ${error}`);
    }
  }
  
  return orchestrationDir;
}

async function changeToProjectDirectory(projectName: string): Promise<string> {
  const projectsDir = await findProjectsDirectory();
  const projectPath = join(projectsDir, projectName);
  
  if (!await exists(projectPath)) {
    throw new Error(`Project '${projectName}' not found in ${projectsDir}`);
  }
  
  Deno.chdir(projectPath);
  return projectPath;
}

// Tool handlers
const handlers = {
  init_project: async (args: any) => {
    const { name } = args;
    const normalizedName = normalizeProjectName(name);
    
    logger.info(`Initializing project: ${normalizedName}`);
    
    try {
      // Ensure we're in the right directory
      const projectsDir = await findProjectsDirectory();
      const projectPath = join(projectsDir, normalizedName);
      
      if (await exists(projectPath)) {
        return {
          success: false,
          project_name: normalizedName,
          project_path: projectPath,
          message: `Project '${normalizedName}' already exists`,
          next_steps: [`Project exists at ~/OrchestrationProjects/${normalizedName}`, `Use get_project_status('${normalizedName}') to see current state`],
        };
      }
      
      // Create project structure directly instead of relying on CLI
      // This avoids path and permission issues when running as MCP server
      logger.info(`Creating project structure directly at: ${projectPath}`);
      
      // Create project directory and subdirectories
      await Deno.mkdir(projectPath, { recursive: true });
      await Deno.mkdir(join(projectPath, 'exploration'), { recursive: true });
      await Deno.mkdir(join(projectPath, 'specification'), { recursive: true });
      await Deno.mkdir(join(projectPath, 'execution'), { recursive: true });
      await Deno.mkdir(join(projectPath, 'feedback'), { recursive: true });
      
      // Create project metadata
      const metadata = {
        name: normalizedName,
        created: new Date().toISOString(),
        currentPhase: "exploration",
        status: "active",
        sessionCount: 0,
      };
      
      await Deno.writeTextFile(
        join(projectPath, '.orchestration.json'),
        JSON.stringify(metadata, null, 2)
      );
      
      // Create initial tasks.md file
      const initialTasks = `# ${name} - Project Tasks

## Phase 1: Exploration
- [ ] Complete initial problem exploration

## Phase 2: Specification
*Tasks will be generated after exploration completion*

## Phase 3: Execution
*Tasks will be generated after specification completion*

## Phase 4: Feedback & Learning
*Tasks will be generated after execution completion*
`;
      
      await Deno.writeTextFile(join(projectPath, 'tasks.md'), initialTasks);
      
      // Project created successfully
      const code = 0;
      const stdoutText = `Project '${normalizedName}' initialized successfully`;
      const stderrText = "";
      
      logger.info(`Project created successfully: ${stdoutText}`);
      
      return {
        success: true,
        project_name: normalizedName,
        project_path: projectPath,
        message: `🎼 ORCHESTRATION FRAMEWORK PROJECT INITIALIZED

Project '${normalizedName}' created with systematic 4-phase methodology:
• Phase 1: EXPLORATION (Current) - Understand the problem space  
• Phase 2: SPECIFICATION - Transform insights into structured requirements
• Phase 3: EXECUTION - Implement solutions based on solid understanding
• Phase 4: FEEDBACK & LEARNING - Capture knowledge for future projects

⚠️  METHODOLOGY ENFORCEMENT: You must complete exploration before moving to specification or implementation.`,
        next_steps: [
          "✅ Project structure created with 4-phase methodology",
          "✅ Initial exploration tasks generated", 
          "🎯 NEXT ACTION: Begin systematic exploration phase",
          `📍 Project location: ~/OrchestrationProjects/${normalizedName}`,
          `🔍 Use start_exploration('${normalizedName}') to begin exploring the problem space`,
          `📊 Use get_project_status('${normalizedName}') to see current state`,
        ],
      };
    } catch (error) {
      logger.error("Failed to initialize project", error);
      return {
        success: false,
        project_name: normalizedName,
        project_path: "",
        message: `Failed to initialize project: ${error instanceof Error ? error.message : String(error)}`,
        next_steps: [],
      };
    }
  },

  list_projects: async () => {
    try {
      const projectsDir = await findProjectsDirectory();
      
      if (!await exists(projectsDir)) {
        return {
          projects: [],
          total: 0,
        };
      }
      
      const projects = [];
      
      for await (const entry of Deno.readDir(projectsDir)) {
        if (entry.isDirectory) {
          const projectPath = join(projectsDir, entry.name);
          const metadataPath = join(projectPath, '.orchestration.json');
          
          if (await exists(metadataPath)) {
            try {
              const metadata = JSON.parse(await Deno.readTextFile(metadataPath));
              
              // Get tasks status
              const tasksPath = join(projectPath, 'tasks.md');
              let tasksRemaining = 0;
              
              if (await exists(tasksPath)) {
                const originalCwd = Deno.cwd();
                try {
                  Deno.chdir(projectPath);
                  const { explorationTasks } = await ProjectManager.parseTasksFile();
                  tasksRemaining = explorationTasks.filter(t => !t.completed).length;
                } finally {
                  Deno.chdir(originalCwd);
                }
              }
              
              projects.push({
                name: entry.name,
                path: projectPath,
                status: ProjectManager.getCurrentStatus([]),
                current_phase: metadata.currentPhase || "exploration",
                session_count: metadata.sessionCount || 0,
                last_session: metadata.lastSessionDate,
                tasks_remaining: tasksRemaining,
              });
            } catch (error) {
              logger.warn(`Failed to load project ${entry.name}`, error);
            }
          }
        }
      }
      
      return {
        projects,
        total: projects.length,
      };
    } catch (error) {
      logger.error("Failed to list projects", error);
      return {
        projects: [],
        total: 0,
      };
    }
  },

  get_project_status: async (args: any) => {
    const { project_name } = args;
    
    try {
      let projectPath;
      
      if (project_name) {
        projectPath = await changeToProjectDirectory(project_name);
      } else {
        projectPath = Deno.cwd();
      }
      
      const metadata = await ProjectManager.getProjectMetadata();
      if (!metadata) {
        throw new Error("Not in a valid Orchestration Framework project");
      }
      
      const { explorationTasks, currentPhase } = await ProjectManager.parseTasksFile();
      const incompleteTasks = explorationTasks.filter(t => !t.completed);
      const status = ProjectManager.getCurrentStatus(explorationTasks);
      
      // Generate recommendations
      const recommendations = [];
      if (incompleteTasks.length > 0) {
        recommendations.push(`Continue exploration: ${incompleteTasks[0].text}`);
      } else {
        recommendations.push("Exploration complete - ready for specification phase");
      }
      
      // Check for flywheel opportunities
      const flywheelManager = new FlywheelManager();
      const flywheelRec = await flywheelManager.recommendFlywheelIteration();
      if (flywheelRec.recommended) {
        recommendations.push(`Flywheel iteration recommended: ${flywheelRec.reason}`);
      }
      
      return {
        project_name: metadata.name,
        current_phase: currentPhase,
        status_summary: status,
        exploration_tasks: explorationTasks,
        session_count: metadata.sessionCount || 0,
        next_action: incompleteTasks.length > 0 ? "start_exploration" : "generate_specification",
        recommendations,
      };
    } catch (error) {
      logger.error("Failed to get project status", error);
      throw error;
    }
  },

  get_project_context: async (args: any) => {
    const { project_name } = args;
    
    try {
      const projectPath = await changeToProjectDirectory(project_name);
      const metadata = await ProjectManager.getProjectMetadata();
      
      if (!metadata) {
        throw new Error(`Project '${project_name}' not found or invalid`);
      }
      
      const conversationHistory = [];
      const keyInsights = [];
      const explorationDir = join(projectPath, 'exploration');
      
      if (await exists(explorationDir)) {
        for await (const entry of Deno.readDir(explorationDir)) {
          if (entry.name.startsWith('conversation-') && entry.name.endsWith('.md')) {
            const sessionNumber = parseInt(entry.name.match(/conversation-(\d+)\.md/)?.[1] || '0');
            const content = await Deno.readTextFile(join(explorationDir, entry.name));
            
            // Extract key insights from conversation
            const insights = content.match(/\*\*You\*\*:([^*]+)/g) || [];
            keyInsights.push(...insights.slice(0, 3).map(i => i.replace(/\*\*You\*\*:/, '').trim()));
            
            conversationHistory.push({
              session_number: sessionNumber,
              file_name: entry.name,
              content: content.substring(0, 500) + (content.length > 500 ? '...' : ''),
              summary: `Session ${sessionNumber} exploration`,
            });
          }
        }
      }
      
      // Sort by session number
      conversationHistory.sort((a, b) => a.session_number - b.session_number);
      
      // Generate current context for next session
      const nextSessionNum = (metadata.sessionCount || 0) + 1;
      const previousContext = await ProjectManager.loadPreviousConversations(nextSessionNum);
      
      return {
        project_name: metadata.name,
        conversation_history: conversationHistory,
        total_sessions: metadata.sessionCount || 0,
        key_insights: [...new Set(keyInsights)].slice(0, 10), // Deduplicate and limit
        current_context: previousContext,
      };
    } catch (error) {
      logger.error("Failed to get project context", error);
      throw error;
    }
  },

  start_exploration: async (args: any) => {
    const { project_name, focus_area } = args;
    
    try {
      let projectPath;
      
      if (project_name) {
        projectPath = await changeToProjectDirectory(project_name);
      } else {
        projectPath = Deno.cwd();
      }
      
      const metadata = await ProjectManager.getProjectMetadata();
      if (!metadata) {
        throw new Error("Not in a valid Orchestration Framework project");
      }
      
      const { explorationTasks } = await ProjectManager.parseTasksFile();
      let nextTask = explorationTasks.find(t => !t.completed);
      
      // If focus_area provided, add it as a new task
      if (focus_area) {
        explorationTasks.push({
          completed: false,
          text: `Explore ${focus_area}`,
        });
        await ProjectManager.updateTasksFile(explorationTasks);
        nextTask = explorationTasks[explorationTasks.length - 1];
      }
      
      if (!nextTask) {
        return {
          project_name: metadata.name,
          session_number: metadata.sessionCount || 0,
          focus_task: "All exploration tasks complete",
          previous_context: "No previous sessions",
          ready_for_conversation: false,
          guidance: "Exploration phase is complete. Ready to move to specification phase.",
        };
      }
      
      // Load previous conversation context
      const nextSessionNum = (metadata.sessionCount || 0) + 1;
      const previousContext = await ProjectManager.loadPreviousConversations(nextSessionNum);
      
      return {
        project_name: metadata.name,
        session_number: nextSessionNum,
        focus_task: nextTask.text,
        previous_context: previousContext,
        ready_for_conversation: true,
        guidance: `🔍 ORCHESTRATION FRAMEWORK - EXPLORATION PHASE

Ready to begin exploration session ${nextSessionNum}.

Current Focus: ${nextTask.text}

${nextSessionNum > 1 ? `Building on ${nextSessionNum - 1} previous session(s). Previous insights preserved.` : 'This is your first exploration session.'}

METHODOLOGY REMINDER: 
• We are in the EXPLORATION phase
• No solutions or implementations yet
• Focus on understanding the problem space
• Ask probing questions to uncover requirements
• Document insights and constraints

The goal is systematic problem understanding before any solution work.`,
      };
    } catch (error) {
      logger.error("Failed to start exploration", error);
      throw error;
    }
  },

  generate_specification: async (args: any) => {
    const { project_name, pattern } = args;
    
    try {
      let projectPath;
      
      if (project_name) {
        projectPath = await changeToProjectDirectory(project_name);
      } else {
        projectPath = Deno.cwd();
      }
      
      const metadata = await ProjectManager.getProjectMetadata();
      if (!metadata) {
        throw new Error("Not in a valid Orchestration Framework project");
      }
      
      // METHODOLOGY ENFORCEMENT: Check if exploration is complete
      const { explorationTasks } = await ProjectManager.parseTasksFile();
      const incompleteTasks = explorationTasks.filter(t => !t.completed);
      
      if (incompleteTasks.length > 0) {
        throw new Error(`Exploration phase incomplete. Remaining tasks: ${incompleteTasks.map(t => t.text).join(', ')}. Complete exploration before generating specification.`);
      }
      
      const patternManager = new PatternManager();
      const specificationPattern = pattern || 'default_specification';
      
      // Load exploration insights
      const explorationInsights = [];
      const explorationDir = join(projectPath, 'exploration');
      
      if (await exists(explorationDir)) {
        for await (const entry of Deno.readDir(explorationDir)) {
          if (entry.name.startsWith('conversation-') && entry.name.endsWith('.md')) {
            const content = await Deno.readTextFile(join(explorationDir, entry.name));
            explorationInsights.push(`## ${entry.name}\n${content}\n`);
          }
        }
      }
      
      const explorationContent = explorationInsights.join('\n---\n\n');
      
      if (!explorationContent) {
        throw new Error("No exploration content found. Complete exploration phase first.");
      }
      
      // Generate specification
      const specification = await patternManager.generateSpecification(
        specificationPattern,
        metadata.name,
        explorationContent
      );
      
      // Save specification to file
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const specFileName = `specification/spec-${specificationPattern}-${timestamp}.md`;
      const specPath = join(projectPath, specFileName);
      
      await Deno.mkdir(join(projectPath, 'specification'), { recursive: true });
      await Deno.writeTextFile(specPath, specification);
      
      // Extract insights for response
      const insights = await patternManager.extractInsights(explorationContent);
      
      return {
        project_name: metadata.name,
        pattern_used: specificationPattern,
        specification_content: specification,
        file_path: specFileName,
        insights_extracted: {
          user_pain_points: insights.userPainPoints,
          core_features: insights.coreFeatures,
          constraints: insights.constraints,
          goals: insights.goals,
        },
      };
    } catch (error) {
      logger.error("Failed to generate specification", error);
      throw error;
    }
  },

  list_patterns: async () => {
    try {
      const patternManager = new PatternManager();
      const patterns = await patternManager.loadAvailablePatterns();
      
      return {
        patterns: patterns.map(p => ({
          name: p.name,
          domain: p.domain,
          description: p.description,
          variables: p.variables?.map(v => v.name) || [],
          sections: p.sections?.map(s => s.title) || [],
        })),
        total: patterns.length,
      };
    } catch (error) {
      logger.error("Failed to list patterns", error);
      throw error;
    }
  },

  check_flywheel_opportunities: async (args: any) => {
    const { project_name } = args;
    
    try {
      let projectPath;
      
      if (project_name) {
        projectPath = await changeToProjectDirectory(project_name);
      } else {
        projectPath = Deno.cwd();
      }
      
      const metadata = await ProjectManager.getProjectMetadata();
      if (!metadata) {
        throw new Error("Not in a valid Orchestration Framework project");
      }
      
      const flywheelManager = new FlywheelManager();
      const gaps = await flywheelManager.analyzeGaps(metadata);
      const recommendation = await flywheelManager.recommendFlywheelIteration();
      const recommendations = flywheelManager.generateGapRecommendations(gaps);
      
      return {
        project_name: metadata.name,
        gaps_detected: gaps,
        recommendations,
        flywheel_recommended: recommendation.recommended,
        target_phase: recommendation.targetPhase,
        reason: recommendation.reason,
      };
    } catch (error) {
      logger.error("Failed to check flywheel opportunities", error);
      throw error;
    }
  },

  save_exploration_session: async (args: any) => {
    const { project_name, conversation_content, session_summary } = args;
    
    try {
      const projectPath = await changeToProjectDirectory(project_name);
      const metadata = await ProjectManager.getProjectMetadata();
      
      if (!metadata) {
        throw new Error(`Project '${project_name}' not found or invalid`);
      }
      
      // Increment session count
      const nextSessionNum = (metadata.sessionCount || 0) + 1;
      
      // Create conversation file
      const timestamp = new Date().toISOString();
      const conversationFileName = `conversation-${nextSessionNum}.md`;
      const conversationPath = join(projectPath, 'exploration', conversationFileName);
      
      // Format conversation content
      const formattedContent = `# Exploration Session ${nextSessionNum}
**Project:** ${metadata.name}
**Date:** ${timestamp}
**Session:** ${nextSessionNum}
${session_summary ? `**Summary:** ${session_summary}` : ''}

---

${conversation_content}

---

**Session completed:** ${timestamp}
`;
      
      // Save conversation file
      await Deno.writeTextFile(conversationPath, formattedContent);
      
      // Update project metadata
      const updatedMetadata = {
        ...metadata,
        sessionCount: nextSessionNum,
        lastSessionDate: timestamp,
      };
      
      await Deno.writeTextFile(
        join(projectPath, '.orchestration.json'),
        JSON.stringify(updatedMetadata, null, 2)
      );
      
      // Update tasks if needed (mark exploration task as complete if this session completes it)
      const { explorationTasks } = await ProjectManager.parseTasksFile();
      
      logger.info(`Saved exploration session ${nextSessionNum} for project ${project_name}`);
      
      return {
        project_name: metadata.name,
        session_number: nextSessionNum,
        file_path: `exploration/${conversationFileName}`,
        conversation_saved: true,
        message: `✅ Exploration session ${nextSessionNum} saved successfully`,
        next_steps: [
          "Conversation captured in exploration files",
          "Session count updated in project metadata",
          "Content available for future specification generation",
          `Use get_project_status('${project_name}') to see updated project state`,
          "Continue exploration or move to specification phase",
        ],
      };
    } catch (error) {
      logger.error("Failed to save exploration session", error);
      throw error;
    }
  },

  complete_exploration_phase: async (args: any) => {
    const { project_name, completion_reason } = args;
    
    try {
      const projectPath = await changeToProjectDirectory(project_name);
      const metadata = await ProjectManager.getProjectMetadata();
      
      if (!metadata) {
        throw new Error(`Project '${project_name}' not found or invalid`);
      }
      
      // Get current exploration tasks
      const { explorationTasks } = await ProjectManager.parseTasksFile();
      const incompleteTasks = explorationTasks.filter(t => !t.completed);
      
      // Mark all exploration tasks as complete
      const completedTasks = explorationTasks.map(task => ({ ...task, completed: true }));
      await ProjectManager.updateTasksFile(completedTasks);
      
      // Update project metadata to mark exploration phase as complete
      const updatedMetadata = {
        ...metadata,
        currentPhase: "specification",
        explorationCompletedDate: new Date().toISOString(),
        explorationCompletionReason: completion_reason || "User determined exploration sufficient",
      };
      
      await Deno.writeTextFile(
        join(projectPath, '.orchestration.json'),
        JSON.stringify(updatedMetadata, null, 2)
      );
      
      // Create completion record in exploration directory
      if (completion_reason) {
        const completionRecord = `# Exploration Phase Completion
**Project:** ${metadata.name}
**Completed:** ${new Date().toISOString()}
**Reason:** ${completion_reason}

## Remaining Tasks (marked complete by user override):
${incompleteTasks.map(t => `- ${t.text}`).join('\n')}

## Completion Decision:
The user determined that sufficient exploration has been conducted to proceed to specification generation.
`;
        
        await Deno.writeTextFile(
          join(projectPath, 'exploration', 'completion-override.md'),
          completionRecord
        );
      }
      
      logger.info(`Exploration phase marked complete for project ${project_name}`);
      
      return {
        project_name: metadata.name,
        exploration_completed: true,
        remaining_tasks_count: incompleteTasks.length,
        completion_reason: completion_reason,
        message: `✅ Exploration phase marked complete. ${incompleteTasks.length} remaining tasks marked as complete.`,
        next_steps: [
          "🎯 Exploration phase completed by user decision",
          "📋 Ready to generate specification",
          `📝 ${incompleteTasks.length} remaining exploration tasks marked complete`,
          completion_reason ? "📄 Completion reason recorded in exploration/completion-override.md" : "",
          `🚀 Use generate_specification('${project_name}') to create specification`,
          `📊 Use get_project_status('${project_name}') to see updated project state`,
        ].filter(Boolean),
      };
    } catch (error) {
      logger.error("Failed to complete exploration phase", error);
      throw error;
    }
  },

  get_framework_lesson: async (args: any) => {
    const { lesson_topic = "methodology-overview", lesson_level = "beginner" } = args;
    
    try {
      // Load available lessons from prompts/lessons directory
      const lessonsDir = join(Deno.cwd(), 'prompts', 'lessons');
      const availableLessons = [];
      
      if (await exists(lessonsDir)) {
        for await (const entry of Deno.readDir(lessonsDir)) {
          if (entry.name.endsWith('.md')) {
            try {
              const lessonPath = join(lessonsDir, entry.name);
              const content = await Deno.readTextFile(lessonPath);
              
              // Parse YAML frontmatter (reuse pattern parsing logic)
              const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
              if (frontmatterMatch) {
                const { parse } = await import("@std/yaml");
                const frontmatter = parse(frontmatterMatch[1]) as any;
                
                availableLessons.push({
                  name: frontmatter.name || entry.name.replace('.md', ''),
                  title: frontmatter.title || 'Untitled Lesson',
                  level: frontmatter.level || 'beginner',
                  description: frontmatter.description || 'No description available',
                });
              }
            } catch (error) {
              logger.warn(`Failed to parse lesson ${entry.name}`, error);
            }
          }
        }
      }
      
      // Find and load the requested lesson
      const requestedLessonFile = `${lesson_topic}.md`;
      const lessonPath = join(lessonsDir, requestedLessonFile);
      
      if (!await exists(lessonPath)) {
        const availableTopics = availableLessons.map(l => l.name).join(', ');
        throw new Error(`Lesson '${lesson_topic}' not found. Available lessons: ${availableTopics}`);
      }
      
      const lessonContent = await Deno.readTextFile(lessonPath);
      
      // Parse lesson metadata
      const frontmatterMatch = lessonContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
      if (!frontmatterMatch) {
        throw new Error(`Invalid lesson format: ${lesson_topic}`);
      }
      
      const { parse } = await import("@std/yaml");
      const frontmatter = parse(frontmatterMatch[1]) as any;
      const content = frontmatterMatch[2];
      
      // Determine next recommended lesson
      const lessonSequence = ['methodology-overview', 'exploration-techniques', 'pattern-system', 'project-workflow'];
      const currentIndex = lessonSequence.indexOf(lesson_topic);
      const nextRecommended = currentIndex >= 0 && currentIndex < lessonSequence.length - 1 
        ? lessonSequence[currentIndex + 1] 
        : undefined;
      
      logger.info(`Delivered lesson: ${lesson_topic} (${lesson_level})`);
      
      return {
        lesson_title: frontmatter.title || 'Orchestration Framework Lesson',
        lesson_content: content,
        lesson_level: frontmatter.level || 'beginner',
        duration: frontmatter.duration || 'Unknown duration',
        available_lessons: availableLessons,
        next_recommended: nextRecommended,
      };
    } catch (error) {
      logger.error("Failed to get framework lesson", error);
      throw error;
    }
  },

  get_man_page: async (args: any) => {
    const { section } = args;
    
    try {
      // Read the man page file
      const manPagePath = join(Deno.cwd(), 'docs', 'man-page.md');
      
      if (!await exists(manPagePath)) {
        throw new Error("Man page not found at docs/man-page.md");
      }
      
      const fullContent = await Deno.readTextFile(manPagePath);
      
      // Extract available sections by finding ## headers
      const sectionHeaders = [];
      const lines = fullContent.split('\n');
      for (const line of lines) {
        const match = line.match(/^## (.+)$/);
        if (match) {
          sectionHeaders.push(match[1].toLowerCase());
        }
      }
      
      let contentToReturn = fullContent;
      let fullPage = true;
      
      // If specific section requested, filter content
      if (section) {
        const sectionLower = section.toLowerCase();
        const sectionRegex = new RegExp(`^## ${section}[\\s\\S]*?(?=^## |$)`, 'im');
        const sectionMatch = fullContent.match(sectionRegex);
        
        if (sectionMatch) {
          // Include the header and section content
          contentToReturn = `# ORCHESTRATION-FRAMEWORK(1) Man Page\n\n${sectionMatch[0]}`;
          fullPage = false;
        } else {
          throw new Error(`Section '${section}' not found. Available sections: ${sectionHeaders.join(', ')}`);
        }
      }
      
      logger.info(`Delivered man page${section ? ` section: ${section}` : ' (full)'}`);
      
      return {
        man_page_content: contentToReturn,
        section_requested: section,
        available_sections: sectionHeaders,
        full_page: fullPage,
      };
    } catch (error) {
      logger.error("Failed to get man page", error);
      throw error;
    }
  },

  write_feedback: async (args: any) => {
    const { project_name, feedback_content, feedback_type = "reflection", session_reference } = args;
    
    try {
      const projectPath = await changeToProjectDirectory(project_name);
      const metadata = await ProjectManager.getProjectMetadata();
      
      if (!metadata) {
        throw new Error(`Project '${project_name}' not found or invalid`);
      }
      
      // Ensure feedback directory exists
      const feedbackDir = join(projectPath, 'feedback');
      await Deno.mkdir(feedbackDir, { recursive: true });
      
      // Generate feedback filename with timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const feedbackFileName = `${feedback_type}-${timestamp}.md`;
      const feedbackPath = join(feedbackDir, feedbackFileName);
      
      // Format feedback content
      const formattedContent = `# ${feedback_type.charAt(0).toUpperCase() + feedback_type.slice(1)} - ${metadata.name}

**Project:** ${metadata.name}
**Date:** ${new Date().toISOString()}
**Type:** ${feedback_type}${session_reference ? `\n**Related Session:** ${session_reference}` : ''}

---

${feedback_content}

---

**Recorded:** ${new Date().toISOString()}
`;
      
      // Save feedback file
      await Deno.writeTextFile(feedbackPath, formattedContent);
      
      logger.info(`Saved ${feedback_type} feedback for project ${project_name}`);
      
      return {
        project_name: metadata.name,
        file_path: `feedback/${feedbackFileName}`,
        feedback_type,
        feedback_saved: true,
        message: `✅ ${feedback_type} feedback saved successfully`,
        next_steps: [
          `${feedback_type.charAt(0).toUpperCase() + feedback_type.slice(1)} captured in feedback folder`,
          "Feedback available for future project retrospectives",
          "Content can inform future methodology improvements",
          `Use get_project_status('${project_name}') to see project state`,
          "Feedback contributes to organizational learning",
        ],
      };
    } catch (error) {
      logger.error("Failed to write feedback", error);
      throw error;
    }
  },
};

// Create and export the MCP server
export async function createOrchestrationMCPServer() {
  logger.info("Creating Orchestration Framework MCP Server...");
  
  return createToolsServer(serverInfo, tools, handlers);
}

// Export handlers for testing
export { handlers as mcpHandlers };

export default createOrchestrationMCPServer;