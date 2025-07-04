"""
Tidal workflow management tools
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Literal

from core.types import MCPTool
from pydantic import BaseModel, Field

from .tide_storage import CreateTideInput, FlowEntry, ListTidesFilter, TideStorage

logger = logging.getLogger(__name__)


# Initialize storage (use mounted volume in Docker or local directory for development)
import os

storage_path = os.getenv("TIDES_STORAGE_PATH", "./tides_data")
tide_storage = TideStorage(storage_path)


# Schema definitions
class CreateTideInputSchema(BaseModel):
    """Schema for creating a tide"""

    name: str = Field(description="Name of the tidal workflow")
    flow_type: Literal["daily", "weekly", "project", "seasonal"] = Field(
        description="Type of tidal flow"
    )
    description: str | None = Field(
        default=None, description="Description of the workflow"
    )


class CreateTideOutputSchema(BaseModel):
    """Schema for create tide output"""

    success: bool
    tide_id: str
    name: str
    flow_type: str
    created_at: str
    next_flow: str | None = None


class TideSummary(BaseModel):
    """Summary of a tide for listing"""

    id: str
    name: str
    flow_type: str
    status: Literal["active", "paused", "completed"]
    created_at: str
    last_flow: str | None = None
    next_flow: str | None = None


class ListTidesInputSchema(BaseModel):
    """Schema for listing tides"""

    flow_type: str | None = Field(default=None, description="Filter by flow type")
    active_only: bool | None = Field(default=None, description="Show only active tides")


class ListTidesOutputSchema(BaseModel):
    """Schema for list tides output"""

    tides: list[TideSummary]
    total: int


class FlowTideInputSchema(BaseModel):
    """Schema for flowing a tide"""

    tide_id: str = Field(description="ID of the tide to flow")
    intensity: Literal["gentle", "moderate", "strong"] | None = Field(
        default="moderate", description="Flow intensity"
    )
    duration: int | None = Field(default=25, description="Flow duration in minutes")


class FlowTideOutputSchema(BaseModel):
    """Schema for flow tide output"""

    success: bool
    tide_id: str
    flow_started: str
    estimated_completion: str
    flow_guidance: str
    next_actions: list[str]


# Tool definitions
tide_tools: list[MCPTool] = [
    MCPTool(
        name="create_tide",
        description="Create a new tidal workflow for rhythmic productivity",
        input_schema=CreateTideInputSchema.model_json_schema(),
        output_schema=CreateTideOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="list_tides",
        description="List all tidal workflows with their current status",
        input_schema=ListTidesInputSchema.model_json_schema(),
        output_schema=ListTidesOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="flow_tide",
        description="Start a flow session for a specific tidal workflow",
        input_schema=FlowTideInputSchema.model_json_schema(),
        output_schema=FlowTideOutputSchema.model_json_schema(),
    ),
]


# Tool handlers
async def create_tide_handler(args: dict[str, Any]) -> dict[str, Any]:
    """Handle tide creation"""
    validated_args = CreateTideInputSchema(**args)

    try:
        input_data = CreateTideInput(
            name=validated_args.name,
            flow_type=validated_args.flow_type,
            description=validated_args.description,
        )

        tide = await tide_storage.create_tide(input_data)

        logger.info(
            f"Creating tide: {validated_args.name} ({validated_args.flow_type})"
        )

        return CreateTideOutputSchema(
            success=True,
            tide_id=tide.id,
            name=tide.name,
            flow_type=tide.flow_type,
            created_at=tide.created_at,
            next_flow=tide.next_flow,
        ).model_dump()

    except Exception as error:
        logger.error(f"Failed to create tide: {error}")
        return CreateTideOutputSchema(
            success=False,
            tide_id="",
            name=validated_args.name,
            flow_type=validated_args.flow_type,
            created_at=datetime.now().isoformat(),
        ).model_dump()


async def list_tides_handler(args: dict[str, Any]) -> dict[str, Any]:
    """Handle listing tides"""
    validated_args = ListTidesInputSchema(**args)

    try:
        filter_data = ListTidesFilter(
            flow_type=validated_args.flow_type, active_only=validated_args.active_only
        )

        tides = await tide_storage.list_tides(filter_data)

        tide_summaries = [
            TideSummary(
                id=tide.id,
                name=tide.name,
                flow_type=tide.flow_type,
                status=tide.status,
                created_at=tide.created_at,
                last_flow=tide.last_flow,
                next_flow=tide.next_flow,
            )
            for tide in tides
        ]

        return ListTidesOutputSchema(
            tides=tide_summaries, total=len(tide_summaries)
        ).model_dump()

    except Exception as error:
        logger.error(f"Failed to list tides: {error}")
        return ListTidesOutputSchema(tides=[], total=0).model_dump()


async def flow_tide_handler(args: dict[str, Any]) -> dict[str, Any]:
    """Handle starting a flow session"""
    validated_args = FlowTideInputSchema(**args)

    try:
        # Verify tide exists
        tide = await tide_storage.get_tide(validated_args.tide_id)
        if not tide:
            return FlowTideOutputSchema(
                success=False,
                tide_id=validated_args.tide_id,
                flow_started="",
                estimated_completion="",
                flow_guidance="Tide not found",
                next_actions=[],
            ).model_dump()

        # Ensure we have valid values (Pydantic should provide defaults)
        intensity = validated_args.intensity or "moderate"
        duration = validated_args.duration or 25

        flow_started = datetime.now().isoformat()
        estimated_completion = (
            datetime.now() + timedelta(minutes=float(duration))
        ).isoformat()

        # Add flow to tide history
        flow_entry = FlowEntry(
            timestamp=flow_started,
            intensity=intensity,
            duration=duration,
        )

        await tide_storage.add_flow_to_tide(validated_args.tide_id, flow_entry)

        # Generate guidance based on intensity
        guidance_map = {
            "gentle": "🌊 Begin with calm, steady focus. Let thoughts flow naturally without forcing. Take breaks as needed.",
            "moderate": "🌊 Maintain focused attention with deliberate action. Balance effort with ease. Stay present to the work.",
            "strong": "🌊 Dive deep with sustained concentration. Channel energy into meaningful progress. Push through resistance mindfully.",
        }

        flow_guidance = guidance_map[intensity]

        next_actions = [
            "🎯 Set clear intention for this flow session",
            "⏰ Start timer and begin focused work",
            "🧘 Take mindful breaks if needed",
            "📝 Capture insights and progress",
            "🌊 Honor the natural rhythm of the work",
        ]

        logger.info(
            f"Starting flow session for tide: {validated_args.tide_id} "
            f"({validated_args.intensity} intensity, {validated_args.duration}min)"
        )

        return FlowTideOutputSchema(
            success=True,
            tide_id=validated_args.tide_id,
            flow_started=flow_started,
            estimated_completion=estimated_completion,
            flow_guidance=flow_guidance,
            next_actions=next_actions,
        ).model_dump()

    except Exception as error:
        logger.error(f"Failed to start flow: {error}")
        return FlowTideOutputSchema(
            success=False,
            tide_id=validated_args.tide_id,
            flow_started="",
            estimated_completion="",
            flow_guidance="Failed to start flow session",
            next_actions=[],
        ).model_dump()


# Handler mapping
tide_handlers = {
    "create_tide": create_tide_handler,
    "list_tides": list_tides_handler,
    "flow_tide": flow_tide_handler,
}
