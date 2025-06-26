"""
Exploration phase tools for Compass server
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from mcp_core.types import MCPTool
from ..managers.project_manager import ProjectManager, Task


logger = logging.getLogger(__name__)


# Schema definitions
class StartExplorationInputSchema(BaseModel):
    """Schema for starting exploration"""
    project_name: str = Field(description="Project name")
    focus_area: Optional[str] = Field(default=None, description="Specific area to explore")
    projects_dir: Optional[str] = Field(default="./workspace", description="Projects directory")


class StartExplorationOutputSchema(BaseModel):
    """Schema for start exploration output"""
    project_name: str
    session_number: int
    focus_task: str
    previous_context: str
    ready_for_conversation: bool
    guidance: str


class SaveExplorationSessionInputSchema(BaseModel):
    """Schema for saving exploration session"""
    project_name: str = Field(description="Project name")
    conversation_content: str = Field(description="The exploration conversation content")
    session_summary: Optional[str] = Field(default=None, description="Optional summary of the session")
    projects_dir: Optional[str] = Field(default="./workspace", description="Projects directory")


class SaveExplorationSessionOutputSchema(BaseModel):
    """Schema for save exploration session output"""
    project_name: str
    session_number: int
    file_path: str
    conversation_saved: bool
    message: str
    next_steps: List[str]


class GetProjectContextInputSchema(BaseModel):
    """Schema for getting project context"""
    project_name: str = Field(description="Project name")
    projects_dir: Optional[str] = Field(default="./workspace", description="Projects directory")


class GetProjectContextOutputSchema(BaseModel):
    """Schema for get project context output"""
    project_name: str
    current_phase: str
    previous_sessions: List[str]
    context_summary: str
    questions_remaining: List[str]


class CompleteExplorationPhaseInputSchema(BaseModel):
    """Schema for completing exploration phase"""
    project_name: str = Field(description="Project name")
    completion_summary: str = Field(description="Summary of exploration findings")
    projects_dir: Optional[str] = Field(default="./workspace", description="Projects directory")


class CompleteExplorationPhaseOutputSchema(BaseModel):
    """Schema for complete exploration phase output"""
    project_name: str
    phase_completed: bool
    next_phase: str
    completion_summary: str
    message: str
    next_steps: List[str]


# Tool definitions
exploration_tools: List[MCPTool] = [
    MCPTool(
        name="start_exploration",
        description="Begin systematic exploration session for a project",
        input_schema=StartExplorationInputSchema.model_json_schema(),
        output_schema=StartExplorationOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="save_exploration_session",
        description="Save exploration conversation and update project state",
        input_schema=SaveExplorationSessionInputSchema.model_json_schema(),
        output_schema=SaveExplorationSessionOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="get_project_context",
        description="Get previous exploration context and remaining questions",
        input_schema=GetProjectContextInputSchema.model_json_schema(),
        output_schema=GetProjectContextOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="complete_exploration_phase",
        description="Complete exploration phase and prepare for specification",
        input_schema=CompleteExplorationPhaseInputSchema.model_json_schema(),
        output_schema=CompleteExplorationPhaseOutputSchema.model_json_schema(),
    ),
]


# Default exploration tasks
DEFAULT_EXPLORATION_TASKS = [
    "Define the core problem or opportunity this project addresses",
    "Identify primary stakeholders and their specific needs",
    "Establish clear success criteria and measurement methods", 
    "Document constraints, limitations, and assumptions",
    "Analyze the broader context and environment",
    "Research existing solutions and approaches",
    "Assess available resources and capabilities",
    "Identify dependencies and external factors",
    "Define project scope and boundaries clearly",
    "Evaluate primary risks and mitigation strategies"
]


# Tool handlers
async def start_exploration_handler(args: dict) -> dict:
    """Start an exploration session"""
    validated_args = StartExplorationInputSchema(**args)
    
    try:
        projects_dir = Path(validated_args.projects_dir)
        project_path = projects_dir / validated_args.project_name
        
        if not project_path.exists():
            return StartExplorationOutputSchema(
                project_name=validated_args.project_name,
                session_number=0,
                focus_task="Project not found",
                previous_context="",
                ready_for_conversation=False,
                guidance="Initialize project first using 'init_project' tool"
            ).model_dump()
        
        project_manager = ProjectManager(str(project_path))
        metadata = await project_manager.get_project_metadata()
        
        # Check if we're in exploration phase
        if metadata.current_phase != "exploration":
            return StartExplorationOutputSchema(
                project_name=validated_args.project_name,
                session_number=metadata.session_count,
                focus_task="Not in exploration phase",
                previous_context="",
                ready_for_conversation=False,
                guidance=f"Project is in {metadata.current_phase} phase. Cannot start exploration."
            ).model_dump()
        
        # Update session count
        session_number = await project_manager.update_session_count()
        
        # Get or create exploration tasks
        try:
            tasks_data = await project_manager.parse_tasks_file()
            exploration_tasks = tasks_data.exploration_tasks
        except FileNotFoundError:
            # Create default tasks if none exist
            exploration_tasks = [Task(completed=False, text=task) for task in DEFAULT_EXPLORATION_TASKS]
            await project_manager.update_tasks_file(exploration_tasks)
        
        # Get previous context
        previous_context = await project_manager.get_exploration_context()
        
        # Determine focus task
        if validated_args.focus_area:
            focus_task = f"Deep dive into: {validated_args.focus_area}"
        else:
            # Find first incomplete task
            incomplete_tasks = [task for task in exploration_tasks if not task.completed]
            if incomplete_tasks:
                focus_task = incomplete_tasks[0].text
            else:
                focus_task = "Review and validate all exploration findings"
        
        # Generate guidance
        completed_count = len([task for task in exploration_tasks if task.completed])
        total_count = len(exploration_tasks)
        
        guidance = f"""🧭 **Exploration Session {session_number}**

