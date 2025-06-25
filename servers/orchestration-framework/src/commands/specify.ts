import { ensureDir, exists } from "@std/fs";
import { join } from "@std/path";

import { ProjectMetadata } from "../types.ts";
import { ProjectManager } from "../project-manager.ts";
import { PatternManager } from "../pattern-manager.ts";
import { FlywheelManager } from "../flywheel-manager.ts";
import { logger } from "../logger.ts";

export interface SpecifyArgs {
  projectName?: string;
  pattern?: string;
  updateExploration?: boolean;
}

async function loadExplorationInsights(): Promise<string> {
  logger.debug("Loading exploration insights from conversation files");
  
  const insights: string[] = [];
  
  try {
    // Read all conversation files
    for await (const entry of Deno.readDir('exploration')) {
      if (entry.name.startsWith('conversation-') && entry.name.endsWith('.md')) {
        try {
          const content = await Deno.readTextFile(`exploration/${entry.name}`);
          insights.push(`## ${entry.name}\n${content}\n`);
        } catch (error) {
          logger.warn(`Failed to read ${entry.name}`, error);
        }
      }
    }
    
    if (insights.length === 0) {
      return "No exploration conversations found. Consider running exploration first.";
    }
    
    logger.debug(`Loaded insights from ${insights.length} conversation files`);
    return insights.join('\n---\n\n');
    
  } catch (error) {
    logger.warn("Failed to load exploration insights", error);
    return "Unable to load exploration insights. Ensure exploration phase was completed.";
  }
}

async function generatePatternBasedSpecification(metadata: ProjectMetadata, patternName: string): Promise<void> {
  logger.info(`Generating pattern-based specification: ${patternName}`);
  
  console.log(`📋 Pattern-Based Specification: ${metadata.name}`);
  console.log(`🎯 Using pattern: ${patternName}`);
  console.log(`📚 Generating specification from exploration insights...\n`);

  try {
    const patternManager = new PatternManager();
    
    // Check if pattern exists
    const pattern = await patternManager.loadPattern(patternName);
    if (!pattern) {
      console.log(`❌ Pattern '${patternName}' not found.`);
      console.log(`\nAvailable patterns:`);
      
      const availablePatterns = await patternManager.loadAvailablePatterns();
      availablePatterns.forEach(p => {
        console.log(`   - ${p.name} (${p.domain}): ${p.description}`);
      });
      return;
    }

    // Load exploration insights
    const explorationInsights = await loadExplorationInsights();
    
    // Generate specification
    const specification = await patternManager.generateSpecification(
      patternName,
      metadata.name,
      explorationInsights
    );

    // Save specification to file
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const specFileName = `specification/spec-${patternName}-${timestamp}.md`;
    
    await ensureDir('specification');
    await Deno.writeTextFile(specFileName, specification);
    
    console.log(`✅ Specification generated successfully!`);
    console.log(`📄 Pattern: ${pattern.name} (${pattern.domain})`);
    console.log(`📝 File: ${specFileName}`);
    console.log(`📊 Length: ${specification.length} characters`);
    
    // Update project metadata
    if (!metadata.patterns) metadata.patterns = [];
    metadata.patterns.push({
      patternName: patternName,
      usedAt: new Date().toISOString(),
      version: 1,
      customizations: {}
    });
    
    await ProjectManager.updateProjectMetadata(metadata);
    
    console.log(`\n🎯 Next steps:`);
    console.log(`   • Review the generated specification: ${specFileName}`);
    console.log(`   • Customize sections as needed`);
    console.log(`   • Begin execution phase when specification is complete`);
    
  } catch (error) {
    logger.error("Failed to generate pattern-based specification", error);
    console.log(`❌ Error generating specification: ${error instanceof Error ? error.message : String(error)}`);
  }
}

