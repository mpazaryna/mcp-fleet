# Compass Usage Guide

A complete guide to using the Compass MCP server for systematic project methodology. This guide walks you through the complete journey from initial project ideas to actionable execution plans.

## Table of Contents
- [Quick Start](#quick-start)
- [Understanding Compass Methodology](#understanding-compass-methodology)
- [Complete Project Workflow](#complete-project-workflow)
- [Phase-by-Phase Guide](#phase-by-phase-guide)
- [Best Practices](#best-practices)
- [File Organization](#file-organization)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. First Time Setup
Make sure your Compass server is running with Docker volume mounting enabled. Your projects will be stored in the persistent workspace.

### 2. Initialize Your First Project
```
Ask Claude: "Initialize a new project called 'mobile-app-prototype' for building a task management mobile app"
```

Expected response: Claude will use the `init_project` tool and return something like:
```
✅ Project 'mobile-app-prototype' initialized successfully
📁 Project structure created
🎯 Current phase: Exploration
📋 Ready to begin systematic exploration
```

### 3. Start Exploration Phase
```
Ask Claude: "Start exploration for mobile-app-prototype project"
```

Expected response:
```
🔍 Exploration started for mobile-app-prototype
📝 Session 1 initialized
🎯 Ready for systematic exploration conversation
💡 Begin by sharing your initial ideas, goals, and requirements
```

## Understanding Compass Methodology

Compass follows a **systematic 4-phase methodology** designed to prevent shallow, surface-level solutions:

### 🔍 **Phase 1: Exploration**
- **Purpose**: Deep discovery and requirement gathering
- **Prevents**: Jumping to solutions too quickly
- **Enforces**: Multiple exploration sessions with context building
- **Output**: Comprehensive conversation history and insights

### 📋 **Phase 2: Specification** 
- **Purpose**: Structured requirements documentation
- **Prevents**: Building without clear specifications
- **Enforces**: Pattern-based specification generation from exploration
- **Output**: Professional requirements documents

### ⚙️ **Phase 3: Execution**
- **Purpose**: Actionable task breakdown and planning
- **Prevents**: Overwhelming or unfocused implementation
- **Enforces**: Context-aware task generation with priorities
- **Output**: Detailed execution plans and task lists

### 🔄 **Phase 4: Feedback** *(Coming Soon)*
- **Purpose**: Learning and iteration cycles
- **Prevents**: One-and-done mentality
- **Enforces**: Systematic reflection and improvement
- **Output**: Lessons learned and next iteration plans

## Complete Project Workflow

### Example: Building an AI Productivity Assistant

#### Phase 1: Exploration Sessions
```
Session 1: "I want to build an AI productivity assistant. What should I explore?"
→ Core functionality, target users, technical considerations

Session 2: "Focus on knowledge workers in consulting. Privacy-first with local LLMs."
→ Deep dive on specific requirements, architecture, implementation

Complete: "Mark exploration complete - covered user needs, technical architecture, and scope"
→ Automatic transition to Specification phase
```

#### Phase 2: Specification Generation
```
"Generate a software product requirements specification from my exploration"
→ Pattern-based PRD created with user stories, technical specs, acceptance criteria

"Show me the specification status"
→ Review generated documents and completion status
```

#### Phase 3: Execution Planning
```
"Start execution phase and create implementation plan"
→ Task breakdown with categories: setup, backend, frontend, testing, deployment

"List all execution tasks with priorities"
→ View actionable task list with estimated hours and status tracking

"Update task 'Setup development environment' to completed"
→ Track progress and maintain momentum
```

## Phase-by-Phase Guide

### 🔍 Exploration Phase

**Key Commands:**
- `"Start exploration for [project-name]"` - Initialize exploration session
- `"Save this exploration session with summary: [your summary]"` - Preserve insights
- `"Get project context for [project-name]"` - Review conversation history
- `"Complete exploration phase because [reason]"` - Transition to specification

**Best Practices:**
- **Have multiple sessions** - Don't rush through exploration
- **Build context gradually** - Each session should deepen understanding
- **Be specific about completion** - Clearly state why exploration is sufficient
- **Cover key areas**: User needs, technical constraints, business goals, success criteria

**Example Flow:**
```
1. Start with broad questions: "What problem am I solving? For whom?"
2. Dive deeper: "What are the technical constraints and requirements?"
3. Explore edge cases: "What could go wrong? What are the risks?"
4. Validate scope: "Is this feasible? What's the MVP vs nice-to-have?"
5. Complete when you have clear answers to core questions
```

### 📋 Specification Phase

**Key Commands:**
- `"List available specification patterns"` - See available templates
- `"Generate specification using [pattern] for [project-name]"` - Create requirements document
- `"Get specification status for [project-name]"` - Check phase progress

**Available Patterns:**
- **software_product_requirements** - Full PRD for software projects
- **business_process_improvement** - Process optimization specifications
- **project_planning** - General project planning framework

**Best Practices:**
- **Choose appropriate patterns** based on your project type
- **Review generated specifications** carefully for completeness
- **Iterate if needed** - specifications can be regenerated with different patterns

### ⚙️ Execution Phase

**Key Commands:**
- `"Start execution phase for [project-name]"` - Generate execution plan and tasks
- `"List execution tasks"` - View all tasks
- `"List tasks with status pending"` - Filter by status
- `"List tasks in category setup"` - Filter by category
- `"Update task [task-id] to completed with notes: [notes]"` - Track progress

**Task Categories:**
- **setup** - Environment and project initialization
- **database** - Data schema and persistence
- **backend** - APIs and business logic
- **frontend** - User interface components
- **testing** - Quality assurance
- **deployment** - Infrastructure and CI/CD
- **documentation** - Project documentation

**Best Practices:**
- **Start with setup tasks** - Establish development environment first
- **Update status regularly** - Maintain accurate progress tracking
- **Add detailed notes** - Document insights and decisions
- **Break down large tasks** - Add subtasks if needed

## Best Practices

### 🎯 **Methodology Discipline**
- **Don't skip phases** - Each phase builds on the previous
- **Be thorough in exploration** - Surface-level exploration leads to weak specifications
- **Document decisions** - Capture the "why" behind choices
- **Iterate when needed** - Not every project gets it right the first time

### 💡 **Effective Exploration**
- **Ask "why" repeatedly** - Get to root motivations and constraints
- **Consider multiple perspectives** - Users, developers, stakeholders, competitors
- **Explore failure modes** - What could go wrong? How to mitigate?
- **Define success clearly** - What does "done" look like?

### 📝 **Quality Specifications**
- **Use concrete language** - Avoid vague requirements
- **Include acceptance criteria** - How will you know it's working?
- **Specify non-functional requirements** - Performance, security, scalability
- **Plan for change** - What might need to evolve?

### 🚀 **Successful Execution**
- **Prioritize ruthlessly** - Focus on high-impact tasks first
- **Track progress visibly** - Regular status updates maintain momentum
- **Celebrate milestones** - Acknowledge completed phases and major tasks
- **Learn from setbacks** - Document challenges and solutions

## File Organization

Compass creates a structured workspace for each project:

```
workspace/
└── your-project-name/
    ├── .compass.json          # Project metadata and phase tracking
    ├── tasks.md              # High-level phase checklist
    ├── exploration/          # All exploration sessions
    │   ├── conversation-1.md
    │   ├── conversation-2.md
    │   └── completion-override.md
    ├── specification/        # Generated requirements documents
    │   └── specification-[pattern]-[timestamp].md
    ├── execution/           # Implementation planning
    │   ├── execution-plan.md
    │   └── tasks.json
    └── feedback/           # Lessons learned and iteration plans
        └── (coming soon)
```

### Key Files:
- **`.compass.json`** - Project state, phase transitions, completion dates
- **`conversation-*.md`** - Exploration session records with full context
- **`specification-*.md`** - Requirements documents generated from exploration
- **`execution-plan.md`** - Human-readable implementation roadmap
- **`tasks.json`** - Machine-readable task list with status tracking

## Advanced Features

### Project Status Monitoring
```
"Get project status for [project-name]"
→ Current phase, completion status, next recommended actions
```

### Cross-Project Learning
- Review completed projects for patterns and lessons
- Use successful exploration approaches for similar projects
- Build personal methodology refinements over time

### Custom Specification Patterns
- Future versions will support custom specification templates
- Organization-specific requirement patterns
- Domain-specific methodology adaptations

## Troubleshooting

### Common Issues:

**"Can't start specification without completing exploration"**
- Ensure exploration phase is marked complete
- Use: `"Complete exploration phase because [detailed reason]"`

**"No exploration content found"**
- Verify you've saved exploration sessions
- Check project name spelling
- Ensure you're in the correct workspace

**"Execution tasks seem generic"**
- Provide more detailed exploration sessions
- Include specific technical requirements and constraints
- Consider regenerating specification with more context

**"Task updates not persisting"**
- Verify correct task ID (use `"List tasks"` to see IDs)
- Ensure proper task status values: pending, in_progress, completed, blocked

### Getting Help:
- **Check project status**: Always start with understanding current phase
- **Review conversation history**: Use `"Get project context"` to see what's been covered
- **Validate file structure**: Ensure all expected directories and files exist
- **Start small**: Test with simple projects before complex ones

---

*Compass enforces systematic thinking to prevent AI from producing shallow, surface-level solutions. The methodology creates necessary friction to force genuine depth and thoughtful progression through project phases.*