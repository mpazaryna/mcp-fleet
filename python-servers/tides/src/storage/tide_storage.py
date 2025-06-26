"""
Storage implementation for tidal workflows
"""
import json
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import BaseModel


FlowType = Literal["daily", "weekly", "project", "seasonal"]
TideStatus = Literal["active", "paused", "completed"]
FlowIntensity = Literal["gentle", "moderate", "strong"]


class FlowEntry(BaseModel):
    """Flow entry in tide history"""
    timestamp: str
    intensity: FlowIntensity
    duration: int
    notes: Optional[str] = None


class TideData(BaseModel):
    """Tide data structure"""
    id: str
    name: str
    flow_type: FlowType
    status: TideStatus
    created_at: str
    last_flow: Optional[str] = None
    next_flow: Optional[str] = None
    description: Optional[str] = None
    flow_history: List[FlowEntry] = []


class CreateTideInput(BaseModel):
    """Input for creating a new tide"""
    name: str
    flow_type: FlowType
    description: Optional[str] = None


class ListTidesFilter(BaseModel):
    """Filter for listing tides"""
    flow_type: Optional[str] = None
    active_only: Optional[bool] = None


class TideStorage:
    """Storage for tidal workflows"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_tide(self, input_data: CreateTideInput) -> TideData:
        """Create a new tide"""
        now = datetime.now()
        tide_id = f"tide_{int(time.time())}_{random.randint(100000, 999999)}"
        
        # Calculate next flow based on type
        next_flow = None
        if input_data.flow_type == "daily":
            next_flow = (now + timedelta(days=1)).isoformat()
        elif input_data.flow_type == "weekly":
            next_flow = (now + timedelta(weeks=1)).isoformat()
        elif input_data.flow_type == "seasonal":
            next_flow = (now + timedelta(days=90)).isoformat()
        # project type has no automatic next flow
        
        tide = TideData(
            id=tide_id,
            name=input_data.name,
            flow_type=input_data.flow_type,
            status="active",
            created_at=now.isoformat(),
            next_flow=next_flow,
            description=input_data.description,
            flow_history=[]
        )
        
        await self._save_tide(tide)
        return tide
    
    async def get_tide(self, tide_id: str) -> Optional[TideData]:
        """Get a tide by ID"""
        file_path = self.data_dir / f"{tide_id}.json"
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return TideData(**data)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    async def list_tides(self, filter_data: Optional[ListTidesFilter] = None) -> List[TideData]:
        """List all tides with optional filtering"""
        if filter_data is None:
            filter_data = ListTidesFilter()
        
        tides = []
        
        try:
            for file_path in self.data_dir.glob("*.json"):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            tide = TideData(**data)
                            
                            # Apply filters
                            if filter_data.flow_type and tide.flow_type != filter_data.flow_type:
                                continue
                            
                            if filter_data.active_only and tide.status != "active":
                                continue
                            
                            tides.append(tide)
                    except (json.JSONDecodeError, ValueError):
                        # Skip invalid files
                        continue
            
            # Sort by created_at descending
            tides.sort(key=lambda t: datetime.fromisoformat(t.created_at), reverse=True)
            return tides
            
        except Exception:
            return []
    
    async def update_tide(self, tide_id: str, updates: dict) -> Optional[TideData]:
        """Update a tide with partial data"""
        tide = await self.get_tide(tide_id)
        if not tide:
            return None
        
        # Create updated tide, ensuring ID can't be changed
        tide_dict = tide.model_dump()
        tide_dict.update(updates)
        tide_dict["id"] = tide_id  # Ensure ID can't be changed
        
        updated_tide = TideData(**tide_dict)
        await self._save_tide(updated_tide)
        return updated_tide
    
    async def add_flow_to_tide(
        self,
        tide_id: str,
        flow_entry: FlowEntry
    ) -> Optional[TideData]:
        """Add a flow entry to a tide's history"""
        tide = await self.get_tide(tide_id)
        if not tide:
            return None
        
        # Add flow to history
        tide.flow_history.append(flow_entry)
        tide.last_flow = flow_entry.timestamp
        
        # Update next_flow for recurring types
        flow_time = datetime.fromisoformat(flow_entry.timestamp)
        if tide.flow_type == "daily":
            tide.next_flow = (flow_time + timedelta(days=1)).isoformat()
        elif tide.flow_type == "weekly":
            tide.next_flow = (flow_time + timedelta(weeks=1)).isoformat()
        elif tide.flow_type == "seasonal":
            tide.next_flow = (flow_time + timedelta(days=90)).isoformat()
        
        await self._save_tide(tide)
        return tide
    
    async def _save_tide(self, tide: TideData) -> None:
        """Save a tide to storage"""
        file_path = self.data_dir / f"{tide.id}.json"
        with open(file_path, 'w') as f:
            json.dump(tide.model_dump(), f, indent=2)