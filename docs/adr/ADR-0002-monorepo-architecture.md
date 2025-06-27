# ADR-0002: Monorepo Architecture

**Status**: Accepted

**Date**: 2025-06-27

## Context

MCP servers are naturally microservices, but they benefit from shared infrastructure and coordinated development. Need to balance independent deployment with development efficiency.

Evaluated approaches:
- Separate repositories per server
- Monorepo with shared packages
- Single server with multiple tools

Influenced by Cloudflare's MCP server architecture using similar patterns.

## Decision

Use monorepo architecture with shared packages and independent server deployments.

**Structure:**
- `packages/`: Shared libraries (mcp_core, claude_client, common_tools)
- `servers/`: Individual MCP servers (tides, compass, toolkit)
- Workspace dependencies with uv
- Multi-stage Docker builds for independent deployment

## Consequences

### Positive
- **Shared Infrastructure**: Common MCP protocol handling and utilities
- **Coordinated Development**: Single repo for easier testing and CI/CD
- **Independent Deployment**: Each server deployed/versioned separately
- **Workspace Benefits**: Dependency resolution across entire ecosystem
- **Code Reuse**: Common patterns and tools shared across servers

### Negative
- More complex build configuration
- Potential for tight coupling between servers
- Larger repository size
- Need for workspace-aware tooling

### Neutral
- Follows industry patterns (Cloudflare, etc.)
- Standard Python monorepo practices
- CI/CD complexity similar to multiple repos