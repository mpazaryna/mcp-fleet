"""
Tests for tide storage
"""
import pytest
import tempfile
import shutil
from pathlib import Path

from tides.src.storage.tide_storage import (
    TideStorage, CreateTideInput, ListTidesFilter, FlowEntry, TideData
)


@pytest.fixture
async def temp_storage():
    """Create temporary storage for testing"""
    temp_dir = tempfile.mkdtemp()
    storage = TideStorage(temp_dir)
    yield storage
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_create_tide(temp_storage):
    """Test tide creation"""
    input_data = CreateTideInput(
        name="Morning Flow",
        flow_type="daily",
        description="Daily morning productivity session"
    )
    
    tide = await temp_storage.create_tide(input_data)
    
    assert tide.name == "Morning Flow"
    assert tide.flow_type == "daily"
    assert tide.status == "active"
    assert tide.description == "Daily morning productivity session"
    assert tide.next_flow is not None  # Should have next flow for daily
    assert len(tide.flow_history) == 0


@pytest.mark.asyncio
async def test_create_project_tide(temp_storage):
    """Test creating project-type tide"""
    input_data = CreateTideInput(
        name="Website Redesign",
        flow_type="project"
    )
    
    tide = await temp_storage.create_tide(input_data)
    
    assert tide.flow_type == "project"
    assert tide.next_flow is None  # Project type has no automatic next flow


@pytest.mark.asyncio
async def test_get_tide(temp_storage):
    """Test getting a tide by ID"""
    input_data = CreateTideInput(name="Test Tide", flow_type="weekly")
    created_tide = await temp_storage.create_tide(input_data)
    
    retrieved_tide = await temp_storage.get_tide(created_tide.id)
    
    assert retrieved_tide is not None
    assert retrieved_tide.id == created_tide.id
    assert retrieved_tide.name == "Test Tide"


@pytest.mark.asyncio
async def test_get_nonexistent_tide(temp_storage):
    """Test getting a tide that doesn't exist"""
    result = await temp_storage.get_tide("nonexistent_id")
    assert result is None


@pytest.mark.asyncio
async def test_list_tides(temp_storage):
    """Test listing tides"""
    # Create multiple tides
    await temp_storage.create_tide(CreateTideInput(name="Daily Flow", flow_type="daily"))
    await temp_storage.create_tide(CreateTideInput(name="Weekly Review", flow_type="weekly"))
    await temp_storage.create_tide(CreateTideInput(name="Project Work", flow_type="project"))
    
    tides = await temp_storage.list_tides()
    
    assert len(tides) == 3
    # Should be sorted by created_at descending
    assert tides[0].name == "Project Work"  # Most recent


@pytest.mark.asyncio
async def test_list_tides_with_filter(temp_storage):
    """Test listing tides with filters"""
    await temp_storage.create_tide(CreateTideInput(name="Daily Flow", flow_type="daily"))
    await temp_storage.create_tide(CreateTideInput(name="Weekly Review", flow_type="weekly"))
    
    # Filter by flow type
    filter_data = ListTidesFilter(flow_type="daily")
    tides = await temp_storage.list_tides(filter_data)
    
    assert len(tides) == 1
    assert tides[0].name == "Daily Flow"


@pytest.mark.asyncio
async def test_add_flow_to_tide(temp_storage):
    """Test adding a flow entry to a tide"""
    input_data = CreateTideInput(name="Test Tide", flow_type="daily")
    tide = await temp_storage.create_tide(input_data)
    
    flow_entry = FlowEntry(
        timestamp="2024-01-01T10:00:00",
        intensity="moderate",
        duration=25,
        notes="Great focus session"
    )
    
    updated_tide = await temp_storage.add_flow_to_tide(tide.id, flow_entry)
    
    assert updated_tide is not None
    assert len(updated_tide.flow_history) == 1
    assert updated_tide.flow_history[0].intensity == "moderate"
    assert updated_tide.last_flow == "2024-01-01T10:00:00"


@pytest.mark.asyncio
async def test_update_tide(temp_storage):
    """Test updating a tide"""
    input_data = CreateTideInput(name="Original Name", flow_type="daily")
    tide = await temp_storage.create_tide(input_data)
    
    updates = {"name": "Updated Name", "status": "paused"}
    updated_tide = await temp_storage.update_tide(tide.id, updates)
    
    assert updated_tide is not None
    assert updated_tide.name == "Updated Name"
    assert updated_tide.status == "paused"
    assert updated_tide.id == tide.id  # ID should not change


@pytest.mark.asyncio
async def test_update_nonexistent_tide(temp_storage):
    """Test updating a tide that doesn't exist"""
    result = await temp_storage.update_tide("nonexistent_id", {"name": "New Name"})
    assert result is None