"""
Test to identify and fix the Docker timeout issue
Following strict TDD methodology
"""

import asyncio
import tempfile
from pathlib import Path

import pytest

from .mcp_docker_client import create_memry_client


class TestDockerTimeoutIssue:
    """Test to identify why Docker commands are timing out"""

    def setup_method(self):
        """Set up test environment with temporary storage"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)  # 30 second timeout to catch hangs
    async def test_docker_tool_call_completes_quickly(self):
        """Test that Docker tool calls complete within reasonable time"""
        client = create_memry_client(str(self.storage_path))

        # This should complete in under 30 seconds, not timeout
        async with client.connect() as mcp:
            start_time = asyncio.get_event_loop().time()

            # Simple tool call that should complete quickly
            result = await mcp.call_tool(
                "create_memory",
                {
                    "title": "Timeout Test",
                    "content": "This should complete quickly",
                    "source": "timeout-test",
                    "tags": ["test"],
                },
            )

            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time

            # Assert the call completed successfully
            assert result.get("structuredContent", {}).get("success")

            # Assert it completed in reasonable time (under 10 seconds)
            assert duration < 10.0, f"Tool call took {duration:.2f} seconds - too slow!"

            print(f"✅ Tool call completed in {duration:.2f} seconds")

    @pytest.mark.asyncio
    @pytest.mark.timeout(20)  # 20 second timeout
    async def test_docker_initialization_speed(self):
        """Test that Docker container initialization is fast"""
        client = create_memry_client(str(self.storage_path))

        start_time = asyncio.get_event_loop().time()

        # Just test initialization and tool listing
        async with client.connect() as mcp:
            tools = await mcp.list_tools()

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        # Assert initialization completed quickly
        assert len(tools) == 4  # Should have 4 tools
        assert (
            duration < 15.0
        ), f"Initialization took {duration:.2f} seconds - too slow!"

        print(f"✅ Docker initialization completed in {duration:.2f} seconds")

    @pytest.mark.asyncio
    @pytest.mark.timeout(45)  # Longer timeout for debugging
    async def test_identify_hanging_point(self):
        """Test to identify exactly where the hang occurs"""
        client = create_memry_client(str(self.storage_path))

        print("🔍 Starting Docker container...")
        start_time = asyncio.get_event_loop().time()

        async with client.connect() as mcp:
            checkpoint1 = asyncio.get_event_loop().time()
            print(f"✅ Container started in {checkpoint1 - start_time:.2f}s")

            print("🔍 Listing tools...")
            await mcp.list_tools()
            checkpoint2 = asyncio.get_event_loop().time()
            print(f"✅ Tools listed in {checkpoint2 - checkpoint1:.2f}s")

            print("🔍 Calling create_memory tool...")
            result = await mcp.call_tool(
                "create_memory",
                {
                    "title": "Debug Test",
                    "content": "Finding the hang point",
                    "source": "debug",
                    "tags": ["debug"],
                },
            )
            checkpoint3 = asyncio.get_event_loop().time()
            print(f"✅ Tool call completed in {checkpoint3 - checkpoint2:.2f}s")

            # Verify the result
            assert result.get("structuredContent", {}).get("success")

            total_time = checkpoint3 - start_time
            print(f"✅ Total test completed in {total_time:.2f}s")

            # If we get here, there's no hang!
            assert total_time < 40.0, f"Total time {total_time:.2f}s is acceptable"
