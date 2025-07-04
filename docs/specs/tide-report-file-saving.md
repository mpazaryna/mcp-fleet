# Specification: Tide Report File Saving Feature

## Overview

Enable the Tides MCP server to save tide reports and workflow data to persistent storage outside the Docker container, allowing users to maintain historical records and share tide data across sessions.

## Problem Statement

Currently, the Tides MCP server operates entirely in-memory within a Docker container. Users cannot:
- Save tide reports to their local filesystem
- Persist tide data between container restarts
- Export workflow analytics for external analysis
- Backup tide configurations and history

## Goals

### Primary Goals
- Enable saving tide reports to user-specified directories
- Maintain Docker security best practices with controlled filesystem access
- Preserve existing MCP protocol compatibility
- Support common report formats (JSON, Markdown, CSV)

### Secondary Goals
- Auto-generate timestamped report files
- Support configurable report templates
- Enable bulk export of historical data
- Integrate with existing tide workflow patterns

## Requirements

### Functional Requirements

#### FR-1: File Saving MCP Tool
- **Description**: Add new MCP tool `save_tide_report` 
- **Input**: tide_id, report_format, output_path (optional)
- **Output**: Success confirmation with file path
- **Formats**: JSON, Markdown, CSV

#### FR-2: Docker Volume Mount Support
- **Description**: Configure Docker containers to mount user-specified directories
- **Security**: Read-write access only to designated report directory
- **Path**: Default to `/app/reports` inside container, user-configurable mount point

#### FR-3: Report Generation
- **Description**: Generate comprehensive tide workflow reports
- **Content**: Tide metadata, flow history, performance metrics, timestamps
- **Naming**: Configurable pattern with defaults like `tide-{name}-{timestamp}.{format}`

#### FR-4: Batch Operations
- **Description**: Support exporting multiple tides at once
- **Tool**: `export_all_tides` with filtering options
- **Options**: Date range, tide type, active/inactive status

### Non-Functional Requirements

#### NFR-1: Security
- **Container Isolation**: Maintain 1 CPU, 2GB memory limits
- **Filesystem Access**: Limited to mounted report directory only
- **Permissions**: No access to system directories or user home outside mount

#### NFR-2: Performance
- **File Operations**: Non-blocking I/O for large reports
- **Memory Usage**: Stream large exports to avoid memory spikes
- **Response Time**: File operations complete within 5 seconds

#### NFR-3: Compatibility
- **MCP Protocol**: Maintain full compatibility with existing tools
- **Docker Desktop**: Work with Docker MCP requirements
- **Claude Desktop**: Seamless integration with current configuration

## Technical Design

### Architecture

```
Claude Desktop
    ↓ (MCP Protocol)
Tides Container (/app/reports) ←→ Host Volume Mount (/path/to/user/reports)
    ↓ (File I/O)
Report Files (JSON/MD/CSV)
```

### New MCP Tools

#### save_tide_report
```typescript
interface SaveTideReportParams {
  tide_id: string;
  format: 'json' | 'markdown' | 'csv';
  output_path?: string; // Relative to reports directory
  include_history?: boolean;
}

interface SaveTideReportResult {
  success: boolean;
  file_path: string;
  file_size: number;
  tide_name: string;
}
```

#### export_all_tides
```typescript
interface ExportAllTidesParams {
  format: 'json' | 'markdown' | 'csv';
  filter?: {
    flow_type?: string;
    active_only?: boolean;
    date_range?: { start: string; end: string };
  };
  output_directory?: string;
}

interface ExportAllTidesResult {
  success: boolean;
  files_created: string[];
  total_tides: number;
  export_summary: string;
}
```

### Docker Configuration Updates

#### Volume Mount Strategy
```bash
# Development
docker run -v "$(pwd)/tide-reports:/app/reports" mcp/tides:latest

# Production 
docker run -v "/Users/username/Documents/TideReports:/app/reports" mcp/tides:latest
```

#### Claude Desktop Config Update
```json
{
  "mcpServers": {
    "tides": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--name", "tides-mcp-session",
        "-e", "ANTHROPIC_API_KEY",
        "-v", "/Users/username/Documents/TideReports:/app/reports",
        "--cpus=1", "--memory=2g",
        "mcp/tides:latest"
      ]
    }
  }
}
```

### File Structure

```
/app/reports/               # Container mount point
├── tides/                  # Individual tide reports
│   ├── daily/             
│   ├── weekly/            
│   ├── project/           
│   └── seasonal/          
├── exports/               # Bulk export files
├── templates/             # Report templates
└── .metadata.json         # Export tracking
```

## Implementation Plan

### Phase 1: Core File Operations
1. Add file I/O utilities to Tides server
2. Implement `save_tide_report` MCP tool
3. Create basic JSON report format
4. Update Docker configuration for volume mounts

### Phase 2: Enhanced Formats
1. Add Markdown report generation
2. Implement CSV export functionality  
3. Create configurable report templates
4. Add batch export capabilities

### Phase 3: Integration & Polish
1. Update Claude Desktop configuration guidance
2. Add comprehensive error handling
3. Create user documentation
4. Performance optimization

## Testing Strategy

### Unit Tests
- File I/O operations with mocked filesystem
- Report generation for all formats
- Error handling for permission issues

### Integration Tests  
- End-to-end MCP tool testing
- Docker volume mount verification
- Claude Desktop integration testing

### Security Tests
- Filesystem access boundary testing
- Permission escalation prevention
- Container isolation verification

## Acceptance Criteria

### Must Have
- [ ] Users can save tide reports to local directories
- [ ] Docker container maintains security isolation
- [ ] MCP tools work seamlessly in Claude Desktop
- [ ] Reports include comprehensive tide data

### Should Have
- [ ] Multiple export formats supported
- [ ] Batch export functionality available
- [ ] Configurable file naming patterns
- [ ] Clear error messages for file operations

### Could Have
- [ ] Custom report templates
- [ ] Automated backup scheduling
- [ ] Report analytics and insights
- [ ] Integration with cloud storage

## Risks & Mitigations

### Risk: Filesystem Security Breach
- **Mitigation**: Strict volume mount controls, no host system access
- **Testing**: Security boundary verification

### Risk: Performance Impact
- **Mitigation**: Async I/O, streaming for large files
- **Testing**: Load testing with large tide datasets

### Risk: Docker Desktop Compatibility
- **Mitigation**: Follow MCP requirements exactly
- **Testing**: Multi-platform Docker testing

## Success Metrics

- Users can successfully save tide reports 100% of the time
- File operations complete within 5 seconds
- Zero security incidents with filesystem access
- Positive user feedback on workflow integration

---

**Document Version**: 1.0  
**Created**: 2025-06-25  
**Author**: Claude Code Assistant  
**Status**: Draft - Ready for Review