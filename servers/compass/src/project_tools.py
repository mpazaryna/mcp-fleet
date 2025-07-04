"""
Project management tools for Compass server
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from core.types import MCPTool
from .project_manager import ProjectManager, ProjectMetadata


logger = logging.getLogger(__name__)

# Get workspace path from environment or use default
DEFAULT_WORKSPACE = os.getenv("COMPASS_WORKSPACE", "./workspace")


# Schema definitions
class InitProjectInputSchema(BaseModel):
    """Schema for initializing a project"""
    name: str = Field(description="Name of the project to initialize")
    projects_dir: Optional[str] = Field(default=DEFAULT_WORKSPACE, description="Projects directory")


class InitProjectOutputSchema(BaseModel):
    """Schema for init project output"""
    success: bool
    project_name: str
    project_path: str
    message: str
    next_steps: List[str]


class ProjectSummary(BaseModel):
    """Project summary for listing"""
    name: str
    path: str
    status: str
    current_phase: str
    created: str


class ListProjectsInputSchema(BaseModel):
    """Schema for listing projects"""
    projects_dir: Optional[str] = Field(default=DEFAULT_WORKSPACE, description="Projects directory")


class ListProjectsOutputSchema(BaseModel):
    """Schema for list projects output"""
    projects: List[ProjectSummary]
    total: int


class TaskSummary(BaseModel):
    """Task summary for status"""
    text: str
    completed: bool


class GetProjectStatusInputSchema(BaseModel):
    """Schema for getting project status"""
    project_name: str = Field(description="Name of the project")
    projects_dir: Optional[str] = Field(default=DEFAULT_WORKSPACE, description="Projects directory")


class GetProjectStatusOutputSchema(BaseModel):
    """Schema for project status output"""
    project_name: str
    current_phase: str
    status_summary: str
    exploration_tasks: List[TaskSummary]
    next_action: str
    recommendations: List[str]


# Tool definitions
project_tools: List[MCPTool] = [
    MCPTool(
        name="init_project",
        description="Initialize a new Compass project with systematic methodology structure",
        input_schema=InitProjectInputSchema.model_json_schema(),
        output_schema=InitProjectOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="list_projects",
        description="List all Compass projects with their current status",
        input_schema=ListProjectsInputSchema.model_json_schema(),
        output_schema=ListProjectsOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="get_project_status",
        description="Get detailed status and progress of a specific project",
        input_schema=GetProjectStatusInputSchema.model_json_schema(),
        output_schema=GetProjectStatusOutputSchema.model_json_schema(),
    ),
]


# Tool handlers
async def init_project_handler(args: dict) -> dict:
    """Initialize a new Compass project"""
    validated_args = InitProjectInputSchema(**args)
    
    try:
        projects_dir = Path(validated_args.projects_dir)
        projects_dir.mkdir(parents=True, exist_ok=True)
        
        project_path = projects_dir / validated_args.name
        
        if project_path.exists():
            return InitProjectOutputSchema(
                success=False,
                project_name=validated_args.name,
                project_path=str(project_path),
                message=f"Project '{validated_args.name}' already exists",
                next_steps=["Choose a different project name", "Use existing project"]
            ).model_dump()
        
        # Create project structure
        project_path.mkdir(parents=True, exist_ok=True)
        (project_path / "exploration").mkdir(exist_ok=True)
        (project_path / "specification").mkdir(exist_ok=True)
        (project_path / "execution").mkdir(exist_ok=True)
        (project_path / "feedback").mkdir(exist_ok=True)
        
        # Create project manager and initialize metadata
        project_manager = ProjectManager(str(project_path))
        metadata = ProjectMetadata(
            name=validated_args.name,
            created=datetime.now().isoformat(),
            current_phase="exploration",
            status="active",
            session_count=0
        )
        await project_manager.save_project_metadata(metadata)
        
        # Create initial tasks.md
        await project_manager.update_tasks_file(
            exploration_tasks=[],
            next_action="Start exploration with 'start_exploration' tool"
        )
        
        # Create questions.md for exploration guidance
        questions_content = f"""# {validated_args.name} - Exploration Questions

## Core Understanding Questions

- [ ] What is the fundamental problem or opportunity this project addresses?
- [ ] Who are the primary stakeholders and what are their needs?
- [ ] What are the success criteria and how will we measure them?
- [ ] What constraints and limitations exist?
- [ ] What assumptions are we making that need validation?

## Context & Environment

- [ ] What is the broader context this project operates within?
- [ ] What existing solutions or approaches have been tried?
- [ ] What resources and capabilities are available?
- [ ] What dependencies and external factors must be considered?

## Scope & Boundaries

- [ ] What is explicitly included in this project scope?
- [ ] What is explicitly excluded from this project scope?
- [ ] What are the minimum viable requirements?
- [ ] What are the nice-to-have enhancements?

## Risks & Challenges

- [ ] What are the primary risks and how can they be mitigated?
- [ ] What technical challenges need to be solved?
- [ ] What organizational or process challenges exist?
- [ ] What unknown unknowns might we discover?

---

