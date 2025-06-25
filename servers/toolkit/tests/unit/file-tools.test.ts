import { assertEquals, assertExists, assert } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { fileTools, fileHandlers, WriteFileInputSchema, ReadFileInputSchema } from "../../src/tools/file-tools.ts";

// Test data directory
const TEST_DIR = "/tmp/toolkit-test";

Deno.test("File Tools - Tool Definitions", async (t) => {
  await t.step("should export write_file tool", () => {
    const writeFileTool = fileTools.find(tool => tool.name === "write_file");
    assertExists(writeFileTool);
    assertEquals(writeFileTool.name, "write_file");
    assertEquals(writeFileTool.description, "Write content to a file, creating directories as needed");
  });

  await t.step("should export read_file tool", () => {
    const readFileTool = fileTools.find(tool => tool.name === "read_file");
    assertExists(readFileTool);
    assertEquals(readFileTool.name, "read_file");
    assertEquals(readFileTool.description, "Read content from a file");
  });

  await t.step("should export create_directory tool", () => {
    const createDirTool = fileTools.find(tool => tool.name === "create_directory");
    assertExists(createDirTool);
    assertEquals(createDirTool.name, "create_directory");
  });

  await t.step("should export list_files tool", () => {
    const listFilesTool = fileTools.find(tool => tool.name === "list_files");
    assertExists(listFilesTool);
    assertEquals(listFilesTool.name, "list_files");
  });

  await t.step("should export delete_file tool", () => {
    const deleteFileTool = fileTools.find(tool => tool.name === "delete_file");
    assertExists(deleteFileTool);
    assertEquals(deleteFileTool.name, "delete_file");
  });

  await t.step("should have correct number of tools", () => {
    assertEquals(fileTools.length, 5);
  });
});

Deno.test("File Tools - Schema Validation", async (t) => {
  await t.step("WriteFileInputSchema should validate correct input", () => {
    const validInput = {
      file_path: "/test/file.txt",
      content: "test content",
      create_dirs: true,
      encoding: "utf8" as const
    };
    
    const result = WriteFileInputSchema.safeParse(validInput);
    assertEquals(result.success, true);
  });

  await t.step("WriteFileInputSchema should require file_path and content", () => {
    const invalidInput = {
      create_dirs: true
    };
    
    const result = WriteFileInputSchema.safeParse(invalidInput);
    assertEquals(result.success, false);
  });

  await t.step("ReadFileInputSchema should validate correct input", () => {
    const validInput = {
      file_path: "/test/file.txt",
      encoding: "utf8" as const
    };
    
    const result = ReadFileInputSchema.safeParse(validInput);
    assertEquals(result.success, true);
  });
});

Deno.test("File Tools - Handler Registration", async (t) => {
  await t.step("should have write_file handler", () => {
    assertExists(fileHandlers.write_file);
    assertEquals(typeof fileHandlers.write_file, "function");
  });

  await t.step("should have read_file handler", () => {
    assertExists(fileHandlers.read_file);
    assertEquals(typeof fileHandlers.read_file, "function");
  });

  await t.step("should have create_directory handler", () => {
    assertExists(fileHandlers.create_directory);
    assertEquals(typeof fileHandlers.create_directory, "function");
  });

  await t.step("should have list_files handler", () => {
    assertExists(fileHandlers.list_files);
    assertEquals(typeof fileHandlers.list_files, "function");
  });

  await t.step("should have delete_file handler", () => {
    assertExists(fileHandlers.delete_file);
    assertEquals(typeof fileHandlers.delete_file, "function");
  });
});

