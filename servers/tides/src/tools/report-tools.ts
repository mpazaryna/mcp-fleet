import { z } from "zod";
import type { MCPTool } from "@packages/mcp-core/types.ts";

// Schemas for tide report saving
export const SaveTideReportInputSchema = z.object({
  tide_id: z.string().describe("ID of the tide to generate a report for"),
  format: z.enum(["json", "markdown", "csv"]).describe("Report format"),
  output_path: z.string().optional().describe("Custom output path (relative to reports directory)"),
  include_history: z.boolean().optional().default(true).describe("Include flow history in the report"),
});

export const SaveTideReportOutputSchema = z.object({
  success: z.boolean(),
  file_path: z.string(),
  file_size: z.number(),
  tide_name: z.string(),
  format: z.string(),
});

export const ExportAllTidesInputSchema = z.object({
  format: z.enum(["json", "markdown", "csv"]).describe("Export format"),
  filter: z.object({
    flow_type: z.string().optional().describe("Filter by flow type"),
    active_only: z.boolean().optional().describe("Export only active tides"),
    date_range: z.object({
      start: z.string().optional(),
      end: z.string().optional(),
    }).optional().describe("Date range filter"),
  }).optional(),
  output_directory: z.string().optional().describe("Custom output directory (relative to reports)"),
});

export const ExportAllTidesOutputSchema = z.object({
  success: z.boolean(),
  files_created: z.array(z.string()),
  total_tides: z.number(),
  export_summary: z.string(),
});

// Report generation utilities
interface TideData {
  id: string;
  name: string;
  flow_type: string;
  status: "active" | "paused" | "completed";
  created_at: string;
  last_flow?: string;
  next_flow?: string;
  description?: string;
  flow_history?: Array<{
    timestamp: string;
    intensity: string;
    duration: number;
    notes?: string;
  }>;
}

// Mock tide data store (in real implementation, this would come from a database)
const mockTideData: Record<string, TideData> = {
  "tide_1703123456789_abc123": {
    id: "tide_1703123456789_abc123",
    name: "Morning Reflection",
    flow_type: "daily",
    status: "active",
    created_at: "2024-12-20T08:00:00Z",
    last_flow: "2024-12-24T08:00:00Z",
    next_flow: "2024-12-25T08:00:00Z",
    description: "Daily morning mindfulness and intention setting",
    flow_history: [
      { timestamp: "2024-12-20T08:00:00Z", intensity: "gentle", duration: 20 },
      { timestamp: "2024-12-21T08:15:00Z", intensity: "moderate", duration: 25 },
      { timestamp: "2024-12-22T08:00:00Z", intensity: "gentle", duration: 15 },
      { timestamp: "2024-12-23T08:30:00Z", intensity: "moderate", duration: 30 },
      { timestamp: "2024-12-24T08:00:00Z", intensity: "gentle", duration: 20 },
    ]
  },
  "tide_1703123456790_def456": {
    id: "tide_1703123456790_def456",
    name: "Weekly Planning",
    flow_type: "weekly",
    status: "active",
    created_at: "2024-12-15T10:00:00Z",
    last_flow: "2024-12-22T10:00:00Z",
    next_flow: "2024-12-29T10:00:00Z",
    description: "Weekly review and planning session",
    flow_history: [
      { timestamp: "2024-12-15T10:00:00Z", intensity: "moderate", duration: 60 },
      { timestamp: "2024-12-22T10:00:00Z", intensity: "strong", duration: 90 },
    ]
  }
};

async function getTideData(tide_id: string): Promise<TideData | null> {
  // In real implementation, this would query a database
  return mockTideData[tide_id] || null;
}

async function getAllTides(): Promise<TideData[]> {
  // In real implementation, this would query a database
  return Object.values(mockTideData);
}

function generateFileName(tideName: string, format: string, timestamp?: string): string {
  const cleanName = tideName.toLowerCase().replace(/[^a-z0-9]/g, '-');
  const timeStr = timestamp || new Date().toISOString().split('T')[0];
  return `tide-${cleanName}-${timeStr}.${format}`;
}

