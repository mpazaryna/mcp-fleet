import { exists } from "@std/fs";
import { dirname, join } from "@std/path";

import { ClaudeClient, ClaudeMessage } from "../claude-client.ts";
import { ProjectManager } from "../project-manager.ts";
import { logger } from "../logger.ts";

const scriptDir = dirname(new URL(import.meta.url).pathname);

// Find the framework root directory (where prompts/ exists)
async function findFrameworkRoot(): Promise<string> {
  const currentDir = Deno.cwd();
  
  // Check if we're already in framework root
  if (await exists(join(currentDir, 'prompts', 'exploration.md'))) {
    return currentDir;
  }
  
  // Check if we're in a project directory (has .orchestration.json)
  if (await exists(join(currentDir, '.orchestration.json'))) {
    // Look for framework root by going up directories
    let searchDir = currentDir;
    for (let i = 0; i < 5; i++) { // Limit search depth
      searchDir = dirname(searchDir);
      if (await exists(join(searchDir, 'prompts', 'exploration.md'))) {
        return searchDir;
      }
    }
  }
  
  // Default to script directory's parent (traditional location)
  return dirname(dirname(dirname(scriptDir)));
}

async function loadPrompt(filename: string, variables: Record<string, string> = {}): Promise<string> {
  const frameworkRoot = await findFrameworkRoot();
  const promptsDir = join(frameworkRoot, 'prompts');
  const promptPath = join(promptsDir, filename);
  
  if (!await exists(promptPath)) {
    throw new Error(`Prompt file not found: ${promptPath}`);
  }
  
  let content = await Deno.readTextFile(promptPath);
  
  for (const [key, value] of Object.entries(variables)) {
    content = content.replaceAll(`{{${key}}}`, value);
  }
  
  return content;
}

