"""
Tests for memory tools functionality
"""
import tempfile
import shutil
import pytest

from memry.src.tools.memory_tools import (
    create_memory_handler,
    search_memories_handler,
    list_all_memories_handler,
    get_memory_stats_handler,
    CreateMemoryInputSchema,
    SearchMemoriesInputSchema,
    memory_storage
)


class TestMemoryTools:
    """Test memory tools functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        # Override the global storage for testing
        memory_storage.base_path = self.temp_dir
        memory_storage.base_path.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_create_memory_handler(self):
        """Test create memory handler"""
        input_data = CreateMemoryInputSchema(
            title="Test Memory",
            content="This is a test memory content.",
            source="claude-code",
            tags=["test", "memory"],
            topic_slug="test-memory"
        )
        
        result = await create_memory_handler(input_data)
        
        assert result.success == True
        assert result.title == "Test Memory"
        assert result.tags == ["test", "memory"]
        assert result.filename.endswith("test-memory.md")
        assert result.file_path != ""
    
    @pytest.mark.asyncio
    async def test_search_memories_handler(self):
        """Test search memories handler"""
        # Create test memories first
        memory1 = CreateMemoryInputSchema(
            title="Memory 1",
            content="Content about AI",
            source="claude-code",
            tags=["ai", "test"]
        )
        
        memory2 = CreateMemoryInputSchema(
            title="Memory 2",
            content="Content about protocols",
            source="claude-desktop",
            tags=["protocol", "test"]
        )
        
        await create_memory_handler(memory1)
        await create_memory_handler(memory2)
        
        # Search by tags
        search_input = SearchMemoriesInputSchema(tags=["ai"])
        result = await search_memories_handler(search_input)
        
        assert result.success == True
        assert result.total_found == 1
        assert result.memories[0].title == "Memory 1"
        
        # Search by content
        search_input = SearchMemoriesInputSchema(content_search="protocols")
        result = await search_memories_handler(search_input)
        
        assert result.success == True
        assert result.total_found == 1
        assert result.memories[0].title == "Memory 2"
    
    @pytest.mark.asyncio
    async def test_list_all_memories_handler(self):
        """Test list all memories handler"""
        # Create test memories
        memory1 = CreateMemoryInputSchema(
            title="Memory 1",
            content="Content 1",
            source="claude-code",
            tags=["test"]
        )
        
        memory2 = CreateMemoryInputSchema(
            title="Memory 2",
            content="Content 2",
            source="claude-desktop",
            tags=["test"]
        )
        
        await create_memory_handler(memory1)
        await create_memory_handler(memory2)
        
        # List all memories
        result = await list_all_memories_handler()
        
        assert result.success == True
        assert result.total_found == 2
        
        titles = [m.title for m in result.memories]
        assert "Memory 1" in titles
        assert "Memory 2" in titles
    
    @pytest.mark.asyncio
    async def test_get_memory_stats_handler(self):
        """Test get memory stats handler"""
        # Create test memories
        memory1 = CreateMemoryInputSchema(
            title="Memory 1",
            content="Content 1",
            source="claude-code",
            tags=["ai", "test"]
        )
        
        memory2 = CreateMemoryInputSchema(
            title="Memory 2",
            content="Content 2",
            source="claude-desktop",
            tags=["protocol", "test"]
        )
        
        await create_memory_handler(memory1)
        await create_memory_handler(memory2)
        
        # Get stats
        result = await get_memory_stats_handler()
        
        assert result.success == True
        assert result.total_memories == 2
        assert result.sources["claude-code"] == 1
        assert result.sources["claude-desktop"] == 1
        assert result.tags["test"] == 2
        assert result.tags["ai"] == 1
        assert result.tags["protocol"] == 1
    
    @pytest.mark.asyncio
    async def test_content_preview_in_search(self):
        """Test that search results include content preview"""
        # Create memory with long content
        long_content = "This is a very long piece of content that should be truncated in the preview. " * 10
        
        memory = CreateMemoryInputSchema(
            title="Long Memory",
            content=long_content,
            source="claude-code",
            tags=["test"]
        )
        
        await create_memory_handler(memory)
        
        # Search and check preview
        result = await list_all_memories_handler()
        
        assert result.success == True
        assert result.total_found == 1
        
        memory_summary = result.memories[0]
        assert len(memory_summary.content_preview) <= 203  # 200 chars + "..."
        assert memory_summary.content_preview.endswith("...")
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self):
        """Test search with no results"""
        search_input = SearchMemoriesInputSchema(tags=["nonexistent"])
        result = await search_memories_handler(search_input)
        
        assert result.success == True
        assert result.total_found == 0
        assert result.memories == []
    
    @pytest.mark.asyncio
    async def test_search_with_date_range(self):
        """Test searching with date range"""
        # Create memory
        memory = CreateMemoryInputSchema(
            title="Memory 1",
            content="Content 1",
            source="claude-code",
            tags=["test"]
        )
        
        await create_memory_handler(memory)
        
        # Search with date range (today should include the memory)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        search_input = SearchMemoriesInputSchema(
            date_from=today,
            date_to=today
        )
        result = await search_memories_handler(search_input)
        
        assert result.success == True
        assert result.total_found == 1