# Changelog

All notable changes to MCP Fleet will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.1] - 2024-12-25

### Added
- Tide report file saving functionality with persistent storage
- Docker volume mounting for report persistence outside containers
- New MCP tools: `save_tide_report` and `export_all_tides`
- Multiple report formats: JSON, Markdown, and CSV
- Comprehensive report generation with flow statistics and history
- Enhanced Docker Desktop MCP Toolkit integration
- Volume mount configuration in docker-compose.yml

### Changed
- Updated tides server to include report tools alongside core tide management
- Enhanced CLAUDE.md documentation with new report functionality
- Improved Docker configuration for file persistence

### Fixed
- Resolved TypeScript linting issues in tool implementations
- Fixed async/await patterns in report generation functions
- Corrected import paths for Deno standard library

## [0.1.0] - 2024-12-20

### Added
- Docker containerization for MCP Fleet servers
- Multi-stage Dockerfile for optimized builds
- Separate Dockerfiles for orchestration-framework and tides servers
- Docker Compose configuration for local development
- Deployment scripts for easy container management
- Docker Desktop MCP Toolkit integration
- Resource constraints configuration (1 CPU, 2GB RAM per MCP requirements)

### Changed
- Refactored Python-based servers to Deno TypeScript for better performance
- Updated all configuration files for containerized deployment
- Enhanced documentation for Docker-based workflows

## [0.0.1] - 2024-12-20

### Added
- Initial monorepo structure with orchestration-framework and tides servers
- Core tidal workflow management system
- MCP tools: `create_tide`, `list_tides`, and `flow_tide`
- Support for daily, weekly, project, and seasonal tide types
- Flow intensity management (gentle, moderate, strong)
- Rhythmic productivity philosophy and natural workflow patterns
- Comprehensive README and documentation
- Basic project structure and configuration files