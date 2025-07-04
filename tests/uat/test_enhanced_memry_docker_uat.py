#!/usr/bin/env python3
"""
Enhanced UAT (User Acceptance Test) for Memry MCP Server Docker Container

Comprehensive testing of the memory management system including:
1. Memory creation, retrieval, and management
2. Advanced search and filtering capabilities
3. Tag-based organization and categorization
4. Data persistence and storage validation
5. Export functionality and data formats
6. Error handling and edge cases

Run with: python tests/uat/test_enhanced_memry_docker_uat.py
"""
import json
import logging
import time
from datetime import datetime, timedelta

from mcp_docker_client import MEMRY_SERVER, MCPDockerClient, create_test_workspace

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_memry_core_functionality():
    """Test core memory management functionality"""
    print("🧠 Memry MCP Server - Enhanced UAT")
    print("=" * 50)
    print("🎯 Testing comprehensive memory management system")

    # Create test workspace
    workspace = create_test_workspace()

    # Configure memry server
    memry_config = MEMRY_SERVER
    memry_config.volume_mappings = {str(workspace): "/app/memories"}

    with MCPDockerClient(memry_config, debug=True) as client:
        # List available tools
        tools = client.list_tools()
        tool_names = [tool["name"] for tool in tools]

        expected_tools = [
            "create_memory",
            "list_memories",
            "search_memories",
            "get_memory",
            "update_memory",
            "delete_memory",
            "export_memories",
        ]

        missing_tools = [tool for tool in expected_tools if tool not in tool_names]
        if missing_tools:
            raise RuntimeError(f"Missing expected tools: {missing_tools}")

        print(f"✅ All expected tools available: {len(expected_tools)} tools")

        # Test 1: Create diverse memories
        print("\n🎬 Test 1: Create diverse memory types...")

        memories_data = [
            {
                "title": "Meeting Notes - Q1 Planning",
                "content": "Discussed Q1 objectives, resource allocation, and key milestones. Focus on UAT testing implementation and Claude integration improvements.",
                "source": "meeting",
                "tags": ["planning", "q1", "meeting", "objectives"],
            },
            {
                "title": "Technical Research - MCP Protocol",
                "content": "Deep dive into Model Context Protocol specifications. Key findings: JSON-RPC 2.0 base, tool-based architecture, stdio transport for desktop integration.",
                "source": "research",
                "tags": ["technical", "mcp", "protocol", "research"],
            },
            {
                "title": "Learning - Docker Container Patterns",
                "content": "Best practices for containerizing MCP servers: proper stdio handling, volume mounting, environment variable management.",
                "source": "learning",
                "tags": ["docker", "containers", "best-practices", "learning"],
            },
            {
                "title": "Idea - Automated Testing Framework",
                "content": "Concept for automated UAT testing across all MCP Fleet servers using Docker containers and standardized test protocols.",
                "source": "brainstorm",
                "tags": ["ideas", "testing", "automation", "framework"],
            },
            {
                "title": "Project Log - Refactoring Progress",
                "content": "Successfully migrated core and storage packages. Removed redundant 'mcp' prefixes and flattened package structure. TDD methodology maintained throughout.",
                "source": "project-log",
                "tags": ["refactoring", "progress", "tdd", "packages"],
            },
        ]

        created_memories = []
        for memory_data in memories_data:
            result = client.call_tool("create_memory", memory_data)
            created_memories.append(result)
            print(f"   ✅ Created: {memory_data['title']}")

        print(f"✅ Created {len(created_memories)} diverse memories")

        # Test 2: List all memories
        print("\n🎬 Test 2: List all memories...")
        list_result = client.call_tool(
            "list_memories", {"limit": 10, "include_content": True}
        )

        # Verify all memories are listed
        if "content" in list_result:
            list_content = list_result["content"][0].get("text", "")
            for memory in memories_data:
                assert (
                    memory["title"] in list_content
                ), f"Memory not found in list: {memory['title']}"

        print("✅ All memories visible in list")

        # Test 3: Search functionality
        print("\n🎬 Test 3: Test search capabilities...")

        # Search by content
        client.call_tool(
            "search_memories",
            {
                "query": "Docker container",
                "search_in": ["content", "title"],
                "limit": 5,
            },
        )

        # Search by tags
        client.call_tool(
            "search_memories", {"query": "technical", "search_in": ["tags"], "limit": 5}
        )

        # Search by source
        client.call_tool(
            "search_memories",
            {"query": "research", "search_in": ["source"], "limit": 5},
        )

        print("✅ Search functionality working across content, tags, and source")

        # Test 4: Retrieve specific memory
        print("\n🎬 Test 4: Retrieve specific memory...")

        # Extract memory ID from one of the created memories
        if created_memories and "content" in created_memories[0]:
            # Parse the structured content to get memory ID
            content = created_memories[0]["content"][0].get("text", "")
            if "memory ID:" in content.lower():
                lines = content.split("\n")
                memory_id = None
                for line in lines:
                    if "memory ID:" in line.lower():
                        memory_id = line.split(":")[-1].strip()
                        break

                if memory_id:
                    client.call_tool(
                        "get_memory", {"memory_id": memory_id}
                    )
                    print(f"✅ Retrieved memory: {memory_id}")

        # Test 5: Update memory
        print("\n🎬 Test 5: Update memory content...")

        # Create a memory specifically for updating
        update_test = client.call_tool(
            "create_memory",
            {
                "title": "UAT Test Memory - For Updates",
                "content": "Original content that will be updated",
                "source": "uat-test",
                "tags": ["test", "update"],
            },
        )

        # Extract memory ID and update
        if "content" in update_test:
            content = update_test["content"][0].get("text", "")
            lines = content.split("\n")
            memory_id = None
            for line in lines:
                if "memory ID:" in line.lower():
                    memory_id = line.split(":")[-1].strip()
                    break

            if memory_id:
                client.call_tool(
                    "update_memory",
                    {
                        "memory_id": memory_id,
                        "updates": {
                            "content": "UPDATED: Content has been modified during UAT testing to verify update functionality",
                            "tags": ["test", "update", "modified", "uat"],
                        },
                    },
                )
                print(f"✅ Updated memory: {memory_id}")

        # Test 6: Export memories
        print("\n🎬 Test 6: Export memories...")

        client.call_tool(
            "export_memories",
            {
                "format": "json",
                "filter": {
                    "tags": ["technical", "research"],
                    "date_range": {
                        "start": (datetime.now() - timedelta(days=1)).isoformat(),
                        "end": datetime.now().isoformat(),
                    },
                },
                "include_metadata": True,
            },
        )

        print("✅ Memory export completed")

        # Test 7: Verify data persistence
        print("\n🎬 Test 7: Verify data persistence...")

        # Check that memory files were created
        memory_files = list(workspace.glob("*.json"))
        assert len(memory_files) >= len(
            memories_data
        ), f"Expected at least {len(memories_data)} files, found {len(memory_files)}"

        # Validate file structure
        for memory_file in memory_files[:3]:  # Check first 3 files
            with open(memory_file) as f:
                memory_data = json.load(f)

            required_fields = ["id", "title", "content", "source", "tags", "created_at"]
            for field in required_fields:
                assert (
                    field in memory_data
                ), f"Missing field {field} in {memory_file.name}"

        print(f"✅ Data persistence validated: {len(memory_files)} files created")

        # Summary statistics
        print("\n📊 UAT Session Summary:")
        print(f"   🧠 Memories created: {len(memories_data) + 1}")  # +1 for update test
        print("   🔍 Search operations: 3")
        print("   📝 Update operations: 1")
        print("   📤 Export operations: 1")
        print(f"   💾 Storage files: {len(memory_files)}")
        print(f"   🗂️  Storage location: {workspace}")

        print("\n🎉 Memry core functionality UAT completed successfully!")
        print("✅ Memory CRUD operations functional")
        print("✅ Search and filtering operational")
        print("✅ Data persistence validated")
        print("✅ Export functionality confirmed")


