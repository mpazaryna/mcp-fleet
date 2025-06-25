# ORCHESTRATION-FRAMEWORK(1) Man Page

## NAME
orchestration-framework - systematic project methodology tools for Claude Desktop

## SYNOPSIS
Conversational interface for 4-phase project methodology:
**Exploration → Specification → Execution → Feedback**

```
get_man_page([section])
```

## DESCRIPTION
The Orchestration Framework is a systematic methodology for knowledge work that combines human strategic thinking with AI execution capabilities. It prevents "brilliant surface solutions" by ensuring thorough problem exploration before execution.

The framework implements a **4-phase process**:
1. **Exploration** - Systematic investigation of the problem space
2. **Specification** - Transform insights into structured requirements  
3. **Execution** - Implement solutions based on solid understanding
4. **Feedback & Learning** - Capture knowledge for future projects

All tools are accessible through the Model Context Protocol (MCP) in Claude Desktop, enabling natural conversation-based project management.

## COMMANDS

### Project Management
- **`init_project(name)`**
  Initialize a new Orchestration Framework project with systematic methodology structure.
  Creates project directory at `~/OrchestrationProjects/{name}` with 4-phase structure.
  
- **`list_projects()`**
  List all available Orchestration Framework projects with status information.
  Shows project names, phases, session counts, and task completion status.
  
- **`get_project_status(project_name?)`**
  Get detailed status of a specific project including tasks and recommendations.
  If no project specified, uses current directory context.

### Exploration Phase
- **`start_exploration(project_name?, focus_area?)`**
  Begin or continue systematic exploration phase for a project.
  Provides methodology guidance and loads previous conversation context.
  
- **`save_exploration_session(project_name, conversation_content, summary?)`**
  Save exploration conversation content to project files for later specification generation.
  Creates timestamped conversation files in `exploration/` directory.
  
- **`complete_exploration_phase(project_name, completion_reason?)`**
  Mark exploration phase as complete even with remaining tasks, enabling specification generation.
  Records completion reasoning and marks all exploration tasks complete.

### Conversation Continuity
- **`get_project_context(project_name)`**
  Load full conversation history and context for a project to enable continuation.
  Returns conversation history, key insights, and context for resuming work.

### Specification Generation
- **`generate_specification(project_name?, pattern?)`**
  Generate pattern-based specification from exploration insights.
  Uses exploration conversations to create structured requirements documents.
  
- **`list_patterns()`**
  List available specification patterns for different domains.
  Shows patterns for software development, business processes, and personal development.

### Gap Analysis & Improvement
- **`check_flywheel_opportunities(project_name?)`**
  Analyze project for gaps and recommend flywheel iterations.
  Identifies missing exploration areas and suggests recursive improvement cycles.

### Learning & Onboarding
- **`get_framework_lesson(lesson_topic?, lesson_level?)`**
  Get interactive lesson content about the Orchestration Framework methodology using Feynman teaching method.
  Available topics: methodology-overview, exploration-techniques.
  Levels: beginner, intermediate, advanced.

### Feedback & Learning Capture
- **`write_feedback(project_name, feedback_content, feedback_type?, session_reference?)`**
  Write feedback, shutdown notes, or reflections to the project's feedback folder.
  Types: shutdown-note, retrospective, reflection, learning. Creates timestamped files in `feedback/` directory.

### Documentation
- **`get_man_page(section?)`**
  Display this manual page or specific sections.
  Sections: commands, examples, methodology, files.

## EXAMPLES

### Starting a New Project
```
User: I want to systematically approach improving our customer onboarding process

Claude: I'll initialize an Orchestration Framework project for this.
[calls init_project("customer-onboarding-improvement")]

✅ Project initialized with 4-phase methodology
📍 Project location: ~/OrchestrationProjects/customer-onboarding-improvement
🎯 Next: Begin systematic exploration phase
```

### Conducting Exploration
```
User: Let's start exploring the onboarding problems

Claude: [calls start_exploration("customer-onboarding-improvement")]

🔍 Ready to begin exploration session 1
Focus: Complete initial problem exploration
Guidance: We are in the EXPLORATION phase - focus on understanding 
the problem space through systematic questioning.
```

