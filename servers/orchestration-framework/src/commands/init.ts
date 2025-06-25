import { ensureDir, exists } from "@std/fs";
import { join } from "@std/path";

import { ProjectMetadata } from "../types.ts";
import { FRAMEWORK_TEMPLATES } from "../templates.ts";
import { logger } from "../logger.ts";

export async function initCommand(projectName: string): Promise<void> {
  logger.info(`Initializing project: ${projectName}`);
  
  const projectDir = join('projects', projectName.toLowerCase().replace(/\s+/g, '-'));
  
  if (await exists(projectDir)) {
    console.log(`❌ Project '${projectDir}' already exists`);
    Deno.exit(1);
  }

  await ensureDir(`${projectDir}/exploration`);
  await ensureDir(`${projectDir}/specification`);
  await ensureDir(`${projectDir}/execution`);
  await ensureDir(`${projectDir}/feedback`);

  const tasksContent = FRAMEWORK_TEMPLATES.tasks
    .replace(/{{PROJECT_NAME}}/g, projectName)
    .replace(/{{STATUS}}/g, "Project initialized - Ready for exploration")
    .replace(/{{NEXT_ACTION}}/g, "deno task explore");
  
  await Deno.writeTextFile(`${projectDir}/tasks.md`, tasksContent);

  const questionsContent = FRAMEWORK_TEMPLATES.explorationQuestions
    .replace(/{{PROJECT_NAME}}/g, projectName);
  await Deno.writeTextFile(`${projectDir}/exploration/questions.md`, questionsContent);

  const metadata: ProjectMetadata = {
    name: projectName,
    created: new Date().toISOString(),
    currentPhase: "exploration",
    status: "initialized",
    sessionCount: 0
  };
  await Deno.writeTextFile(`${projectDir}/.orchestration.json`, JSON.stringify(metadata, null, 2));

  console.log(`✅ Project initialized: ${projectDir}`);
  console.log(`\n🎯 Next steps:`);
  console.log(`   cd ${projectDir}`);
  console.log(`   deno task status    # View project dashboard`);
  console.log(`   deno task explore   # Start first exploration session`);
  
  logger.info(`Project initialized successfully: ${projectDir}`);
}