export async function exploreCommand(projectName?: string): Promise<void> {
  logger.info("Starting exploration session");
  
  // If project name provided, change to that directory
  if (projectName) {
    const projectPath = join('projects', projectName);
    if (!await exists(projectPath)) {
      console.log(`❌ Project '${projectName}' not found in projects/`);
      return;
    }
    Deno.chdir(projectPath);
  }
  
  const metadata = await ProjectManager.getProjectMetadata();
  if (!metadata) {
    console.log('❌ Not in a framework project directory. Run `deno task init "project name"` first.');
    return;
  }

  const { explorationTasks } = await ProjectManager.parseTasksFile();
  
  const nextTask = explorationTasks.find(t => !t.completed);
  
  if (!nextTask) {
    console.log('✅ All exploration tasks complete!');
    console.log('🎯 Ready to move to specification phase');
    return;
  }

  // Determine session number
  const sessionNum = (metadata.sessionCount || 0) + 1;
  const sessionFile = `exploration/conversation-${sessionNum}.md`;
  
  console.log(`🔍 Exploration Session ${sessionNum}: ${metadata.name}`);
  console.log(`📋 Focus: ${nextTask.text}`);
  if (sessionNum > 1) {
    console.log(`🔗 Building on ${sessionNum - 1} previous session(s)`);
  }
  console.log(`💬 Starting AI-assisted exploration (type 'quit' to exit)...\n`);

  const claude = new ClaudeClient();
  let conversationHistory: ClaudeMessage[] = [];
  
  // Initialize conversation log
  let conversationLog = `# Exploration Session ${sessionNum}: ${metadata.name}\n\n`;
  conversationLog += `**Focus**: ${nextTask.text}\n\n`;
  if (sessionNum > 1) {
    conversationLog += `**Building on**: ${sessionNum - 1} previous session(s)\n\n`;
  }
  
  try {
    // Load context from previous sessions
    const previousContext = await ProjectManager.loadPreviousConversations(sessionNum);
    
    const systemPrompt = await loadPrompt('exploration.md', {
      PROJECT_NAME: metadata.name,
      CURRENT_TASK: nextTask.text,
      SESSION_NUMBER: sessionNum.toString(),
      PREVIOUS_CONTEXT: previousContext
    });

    // Initial message that includes context awareness
    let initialMessage = `Starting exploration session ${sessionNum} for: ${metadata.name}. Current focus: ${nextTask.text}.`;
    
    if (sessionNum > 1) {
      initialMessage += ` This builds on our previous exploration session(s). Please acknowledge what we've already covered and focus on this new area.`;
    } else {
      initialMessage += ` Let's systematically explore this area.`;
    }

    // Initial AI greeting
    logger.debug("Sending initial message to Claude");
    const initialResponse = await claude.chat([
      { role: "user", content: initialMessage }
    ], systemPrompt);
    
    console.log(`🤖 Claude: ${initialResponse}\n`);
    
    conversationLog += `## Session Start: ${new Date().toISOString()}\n\n`;
    conversationLog += `**Claude**: ${initialResponse}\n\n`;
    
    conversationHistory.push(
      { role: "user", content: initialMessage },
      { role: "assistant", content: initialResponse }
    );

    // Interactive conversation loop with transition management
    let exchangeCount = 0;
    const TRANSITION_CHECK_INTERVALS = [5, 10, 15]; // Check at these exchange counts
    
    while (true) {
      const userInput = prompt("You: ");
      if (!userInput || userInput.toLowerCase() === 'quit' || userInput.toLowerCase() === 'exit') {
        logger.info("User ended conversation");
        break;
      }

      conversationHistory.push({ role: "user", content: userInput });
      
      try {
        logger.debug("Sending user message to Claude");
        const response = await claude.chat(conversationHistory, systemPrompt);
        console.log(`\n🤖 Claude: ${response}\n`);
        
        conversationHistory.push({ role: "assistant", content: response });
        exchangeCount++;
        
        // Implement sliding window - keep only last 6 messages (3 exchanges)
        if (conversationHistory.length > 6) {
          conversationHistory = conversationHistory.slice(-6);
          logger.debug("Applied sliding window to conversation history");
        }
        
        conversationLog += `**You**: ${userInput}\n\n`;
        conversationLog += `**Claude**: ${response}\n\n`;
        
        // Save conversation after each exchange
        await Deno.writeTextFile(sessionFile, conversationLog);
        
        // Check for transition prompts at intervals
        if (TRANSITION_CHECK_INTERVALS.includes(exchangeCount)) {
          console.log(`\n🎯 Orchestration Check (${exchangeCount} exchanges):`);
          const continueExploration = prompt("Do you want to continue exploration, or are you ready to transition to specification? (continue/transition/pause): ");
          
          if (continueExploration?.toLowerCase() === 'transition') {
            console.log("🎯 Moving to specification phase. Ending exploration session...");
            break;
          } else if (continueExploration?.toLowerCase() === 'pause') {
            console.log("⏸️  Pausing exploration. You can resume later with `deno task explore`");
            break;
          } else {
            console.log("▶️  Continuing exploration...\n");
          }
        }
        
      } catch (error) {
        logger.error("Error during conversation", error);
        console.log(`❌ Error: ${error instanceof Error ? error.message : String(error)}`);
      }
    }

    // Session completion workflow
    console.log('\n📝 Session complete! Saving conversation...');
    await Deno.writeTextFile(sessionFile, conversationLog);
    
    // Update session count in metadata
    metadata.sessionCount = sessionNum;
    metadata.lastSessionDate = new Date().toISOString();
    await ProjectManager.updateProjectMetadata(metadata);
    
    // Mark current task as complete
    const taskIndex = explorationTasks.findIndex(t => t.text === nextTask.text);
    if (taskIndex !== -1) {
      explorationTasks[taskIndex].completed = true;
      logger.debug(`Marked task as complete: ${nextTask.text}`);
    }
    
    // Ask about additional exploration areas
    console.log('\n🤔 Session reflection:');
    const needsMore = prompt("Did this session reveal new areas that need exploration? (y/n): ");
    
    if (needsMore?.toLowerCase() === 'y' || needsMore?.toLowerCase() === 'yes') {
      const newArea = prompt("What new exploration area did you discover? ");
      if (newArea && newArea.trim()) {
        explorationTasks.push({
          completed: false,
          text: `Explore ${newArea.trim()}`
        });
        console.log(`✅ Added new exploration task: "Explore ${newArea.trim()}"`);
        logger.info(`Added new exploration task: ${newArea.trim()}`);
      }
    }
    
    // Update tasks.md
    await ProjectManager.updateTasksFile(explorationTasks);
    
    console.log(`💾 Session saved to: ${sessionFile}`);
    console.log('📋 Run `deno task status` to see updated progress');
    
    // Show what's next
    const remainingTasks = explorationTasks.filter(t => !t.completed);
    if (remainingTasks.length > 0) {
      console.log(`🎯 Next: ${remainingTasks[0].text}`);
    } else {
      console.log('🎯 Exploration complete! Ready for specification phase.');
    }

  } catch (error) {
    logger.error("Error during exploration session", error);
    console.log(`❌ Error loading exploration prompt: ${error instanceof Error ? error.message : String(error)}`);
  }
}