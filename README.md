# MCP Fleet - Productivity-Focused AI Servers

A collection of Model Context Protocol (MCP) servers designed to enhance AI-assisted productivity workflows. Each server addresses a specific aspect of knowledge work - from sustainable work rhythms to systematic project management.

## Philosophy

MCP Fleet embraces a philosophy of **systematic, sustainable productivity** enhanced by AI. Rather than chasing productivity hacks or rigid systems, these servers work with natural human patterns and proven methodologies to create lasting value.

The servers are designed to prevent common pitfalls of AI-assisted work: superficial solutions, unsustainable intensity, and scattered effort. Instead, they promote depth, rhythm, and systematic progress.

## Server Overview

### 🌊 [Tides](./servers/tides/) - Rhythmic Workflow Management
Brings natural rhythm and sustainability to productivity workflows, inspired by tidal patterns in nature.
Tides helps create balanced work cycles that prevent burnout while maintaining consistent progress. [Learn more →](./servers/tides/)

### 🧭 [Compass](./servers/compass/) - Systematic Project Methodology  
Guides projects through a 4-phase methodology designed to prevent superficial work and ensure deep, meaningful outcomes.
Compass enforces thorough exploration before execution, creating lasting value rather than quick wins. [Learn more →](./servers/compass/)

## Architecture

### Why Monorepo
MCP Fleet uses a monorepo architecture following proven patterns from enterprise implementations:

1. **Shared Infrastructure**: Common MCP protocol handling and utilities
2. **Coordinated Development**: Single repository for easier testing and CI/CD  
3. **Independent Deployment**: Each server can be deployed and versioned separately
4. **Workspace Benefits**: Unified dependency resolution across the ecosystem

### Structure
```
├── servers/          # Individual MCP servers with focused responsibilities
├── packages/         # Shared libraries (MCP core, AI client, common tools)
├── docs/            # Architecture decisions, specs, and development logs
└── tests/           # Comprehensive test suite covering all components
```

## Getting Started

Each server is designed to work independently through Claude Desktop's MCP integration. The servers are available as pre-built Docker images and can be easily added to your Claude Desktop configuration.

### Prerequisites
- [Claude Desktop](https://claude.ai/download) (for MCP integration)
- Docker (for containerized deployment)
- `ANTHROPIC_API_KEY` environment variable (for AI features)

## Use Cases

### Knowledge Workers
- **Researchers**: Use Compass for systematic literature reviews and research projects
- **Consultants**: Apply Compass methodology for client engagements and deliverables
- **Product Managers**: Balance feature development with Tides rhythms

### Software Developers  
- **Project Planning**: Compass for requirement gathering and specification
- **Work-Life Balance**: Tides for sustainable development cycles
- **File Management**: Built-in file operations for project organization

### Creative Professionals
- **Writers**: Tides for managing creative energy across projects
- **Designers**: Compass for client projects requiring systematic exploration
- **Content Creators**: Balanced workflows using both servers together

## Documentation

- **[Architecture Decisions](./docs/adr/)**: Key technical decisions and rationale
- **[Technical Specifications](./docs/specs/)**: Detailed system documentation  
- **[Development Log](./docs/devlog/)**: Progress notes and insights

## Project Status

MCP Fleet is actively developed with a focus on quality over quantity. Each server is thoroughly tested and designed for long-term reliability. The project follows a "showcase open source" model - sharing clean implementations and architectural patterns rather than seeking contributions.

For questions or discussions, see the project's GitHub repository.

## License

MIT