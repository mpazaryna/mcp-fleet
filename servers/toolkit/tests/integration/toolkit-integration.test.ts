import { assertEquals, assertExists, assert } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { fileHandlers } from "../../src/tools/file-tools.ts";

const TEST_DIR = "/tmp/toolkit-integration-test";

Deno.test("Toolkit Integration - Complete File Workflow", async (t) => {
  const setup = async () => {
    try {
      await Deno.remove(TEST_DIR, { recursive: true });
    } catch {
      // Ignore if doesn't exist
    }
  };

  const teardown = async () => {
    try {
      await Deno.remove(TEST_DIR, { recursive: true });
    } catch {
      // Ignore
    }
  };

  await t.step("Complete workflow: create directory, write files, read, list, delete", async () => {
    await setup();

    // 1. Create directory structure
    const reportsDir = `${TEST_DIR}/reports/tides/daily`;
    const createDirResult = await fileHandlers.create_directory({
      dir_path: reportsDir,
      recursive: true
    });
    assertEquals(createDirResult.success, true);

    // 2. Write multiple files
    const file1 = `${reportsDir}/morning-routine.json`;
    const file1Content = JSON.stringify({
      name: "Morning Routine",
      type: "daily",
      flows: [
        { timestamp: "2024-01-01T06:00:00Z", intensity: "gentle", duration: 20 }
      ]
    }, null, 2);

    const writeResult1 = await fileHandlers.write_file({
      file_path: file1,
      content: file1Content,
      create_dirs: false, // Directory already exists
      encoding: "utf8"
    });
    assertEquals(writeResult1.success, true);

    const file2 = `${reportsDir}/evening-shutdown.md`;
    const file2Content = `# Evening Shutdown Report

## Statistics
- Total Flows: 5
- Average Duration: 25 minutes

## Flow History
| Time | Intensity | Duration |
|------|-----------|----------|
| 18:00 | moderate | 25min |
`;

    const writeResult2 = await fileHandlers.write_file({
      file_path: file2,
      content: file2Content,
      create_dirs: false,
      encoding: "utf8"
    });
    assertEquals(writeResult2.success, true);

    // 3. List files in directory
    const listResult = await fileHandlers.list_files({
      dir_path: reportsDir,
      include_dirs: false,
      recursive: false
    });
    assertEquals(listResult.success, true);
    assertEquals(listResult.total, 2);
    assert(listResult.files.some(f => f.name === "morning-routine.json"));
    assert(listResult.files.some(f => f.name === "evening-shutdown.md"));

    // 4. Read files back
    const readResult1 = await fileHandlers.read_file({
      file_path: file1,
      encoding: "utf8"
    });
    assertEquals(readResult1.success, true);
    assertEquals(readResult1.content, file1Content);

    const readResult2 = await fileHandlers.read_file({
      file_path: file2,
      encoding: "utf8"
    });
    assertEquals(readResult2.success, true);
    assertEquals(readResult2.content, file2Content);

    // 5. Create subdirectory and more files
    const subDir = `${reportsDir}/archives`;
    await fileHandlers.create_directory({
      dir_path: subDir,
      recursive: true
    });

    await fileHandlers.write_file({
      file_path: `${subDir}/old-report.txt`,
      content: "This is an archived report",
      create_dirs: false,
      encoding: "utf8"
    });

    // 6. List files recursively
    const recursiveListResult = await fileHandlers.list_files({
      dir_path: reportsDir,
      include_dirs: true,
      recursive: true
    });
    assertEquals(recursiveListResult.success, true);
    assert(recursiveListResult.total >= 4); // 2 files + 1 subdir + 1 file in subdir

    // 7. Delete specific file
    const deleteResult = await fileHandlers.delete_file({
      file_path: `${subDir}/old-report.txt`,
      recursive: false
    });
    assertEquals(deleteResult.success, true);
    assertEquals(deleteResult.deleted, true);

    // 8. Delete entire directory
    const deleteDirResult = await fileHandlers.delete_file({
      file_path: subDir,
      recursive: true
    });
    assertEquals(deleteDirResult.success, true);

    await teardown();
  });

  await t.step("Pattern matching and filtering", async () => {
    await setup();

    const testDir = `${TEST_DIR}/pattern-test`;
    await fileHandlers.create_directory({ dir_path: testDir, recursive: true });

    // Create various files
    const files = [
      "report-2024-01-01.json",
      "report-2024-01-02.json", 
      "report-2024-01-03.md",
      "config.yaml",
      "README.md",
      "data.csv"
    ];

    for (const file of files) {
      await fileHandlers.write_file({
        file_path: `${testDir}/${file}`,
        content: `Content of ${file}`,
        create_dirs: false,
        encoding: "utf8"
      });
    }

    // Test pattern matching for JSON files
    const jsonListResult = await fileHandlers.list_files({
      dir_path: testDir,
      pattern: "*.json",
      include_dirs: false,
      recursive: false
    });
    assertEquals(jsonListResult.success, true);
    assertEquals(jsonListResult.total, 2);
    assert(jsonListResult.files.every(f => f.name.endsWith(".json")));

    // Test pattern matching for report files
    const reportListResult = await fileHandlers.list_files({
      dir_path: testDir,
      pattern: "report-*",
      include_dirs: false,
      recursive: false
    });
    assertEquals(reportListResult.success, true);
    assertEquals(reportListResult.total, 3);
    assert(reportListResult.files.every(f => f.name.startsWith("report-")));

    await teardown();
  });

  await t.step("Base64 encoding support", async () => {
    await setup();

    const testDir = `${TEST_DIR}/base64-test`;
    await fileHandlers.create_directory({ dir_path: testDir, recursive: true });

    // Create binary-like content encoded as base64
    const binaryContent = "Hello, World! This is binary data: \x00\x01\x02\x03";
    const base64Content = btoa(binaryContent);

    const binaryFile = `${testDir}/binary-data.bin`;
    
    // Write as base64
    const writeResult = await fileHandlers.write_file({
      file_path: binaryFile,
      content: base64Content,
      create_dirs: false,
      encoding: "base64"
    });
    assertEquals(writeResult.success, true);

    // Read back as base64
    const readResult = await fileHandlers.read_file({
      file_path: binaryFile,
      encoding: "base64"
    });
    assertEquals(readResult.success, true);
    assertEquals(readResult.content, base64Content);

    // Verify the actual file contains the decoded binary data
    const actualBytes = await Deno.readFile(binaryFile);
    const decodedContent = new TextDecoder().decode(actualBytes);
    assertEquals(decodedContent, binaryContent);

    await teardown();
  });

  await t.step("Error handling and edge cases", async () => {
    await setup();

    // Test handling of non-existent directory
    try {
      await fileHandlers.list_files({
        dir_path: "/absolutely/non/existent/directory",
        include_dirs: true,
        recursive: false
      });
      assert(false, "Should have thrown error");
    } catch (error) {
      assertExists(error);
      assert((error as Error).message.includes("Failed to list files"));
    }

    // Test deleting non-existent file (should succeed without error)
    const deleteResult = await fileHandlers.delete_file({
      file_path: "/non/existent/file.txt",
      recursive: false
    });
    assertEquals(deleteResult.success, true);
    assertEquals(deleteResult.deleted, false);

    // Test creating directory that already exists
    const tempDir = `${TEST_DIR}/already-exists`;
    await Deno.mkdir(tempDir, { recursive: true });

    const createResult = await fileHandlers.create_directory({
      dir_path: tempDir,
      recursive: true
    });
    assertEquals(createResult.success, true);
    assertEquals(createResult.created, false);
    assertEquals(createResult.already_exists, true);

    await teardown();
  });
});