# Changelog

All notable changes to MCP Fleet will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.3.0] - 2024-06-25

### Added
- **Toolkit MCP Server**: Complete shared infrastructure server for file I/O operations
  - `write_file` - Save content with automatic directory creation and encoding support
  - `read_file` - Read file contents with UTF-8 and Base64 encoding
  - `create_directory` - Create directories with recursive support
  - `list_files` - List directory contents with pattern filtering and recursive traversal
  - `delete_file` - Safe file and directory deletion
- **Docker Integration**: Full containerization support for toolkit server
  - `Dockerfile.toolkit` for standalone toolkit deployment
  - Updated `docker-compose.yml` with toolkit service and persistent volumes
  - Integration with Docker Desktop MCP Toolkit
- **Comprehensive Testing**: Full test suite with 24 test scenarios
  - Unit tests for all tool definitions and handlers
  - Integration tests for complete workflow validation
  - Pattern matching, encoding support, and error handling tests
- **Architecture Documentation**: Complete documentation of microservices pattern
  - `docs/toolkit-architecture.md` - Comprehensive architectural overview
  - `docs/specifications/true-microservices-architecture.md` - Future evolution plan
  - Visual diagrams and implementation patterns

### Changed
- **Workspace Configuration**: Updated `deno.json` to include toolkit in workspace
- **Claude Desktop Config**: Added toolkit server to `claude-desktop-config.json`
- **Build System**: Added toolkit to Docker build tasks and commands

### Technical Implementation
- **Separation of Concerns**: Clear distinction between domain logic and infrastructure
- **Shared Infrastructure**: Common file operations available to all MCP Fleet servers
- **Production Ready**: Comprehensive error handling, logging, and resource management
- **Extensible Design**: Framework for adding additional shared utilities

### Architecture Evolution
- **Current State**: Hybrid architecture with both direct file I/O and toolkit services
- **Future Vision**: Pure microservices with toolkit handling all infrastructure concerns
- **Migration Path**: Documented plan for removing file I/O from domain servers

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