# Multi-stage Dockerfile for MCP Fleet Base Image
# Optimized for Docker Desktop MCP Toolkit integration

FROM denoland/deno:latest AS base

# Use existing deno user from base image

# Set working directory
WORKDIR /app

# Copy deno configuration files first for better caching
COPY deno.json ./
COPY packages/*/deno.json ./packages/*/
COPY servers/*/deno.json ./servers/*/

# Cache dependencies by copying and running deno cache
# This stage helps with build performance
FROM base AS deps
COPY . .
RUN deno cache \
    servers/orchestration-framework/mcp_main.ts \
    servers/tides/mcp_main.ts \
    servers/compass/mcp_main.ts

# Production stage
FROM base AS production

# Copy all source code
COPY . .

# Copy cached dependencies from deps stage
COPY --from=deps /deno-dir /deno-dir

# Set proper permissions
RUN chown -R root:root /app

# Create projects directory for orchestration-framework
RUN mkdir -p /app/projects

# Health check endpoint - simple check that Deno can run
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD deno eval "console.log('Health check passed')" || exit 1

# Default command - override in specific server images
CMD ["deno", "--version"]