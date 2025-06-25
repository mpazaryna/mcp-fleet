# Completion Criteria

## Purpose
This document defines the mandatory rules and completion criteria for each Orchestration Framework phase. These are non-negotiable implementation standards that ensure framework integrity and prevent premature phase transitions.

## Application
Use this context whenever applying the Orchestration Framework to ensure proper phase completion and quality gates are met.

## Integration
This module works with core/methodology.md to provide specific implementation rules. Required for all framework applications.

---

## Critical Implementation Rule

### Time is Not an Accurate Artifact
**Fundamental Principle**: Each phase is complete when its purpose is fulfilled, not when a predetermined timeline is reached.

**Why This Matters**:
- Proper exploration often reveals projects are more complex than assumed OR can be dramatically simplified
- Time-based completion leads to shallow solutions and missed requirements
- Framework optimizes for solution quality and organizational learning over schedule predictability
- Real-world complexity doesn't conform to arbitrary timelines

**Application**: Never advance phases based on time pressure. Always validate that phase purposes have been achieved.

---

## Phase Completion Criteria

### Exploration Phase Completion

**Phase is NOT complete until all of these are achieved:**

#### Problem Understanding Validation
- [ ] Multiple assumptions about the problem have been surfaced and examined
- [ ] Problem complexity has been mapped beyond surface-level requirements
- [ ] Integration requirements and real-world constraints have been identified
- [ ] Stakeholder perspectives and context have been understood

#### Risk and Edge Case Identification
- [ ] Edge cases and failure modes have been systematically identified
- [ ] "What could go wrong?" scenarios have been explored
- [ ] Dependencies and integration points have been mapped
- [ ] Resource and capability constraints have been assessed

#### Complexity Surface Test
- [ ] The "hard stuff" that initial solutions typically miss has been surfaced
- [ ] Problem appears more complex than initial assessment OR significantly simpler
- [ ] Integration challenges and real-world constraints are understood
- [ ] Assumptions have been challenged with deeper inquiry

#### Knowledge Sufficiency Check
- [ ] Sufficient domain knowledge exists to create meaningful specifications
- [ ] Key unknowns have been identified and addressed or flagged
- [ ] Problem space feels thoroughly understood, not just defined
- [ ] Exploration has revealed insights that weren't obvious initially

**Warning Signs of Incomplete Exploration**:
- Problem still feels "obvious" or "straightforward"
- No significant assumptions have been challenged
- Edge cases haven't been identified
- Integration requirements are unclear
- Problem complexity hasn't changed from initial assessment

### Specification Phase Completion

**Phase is NOT complete until all of these are achieved:**

#### Documentation Completeness
- [ ] Specifications address insights from exploration, not just surface requirements
- [ ] Edge cases and failure modes identified in exploration are covered
- [ ] Integration points and system architecture are defined
- [ ] Acceptance criteria reflect real requirements, not just happy paths

#### Execution Readiness Test  
- [ ] AI agent could execute against specifications without additional problem exploration
- [ ] Specifications are specific enough to prevent "brilliant surface solutions"
- [ ] Technical architecture addresses real-world constraints
- [ ] Quality validation methods are defined

#### Specification Formats (Choose Appropriate)
- [ ] Narrative summaries capture key exploration insights
- [ ] Gherkin scenarios (Given/When/Then) define required behaviors
- [ ] UML diagrams or workflows show system architecture
- [ ] Component specifications define interfaces and interactions
- [ ] Acceptance criteria establish validation methods

#### Reality Check
- [ ] Specifications address production requirements, not demo scenarios
- [ ] Real APIs, constraints, and integration points are specified
- [ ] Edge cases have specific handling requirements
- [ ] Specifications would prevent the typical AI "brilliant surface solution"

**Warning Signs of Incomplete Specification**:
- Specifications only cover obvious/happy path scenarios
- Implementation approach is still unclear
- Edge cases are mentioned but not specified
- Integration requirements are vague
- Specifications could lead to proof-of-concept rather than production solution

### Execution Phase Completion

**Phase is NOT complete until all of these are achieved:**

#### Specification Adherence
- [ ] Solution addresses specification requirements, not original surface problem
- [ ] Edge cases identified in exploration have been implemented
- [ ] Integration requirements from specification have been met
- [ ] Quality criteria defined in specification have been satisfied

