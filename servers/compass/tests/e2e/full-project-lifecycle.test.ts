import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import { projectHandlers } from "../../src/tools/project-tools.ts";
import { explorationHandlers } from "../../src/tools/exploration-tools.ts";

Deno.test({
  name: "E2E: Complete project lifecycle with real file operations",
  permissions: { read: true, write: true, env: true },
  fn: async () => {
    // Use a test directory under current working directory for easy inspection
    const testWorkspace = join(Deno.cwd(), "tests", "e2e", "test-workspace");
    await Deno.mkdir(testWorkspace, { recursive: true });
    
    const projectName = "sample-ecommerce-platform";
    const projectPath = join(testWorkspace, projectName);
    
    // Clean up any existing project from previous runs
    try {
      await Deno.remove(projectPath, { recursive: true });
    } catch {
      // Ignore if it doesn't exist
    }
    
    try {
      console.log(`\n=== E2E Test: Creating project in ${testWorkspace} ===`);
      
      // PHASE 1: PROJECT INITIALIZATION
      console.log("\n🚀 PHASE 1: Project Initialization");
      const initResult = await projectHandlers.init_project({
        name: projectName,
        projectsDir: testWorkspace,
      });
      
      assertEquals(initResult.success, true);
      console.log(`✅ Project '${projectName}' initialized successfully`);
      
      // Verify project structure was created
      const expectedDirs = ["exploration", "specification", "execution", "feedback"];
      for (const dir of expectedDirs) {
        const dirPath = join(projectPath, dir);
        assertEquals(await exists(dirPath), true);
        console.log(`✅ Directory created: ${dir}/`);
      }
      
      // Verify metadata file
      const metadataPath = join(projectPath, ".compass.json");
      assertEquals(await exists(metadataPath), true);
      const metadata = JSON.parse(await Deno.readTextFile(metadataPath));
      assertEquals(metadata.name, projectName);
      assertEquals(metadata.currentPhase, "exploration");
      console.log(`✅ Metadata file created with correct phase: ${metadata.currentPhase}`);
      
      // Verify tasks file
      const tasksPath = join(projectPath, "tasks.md");
      assertEquals(await exists(tasksPath), true);
      const tasksContent = await Deno.readTextFile(tasksPath);
      assertEquals(tasksContent.includes("Phase 1: Exploration"), true);
      console.log("✅ Tasks file created with exploration phase");
      
      // PHASE 2: EXPLORATION SESSIONS
      console.log("\n🔍 PHASE 2: Exploration Sessions");
      
      // Start exploration
      const exploreResult = await explorationHandlers.start_exploration({
        project_name: projectName,
        projectsDir: testWorkspace,
      });
      
      assertEquals(exploreResult.ready_for_conversation, true);
      assertEquals(exploreResult.session_number, 1);
      console.log(`✅ Exploration started - Session ${exploreResult.session_number}`);
      
      // Save first exploration session
      const session1Content = `**USER:** I want to build an e-commerce platform. What are the key areas I should explore?

**ASSISTANT:** Let's systematically explore the key areas for your e-commerce platform:

1. **Business Model & Requirements**
   - What type of products will you sell? (Physical, digital, services)
   - Will this be B2C, B2B, or marketplace?
   - What's your target market and customer personas?
   - Revenue model (direct sales, subscriptions, commissions)?

2. **Technical Architecture**
   - Expected scale (users, products, transactions per day)?
   - Mobile-first, web-first, or omnichannel?
   - Integration requirements (payment processors, shipping, inventory)?
   - Security and compliance needs (PCI DSS, GDPR, etc.)?

3. **User Experience & Journey**
   - Customer acquisition and onboarding flow
   - Product discovery and search capabilities
   - Shopping cart and checkout experience
   - Post-purchase experience and support

Let's start with the business model - can you tell me more about what you want to sell and who your target customers are?`;

      const saveResult1 = await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: session1Content,
        session_summary: "Initial business model and technical architecture exploration",
        projectsDir: testWorkspace,
      });
      
      assertEquals(saveResult1.conversation_saved, true);
      assertEquals(saveResult1.session_number, 1);
      console.log(`✅ Session 1 saved: ${saveResult1.file_path}`);
      
      // Verify conversation file was created
      const conv1Path = join(projectPath, "exploration", "conversation-1.md");
      assertEquals(await exists(conv1Path), true);
      const conv1Content = await Deno.readTextFile(conv1Path);
      assertEquals(conv1Content.includes("Initial business model"), true);
      assertEquals(conv1Content.includes("e-commerce platform"), true);
      console.log("✅ Conversation file contains expected content");
      
      // Start second exploration session
      const exploreResult2 = await explorationHandlers.start_exploration({
        project_name: projectName,
        projectsDir: testWorkspace,
      });
      
      assertEquals(exploreResult2.session_number, 2);
      assertEquals(exploreResult2.previous_context.includes("SESSION 1 INSIGHTS"), true);
      console.log("✅ Session 2 started with previous context");
      
      // Save second exploration session
      const session2Content = `**USER:** Based on our previous discussion, I want to focus on fashion items (clothing and accessories) for millennials and Gen Z, primarily B2C with some influencer partnerships.

**ASSISTANT:** Excellent! Fashion e-commerce for millennials/Gen Z has specific characteristics. Let me explore the key technical and business considerations:

**Technical Requirements:**
- Mobile-first design (80%+ of this demographic shops on mobile)
- Fast image loading and high-quality product photos
- Size recommendation engine
- AR/VR try-on features
- Social media integration for sharing
- Influencer collaboration tools

**Business Model Specifics:**
- Seasonal inventory management
- Returns and exchange policies (high return rates in fashion)
- Size chart standardization
- Trend forecasting integration
- Influencer commission tracking

**User Experience Priorities:**
- Visual search capabilities
- Outfit recommendations
- Social proof (reviews, user photos)
- Wishlist and favorites
- Quick reordering

What's your approach to inventory - will you hold stock, dropship, or use a hybrid model?`;

      const saveResult2 = await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: session2Content,
        session_summary: "Fashion-specific requirements and technical considerations",
        projectsDir: testWorkspace,
      });
      
      assertEquals(saveResult2.session_number, 2);
      console.log(`✅ Session 2 saved: ${saveResult2.file_path}`);
      
      // PHASE 3: PROJECT CONTEXT AND STATUS
      console.log("\n📊 PHASE 3: Project Context Review");
      
      const contextResult = await explorationHandlers.get_project_context({
        project_name: projectName,
        projectsDir: testWorkspace,
      });
      
      assertEquals(contextResult.total_sessions, 2);
      assertEquals(contextResult.conversation_history.length, 2);
      console.log(`✅ Project context loaded: ${contextResult.total_sessions} sessions`);
      
      // Check project status
      const statusResult = await projectHandlers.get_project_status({
        project_name: projectName,
        projectsDir: testWorkspace,
      });
      
      assertEquals(statusResult.current_phase, "exploration");
      assertEquals(statusResult.next_action, "start_exploration");
      console.log(`✅ Project status: ${statusResult.status_summary}`);
      
      // PHASE 4: EXPLORATION COMPLETION
      console.log("\n✅ PHASE 4: Exploration Completion");
      
      const completeResult = await explorationHandlers.complete_exploration_phase({
        project_name: projectName,
        completion_reason: "Sufficient exploration completed for fashion e-commerce platform. Key areas covered: business model, target audience, technical architecture, and user experience requirements.",
        projectsDir: testWorkspace,
      });
      
      assertEquals(completeResult.exploration_completed, true);
      console.log("✅ Exploration phase completed");
      
      // Verify completion record
      const completionPath = join(projectPath, "exploration", "completion-override.md");
      assertEquals(await exists(completionPath), true);
      const completionContent = await Deno.readTextFile(completionPath);
      assertEquals(completionContent.includes("Sufficient exploration completed"), true);
      console.log("✅ Completion record created");
      
      // Verify phase transition
      const updatedMetadata = JSON.parse(await Deno.readTextFile(metadataPath));
      assertEquals(updatedMetadata.currentPhase, "specification");
      assertEquals(updatedMetadata.sessionCount, 2);
      assertExists(updatedMetadata.explorationCompletedDate);
      console.log(`✅ Phase transitioned to: ${updatedMetadata.currentPhase}`);
      
      // PHASE 5: FINAL VERIFICATION
      console.log("\n🔍 PHASE 5: Final File Structure Verification");
      
      const finalFiles = [
        ".compass.json",
        "tasks.md",
        "exploration/conversation-1.md",
        "exploration/conversation-2.md",
        "exploration/completion-override.md",
      ];
      
      for (const file of finalFiles) {
        const filePath = join(projectPath, file);
        assertEquals(await exists(filePath), true);
        const stat = await Deno.stat(filePath);
        assertEquals(stat.isFile, true);
        console.log(`✅ File exists and is readable: ${file}`);
      }
      
      console.log("\n🎉 E2E TEST COMPLETED SUCCESSFULLY");
      console.log(`📁 Test artifacts preserved at: ${projectPath}`);
      console.log("\nProject Structure Created:");
      console.log(`${projectName}/`);
      console.log(`├── .compass.json (metadata)`);
      console.log(`├── tasks.md (phase tracking)`);
      console.log(`├── exploration/`);
      console.log(`│   ├── conversation-1.md`);
      console.log(`│   ├── conversation-2.md`);
      console.log(`│   └── completion-override.md`);
      console.log(`├── specification/ (ready for next phase)`);
      console.log(`├── execution/`);
      console.log(`└── feedback/`);
      
    } catch (error) {
      console.error(`❌ E2E Test failed: ${error}`);
      throw error;
    }
    
    // Note: We're intentionally NOT cleaning up the test workspace
    // so the files can be inspected manually
  },
});