*Use these questions to guide exploration conversations. Each question should be thoroughly explored before moving to specification phase.*
"""
        
        questions_path = project_path / "exploration" / "questions.md"
        questions_path.write_text(questions_content, encoding='utf-8')
        
        logger.info(f"Initialized new Compass project: {validated_args.name}")
        
        return InitProjectOutputSchema(
            success=True,
            project_name=validated_args.name,
            project_path=str(project_path),
            message=f"Successfully initialized Compass project '{validated_args.name}'",
            next_steps=[
                "Review exploration questions in exploration/questions.md",
                "Start exploration session with 'start_exploration' tool",
                "Work through systematic exploration before moving to specification"
            ]
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to initialize project: {error}")
        return InitProjectOutputSchema(
            success=False,
            project_name=validated_args.name,
            project_path="",
            message=f"Failed to initialize project: {str(error)}",
            next_steps=["Check permissions and try again"]
        ).model_dump()


async def list_projects_handler(args: dict) -> dict:
    """List all Compass projects"""
    validated_args = ListProjectsInputSchema(**args)
    
    try:
        projects_dir = Path(validated_args.projects_dir)
        if not projects_dir.exists():
            return ListProjectsOutputSchema(
                projects=[],
                total=0
            ).model_dump()
        
        projects = []
        
        for item in projects_dir.iterdir():
            if item.is_dir():
                compass_file = item / ".compass.json"
                if compass_file.exists():
                    try:
                        metadata_data = json.loads(compass_file.read_text())
                        metadata = ProjectMetadata.model_validate(metadata_data)
                        
                        projects.append(ProjectSummary(
                            name=metadata.name,
                            path=str(item),
                            status=metadata.status,
                            current_phase=metadata.current_phase,
                            created=metadata.created
                        ))
                    except Exception:
                        # Skip invalid projects
                        continue
        
        # Sort by created date, newest first
        projects.sort(key=lambda p: p.created, reverse=True)
        
        return ListProjectsOutputSchema(
            projects=projects,
            total=len(projects)
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to list projects: {error}")
        return ListProjectsOutputSchema(
            projects=[],
            total=0
        ).model_dump()


async def get_project_status_handler(args: dict) -> dict:
    """Get detailed project status"""
    validated_args = GetProjectStatusInputSchema(**args)
    
    try:
        projects_dir = Path(validated_args.projects_dir)
        project_path = projects_dir / validated_args.project_name
        
        if not project_path.exists():
            return GetProjectStatusOutputSchema(
                project_name=validated_args.project_name,
                current_phase="unknown",
                status_summary="Project not found",
                exploration_tasks=[],
                next_action="Initialize project first",
                recommendations=["Use 'init_project' tool to create this project"]
            ).model_dump()
        
        project_manager = ProjectManager(str(project_path))
        metadata = await project_manager.get_project_metadata()
        
        # Get exploration tasks
        exploration_tasks = []
        try:
            tasks_data = await project_manager.parse_tasks_file()
            exploration_tasks = [
                TaskSummary(text=task.text, completed=task.completed)
                for task in tasks_data.exploration_tasks
            ]
        except Exception:
            pass
        
        # Generate status summary
        completed_tasks = len([t for t in exploration_tasks if t.completed])
        total_tasks = len(exploration_tasks)
        
        if metadata.current_phase == "exploration":
            if total_tasks == 0:
                status_summary = "Exploration not started - no tasks defined yet"
                next_action = "Start exploration session to begin systematic discovery"
                recommendations = [
                    "Use 'start_exploration' tool to begin guided exploration",
                    "Review questions.md for exploration guidance",
                    "Focus on understanding the problem deeply before solutions"
                ]
            elif completed_tasks < total_tasks * 0.8:
                status_summary = f"Exploration in progress ({completed_tasks}/{total_tasks} tasks completed)"
                next_action = "Continue exploration sessions to complete remaining tasks"
                recommendations = [
                    "Focus on completing unchecked exploration tasks",
                    "Ensure each topic is thoroughly explored",
                    "Document insights and decisions in exploration sessions"
                ]
            else:
                status_summary = f"Exploration nearly complete ({completed_tasks}/{total_tasks} tasks completed)"
                next_action = "Complete remaining exploration or move to specification"
                recommendations = [
                    "Complete final exploration tasks",
                    "Review all exploration content for completeness",
                    "Use 'complete_exploration_phase' when ready to proceed"
                ]
        else:
            status_summary = f"Project in {metadata.current_phase} phase"
            next_action = f"Continue {metadata.current_phase} activities"
            recommendations = [f"Focus on {metadata.current_phase} phase requirements"]
        
        return GetProjectStatusOutputSchema(
            project_name=validated_args.project_name,
            current_phase=metadata.current_phase,
            status_summary=status_summary,
            exploration_tasks=exploration_tasks,
            next_action=next_action,
            recommendations=recommendations
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to get project status: {error}")
        return GetProjectStatusOutputSchema(
            project_name=validated_args.project_name,
            current_phase="error",
            status_summary=f"Error retrieving status: {str(error)}",
            exploration_tasks=[],
            next_action="Check project and try again",
            recommendations=["Ensure project exists and is properly initialized"]
        ).model_dump()


# Handler mapping
project_handlers = {
    "init_project": init_project_handler,
    "list_projects": list_projects_handler,
    "get_project_status": get_project_status_handler,
}