import { z } from "zod";
import type { MCPTool } from "@packages/mcp-core/types.ts";

// Schemas for tidal workflow management
export const CreateTideInputSchema = z.object({
  name: z.string().describe("Name of the tidal workflow"),
  flow_type: z.enum(["daily", "weekly", "project", "seasonal"]).describe("Type of tidal flow"),
  description: z.string().optional().describe("Description of the workflow"),
});

export const CreateTideOutputSchema = z.object({
  success: z.boolean(),
  tide_id: z.string(),
  name: z.string(),
  flow_type: z.string(),
  created_at: z.string(),
  next_flow: z.string().optional(),
});

export const ListTidesInputSchema = z.object({
  flow_type: z.string().optional().describe("Filter by flow type"),
  active_only: z.boolean().optional().describe("Show only active tides"),
});

export const ListTidesOutputSchema = z.object({
  tides: z.array(z.object({
    id: z.string(),
    name: z.string(),
    flow_type: z.string(),
    status: z.enum(["active", "paused", "completed"]),
    created_at: z.string(),
    last_flow: z.string().optional(),
    next_flow: z.string().optional(),
  })),
  total: z.number(),
});

export const FlowTideInputSchema = z.object({
  tide_id: z.string().describe("ID of the tide to flow"),
  intensity: z.enum(["gentle", "moderate", "strong"]).optional().describe("Flow intensity"),
  duration: z.number().optional().describe("Flow duration in minutes"),
});

export const FlowTideOutputSchema = z.object({
  success: z.boolean(),
  tide_id: z.string(),
  flow_started: z.string(),
  estimated_completion: z.string(),
  flow_guidance: z.string(),
  next_actions: z.array(z.string()),
});

// Tool definitions
export const tideTools: MCPTool[] = [
  {
    name: "create_tide",
    description: "Create a new tidal workflow for rhythmic productivity",
    inputSchema: CreateTideInputSchema,
    outputSchema: CreateTideOutputSchema,
  },
  {
    name: "list_tides",
    description: "List all tidal workflows with their current status",
    inputSchema: ListTidesInputSchema,
    outputSchema: ListTidesOutputSchema,
  },
  {
    name: "flow_tide",
    description: "Start a flow session for a specific tidal workflow",
    inputSchema: FlowTideInputSchema,
    outputSchema: FlowTideOutputSchema,
  },
];

// Tool handlers
export const tideHandlers = {
  create_tide: async (args: z.infer<typeof CreateTideInputSchema>) => {
    const { name, flow_type, description } = args;
    
    // Generate unique ID
    const tide_id = `tide_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const created_at = new Date().toISOString();
    
    // Calculate next flow based on type
    const now = new Date();
    let next_flow;
    
    switch (flow_type) {
      case "daily":
        next_flow = new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString();
        break;
      case "weekly":
        next_flow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString();
        break;
      case "project":
        // Project-based, no automatic next flow
        break;
      case "seasonal":
        next_flow = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000).toISOString();
        break;
    }
    
    // In a real implementation, this would be saved to a database
    console.log(`Creating tide: ${name} (${flow_type})`);
    
    return {
      success: true,
      tide_id,
      name,
      flow_type,
      created_at,
      next_flow,
    };
  },

  list_tides: async (args: z.infer<typeof ListTidesInputSchema>) => {
    const { flow_type, active_only = false } = args;
    
    // Mock data - in real implementation, this would come from storage
    const mockTides = [
      {
        id: "tide_1703123456789_abc123",
        name: "Morning Reflection",
        flow_type: "daily",
        status: "active" as const,
        created_at: "2024-12-20T08:00:00Z",
        last_flow: "2024-12-24T08:00:00Z",
        next_flow: "2024-12-25T08:00:00Z",
      },
      {
        id: "tide_1703123456790_def456",
        name: "Weekly Planning",
        flow_type: "weekly",
        status: "active" as const,
        created_at: "2024-12-15T10:00:00Z",
        last_flow: "2024-12-22T10:00:00Z",
        next_flow: "2024-12-29T10:00:00Z",
      },
      {
        id: "tide_1703123456791_ghi789",
        name: "Project Retrospective",
        flow_type: "project",
        status: "completed" as const,
        created_at: "2024-12-01T14:00:00Z",
        last_flow: "2024-12-20T14:00:00Z",
      },
    ];
    
    let filteredTides = mockTides;
    
    if (flow_type) {
      filteredTides = filteredTides.filter(tide => tide.flow_type === flow_type);
    }
    
    if (active_only) {
      filteredTides = filteredTides.filter(tide => tide.status === "active");
    }
    
    return {
      tides: filteredTides,
      total: filteredTides.length,
    };
  },

  flow_tide: async (args: z.infer<typeof FlowTideInputSchema>) => {
    const { tide_id, intensity = "moderate", duration = 25 } = args;
    
    const flow_started = new Date().toISOString();
    const estimated_completion = new Date(Date.now() + duration * 60 * 1000).toISOString();
    
    // Generate guidance based on intensity
    const guidanceMap = {
      gentle: "🌊 Begin with calm, steady focus. Let thoughts flow naturally without forcing. Take breaks as needed.",
      moderate: "🌊 Maintain focused attention with deliberate action. Balance effort with ease. Stay present to the work.",
      strong: "🌊 Dive deep with sustained concentration. Channel energy into meaningful progress. Push through resistance mindfully.",
    };
    
    const flow_guidance = guidanceMap[intensity];
    
    const next_actions = [
      "🎯 Set clear intention for this flow session",
      "⏰ Start timer and begin focused work",
      "🧘 Take mindful breaks if needed",
      "📝 Capture insights and progress",
      "🌊 Honor the natural rhythm of the work",
    ];
    
    console.log(`Starting flow session for tide: ${tide_id} (${intensity} intensity, ${duration}min)`);
    
    return {
      success: true,
      tide_id,
      flow_started,
      estimated_completion,
      flow_guidance,
      next_actions,
    };
  },
};