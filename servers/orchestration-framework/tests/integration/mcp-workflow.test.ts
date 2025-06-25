/**
 * End-to-End MCP Workflow Test
 * 
 * This test validates the complete conversational methodology workflow:
 * 1. Initialize project via MCP
 * 2. Conduct realistic exploration sessions
 * 3. Save exploration conversations
 * 4. Generate pattern-based specification
 * 5. Verify all files and content are created correctly
 * 
 * This proves the core value proposition: natural conversation → systematic methodology
 */

import { assertEquals, assertExists } from "@std/assert";
import { join } from "@std/path";
import { exists } from "@std/fs";
import { mcpHandlers } from "../../src/mcp/server.ts";

// Test data for realistic time management exploration
const TIME_MANAGEMENT_EXPLORATION = {
  projectName: `time-management-improvement-${Date.now()}`,
  initialProblem: "I want to explore good time management because I can't complete my tasks",
  
  explorationSession1: `**You**: I'm struggling with time management. I have a lot of tasks but can't seem to complete them. I feel overwhelmed and constantly behind schedule.

**Claude**: Let me help you explore this systematically. Can you tell me more about what a typical day looks like for you? When do you feel most productive, and when do you tend to get stuck?

**You**: I usually start my day with good intentions, but I get distracted easily. I'll start working on something important, then an email comes in, or I remember something else I need to do. Before I know it, hours have passed and I haven't finished anything meaningful.

**Claude**: That's a very common pattern. It sounds like context switching and interruptions are major factors. How do you currently organize your tasks? Do you use any specific tools or methods?

**You**: I've tried various apps - Todoist, Notion, even just simple lists. But I tend to either overcomplicate the system or abandon it after a few days. I also have trouble estimating how long things will take.

**Claude**: Interesting - so there are really two challenges here: the organizational system itself, and time estimation. When you do manage to focus and get things done, what conditions enable that? Are there specific times, places, or circumstances where you're more successful?

**You**: Actually, yes. I'm most productive in the morning before 10 AM, especially if I can work without interruptions. And I do better with physical deadlines - like if I have a meeting about something, I'll usually get it done beforehand.

**Claude**: Excellent insights. So external structure and accountability seem to help, and you have natural energy patterns. What about the tasks themselves - are they mostly work-related, personal, or a mix? And do you find certain types of tasks harder to complete than others?

**You**: It's a mix, which might be part of the problem. I have work projects, household tasks, personal goals like exercise, and administrative stuff like bills. The administrative and routine tasks are the worst - I procrastinate on them forever.`,

  explorationSession2: `**You**: I've been thinking more about what we discussed. The admin tasks really are my biggest weakness. And I realized I don't have clear boundaries between work and personal time, so everything bleeds together.

**Claude**: That's a crucial insight about boundaries. When everything blends together, it's much harder to prioritize and focus. Can you tell me more about how your days are currently structured? Do you have set work hours, or is it more fluid?

**You**: It's pretty fluid, which I thought would be good for flexibility, but maybe it's hurting me. I work from home, so I might do some work, then some household tasks, then back to work. There's no clear separation.

**Claude**: And how does this affect your ability to complete tasks? Do you find yourself half-finishing things because you're switching contexts so much?

**You**: Exactly! I have dozens of half-finished tasks. I'll start something, get interrupted or distracted, and then when I come back to it later, I have to remember where I was and what I was doing. It's exhausting.

**Claude**: This is really valuable. So we're seeing a pattern where the lack of structure creates cognitive overhead - you're spending mental energy just managing the chaos rather than doing the actual work. What would ideal structure look like to you? If you could design your perfect day, how would it flow?

**You**: I think I'd want clear blocks of time for different types of work. Like, morning for deep work on important projects, afternoon for meetings and communication, and maybe specific times for admin tasks so I actually do them instead of avoiding them.

**Claude**: That makes a lot of sense. And what about the procrastination on admin tasks specifically - what makes those so difficult compared to other work?

**You**: They're boring, and they don't feel important even though I know they are. Like, updating my budget or organizing files - these things matter but they're not exciting or creative. I'd rather work on interesting projects.`,

  explorationSession3: `**You**: I tried blocking my time yesterday based on our conversation, and it helped! But I ran into a problem - I'm terrible at estimating how long things take, so my schedule got completely derailed by noon.

**Claude**: That's fantastic that you tried it and got some positive results! Time estimation is definitely a skill that takes practice. What happened specifically with the time estimates?

**You**: I thought a budget review would take 30 minutes, but it took 2 hours because I found discrepancies I had to investigate. And I allocated 1 hour for email, but there were several that required longer responses than I expected.

**Claude**: Those are perfect examples of why time estimation is tricky - you planned for the ideal case, but reality includes unexpected complications. How did you handle it when you realized you were behind schedule?

**You**: I got frustrated and kind of gave up on the schedule. I reverted to my old reactive mode - just responding to whatever seemed most urgent.

**Claude**: Understandable reaction. So we need to build in buffer time and have strategies for when things go off track. But let's also talk about the success - what specifically made the morning time blocking work well?

**You**: Having a clear intention for what I was going to do during that time. Instead of sitting down and thinking "what should I work on?", I already knew. It eliminated that decision fatigue.

**Claude**: Exactly! Decision fatigue is huge. So pre-deciding reduces cognitive load. What other friction points do you notice when you're trying to start or finish tasks?

**You**: Tools and setup. Like, if I want to work on a presentation but I have to spend 10 minutes finding the right files and opening programs, I sometimes just... don't. The friction is enough to make me procrastinate.

**Claude**: Perfect insight. So we're identifying multiple layers: time structure, realistic estimation, decision pre-loading, and reducing friction. Are there any personal characteristics or constraints we should consider? Like, do you work better with external accountability, or are you more self-motivated?

**You**: Definitely external accountability. When I tell someone I'll do something by a certain time, I almost always do it. But when it's just for me, I'm much more flexible with deadlines.`
};

