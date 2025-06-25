export const FRAMEWORK_TEMPLATES = {
  tasks: `# {{PROJECT_NAME}} - Orchestration Framework Tasks

## Phase 1: Exploration ⏳
- [ ] Complete initial problem exploration
- **Artifacts**: \`exploration/questions.md\`, \`exploration/conversation-*.md\`, \`exploration/insights.md\`

## Phase 2: Specification 📋
- [ ] Process exploration inputs into insights document
- [ ] Transform insights into structured specifications
- [ ] Generate behavioral scenarios (Given/When/Then)
- [ ] Define system architecture and components
- **Artifacts**: \`specification/insights.md\`, \`specification/requirements.md\`, \`specification/scenarios.gherkin\`

## Phase 3: Execution 🎯
- [ ] Implement solution based on specifications
- [ ] Validate against acceptance criteria
- **Artifacts**: Working solution in \`execution/\`

## Phase 4: Feedback & Learning 🔄
- [ ] Analyze outcomes and lessons learned
- [ ] Update framework knowledge base
- **Artifacts**: \`feedback/lessons.md\`

---
**Current Status**: {{STATUS}}
**Next Action**: {{NEXT_ACTION}}
`,

  explorationQuestions: `# Exploration Questions: {{PROJECT_NAME}}

## Core Problem Definition
**What problem are we actually solving?**

**Surface problem**: 

**Deeper problems**: 

**Why is this important now?**: 

## Context & Assumptions
**What are we assuming?**

**Key assumptions**: 
- Assumption 1:
- Assumption 2:

## Stakeholders & Impact
**Who cares about this problem?**

**Primary stakeholders**: 

**What happens if this problem isn't solved?**: 

## Hidden Complexity
**What makes this harder than it seems?**

**Technical complexity**: 

**Organizational complexity**: 

**Domain complexity**: 

---
*This template guides systematic exploration. Use \`deno task explore\` for AI-assisted sessions.*
`
};