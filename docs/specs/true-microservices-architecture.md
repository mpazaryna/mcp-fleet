# True Microservices Architecture Specification

**Status**: Planned  
**Created**: 2024-06-25  
**Priority**: High  

## Overview

This specification outlines the evolution of MCP Fleet from its current hybrid architecture to a true microservices pattern where each server has a single, well-defined responsibility.

## Current Architecture Issues

### Hybrid State
Currently, the MCP Fleet has overlapping responsibilities:

- **Tides Server**: Handles both workflow logic AND file I/O operations
- **Toolkit Server**: Provides file I/O operations but tides doesn't use it
- **Result**: Two different file I/O implementations doing similar work

### Tool Duplication
Users see both sets of tools in Claude Desktop:
- `tides:save_tide_report` - Direct file operations by tides
- `toolkit:write_file` - File operations by toolkit

## Proposed Architecture

### Pure Microservices Pattern

Each server focuses on its core domain:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Tides       │    │ Orchestration   │    │     Future      │
│     Server      │    │   Framework     │    │    Servers      │
│                 │    │     Server      │    │                 │
│ ONLY:           │    │ ONLY:           │    │ ONLY:           │
│ - Workflows     │    │ - Projects      │    │ - Domain        │
│ - Flow sessions │    │ - Patterns      │    │   Logic         │
│ - Tide logic    │    │ - Conversations │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Toolkit     │
                    │     Server      │
                    │                 │
                    │ ONLY:           │
                    │ - File I/O      │
                    │ - Directory ops │
                    │ - Data persist. │
                    └─────────────────┘
```

## Implementation Plan

### Phase 1: Remove Tides File Operations

**Remove these tools from tides:**
- `save_tide_report` 
- `export_all_tides`

**Keep these domain tools:**
- `create_tide`
- `list_tides` 
- `flow_tide`

### Phase 2: Update Tides Implementation

**Modify `servers/tides/src/tools/report-tools.ts`:**
- Remove file I/O handlers completely
- Keep report generation logic as internal functions
- Create helper functions that return report content instead of saving

**Files to modify:**
- `servers/tides/src/tools/report-tools.ts` - Remove file operations
- `servers/tides/mcp_main.ts` - Remove report tools from exports
- `servers/tides/tests/` - Update tests for new pattern

### Phase 3: User Workflow Evolution

**Old Pattern:**
```
1. tides:flow_tide
2. tides:save_tide_report
```

**New Pattern:**
```
1. tides:flow_tide
2. tides:get_tide_data (new helper)
3. toolkit:write_file (user controls format/location)
```

## Benefits

### 1. True Separation of Concerns
- **Tides**: Pure workflow management
- **Toolkit**: Pure infrastructure operations
- **No overlap**: Each server has single responsibility

### 2. User Empowerment
- Users control exactly what gets saved and where
- Flexible report formats and locations
- Composable workflows from available tools

### 3. Architectural Clarity
- Clear boundaries between domain and infrastructure
- Easier testing and maintenance
- Better scalability

### 4. Future Extensibility
- Easy to add new domain servers
- All servers benefit from toolkit improvements
- Clean migration path for new capabilities

## New User Workflows

### Basic Tide Report
```bash
# 1. Record flow session
tides:flow_tide → Records session data

# 2. Generate custom report
toolkit:write_file → User saves whatever format they want
```

### Advanced Reporting
```bash
# 1. Multiple flow sessions
tides:flow_tide (morning)
tides:flow_tide (afternoon)

# 2. Get tide data for custom processing
tides:list_tides → Get all tide data

# 3. Create custom reports
toolkit:write_file → Daily summary
toolkit:write_file → Weekly analysis  
toolkit:write_file → CSV export for analytics
```

### Organized File Management
```bash
# 1. Create organized structure
toolkit:create_directory → /reports/2024/june/
toolkit:create_directory → /reports/2024/june/daily/
toolkit:create_directory → /reports/2024/june/weekly/

# 2. Save reports in organized structure
toolkit:write_file → Specific locations and formats
```

## Technical Implementation

### Helper Functions
Create internal functions in tides that generate report content:

```typescript
// Internal helper - not exposed as MCP tool
function generateTideReport(tide: TideData, format: 'json' | 'markdown' | 'csv'): string {
  // Generate report content but don't save
  return reportContent;
}

// Could be exposed as MCP tool for user convenience
export const tideReportGenerators = {
  get_tide_report_json: (args) => generateTideReport(tide, 'json'),
  get_tide_report_markdown: (args) => generateTideReport(tide, 'markdown'),
  get_tide_report_csv: (args) => generateTideReport(tide, 'csv'),
};
```

### Backward Compatibility
- Provide migration guide for existing workflows
- Document the new patterns clearly
- Keep helper functions for easy report generation

## Success Criteria

### 1. Clean Tool Separation
- ✅ Tides tools focus only on workflow logic
- ✅ Toolkit tools handle all file operations
- ✅ No functionality overlap

### 2. User Experience
- ✅ Users can create custom reports easily
- ✅ Flexible file organization
- ✅ Clear workflow patterns documented

### 3. Architecture
- ✅ True microservices pattern
- ✅ Single responsibility per server
- ✅ Composable tool ecosystem

## Migration Strategy

### For Existing Users
1. **Document new patterns** in updated USAGE.md files
2. **Provide examples** of equivalent workflows
3. **Keep helper functions** for easy report generation
4. **Update Claude Desktop configs** if needed

### For Developers
1. **Update tests** to reflect new architecture
2. **Clean up file I/O code** from domain servers
3. **Improve toolkit** based on real usage patterns
4. **Document** the new development patterns

## Timeline

- **Specification**: ✅ Completed 2024-06-25
- **Implementation**: Planned for next development session
- **Testing**: Validate new patterns work correctly
- **Documentation**: Update all relevant docs
- **Release**: Tag as major version (breaking change)

## Conclusion

This evolution represents the maturation of MCP Fleet from a collection of servers to a true microservices ecosystem. Each server will have a clear, focused purpose, and users will benefit from the composability and flexibility that comes from proper separation of concerns.

The toolkit server becomes the reliable infrastructure foundation that all other servers and users can depend on, while domain servers focus entirely on their specialized logic.

This is the realization of the "fleet with shared toolkit" vision - specialized vessels working together with shared, reliable infrastructure.