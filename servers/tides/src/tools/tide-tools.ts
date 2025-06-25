import { z } from "zod";
import type { MCPTool } from "@packages/mcp-core/types.ts";
import { tideStorage } from "../storage/index.ts";

// Schemas for tidal workflow management
export const CreateTideInputSchema = z.object({
  name: z.string().describe("Name of the tidal workflow"),
  flow_type: z.enum(["daily", "weekly", "project", "seasonal"]).describe(
    "Type of tidal flow",
  ),
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
  intensity: z.enum(["gentle", "moderate", "strong"]).optional().describe(
    "Flow intensity",
  ),
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

    try {
      const tide = await tideStorage.createTide({
        name,
        flow_type,
        description
      });

      console.error(`Creating tide: ${name} (${flow_type})`);

      return {
        success: true,
        tide_id: tide.id,
        name: tide.name,
        flow_type: tide.flow_type,
        created_at: tide.created_at,
        next_flow: tide.next_flow,
      };
    } catch (error) {
      console.error("Failed to create tide:", error);
      return {
        success: false,
        tide_id: "",
        name,
        flow_type,
        created_at: new Date().toISOString(),
      };
    }
  },

  list_tides: async (args: z.infer<typeof ListTidesInputSchema>) => {
    const { flow_type, active_only = false } = args;

    try {
      const tides = await tideStorage.listTides({
        flow_type,
        active_only
      });

      return {
        tides: tides.map(tide => ({
          id: tide.id,
          name: tide.name,
          flow_type: tide.flow_type,
          status: tide.status,
          created_at: tide.created_at,
          last_flow: tide.last_flow,
          next_flow: tide.next_flow,
        })),
        total: tides.length,
      };
    } catch (error) {
      console.error("Failed to list tides:", error);
      return {
        tides: [],
        total: 0,
      };
    }
  },

  flow_tide: async (args: z.infer<typeof FlowTideInputSchema>) => {
    const { tide_id, intensity = "moderate", duration = 25 } = args;

    try {
      // Verify tide exists
      const tide = await tideStorage.getTide(tide_id);
      if (!tide) {
        return {
          success: false,
          tide_id,
          flow_started: "",
          estimated_completion: "",
          flow_guidance: "Tide not found",
          next_actions: [],
        };
      }

      const flow_started = new Date().toISOString();
      const estimated_completion = new Date(
        Date.now() + duration * 60 * 1000,
      ).toISOString();

      // Add flow to tide history
      await tideStorage.addFlowToTide(tide_id, {
        timestamp: flow_started,
        intensity,
        duration,
      });

      // Generate guidance based on intensity
      const guidanceMap = {
        gentle:
          "🌊 Begin with calm, steady focus. Let thoughts flow naturally without forcing. Take breaks as needed.",
        moderate:
          "🌊 Maintain focused attention with deliberate action. Balance effort with ease. Stay present to the work.",
        strong:
          "🌊 Dive deep with sustained concentration. Channel energy into meaningful progress. Push through resistance mindfully.",
      };

      const flow_guidance = guidanceMap[intensity];

      const next_actions = [
        "🎯 Set clear intention for this flow session",
        "⏰ Start timer and begin focused work",
        "🧘 Take mindful breaks if needed",
        "📝 Capture insights and progress",
        "🌊 Honor the natural rhythm of the work",
      ];

      console.error(
        `Starting flow session for tide: ${tide_id} (${intensity} intensity, ${duration}min)`,
      );

      return {
        success: true,
        tide_id,
        flow_started,
        estimated_completion,
        flow_guidance,
        next_actions,
      };
    } catch (error) {
      console.error("Failed to start flow:", error);
      return {
        success: false,
        tide_id,
        flow_started: "",
        estimated_completion: "",
        flow_guidance: "Failed to start flow session",
        next_actions: [],
      };
    }
  },
};