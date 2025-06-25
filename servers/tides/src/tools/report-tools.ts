import { z } from "zod";
import type { MCPTool } from "@packages/mcp-core/types.ts";
import { tideStorage } from "../storage/index.ts";
import type { TideData } from "../storage/index.ts";

// Schemas for tide report saving
export const SaveTideReportInputSchema = z.object({
  tide_id: z.string().describe("ID of the tide to generate a report for"),
  format: z.enum(["json", "markdown", "csv"]).describe("Report format"),
  output_path: z.string().optional().describe(
    "Custom output path (relative to reports directory)",
  ),
  include_history: z.boolean().optional().default(true).describe(
    "Include flow history in the report",
  ),
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
  output_directory: z.string().optional().describe(
    "Custom output directory (relative to reports)",
  ),
});

export const ExportAllTidesOutputSchema = z.object({
  success: z.boolean(),
  files_created: z.array(z.string()),
  total_tides: z.number(),
  export_summary: z.string(),
});

// Helper functions to get tide data from storage
async function getTideData(tide_id: string): Promise<TideData | null> {
  return await tideStorage.getTide(tide_id);
}

async function getAllTides(): Promise<TideData[]> {
  return await tideStorage.listTides();
}

function generateFileName(
  tideName: string,
  format: string,
  timestamp?: string,
): string {
  const cleanName = tideName.toLowerCase().replace(/[^a-z0-9]/g, "-");
  const timeStr = timestamp || new Date().toISOString().split("T")[0];
  return `tide-${cleanName}-${timeStr}.${format}`;
}