**Focus:** {focus_task}

**Progress:** {completed_count}/{total_count} exploration tasks completed

**Guidelines:**
- Ask probing questions to uncover deeper insights
- Challenge assumptions and explore alternative perspectives  
- Document key decisions and their reasoning
- Don't rush to solutions - thoroughly understand the problem space
- Each topic should be explored until you have clarity and confidence

**Remember:** The goal of exploration is deep understanding, not quick answers. Take time to really understand the nuances and complexities."""
        
        logger.info(f"Started exploration session {session_number} for project: {validated_args.project_name}")
        
        return StartExplorationOutputSchema(
            project_name=validated_args.project_name,
            session_number=session_number,
            focus_task=focus_task,
            previous_context=previous_context[:1000] + "..." if len(previous_context) > 1000 else previous_context,
            ready_for_conversation=True,
            guidance=guidance
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to start exploration: {error}")
        return StartExplorationOutputSchema(
            project_name=validated_args.project_name,
            session_number=0,
            focus_task="Error occurred",
            previous_context="",
            ready_for_conversation=False,
            guidance=f"Error starting exploration: {str(error)}"
        ).model_dump()


async def save_exploration_session_handler(args: dict) -> dict:
    """Save exploration session content"""
    validated_args = SaveExplorationSessionInputSchema(**args)
    
    try:
        projects_dir = Path(validated_args.projects_dir)
        project_path = projects_dir / validated_args.project_name
        
        if not project_path.exists():
            return SaveExplorationSessionOutputSchema(
                project_name=validated_args.project_name,
                session_number=0,
                file_path="",
                conversation_saved=False,
                message="Project not found",
                next_steps=["Initialize project first"]
            ).model_dump()
        
        project_manager = ProjectManager(str(project_path))
        metadata = await project_manager.get_project_metadata()
        
        # Save conversation
        file_path = await project_manager.save_exploration_session(
            metadata.session_count,
            validated_args.conversation_content,
            validated_args.session_summary
        )
        
        # Generate next steps based on completion status
        completion_check = await project_manager.check_exploration_completion()
        
        if completion_check["is_complete"]:
            next_steps = [
                "Review all exploration content for completeness",
                "Use 'complete_exploration_phase' to move to specification",
                "Ensure all stakeholder needs are well understood"
            ]
            message = f"Exploration session saved. Project appears ready for specification phase ({completion_check['completion_rate']:.0%} complete)."
        else:
            next_steps = [
                "Continue exploration sessions for remaining topics",
                f"Complete {completion_check['total_tasks'] - completion_check['completed_tasks']} more exploration tasks",
                "Focus on areas that need deeper understanding"
            ]
            message = f"Exploration session saved. Continue exploration ({completion_check['completion_rate']:.0%} complete)."
        
        logger.info(f"Saved exploration session {metadata.session_count} for project: {validated_args.project_name}")
        
        return SaveExplorationSessionOutputSchema(
            project_name=validated_args.project_name,
            session_number=metadata.session_count,
            file_path=file_path,
            conversation_saved=True,
            message=message,
            next_steps=next_steps
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to save exploration session: {error}")
        return SaveExplorationSessionOutputSchema(
            project_name=validated_args.project_name,
            session_number=0,
            file_path="",
            conversation_saved=False,
            message=f"Error saving session: {str(error)}",
            next_steps=["Check project status and try again"]
        ).model_dump()


async def get_project_context_handler(args: dict) -> dict:
    """Get project exploration context"""
    validated_args = GetProjectContextInputSchema(**args)
    
    try:
        projects_dir = Path(validated_args.projects_dir)
        project_path = projects_dir / validated_args.project_name
        
        if not project_path.exists():
            return GetProjectContextOutputSchema(
                project_name=validated_args.project_name,
                current_phase="unknown",
                previous_sessions=[],
                context_summary="Project not found",
                questions_remaining=[]
            ).model_dump()
        
        project_manager = ProjectManager(str(project_path))
        metadata = await project_manager.get_project_metadata()
        
        # Get session files
        exploration_dir = project_path / "exploration"
        previous_sessions = []
        if exploration_dir.exists():
            for session_file in sorted(exploration_dir.glob("conversation-*.md")):
                previous_sessions.append(session_file.name)
        
        # Get context summary
        context_summary = await project_manager.get_exploration_context()
        
        # Get remaining questions
        questions_remaining = []
        try:
            tasks_data = await project_manager.parse_tasks_file()
            questions_remaining = [
                task.text for task in tasks_data.exploration_tasks 
                if not task.completed
            ]
        except Exception:
            pass
        
        return GetProjectContextOutputSchema(
            project_name=validated_args.project_name,
            current_phase=metadata.current_phase,
            previous_sessions=previous_sessions,
            context_summary=context_summary[:2000] + "..." if len(context_summary) > 2000 else context_summary,
            questions_remaining=questions_remaining
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to get project context: {error}")
        return GetProjectContextOutputSchema(
            project_name=validated_args.project_name,
            current_phase="error",
            previous_sessions=[],
            context_summary=f"Error retrieving context: {str(error)}",
            questions_remaining=[]
        ).model_dump()


async def complete_exploration_phase_handler(args: dict) -> dict:
    """Complete exploration phase and move to specification"""
    validated_args = CompleteExplorationPhaseInputSchema(**args)
    
    try:
        projects_dir = Path(validated_args.projects_dir)
        project_path = projects_dir / validated_args.project_name
        
        if not project_path.exists():
            return CompleteExplorationPhaseOutputSchema(
                project_name=validated_args.project_name,
                phase_completed=False,
                next_phase="unknown",
                completion_summary="",
                message="Project not found",
                next_steps=["Initialize project first"]
            ).model_dump()
        
        project_manager = ProjectManager(str(project_path))
        metadata = await project_manager.get_project_metadata()
        
        if metadata.current_phase != "exploration":
            return CompleteExplorationPhaseOutputSchema(
                project_name=validated_args.project_name,
                phase_completed=False,
                next_phase=metadata.current_phase,
                completion_summary="",
                message=f"Project is not in exploration phase (currently in {metadata.current_phase})",
                next_steps=[f"Continue with {metadata.current_phase} phase activities"]
            ).model_dump()
        
        # Check if exploration is sufficiently complete
        completion_check = await project_manager.check_exploration_completion()
        
        if not completion_check["is_complete"]:
            return CompleteExplorationPhaseOutputSchema(
                project_name=validated_args.project_name,
                phase_completed=False,
                next_phase="exploration",
                completion_summary="",
                message=f"Exploration not sufficiently complete ({completion_check['completion_rate']:.0%}). Need more depth.",
                next_steps=[
                    "Complete more exploration tasks",
                    "Ensure thorough understanding of all key areas",
                    "Aim for at least 80% task completion before proceeding"
                ]
            ).model_dump()
        
        # Update metadata to specification phase
        metadata.current_phase = "specification"
        metadata.exploration_completed_date = datetime.now().isoformat()
        metadata.exploration_completion_reason = validated_args.completion_summary
        await project_manager.save_project_metadata(metadata)
        
        # Create completion summary file
        completion_file = project_path / "exploration" / "completion-override.md"
        completion_content = f"""# Exploration Phase Completion

