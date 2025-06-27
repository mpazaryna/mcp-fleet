# Multi-stage Dockerfile for all Python MCP servers
# This builds all images in a single build to avoid dependency issues

# Base Python image with uv
FROM python:3.11-slim AS python-base

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy workspace configuration and lock file
COPY pyproject.toml uv.lock ./
COPY packages/ ./packages/
COPY servers/ ./servers/

# Install dependencies for the workspace
RUN uv sync --frozen --no-dev

# Set Python path for workspace packages
ENV PYTHONPATH=/app/packages:/app/servers:/app

# Base stage for MCP servers
FROM python-base AS mcp-base

# Tides MCP Server
FROM mcp-base AS tides
WORKDIR /app/servers/tides
RUN mkdir -p /app/reports && chown -R root:root /app/reports
VOLUME ["/app/reports"]
STOPSIGNAL SIGTERM
ENTRYPOINT ["uv", "run", "python", "main.py"]
LABEL org.opencontainers.image.title="Tides MCP Server"
LABEL org.opencontainers.image.description="Rhythmic workflow management based on natural tidal patterns"
LABEL org.opencontainers.image.vendor="MCP Fleet"
LABEL org.opencontainers.image.version="2.0.0"
LABEL mcp.server.name="tides"
LABEL mcp.server.tools="workflow_management,rhythm_tracking,tide_creation,report_generation"

# Compass MCP Server  
FROM mcp-base AS compass
WORKDIR /app/servers/compass
ENV COMPASS_WORKSPACE=/app/workspace
RUN mkdir -p /app/workspace && chown -R root:root /app/workspace
VOLUME ["/app/workspace"]
STOPSIGNAL SIGTERM
ENTRYPOINT ["uv", "run", "python", "main.py"]
LABEL org.opencontainers.image.title="Compass MCP Server"
LABEL org.opencontainers.image.description="Systematic project methodology through exploration-to-execution phases"
LABEL org.opencontainers.image.vendor="MCP Fleet"
LABEL org.opencontainers.image.version="2.0.0"
LABEL mcp.server.name="compass"
LABEL mcp.server.tools="project_management,exploration,specification,execution,systematic_methodology"

# Toolkit MCP Server
FROM mcp-base AS toolkit
WORKDIR /app/servers/toolkit
STOPSIGNAL SIGTERM
ENTRYPOINT ["uv", "run", "python", "main.py"]
LABEL org.opencontainers.image.title="Toolkit MCP Server"
LABEL org.opencontainers.image.description="Essential file operations and utility tools for MCP servers"
LABEL org.opencontainers.image.vendor="MCP Fleet"
LABEL org.opencontainers.image.version="2.0.0"
LABEL mcp.server.name="toolkit"
LABEL mcp.server.tools="file_operations,utility_tools,common_tools"

