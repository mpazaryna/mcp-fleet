# Changelog

All notable changes to MCP Fleet will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [3.0.0] - 2025-07-03

### Added
- **Memry Server**: New MCP server for memory storage and retrieval
  - File-based storage using markdown with YAML frontmatter
  - `store_memory` - Store new memories with content and metadata
  - `search_memories` - Full-text search across stored memories
  - `get_memory` - Retrieve specific memory by ID
  - `list_memories` - List all stored memories with filtering
  - `delete_memory` - Remove specific memories
  - Docker Hub CI/CD integration for automated builds
- **mcp-storage Package**: Shared storage library for MCP servers
  - JSON file backend implementation
  - Entity and configuration management
  - Type-safe Pydantic models for data validation
- **Enhanced Testing Infrastructure**
  - New E2E test framework for Docker-based MCP servers
  - UAT (User Acceptance Testing) for real-world scenarios
  - Comprehensive test coverage for memry server and storage package
- **GitHub Workflow Commands**: New Claude Code commands for systematic development
  - `/project:write-github-issue` - Create well-structured GitHub issues
  - `/project:fix-github-issue` - Systematically analyze and fix issues with TDD

### Changed
- **MCP Protocol Compliance**: Major fixes for proper MCP specification adherence
  - Fixed missing input parameters in handlers without input
  - Updated all MCP tool handlers for proper protocol compatibility
  - Standardized tool schemas across all servers
- **Documentation Updates**
  - Updated CLAUDE.md with new development workflow commands
  - Added comprehensive testing strategy documentation
  - Enhanced server architecture descriptions

### Breaking Changes
- **MCP Protocol Updates**: All MCP tool handlers now strictly follow the protocol specification. Existing integrations may need updates to handle the corrected input/output schemas.
- **Storage Format**: New mcp-storage package introduces a standardized storage format that may not be compatible with custom storage implementations.

### Fixed
- MCP tool handlers now properly handle cases with no input parameters
- Protocol compatibility issues that could cause client connection failures
- Standardized error handling across all MCP servers

## [2.2.0] - 2025-06-27 (Unreleased)

### Changed
- **CLAUDE.md**: Complete rewrite to reflect Python architecture
  - Updated from outdated Deno/TypeScript references to current Python implementation
  - Updated all command examples to use `uv` instead of `deno`
  - Added proper Claude Desktop configuration patterns for all servers
- **Workspace Configuration**: Updated uv workspace members in pyproject.toml
- **Claude Desktop Integration**: Updated configuration to use proper `uv --directory` pattern for workspace execution

### Technical Implementation
- **MCP Protocol Compliance**: Full stdio transport with proper tool registration and handlers
- **Python Async Patterns**: Consistent async/await implementation following MCP Fleet standards

### Fixed
- **MCP Protocol Implementation**: Proper stdio server implementation replacing custom JSON-RPC handling
- **Workspace Dependencies**: Correct uv workspace integration for shared package access

## [2.1.0] - 2025-06-27

