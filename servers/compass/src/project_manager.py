"""
Project manager for Compass server
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class Task(BaseModel):
    """Task representation"""

    completed: bool
    text: str


class TasksData(BaseModel):
    """Tasks data structure"""

    exploration_tasks: list[Task]
    current_phase: str


class ProjectMetadata(BaseModel):
    """Project metadata structure"""

    name: str
    created: str
    current_phase: str
    status: str
    session_count: int
    last_session_date: str | None = None
    exploration_completed_date: str | None = None
    exploration_completion_reason: str | None = None

    class Config:
        extra = "allow"  # Allow additional fields


class ProjectManager:
    """Manages Compass project structure and metadata"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    async def parse_tasks_file(self) -> TasksData:
        """Parse tasks.md file and return structured task data"""
        tasks_path = self.project_path / "tasks.md"

        if not tasks_path.exists():
            raise FileNotFoundError("tasks.md not found")

        content = tasks_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        exploration_tasks: list[Task] = []
        in_exploration_phase = False
        current_phase = "exploration"  # TODO: Detect from content

        for line in lines:
            if "## Phase 1: Exploration" in line:
                in_exploration_phase = True
                continue
            if "## Phase 2:" in line:
                in_exploration_phase = False

            if in_exploration_phase and ("- [x]" in line or "- [ ]" in line):
                completed = "- [x]" in line
                text = re.sub(r"- \[[x ]\]", "", line).strip()
                exploration_tasks.append(Task(completed=completed, text=text))

        return TasksData(
            exploration_tasks=exploration_tasks, current_phase=current_phase
        )

    async def update_tasks_file(
        self, exploration_tasks: list[Task], next_action: str = "continue exploration"
    ) -> None:
        """Update tasks.md with new or modified tasks"""
        try:
            metadata_path = self.project_path / ".compass.json"
            metadata = ProjectMetadata.model_validate(
                json.loads(metadata_path.read_text())
            )
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default metadata if not found
            metadata = ProjectMetadata(
                name=self.project_path.name,
                created=datetime.now().isoformat(),
                current_phase="exploration",
                status="active",
                session_count=0,
            )

        tasks_content = f"""# {metadata.name} - Compass Project Tasks

**Current Phase:** {metadata.current_phase.title()}
**Status:** {metadata.status.title()}
**Created:** {metadata.created}
**Sessions:** {metadata.session_count}

## Phase 1: Exploration

### Core Questions & Tasks
"""

        for task in exploration_tasks:
            checkbox = "[x]" if task.completed else "[ ]"
            tasks_content += f"- {checkbox} {task.text}\n"

        tasks_content += f"""

## Phase 2: Specification
(Locked until exploration phase complete)

## Phase 3: Execution
(Locked until specification phase complete)

## Phase 4: Feedback
(Locked until execution phase complete)

---

**Next Action:** {next_action}

**Note:** This project follows the Compass methodology. Each phase must be
completed thoroughly before proceeding to the next phase.
"""

        tasks_path = self.project_path / "tasks.md"
        tasks_path.write_text(tasks_content, encoding="utf-8")

    async def get_project_metadata(self) -> ProjectMetadata:
        """Get project metadata from .compass.json"""
        metadata_path = self.project_path / ".compass.json"

        if not metadata_path.exists():
            # Create default metadata
            metadata = ProjectMetadata(
                name=self.project_path.name,
                created=datetime.now().isoformat(),
                current_phase="exploration",
                status="active",
                session_count=0,
            )
            await self.save_project_metadata(metadata)
            return metadata

        try:
            data = json.loads(metadata_path.read_text())
            return ProjectMetadata.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            # Create new metadata if corrupted
            metadata = ProjectMetadata(
                name=self.project_path.name,
                created=datetime.now().isoformat(),
                current_phase="exploration",
                status="active",
                session_count=0,
            )
            await self.save_project_metadata(metadata)
            return metadata

    async def save_project_metadata(self, metadata: ProjectMetadata) -> None:
        """Save project metadata to .compass.json"""
        metadata_path = self.project_path / ".compass.json"
        metadata_path.write_text(
            json.dumps(metadata.model_dump(), indent=2), encoding="utf-8"
        )

    async def update_session_count(self) -> int:
        """Increment and return session count"""
        metadata = await self.get_project_metadata()
        metadata.session_count += 1
        metadata.last_session_date = datetime.now().isoformat()
        await self.save_project_metadata(metadata)
        return metadata.session_count

    async def get_exploration_context(self) -> str:
        """Get previous exploration context from conversation files"""
        exploration_dir = self.project_path / "exploration"
        if not exploration_dir.exists():
            return "No previous exploration sessions found."

        context_parts = []

        # Look for conversation files
        for conv_file in sorted(exploration_dir.glob("conversation-*.md")):
            try:
                content = conv_file.read_text(encoding="utf-8")
                # Extract key insights (simplified)
                if content.strip():
                    context_parts.append(f"From {conv_file.name}:\n{content[:500]}...")
            except Exception:
                continue

        if not context_parts:
            return "No previous conversation content found."

        return "\n\n".join(context_parts)

    async def save_exploration_session(
        self,
        session_number: int,
        conversation_content: str,
        session_summary: str | None = None,
    ) -> str:
        """Save exploration session to file"""
        exploration_dir = self.project_path / "exploration"
        exploration_dir.mkdir(exist_ok=True)

        # Create conversation file
        conversation_file = exploration_dir / f"conversation-{session_number}.md"

        session_content = f"""# Exploration Session {session_number}

**Date:** {datetime.now().isoformat()}
**Project:** {self.project_path.name}

## Session Summary
{session_summary or "No summary provided"}

## Conversation Content

{conversation_content}

---
*Generated by Compass MCP Server*
"""

        conversation_file.write_text(session_content, encoding="utf-8")
        return str(conversation_file)

    async def check_exploration_completion(self) -> dict[str, Any]:
        """Check if exploration phase is complete"""
        try:
            tasks_data = await self.parse_tasks_file()
            completed_tasks = [
                task for task in tasks_data.exploration_tasks if task.completed
            ]
            total_tasks = len(tasks_data.exploration_tasks)
            completion_rate = (
                len(completed_tasks) / total_tasks if total_tasks > 0 else 0
            )

            # Exploration is complete if 80% or more tasks are done
            is_complete = completion_rate >= 0.8 and total_tasks >= 5

            return {
                "is_complete": is_complete,
                "completion_rate": completion_rate,
                "completed_tasks": len(completed_tasks),
                "total_tasks": total_tasks,
                "reason": (
                    "Sufficient exploration depth achieved"
                    if is_complete
                    else "More exploration needed"
                ),
            }
        except Exception:
            return {
                "is_complete": False,
                "completion_rate": 0.0,
                "completed_tasks": 0,
                "total_tasks": 0,
                "reason": "Unable to assess completion",
            }