async function generateJSONReport(tide: TideData, includeHistory: boolean): Promise<string> {
  const report = {
    tide: {
      id: tide.id,
      name: tide.name,
      flow_type: tide.flow_type,
      status: tide.status,
      created_at: tide.created_at,
      last_flow: tide.last_flow,
      next_flow: tide.next_flow,
      description: tide.description,
    },
    statistics: {
      total_flows: tide.flow_history?.length || 0,
      avg_duration: tide.flow_history?.length 
        ? Math.round(tide.flow_history.reduce((sum, flow) => sum + flow.duration, 0) / tide.flow_history.length)
        : 0,
      intensity_distribution: tide.flow_history?.reduce((acc, flow) => {
        acc[flow.intensity] = (acc[flow.intensity] || 0) + 1;
        return acc;
      }, {} as Record<string, number>) || {},
    },
    flow_history: includeHistory ? tide.flow_history : undefined,
    generated_at: new Date().toISOString(),
  };
  
  return JSON.stringify(report, null, 2);
}

async function generateMarkdownReport(tide: TideData, includeHistory: boolean): Promise<string> {
  const stats = tide.flow_history?.length 
    ? {
        total: tide.flow_history.length,
        avgDuration: Math.round(tide.flow_history.reduce((sum, flow) => sum + flow.duration, 0) / tide.flow_history.length),
        intensityDist: tide.flow_history.reduce((acc, flow) => {
          acc[flow.intensity] = (acc[flow.intensity] || 0) + 1;
          return acc;
        }, {} as Record<string, number>)
      }
    : { total: 0, avgDuration: 0, intensityDist: {} };

  let markdown = `# 🌊 Tide Report: ${tide.name}

## Overview
- **ID**: ${tide.id}
- **Type**: ${tide.flow_type}
- **Status**: ${tide.status}
- **Created**: ${new Date(tide.created_at).toLocaleDateString()}
- **Description**: ${tide.description || 'No description'}

## Flow Statistics
- **Total Flows**: ${stats.total}
- **Average Duration**: ${stats.avgDuration} minutes
- **Last Flow**: ${tide.last_flow ? new Date(tide.last_flow).toLocaleDateString() : 'Never'}
- **Next Flow**: ${tide.next_flow ? new Date(tide.next_flow).toLocaleDateString() : 'Not scheduled'}

### Intensity Distribution
${Object.entries(stats.intensityDist).map(([intensity, count]) => 
  `- **${intensity.charAt(0).toUpperCase() + intensity.slice(1)}**: ${count} flows`
).join('\n')}
`;

  if (includeHistory && tide.flow_history?.length) {
    markdown += `
## Flow History

| Date | Intensity | Duration | Notes |
|------|-----------|----------|-------|
${tide.flow_history.map(flow => 
  `| ${new Date(flow.timestamp).toLocaleDateString()} | ${flow.intensity} | ${flow.duration}min | ${flow.notes || '-'} |`
).join('\n')}
`;
  }

  markdown += `

---
*Report generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}*
`;

  return markdown;
}

async function generateCSVReport(tide: TideData, includeHistory: boolean): Promise<string> {
  if (!includeHistory || !tide.flow_history?.length) {
    // Basic tide info as CSV
    return `id,name,flow_type,status,created_at,last_flow,next_flow,description
"${tide.id}","${tide.name}","${tide.flow_type}","${tide.status}","${tide.created_at}","${tide.last_flow || ''}","${tide.next_flow || ''}","${tide.description || ''}"`;
  }

  // Flow history as CSV
  let csv = `tide_id,tide_name,flow_type,timestamp,intensity,duration,notes\n`;
  for (const flow of tide.flow_history) {
    csv += `"${tide.id}","${tide.name}","${tide.flow_type}","${flow.timestamp}","${flow.intensity}",${flow.duration},"${flow.notes || ''}"\n`;
  }
  return csv;
}