async function handleFlywheelIteration(metadata: ProjectMetadata, gaps?: string[]): Promise<void> {
  logger.info("Starting flywheel iteration");
  
  const flywheelManager = new FlywheelManager();
  
  // If gaps not provided, analyze them
  if (!gaps) {
    gaps = await flywheelManager.analyzeGaps(metadata);
  }
  
  if (gaps.length === 0) {
    console.log('✅ No gaps detected between exploration and specification phases');
    return;
  }
  
  console.log('🔄 Starting Flywheel Iteration: Recursive Improvement Cycle');
  console.log(`📋 Project: ${metadata.name}`);
  console.log(`🎯 Addressing ${gaps.length} identified gaps\n`);
  
  // Create flywheel iteration record
  const iteration = await flywheelManager.createFlywheelIteration(
    'specification',
    'Gap analysis identified areas needing additional exploration',
    'exploration',
    gaps
  );
  
  // Show gaps and recommendations
  console.log('📝 Identified Gaps:');
  gaps.forEach((gap, i) => console.log(`   ${i + 1}. ${gap}`));
  
  const recommendations = flywheelManager.generateGapRecommendations(gaps);
  console.log('\n💡 Recommended Actions:');
  recommendations.forEach((rec, i) => console.log(`   ${i + 1}. ${rec}`));
  
  console.log('\n🎯 Flywheel Process:');
  console.log('   1. Add new exploration tasks based on gaps');
  console.log('   2. Continue with exploration sessions');
  console.log('   3. Re-analyze specification after exploration');
  console.log('   4. Iterate until gaps are resolved\n');
  
  // Ask user which gaps to address
  const gapsToAddress = prompt('Which gap numbers do you want to address? (e.g., "1,3" or "all"): ') || 'all';
  
  let selectedGaps: string[];
  if (gapsToAddress.toLowerCase() === 'all') {
    selectedGaps = gaps;
  } else {
    const indices = gapsToAddress.split(',').map(s => parseInt(s.trim()) - 1);
    selectedGaps = indices.filter(i => i >= 0 && i < gaps.length).map(i => gaps[i]);
  }
  
  if (selectedGaps.length === 0) {
    console.log('❌ No valid gaps selected');
    return;
  }
  
  // Convert gaps to exploration tasks
  const { explorationTasks } = await ProjectManager.parseTasksFile();
  
  console.log(`\n📋 Adding ${selectedGaps.length} new exploration tasks...`);
  for (const gap of selectedGaps) {
    const taskText = `Address gap: ${gap}`;
    explorationTasks.push({
      completed: false,
      text: taskText
    });
    console.log(`   ✅ Added: ${taskText}`);
  }
  
  // Update tasks file
  await ProjectManager.updateTasksFile(explorationTasks);
  
  // Record flywheel iteration
  iteration.updatedArtifacts = ['tasks.md'];
  await flywheelManager.recordFlywheelIteration(iteration);
  
  console.log('\n🎯 Flywheel iteration created successfully!');
  console.log('📋 Next steps:');
  console.log('   • Run `deno task explore` to address new exploration tasks');
  console.log('   • Complete exploration of identified gaps');
  console.log('   • Return to specification when exploration is complete');
  console.log(`\n📊 Flywheel Iteration ID: ${iteration.iterationId}`);
}

export async function specifyCommand(args: SpecifyArgs): Promise<void> {
  logger.info("Starting specification session");
  
  // If project name provided, change to that directory
  if (args.projectName) {
    const projectPath = join('projects', args.projectName);
    if (!await exists(projectPath)) {
      console.log(`❌ Project '${args.projectName}' not found in projects/`);
      return;
    }
    Deno.chdir(projectPath);
  }
  
  const metadata = await ProjectManager.getProjectMetadata();
  if (!metadata) {
    console.log('❌ Not in a framework project directory. Run `deno task init "project name"` first.');
    return;
  }

  // Check for flywheel iteration opportunity
  if (args.updateExploration) {
    await handleFlywheelIteration(metadata);
    return;
  }

  // Analyze gaps and recommend flywheel iteration
  const flywheelManager = new FlywheelManager();
  const recommendation = await flywheelManager.recommendFlywheelIteration();
  
  if (recommendation.recommended) {
    console.log('🔄 Flywheel Analysis: Gaps detected between exploration and specification');
    console.log(`📋 Reason: ${recommendation.reason}`);
    console.log('📝 Identified gaps:');
    recommendation.gaps.forEach(gap => console.log(`   - ${gap}`));
    
    const shouldIterate = prompt('\n🤔 Start flywheel iteration to address these gaps? (y/n): ');
    if (shouldIterate?.toLowerCase() === 'y' || shouldIterate?.toLowerCase() === 'yes') {
      await handleFlywheelIteration(metadata, recommendation.gaps);
      return;
    }
  } else {
    console.log('✅ Flywheel Analysis: No gaps detected - ready to proceed with specification');
  }

  // Check if exploration is complete
  const { explorationTasks } = await ProjectManager.parseTasksFile();
  const incompleteTasks = explorationTasks.filter(t => !t.completed);
  
  if (incompleteTasks.length > 0) {
    console.log('⚠️  Exploration phase not complete. Remaining tasks:');
    incompleteTasks.forEach(task => console.log(`   - ${task.text}`));
    console.log('\n💡 Complete exploration first with `deno task explore` or continue anyway? (complete/continue): ');
    const choice = prompt('') || '';
    if (choice.toLowerCase() !== 'continue') {
      return;
    }
  }

  // Use pattern-based specification (default framework pattern if none specified)
  const specificationPattern = args.pattern || 'default_specification';
  await generatePatternBasedSpecification(metadata, specificationPattern);
}