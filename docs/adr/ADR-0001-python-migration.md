# ADR-0001: Python Migration from Deno

**Status**: Accepted

**Date**: 2025-06-27

## Context

MCP Fleet was originally implemented in Deno/TypeScript but needed to be migrated to Python for better ecosystem alignment and development velocity.

Key factors:
- **Docker Hub publishing**: Python ecosystem has established patterns for automated Docker publishing via GitHub Actions
- Python ecosystem has stronger AI/ML library support
- Better alignment with MCP community (many examples in Python)
- Simpler dependency management with uv
- More straightforward Docker deployment patterns

## Decision

Migrate entire codebase from Deno/TypeScript to Python 3.11+ with uv package management.

**Implementation approach:**
- Use uv for fast dependency resolution and environment management
- Maintain monorepo structure with workspace dependencies
- Use Pydantic for type safety (replacing TypeScript interfaces)
- Implement async/await throughout for I/O operations
- Use pytest for testing with comprehensive coverage

## Consequences

### Positive
- Faster development iteration with Python ecosystem
- Better library support for AI/ML features
- Simpler deployment with standard Python Docker patterns
- Type safety maintained through Pydantic
- Faster dependency resolution with uv

### Negative
- Lost Deno's built-in TypeScript support
- Required complete rewrite of all servers
- Temporary development velocity loss during migration
- Need to maintain Python-specific tooling (black, ruff, mypy)

### Neutral
- Similar async programming patterns
- Maintained MCP protocol compatibility
- Docker deployment complexity roughly equivalent