function generateJSONReport(
  tide: TideData,
  includeHistory: boolean,
): string {
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
        ? Math.round(
          tide.flow_history.reduce((sum, flow) => sum + flow.duration, 0) /
            tide.flow_history.length,
        )
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

function generateMarkdownReport(
  tide: TideData,
  includeHistory: boolean,
): string {
  let md = `# Tide Report: ${tide.name}\n\n`;
  md += `**ID:** ${tide.id}  \n`;
  md += `**Type:** ${tide.flow_type}  \n`;
  md += `**Status:** ${tide.status}  \n`;
  md += `**Created:** ${new Date(tide.created_at).toLocaleString()}  \n`;

  if (tide.description) {
    md += `\n## Description\n${tide.description}\n`;
  }

  md += `\n## Statistics\n`;
  const totalFlows = tide.flow_history?.length || 0;
  md += `- **Total Flows:** ${totalFlows}\n`;

  if (totalFlows > 0 && tide.flow_history) {
    const totalDuration = tide.flow_history.reduce(
      (sum, flow) => sum + flow.duration,
      0,
    );
    const avgDuration = Math.round(totalDuration / totalFlows);
    md += `- **Average Duration:** ${avgDuration} minutes\n`;
    md += `- **Total Time:** ${totalDuration} minutes (${
      (totalDuration / 60).toFixed(1)
    } hours)\n`;

    // Intensity distribution
    const intensityDist = tide.flow_history.reduce((acc, flow) => {
      acc[flow.intensity] = (acc[flow.intensity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    md += `\n### Intensity Distribution\n`;
    Object.entries(intensityDist).forEach(([intensity, count]) => {
      const percentage = ((count / totalFlows) * 100).toFixed(1);
      md += `- **${intensity}:** ${count} flows (${percentage}%)\n`;
    });
  }

  if (includeHistory && tide.flow_history && tide.flow_history.length > 0) {
    md += `\n## Flow History\n\n`;
    md += `| Date/Time | Intensity | Duration | Notes |\n`;
    md += `|-----------|-----------|----------|-------|\n`;

    tide.flow_history.forEach((flow) => {
      const date = new Date(flow.timestamp).toLocaleString();
      const notes = flow.notes || "-";
      md += `| ${date} | ${flow.intensity} | ${flow.duration}min | ${notes} |\n`;
    });
  }

  md += `\n---\n*Report generated: ${new Date().toLocaleString()}*\n`;
  return md;
}

function generateCSVReport(
  tide: TideData,
  includeHistory: boolean,
): string {
  const lines: string[] = [];

  if (includeHistory && tide.flow_history && tide.flow_history.length > 0) {
    // Detailed CSV with flow history
    lines.push(
      "Tide ID,Tide Name,Flow Type,Status,Flow Date,Intensity,Duration (min),Notes",
    );
    tide.flow_history.forEach((flow) => {
      const notes = flow.notes ? `"${flow.notes.replace(/"/g, '""')}"` : "";
      lines.push(
        `"${tide.id}","${tide.name}","${tide.flow_type}","${tide.status}","${flow.timestamp}","${flow.intensity}",${flow.duration},${notes}`,
      );
    });
  } else {
    // Summary CSV
    lines.push(
      "Tide ID,Tide Name,Flow Type,Status,Created At,Last Flow,Next Flow,Total Flows,Avg Duration (min)",
    );
    const totalFlows = tide.flow_history?.length || 0;
    const avgDuration = totalFlows > 0 && tide.flow_history
      ? Math.round(
        tide.flow_history.reduce((sum, flow) => sum + flow.duration, 0) /
          totalFlows,
      )
      : 0;

    lines.push(
      `"${tide.id}","${tide.name}","${tide.flow_type}","${tide.status}","${tide.created_at}","${
        tide.last_flow || ""
      }","${tide.next_flow || ""}",${totalFlows},${avgDuration}`,
    );
  }

  return lines.join("\n");
}

// Tool definitions
export const reportTools: MCPTool[] = [
  {
    name: "save_tide_report",
    description:
      "Save a comprehensive report for a specific tide to the reports directory",
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
          content = generateJSONReport(tide, include_history);
          break;
        case "markdown":
          content = generateMarkdownReport(tide, include_history);
          break;
        case "csv":
          content = generateCSVReport(tide, include_history);
          break;
        default:
          throw new Error(`Unsupported format: ${format}`);
      }

      // Determine file path
      const fileName = output_path || generateFileName(tide.name, format);
      const reportsDir = Deno.env.get("TIDES_REPORTS_DIR") || "/app/reports";
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

      console.error(
        `📊 Saved ${format} report for tide "${tide.name}" to ${filePath}`,
      );

      return {
        success: true,
        file_path: filePath,
        file_size: stat.size,
        tide_name: tide.name,
        format,
      };
    } catch (error) {
      throw new Error(
        `Failed to save tide report: ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
    }
  },

  export_all_tides: async (args: z.infer<typeof ExportAllTidesInputSchema>) => {
    const { format, filter, output_directory } = args;

    try {
      // Get all tides
      let tides = await getAllTides();

      // Apply filters
      if (filter?.flow_type) {
        tides = tides.filter((tide) => tide.flow_type === filter.flow_type);
      }

      if (filter?.active_only) {
        tides = tides.filter((tide) => tide.status === "active");
      }

      if (filter?.date_range) {
        const start = filter.date_range.start
          ? new Date(filter.date_range.start)
          : null;
        const end = filter.date_range.end
          ? new Date(filter.date_range.end)
          : null;

        tides = tides.filter((tide) => {
          const created = new Date(tide.created_at);
          if (start && created < start) return false;
          if (end && created > end) return false;
          return true;
        });
      }

      // Create reports
      const reportsDir = Deno.env.get("TIDES_REPORTS_DIR") || "/app/reports";
      const baseDir = output_directory
        ? `${reportsDir}/${output_directory}`
        : `${reportsDir}/exports/${new Date().toISOString().split("T")[0]}`;

      await Deno.mkdir(baseDir, { recursive: true });

      const filesCreated: string[] = [];

      for (const tide of tides) {
        let content: string;
        switch (format) {
          case "json":
            content = generateJSONReport(tide, true);
            break;
          case "markdown":
            content = generateMarkdownReport(tide, true);
            break;
          case "csv":
            content = generateCSVReport(tide, true);
            break;
          default:
            continue;
        }

        const fileName = generateFileName(tide.name, format);
        const filePath = `${baseDir}/${fileName}`;
        await Deno.writeTextFile(filePath, content);
        filesCreated.push(filePath);
      }

      const summary = `Exported ${filesCreated.length} tide reports to ${baseDir}`;
      console.error(`📊 ${summary}`);

      return {
        success: true,
        files_created: filesCreated,
        total_tides: filesCreated.length,
        export_summary: summary,
      };
    } catch (error) {
      throw new Error(
        `Failed to export tides: ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
    }
  },
};