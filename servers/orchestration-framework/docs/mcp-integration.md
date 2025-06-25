# MCP Integration for Orchestration Framework

## Overview

The Model Context Protocol (MCP) integration transforms the Orchestration Framework from a command-line tool into a conversational, Claude Desktop-native experience. This enables users to manage systematic project methodology through natural conversation while preserving all the sophisticated underlying logic.

## Architecture

### MCP as Facade Pattern
- **CLI Remains**: All existing commands (`deno task init`, `deno task explore`, etc.) continue to work
- **MCP Wraps**: The MCP server provides conversational access to the same functionality
- **Zero Breaking Changes**: Power users can still use the CLI directly
- **Additive Value**: MCP adds guided, conversational project methodology

### Conversation Continuity
The MCP server enables persistent project conversations across multiple Claude Desktop sessions:
- **Project Memory**: Full conversation history accessible across sessions
- **Context Preservation**: Previous insights inform new conversations
- **Session Building**: Each conversation deepens project understanding
- **Smart Resumption**: Claude can pick up projects weeks later with full context

## MCP Tools Available

### Project Management
- `init_project(name)` - Initialize new project with 4-phase structure
- `list_projects()` - Show all projects with status information
- `get_project_status(project_name?)` - Detailed project status and recommendations

### Conversation Continuity
- `get_project_context(project_name)` - Load full conversation history
- `start_exploration(project_name?, focus_area?)` - Begin/continue exploration phase
- `save_exploration_session(project_name, conversation_content, summary?)` - Capture exploration conversations to files
- `complete_exploration_phase(project_name, completion_reason?)` - Mark exploration complete even with remaining tasks

### Specification Generation
- `generate_specification(project_name?, pattern?)` - Pattern-based spec generation
- `list_patterns()` - Available specification patterns

### Flywheel System
- `check_flywheel_opportunities(project_name?)` - Gap analysis and iteration recommendations

### Learning & Onboarding
- `get_framework_lesson(lesson_topic?, lesson_level?)` - Interactive lessons using Feynman teaching method
- `get_man_page(section?)` - Comprehensive manual page for all MCP tools and methodology

## Installation & Setup

### 1. Install Dependencies
```bash
# Dependencies are already configured in deno.json
deno cache mcp_main.ts
```

### 2. Configure Claude Desktop
Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "orchestration-framework": {
      "command": "deno",
      "args": ["run", "--allow-all", "/path/to/orchestration-framework/mcp_main.ts"],
      "cwd": "/path/to/orchestration-framework"
    }
  }
}
```

### 3. Start Claude Desktop
The MCP server will automatically start when Claude Desktop connects.

## Usage Examples

### Starting a New Project
```
User: I want to start a systematic approach to redesigning our customer onboarding

Claude: I'll initialize an Orchestration Framework project for this. 
        [calls init_project("customer-onboarding-redesign")]
        
        ✅ Project initialized with 4-phase methodology:
        • Exploration → Specification → Execution → Feedback
        
        Let's begin systematic exploration. What's the current onboarding 
        experience like for your customers?
```

### Resuming Previous Work
```
User: Let's continue working on my onboarding project

Claude: [calls get_project_context("customer-onboarding-redesign")]
        
        Welcome back! I see we've had 3 exploration sessions on this project.
        From our previous conversations, you identified:
        • Users drop off at SMS verification (Session 1)  
        • Mobile UX has specific pain points (Session 2)
        • Verification flow needs simplification (Session 3)
        
        Would you like to:
        1. Generate a specification based on our exploration
        2. Explore mobile verification flow deeper
        3. Start a new exploration area
```

### Capturing Exploration Sessions
```
User: Let's save this conversation to the project files

Claude: [calls save_exploration_session("customer-onboarding-redesign", conversation_content)]
        
        ✅ Exploration session 1 saved successfully
        
        • Conversation captured in exploration/conversation-1.md
        • Session count updated in project metadata
        • Content available for future specification generation
```

### Completing Exploration Phase
```
User: I feel like I've explored enough. Let's move to creating a specification.

Claude: [calls complete_exploration_phase("customer-onboarding-redesign", "Sufficient insights gathered on user pain points and verification flow")]
        
        ✅ Exploration phase marked complete. 3 remaining tasks marked as complete.
        
        • Exploration phase completed by user decision
        • Completion reason recorded in exploration/completion-override.md
        • Ready to generate specification
```

### Getting Help and Documentation
```
User: What tools are available? Show me the manual.