Deno.test("File Tools - Handler Functionality", async (t) => {
  const setup = async () => {
    try {
      await Deno.remove(TEST_DIR, { recursive: true });
    } catch {
      // Ignore if doesn't exist
    }
    await Deno.mkdir(TEST_DIR, { recursive: true });
  };

  const teardown = async () => {
    try {
      await Deno.remove(TEST_DIR, { recursive: true });
    } catch {
      // Ignore
    }
  };

  await t.step("write_file should create file and directories", async () => {
    await setup();

    const testFile = `${TEST_DIR}/subdir/test.txt`;
    const testContent = "Hello, Toolkit!";

    const result = await fileHandlers.write_file({
      file_path: testFile,
      content: testContent,
      create_dirs: true,
      encoding: "utf8"
    });

    assertEquals(result.success, true);
    assertEquals(result.file_path, testFile);
    assert(result.bytes_written > 0);
    assertExists(result.created_dirs);

    // Verify file was created
    const fileContent = await Deno.readTextFile(testFile);
    assertEquals(fileContent, testContent);

    await teardown();
  });

  await t.step("read_file should read file content", async () => {
    await setup();

    const testFile = `${TEST_DIR}/read-test.txt`;
    const testContent = "Read this content!";
    
    // Create test file first
    await Deno.writeTextFile(testFile, testContent);

    const result = await fileHandlers.read_file({
      file_path: testFile,
      encoding: "utf8"
    });

    assertEquals(result.success, true);
    assertEquals(result.file_path, testFile);
    assertEquals(result.content, testContent);
    assert(result.size > 0);
    assertExists(result.modified);

    await teardown();
  });

  await t.step("create_directory should create directory", async () => {
    await setup();

    const testDir = `${TEST_DIR}/new-directory`;

    const result = await fileHandlers.create_directory({
      dir_path: testDir,
      recursive: true
    });

    assertEquals(result.success, true);
    assertEquals(result.dir_path, testDir);
    assertEquals(result.created, true);
    assertEquals(result.already_exists, false);

    // Verify directory exists
    const stat = await Deno.stat(testDir);
    assert(stat.isDirectory);

    await teardown();
  });

  await t.step("list_files should list directory contents", async () => {
    await setup();

    // Create test files
    await Deno.writeTextFile(`${TEST_DIR}/file1.txt`, "content1");
    await Deno.writeTextFile(`${TEST_DIR}/file2.txt`, "content2");
    await Deno.mkdir(`${TEST_DIR}/subdir`);

    const result = await fileHandlers.list_files({
      dir_path: TEST_DIR,
      include_dirs: true,
      recursive: false
    });

    assertEquals(result.success, true);
    assertEquals(result.dir_path, TEST_DIR);
    assertEquals(result.total, 3); // 2 files + 1 directory
    assert(result.files.some(f => f.name === "file1.txt" && f.type === "file"));
    assert(result.files.some(f => f.name === "file2.txt" && f.type === "file"));
    assert(result.files.some(f => f.name === "subdir" && f.type === "directory"));

    await teardown();
  });

  await t.step("delete_file should delete file", async () => {
    await setup();

    const testFile = `${TEST_DIR}/delete-me.txt`;
    await Deno.writeTextFile(testFile, "delete this");

    const result = await fileHandlers.delete_file({
      file_path: testFile,
      recursive: false
    });

    assertEquals(result.success, true);
    assertEquals(result.file_path, testFile);
    assertEquals(result.deleted, true);

    // Verify file was deleted
    try {
      await Deno.stat(testFile);
      assert(false, "File should have been deleted");
    } catch (error) {
      assert(error instanceof Deno.errors.NotFound);
    }

    await teardown();
  });

  await t.step("should handle errors gracefully", async () => {
    // Test reading non-existent file
    try {
      await fileHandlers.read_file({
        file_path: "/non/existent/file.txt",
        encoding: "utf8"
      });
      assert(false, "Should have thrown error");
    } catch (error) {
      assertExists(error);
      assert((error as Error).message.includes("Failed to read file"));
    }

    // Test writing to invalid path (without create_dirs)
    try {
      await fileHandlers.write_file({
        file_path: "/non/existent/dir/file.txt",
        content: "test",
        create_dirs: false,
        encoding: "utf8"
      });
      assert(false, "Should have thrown error");
    } catch (error) {
      assertExists(error);
      assert((error as Error).message.includes("Failed to write file"));
    }
  });
});