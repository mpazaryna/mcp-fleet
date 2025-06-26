import { z } from "zod";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { exists } from "https://deno.land/std@0.208.0/fs/mod.ts";
import type { MCPTool } from "@packages/mcp-core/mod.ts";
import { ProjectManager } from "../managers/project-manager.ts";

// Temporary local implementations
async function writeFile(args: { path: string; content: string }) {
  const dir = args.path.substring(0, args.path.lastIndexOf("/"));
  await Deno.mkdir(dir, { recursive: true });
  await Deno.writeTextFile(args.path, args.content);
}

async function readFile(path: string): Promise<string> {
  return await Deno.readTextFile(path);
}

// Schema definitions
const GenerateSpecificationInputSchema = z.object({
  project_name: z.string().describe("Project name"),
  pattern: z.string().optional().describe("Specification pattern to use"),
  projectsDir: z.string().optional().describe("Projects directory (for testing)"),
});

const GenerateSpecificationOutputSchema = z.object({
  success: z.boolean(),
  project_name: z.string(),
  pattern_used: z.string(),
  specification_content: z.string(),
  file_path: z.string(),
  insights_extracted: z.object({
    user_pain_points: z.string(),
    core_features: z.string(),
    constraints: z.string(),
    goals: z.string(),
  }),
  error: z.string().optional(),
});

const ListPatternsInputSchema = z.object({});

const ListPatternsOutputSchema = z.object({
  success: z.boolean(),
  patterns: z.array(z.object({
    name: z.string(),
    domain: z.string(),
    description: z.string(),
    variables: z.array(z.string()),
    sections: z.array(z.string()),
  })),
  total: z.number(),
});

const GetSpecificationStatusInputSchema = z.object({
  project_name: z.string().describe("Project name"),
  projectsDir: z.string().optional().describe("Projects directory (for testing)"),
});

const GetSpecificationStatusOutputSchema = z.object({
  project_name: z.string(),
  current_phase: z.string(),
  ready_for_specification: z.boolean(),
  specifications_generated: z.number(),
  specifications: z.array(z.object({
    pattern: z.string(),
    file_path: z.string(),
    created_at: z.string(),
  })),
  next_action: z.string(),
  recommendations: z.array(z.string()),
});

// Tool definitions
export const specificationTools: MCPTool[] = [
  {
    name: "generate_specification",
    description: "Generate pattern-based specification from exploration insights",
    inputSchema: GenerateSpecificationInputSchema,
    outputSchema: GenerateSpecificationOutputSchema,
  },
  {
    name: "list_patterns",
    description: "List available specification patterns for different domains",
    inputSchema: ListPatternsInputSchema,
    outputSchema: ListPatternsOutputSchema,
  },
  {
    name: "get_specification_status",
    description: "Get specification status and generated documents for a project",
    inputSchema: GetSpecificationStatusInputSchema,
    outputSchema: GetSpecificationStatusOutputSchema,
  },
];

// Built-in specification patterns
const BUILT_IN_PATTERNS = [
  {
    name: "software_product_requirements",
    domain: "software",
    description: "Product requirements document for software development",
    variables: ["product_name", "target_users", "core_features", "technical_constraints"],
    sections: ["Overview", "User Stories", "Functional Requirements", "Technical Specifications", "Acceptance Criteria"],
  },
  {
    name: "business_process_analysis",
    domain: "business",
    description: "Business process analysis and improvement documentation",
    variables: ["process_name", "stakeholders", "current_state", "desired_outcomes"],
    sections: ["Current State", "Pain Points", "Proposed Solutions", "Implementation Plan", "Success Metrics"],
  },
  {
    name: "project_planning",
    domain: "general",
    description: "General project planning and execution framework",
    variables: ["project_scope", "timeline", "resources", "deliverables"],
    sections: ["Project Charter", "Scope Definition", "Timeline", "Resource Allocation", "Risk Assessment"],
  },
];

