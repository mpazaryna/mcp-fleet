import { exists } from "@std/fs";
import { FlywheelIteration, ProjectMetadata } from "./types.ts";
import { ProjectManager } from "./project-manager.ts";
import { logger } from "./logger.ts";

export class FlywheelManager {
  
  /**
   * Analyze gaps between exploration and specification phases
   * Returns areas that need additional exploration or specification refinement
   */
  async analyzeGaps(projectMetadata: ProjectMetadata): Promise<string[]> {
    logger.debug("Analyzing gaps between exploration and specification");
    
    const gaps: string[] = [];
    
    try {
      // Load exploration content
      const explorationContent = await this.loadExplorationContent();
      
      // Load specification content if it exists
      const specificationContent = await this.loadSpecificationContent();
      
      if (!explorationContent) {
        gaps.push("No exploration content found - exploration phase incomplete");
        return gaps;
      }
      
      // Only flag missing specification as a gap if we're in a later phase
      // or if this is explicitly a flywheel iteration request
      if (!specificationContent) {
        // If we're still in exploration phase and haven't started specification yet,
        // this is not a gap - it's the expected state
        if (projectMetadata.currentPhase === "exploration") {
          // No gaps - this is normal for exploration phase
          return gaps;
        } else {
          // If we're past exploration phase, missing specification is indeed a gap
          gaps.push("No specification content found - specification phase not started");
          return gaps;
        }
      }
      
      // Analyze content gaps using keyword-based heuristics
      const explorationGaps = this.findExplorationGaps(explorationContent, specificationContent);
      const specificationGaps = this.findSpecificationGaps(explorationContent, specificationContent);
      
      gaps.push(...explorationGaps);
      gaps.push(...specificationGaps);
      
      logger.debug(`Found ${gaps.length} gaps in analysis`);
      return gaps;
      
    } catch (error) {
      logger.error("Failed to analyze gaps", error);
      return ["Error analyzing gaps - unable to compare phases"];
    }
  }
  
  /**
   * Create a new flywheel iteration when gaps are identified
   */
  async createFlywheelIteration(
    triggerPhase: 'exploration' | 'specification' | 'execution',
    triggerReason: string,
    targetPhase: 'exploration' | 'specification',
    gapsIdentified: string[]
  ): Promise<FlywheelIteration> {
    
    const iteration: FlywheelIteration = {
      iterationId: `flywheel-${Date.now()}`,
      triggerPhase,
      triggerReason,
      targetPhase,
      gapsIdentified,
      updatedArtifacts: [],
      newInsights: [],
      timestamp: new Date().toISOString()
    };
    
    logger.info(`Created flywheel iteration: ${iteration.iterationId}`);
    return iteration;
  }
  
  /**
   * Update project metadata with flywheel iteration
   */
  async recordFlywheelIteration(iteration: FlywheelIteration): Promise<void> {
    const metadata = await ProjectManager.getProjectMetadata();
    if (!metadata) {
      throw new Error("Project metadata not found");
    }
    
    if (!metadata.flywheelIterations) {
      metadata.flywheelIterations = [];
    }
    
    metadata.flywheelIterations.push(iteration);
    
    // Update cycle count
    metadata.cycleCount = (metadata.cycleCount || 0) + 1;
    
    await ProjectManager.updateProjectMetadata(metadata);
    logger.info(`Recorded flywheel iteration: ${iteration.iterationId}`);
  }
  
  /**
   * Generate recommendations for addressing identified gaps
   */
  generateGapRecommendations(gaps: string[]): string[] {
    const recommendations: string[] = [];
    
    for (const gap of gaps) {
      const lowerGap = gap.toLowerCase();
      
      if (lowerGap.includes('user') || lowerGap.includes('stakeholder')) {
        recommendations.push("Conduct additional user research and stakeholder interviews");
      }
      
      if (lowerGap.includes('technical') || lowerGap.includes('architecture')) {
        recommendations.push("Explore technical architecture and implementation details");
      }
      
      if (lowerGap.includes('requirement') || lowerGap.includes('feature')) {
        recommendations.push("Clarify functional and non-functional requirements");
      }
      
      if (lowerGap.includes('risk') || lowerGap.includes('constraint')) {
        recommendations.push("Identify and assess project risks and constraints");
      }
      
      if (lowerGap.includes('metric') || lowerGap.includes('success')) {
        recommendations.push("Define clear success metrics and measurement criteria");
      }
      
      if (lowerGap.includes('timeline') || lowerGap.includes('schedule')) {
        recommendations.push("Establish realistic timeline and milestone planning");
      }
    }
    
    // Add generic recommendations if no specific ones found
    if (recommendations.length === 0) {
      recommendations.push("Review and expand exploration in areas identified as incomplete");
      recommendations.push("Cross-reference specification against exploration insights");
    }
    
    return recommendations;
  }
  
