# Tides Usage Guide

A complete guide to using the Tides MCP server for rhythmic productivity workflows. This guide walks you through typical sessions, report generation, and reviewing your work over multiple days.

## Table of Contents
- [Quick Start](#quick-start)
- [Understanding Tides](#understanding-tides)
- [Typical Daily Workflow](#typical-daily-workflow)
- [Flow Sessions](#flow-sessions)
- [Saving Reports to Disk](#saving-reports-to-disk)
- [Multi-Day Review](#multi-day-review)
- [Advanced Features](#advanced-features)
- [File Organization](#file-organization)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. First Time Setup
Make sure your Tides server is running with Docker volume mounting enabled. Your reports will be saved to `~/Documents/TideReports/`.

### 2. Create Your First Tide
```
Ask Claude: "Create a daily tide called 'Morning Focus' for my morning deep work sessions"
```

Expected response: Claude will use the `create_tide` tool and return something like:
```
✅ Created tide: Morning Focus (daily)
🌊 Tide ID: tide_1703123456789_abc123
📅 Next flow scheduled for tomorrow at this time
```

### 3. Start Your First Flow Session
```
Ask Claude: "Start a moderate flow session for my Morning Focus tide, 45 minutes"
```

Expected response:
```
🌊 Flow session started for Morning Focus
⏰ Duration: 45 minutes
💫 Intensity: Moderate - Maintain focused attention with deliberate action
🎯 Next actions:
- Set clear intention for this flow session
- Start timer and begin focused work
- Take mindful breaks if needed
- Capture insights and progress
```

## Understanding Tides

### Tide Types
- **Daily** - Recurring daily practices (morning routines, focus blocks)
- **Weekly** - Weekly rhythms (planning, reviews, learning sessions)
- **Project** - Sprint cycles tied to specific projects
- **Seasonal** - Quarterly or longer cycles (planning retreats, sabbaticals)

### Flow Intensities
- **Gentle** - Light, exploratory work with natural breaks (15-30 min recommended)
- **Moderate** - Balanced focused work with deliberate pacing (25-60 min recommended)  
- **Strong** - Deep, sustained concentration (60-120 min recommended)

## Typical Daily Workflow

### Morning Startup (5 minutes)
```
1. "Show me all my active tides"
2. "Start a gentle flow for my Morning Reflection tide, 20 minutes"
3. [Do your morning reflection work]
4. "Save a markdown report for my Morning Reflection tide"
```

### Mid-Day Check-in (2 minutes)
```
1. "List my daily tides"
2. "Start a strong flow for my Deep Work tide, 90 minutes"
3. [Complete focused work session]
```

### Evening Review (10 minutes)
```
1. "Save reports for all my daily tides in markdown format"
2. "Show me my tide reports from the last 3 days"
3. [Review patterns and progress]
```

## Flow Sessions

### Starting a Flow Session
```
Ask Claude: "Start a [intensity] flow for tide [name/ID], [duration] minutes"

Examples:
- "Start a gentle flow for Morning Pages, 15 minutes"
- "Start a moderate flow for my coding tide, 45 minutes"  
- "Start a strong flow for writing, 2 hours"
```

### Flow Session Guidance
When you start a flow, Claude provides:
- **Timing information** - Start time and estimated completion
- **Intensity guidance** - Specific advice for that intensity level
- **Next actions** - Checklist to optimize your session

### Example Flow Session Output
```
🌊 Starting flow session for Deep Work (strong intensity, 90min)

Flow Guidance:
"Dive deep with sustained concentration. Channel energy into meaningful progress. Push through resistance mindfully."

Next Actions:
🎯 Set clear intention for this flow session
⏰ Start timer and begin focused work
🧘 Take mindful breaks if needed
📝 Capture insights and progress
🌊 Honor the natural rhythm of the work
```

## Saving Reports to Disk

### Individual Tide Reports
```
Ask Claude: "Save a [format] report for my [tide name] tide"

Examples:
- "Save a markdown report for my Morning Reflection tide"
- "Save a JSON report for my Weekly Planning tide with full history"
- "Save a CSV report for my coding sessions tide"
```

### What Gets Saved
Your reports include:
- **Tide metadata** - Name, type, status, creation date
- **Flow statistics** - Total sessions, average duration, intensity patterns
- **Complete history** - All flow sessions with timestamps
- **Generated insights** - Patterns and productivity metrics

### Report Formats

#### Markdown Reports (Human-readable)
```
# 🌊 Tide Report: Morning Reflection

## Overview
- **ID**: tide_1703123456789_abc123
- **Type**: daily
- **Status**: active
- **Description**: Daily morning mindfulness and intention setting

## Flow Statistics
- **Total Flows**: 5
- **Average Duration**: 22 minutes
- **Intensity Distribution**:
  - Gentle: 3 flows
  - Moderate: 2 flows

## Flow History
| Date | Intensity | Duration | Notes |
|------|-----------|----------|-------|
| 12/20/2024 | gentle | 20min | - |
| 12/21/2024 | moderate | 25min | - |
```

#### JSON Reports (Data export)
```json
{
  "tide": {
    "id": "tide_1703123456789_abc123",
    "name": "Morning Reflection",
    "flow_type": "daily",
    "status": "active"
  },
  "statistics": {
    "total_flows": 5,
    "avg_duration": 22,
    "intensity_distribution": {
      "gentle": 3,
      "moderate": 2
    }
  },
  "flow_history": [...]
}
```

#### CSV Reports (Spreadsheet analysis)
```csv
tide_id,tide_name,flow_type,timestamp,intensity,duration,notes
"tide_123","Morning Reflection","daily","2024-12-20T08:00:00Z","gentle",20,""
"tide_123","Morning Reflection","daily","2024-12-21T08:15:00Z","moderate",25,""
```

## Multi-Day Review

### Reviewing Recent Work
```
Ask Claude: "Export all my daily tides as markdown reports from the last week"
```

This creates separate report files for each tide, organized by type in your `~/Documents/TideReports/` folder.

### Finding Patterns
```
Ask Claude: "Show me a summary of all my flow sessions this week"
```

Then save comprehensive reports:
```
Ask Claude: "Export all tides as JSON for analysis, only active ones"
```

### Weekly Review Workflow
```
1. "List all my tides, show only active ones"
2. "Export all active tides as markdown reports"
3. [Review generated files in ~/Documents/TideReports/]
4. "Create a weekly planning tide for next week's goals"
```

## Advanced Features

### Batch Export with Filtering
```
Ask Claude: "Export all my project tides as CSV files, active ones only"
Ask Claude: "Export all tides from December as JSON reports"
Ask Claude: "Save markdown reports for all weekly tides"
```

### Custom Report Organization
```
Ask Claude: "Save my Morning Focus tide report to a custom folder called 'december-review'"
```

### Flow Type Analysis
```
Ask Claude: "Show me all my daily tides"
Ask Claude: "Export only my weekly tides as markdown"
Ask Claude: "List project tides that are completed"
```

## File Organization

### Default Structure
Your reports are automatically organized in:
```
~/Documents/TideReports/
├── tides/
│   ├── daily/          # Daily tide reports
│   │   ├── tide-morning-reflection-2024-12-25.md
│   │   └── tide-evening-review-2024-12-25.json
│   ├── weekly/         # Weekly tide reports  
│   │   └── tide-weekly-planning-2024-12-25.md
│   ├── project/        # Project tide reports
│   │   └── tide-website-redesign-2024-12-25.csv
│   └── seasonal/       # Seasonal tide reports
└── exports/            # Batch export files
```

### File Naming Convention
- **Format**: `tide-{name}-{date}.{format}`
- **Date**: YYYY-MM-DD format
- **Name**: Lowercase with hyphens replacing spaces

### Examples
- `tide-morning-reflection-2024-12-25.md`
- `tide-weekly-planning-2024-12-25.json`
- `tide-deep-work-sessions-2024-12-25.csv`

## Troubleshooting

### "Tide not found" errors
```
1. Ask Claude: "List all my tides" to see available tide IDs
2. Use the exact tide ID from the list
3. Or use the tide name in quotes: "Morning Reflection"
```

### Reports not saving to disk
1. Check that Docker volume mounting is configured correctly
2. Verify `~/Documents/TideReports/` directory exists
3. Restart the Tides container if needed

### No flow history in reports
- Flow history is only generated when you actually use `flow_tide`
- Create some flow sessions first, then generate reports

### Finding old reports
```
Ask Claude: "Show me what tide reports I have saved"
```
Then check your `~/Documents/TideReports/` folder structure.

## Example Complete Session

Here's a realistic full day with the Tides system:

### Morning (8:00 AM)
```
You: "List my active daily tides"
Claude: Shows your Morning Reflection and Deep Work tides

You: "Start a gentle Morning Reflection flow for 20 minutes"
Claude: Provides flow guidance and timing

[You do 20 minutes of journaling/reflection]

You: "Save a markdown report for Morning Reflection"
Claude: Saves to ~/Documents/TideReports/tides/daily/tide-morning-reflection-2024-12-25.md
```

### Mid-Morning (10:00 AM)  
```
You: "Start a strong Deep Work flow for 90 minutes"
Claude: Sets up focused work session

[You complete your most important work]

You: "Save a JSON report for Deep Work with full history"
Claude: Saves detailed data export
```

### Evening (6:00 PM)
```
You: "Export all my daily tides as markdown reports"
Claude: Creates reports for all daily tides

You: "Show me my productivity patterns from this week"  
Claude: Analyzes your saved reports and flow history
```

This creates a sustainable rhythm where you're both doing focused work AND building a historical record of your productivity patterns over time.

---

*Remember: The goal isn't to track every minute, but to create sustainable rhythms that support your best work while building awareness of your natural productivity patterns.*