Claude: [calls get_man_page()]
        
        # ORCHESTRATION-FRAMEWORK(1) Man Page
        
        ## NAME
        orchestration-framework - systematic project methodology tools for Claude Desktop
        
        ## SYNOPSIS
        Conversational interface for 4-phase project methodology:
        **Exploration → Specification → Execution → Feedback**
        
        ## COMMANDS
        
        ### Project Management
        - init_project(name) - Initialize new project with 4-phase structure
        - list_projects() - Show all projects with status information
        [Complete command reference...]
```

### Learning the Framework
```
User: I'm new to the Orchestration Framework. Can you teach me how it works?

Claude: [calls get_framework_lesson("methodology-overview", "beginner")]
        
        🎓 ORCHESTRATION FRAMEWORK LESSON: Understanding the 4-Phase Methodology
        
        ## The Core Problem We're Solving
        
        Imagine you're building a bridge. Most people would immediately start designing 
        the bridge structure, choosing materials, calculating load capacity...
        
        [Full Feynman-method lesson content delivered]
        
        📚 Available lessons: methodology-overview, exploration-techniques
        🎯 Next recommended: exploration-techniques
```

### Pattern-Based Specification
```
User: I think we're ready to create a product requirements document

Claude: [calls check_flywheel_opportunities() then generate_specification("product_requirement_doc")]
        
        ✅ No gaps detected - ready for specification!
        
        I've generated a comprehensive PRD based on your exploration insights:
        • Problem Statement: SMS verification complexity causing 40% drop-off
        • User Stories: Simplified verification with progress indicators
        • Technical Requirements: Mobile-first design with fallback options
        
        The specification is saved as: specification/spec-product_requirement_doc-2025-06-22.md
```

## Benefits

### For Users
- **Natural Workflow**: Project methodology through conversation
- **Persistent Memory**: Claude remembers all project context
- **Guided Process**: Systematic approach without CLI complexity
- **Intelligent Recommendations**: Flywheel iterations and pattern suggestions
- **Methodology Enforcement**: Built-in guardrails prevent shortcuts to implementation

### For Organizations
- **Methodology Adherence**: Systematic approach becomes natural
- **Knowledge Capture**: All insights preserved in project structure
- **Scalable Process**: Teams can follow proven patterns
- **Quality Assurance**: Completion criteria prevent shortcuts

## Technical Architecture

### MCP Server (`src/mcp/server.ts`)
- Implements @mizchi/mcp-helper for protocol compliance
- Zod schemas for type safety
- Error handling and logging
- CLI command integration

### Tool Handlers
Each MCP tool wraps corresponding CLI functionality:
- Project directory management
- File system operations
- Pattern processing
- Conversation history loading

### State Management
- Projects stored in `~/OrchestrationProjects/` directory (user's home directory)
- Metadata in `.orchestration.json` files
- Conversation history in `exploration/conversation-*.md`
- Specifications in `specification/` directory

## Development

### Running MCP Server
```bash
# Start MCP server for Claude Desktop
deno task mcp-server

# Test MCP server creation
deno test tests/unit/mcp/
```

### Testing
The MCP server includes unit tests to verify:
- Server creation without errors
- Tool exposure and functionality
- Error handling and edge cases

## Future Enhancements

### Phase 1 (Current)
- ✅ Core project lifecycle tools
- ✅ Conversation continuity
- ✅ Pattern-based specification
- ✅ Flywheel gap analysis

### Phase 2 (Planned)
- Real-time exploration sessions through MCP
- File reading/writing for direct context access
- Advanced pattern recommendation
- Multi-project workflow management

### Phase 3 (Vision)
- Cross-project insight aggregation
- Team collaboration features
- Custom pattern creation
- Advanced analytics and reporting

## Conclusion

The MCP integration represents a fundamental transformation of the Orchestration Framework from a CLI tool into a conversational, AI-native methodology system. It preserves all existing functionality while making systematic project work accessible through natural conversation with Claude Desktop.

This creates the potential for the Orchestration Framework to become **the definitive way to do systematic project work with Claude** - enabling anyone to leverage sophisticated methodology through simple conversation.

## Troubleshooting

### Project Storage Location
Projects created via MCP are stored in `~/OrchestrationProjects/` (your home directory) rather than the framework's `projects/` directory. This ensures:
- Reliable permissions when running from Claude Desktop
- User-accessible project files regardless of framework installation location
- Consistent behavior across different operating systems

### Methodology Enforcement
The MCP server includes built-in guardrails:
- **Specification generation** requires completed exploration tasks
- **Clear phase indicators** in all tool responses
- **Guided next actions** that reinforce the systematic approach

If Claude tries to jump to implementation, the MCP tools will provide clear error messages explaining what exploration is needed first.