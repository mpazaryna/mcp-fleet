"""
Tests for tide tools
"""

from unittest.mock import AsyncMock, patch

import pytest
from tides.src.storage.tide_storage import TideData
from tides.src.tools.tide_tools import (
    CreateTideInputSchema,
    FlowTideInputSchema,
    create_tide_handler,
    flow_tide_handler,
    list_tides_handler,
)


@pytest.fixture
def mock_tide_data():
    """Mock tide data for testing"""
    return TideData(
        id="test_tide_123",
        name="Test Tide",
        flow_type="daily",
        status="active",
        created_at="2024-01-01T10:00:00",
        next_flow="2024-01-02T10:00:00",
        description="Test description",
        flow_history=[],
    )


@pytest.mark.asyncio
@patch("tides.src.tools.tide_tools.tide_storage")
async def test_create_tide_handler_success(mock_storage, mock_tide_data):
    """Test successful tide creation"""
    mock_storage.create_tide = AsyncMock(return_value=mock_tide_data)

    args = {
        "name": "Test Tide",
        "flow_type": "daily",
        "description": "Test description",
    }

    result = await create_tide_handler(args)

    assert result["success"] is True
    assert result["tide_id"] == "test_tide_123"
    assert result["name"] == "Test Tide"
    assert result["flow_type"] == "daily"


@pytest.mark.asyncio
@patch("tides.src.tools.tide_tools.tide_storage")
async def test_create_tide_handler_failure(mock_storage):
    """Test tide creation failure"""
    mock_storage.create_tide = AsyncMock(side_effect=Exception("Storage error"))

    args = {"name": "Test Tide", "flow_type": "daily"}

    result = await create_tide_handler(args)

    assert result["success"] is False
    assert result["tide_id"] == ""
    assert result["name"] == "Test Tide"


@pytest.mark.asyncio
@patch("tides.src.tools.tide_tools.tide_storage")
async def test_list_tides_handler_success(mock_storage, mock_tide_data):
    """Test successful tide listing"""
    mock_storage.list_tides = AsyncMock(return_value=[mock_tide_data])

    args = {"flow_type": "daily", "active_only": True}

    result = await list_tides_handler(args)

    assert result["total"] == 1
    assert len(result["tides"]) == 1
    assert result["tides"][0]["id"] == "test_tide_123"
    assert result["tides"][0]["name"] == "Test Tide"


@pytest.mark.asyncio
@patch("tides.src.tools.tide_tools.tide_storage")
async def test_list_tides_handler_empty(mock_storage):
    """Test listing tides with no results"""
    mock_storage.list_tides = AsyncMock(return_value=[])

    args = {}

    result = await list_tides_handler(args)

    assert result["total"] == 0
    assert len(result["tides"]) == 0


@pytest.mark.asyncio
@patch("tides.src.tools.tide_tools.tide_storage")
async def test_flow_tide_handler_success(mock_storage, mock_tide_data):
    """Test successful flow session start"""
    mock_storage.get_tide = AsyncMock(return_value=mock_tide_data)
    mock_storage.add_flow_to_tide = AsyncMock(return_value=mock_tide_data)

    args = {"tide_id": "test_tide_123", "intensity": "moderate", "duration": 30}

    result = await flow_tide_handler(args)

    assert result["success"] is True
    assert result["tide_id"] == "test_tide_123"
    assert "🌊" in result["flow_guidance"]
    assert len(result["next_actions"]) > 0

    # Verify flow was added to storage
    mock_storage.add_flow_to_tide.assert_called_once()


@pytest.mark.asyncio
@patch("tides.src.tools.tide_tools.tide_storage")
async def test_flow_tide_handler_tide_not_found(mock_storage):
    """Test flow session with non-existent tide"""
    mock_storage.get_tide = AsyncMock(return_value=None)

    args = {"tide_id": "nonexistent_tide", "intensity": "moderate", "duration": 25}

    result = await flow_tide_handler(args)

    assert result["success"] is False
    assert result["flow_guidance"] == "Tide not found"
    assert len(result["next_actions"]) == 0


@pytest.mark.asyncio
@patch("tides.src.tools.tide_tools.tide_storage")
async def test_flow_tide_handler_different_intensities(mock_storage, mock_tide_data):
    """Test flow session with different intensities"""
    mock_storage.get_tide = AsyncMock(return_value=mock_tide_data)
    mock_storage.add_flow_to_tide = AsyncMock(return_value=mock_tide_data)

    intensities = ["gentle", "moderate", "strong"]

    for intensity in intensities:
        args = {"tide_id": "test_tide_123", "intensity": intensity, "duration": 25}

        result = await flow_tide_handler(args)

        assert result["success"] is True
        assert "🌊" in result["flow_guidance"]
        # Each intensity should have different guidance text
        if intensity == "gentle":
            assert "calm" in result["flow_guidance"].lower()
        elif intensity == "strong":
            assert "deep" in result["flow_guidance"].lower()


def test_create_tide_input_schema_validation():
    """Test input schema validation for create tide"""
    # Valid input
    valid_data = {
        "name": "Test Tide",
        "flow_type": "daily",
        "description": "Test description",
    }
    schema = CreateTideInputSchema(**valid_data)
    assert schema.name == "Test Tide"
    assert schema.flow_type == "daily"

    # Invalid flow type should raise validation error
    with pytest.raises(ValueError):
        CreateTideInputSchema(name="Test", flow_type="invalid_type")


def test_flow_tide_input_schema_defaults():
    """Test default values in flow tide input schema"""
    schema = FlowTideInputSchema(tide_id="test_123")

    assert schema.tide_id == "test_123"
    assert schema.intensity == "moderate"  # Default
    assert schema.duration == 25  # Default
