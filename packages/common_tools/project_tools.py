"""
Project discovery and management tools
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from mcp_core.types import MCPTool


# Schema definitions
class ProjectMetadata(BaseModel):
    """Project metadata"""
    name: str
    type: str
    config_files: List[str]
    metadata: Optional[Dict[str, Any]] = None


class FindProjectsInputSchema(BaseModel):
    """Schema for find projects input"""
    root_directory: Optional[str] = Field(default=".", description="Root directory to search for projects")
    project_type: Optional[str] = Field(default=None, description="Type of projects to find")


class FindProjectsOutputSchema(BaseModel):
    """Schema for find projects output"""
    projects: List[ProjectMetadata]
    total: int


class GetProjectInfoInputSchema(BaseModel):
    """Schema for get project info input"""
    project_path: str = Field(description="Path to the project")


class GetProjectInfoOutputSchema(BaseModel):
    """Schema for get project info output"""
    name: str
    path: str
    type: str
    config_files: List[str]
    metadata: Optional[Dict[str, Any]] = None


class CreateProjectInputSchema(BaseModel):
    """Schema for create project input"""
    name: str = Field(description="Project name")
    path: str = Field(description="Project path")
    project_type: Optional[str] = Field(default="basic", description="Project type")


class CreateProjectOutputSchema(BaseModel):
    """Schema for create project output"""
    success: bool
    name: str
    path: str


# Tool definitions
project_tools: List[MCPTool] = [
    MCPTool(
        name="find_projects",
        description="Find projects in a directory",
        input_schema=FindProjectsInputSchema.model_json_schema(),
        output_schema=FindProjectsOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="get_project_info",
        description="Get information about a specific project",
        input_schema=GetProjectInfoInputSchema.model_json_schema(),
        output_schema=GetProjectInfoOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="create_project",
        description="Create a new project",
        input_schema=CreateProjectInputSchema.model_json_schema(),
        output_schema=CreateProjectOutputSchema.model_json_schema(),
    ),
]


# Helper functions
def detect_project_type(path: Path) -> tuple[str, List[str]]:
    """Detect project type based on config files"""
    config_files = []
    project_type = "unknown"
    
    # Check for common project files
    if (path / "package.json").exists():
        config_files.append("package.json")
        project_type = "nodejs"
    
    if (path / "deno.json").exists():
        config_files.append("deno.json")
        project_type = "deno"
    
    if (path / "pyproject.toml").exists():
        config_files.append("pyproject.toml")
        project_type = "python"
    
    if (path / "Cargo.toml").exists():
        config_files.append("Cargo.toml")
        project_type = "rust"
    
    if (path / ".orchestration.json").exists():
        config_files.append(".orchestration.json")
        project_type = "orchestration"
    
    return project_type, config_files


# Tool handlers
async def find_projects_handler(args: dict) -> dict:
    """Find projects handler"""
    validated_args = FindProjectsInputSchema(**args)
    root_path = Path(validated_args.root_directory)
    
    try:
        projects = []
        
        # Search for projects recursively
        for item in root_path.rglob("*"):
            if item.is_dir():
                project_type, config_files = detect_project_type(item)
                
                # Filter by project type if specified
                if validated_args.project_type and project_type != validated_args.project_type:
                    continue
                
                if config_files:  # Only include if we found config files
                    metadata = None
                    
                    # Try to extract metadata from config files
                    if "package.json" in config_files:
                        try:
                            with open(item / "package.json") as f:
                                pkg_data = json.load(f)
                                metadata = {
                                    "name": pkg_data.get("name"),
                                    "version": pkg_data.get("version"),
                                    "description": pkg_data.get("description")
                                }
                        except:
                            pass
                    
                    projects.append(ProjectMetadata(
                        name=item.name,
                        type=project_type,
                        config_files=config_files,
                        metadata=metadata
                    ))
        
        return FindProjectsOutputSchema(
            projects=projects,
            total=len(projects)
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to find projects in {root_path}: {str(error)}")


async def get_project_info_handler(args: dict) -> dict:
    """Get project info handler"""
    validated_args = GetProjectInfoInputSchema(**args)
    project_path = Path(validated_args.project_path)
    
    try:
        if not project_path.exists():
            raise Exception(f"Project path {project_path} does not exist")
        
        project_type, config_files = detect_project_type(project_path)
        
        metadata = None
        if "package.json" in config_files:
            try:
                with open(project_path / "package.json") as f:
                    pkg_data = json.load(f)
                    metadata = {
                        "name": pkg_data.get("name"),
                        "version": pkg_data.get("version"),
                        "description": pkg_data.get("description")
                    }
            except:
                pass
        
        return GetProjectInfoOutputSchema(
            name=project_path.name,
            path=str(project_path),
            type=project_type,
            config_files=config_files,
            metadata=metadata
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to get project info for {project_path}: {str(error)}")


async def create_project_handler(args: dict) -> dict:
    """Create project handler"""
    validated_args = CreateProjectInputSchema(**args)
    project_path = Path(validated_args.path)
    
    try:
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create basic project structure based on type
        if validated_args.project_type == "python":
            # Create basic Python project structure
            (project_path / "src").mkdir(exist_ok=True)
            (project_path / "tests").mkdir(exist_ok=True)
            
            # Create pyproject.toml
            pyproject_content = f"""[project]
name = "{validated_args.name}"
version = "0.1.0"
description = ""
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
            with open(project_path / "pyproject.toml", "w") as f:
                f.write(pyproject_content)
        
        return CreateProjectOutputSchema(
            success=True,
            name=validated_args.name,
            path=str(project_path)
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to create project {validated_args.name}: {str(error)}")


# Handler mapping
project_handlers = {
    "find_projects": find_projects_handler,
    "get_project_info": get_project_info_handler,
    "create_project": create_project_handler,
}