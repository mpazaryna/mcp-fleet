# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records for MCP Fleet.

## Format

ADR files follow the format: `ADR-XXXX-title.md`

Each ADR should contain:
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: The issue motivating this decision
- **Decision**: The change being proposed or has been agreed
- **Consequences**: What becomes easier or more difficult

## Template

```markdown
# ADR-XXXX: [Title]

**Status**: [Proposed/Accepted/Deprecated/Superseded by ADR-YYYY]

**Date**: YYYY-MM-DD

## Context

Brief description of the issue or decision that needs to be made.

## Decision

The decision that was made and why.

## Consequences

### Positive
- What becomes easier or better

### Negative  
- What becomes harder or worse

### Neutral
- Other implications
```

## Current ADRs

- ADR-0001: [Python Migration from Deno](./ADR-0001-python-migration.md)
- ADR-0002: [Monorepo Architecture](./ADR-0002-monorepo-architecture.md)