  /**
   * Check if a flywheel iteration is recommended based on current project state
   */
  async recommendFlywheelIteration(): Promise<{
    recommended: boolean;
    reason?: string;
    targetPhase?: 'exploration' | 'specification';
    gaps: string[];
  }> {
    
    const metadata = await ProjectManager.getProjectMetadata();
    if (!metadata) {
      return { recommended: false, gaps: [] };
    }
    
    const gaps = await this.analyzeGaps(metadata);
    
    if (gaps.length === 0) {
      return { recommended: false, gaps: [] };
    }
    
    // Determine target phase based on gap types
    const hasExplorationGaps = gaps.some(gap => 
      gap.toLowerCase().includes('exploration') || 
      gap.toLowerCase().includes('unclear') ||
      gap.toLowerCase().includes('missing context')
    );
    
    const hasSpecificationGaps = gaps.some(gap =>
      gap.toLowerCase().includes('specification') ||
      gap.toLowerCase().includes('requirement') ||
      gap.toLowerCase().includes('detail')
    );
    
    if (hasExplorationGaps) {
      return {
        recommended: true,
        reason: "Exploration gaps identified that need additional investigation",
        targetPhase: 'exploration',
        gaps
      };
    }
    
    if (hasSpecificationGaps) {
      return {
        recommended: true,
        reason: "Specification gaps identified that need refinement",
        targetPhase: 'specification', 
        gaps
      };
    }
    
    return {
      recommended: true,
      reason: "General gaps identified between phases",
      targetPhase: 'exploration', // Default to exploration for unknown gap types
      gaps
    };
  }
  
  private async loadExplorationContent(): Promise<string> {
    const conversations: string[] = [];
    
    try {
      if (!await exists('exploration')) {
        return "";
      }
      
      for await (const entry of Deno.readDir('exploration')) {
        if (entry.name.startsWith('conversation-') && entry.name.endsWith('.md')) {
          const content = await Deno.readTextFile(`exploration/${entry.name}`);
          conversations.push(content);
        }
      }
      
      return conversations.join('\n\n---\n\n');
    } catch (error) {
      logger.warn("Failed to load exploration content", error);
      return "";
    }
  }
  
  private async loadSpecificationContent(): Promise<string> {
    const specifications: string[] = [];
    
    try {
      if (!await exists('specification')) {
        return "";
      }
      
      for await (const entry of Deno.readDir('specification')) {
        if (entry.name.endsWith('.md')) {
          const content = await Deno.readTextFile(`specification/${entry.name}`);
          specifications.push(content);
        }
      }
      
      return specifications.join('\n\n---\n\n');
    } catch (error) {
      logger.warn("Failed to load specification content", error);
      return "";
    }
  }
  
  private findExplorationGaps(explorationContent: string, specificationContent: string): string[] {
    const gaps: string[] = [];
    
    // Check if specification mentions concepts not explored
    const specWords = this.extractKeywords(specificationContent);
    const explorationWords = this.extractKeywords(explorationContent);
    
    const criticalKeywords = [
      'user', 'customer', 'stakeholder', 'requirement', 'feature',
      'technical', 'architecture', 'performance', 'security',
      'risk', 'constraint', 'timeline', 'budget', 'resource'
    ];
    
    for (const keyword of criticalKeywords) {
      const inSpec = specWords.some(word => word.includes(keyword));
      const inExploration = explorationWords.some(word => word.includes(keyword));
      
      if (inSpec && !inExploration) {
        gaps.push(`Specification mentions ${keyword} but exploration lacks sufficient detail`);
      }
    }
    
    // Check for vague or unclear exploration content
    if (explorationContent.length < 500) {
      gaps.push("Exploration content is too brief - may need deeper investigation");
    }
    
    const questionCount = (explorationContent.match(/\?/g) || []).length;
    const answerCount = (explorationContent.match(/\*\*You\*\*:/g) || []).length;
    
    if (questionCount > answerCount * 2) {
      gaps.push("Many questions in exploration remain unanswered");
    }
    
    return gaps;
  }
  
  private findSpecificationGaps(explorationContent: string, specificationContent: string): string[] {
    const gaps: string[] = [];
    
    // Check if exploration insights are properly captured in specification
    const explorationInsights = this.extractInsights(explorationContent);
    const specificationCoverage = this.checkSpecificationCoverage(specificationContent, explorationInsights);
    
    if (specificationCoverage.missingAreas.length > 0) {
      gaps.push(`Specification missing coverage for: ${specificationCoverage.missingAreas.join(', ')}`);
    }
    
    // Check for technical detail gaps
    if (explorationContent.toLowerCase().includes('technical') && 
        !specificationContent.toLowerCase().includes('architecture')) {
      gaps.push("Exploration mentions technical aspects but specification lacks architectural details");
    }
    
    // Check for requirement completeness
    if (explorationContent.toLowerCase().includes('feature') &&
        !specificationContent.toLowerCase().includes('requirement')) {
      gaps.push("Features discussed in exploration but requirements not fully specified");
    }
    
    return gaps;
  }
  
  private extractKeywords(content: string): string[] {
    return content.toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 3)
      .filter(word => /^[a-z]+$/.test(word));
  }
  
  private extractInsights(content: string): string[] {
    const insights: string[] = [];
    
    // Look for key insight patterns
    const patterns = [
      /\*\*You\*\*:([^*]+)/g,
      /problem[s]?[:\s]+([^.!?]+)/gi,
      /need[s]?[:\s]+([^.!?]+)/gi,
      /goal[s]?[:\s]+([^.!?]+)/gi,
      /challenge[s]?[:\s]+([^.!?]+)/gi
    ];
    
    for (const pattern of patterns) {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        insights.push(match[1].trim());
      }
    }
    
    return insights;
  }
  
  private checkSpecificationCoverage(specification: string, insights: string[]): {
    coveredAreas: string[];
    missingAreas: string[];
  } {
    const covered: string[] = [];
    const missing: string[] = [];
    
    const specLower = specification.toLowerCase();
    
    for (const insight of insights) {
      const insightWords = insight.toLowerCase().split(/\s+/).filter(word => word.length > 3);
      const hasKeywords = insightWords.some(word => specLower.includes(word));
      
      if (hasKeywords) {
        covered.push(insight);
      } else {
        missing.push(insight);
      }
    }
    
    return { coveredAreas: covered, missingAreas: missing };
  }
}