// Helper functions
async function getProjectsDirectory(customDir?: string): Promise<string> {
  if (customDir) return customDir;
  
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE");
  if (!homeDir) {
    throw new Error("Unable to determine user home directory");
  }
  
  const projectsDir = join(homeDir, "CompassProjects");
  await Deno.mkdir(projectsDir, { recursive: true });
  return projectsDir;
}

async function extractInsightsFromExploration(explorationContent: string) {
  // Simple insight extraction - in a real implementation, this could use Claude API
  const insights = {
    user_pain_points: "Pain points identified from exploration sessions",
    core_features: "Core features derived from user needs",
    constraints: "Technical and business constraints discovered",
    goals: "Primary goals and success criteria established",
  };
  
  // Basic text analysis to extract key themes
  const content = explorationContent.toLowerCase();
  
  if (content.includes("user") || content.includes("customer")) {
    insights.user_pain_points = "User experience and customer needs identified in exploration";
  }
  
  if (content.includes("feature") || content.includes("function")) {
    insights.core_features = "Key features and functionality requirements established";
  }
  
  if (content.includes("constraint") || content.includes("limit") || content.includes("requirement")) {
    insights.constraints = "Technical and business constraints documented in exploration";
  }
  
  if (content.includes("goal") || content.includes("objective") || content.includes("success")) {
    insights.goals = "Project goals and success criteria defined through exploration";
  }
  
  return insights;
}

async function generateSpecificationContent(pattern: string, projectName: string, explorationContent: string): Promise<string> {
  const patternConfig = BUILT_IN_PATTERNS.find(p => p.name === pattern);
  if (!patternConfig) {
    throw new Error(`Unknown pattern: ${pattern}`);
  }
  
  const timestamp = new Date().toISOString();
  const insights = await extractInsightsFromExploration(explorationContent);
  
  // Generate specification based on pattern
  switch (pattern) {
    case "software_product_requirements":
      return `# Product Requirements Document
**Project:** ${projectName}
**Generated:** ${timestamp}
**Pattern:** ${pattern}

## 1. Project Overview
Based on exploration sessions, this document outlines the requirements for ${projectName}.

### Key Insights from Exploration
- **User Pain Points:** ${insights.user_pain_points}
- **Core Features:** ${insights.core_features}
- **Constraints:** ${insights.constraints}
- **Goals:** ${insights.goals}

## 2. User Stories
*Derived from exploration conversations*

### Primary User Scenarios
- As a user, I want to accomplish core tasks efficiently
- As a user, I want the system to address my main pain points
- As a user, I want a solution that meets my specific needs

## 3. Functional Requirements
*Based on exploration findings*

### Core Features
1. Primary functionality identified in exploration
2. Secondary features that support user goals
3. Integration requirements discovered

### Technical Requirements
- Performance expectations from exploration
- Scalability requirements identified
- Security and compliance needs

## 4. Technical Specifications
*Constraints and architecture considerations*

### System Architecture
- Technical approach based on exploration constraints
- Integration requirements
- Data management approach

### Implementation Considerations
- Technology choices based on constraints
- Development approach
- Testing strategy

## 5. Acceptance Criteria
*Success criteria from exploration*

### Definition of Done
- Feature completeness criteria
- Quality standards
- User acceptance requirements

### Success Metrics
- Measurable outcomes identified in exploration
- Performance benchmarks
- User satisfaction criteria

---
*Generated from exploration insights using Compass systematic methodology*
`;

    case "business_process_analysis":
      return `# Business Process Analysis
**Project:** ${projectName}
**Generated:** ${timestamp}
**Pattern:** ${pattern}

## 1. Executive Summary
This analysis documents the current state and improvement opportunities for ${projectName}.

### Exploration Insights
- **Current Pain Points:** ${insights.user_pain_points}
- **Process Goals:** ${insights.goals}
- **Identified Constraints:** ${insights.constraints}
- **Improvement Areas:** ${insights.core_features}

## 2. Current State Analysis
*Based on exploration sessions*

### Existing Process Flow
- Current workflow identified in exploration
- Key stakeholders and their roles
- Decision points and bottlenecks

### Pain Points
- Process inefficiencies discovered
- User frustrations documented
- System limitations identified

## 3. Proposed Improvements
*Solutions derived from exploration*

### Process Optimization
- Streamlined workflow design
- Automation opportunities
- Stakeholder experience improvements

### Implementation Approach
- Phased improvement plan
- Change management considerations
- Risk mitigation strategies

## 4. Success Criteria
*Outcomes and metrics from exploration*

### Key Performance Indicators
- Efficiency improvements
- User satisfaction metrics
- Business impact measures

---
*Generated from exploration insights using Compass systematic methodology*
`;

    case "project_planning":
      return `# Project Planning Document
**Project:** ${projectName}
**Generated:** ${timestamp}
**Pattern:** ${pattern}

## 1. Project Charter
*Foundation established through exploration*

### Project Purpose
Based on exploration sessions, ${projectName} aims to address identified needs and opportunities.

### Key Insights
- **Objectives:** ${insights.goals}
- **Scope Elements:** ${insights.core_features}
- **Constraints:** ${insights.constraints}
- **Success Criteria:** ${insights.user_pain_points}

## 2. Scope Definition
*Boundaries and deliverables from exploration*

### In Scope
- Primary deliverables identified
- Key functionality requirements
- Essential project components

### Out of Scope
- Elements explicitly excluded
- Future phase considerations
- Boundary conditions

## 3. Implementation Plan
*Approach derived from exploration*

### Phase Structure
1. **Foundation Phase:** Core infrastructure and setup
2. **Development Phase:** Primary deliverable creation
3. **Integration Phase:** System integration and testing
4. **Deployment Phase:** Go-live and transition

### Timeline Considerations
- Major milestones identified
- Dependencies and prerequisites
- Critical path elements

## 4. Resource Requirements
*Needs identified in exploration*

### Human Resources
- Key roles and responsibilities
- Skill requirements
- Collaboration needs

### Technical Resources
- Infrastructure requirements
- Tool and technology needs
- Integration considerations

## 5. Risk Assessment
*Challenges and mitigation from exploration*

### Identified Risks
- Technical risks discovered
- Business risks identified
- Mitigation strategies

---
*Generated from exploration insights using Compass systematic methodology*
`;

    default:
      throw new Error(`Pattern implementation not found: ${pattern}`);
  }
}

