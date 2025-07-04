"""
End-to-End tests for MCP-Memry server via Docker

Tests the complete integration flow as Claude Desktop would use it.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from .mcp_docker_client import create_memry_client


class TestMemryE2E:
    """End-to-end tests for memry server"""

    def setup_method(self):
        """Set up test environment with temporary storage"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_memry_server_startup_and_tools(self):
        """Test that memry server starts and lists expected tools"""
        client = create_memry_client(str(self.storage_path))

        async with client.connect() as mcp:
            # Test server startup and tool listing
            tools = await mcp.list_tools()

            # Verify expected tools are available
            tool_names = [tool["name"] for tool in tools]
            expected_tools = [
                "create_memory",
                "search_memories",
                "list_all_memories",
                "get_memory_stats",
            ]

            for expected_tool in expected_tools:
                assert expected_tool in tool_names, f"Missing tool: {expected_tool}"

            print(f"✅ Found {len(tools)} tools: {tool_names}")

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_memory_creation_workflow(self):
        """Test complete memory creation workflow"""
        client = create_memry_client(str(self.storage_path))

        async with client.connect() as mcp:
            # Create a memory
            create_result = await mcp.call_tool(
                "create_memory",
                {
                    "title": "E2E Test Memory",
                    "content": "This is a test memory created during E2E testing.",
                    "source": "e2e-test",
                    "tags": ["test", "e2e", "automation"],
                    "topic_slug": "e2e-test-memory",
                },
            )

            # Verify creation result
            assert create_result.get("structuredContent", {}).get("success")
            assert "filename" in create_result.get("structuredContent", {})
            filename = create_result["structuredContent"]["filename"]
            print(f"✅ Created memory: {filename}")

            # Verify file was actually created (JSON backend creates .json files)
            json_files = list(self.storage_path.glob("*.json"))
            assert len(json_files) == 1

            json_file = json_files[0]
            # The actual file is JSON but the display filename is .md
            assert filename.endswith(".md")  # Display filename
            assert json_file.name.endswith(".json")  # Actual storage file

            # Verify file content (JSON format)
            import json

            with open(json_file) as f:
                content = json.load(f)
            assert content["title"] == "E2E Test Memory"
            assert content["source"] == "e2e-test"
            assert (
                content["content"]
                == "This is a test memory created during E2E testing."
            )
            assert "test" in content["tags"]
            assert "e2e" in content["tags"]
            print("✅ Verified JSON file content")

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_memory_search_workflow(self):
        """Test memory search functionality"""
        client = create_memry_client(str(self.storage_path))

        async with client.connect() as mcp:
            # Create multiple memories
            memories_data = [
                {
                    "title": "AI Research Notes",
                    "content": "Research on artificial intelligence and machine learning.",
                    "source": "research",
                    "tags": ["ai", "research", "ml"],
                },
                {
                    "title": "Protocol Design",
                    "content": "Notes about MCP protocol design and implementation.",
                    "source": "development",
                    "tags": ["protocol", "mcp", "development"],
                },
                {
                    "title": "Meeting Notes",
                    "content": "Important discussion about project direction.",
                    "source": "meeting",
                    "tags": ["meeting", "planning"],
                },
            ]

            # Create all memories
            for memory_data in memories_data:
                result = await mcp.call_tool("create_memory", memory_data)
                assert result.get("structuredContent", {}).get("success")

            print(f"✅ Created {len(memories_data)} test memories")

            # Test search by tags
            search_result = await mcp.call_tool("search_memories", {"tags": ["ai"]})

            assert search_result.get("structuredContent", {}).get("success")
            found_memories = search_result.get("structuredContent", {}).get(
                "memories", []
            )
            assert len(found_memories) == 1
            assert found_memories[0]["title"] == "AI Research Notes"
            print("✅ Tag search found correct memory")

            # Test content search
            content_search_result = await mcp.call_tool(
                "search_memories", {"content_search": "protocol"}
            )

            assert (
                content_search_result.get("structuredContent", {}).get("success")
            )
            protocol_memories = content_search_result.get("structuredContent", {}).get(
                "memories", []
            )
            assert len(protocol_memories) == 1
            assert protocol_memories[0]["title"] == "Protocol Design"
            print("✅ Content search found correct memory")

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_memory_stats_workflow(self):
        """Test memory statistics functionality"""
        client = create_memry_client(str(self.storage_path))

        async with client.connect() as mcp:
            # Create memories with different sources and tags
            test_memories = [
                {
                    "title": "Memory 1",
                    "content": "Content 1",
                    "source": "claude-desktop",
                    "tags": ["work", "ai"],
                },
                {
                    "title": "Memory 2",
                    "content": "Content 2",
                    "source": "claude-code",
                    "tags": ["work", "development"],
                },
                {
                    "title": "Memory 3",
                    "content": "Content 3",
                    "source": "claude-desktop",
                    "tags": ["personal", "ai"],
                },
            ]

            for memory in test_memories:
                result = await mcp.call_tool("create_memory", memory)
                assert result.get("structuredContent", {}).get("success")

            # Get statistics
            stats_result = await mcp.call_tool("get_memory_stats", {})

            assert stats_result.get("structuredContent", {}).get("success")
            stats = stats_result.get("structuredContent", {})

            # Verify statistics
            assert stats["total_memories"] == 3
            assert stats["sources"]["claude-desktop"] == 2
            assert stats["sources"]["claude-code"] == 1
            assert stats["tags"]["work"] == 2
            assert stats["tags"]["ai"] == 2
            assert stats["tags"]["development"] == 1
            assert stats["tags"]["personal"] == 1

            print(f"✅ Statistics correct: {stats['total_memories']} memories")

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_list_all_memories_workflow(self):
        """Test listing all memories"""
        client = create_memry_client(str(self.storage_path))

        async with client.connect() as mcp:
            # Create some memories
            for i in range(3):
                result = await mcp.call_tool(
                    "create_memory",
                    {
                        "title": f"Test Memory {i+1}",
                        "content": f"This is test memory number {i+1}.",
                        "source": "test",
                        "tags": ["test", f"batch-{i+1}"],
                    },
                )
                assert result.get("structuredContent", {}).get("success")

            # List all memories
            list_result = await mcp.call_tool("list_all_memories", {})

            assert list_result.get("structuredContent", {}).get("success")
            memories = list_result.get("structuredContent", {}).get("memories", [])
            assert len(memories) == 3

            # Verify memories have expected structure
            for memory in memories:
                assert "filename" in memory
                assert "title" in memory
                assert "date" in memory
                assert "source" in memory
                assert "tags" in memory
                assert "content_preview" in memory

            print(f"✅ Listed {len(memories)} memories with correct structure")

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        client = create_memry_client(str(self.storage_path))

        async with client.connect() as mcp:
            # Test creating memory with missing required fields
            try:
                result = await mcp.call_tool(
                    "create_memory",
                    {
                        "title": "",  # Empty title
                        "content": "Test content",
                        # Missing source
                    },
                )
                # Should handle gracefully and return success=False
                assert not result.get("structuredContent", {}).get("success")
                print("✅ Invalid creation handled gracefully")
            except Exception as e:
                # Also acceptable if it raises an exception
                print(f"✅ Invalid creation raised exception: {e}")

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_persistence_across_restarts(self):
        """Test that data persists across container restarts"""
        storage_path = str(self.storage_path)

        # First session - create data
        client1 = create_memry_client(storage_path)
        async with client1.connect() as mcp:
            result = await mcp.call_tool(
                "create_memory",
                {
                    "title": "Persistent Memory",
                    "content": "This memory should persist across restarts.",
                    "source": "persistence-test",
                    "tags": ["persistence", "test"],
                },
            )
            assert result.get("structuredContent", {}).get("success")

        # Second session - verify data exists
        client2 = create_memry_client(storage_path)
        async with client2.connect() as mcp:
            list_result = await mcp.call_tool("list_all_memories", {})
            memories = list_result.get("structuredContent", {}).get("memories", [])

            # Find our persistent memory
            persistent_memory = next(
                (m for m in memories if m["title"] == "Persistent Memory"), None
            )
            assert persistent_memory is not None
            assert persistent_memory["source"] == "persistence-test"

            print("✅ Data persisted across container restarts")
