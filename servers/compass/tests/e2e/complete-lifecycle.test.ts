import { assertEquals, assertExists, assert } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import { projectHandlers } from "../../src/tools/project-tools.ts";
import { explorationHandlers } from "../../src/tools/exploration-tools.ts";
import { specificationHandlers } from "../../src/tools/specification-tools.ts";
import { executionHandlers } from "../../src/tools/execution-tools.ts";

Deno.test({
  name: "E2E: Complete project lifecycle - Exploration → Specification → Execution",
  permissions: { read: true, write: true, env: true },
  fn: async () => {
    // Use a test directory under current working directory for easy inspection
    const testWorkspace = join(Deno.cwd(), "tests", "e2e", "complete-lifecycle-workspace");
    await Deno.mkdir(testWorkspace, { recursive: true });
    
    const projectName = "ai-productivity-assistant";
    const projectPath = join(testWorkspace, projectName);
    
    // Clean up any existing project from previous runs
    try {
      await Deno.remove(projectPath, { recursive: true });
    } catch {
      // Ignore if it doesn't exist
    }
    
    try {
      console.log(`\n=== Complete Lifecycle E2E Test ===`);
      console.log(`📁 Project workspace: ${testWorkspace}`);
      console.log(`🚀 Project: ${projectName}`);
      
      // ===============================
      // PHASE 1: PROJECT INITIALIZATION
      // ===============================
      console.log("\n🚀 PHASE 1: Project Initialization");
      const initResult = await projectHandlers.init_project({
        name: projectName,
        projectsDir: testWorkspace,
      });
      
      assertEquals(initResult.success, true);
      console.log(`✅ Project '${projectName}' initialized successfully`);
      
      // ===============================
      // PHASE 2: EXPLORATION SESSIONS
      // ===============================
      console.log("\n🔍 PHASE 2: Exploration Sessions");
      
      // Start exploration
      const exploreResult = await explorationHandlers.start_exploration({
        project_name: projectName,
        projectsDir: testWorkspace,
      });
      
      assertEquals(exploreResult.ready_for_conversation, true);
      console.log(`✅ Exploration started - Session ${exploreResult.session_number}`);
      
      // Save first exploration session - detailed requirements gathering
      const session1Content = `**USER:** I want to build an AI-powered productivity assistant that helps knowledge workers manage their tasks, research, and decision-making. What should I explore?

**ASSISTANT:** Great concept! An AI-powered productivity assistant is a complex system with many considerations. Let me help you explore the key areas systematically:

## Core Functionality & Features
1. **Task Management Intelligence**
   - AI-powered task prioritization based on deadlines, importance, and context
   - Smart scheduling that adapts to your work patterns and energy levels
   - Automatic task breakdown for complex projects
   - Integration with existing productivity tools (Notion, Asana, Todoist)

2. **Research & Knowledge Management**
   - Intelligent document summarization and extraction
   - Cross-reference finding across your knowledge base
   - Research assistant that can gather and synthesize information
   - Personal knowledge graph that learns from your interactions

3. **Decision Support System**
   - Decision framework recommendations based on decision type
   - Pros/cons analysis with weighted criteria
   - Historical decision tracking and outcome analysis
   - Bias detection and mitigation suggestions

## Technical Architecture Considerations
- **AI Model Strategy**: Local vs cloud LLMs, fine-tuning approaches
- **Data Privacy**: Local-first architecture vs cloud processing
- **Integration Layer**: APIs for calendar, email, document systems
- **User Interface**: Desktop app, web app, mobile, or browser extension
- **Real-time Processing**: For notifications and contextual suggestions

## User Experience & Personalization
- **Learning System**: How the AI adapts to individual work styles
- **Interaction Modalities**: Chat, voice, automation rules, smart suggestions
- **Onboarding**: How to train the system on user preferences initially
- **Trust & Transparency**: Explaining AI decisions and allowing user control

What's your primary use case? Are you building this for yourself, a specific industry, or as a general productivity tool?`;

      const saveResult1 = await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: session1Content,
        session_summary: "Core functionality, technical architecture, and user experience exploration",
        projectsDir: testWorkspace,
      });
      
      assertEquals(saveResult1.conversation_saved, true);
      console.log(`✅ Session 1 saved: ${saveResult1.file_path}`);
      
      // Save second exploration session - technical deep dive
      const exploreResult2 = await explorationHandlers.start_exploration({
        project_name: projectName,
        projectsDir: testWorkspace,
      });
      
      const session2Content = `**USER:** I want to focus on knowledge workers in consulting and research roles. The system should be desktop-first with web backup, using local LLMs for privacy. Priority on document analysis and decision support.

**ASSISTANT:** Perfect focus! Consulting and research professionals have specific needs. Let me explore the targeted requirements:

## Target User Profile: Consultants & Researchers
**Daily Workflows:**
- Document-heavy research and analysis
- Client presentation preparation  
- Data synthesis from multiple sources
- Time-sensitive decision making
- Collaborative knowledge sharing

**Key Pain Points:**
- Information overload from multiple sources
- Difficulty tracking decision rationales over time
- Manual effort in document summarization
- Context switching between tools
- Maintaining confidentiality with client data

## Technical Architecture for Privacy-First Design
**Local-First Approach:**
- Ollama integration for local LLM inference
- SQLite database for knowledge storage
- Electron/Tauri desktop application
- Optional cloud sync for non-sensitive metadata only

**Document Processing Pipeline:**
- PDF, Word, PowerPoint parsing capabilities
- OCR for scanned documents and images
- Semantic chunking and embedding generation
- Local vector database (Chroma/Qdrant)

**Decision Support Features:**
- Framework templates (SWOT, decision trees, cost-benefit)
- Stakeholder analysis automation
- Risk assessment questionnaires
- Historical decision outcome tracking

## Implementation Considerations
**Technology Stack:**
- Frontend: Electron + React/Vue for cross-platform desktop
- Backend: Node.js/Python for document processing
- AI: Ollama + Mistral/Llama models for local inference
- Database: SQLite + vector embeddings
- Security: End-to-end encryption for document storage

**MVP Scope:**
- Document upload and intelligent summarization
- Basic decision framework templates
- Simple task prioritization
- Search across personal knowledge base

What's your timeline and team size for this project? Are you planning to build this as open source or commercial?`;

      const saveResult2 = await explorationHandlers.save_exploration_session({
        project_name: projectName,
        conversation_content: session2Content,
        session_summary: "Target user focus, privacy-first architecture, and technical implementation details",
        projectsDir: testWorkspace,
      });
      
      assertEquals(saveResult2.session_number, 2);
      console.log(`✅ Session 2 saved: ${saveResult2.file_path}`);
      
      // Complete exploration phase
      const completeResult = await explorationHandlers.complete_exploration_phase({
        project_name: projectName,
        completion_reason: "Comprehensive exploration completed for AI productivity assistant. Covered target users (consultants/researchers), privacy-first technical architecture, core features (document analysis, decision support), and implementation approach with local LLMs.",
        projectsDir: testWorkspace,
      });
      
      assertEquals(completeResult.exploration_completed, true);
      console.log("✅ Exploration phase completed and transitioned to specification");
      
      // ===============================
      // PHASE 3: SPECIFICATION GENERATION
      // ===============================
      console.log("\n📋 PHASE 3: Specification Generation");
      
      // List available patterns
      const patternsResult = await specificationHandlers.list_patterns();
      assertEquals(patternsResult.success, true);
      console.log(`✅ Available specification patterns: ${patternsResult.patterns.length}`);
      
      // Generate specification using software pattern
      const specResult = await specificationHandlers.generate_specification({
        project_name: projectName,
        pattern: "software_product_requirements",
        projectsDir: testWorkspace
      });
      
      assertEquals(specResult.success, true);
      console.log(`✅ Specification generated using pattern: ${specResult.pattern_used}`);
      console.log(`📄 Specification file: ${specResult.file_path}`);
      
      // Verify specification file was created
      const specFilePath = join(projectPath, specResult.file_path);
      assertEquals(await exists(specFilePath), true);
      const specContent = await Deno.readTextFile(specFilePath);
      console.log(`✅ Specification file created (${specContent.length} characters)`);
      
      // Check specification status
      const specStatus = await specificationHandlers.get_specification_status({
        project_name: projectName,
        projectsDir: testWorkspace
      });
      
      assertEquals(specStatus.current_phase, "specification");
      assertEquals(specStatus.specifications_generated, 1);
      console.log(`✅ Specification status: ${specStatus.specifications_generated} specification(s) generated`);
      
      // ===============================
      // PHASE 4: EXECUTION SETUP
      // ===============================
      console.log("\n⚙️ PHASE 4: Execution Setup");
      
      // Manually mark specification as completed to enable execution
      const metadataPath = join(projectPath, ".compass.json");
      const metadata = JSON.parse(await Deno.readTextFile(metadataPath));
      metadata.specificationCompletedDate = new Date().toISOString();
      await Deno.writeTextFile(metadataPath, JSON.stringify(metadata, null, 2));
      console.log("✅ Specification phase marked as completed");
      
      // Start execution phase
      const execResult = await executionHandlers.start_execution({
        projectName: projectName,
        workspacePath: testWorkspace
      });
      
      assertEquals(execResult.success, true);
      console.log(`✅ Execution plan created with ${execResult.data?.tasks?.length} tasks`);
      console.log(`📋 Execution plan: ${execResult.data?.executionPlanPath}`);
      console.log(`📝 Tasks file: ${execResult.data?.tasksPath}`);
      
      // List execution tasks
      const tasksResult = await executionHandlers.list_tasks({
        projectName: projectName,
        workspacePath: testWorkspace
      });
      
      assertEquals(tasksResult.success, true);
      console.log(`✅ Execution tasks loaded: ${tasksResult.data?.summary?.total} total`);
      console.log(`   - Pending: ${tasksResult.data?.summary?.pending}`);
      console.log(`   - Completed: ${tasksResult.data?.summary?.completed}`);
      
      // Show task breakdown by category
      const tasks = tasksResult.data?.tasks || [];
      const categories = [...new Set(tasks.map((t: any) => t.category))];
      console.log(`✅ Task categories: ${categories.join(", ")}`);
      
      // ===============================
      // PHASE 5: FINAL VERIFICATION
      // ===============================
      console.log("\n🔍 PHASE 5: Final Structure Verification");
      
      const finalFiles = [
        ".compass.json",
        "tasks.md",
        "exploration/conversation-1.md",
        "exploration/conversation-2.md", 
        "exploration/completion-override.md",
        specResult.file_path,
        "execution/execution-plan.md",
        "execution/tasks.json"
      ];
      
      for (const file of finalFiles) {
        const filePath = join(projectPath, file);
        assertEquals(await exists(filePath), true);
        const stat = await Deno.stat(filePath);
        assertEquals(stat.isFile, true);
        console.log(`✅ File exists: ${file}`);
      }
      
      // Verify final project state
      const finalMetadata = JSON.parse(await Deno.readTextFile(metadataPath));
      assertEquals(finalMetadata.currentPhase, "execution");
      assertExists(finalMetadata.explorationCompletedDate);
      assertExists(finalMetadata.specificationCompletedDate);
      assertExists(finalMetadata.executionStartedDate);
      
      // ===============================
      // SUMMARY AND OUTPUT
      // ===============================
      console.log("\n🎉 COMPLETE LIFECYCLE TEST SUCCESSFUL!");
      console.log(`📁 All artifacts preserved at: ${projectPath}`);
      console.log("\n📋 Final Project Structure:");
      console.log(`${projectName}/`);
      console.log(`├── .compass.json (project metadata)`);
      console.log(`├── tasks.md (phase tracking)`);
      console.log(`├── exploration/ (2 conversations + completion)`);
      console.log(`│   ├── conversation-1.md (core functionality exploration)`);
      console.log(`│   ├── conversation-2.md (technical architecture deep-dive)`);
      console.log(`│   └── completion-override.md`);
      console.log(`├── specification/ (requirements document)`);
      console.log(`│   └── ${specResult.file_path.split('/').pop()} (generated PRD)`);
      console.log(`├── execution/ (task breakdown and planning)`);
      console.log(`│   ├── execution-plan.md (detailed implementation plan)`);
      console.log(`│   └── tasks.json (actionable task list)`);
      console.log(`└── feedback/ (ready for final phase)`);
      
      console.log("\n📄 Key Generated Documents:");
      console.log(`   • Exploration insights: ${finalMetadata.sessionCount} sessions`);
      console.log(`   • Specification: ${specResult.pattern_used} pattern`);
      console.log(`   • Execution tasks: ${tasksResult.data?.summary?.total} actionable items`);
      
      console.log(`\n📂 Review the complete project at:`);
      console.log(`   ${projectPath}`);
      
    } catch (error) {
      console.error(`❌ Complete Lifecycle Test failed: ${error}`);
      throw error;
    }
    
    // Note: We're intentionally NOT cleaning up the test workspace
    // so the generated documents can be inspected manually
  },
});