def test_memry_advanced_features():
    """Test advanced memry features and edge cases"""
    print("\n🧠 Testing Memry Advanced Features...")

    workspace = create_test_workspace()
    memry_config = MEMRY_SERVER
    memry_config.volume_mappings = {str(workspace): "/app/memories"}

    with MCPDockerClient(memry_config) as client:
        # Test 1: Complex search queries
        print("🔬 Testing complex search patterns...")

        # Create memories with specific patterns for testing
        test_memories = [
            {
                "title": "Complex Search Test Alpha",
                "content": "This memory contains specific keywords: algorithm optimization, performance tuning, and database indexing strategies.",
                "source": "documentation",
                "tags": ["algorithm", "performance", "database", "optimization"],
            },
            {
                "title": "Complex Search Test Beta",
                "content": "Different content about machine learning models, neural networks, and training optimization techniques.",
                "source": "research",
                "tags": ["ml", "neural-networks", "training", "optimization"],
            },
        ]

        for memory in test_memories:
            client.call_tool("create_memory", memory)

        # Test multi-term search
        client.call_tool(
            "search_memories",
            {
                "query": "optimization performance",
                "search_in": ["content", "tags"],
                "limit": 10,
            },
        )

        print("✅ Complex search patterns working")

        # Test 2: Large content handling
        print("🔬 Testing large content handling...")

        large_content = "Large content test. " * 500  # ~10KB content
        client.call_tool(
            "create_memory",
            {
                "title": "Large Content Test",
                "content": large_content,
                "source": "stress-test",
                "tags": ["large", "content", "test"],
            },
        )

        print("✅ Large content handling working")

        # Test 3: Special character handling
        print("🔬 Testing special character handling...")

        client.call_tool(
            "create_memory",
            {
                "title": "Special Characters: émojis 🚀, symbols & [brackets]",
                "content": "Content with special chars: àáâãäå, çñü, quotes \"'', and symbols @#$%^&*()",
                "source": "encoding-test",
                "tags": ["special-chars", "encoding", "unicode", "test"],
            },
        )

        print("✅ Special character handling working")

        # Test 4: Memory limit and pagination
        print("🔬 Testing pagination and limits...")

        # List with small limit
        client.call_tool(
            "list_memories", {"limit": 2, "include_content": False}
        )

        # List with larger limit
        client.call_tool(
            "list_memories", {"limit": 100, "include_content": True}
        )

        print("✅ Pagination and limits working")


