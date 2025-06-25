import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { tideHandlers } from "../../src/tools/tide-tools.ts";
import { reportHandlers } from "../../src/tools/report-tools.ts";
import { TideStorage } from "../../src/storage/tide-storage.ts";

// Test data directory
const TEST_DATA_DIR = "/tmp/tides-integration-test";

Deno.test("Tides Persistence Integration", async (t) => {
  // Override the default storage for testing
  const originalDataEnv = Deno.env.get("TIDES_DATA_DIR");
  const originalReportsEnv = Deno.env.get("TIDES_REPORTS_DIR");
  Deno.env.set("TIDES_DATA_DIR", TEST_DATA_DIR);
  Deno.env.set("TIDES_REPORTS_DIR", TEST_DATA_DIR);

  const setup = async () => {
    await Deno.mkdir(TEST_DATA_DIR, { recursive: true });
  };

  const teardown = async () => {
    try {
      await Deno.remove(TEST_DATA_DIR, { recursive: true });
    } catch {
      // Ignore
    }
    // Restore original env
    if (originalDataEnv) {
      Deno.env.set("TIDES_DATA_DIR", originalDataEnv);
    } else {
      Deno.env.delete("TIDES_DATA_DIR");
    }
    if (originalReportsEnv) {
      Deno.env.set("TIDES_REPORTS_DIR", originalReportsEnv);
    } else {
      Deno.env.delete("TIDES_REPORTS_DIR");
    }
  };

  await t.step("Full workflow: create, list, flow, and report", async () => {
    await setup();

    // 1. Create a tide
    const createResult = await tideHandlers.create_tide({
      name: "Integration Test Tide",
      flow_type: "daily",
      description: "Testing full persistence workflow"
    });

    assertEquals(createResult.success, true);
    assertExists(createResult.tide_id);
    const tideId = createResult.tide_id;

    // 2. List tides - should include our new tide
    const listResult = await tideHandlers.list_tides({});
    assertEquals(listResult.total, 1);
    assertEquals(listResult.tides[0].name, "Integration Test Tide");

    // 3. Start a flow session
    const flowResult = await tideHandlers.flow_tide({
      tide_id: tideId,
      intensity: "moderate",
      duration: 30
    });

    assertEquals(flowResult.success, true);
    assertExists(flowResult.flow_started);

    // 4. List tides again - should show last_flow updated
    const listResult2 = await tideHandlers.list_tides({});
    assertExists(listResult2.tides[0].last_flow);

    // 5. Generate a report
    const reportResult = await reportHandlers.save_tide_report({
      tide_id: tideId,
      format: "markdown",
      include_history: true
    });

    assertEquals(reportResult.success, true);
    assertExists(reportResult.file_path);
    assertEquals(reportResult.tide_name, "Integration Test Tide");

    await teardown();
  });

  await t.step("Persistence across handler calls", async () => {
    await teardown();
    await setup();

    // Create multiple tides
    const tide1 = await tideHandlers.create_tide({
      name: "Morning Meditation",
      flow_type: "daily"
    });

    const tide2 = await tideHandlers.create_tide({
      name: "Weekly Planning", 
      flow_type: "weekly"
    });

    const tide3 = await tideHandlers.create_tide({
      name: "Project Alpha",
      flow_type: "project"
    });

    // List all
    const allTides = await tideHandlers.list_tides({});
    assertEquals(allTides.total, 3);

    // Filter by type
    const dailyTides = await tideHandlers.list_tides({ flow_type: "daily" });
    assertEquals(dailyTides.total, 1);
    assertEquals(dailyTides.tides[0].name, "Morning Meditation");

    const weeklyTides = await tideHandlers.list_tides({ flow_type: "weekly" });
    assertEquals(weeklyTides.total, 1);
    assertEquals(weeklyTides.tides[0].name, "Weekly Planning");

    await teardown();
  });

  await t.step("Export all tides functionality", async () => {
    await teardown();
    await setup();

    // Create test tides
    await tideHandlers.create_tide({
      name: "Export Test 1",
      flow_type: "daily"
    });

    await tideHandlers.create_tide({
      name: "Export Test 2",
      flow_type: "weekly"
    });

    // Export all as JSON
    const exportResult = await reportHandlers.export_all_tides({
      format: "json"
    });

    assertEquals(exportResult.success, true);
    assertEquals(exportResult.total_tides, 2);
    assertEquals(exportResult.files_created.length, 2);

    await teardown();
  });

  await t.step("Handle non-existent tide gracefully", async () => {
    await teardown();
    await setup();

    // Try to flow a non-existent tide
    const flowResult = await tideHandlers.flow_tide({
      tide_id: "non_existent_tide_12345"
    });

    assertEquals(flowResult.success, false);
    assertEquals(flowResult.flow_guidance, "Tide not found");

    // Try to save report for non-existent tide
    try {
      await reportHandlers.save_tide_report({
        tide_id: "non_existent_tide_12345",
        format: "json",
        include_history: true
      });
      // Should not reach here
      assertEquals(true, false, "Expected error was not thrown");
    } catch (error) {
      assertExists(error);
      assertEquals((error as Error).message.includes("not found"), true);
    }

    await teardown();
  });
});