interface MCPResponse {
  success: boolean;
  [key: string]: any;
}

class MCPTestClient {
  private handlers: any;
  
  constructor() {
    this.handlers = mcpHandlers;
  }
  
  async callTool(toolName: string, args: any): Promise<MCPResponse> {
    // Simulate MCP tool call using exported handlers
    const handler = this.handlers[toolName];
    
    if (!handler) {
      throw new Error(`Tool ${toolName} not found. Available tools: ${Object.keys(this.handlers).join(', ')}`);
    }
    
    try {
      const result = await handler(args);
      return { success: true, ...result };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : String(error) 
      };
    }
  }
}

async function createTestProject(client: MCPTestClient, projectName: string): Promise<void> {
  console.log(`🚀 Creating test project: ${projectName}`);
  
  const result = await client.callTool("init_project", { name: projectName });
  assertEquals(result.success, true);
  assertEquals(result.project_name, projectName);
  
  // Verify project directory was created
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
  const projectPath = join(homeDir!, "OrchestrationProjects", projectName);
  assertEquals(await exists(projectPath), true);
  assertEquals(await exists(join(projectPath, "exploration")), true);
  assertEquals(await exists(join(projectPath, ".orchestration.json")), true);
  
  console.log(`✅ Project created successfully at ${projectPath}`);
}

async function runExplorationSession(
  client: MCPTestClient, 
  projectName: string, 
  sessionContent: string,
  sessionNumber: number
): Promise<void> {
  console.log(`🔍 Running exploration session ${sessionNumber}`);
  
  // Start exploration
  const startResult = await client.callTool("start_exploration", { 
    project_name: projectName 
  });
  assertEquals(startResult.success, true);
  assertEquals(startResult.ready_for_conversation, true);
  
  // Save the exploration conversation
  const saveResult = await client.callTool("save_exploration_session", {
    project_name: projectName,
    conversation_content: sessionContent,
    session_summary: `Session ${sessionNumber}: Time management exploration - key insights captured`
  });
  
  assertEquals(saveResult.success, true);
  assertEquals(saveResult.session_number, sessionNumber);
  assertEquals(saveResult.conversation_saved, true);
  
  // Verify conversation file was created
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
  const conversationPath = join(
    homeDir!, 
    "OrchestrationProjects", 
    projectName, 
    "exploration", 
    `conversation-${sessionNumber}.md`
  );
  assertEquals(await exists(conversationPath), true);
  
  // Verify conversation content was saved correctly
  const savedContent = await Deno.readTextFile(conversationPath);
  assertEquals(savedContent.includes(sessionContent), true);
  assertEquals(savedContent.includes(`Session ${sessionNumber}`), true);
  
  console.log(`✅ Exploration session ${sessionNumber} saved successfully`);
}

