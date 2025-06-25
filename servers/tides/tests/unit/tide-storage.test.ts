import { assertEquals, assertExists, assert } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { TideStorage } from "../../src/storage/tide-storage.ts";
import { join } from "https://deno.land/std@0.208.0/path/mod.ts";

// Test data directory
const TEST_DATA_DIR = "/tmp/tides-test-data";

Deno.test("TideStorage - Persistence Tests", async (t) => {
  // Setup and teardown for each test
  const setup = async () => {
    await Deno.mkdir(TEST_DATA_DIR, { recursive: true });
    return new TideStorage(TEST_DATA_DIR);
  };

  const teardown = async () => {
    try {
      await Deno.remove(TEST_DATA_DIR, { recursive: true });
    } catch {
      // Ignore if directory doesn't exist
    }
  };

  await t.step("should create and persist a new tide", async () => {
    const storage = await setup();
    
    const tideData = {
      name: "Test Tide",
      flow_type: "daily" as const,
      description: "Test description"
    };

    const result = await storage.createTide(tideData);
    
    assertExists(result.id);
    assertEquals(result.name, "Test Tide");
    assertEquals(result.flow_type, "daily");
    assertEquals(result.status, "active");
    assertExists(result.created_at);

    // Verify it's persisted
    const retrieved = await storage.getTide(result.id);
    assertExists(retrieved);
    assertEquals(retrieved.id, result.id);
    assertEquals(retrieved.name, result.name);

    await teardown();
  });

  await t.step("should list all persisted tides", async () => {
    const storage = await setup();
    
    // Create multiple tides
    await storage.createTide({
      name: "Morning Routine",
      flow_type: "daily",
      description: "Morning activities"
    });

    await storage.createTide({
      name: "Weekly Review",
      flow_type: "weekly",
      description: "Weekly planning"
    });

    const tides = await storage.listTides();
    assertEquals(tides.length, 2);
    
    const names = tides.map(t => t.name).sort();
    assertEquals(names, ["Morning Routine", "Weekly Review"]);

    await teardown();
  });

  await t.step("should filter tides by flow_type", async () => {
    const storage = await setup();
    
    await storage.createTide({ name: "Daily 1", flow_type: "daily" });
    await storage.createTide({ name: "Daily 2", flow_type: "daily" });
    await storage.createTide({ name: "Weekly 1", flow_type: "weekly" });

    const dailyTides = await storage.listTides({ flow_type: "daily" });
    assertEquals(dailyTides.length, 2);
    
    const weeklyTides = await storage.listTides({ flow_type: "weekly" });
    assertEquals(weeklyTides.length, 1);

    await teardown();
  });

  await t.step("should filter active tides only", async () => {
    const storage = await setup();
    
    const tide1 = await storage.createTide({ name: "Active Tide", flow_type: "daily" });
    const tide2 = await storage.createTide({ name: "Completed Tide", flow_type: "project" });
    
    // Mark tide2 as completed
    await storage.updateTide(tide2.id, { status: "completed" });

    const activeTides = await storage.listTides({ active_only: true });
    assertEquals(activeTides.length, 1);
    assertEquals(activeTides[0].name, "Active Tide");

    await teardown();
  });

  await t.step("should update tide flow history", async () => {
    const storage = await setup();
    
    const tide = await storage.createTide({ name: "Flow Test", flow_type: "daily" });
    
    const flowData = {
      timestamp: new Date().toISOString(),
      intensity: "moderate" as const,
      duration: 30,
      notes: "Good session"
    };

    await storage.addFlowToTide(tide.id, flowData);

    const updated = await storage.getTide(tide.id);
    assertExists(updated);
    assertEquals(updated.flow_history.length, 1);
    assertEquals(updated.flow_history[0].intensity, "moderate");
    assertEquals(updated.flow_history[0].duration, 30);

    await teardown();
  });

  await t.step("should persist across storage instances", async () => {
    // First instance creates a tide
    const storage1 = await setup();
    const tide = await storage1.createTide({ 
      name: "Persistent Tide", 
      flow_type: "daily" 
    });

    // Second instance should be able to read it
    const storage2 = new TideStorage(TEST_DATA_DIR);
    const retrieved = await storage2.getTide(tide.id);
    
    assertExists(retrieved);
    assertEquals(retrieved.name, "Persistent Tide");

    await teardown();
  });

  await t.step("should handle non-existent tide gracefully", async () => {
    const storage = await setup();
    
    const result = await storage.getTide("non_existent_id");
    assertEquals(result, null);

    await teardown();
  });

  await t.step("should save tide data as JSON files", async () => {
    const storage = await setup();
    
    const tide = await storage.createTide({ 
      name: "File Test", 
      flow_type: "daily" 
    });

    // Check if file exists
    const filePath = join(TEST_DATA_DIR, `${tide.id}.json`);
    const fileInfo = await Deno.stat(filePath);
    assert(fileInfo.isFile);

    // Verify file contents
    const fileContent = await Deno.readTextFile(filePath);
    const data = JSON.parse(fileContent);
    assertEquals(data.name, "File Test");
    assertEquals(data.id, tide.id);

    await teardown();
  });
});