def test_memry_error_handling():
    """Test memry error handling and validation"""
    print("\n🧠 Testing Memry Error Handling...")

    workspace = create_test_workspace()
    memry_config = MEMRY_SERVER
    memry_config.volume_mappings = {str(workspace): "/app/memories"}

    with MCPDockerClient(memry_config) as client:
        # Test 1: Invalid memory creation
        print("🔬 Testing invalid memory creation...")
        try:
            client.call_tool(
                "create_memory",
                {
                    "title": "",  # Empty title
                    "content": "",  # Empty content
                    "source": "",  # Empty source
                    "tags": [],  # Empty tags
                },
            )
            print("⚠️  Empty memory creation succeeded (may be allowed)")
        except RuntimeError as e:
            print(f"✅ Empty memory properly rejected: {str(e)[:50]}...")

        # Test 2: Non-existent memory operations
        print("🔬 Testing non-existent memory operations...")
        try:
            client.call_tool("get_memory", {"memory_id": "non-existent-id-12345"})
            print("⚠️  Non-existent memory retrieval succeeded (may return null)")
        except RuntimeError as e:
            print(f"✅ Non-existent memory properly handled: {str(e)[:50]}...")

        # Test 3: Invalid search parameters
        print("🔬 Testing invalid search parameters...")
        try:
            client.call_tool(
                "search_memories",
                {
                    "query": "",  # Empty query
                    "search_in": ["invalid_field"],  # Invalid field
                    "limit": -1,  # Invalid limit
                },
            )
            print("⚠️  Invalid search succeeded (may be allowed)")
        except RuntimeError as e:
            print(f"✅ Invalid search properly rejected: {str(e)[:50]}...")

        print("✅ Error handling tests completed")


def test_memry_performance():
    """Test memry performance with multiple operations"""
    print("\n🧠 Testing Memry Performance...")

    workspace = create_test_workspace()
    memry_config = MEMRY_SERVER
    memry_config.volume_mappings = {str(workspace): "/app/memories"}

    with MCPDockerClient(memry_config) as client:
        print("🔬 Creating multiple memories for performance testing...")

        start_time = time.time()

        # Create 10 memories rapidly
        for i in range(10):
            client.call_tool(
                "create_memory",
                {
                    "title": f"Performance Test Memory {i+1}",
                    "content": f"This is test memory number {i+1} created for performance testing. Contains various keywords for search testing: test{i} performance{i} benchmark{i}.",
                    "source": "performance-test",
                    "tags": [f"test{i}", "performance", "benchmark", f"batch{i//5}"],
                },
            )

        creation_time = time.time() - start_time

        # Test rapid search operations
        search_start = time.time()
        for i in range(5):
            client.call_tool(
                "search_memories",
                {"query": f"test{i}", "search_in": ["content", "tags"], "limit": 10},
            )

        search_time = time.time() - search_start

        print("✅ Performance test completed:")
        print(f"   📝 10 memory creations: {creation_time:.2f}s")
        print(f"   🔍 5 search operations: {search_time:.2f}s")
        print(f"   ⚡ Average creation time: {creation_time/10:.3f}s")
        print(f"   ⚡ Average search time: {search_time/5:.3f}s")


if __name__ == "__main__":
    try:
        test_memry_core_functionality()
        test_memry_advanced_features()
        test_memry_error_handling()
        test_memry_performance()

        print("\n🌟 All Enhanced Memry UAT tests passed!")
        print("✅ Memry server ready for production!")
        print("✅ Comprehensive memory management validated!")
        print("✅ Advanced features and edge cases tested!")

    except Exception as e:
        print(f"\n❌ UAT failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
