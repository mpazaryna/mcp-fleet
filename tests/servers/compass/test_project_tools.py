"""
Tests for Compass project tools
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from compass.src.tools.project_tools import (
    init_project_handler, list_projects_handler, get_project_status_handler
)


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_init_project_handler_success(temp_workspace):
    """Test successful project initialization"""
    args = {
        "name": "test-project",
        "projects_dir": temp_workspace
    }
    
    result = await init_project_handler(args)
    
    assert result["success"] == True
    assert result["project_name"] == "test-project"
    assert "test-project" in result["project_path"]
    assert len(result["next_steps"]) > 0
    
    # Verify project structure was created
    project_path = Path(temp_workspace) / "test-project"
    assert project_path.exists()
    assert (project_path / "exploration").exists()
    assert (project_path / "specification").exists()
    assert (project_path / "execution").exists()
    assert (project_path / "feedback").exists()
    assert (project_path / ".compass.json").exists()
    assert (project_path / "tasks.md").exists()
    assert (project_path / "exploration" / "questions.md").exists()


@pytest.mark.asyncio
async def test_init_project_handler_already_exists(temp_workspace):
    """Test initializing project that already exists"""
    # Create project first
    project_path = Path(temp_workspace) / "existing-project"
    project_path.mkdir(parents=True)
    
    args = {
        "name": "existing-project",
        "projects_dir": temp_workspace
    }
    
    result = await init_project_handler(args)
    
    assert result["success"] == False
    assert "already exists" in result["message"]


@pytest.mark.asyncio
async def test_list_projects_handler_empty(temp_workspace):
    """Test listing projects when none exist"""
    args = {"projects_dir": temp_workspace}
    
    result = await list_projects_handler(args)
    
    assert result["total"] == 0
    assert len(result["projects"]) == 0


@pytest.mark.asyncio
async def test_list_projects_handler_with_projects(temp_workspace):
    """Test listing projects with existing projects"""
    # Create a test project first
    await init_project_handler({
        "name": "project1",
        "projects_dir": temp_workspace
    })
    
    await init_project_handler({
        "name": "project2", 
        "projects_dir": temp_workspace
    })
    
    args = {"projects_dir": temp_workspace}
    
    result = await list_projects_handler(args)
    
    assert result["total"] == 2
    assert len(result["projects"]) == 2
    
    # Projects should be sorted by creation date
    project_names = [p["name"] for p in result["projects"]]
    assert "project1" in project_names
    assert "project2" in project_names


@pytest.mark.asyncio
async def test_get_project_status_handler_not_found(temp_workspace):
    """Test getting status of non-existent project"""
    args = {
        "project_name": "nonexistent",
        "projects_dir": temp_workspace
    }
    
    result = await get_project_status_handler(args)
    
    assert result["current_phase"] == "unknown"
    assert "not found" in result["status_summary"]
    assert "Initialize project first" in result["next_action"]


@pytest.mark.asyncio
async def test_get_project_status_handler_new_project(temp_workspace):
    """Test getting status of newly created project"""
    # Create project first
    await init_project_handler({
        "name": "new-project",
        "projects_dir": temp_workspace
    })
    
    args = {
        "project_name": "new-project",
        "projects_dir": temp_workspace
    }
    
    result = await get_project_status_handler(args)
    
    assert result["project_name"] == "new-project"
    assert result["current_phase"] == "exploration"
    assert "not started" in result["status_summary"]
    assert "Start exploration session" in result["next_action"]
    assert len(result["recommendations"]) > 0


@pytest.mark.asyncio 
async def test_get_project_status_handler_with_tasks(temp_workspace):
    """Test getting status of project with exploration tasks"""
    # Create project first
    await init_project_handler({
        "name": "active-project",
        "projects_dir": temp_workspace
    })
    
    # Create tasks file with some completed tasks
    project_path = Path(temp_workspace) / "active-project"
    tasks_content = """# Active Project

## Phase 1: Exploration

- [x] Understand the problem
- [x] Identify stakeholders  
- [ ] Define success criteria
- [ ] Document constraints
- [ ] Analyze existing solutions
"""
    
    tasks_file = project_path / "tasks.md"
    tasks_file.write_text(tasks_content)
    
    args = {
        "project_name": "active-project",
        "projects_dir": temp_workspace
    }
    
    result = await get_project_status_handler(args)
    
    assert result["current_phase"] == "exploration"
    assert "in progress" in result["status_summary"]
    assert len(result["exploration_tasks"]) == 5
    assert result["exploration_tasks"][0]["completed"] == True
    assert result["exploration_tasks"][0]["text"] == "Understand the problem"
    assert "Continue exploration" in result["next_action"]


@pytest.mark.asyncio
async def test_init_project_creates_proper_structure(temp_workspace):
    """Test that init_project creates all necessary files and directories"""
    args = {
        "name": "complete-project",
        "projects_dir": temp_workspace
    }
    
    result = await init_project_handler(args)
    
    project_path = Path(temp_workspace) / "complete-project"
    
    # Check all directories exist
    assert (project_path / "exploration").is_dir()
    assert (project_path / "specification").is_dir()
    assert (project_path / "execution").is_dir()
    assert (project_path / "feedback").is_dir()
    
    # Check key files exist
    assert (project_path / ".compass.json").is_file()
    assert (project_path / "tasks.md").is_file()
    assert (project_path / "exploration" / "questions.md").is_file()
    
    # Check questions.md has proper content
    questions_content = (project_path / "exploration" / "questions.md").read_text()
    assert "Core Understanding Questions" in questions_content
    assert "fundamental problem" in questions_content
    assert "stakeholders" in questions_content
    
    # Check tasks.md has proper content
    tasks_content = (project_path / "tasks.md").read_text()
    assert "Compass Project Tasks" in tasks_content
    assert "Phase 1: Exploration" in tasks_content
    assert "Phase 2: Specification" in tasks_content