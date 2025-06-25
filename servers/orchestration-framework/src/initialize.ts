#!/usr/bin/env -S deno run --allow-read --allow-write --allow-net

import { parseArgs } from "@std/cli";
import { ensureDir, exists } from "@std/fs";

const FRAMEWORK_TEMPLATES = {
 tasks: `# {{PROJECT_NAME}} - Orchestration Framework Tasks

## Phase 1: Exploration ⏳
- [ ] Complete exploration questions template
- [ ] Conduct AI-assisted exploration conversations
- [ ] Process exploration inputs into insights
- **Artifacts**: \`exploration/questions.md\`, \`exploration/conversation.md\`, \`exploration/insights.md\`

## Phase 2: Specification 📋
- [ ] Transform insights into structured specifications
- [ ] Generate behavioral scenarios (Given/When/Then)
- [ ] Define system architecture and components
- **Artifacts**: \`specification/requirements.md\`, \`specification/scenarios.gherkin\`

## Phase 3: Execution 🎯
- [ ] Implement solution based on specifications
- [ ] Validate against acceptance criteria
- **Artifacts**: Working solution in \`execution/\`

## Phase 4: Feedback & Learning 🔄
- [ ] Analyze outcomes and lessons learned
- [ ] Update framework knowledge base
- **Artifacts**: \`feedback/lessons.md\`

---
**Current Status**: Project initialized - Ready for exploration
**Next Action**: \`orch explore\`
`,

 explorationQuestions: `# Exploration Phase: {{PROJECT_NAME}}

## Core Problem Definition
What problem are we actually solving?

**Surface problem**: 
*Write the obvious, immediate problem statement here*

**Deeper problems**: 
*What underlying issues might this surface problem represent?*

**Why is this important now?**:
*What makes this urgent or timely?*

## Assumptions to Challenge
What are we assuming about this situation?

**Assumption 1**: 
*State a key assumption you're making*
- Evidence supporting this assumption:
- Evidence that might challenge this assumption:

**Assumption 2**:
*State another key assumption*
- Evidence supporting this assumption:
- Evidence that might challenge this assumption:

## Edge Cases & Failure Modes
What could go wrong or not work as expected?

**Edge case 1**: 
*Describe a scenario where the obvious solution might not work*

**Edge case 2**:
*Describe another challenging scenario*

**Primary failure mode**:
*What's the most likely way this could fail completely?*

## Integration & Constraints  
What real-world factors affect this?

**Existing systems/processes**:
*What do you already have in place that this needs to work with?*

**Time constraints**:
*What are the real deadlines and time pressures?*

**Resource constraints**:
*What limitations exist in terms of people, budget, tools?*

**Stakeholder constraints**:
*Who needs to be involved and what are their requirements?*

## The "Hard Stuff"
What makes this problem more complex than it initially appears?

**Technical complexity**:
*What technical challenges are lurking beneath the surface?*

**Organizational complexity**:
*What people/process issues might emerge?*

**Domain complexity**:
*What specialized knowledge or expertise is required?*

---
*Complete this template thoughtfully. Take time to reflect on each section. Use \`orch chat\` if you want to explore any of these questions with AI assistance.*
`
};

async function initProject(projectName: string) {
 const projectDir = projectName.toLowerCase().replace(/\s+/g, '-');
 
 // Check if project already exists
 if (await exists(projectDir)) {
   console.log(`❌ Project '${projectDir}' already exists`);
   Deno.exit(1);
 }

 // Create project structure
 await ensureDir(`${projectDir}/exploration`);
 await ensureDir(`${projectDir}/specification`);
 await ensureDir(`${projectDir}/execution`);
 await ensureDir(`${projectDir}/feedback`);

 // Generate tasks.md
 const tasksContent = FRAMEWORK_TEMPLATES.tasks.replace(/{{PROJECT_NAME}}/g, projectName);
 await Deno.writeTextFile(`${projectDir}/tasks.md`, tasksContent);

 // Generate exploration questions template
 const questionsContent = FRAMEWORK_TEMPLATES.explorationQuestions.replace(/{{PROJECT_NAME}}/g, projectName);
 await Deno.writeTextFile(`${projectDir}/exploration/questions.md`, questionsContent);

 // Create empty conversation file
 await Deno.writeTextFile(`${projectDir}/exploration/conversation.md`, `# Exploration Conversations: ${projectName}\n\n*AI-assisted exploration conversations will be recorded here*\n\n`);

 // Create project metadata
 const metadata = {
   name: projectName,
   created: new Date().toISOString(),
   currentPhase: "exploration",
   status: "initialized"
 };
 await Deno.writeTextFile(`${projectDir}/.orchestration.json`, JSON.stringify(metadata, null, 2));

 console.log(`✅ Orchestration Framework project initialized: ${projectDir}`);
 console.log(`📁 Project structure created`);
 console.log(`📋 Framework tasks generated: ${projectDir}/tasks.md`);
 console.log(`❓ Exploration questions ready: ${projectDir}/exploration/questions.md`);
 console.log(`\n🎯 Next steps:`);
 console.log(`   cd ${projectDir}`);
 console.log(`   orch explore  # Start exploration phase`);
 console.log(`   orch status   # Check current progress`);
}

async function main() {
 const args = parseArgs(Deno.args);
 
 if (args._.length === 0) {
   console.log("Orchestration Framework CLI");
   console.log("\nUsage:");
   console.log("  orch init \"project name\"     # Initialize new framework project");
   console.log("  orch status                  # Show current project status");
   console.log("  orch explore                 # Start exploration phase");
   console.log("  orch chat                    # AI-assisted exploration");
   Deno.exit(0);
 }

 const command = args._[0];
 
 switch (command) {
   case "init":
     if (args._.length < 2) {
       console.log("❌ Project name required: orch init \"project name\"");
       Deno.exit(1);
     }
     await initProject(args._[1] as string);
     break;
     
   case "status":
     console.log("📊 Status checking not implemented yet");
     break;
     
   case "explore":
     console.log("🔍 Exploration phase not implemented yet");
     break;
     
   case "chat":
     console.log("💬 AI chat not implemented yet");
     break;
     
   default:
     console.log(`❌ Unknown command: ${command}`);
     Deno.exit(1);
 }
}

if (import.meta.main) {
 main();
}