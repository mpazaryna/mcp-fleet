#!/usr/bin/env -S deno run --allow-read --allow-write --allow-net --allow-env

import { parseArgs } from "@std/cli";
import { exists } from "@std/fs";
import { dirname, join } from "@std/path";

import { logger } from "./logger.ts";
import { initCommand } from "./commands/init.ts";
import { statusCommand } from "./commands/status.ts";
import { exploreCommand } from "./commands/explore.ts";
import { specifyCommand, SpecifyArgs } from "./commands/specify.ts";

// Command registry for functional approach
type CommandFunction = (...args: unknown[]) => Promise<void>;

const commands: Map<string, CommandFunction> = new Map([
  ['init', initCommand as CommandFunction],
  ['status', statusCommand as CommandFunction],
  ['explore', exploreCommand as CommandFunction],
  ['specify', specifyCommand as CommandFunction],
]);

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
  const scriptDir = dirname(new URL(import.meta.url).pathname);
  return dirname(scriptDir);
}

async function main() {
  const args = parseArgs(Deno.args);
  
  if (args._.length === 0) {
    const frameworkRoot = await findFrameworkRoot();
    const promptsDir = join(frameworkRoot, 'prompts');
    
    console.log("🎼 Orchestration Framework CLI");
    console.log("\nCommands:");
    console.log("  deno task init \"project name\"     # Initialize new project");
    console.log("  deno task status [project]        # Show project dashboard");
    console.log("  deno task explore [project]       # Start/continue exploration session");
    console.log("  deno task specify [project]       # Begin specification phase");
    console.log("  deno task specify [project] pattern=pattern_name  # Generate pattern-based specification");
    console.log("  deno task specify [project] --update-exploration  # Start flywheel iteration to update exploration");
    console.log("\nFramework Approach:");
    console.log("  • Systematic exploration before solutions");
    console.log("  • Active transition management between phases");
    console.log("  • Each session builds on previous insights");
    console.log("  • Type 'quit' to end sessions and reflect");
    console.log(`\nPrompts Directory: ${promptsDir}`);
    Deno.exit(0);
  }

  const command = args._[0] as string;
  
  try {
    const commandFunction = commands.get(command);
    
    if (!commandFunction) {
      console.log(`❌ Unknown command: ${command}`);
      Deno.exit(1);
    }
    
    // Handle different command argument patterns
    switch (command) {
      case "init":
        if (args._.length < 2) {
          console.log("❌ Project name required: deno task init \"project name\"");
          Deno.exit(1);
        }
        await commandFunction(args._[1] as string);
        break;
        
      case "status":
      case "explore":
        await commandFunction(args._[1] as string);
        break;
        
      case "specify": {
        // Parse parameters: pattern=pattern_name or --update-exploration
        let projectArg: string | undefined = undefined;
        let patternArg: string | undefined = undefined;
        let updateExplorationFlag = false;
        
        // Check for flags
        if (args['update-exploration']) {
          updateExplorationFlag = true;
        }
        
        for (const arg of args._.slice(1)) {
          const argStr = arg as string;
          if (argStr.startsWith('pattern=')) {
            patternArg = argStr.split('=')[1];
          } else if (argStr !== '--update-exploration') {
            projectArg = argStr;
          }
        }
        
        const specifyArgs: SpecifyArgs = {
          projectName: projectArg,
          pattern: patternArg,
          updateExploration: updateExplorationFlag
        };
        
        await commandFunction(specifyArgs);
        break;
      }
        
      default:
        await commandFunction();
        break;
    }
  } catch (error) {
    logger.error("Command execution failed", error);
    console.log(`❌ Error: ${error instanceof Error ? error.message : String(error)}`);
    Deno.exit(1);
  }
}

if (import.meta.main) {
  main();
}