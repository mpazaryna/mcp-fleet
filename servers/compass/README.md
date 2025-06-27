# Compass - Systematic Project Methodology

Compass is an MCP server that guides projects through a systematic 4-phase methodology designed to prevent superficial work and ensure deep, meaningful outcomes. It enforces thorough exploration before execution, creating lasting value rather than quick wins.

## Philosophy

Modern work environments often reward speed over depth, leading to surface-level solutions that don't address root problems. Compass counters this by enforcing a systematic methodology that ensures proper exploration and specification before any execution begins.

The system is designed to prevent "shiny object syndrome" and shallow AI-generated responses by requiring genuine understanding and thorough planning at each phase.

## Methodology

### Phase 1: Exploration
Deep investigation and understanding of the problem space.

**Purpose**: Develop genuine understanding before proposing solutions
**Activities**: Research, stakeholder interviews, problem analysis, constraint identification
**Outputs**: Rich context documentation, conversation histories, insight summaries
**Completion Criteria**: Comprehensive understanding demonstrated through detailed documentation

**Key Principle**: No solutions allowed - only questions and understanding

### Phase 2: Specification
Transform exploration insights into clear, actionable requirements.

**Purpose**: Create detailed blueprints based on exploration findings
**Activities**: Requirements synthesis, pattern application, specification generation
**Outputs**: Professional requirements documents, technical specifications, acceptance criteria
**Completion Criteria**: Clear, testable specifications that address exploration insights

**Key Principle**: Solutions must be grounded in exploration findings

### Phase 3: Execution
Break down specifications into manageable tasks and execute systematically.

**Purpose**: Deliver working solutions that meet specifications
**Activities**: Task breakdown, priority setting, implementation tracking, progress monitoring
**Outputs**: Completed deliverables, tested implementations, progress reports
**Completion Criteria**: All specification requirements met and validated

**Key Principle**: Stay true to specifications, resist scope creep

### Phase 4: Feedback
Evaluate outcomes and capture learnings for future projects.

**Purpose**: Learn from results and improve methodology
**Activities**: Outcome assessment, stakeholder feedback, lesson extraction, process refinement
**Outputs**: Retrospective reports, methodology improvements, knowledge artifacts
**Completion Criteria**: Clear learnings documented and process improvements identified

## Core Features

### Phase Enforcement
- Cannot skip phases - each must be completed before advancing
- Automatic validation of phase completion criteria
- Prevents premature solution jumping

### Context Preservation
- All conversations and decisions preserved across sessions
- Rich project history maintained for reference
- Systematic knowledge capture and organization

### Pattern-Based Specifications
- Professional templates for different project types
- Automatic specification generation from exploration insights
- Industry-standard requirements documentation

### Task Management
- Context-aware task breakdown from specifications
- Priority-based execution planning
- Progress tracking with completion validation

## Project Types

### Software Development
- Product requirements with user stories
- Technical architecture specifications  
- Implementation plans with testing strategies

### Business Process Analysis
- Current state documentation
- Process improvement recommendations
- Implementation roadmaps

### Strategic Planning
- Situation analysis and stakeholder mapping
- Strategic options evaluation
- Implementation planning with success metrics

### Research Projects
- Literature review and knowledge synthesis
- Research methodology design
- Finding documentation and recommendation development

## Workspace Organization

Each project maintains a structured workspace:
```
project-name/
├── .compass.json           # Project metadata and status
├── exploration/           
│   ├── conversation-*.md   # Exploration sessions
│   └── insights.md        # Key findings summary
├── specification/
│   └── requirements.md    # Generated specifications
├── execution/
│   ├── tasks.json        # Task breakdown and status
│   └── progress.md       # Implementation updates
└── feedback/
    └── retrospective.md  # Lessons learned
```

## MCP Tools

### Project Management
- `init_project`: Create new systematic project
- `list_projects`: View all projects and their status
- `get_project_status`: Detailed project information

### Exploration Tools
- `start_exploration`: Begin systematic investigation
- `save_exploration_session`: Preserve conversation context
- `complete_exploration_phase`: Validate and advance to specification

### Specification Tools  
- `generate_specification`: Create requirements from exploration
- `list_patterns`: View available specification templates
- `get_specification_status`: Review specification completeness

### Execution Tools
- `start_execution`: Break down specifications into tasks
- `list_tasks`: View task breakdown and progress
- `update_task_status`: Track implementation progress

## Value Proposition

Compass transforms chaotic project work into systematic progress. Instead of jumping between ideas or creating superficial solutions, it ensures every project builds on solid understanding and clear requirements.

The result is higher-quality outcomes, reduced rework, and accumulated organizational knowledge that improves over time. Projects feel more purposeful because they address real problems with well-thought solutions.