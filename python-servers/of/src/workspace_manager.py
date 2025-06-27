"""
Workspace manager for OF (Orchestration Framework) server
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ProjectData(BaseModel):
    """Project data structure for OF"""
    id: str
    name: str
    phase: str  # exploration, specification, execution, feedback
    status: str  # active, paused, completed
    created_at: str
    last_updated: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}


class WorkspaceManager:
    """Manages OF workspace structure and project files"""
    
    def __init__(self, workspace_path: str = None):
        # Use environment variable or default
        self.workspace_path = Path(workspace_path or os.getenv("OF_WORKSPACE", "./workspace"))
        self.workspace_path.mkdir(parents=True, exist_ok=True)
    
    async def create_project(self, name: str, description: str = None) -> ProjectData:
        """Create a new project in the workspace"""
        # Generate project ID
        timestamp = int(datetime.now().timestamp())
        project_id = f"of_{timestamp}_{hash(name) % 10000}"
        
        # Create project directory structure
        project_dir = self.workspace_path / name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create phase directories
        for phase in ["exploration", "specification", "execution", "feedback"]:
            (project_dir / phase).mkdir(exist_ok=True)
        
        # Create templates directory
        (project_dir / "templates").mkdir(exist_ok=True)
        
        # Create project metadata
        project_data = ProjectData(
            id=project_id,
            name=name,
            phase="exploration",
            status="active",
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            description=description
        )
        
        # Save project metadata
        metadata_file = project_dir / "project.json"
        with open(metadata_file, 'w') as f:
            json.dump(project_data.model_dump(), f, indent=2)
        
        # Create initial README
        readme_file = project_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(f"# {name}\n\n")
            if description:
                f.write(f"{description}\n\n")
            f.write("## 4-Phase Systematic Methodology\n\n")
            f.write("- **Exploration**: Understanding the problem space\n")
            f.write("- **Specification**: Defining requirements and approach\n")
            f.write("- **Execution**: Implementation and development\n")
            f.write("- **Feedback**: Review, iteration, and improvement\n\n")
            f.write(f"**Current Phase**: {project_data.phase}\n")
            f.write(f"**Status**: {project_data.status}\n")
            f.write(f"**Created**: {project_data.created_at}\n")
        
        return project_data
    
    async def list_projects(self) -> List[ProjectData]:
        """List all projects in the workspace"""
        projects = []
        
        if not self.workspace_path.exists():
            return projects
        
        for project_dir in self.workspace_path.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / "project.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            data = json.load(f)
                        projects.append(ProjectData(**data))
                    except Exception as e:
                        # Skip invalid project files
                        continue
        
        return sorted(projects, key=lambda p: p.created_at, reverse=True)
    
    async def get_project(self, name: str) -> Optional[ProjectData]:
        """Get a specific project by name"""
        project_dir = self.workspace_path / name
        metadata_file = project_dir / "project.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            return ProjectData(**data)
        except Exception:
            return None
    
    async def update_project_phase(self, name: str, phase: str) -> Optional[ProjectData]:
        """Update project phase"""
        project_data = await self.get_project(name)
        if not project_data:
            return None
        
        project_data.phase = phase
        project_data.last_updated = datetime.now().isoformat()
        
        # Save updated metadata
        project_dir = self.workspace_path / name
        metadata_file = project_dir / "project.json"
        with open(metadata_file, 'w') as f:
            json.dump(project_data.model_dump(), f, indent=2)
        
        return project_data
    
    async def save_session_notes(self, project_name: str, phase: str, content: str, session_type: str = "notes") -> str:
        """Save session notes to the appropriate phase directory"""
        project_dir = self.workspace_path / project_name
        phase_dir = project_dir / phase
        
        if not phase_dir.exists():
            phase_dir.mkdir(parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{session_type}_{timestamp}.md"
        file_path = phase_dir / filename
        
        with open(file_path, 'w') as f:
            f.write(f"# {session_type.title()} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(content)
        
        return str(file_path)