// Tool handlers
export const specificationHandlers = {
  generate_specification: async (args: z.infer<typeof GenerateSpecificationInputSchema>) => {
    const { project_name, pattern = "software_product_requirements", projectsDir: customDir } = args;
    
    try {
      const projectsDir = await getProjectsDirectory(customDir);
      const projectPath = join(projectsDir, project_name);
      
      if (!await exists(projectPath)) {
        return {
          success: false,
          project_name,
          pattern_used: pattern,
          specification_content: "",
          file_path: "",
          insights_extracted: {
            user_pain_points: "",
            core_features: "",
            constraints: "",
            goals: "",
          },
          error: `Project '${project_name}' not found`,
        };
      }
      
      const manager = new ProjectManager(projectPath);
      const metadata = await manager.loadMetadata();
      
      if (!metadata) {
        return {
          success: false,
          project_name,
          pattern_used: pattern,
          specification_content: "",
          file_path: "",
          insights_extracted: {
            user_pain_points: "",
            core_features: "",
            constraints: "",
            goals: "",
          },
          error: "Invalid project metadata",
        };
      }
      
      // Check if exploration is complete
      if (metadata.currentPhase !== "specification") {
        return {
          success: false,
          project_name,
          pattern_used: pattern,
          specification_content: "",
          file_path: "",
          insights_extracted: {
            user_pain_points: "",
            core_features: "",
            constraints: "",
            goals: "",
          },
          error: "Exploration phase not completed. Complete exploration before generating specification.",
        };
      }
      
      // Load exploration content
      const explorationDir = join(projectPath, "exploration");
      let explorationContent = "";
      
      if (await exists(explorationDir)) {
        for await (const entry of Deno.readDir(explorationDir)) {
          if (entry.name.startsWith("conversation-") && entry.name.endsWith(".md")) {
            const content = await readFile(join(explorationDir, entry.name));
            explorationContent += content + "\n\n";
          }
        }
      }
      
      if (!explorationContent.trim()) {
        return {
          success: false,
          project_name,
          pattern_used: pattern,
          specification_content: "",
          file_path: "",
          insights_extracted: {
            user_pain_points: "",
            core_features: "",
            constraints: "",
            goals: "",
          },
          error: "No exploration content found. Complete exploration first.",
        };
      }
      
      // Generate specification
      const specificationContent = await generateSpecificationContent(pattern, project_name, explorationContent);
      const insights = await extractInsightsFromExploration(explorationContent);
      
      // Save specification file
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const fileName = `specification-${pattern}-${timestamp}.md`;
      const filePath = `specification/${fileName}`;
      const fullPath = join(projectPath, filePath);
      
      await writeFile({
        path: fullPath,
        content: specificationContent,
      });
      
      return {
        success: true,
        project_name,
        pattern_used: pattern,
        specification_content: specificationContent,
        file_path: filePath,
        insights_extracted: insights,
      };
    } catch (error) {
      return {
        success: false,
        project_name,
        pattern_used: pattern,
        specification_content: "",
        file_path: "",
        insights_extracted: {
          user_pain_points: "",
          core_features: "",
          constraints: "",
          goals: "",
        },
        error: error instanceof Error ? error.message : String(error),
      };
    }
  },
  
  list_patterns: async () => {
    try {
      return {
        success: true,
        patterns: BUILT_IN_PATTERNS,
        total: BUILT_IN_PATTERNS.length,
      };
    } catch (error) {
      return {
        success: false,
        patterns: [],
        total: 0,
      };
    }
  },
  
  get_specification_status: async (args: z.infer<typeof GetSpecificationStatusInputSchema>) => {
    const { project_name, projectsDir: customDir } = args;
    
    try {
      const projectsDir = await getProjectsDirectory(customDir);
      const projectPath = join(projectsDir, project_name);
      
      if (!await exists(projectPath)) {
        throw new Error(`Project '${project_name}' not found`);
      }
      
      const manager = new ProjectManager(projectPath);
      const metadata = await manager.loadMetadata();
      
      if (!metadata) {
        throw new Error("Invalid project metadata");
      }
      
      // Check specifications directory
      const specDir = join(projectPath, "specification");
      const specifications = [];
      
      if (await exists(specDir)) {
        for await (const entry of Deno.readDir(specDir)) {
          if (entry.name.startsWith("specification-") && entry.name.endsWith(".md")) {
            const match = entry.name.match(/specification-(.+)-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}/);
            const pattern = match ? match[1] : "unknown";
            
            const stat = await Deno.stat(join(specDir, entry.name));
            specifications.push({
              pattern,
              file_path: `specification/${entry.name}`,
              created_at: stat.mtime?.toISOString() || new Date().toISOString(),
            });
          }
        }
      }
      
      const ready_for_specification = metadata.currentPhase === "specification";
      const recommendations = [];
      
      if (!ready_for_specification) {
        recommendations.push("Complete exploration phase before generating specifications");
      } else if (specifications.length === 0) {
        recommendations.push("Generate your first specification using available patterns");
      } else {
        recommendations.push("Review generated specifications and move to execution phase");
      }
      
      return {
        project_name,
        current_phase: metadata.currentPhase,
        ready_for_specification,
        specifications_generated: specifications.length,
        specifications,
        next_action: ready_for_specification 
          ? (specifications.length === 0 ? "generate_specification" : "review_specifications")
          : "complete_exploration",
        recommendations,
      };
    } catch (error) {
      throw error;
    }
  },
};