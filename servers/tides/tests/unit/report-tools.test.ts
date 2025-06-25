import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { reportTools, reportHandlers, SaveTideReportInputSchema, SaveTideReportOutputSchema } from "../../src/tools/report-tools.ts";
import { z } from "zod";

Deno.test("Report Tools - Tool Definitions", async (t) => {
  await t.step("should export save_tide_report tool", () => {
    const saveTideReportTool = reportTools.find(tool => tool.name === "save_tide_report");
    assertExists(saveTideReportTool);
    assertEquals(saveTideReportTool.name, "save_tide_report");
    assertEquals(
      saveTideReportTool.description,
      "Save a comprehensive report for a specific tide to the reports directory"
    );
  });

  await t.step("should export export_all_tides tool", () => {
    const exportAllTidesTool = reportTools.find(tool => tool.name === "export_all_tides");
    assertExists(exportAllTidesTool);
    assertEquals(exportAllTidesTool.name, "export_all_tides");
    assertEquals(
      exportAllTidesTool.description,
      "Export reports for all tides with optional filtering"
    );
  });

  await t.step("should have correct number of tools", () => {
    assertEquals(reportTools.length, 2);
  });
});

Deno.test("Report Tools - Schema Validation", async (t) => {
  await t.step("SaveTideReportInputSchema should validate correct input", () => {
    const validInput = {
      tide_id: "tide_123",
      format: "json" as const,
      output_path: "custom/path.json",
      include_history: true
    };
    
    const result = SaveTideReportInputSchema.safeParse(validInput);
    assertEquals(result.success, true);
  });

  await t.step("SaveTideReportInputSchema should require tide_id and format", () => {
    const invalidInput = {
      output_path: "custom/path.json"
    };
    
    const result = SaveTideReportInputSchema.safeParse(invalidInput);
    assertEquals(result.success, false);
  });

  await t.step("SaveTideReportInputSchema should only accept valid formats", () => {
    const invalidFormat = {
      tide_id: "tide_123",
      format: "xml" // invalid format
    };
    
    const result = SaveTideReportInputSchema.safeParse(invalidFormat);
    assertEquals(result.success, false);
  });
});

Deno.test("Report Tools - Handler Registration", async (t) => {
  await t.step("should have save_tide_report handler", () => {
    assertExists(reportHandlers.save_tide_report);
    assertEquals(typeof reportHandlers.save_tide_report, "function");
  });

  await t.step("should have export_all_tides handler", () => {
    assertExists(reportHandlers.export_all_tides);
    assertEquals(typeof reportHandlers.export_all_tides, "function");
  });
});

// Mock test for handler functionality
Deno.test("Report Tools - save_tide_report Handler Mock", async (t) => {
  await t.step("should handle missing tide gracefully", async () => {
    try {
      await reportHandlers.save_tide_report({
        tide_id: "non_existent_tide",
        format: "json",
        include_history: true
      });
      // Should not reach here
      assertEquals(true, false, "Expected error was not thrown");
    } catch (error) {
      assertExists(error);
      assertEquals(error.message.includes("not found"), true);
    }
  });
});