### Resuming Previous Work
```
User: Let's continue my onboarding project from last week

Claude: [calls get_project_context("customer-onboarding-improvement")]

Welcome back! I see we've had 3 exploration sessions.
Key insights discovered:
• SMS verification causing 40% drop-off (Session 1)
• Mobile UX needs specific attention (Session 2)  
• Users want progress indicators (Session 3)

Ready to generate specification or explore further?
```

### Moving to Specification
```
User: I think we have enough insights. Let's create a specification.

Claude: [calls complete_exploration_phase("customer-onboarding-improvement", 
         "Sufficient insights on user pain points and technical constraints")]

✅ Exploration phase marked complete
📋 Ready to generate specification

[calls generate_specification("customer-onboarding-improvement", "product_requirement_doc")]

✅ Specification generated: specification/spec-product_requirement_doc-*.md
```

### Capturing Shutdown Notes and Reflections
```
User: I want to record my shutdown notes for today's time management session

Claude: [calls write_feedback("time-management-improvement-1750621704305", 
         "Today's session was highly productive. We identified key time blocks for deep work and established shutdown rituals. Key insights: Morning energy is best for strategic work, afternoon better for administrative tasks. Need to implement strict email boundaries.", 
         "shutdown-note", "Session 4")]

✅ Shutdown-note feedback saved successfully
📝 Feedback captured in feedback/shutdown-note-*.md
🔄 Available for future project retrospectives
```

### Learning the Framework
```
User: I'm new to this methodology. Can you teach me?

Claude: [calls get_framework_lesson("methodology-overview", "beginner")]

🎓 ORCHESTRATION FRAMEWORK LESSON: Understanding the 4-Phase Methodology

## The Core Problem We're Solving
Imagine you're building a bridge. Most people would immediately start 
designing the bridge structure...
[Full lesson content]
```

## METHODOLOGY

### 4-Phase Process
1. **🔍 Exploration**: Systematic investigation prevents jumping to solutions
2. **📋 Specification**: Transform insights using proven patterns  
3. **🎯 Execution**: Implement with clear requirements and constraints
4. **🔄 Feedback**: Capture learning for compound intelligence

### Key Principles
- **Time is Not an Artifact**: Phases complete when purpose is fulfilled
- **Systematic Before Reactive**: No shortcuts to execution without proper exploration
- **Real Integration from Start**: Production requirements from beginning
- **Documentation as Asset**: Conversations become organizational knowledge

### Flywheel Iterations
The framework includes automatic gap detection that identifies when exploration is insufficient for specification requirements, triggering additional exploration cycles.

## FILES
- **`~/OrchestrationProjects/`** - Default project storage location
- **`{project}/exploration/`** - Conversation history and exploration artifacts
- **`{project}/specification/`** - Generated specifications and requirements
- **`{project}/execution/`** - Implementation artifacts  
- **`{project}/feedback/`** - Learning capture and retrospectives
- **`{project}/.orchestration.json`** - Project metadata and session tracking
- **`{project}/tasks.md`** - Phase progress and task completion tracking

## ENVIRONMENT
- **MCP Integration**: Runs as Model Context Protocol server for Claude Desktop
- **Storage**: Uses user home directory for reliable cross-platform access
- **Dependencies**: Deno runtime with @std/yaml and @mizchi/mcp-helper

## EXIT STATUS
MCP tools return structured JSON responses with success/failure indicators and descriptive error messages.

## SEE ALSO
- **docs/mcp-integration.md** - MCP setup and configuration guide
- **CLAUDE.md** - Development commands and CLI usage
- **docs/methodology.md** - Detailed methodology explanation
- **prompts/lessons/** - Interactive learning content
- **patterns/** - Specification pattern templates

## AUTHOR
Orchestration Framework - Systematic methodology for knowledge work

## VERSION
1.0.0 - Initial MCP implementation with conversational project management

---

*This manual page describes the Model Context Protocol interface. For CLI usage, see CLAUDE.md.*