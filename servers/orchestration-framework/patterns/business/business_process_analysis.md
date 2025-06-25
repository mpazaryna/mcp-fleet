---
name: business_process_analysis
domain: business
description: Analysis and optimization plan for business processes and operations
variables:
  - name: PROJECT_NAME
    description: Name of the business process being analyzed
    required: true
  - name: EXPLORATION_INSIGHTS
    description: Key insights from exploration phase
    required: true
sections:
  - title: Current Process Mapping
    description: Documentation of how the process currently works
    required: true
    explorationMappings: [currentState, stakeholders]
  - title: Problem Analysis
    description: Issues and inefficiencies in current process
    required: true
    explorationMappings: [userPainPoints, constraints]
  - title: Optimization Strategy
    description: How to improve the process
    required: true
    explorationMappings: [coreFeatures, technicalConsiderations]
---

# {{PROJECT_NAME}} - Business Process Analysis

## Executive Summary
{{GOALS}}

**Process Scope:** {{PROJECT_NAME}}
**Analysis Date:** [Current date]
**Stakeholders Involved:** {{STAKEHOLDERS}}

## Current State Mapping
{{CURRENT_STATE}}

### Process Flow
1. **Input:** [What triggers the process]
2. **Steps:** [Current process steps]
3. **Output:** [What the process produces]
4. **Handoffs:** [Between teams/systems]

### Current Stakeholders
{{STAKEHOLDERS}}

**Roles & Responsibilities:**
- [Stakeholder 1]: [Current responsibilities]
- [Stakeholder 2]: [Current responsibilities]

## Problem Analysis

### Pain Points & Inefficiencies
{{USER_PAIN_POINTS}}

### Root Cause Analysis
**Primary Issues:**
1. [Root cause 1]
   - **Symptoms:** [Observable problems]
   - **Impact:** [Business impact]
   
2. [Root cause 2]
   - **Symptoms:** [Observable problems]
   - **Impact:** [Business impact]

### Constraints & Limitations
{{CONSTRAINTS}}

## Impact Assessment

### Quantitative Impact
- **Time:** [Current time requirements]
- **Cost:** [Current cost structure]
- **Quality:** [Current quality metrics]
- **Volume:** [Current throughput]

### Qualitative Impact
- **Employee satisfaction:** [Current state]
- **Customer experience:** [Current impact]
- **Compliance:** [Current compliance status]

## Optimization Strategy

### Target State Vision
{{CORE_FEATURES}}

### Process Improvements
{{TECHNICAL_CONSIDERATIONS}}

**Key Improvements:**
1. [Improvement 1]
   - **Current state:** [How it works now]
   - **Future state:** [How it should work]
   - **Benefit:** [Expected improvement]

2. [Improvement 2]
   - **Current state:** [How it works now]
   - **Future state:** [How it should work]
   - **Benefit:** [Expected improvement]

## Implementation Roadmap

### Phase 1: Quick Wins (0-30 days)
- [Quick improvement 1]
- [Quick improvement 2]
**Expected impact:** [Immediate benefits]

### Phase 2: Process Redesign (1-3 months)
- [Major change 1]
- [Major change 2]
**Expected impact:** [Medium-term benefits]

### Phase 3: Optimization (3-6 months)
- [Advanced improvement 1]
- [Advanced improvement 2]
**Expected impact:** [Long-term benefits]

## Resource Requirements

### Human Resources
- **Project team:** [Team composition needed]
- **Training:** [Training requirements]
- **Change management:** [Support needed]

### Technology Requirements
- **Systems:** [Technology changes needed]
- **Integration:** [System integration needs]
- **Data:** [Data requirements]

### Financial Investment
- **Initial cost:** [Upfront investment]
- **Ongoing cost:** [Operational changes]
- **ROI timeline:** [Expected payback period]

## Success Metrics & KPIs
{{SUCCESS_CRITERIA}}

**Measurement Framework:**
- **Efficiency metrics:** [Time, cost, quality measures]
- **Effectiveness metrics:** [Outcome and impact measures]
- **Satisfaction metrics:** [Stakeholder satisfaction]

## Risk Assessment & Mitigation
{{RISKS}}

**Implementation Risks:**
1. [Risk 1]
   - **Probability:** [High/Medium/Low]
   - **Impact:** [High/Medium/Low]
   - **Mitigation:** [Risk mitigation strategy]

2. [Risk 2]
   - **Probability:** [High/Medium/Low]
   - **Impact:** [High/Medium/Low]
   - **Mitigation:** [Risk mitigation strategy]

## Change Management Plan

### Communication Strategy
- **Stakeholder communication:** [How to keep stakeholders informed]
- **Training plan:** [How to prepare team for changes]
- **Feedback mechanism:** [How to collect and respond to feedback]

### Success Factors
- [Critical success factor 1]
- [Critical success factor 2]
- [Critical success factor 3]

## Appendix: Exploration Insights
{{EXPLORATION_INSIGHTS}}

---
*This business process analysis was generated from systematic exploration using the Orchestration Framework. All recommendations are based on thorough investigation of current state, stakeholder needs, and optimization opportunities.*