**Project:** {validated_args.project_name}
**Completed:** {datetime.now().isoformat()}
**Completion Rate:** {completion_check['completion_rate']:.0%}

## Summary

{validated_args.completion_summary}

## Completion Statistics

- **Tasks Completed:** {completion_check['completed_tasks']}/{completion_check['total_tasks']}
- **Sessions Conducted:** {metadata.session_count}
- **Completion Reason:** Sufficient exploration depth achieved

## Next Phase

The project is now ready to move to the **Specification** phase where the exploration insights will be transformed into detailed requirements and specifications.

---
*Generated by Compass MCP Server*
"""
        
        completion_file.write_text(completion_content, encoding='utf-8')
        
        logger.info(f"Completed exploration phase for project: {validated_args.project_name}")
        
        return CompleteExplorationPhaseOutputSchema(
            project_name=validated_args.project_name,
            phase_completed=True,
            next_phase="specification",
            completion_summary=validated_args.completion_summary,
            message="Exploration phase completed successfully. Ready for specification phase.",
            next_steps=[
                "Begin specification phase activities",
                "Transform exploration insights into detailed requirements",
                "Use specification tools to create structured documents"
            ]
        ).model_dump()
        
    except Exception as error:
        logger.error(f"Failed to complete exploration phase: {error}")
        return CompleteExplorationPhaseOutputSchema(
            project_name=validated_args.project_name,
            phase_completed=False,
            next_phase="exploration",
            completion_summary="",
            message=f"Error completing exploration: {str(error)}",
            next_steps=["Check project status and try again"]
        ).model_dump()


# Handler mapping
exploration_handlers = {
    "start_exploration": start_exploration_handler,
    "save_exploration_session": save_exploration_session_handler,
    "get_project_context": get_project_context_handler,
    "complete_exploration_phase": complete_exploration_phase_handler,
}