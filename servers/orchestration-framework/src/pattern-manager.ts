import { exists } from "@std/fs";
import { join, dirname } from "@std/path";
import { parse as parseYaml } from "@std/yaml";
import { SpecificationPattern, PatternVariable, PatternSection, ExplorationInsights } from "./types.ts";
import { logger } from "./logger.ts";

export class PatternManager {
  private patternsDir: string;

  constructor() {
    // Get the directory where this script is located
    const scriptDir = dirname(new URL(import.meta.url).pathname);
    // Patterns directory is relative to project root
    this.patternsDir = join(dirname(scriptDir), 'patterns');
  }

  async loadAvailablePatterns(): Promise<SpecificationPattern[]> {
    logger.debug("Loading available patterns from filesystem");
    
    const patterns: SpecificationPattern[] = [];
    
    try {
      // Scan pattern directories
      const domains = ['software', 'business', 'personal', 'framework'];
      
      for (const domain of domains) {
        const domainDir = join(this.patternsDir, domain);
        
        if (await exists(domainDir)) {
          for await (const entry of Deno.readDir(domainDir)) {
            if (entry.isFile && entry.name.endsWith('.md')) {
              try {
                const patternPath = join(domainDir, entry.name);
                const pattern = await this.loadPatternFromFile(patternPath, domain);
                if (pattern) {
                  patterns.push(pattern);
                }
              } catch (error) {
                logger.warn(`Failed to load pattern ${entry.name}`, error);
              }
            }
          }
        }
      }
      
      logger.debug(`Loaded ${patterns.length} patterns`);
      return patterns;
      
    } catch (error) {
      logger.error("Failed to load patterns", error);
      return [];
    }
  }

  async loadPattern(patternName: string): Promise<SpecificationPattern | null> {
    logger.debug(`Loading pattern: ${patternName}`);
    
    try {
      const patterns = await this.loadAvailablePatterns();
      const pattern = patterns.find(p => p.name === patternName);
      
      if (!pattern) {
        logger.warn(`Pattern not found: ${patternName}`);
        return null;
      }
      
      return pattern;
    } catch (error) {
      logger.error(`Failed to load pattern ${patternName}`, error);
      return null;
    }
  }

  private async loadPatternFromFile(filePath: string, domain: string): Promise<SpecificationPattern | null> {
    try {
      const content = await Deno.readTextFile(filePath);
      
      // Parse frontmatter and content
      const { frontmatter, template } = this.parseFrontmatter(content);
      
      if (!frontmatter.name) {
        logger.warn(`Pattern file missing name: ${filePath}`);
        return null;
      }
      
      return {
        name: frontmatter.name,
        domain: frontmatter.domain || domain,
        description: frontmatter.description || '',
        template,
        variables: frontmatter.variables || [],
        sections: frontmatter.sections || []
      };
      
    } catch (error) {
      logger.warn(`Failed to parse pattern file ${filePath}`, error);
      return null;
    }
  }

  private parseFrontmatter(content: string): { frontmatter: any, template: string } {
    const lines = content.split('\n');
    
    // Check if content has frontmatter (starts with ---)
    if (lines[0] !== '---') {
      return { frontmatter: {}, template: content };
    }
    
    // Find end of frontmatter
    let frontmatterEnd = -1;
    for (let i = 1; i < lines.length; i++) {
      if (lines[i] === '---') {
        frontmatterEnd = i;
        break;
      }
    }
    
    if (frontmatterEnd === -1) {
      logger.warn("Frontmatter started but no closing --- found");
      return { frontmatter: {}, template: content };
    }
    
    // Extract frontmatter and template
    const frontmatterContent = lines.slice(1, frontmatterEnd).join('\n');
    const template = lines.slice(frontmatterEnd + 1).join('\n');
    
    // Parse YAML frontmatter
    try {
      const frontmatter = parseYaml(frontmatterContent) as any;
      logger.debug("YAML frontmatter parsed successfully");
      return { frontmatter: frontmatter || {}, template };
    } catch (error) {
      logger.error("Failed to parse YAML frontmatter", error);
      throw new Error(`Invalid YAML frontmatter: ${error instanceof Error ? error.message : String(error)}`);
    }
  }


  substituteVariables(template: string, variables: Record<string, string>): string {
    let result = template;
    
    for (const [key, value] of Object.entries(variables)) {
      const placeholder = `{{${key}}}`;
      result = result.replaceAll(placeholder, value);
    }
    
    return result;
  }

