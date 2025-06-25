export interface Task {
  completed: boolean;
  text: string;
  artifacts?: string[];
}

export interface ProjectMetadata {
  name: string;
  created: string;
  currentPhase: string;
  status: string;
  sessionCount: number;
  lastSessionDate?: string;
  
  // New flywheel properties
  cycleCount?: number;
  currentCycle?: ProjectCycle;
  flywheelIterations?: FlywheelIteration[];
  patterns?: PatternUsage[];
}

export interface ProjectCycle {
  cycleNumber: number;
  purpose: string;
  startDate: string;
  phases: {
    exploration: { completed: boolean; sessions: string[] };
    specification: { completed: boolean; patterns: string[]; version: number };
    execution: { completed: boolean; artifacts: string[] };
    learning: { completed: boolean; insights: string[] };
  };
}

export interface FlywheelIteration {
  iterationId: string;
  triggerPhase: 'exploration' | 'specification' | 'execution';
  triggerReason: string;
  targetPhase: 'exploration' | 'specification';
  gapsIdentified: string[];
  updatedArtifacts: string[];
  newInsights: string[];
  timestamp: string;
}

export interface PatternUsage {
  patternName: string;
  usedAt: string;
  version: number;
  customizations: Record<string, string>;
}

export interface SpecificationPattern {
  name: string;
  domain: string;
  description: string;
  template: string;
  variables: PatternVariable[];
  sections: PatternSection[];
}

export interface PatternVariable {
  name: string;
  description: string;
  required: boolean;
  defaultValue?: string;
}

export interface PatternSection {
  title: string;
  description: string;
  template: string;
  required: boolean;
  explorationMappings: string[]; // Which exploration insights to inject
}

export interface ExplorationInsights {
  userPainPoints: string;
  coreFeatures: string;
  constraints: string;
  goals: string;
  risks: string;
  stakeholders: string;
  successCriteria: string;
  technicalConsiderations: string;
  currentState: string;
  targetState: string;
}