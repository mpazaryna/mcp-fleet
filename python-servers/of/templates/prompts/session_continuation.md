---
name: session_continuation
description: Template for continuing previous sessions with context
variables:
  - name: LAST_SESSION_SUMMARY
    description: Summary of the previous session
    required: true
  - name: SESSIONS_SO_FAR
    description: Number of sessions completed so far
    required: true
---

## Session Continuation Context

This is session {{SESSION_COUNT}} for the {{PROJECT_NAME}} project. You have been working with the user through {{SESSIONS_SO_FAR}} previous session(s).

### Previous Session Summary:
{{LAST_SESSION_SUMMARY}}

### Current Status:
- **Phase**: {{CURRENT_PHASE}}
- **Progress**: {{EXPLORATION_PROGRESS}}

Please acknowledge this context and continue the conversation naturally, building on the previous work while maintaining focus on the current phase objectives.