  async extractInsights(explorationContent: string): Promise<ExplorationInsights> {
    logger.debug("Extracting insights from exploration content");
    
    // Context-aware extraction that looks for Q&A pairs
    const insights: ExplorationInsights = {
      userPainPoints: this.extractContextualAnswer(explorationContent, ['pain', 'problem', 'issue', 'struggle', 'difficulty']),
      coreFeatures: this.extractContextualAnswer(explorationContent, ['feature', 'functionality', 'need', 'want', 'require']),
      constraints: this.extractSection(explorationContent, ['constraint', 'limitation', 'budget', 'time', 'resource']),
      goals: this.extractSection(explorationContent, ['goal', 'objective', 'want to', 'trying to', 'hoping to']),
      risks: this.extractSection(explorationContent, ['risk', 'concern', 'worry', 'might fail', 'could go wrong']),
      stakeholders: this.extractSection(explorationContent, ['stakeholder', 'user', 'customer', 'team', 'person']),
      successCriteria: this.extractSection(explorationContent, ['success', 'measure', 'metric', 'KPI', 'indicator']),
      technicalConsiderations: this.extractSection(explorationContent, ['technical', 'technology', 'system', 'architecture', 'performance']),
      currentState: this.extractSection(explorationContent, ['currently', 'now', 'existing', 'present', 'today']),
      targetState: this.extractSection(explorationContent, ['target', 'future', 'desired', 'want to be', 'goal state'])
    };
    
    return insights;
  }

  private extractContextualAnswer(content: string, keywords: string[]): string {
    // Look for Q&A patterns where question contains keywords and extract the answer
    const lines = content.split('\n');
    const relevantAnswers: string[] = [];
    
    for (let i = 0; i < lines.length - 1; i++) {
      const currentLine = lines[i].toLowerCase();
      
      // Check if current line is a question with our keywords
      const hasKeyword = keywords.some(keyword => currentLine.includes(keyword.toLowerCase()));
      const isQuestion = currentLine.includes('**claude**:') || currentLine.includes('?');
      
      if (hasKeyword && isQuestion) {
        // Look for the next "**You**:" response
        for (let j = i + 1; j < lines.length; j++) {
          const nextLine = lines[j];
          if (nextLine.toLowerCase().includes('**you**:')) {
            relevantAnswers.push(nextLine.trim());
            break;
          }
        }
      }
    }
    
    // Fall back to regular extraction if no Q&A patterns found
    if (relevantAnswers.length === 0) {
      return this.extractSection(content, keywords);
    }
    
    return relevantAnswers.join(' ').trim();
  }

  private extractSection(content: string, keywords: string[]): string {
    const lines = content.split('\n');
    const relevantLines: string[] = [];
    const lowerContent = content.toLowerCase();
    
    // First, try to find lines that contain keywords
    for (const line of lines) {
      const lowerLine = line.toLowerCase();
      for (const keyword of keywords) {
        if (lowerLine.includes(keyword.toLowerCase())) {
          // Get the original case line, not lowercase
          relevantLines.push(line.trim());
          break;
        }
      }
    }
    
    // If no direct matches, try broader pattern matching
    if (relevantLines.length === 0) {
      for (const keyword of keywords) {
        if (lowerContent.includes(keyword.toLowerCase())) {
          // Find context around the keyword
          const sentences = content.split(/[.!?]+/);
          for (const sentence of sentences) {
            if (sentence.toLowerCase().includes(keyword.toLowerCase())) {
              relevantLines.push(sentence.trim());
            }
          }
        }
      }
    }
    
    return relevantLines.length > 0 
      ? relevantLines.join(' ').trim() 
      : 'No specific information identified from exploration.';
  }

  async generateSpecification(
    patternName: string,
    projectName: string,
    explorationContent: string
  ): Promise<string> {
    logger.debug(`Generating specification using pattern: ${patternName}`);
    
    const pattern = await this.loadPattern(patternName);
    if (!pattern) {
      throw new Error(`Pattern not found: ${patternName}`);
    }
    
    const insights = await this.extractInsights(explorationContent);
    
    // Create variable substitution map
    const variables: Record<string, string> = {
      PROJECT_NAME: projectName,
      EXPLORATION_INSIGHTS: explorationContent,
      
      // Map insights to template variables
      USER_PAIN_POINTS: insights.userPainPoints,
      CORE_FEATURES: insights.coreFeatures,
      CONSTRAINTS: insights.constraints,
      GOALS: insights.goals,
      RISKS: insights.risks,
      STAKEHOLDERS: insights.stakeholders,
      SUCCESS_CRITERIA: insights.successCriteria,
      TECHNICAL_CONSIDERATIONS: insights.technicalConsiderations,
      CURRENT_STATE: insights.currentState,
      TARGET_STATE: insights.targetState
    };
    
    // Substitute variables in template
    const specification = this.substituteVariables(pattern.template, variables);
    
    logger.debug("Specification generated successfully");
    return specification;
  }
}