// Tool definitions
export const reportTools: MCPTool[] = [
  {
    name: "save_tide_report",
    description: "Save a comprehensive report for a specific tide to the reports directory",
    inputSchema: SaveTideReportInputSchema,
    outputSchema: SaveTideReportOutputSchema,
  },
  {
    name: "export_all_tides",
    description: "Export reports for all tides with optional filtering",
    inputSchema: ExportAllTidesInputSchema,
    outputSchema: ExportAllTidesOutputSchema,
  },
];

// Tool handlers
export const reportHandlers = {
  save_tide_report: async (args: z.infer<typeof SaveTideReportInputSchema>) => {
    const { tide_id, format, output_path, include_history } = args;
    
    try {
      // Get tide data
      const tide = await getTideData(tide_id);
      if (!tide) {
        throw new Error(`Tide with ID ${tide_id} not found`);
      }

      // Generate report content
      let content: string;
      switch (format) {
        case "json":
          content = await generateJSONReport(tide, include_history);
          break;
        case "markdown":
          content = await generateMarkdownReport(tide, include_history);
          break;
        case "csv":
          content = await generateCSVReport(tide, include_history);
          break;
        default:
          throw new Error(`Unsupported format: ${format}`);
      }

      // Determine file path
      const fileName = output_path || generateFileName(tide.name, format);
      const reportsDir = "/app/reports";
      const subDir = `${reportsDir}/tides/${tide.flow_type}`;
      const filePath = `${subDir}/${fileName}`;

      // Ensure directory exists
      try {
        await Deno.mkdir(subDir, { recursive: true });
      } catch {
        // Directory might already exist, ignore error
      }

      // Write file
      await Deno.writeTextFile(filePath, content);
      const stat = await Deno.stat(filePath);

      console.log(`📊 Saved ${format} report for tide "${tide.name}" to ${filePath}`);

      return {
        success: true,
        file_path: filePath,
        file_size: stat.size,
        tide_name: tide.name,
        format,
      };
    } catch (error) {
      throw new Error(`Failed to save tide report: ${error instanceof Error ? error.message : String(error)}`);
    }
  },

  export_all_tides: async (args: z.infer<typeof ExportAllTidesInputSchema>) => {
    const { format, filter, output_directory } = args;
    
    try {
      // Get all tides
      let tides = await getAllTides();
      
      // Apply filters
      if (filter?.flow_type) {
        tides = tides.filter(tide => tide.flow_type === filter.flow_type);
      }
      
      if (filter?.active_only) {
        tides = tides.filter(tide => tide.status === "active");
      }
      
      if (filter?.date_range) {
        const startDate = filter.date_range.start ? new Date(filter.date_range.start) : null;
        const endDate = filter.date_range.end ? new Date(filter.date_range.end) : null;
        
        tides = tides.filter(tide => {
          const createdDate = new Date(tide.created_at);
          if (startDate && createdDate < startDate) return false;
          if (endDate && createdDate > endDate) return false;
          return true;
        });
      }

      const filesCreated: string[] = [];
      const timestamp = new Date().toISOString().split('T')[0];
      
      // Export each tide
      for (const tide of tides) {
        try {
          const saveResult = await reportHandlers.save_tide_report({
            tide_id: tide.id,
            format,
            output_path: output_directory 
              ? `${output_directory}/${generateFileName(tide.name, format, timestamp)}`
              : undefined,
            include_history: true,
          });
          
          if (saveResult.success) {
            filesCreated.push(saveResult.file_path);
          }
        } catch (error) {
          console.error(`Failed to export tide ${tide.name}:`, error);
        }
      }

      const exportSummary = `Exported ${filesCreated.length} of ${tides.length} tides in ${format} format${filter ? ' with filters applied' : ''}`;
      
      console.log(`📦 ${exportSummary}`);

      return {
        success: true,
        files_created: filesCreated,
        total_tides: tides.length,
        export_summary: exportSummary,
      };
    } catch (error) {
      throw new Error(`Failed to export all tides: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
};