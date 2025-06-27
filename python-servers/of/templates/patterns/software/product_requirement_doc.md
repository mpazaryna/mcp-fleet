---
name: product_requirement_doc
domain: software
description: Product Requirements Document for software features and products
variables:
  - name: PROJECT_NAME
    description: Name of the project or product
    required: true
  - name: EXPLORATION_INSIGHTS
    description: Key insights from exploration phase
    required: true
sections:
  - title: Problem Statement
    description: Core problem being solved and user pain points
    required: true
    explorationMappings: [userPainPoints, goals]
  - title: User Stories
    description: User stories with acceptance criteria
    required: true
    explorationMappings: [coreFeatures, stakeholders]
  - title: Technical Requirements
    description: Technical constraints and considerations
    required: true
    explorationMappings: [technicalConsiderations, constraints]
---

# {{PROJECT_NAME}} - Product Requirements Document

## Problem Statement & User Pain Points
{{USER_PAIN_POINTS}}

**Core Problem:**
{{GOALS}}

## User Stories & Acceptance Criteria

### Primary User Journey
{{CORE_FEATURES}}

**Stakeholders:**
{{STAKEHOLDERS}}

### User Story Format
**As a** [user type], **I want** [functionality] **so that** [benefit]

**Acceptance Criteria:**
- [ ] [Specific measurable outcome]
- [ ] [Edge case handling]
- [ ] [Performance requirement]

## Functional Requirements

### Priority 0 (Must Have)
{{CORE_FEATURES}}

### Priority 1 (Should Have)
[Secondary features from exploration]

### Priority 2 (Nice to Have)
[Enhancement features from exploration]

## Non-Functional Requirements

### Performance
{{TECHNICAL_CONSIDERATIONS}}

### Security & Compliance
{{CONSTRAINTS}}

### Scalability
[Scalability requirements from exploration]

### Usability
[User experience requirements from exploration]

## Technical Considerations
{{TECHNICAL_CONSIDERATIONS}}

**Constraints:**
{{CONSTRAINTS}}

## Success Metrics & KPIs
{{SUCCESS_CRITERIA}}

**How we'll measure success:**
- User adoption metrics
- Performance benchmarks
- User satisfaction scores
- Business impact measures

## Risk Assessment & Mitigation
{{RISKS}}

**Risk Mitigation Strategies:**
- [Primary risk mitigation approach]
- [Secondary risk mitigation approach]
- [Contingency planning]

## Implementation Timeline
[High-level timeline based on exploration complexity]

**Phase 1:** Core functionality
**Phase 2:** Advanced features
**Phase 3:** Polish and optimization

## Appendix: Exploration Insights
{{EXPLORATION_INSIGHTS}}

---
*This PRD was generated from systematic exploration using the Orchestration Framework. All requirements are based on thorough problem space investigation.*