#### Production Readiness
- [ ] Solution handles real-world constraints and integration points
- [ ] Error handling and failure modes are implemented
- [ ] Solution is robust enough for actual use, not just demonstration
- [ ] Performance and scalability requirements are met

#### Validation Against Framework Goals
- [ ] Solution addresses the complexity uncovered in exploration
- [ ] Implementation avoids the "brilliant surface solution" trap
- [ ] Real integration requirements work, not just simulated ones
- [ ] Solution would satisfy actual users/stakeholders, not just demos

#### Quality Assurance
- [ ] Solution has been tested against acceptance criteria
- [ ] Edge cases function as specified
- [ ] Integration points work with real systems/constraints
- [ ] Solution maintains quality under realistic conditions

**Warning Signs of Incomplete Execution**:
- Solution only works in ideal/demo conditions
- Edge cases aren't actually handled
- Integration is simulated rather than real
- Solution feels like proof-of-concept rather than production-ready

### Feedback & Learning Phase Completion

**Phase is NOT complete until all of these are achieved:**

#### Solution Analysis
- [ ] What worked well and what didn't has been systematically analyzed
- [ ] Implementation challenges have been documented
- [ ] Specification effectiveness has been evaluated
- [ ] Exploration completeness has been assessed

#### Framework Improvement
- [ ] Insights for improving future exploration phases have been captured
- [ ] Specification patterns that worked (or didn't) have been documented
- [ ] Framework methodology improvements have been identified
- [ ] Domain-specific patterns have been extracted for reuse

#### Knowledge Integration
- [ ] Lessons learned are documented for organizational benefit
- [ ] Patterns identified can be applied to similar problems
- [ ] Framework knowledge base has been updated
- [ ] Success/failure factors have been captured

#### Continuous Improvement
- [ ] Specific improvements to framework application have been identified
- [ ] Next similar projects would benefit from captured insights
- [ ] Organizational capability has measurably increased
- [ ] Framework effectiveness metrics show improvement

---

## Quality Gates

### Between Exploration and Specification
**Gate Question**: "Do we understand this problem well enough to create specifications that will prevent surface-level solutions?"

**Must Answer "Yes" to Proceed**:
- Problem complexity is thoroughly mapped
- Edge cases and integration requirements are identified
- Assumptions have been challenged and validated
- "Hard stuff" has been surfaced

### Between Specification and Execution
**Gate Question**: "Are these specifications complete enough for an AI agent to build a production-ready solution?"

**Must Answer "Yes" to Proceed**:
- Specifications address exploration insights
- Edge cases have defined handling requirements
- Integration points are specifically defined
- Quality criteria are established

### Between Execution and Learning
**Gate Question**: "Does this solution address the real requirements identified in exploration and specification?"

**Must Answer "Yes" to Proceed**:
- Solution handles real-world complexity
- Edge cases actually work
- Integration requirements are met
- Solution is production-ready, not proof-of-concept

---

## Framework Integrity Checks

### Systematic Process Validation
- [ ] Each phase built on insights from previous phase
- [ ] No phase was skipped or abbreviated due to time pressure
- [ ] Quality gates were properly validated before phase transitions
- [ ] Framework principles were maintained throughout

### Outcome Quality Assessment
- [ ] Final solution addresses real requirements, not surface assumptions
- [ ] Complex problems received appropriately complex solutions
- [ ] Simple problems weren't over-engineered
- [ ] Solution quality reflects exploration and specification investment

### Learning Integration Validation
- [ ] Framework application improved organizational capability
- [ ] Insights captured will inform future projects
- [ ] Methodology refinements have been identified
- [ ] Success patterns can be replicated

---

## Common Completion Failures

### Premature Phase Advancement
**Symptom**: Moving to next phase because "we've spent enough time on this"
**Solution**: Validate completion criteria rather than time investment

### Surface-Level Satisfaction
**Symptom**: Phase "feels complete" but criteria checklist reveals gaps
**Solution**: Use objective criteria, not subjective assessment

### Pressure-Based Shortcuts
**Symptom**: Skipping criteria due to external timeline pressure
**Solution**: Explain that proper process reduces total time to quality solution

### Specification Bypass
**Symptom**: Going directly from exploration to execution
**Solution**: Recognize that specifications prevent costly rework and ensure quality

---

## Metadata
- Version: 1.0
- Dependencies: core/methodology.md
- Last Updated: Based on implementation rules from project conversations
- Integration: Required for all framework applications to ensure quality and prevent shortcuts