async function markExplorationComplete(projectName: string): Promise<void> {
  console.log(`✅ Marking exploration tasks as complete for ${projectName}`);
  
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
  const projectPath = join(homeDir!, "OrchestrationProjects", projectName);
  const tasksPath = join(projectPath, "tasks.md");
  
  // Read current tasks file
  const tasksContent = await Deno.readTextFile(tasksPath);
  
  // Mark exploration task as complete
  const updatedTasks = tasksContent.replace(
    "- [ ] Complete initial problem exploration",
    "- [x] Complete initial problem exploration"
  );
  
  // Write updated tasks back
  await Deno.writeTextFile(tasksPath, updatedTasks);
  
  console.log(`✅ Exploration phase marked as complete`);
}

async function generateSpecification(
  client: MCPTestClient, 
  projectName: string
): Promise<void> {
  console.log(`📋 Generating specification for ${projectName}`);
  
  // Mark exploration tasks as complete first
  await markExplorationComplete(projectName);
  
  // Verify project status shows exploration is ready
  const statusResult = await client.callTool("get_project_status", { 
    project_name: projectName 
  });
  assertEquals(statusResult.success, true);
  
  // Generate specification using life_skill_development pattern (perfect for time management)
  const specResult = await client.callTool("generate_specification", {
    project_name: projectName,
    pattern: "life_skill_development"
  });
  
  assertEquals(specResult.success, true);
  assertEquals(specResult.pattern_used, "life_skill_development");
  assertExists(specResult.specification_content);
  assertExists(specResult.insights_extracted);
  
  // Verify specification file was created
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
  const specPath = join(
    homeDir!, 
    "OrchestrationProjects", 
    projectName, 
    specResult.file_path
  );
  assertEquals(await exists(specPath), true);
  
  // Verify specification content includes insights from exploration
  const specContent = await Deno.readTextFile(specPath);
  assertEquals(specContent.includes("time management"), true);
  assertEquals(specContent.includes("procrastination"), true);
  assertEquals(specContent.includes("admin tasks"), true);
  
  console.log(`✅ Specification generated successfully: ${specResult.file_path}`);
  console.log(`📊 Key insights extracted:`, specResult.insights_extracted);
}

async function verifyCompleteWorkflow(projectName: string): Promise<void> {
  console.log(`🔍 Verifying complete workflow for ${projectName}`);
  
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
  const projectPath = join(homeDir!, "OrchestrationProjects", projectName);
  
  // Verify project structure
  assertEquals(await exists(join(projectPath, "exploration")), true);
  assertEquals(await exists(join(projectPath, "specification")), true);
  assertEquals(await exists(join(projectPath, "execution")), true);
  assertEquals(await exists(join(projectPath, "feedback")), true);
  
  // Verify exploration conversations exist
  assertEquals(await exists(join(projectPath, "exploration", "conversation-1.md")), true);
  assertEquals(await exists(join(projectPath, "exploration", "conversation-2.md")), true);
  assertEquals(await exists(join(projectPath, "exploration", "conversation-3.md")), true);
  
  // Verify specification was generated
  const specDir = join(projectPath, "specification");
  let specFileExists = false;
  try {
    for await (const entry of Deno.readDir(specDir)) {
      if (entry.name.startsWith("spec-life_skill_development-") && entry.name.endsWith(".md")) {
        specFileExists = true;
        break;
      }
    }
  } catch {
    // Directory might not exist yet
  }
  assertEquals(specFileExists, true);
  
  // Verify metadata was updated correctly
  const metadata = JSON.parse(await Deno.readTextFile(join(projectPath, ".orchestration.json")));
  assertEquals(metadata.sessionCount, 3);
  assertEquals(metadata.name, projectName);
  
  console.log(`✅ Complete workflow verification passed!`);
}

