"""
Orchestration Framework (OF) tools
"""
import logging
import os
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

# Simple tool definition to replace MCPTool
class MCPTool:
    def __init__(self, name: str, description: str, input_schema: dict, output_schema: dict):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema
from ..workspace_manager import WorkspaceManager, ProjectData


logger = logging.getLogger(__name__)

# Initialize workspace manager
workspace_manager = WorkspaceManager()


# Schema definitions
class CreateProjectInputSchema(BaseModel):
    """Schema for creating a project"""
    name: str = Field(description="Name of the project")
    description: Optional[str] = Field(default=None, description="Project description")


class CreateProjectOutputSchema(BaseModel):
    """Schema for create project output"""
    success: bool
    project_id: str
    project_name: str
    project_path: str
    phase: str
    message: str


class ListProjectsOutputSchema(BaseModel):
    """Schema for list projects output"""
    success: bool
    projects: List[dict]
    total_count: int


class UpdateProjectPhaseInputSchema(BaseModel):
    """Schema for updating project phase"""
    project_name: str = Field(description="Name of the project")
    phase: str = Field(description="New phase (exploration, specification, execution, feedback)")


class UpdateProjectPhaseOutputSchema(BaseModel):
    """Schema for update project phase output"""
    success: bool
    project_name: str
    new_phase: str
    message: str


class SaveSessionNotesInputSchema(BaseModel):
    """Schema for saving session notes"""
    project_name: str = Field(description="Name of the project")
    phase: str = Field(description="Project phase")
    content: str = Field(description="Session notes content")
    session_type: str = Field(default="notes", description="Type of session (notes, insights, decisions)")


class SaveSessionNotesOutputSchema(BaseModel):
    """Schema for save session notes output"""
    success: bool
    file_path: str
    message: str


# Tool handlers
async def create_project_handler(arguments: dict) -> dict:
    """Handle create project requests"""
    try:
        # Validate input
        validated_args = CreateProjectInputSchema(**arguments)
        
        # Create project
        project_data = await workspace_manager.create_project(
            name=validated_args.name,
            description=validated_args.description
        )
        
        logger.info(f"Created project: {project_data.name} (ID: {project_data.id})")
        
        return CreateProjectOutputSchema(
            success=True,
            project_id=project_data.id,
            project_name=project_data.name,
            project_path=str(workspace_manager.workspace_path / project_data.name),
            phase=project_data.phase,
            message=f"Project '{project_data.name}' created successfully. Starting in exploration phase."
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to create project: {error}")
        return CreateProjectOutputSchema(
            success=False,
            project_id="",
            project_name="",
            project_path="",
            phase="",
            message=f"Failed to create project: {error}"
        ).model_dump()


async def list_projects_handler(arguments: dict) -> dict:
    """Handle list projects requests"""
    try:
        projects = await workspace_manager.list_projects()
        
        project_list = [
            {
                "name": p.name,
                "phase": p.phase,
                "status": p.status,
                "created_at": p.created_at,
                "description": p.description
            }
            for p in projects
        ]
        
        return ListProjectsOutputSchema(
            success=True,
            projects=project_list,
            total_count=len(projects)
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to list projects: {error}")
        return ListProjectsOutputSchema(
            success=False,
            projects=[],
            total_count=0
        ).model_dump()


async def update_project_phase_handler(arguments: dict) -> dict:
    """Handle update project phase requests"""
    try:
        # Validate input
        validated_args = UpdateProjectPhaseInputSchema(**arguments)
        
        # Update project phase
        project_data = await workspace_manager.update_project_phase(
            name=validated_args.project_name,
            phase=validated_args.phase
        )
        
        if not project_data:
            return UpdateProjectPhaseOutputSchema(
                success=False,
                project_name=validated_args.project_name,
                new_phase="",
                message=f"Project '{validated_args.project_name}' not found"
            ).model_dump()
        
        logger.info(f"Updated project {project_data.name} to phase: {project_data.phase}")
        
        return UpdateProjectPhaseOutputSchema(
            success=True,
            project_name=project_data.name,
            new_phase=project_data.phase,
            message=f"Project '{project_data.name}' moved to {project_data.phase} phase"
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to update project phase: {error}")
        return UpdateProjectPhaseOutputSchema(
            success=False,
            project_name="",
            new_phase="",
            message=f"Failed to update project phase: {error}"
        ).model_dump()


async def save_session_notes_handler(arguments: dict) -> dict:
    """Handle save session notes requests"""
    try:
        # Validate input
        validated_args = SaveSessionNotesInputSchema(**arguments)
        
        # Save session notes
        file_path = await workspace_manager.save_session_notes(
            project_name=validated_args.project_name,
            phase=validated_args.phase,
            content=validated_args.content,
            session_type=validated_args.session_type
        )
        
        logger.info(f"Saved session notes to: {file_path}")
        
        return SaveSessionNotesOutputSchema(
            success=True,
            file_path=file_path,
            message=f"Session notes saved successfully to {file_path}"
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to save session notes: {error}")
        return SaveSessionNotesOutputSchema(
            success=False,
            file_path="",
            message=f"Failed to save session notes: {error}"
        ).model_dump()


# Tool definitions
of_tools = [
    MCPTool(
        name="create_project",
        description="Create a new OF project with 4-phase methodology structure",
        input_schema=CreateProjectInputSchema.model_json_schema(),
        output_schema=CreateProjectOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="list_projects",
        description="List all OF projects in the workspace",
        input_schema={},
        output_schema=ListProjectsOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="update_project_phase",
        description="Update a project to a new phase (exploration, specification, execution, feedback)",
        input_schema=UpdateProjectPhaseInputSchema.model_json_schema(),
        output_schema=UpdateProjectPhaseOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="save_session_notes",
        description="Save session notes, insights, or decisions to a project phase",
        input_schema=SaveSessionNotesInputSchema.model_json_schema(),
        output_schema=SaveSessionNotesOutputSchema.model_json_schema(),
    ),
]

# Handler mapping
of_handlers = {
    "create_project": create_project_handler,
    "list_projects": list_projects_handler,
    "update_project_phase": update_project_phase_handler,
    "save_session_notes": save_session_notes_handler,
}