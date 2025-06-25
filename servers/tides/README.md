# Tides MCP Server

A rhythmic workflow management system inspired by natural tidal patterns. Tides helps create sustainable productivity cycles through purposeful flows and natural rhythms.

## Philosophy

Just as ocean tides follow natural cycles of ebb and flow, human productivity and creativity have natural rhythms. The Tides system helps you:

- **Recognize Natural Rhythms** - Work with your energy patterns, not against them
- **Create Sustainable Flows** - Build productive cycles that can be maintained over time  
- **Honor Rest Periods** - Embrace the necessary pauses between intense work sessions
- **Cultivate Mindful Productivity** - Stay present and intentional during work flows

## Features

### Tidal Workflows
- **Daily Tides** - Morning routines, evening reflections, focused work blocks
- **Weekly Tides** - Planning sessions, reviews, deep work periods
- **Project Tides** - Sprint cycles, creative bursts, completion phases
- **Seasonal Tides** - Quarterly planning, annual reviews, sabbaticals

### Flow Management
- **Gentle Flows** - Light, exploratory work with natural breaks
- **Moderate Flows** - Balanced focused work with deliberate pacing
- **Strong Flows** - Deep, sustained concentration for significant progress

### Rhythm Tracking
- Track flow patterns and energy levels
- Identify optimal work times and intensities
- Build sustainable long-term practices

## Quick Start

### Running the Server

```bash
# Start MCP server
deno task start

# Development mode
deno task dev

# Run tests
deno task test
```

### Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "tides": {
      "command": "deno",
      "args": ["run", "--allow-all", "/path/to/servers/tides/mcp_main.ts"]
    }
  }
}
```

## Available Tools

### Core Workflow Management
- `create_tide(name, flow_type, description?)` - Create new tidal workflow
- `list_tides(flow_type?, active_only?)` - View all workflows with status
- `flow_tide(tide_id, intensity?, duration?)` - Start a focused flow session

### Future Tools (Coming Soon)
- `pause_tide(tide_id, reason?)` - Temporarily pause a workflow
- `complete_tide(tide_id, reflection?)` - Mark workflow complete with learnings
- `analyze_patterns(timeframe?)` - Insights on productivity rhythms
- `adjust_tide(tide_id, changes)` - Modify existing workflow parameters

## Usage Examples

### Creating Your First Tide

```typescript
// Morning reflection practice
await create_tide({
  name: "Morning Pages",
  flow_type: "daily",
  description: "Stream-of-consciousness writing to clear mental space"
});

// Weekly planning session
await create_tide({
  name: "Weekly Compass",
  flow_type: "weekly", 
  description: "Set intentions and priorities for the coming week"
});
```

### Starting a Flow Session

```typescript
// Gentle morning flow
await flow_tide({
  tide_id: "tide_123_abc",
  intensity: "gentle",
  duration: 15
});

// Deep work session
await flow_tide({
  tide_id: "tide_456_def",
  intensity: "strong", 
  duration: 90
});
```

## Tidal Flow Types

### Daily Tides
- **Morning Rituals** - Meditation, journaling, intention setting
- **Focus Blocks** - 25-90 minute concentrated work periods
- **Transition Rituals** - Brief practices between major activities
- **Evening Reviews** - Reflection, gratitude, next-day preparation

### Weekly Tides  
- **Planning Sessions** - Goal setting, calendar review, priority alignment
- **Creative Exploration** - Unstructured time for new ideas
- **Administrative Flows** - Email, paperwork, system maintenance
- **Learning Blocks** - Skill development, reading, course work

### Project Tides
- **Initiation Phase** - Research, planning, team formation
- **Building Phase** - Active creation, iteration, development  
- **Completion Phase** - Finishing, polishing, delivery
- **Integration Phase** - Reflection, documentation, knowledge capture

### Seasonal Tides
- **Quarterly Reviews** - Assessment of goals and major adjustments
- **Annual Planning** - Vision setting and year-long goal creation
- **Sabbaticals** - Extended periods of rest, travel, or learning
- **Intensive Retreats** - Focused periods for major projects or life changes

## Architecture

### Core Components
- **TideManager** - Workflow creation and lifecycle management
- **FlowEngine** - Session timing and intensity management  
- **RhythmTracker** - Pattern analysis and optimization
- **MindfulnessGuide** - Presence and intention cultivation

### Data Storage
Currently uses in-memory storage for demonstration. Future versions will support:
- Local file-based storage
- Database integration
- Cloud synchronization
- Export/import capabilities

## Philosophy & Principles

### Natural Rhythms
Work with your body's natural energy cycles rather than fighting them. Honor high-energy periods with intensive work and low-energy periods with rest or gentle activities.

### Sustainable Pace
Build practices that can be maintained over months and years, not just days or weeks. Avoid burnout through intentional rest and recovery.

### Mindful Productivity
Stay present during work sessions. Quality of attention matters more than quantity of hours. Cultivate awareness of your mental and emotional state.

### Cyclical Thinking
Embrace the cyclical nature of productivity. Periods of intense creation are balanced by periods of rest, reflection, and integration.

## Development

### Adding New Tools

```typescript
// Add to src/tools/tide-tools.ts
export const newToolSchema = z.object({
  // Define input schema
});

export const newToolHandler = async (args) => {
  // Implement handler logic
  return result;
};
```

### Testing

```bash
# Run all tests
deno task test

# Run specific test file
deno test tests/tide-tools.test.ts
```

## Roadmap

### v0.2.0
- [ ] Persistent storage with file-based backend
- [ ] Pattern analysis and rhythm insights
- [ ] Integration with calendar systems
- [ ] Customizable flow templates

### v0.3.0  
- [ ] Team and collaborative tides
- [ ] Advanced analytics and reporting
- [ ] Mobile app companion
- [ ] Integration with health/fitness trackers

### v1.0.0
- [ ] Production-ready storage backend
- [ ] Full API for third-party integrations
- [ ] Comprehensive documentation
- [ ] Enterprise features

---

*"The sea, once it casts its spell, holds one in its net of wonder forever."* - Jacques Cousteau