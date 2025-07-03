"""
Tests for memory storage functionality
"""
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

import pytest

from memry.src.storage.memory_storage import MemoryStorage, CreateMemoryInput, SearchFilter


class TestMemoryStorage:
    """Test memory storage functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = MemoryStorage(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_memory(self):
        """Test creating a memory"""
        input_data = CreateMemoryInput(
            title="Test Memory",
            content="This is a test memory content.",
            source="claude-code",
            tags=["test", "memory"],
            topic_slug="test-memory"
        )
        
        memory = self.storage.create_memory(input_data)
        
        assert memory.metadata.title == "Test Memory"
        assert memory.metadata.source == "claude-code"
        assert memory.metadata.tags == ["test", "memory"]
        assert memory.content == "This is a test memory content."
        assert memory.filename.endswith("test-memory.md")
        assert Path(memory.file_path).exists()
    
    def test_create_memory_without_topic_slug(self):
        """Test creating a memory without topic slug"""
        input_data = CreateMemoryInput(
            title="Test Memory Without Slug",
            content="This is a test memory content.",
            source="claude-desktop",
            tags=["test"]
        )
        
        memory = self.storage.create_memory(input_data)
        
        assert memory.metadata.title == "Test Memory Without Slug"
        assert "test-memory-without-slug" in memory.filename
        assert Path(memory.file_path).exists()
    
    def test_search_memories_by_tags(self):
        """Test searching memories by tags"""
        # Create test memories
        memory1 = self.storage.create_memory(CreateMemoryInput(
            title="Memory 1",
            content="Content 1",
            source="claude-code",
            tags=["ai", "test"]
        ))
        
        memory2 = self.storage.create_memory(CreateMemoryInput(
            title="Memory 2",
            content="Content 2",
            source="claude-desktop",
            tags=["protocol", "test"]
        ))
        
        # Search by tags
        results = self.storage.search_memories(SearchFilter(tags=["ai"]))
        assert len(results) == 1
        assert results[0].metadata.title == "Memory 1"
        
        results = self.storage.search_memories(SearchFilter(tags=["test"]))
        assert len(results) == 2
    
    def test_search_memories_by_content(self):
        """Test searching memories by content"""
        # Create test memories
        memory1 = self.storage.create_memory(CreateMemoryInput(
            title="Memory 1",
            content="This is about artificial intelligence",
            source="claude-code",
            tags=["ai"]
        ))
        
        memory2 = self.storage.create_memory(CreateMemoryInput(
            title="Memory 2",
            content="This is about something else",
            source="claude-desktop",
            tags=["other"]
        ))
        
        # Search by content
        results = self.storage.search_memories(SearchFilter(content_search="artificial intelligence"))
        assert len(results) == 1
        assert results[0].metadata.title == "Memory 1"
        
        results = self.storage.search_memories(SearchFilter(content_search="something"))
        assert len(results) == 1
        assert results[0].metadata.title == "Memory 2"
    
    def test_list_all_memories(self):
        """Test listing all memories"""
        # Create test memories
        memory1 = self.storage.create_memory(CreateMemoryInput(
            title="Memory 1",
            content="Content 1",
            source="claude-code",
            tags=["test"]
        ))
        
        memory2 = self.storage.create_memory(CreateMemoryInput(
            title="Memory 2",
            content="Content 2",
            source="claude-desktop",
            tags=["test"]
        ))
        
        # List all memories
        results = self.storage.list_all_memories()
        assert len(results) == 2
        
        # Should be sorted by date (newest first)
        titles = [m.metadata.title for m in results]
        assert "Memory 1" in titles
        assert "Memory 2" in titles
    
    def test_get_memory_stats(self):
        """Test getting memory statistics"""
        # Create test memories
        memory1 = self.storage.create_memory(CreateMemoryInput(
            title="Memory 1",
            content="Content 1",
            source="claude-code",
            tags=["ai", "test"]
        ))
        
        memory2 = self.storage.create_memory(CreateMemoryInput(
            title="Memory 2",
            content="Content 2",
            source="claude-desktop",
            tags=["protocol", "test"]
        ))
        
        # Get stats
        stats = self.storage.get_memory_stats()
        
        assert stats["total_memories"] == 2
        assert stats["sources"]["claude-code"] == 1
        assert stats["sources"]["claude-desktop"] == 1
        assert stats["tags"]["test"] == 2
        assert stats["tags"]["ai"] == 1
        assert stats["tags"]["protocol"] == 1
        assert str(self.temp_dir) in stats["storage_path"]
    
    def test_slugify(self):
        """Test the slugify function"""
        # Test basic slugification
        assert self.storage._slugify("Hello World") == "hello-world"
        assert self.storage._slugify("Test with CAPS") == "test-with-caps"
        assert self.storage._slugify("Special!@#$%Characters") == "specialcharacters"
        assert self.storage._slugify("Multiple   Spaces") == "multiple-spaces"
        assert self.storage._slugify("Hyphens-Already-Here") == "hyphens-already-here"
    
    def test_filename_generation(self):
        """Test filename generation"""
        date = "2025-07-03"
        title = "Test Memory"
        topic_slug = "custom-slug"
        
        # With topic slug
        filename = self.storage._generate_filename(title, date, topic_slug)
        assert filename == "2025-07-03-custom-slug.md"
        
        # Without topic slug (should use title)
        filename = self.storage._generate_filename(title, date)
        assert filename == "2025-07-03-test-memory.md"
    
    def test_duplicate_filename_handling(self):
        """Test handling of duplicate filenames"""
        input_data = CreateMemoryInput(
            title="Test Memory",
            content="First memory",
            source="claude-code",
            tags=["test"],
            topic_slug="same-slug"
        )
        
        # Create first memory
        memory1 = self.storage.create_memory(input_data)
        
        # Create second memory with same slug
        input_data.content = "Second memory"
        memory2 = self.storage.create_memory(input_data)
        
        # Should have different filenames
        assert memory1.filename != memory2.filename
        assert "same-slug" in memory1.filename
        assert "same-slug" in memory2.filename
        assert Path(memory1.file_path).exists()
        assert Path(memory2.file_path).exists()