### Added
- Clean folder structure with standardized naming conventions
  - **packages/**: Renamed from python-packages for cleaner structure
  - **servers/**: Renamed from python-servers for consistency
  - Removed "python-" prefixes from all folder names for better navigation

### Changed
- **BREAKING**: Folder structure reorganization affects local development setup
- **Docker Configuration**: Updated Dockerfile with new folder paths
- **Workspace Configuration**: Updated pyproject.toml workspace members
- **Development Configs**: Updated claude-desktop-config-local.json paths
- **Test Imports**: Updated all test files to use new folder structure

### Removed
- **OF (Orchestration Framework) Server**: Removed problematic server implementation
  - Eliminated complex template engine causing deployment issues
  - Simplified codebase to focus on stable servers (tides, compass)
  - Removed 50+ template files and related Python cache artifacts
- **Redundant Docker Files**: Cleaned up deployment infrastructure
  - Removed docker-compose.yml (redundant with Dockerfile)
  - Removed individual server Dockerfiles (consolidated to multi-stage build)
  - Removed deploy-tides-mcp.sh script (CI/CD handles publishing)

### Fixed
- **Build System**: Streamlined Docker builds to single multi-stage Dockerfile
- **CI/CD Pipeline**: Verified GitHub Actions still builds correctly after restructure
- **Python Cache**: Removed all __pycache__ directories from version control
- **Import Paths**: Fixed test file imports to work with new folder structure

### Technical Details
- **Workspace Structure**: Explicit server listing in pyproject.toml for better control
- **Docker Build**: Multi-stage builds for tides, compass servers only
- **GitHub Actions**: Continues to publish to Docker Hub with new folder structure
- **Python Paths**: Updated PYTHONPATH configurations in all development configs

## [2.0.0] - 2025-06-27

### Added
- **COMPLETE PYTHON MIGRATION**: Entire codebase migrated from Deno/TypeScript to Python 3.11+ with uv
  - **Python Monorepo**: Workspace structure with shared packages (mcp_core, claude_client, common_tools)
  - **uv Package Management**: Fast dependency resolution and environment management
  - **Async/Await Throughout**: Full async implementation for file I/O and API calls

- **OF (Orchestration Framework) Server**: Template-driven systematic methodology
  - **External Markdown Templates**: Prompts and patterns as versionable markdown files outside code
  - **Generic Template Engine**: YAML frontmatter parsing with Jinja2 variable injection
  - **Pattern Manager**: Domain-specific specification templates (software, business, personal)
  - **Prompt Manager**: AI conversation templates with phase-specific context injection
  - **Template Inheritance**: Composition and extension support for complex templates

- **Template System Features**:
  - **Business Patterns**: `business_process_analysis.md` with comprehensive workflow documentation
  - **Software Patterns**: `product_requirement_doc.md`, `learning_new_paradigm.md`
  - **AI Prompts**: Phase-specific guidance (exploration, specification, execution, flywheel)
  - **Variable Validation**: Required/optional variable checking with type safety
  - **Section Mapping**: Automatic exploration insights to pattern section mapping

- **Docker & CI/CD Improvements**:
  - **Multi-stage Dockerfile**: Single build file for all Python servers with shared base
  - **GitHub Actions**: Automated Docker Hub publishing with multi-platform builds
  - **Template Bundling**: All markdown templates included in Docker images
  - **Optimized Caching**: GitHub Actions cache for faster builds

- **Comprehensive Testing**: Maintained TDD approach throughout migration
  - **Template Validation**: Automated testing of markdown template parsing and rendering
  - **Pattern Rendering**: Full specification generation testing with real variables
  - **Import System**: Python workspace package testing and validation

### Changed
- **BREAKING**: Complete migration from Deno to Python runtime
- **Architecture**: Pydantic models replace TypeScript interfaces for type safety
- **Dependencies**: httpx replaces @anthropic-ai/sdk for Claude API integration
- **Package Structure**: Clean separation of packages vs servers in monorepo
- **Docker Images**: All images now use Python 3.11 base with uv package manager

### Fixed
- **Docker Dependencies**: Resolved circular dependency issues in multi-stage builds
- **Authentication**: GitHub Actions Docker Hub publishing with proper credentials
- **Template Loading**: Async file loading with proper error handling and caching
- **Import Paths**: Workspace package imports working correctly across all servers

### Technical Details
- **Runtime**: Python 3.11+ with asyncio throughout
- **Package Manager**: uv for fast dependency resolution
- **Schema Validation**: Pydantic models with comprehensive type hints
- **Template Engine**: Jinja2 with YAML frontmatter parsing
- **AI Integration**: Anthropic Claude API with retry logic and conversation management
- **Testing**: pytest with async support and comprehensive coverage

## [1.3.0] - 2025-06-26

### Added
- **Compass MCP Server**: Complete systematic project methodology implementation
  - 4-phase systematic approach: Exploration → Specification → Execution → Feedback
  - **Project Management Tools**: `init_project`, `list_projects`, `get_project_status`
  - **Exploration Tools**: `start_exploration`, `save_exploration_session`, `get_project_context`, `complete_exploration_phase`
  - **Specification Tools**: `generate_specification`, `list_patterns`, `get_specification_status`
  - **Execution Tools**: `start_execution`, `list_tasks`, `update_task_status`
- **Pattern-Based Specifications**: Built-in templates for software, business, and project domains
  - Software product requirements with user stories and technical specs
  - Business process analysis with current state and improvement documentation
  - General project planning with charter, scope, and implementation plans
- **Context-Aware Task Generation**: AI-assisted breakdown of specifications into actionable tasks
- **Conversation History Preservation**: Systematic capture of exploration insights as organizational knowledge
- **Docker Integration**: Full containerization with workspace persistence
  - `Dockerfile.compass` with optimized resource constraints
  - Volume mounting to `~/Documents/CompassProjects/` for file persistence
  - Docker Desktop MCP Toolkit integration with proper workspace handling
- **Comprehensive Testing**: 35+ test scenarios across unit, integration, and E2E levels
  - Test-driven development (TDD) implementation for all phases
  - Complete lifecycle validation with real file artifacts
  - Integration workflow testing between phases

### Changed
- **CLAUDE.md**: Updated with comprehensive Compass server documentation
- **Claude Desktop Config**: Added Compass server with Docker volume mounting
- **Build System**: Added Compass to Docker build tasks and monorepo commands
- **Architecture**: Extended MCP Fleet pattern with systematic methodology enforcement

### Technical Implementation
- **Methodology Enforcement**: Prevents "surface-level shiny object" AI responses through structured phases
- **Phase Gating**: Must complete exploration before specification, specification before execution
- **Context Continuity**: Conversation histories preserved across sessions for consistent context
- **Zod Schema Validation**: Type-safe tool definitions with comprehensive input/output validation
- **Docker Workspace Fix**: Resolved file persistence issues with COMPASS_WORKSPACE environment variable

### Fixed
- **Docker Volume Mounting**: Fixed workspace detection to use mounted directories instead of container-internal paths
- **File Persistence**: Ensured all project files are saved to persistent mounted volumes
- **Cross-Platform Compatibility**: Proper workspace detection for both native and Docker deployments

## [0.1.1] - 2025-06-25

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

## [0.1.0] - 2025-06-20

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

## [0.0.1] - 2025-06-20

### Added
- Initial monorepo structure with orchestration-framework and tides servers
- Core tidal workflow management system
- MCP tools: `create_tide`, `list_tides`, and `flow_tide`
- Support for daily, weekly, project, and seasonal tide types
- Flow intensity management (gentle, moderate, strong)
- Rhythmic productivity philosophy and natural workflow patterns
- Comprehensive README and documentation
- Basic project structure and configuration files