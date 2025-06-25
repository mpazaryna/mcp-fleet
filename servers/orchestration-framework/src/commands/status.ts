import { exists } from "@std/fs";
import { join } from "@std/path";

import { ProjectManager } from "../project-manager.ts";
import { logger } from "../logger.ts";

export async function statusCommand(projectName?: string): Promise<void> {
  logger.debug("Showing project status");
  
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
    console.log('❌ Not in a framework project directory');
    return;
  }

  const { explorationTasks } = await ProjectManager.parseTasksFile();
  
  const completed = explorationTasks.filter(t => t.completed).length;
  const total = explorationTasks.length;
  const progressPercent = Math.round((completed / total) * 100);
  
  console.log(`\n🎼 ${metadata.name} - Orchestration Framework Dashboard`);
  console.log(`📅 Created: ${new Date(metadata.created).toLocaleDateString()}`);
  console.log(`🔄 Phase: ${metadata.currentPhase}`);
  console.log(`📊 Sessions: ${metadata.sessionCount || 0}`);
  
  console.log(`\n📈 Exploration Progress: ${'█'.repeat(Math.floor(progressPercent/10))}${'░'.repeat(10-Math.floor(progressPercent/10))} ${progressPercent}%`);
  console.log(`✅ Completed: ${completed}  ⏳ Remaining: ${total - completed}`);
  
  console.log(`\n📋 Exploration Tasks:`);
  explorationTasks.forEach((task, i) => {
    const icon = task.completed ? '✅' : (i === completed ? '👉' : '⏳');
    const status = task.completed ? 'DONE' : (i === completed ? 'NEXT' : 'PENDING');
    console.log(`   ${icon} ${task.text} [${status}]`);
  });
  
  // Show next recommended action
  if (completed < total) {
    console.log(`\n🎯 Next Action: deno task explore`);
    console.log(`💡 Focus: ${explorationTasks[completed]?.text || 'Continue exploration'}`);
  } else {
    console.log(`\n🎯 Next Action: deno task specification`);
    console.log(`💡 Ready to move to specification phase`);
  }
  
  // Show existing artifacts
  console.log(`\n📁 Artifacts:`);
  const conversationFiles = [];
  try {
    for await (const entry of Deno.readDir('exploration')) {
      if (entry.name.startsWith('conversation-') && entry.name.endsWith('.md')) {
        conversationFiles.push(entry.name);
      }
    }
    conversationFiles.sort();
    
    if (conversationFiles.length > 0) {
      console.log(`   📝 Conversations: ${conversationFiles.length} sessions`);
      conversationFiles.forEach(file => console.log(`      - ${file}`));
    }
    
    if (await exists('exploration/questions.md')) {
      console.log(`   ❓ Questions template: exploration/questions.md`);
    }
    
    if (await exists('exploration/insights.md')) {
      console.log(`   💡 Insights: exploration/insights.md`);
    }
  } catch (error) {
    logger.warn("Failed to read exploration directory", error);
    console.log(`   📁 exploration/ directory exists`);
  }
}