async function cleanupTestProject(projectName: string): Promise<void> {
  try {
    const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
    const projectPath = join(homeDir!, "OrchestrationProjects", projectName);
    
    console.log(`📁 Project preserved for inspection at: ${projectPath}`);
    console.log(`📂 Contents include:`);
    console.log(`   • exploration/conversation-1.md`);
    console.log(`   • exploration/conversation-2.md`); 
    console.log(`   • exploration/conversation-3.md`);
    console.log(`   • specification/spec-life_skill_development-*.md`);
    console.log(`   • .orchestration.json (project metadata)`);
    console.log(`   • tasks.md (task tracking)`);
    
    // Comment out the actual cleanup so files persist
    // await Deno.remove(projectPath, { recursive: true });
    // console.log(`🧹 Cleaned up test project: ${projectPath}`);
  } catch {
    // Cleanup failure is not critical for test success
  }
}

Deno.test("MCP End-to-End Workflow - Time Management Exploration → Specification", async () => {
  const projectName = TIME_MANAGEMENT_EXPLORATION.projectName;
  
  try {
    console.log("🎯 Starting complete MCP workflow test...");
    
    // Create MCP client
    const client = new MCPTestClient();
    
    // Step 1: Initialize project
    await createTestProject(client, projectName);
    
    // Step 2: Conduct multi-session exploration
    await runExplorationSession(
      client, 
      projectName, 
      TIME_MANAGEMENT_EXPLORATION.explorationSession1,
      1
    );
    
    await runExplorationSession(
      client, 
      projectName, 
      TIME_MANAGEMENT_EXPLORATION.explorationSession2,
      2
    );
    
    await runExplorationSession(
      client, 
      projectName, 
      TIME_MANAGEMENT_EXPLORATION.explorationSession3,
      3
    );
    
    // Step 3: Generate specification from exploration insights
    await generateSpecification(client, projectName);
    
    // Step 4: Verify complete workflow
    await verifyCompleteWorkflow(projectName);
    
    console.log("🎉 COMPLETE WORKFLOW SUCCESS!");
    console.log("✅ Proved: Natural conversation → Systematic exploration → Pattern-based specification");
    
  } finally {
    // Cleanup
    await cleanupTestProject(projectName);
  }
});

Deno.test("MCP Workflow - Verify Conversation Content Quality", async () => {
  const projectName = `test-conversation-quality-${Date.now()}`;
  
  try {
    const client = new MCPTestClient();
    
    await createTestProject(client, projectName);
    
    // Save a conversation and verify it contains meaningful content
    const testConversation = `**You**: I need help with project planning.

**Claude**: What specific challenges are you facing with project planning?

**You**: I struggle with breaking down large projects into manageable tasks.

**Claude**: Can you give me an example of a recent project where this was an issue?`;
    
    await client.callTool("save_exploration_session", {
      project_name: projectName,
      conversation_content: testConversation,
      session_summary: "Initial planning discussion"
    });
    
    // Verify the saved conversation has proper structure
    const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
    const conversationPath = join(
      homeDir!, 
      "OrchestrationProjects", 
      projectName, 
      "exploration", 
      "conversation-1.md"
    );
    
    const savedContent = await Deno.readTextFile(conversationPath);
    
    // Verify conversation structure
    assertEquals(savedContent.includes("# Exploration Session 1"), true);
    assertEquals(savedContent.includes("**Project:**"), true);
    assertEquals(savedContent.includes("**Date:**"), true);
    assertEquals(savedContent.includes("**Session:**"), true);
    assertEquals(savedContent.includes("**Summary:**"), true);
    assertEquals(savedContent.includes(testConversation), true);
    assertEquals(savedContent.includes("**Session completed:**"), true);
    
    console.log("✅ Conversation content quality verification passed");
    
  } finally {
    await cleanupTestProject(projectName);
  }
});