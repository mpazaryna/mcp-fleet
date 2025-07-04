"""
Tests for Compass project manager
"""

import shutil
import tempfile
from pathlib import Path

import pytest
from compass.src.managers.project_manager import ProjectManager, ProjectMetadata, Task


@pytest.fixture
def temp_project():
    """Create temporary project for testing"""
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir) / "test_project"
    project_path.mkdir(parents=True)

    yield str(project_path)

    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_project_metadata_creation(temp_project):
    """Test creating and saving project metadata"""
    manager = ProjectManager(temp_project)

    metadata = ProjectMetadata(
        name="Test Project",
        created="2024-01-01T10:00:00",
        current_phase="exploration",
        status="active",
        session_count=0,
    )

    await manager.save_project_metadata(metadata)

    # Verify file was created
    metadata_file = Path(temp_project) / ".compass.json"
    assert metadata_file.exists()

    # Verify content
    loaded_metadata = await manager.get_project_metadata()
    assert loaded_metadata.name == "Test Project"
    assert loaded_metadata.current_phase == "exploration"


@pytest.mark.asyncio
async def test_get_metadata_creates_default(temp_project):
    """Test that get_project_metadata creates default metadata if none exists"""
    manager = ProjectManager(temp_project)

    metadata = await manager.get_project_metadata()

    assert metadata.name == "test_project"  # Based on directory name
    assert metadata.current_phase == "exploration"
    assert metadata.status == "active"
    assert metadata.session_count == 0


@pytest.mark.asyncio
async def test_update_session_count(temp_project):
    """Test updating session count"""
    manager = ProjectManager(temp_project)

    # First update
    count1 = await manager.update_session_count()
    assert count1 == 1

    # Second update
    count2 = await manager.update_session_count()
    assert count2 == 2

    # Verify metadata was updated
    metadata = await manager.get_project_metadata()
    assert metadata.session_count == 2
    assert metadata.last_session_date is not None


@pytest.mark.asyncio
async def test_parse_tasks_file_not_found(temp_project):
    """Test parsing tasks file when it doesn't exist"""
    manager = ProjectManager(temp_project)

    with pytest.raises(FileNotFoundError):
        await manager.parse_tasks_file()


@pytest.mark.asyncio
async def test_update_tasks_file(temp_project):
    """Test updating tasks file"""
    manager = ProjectManager(temp_project)

    tasks = [
        Task(completed=True, text="Understand the problem"),
        Task(completed=False, text="Identify stakeholders"),
        Task(completed=False, text="Define success criteria"),
    ]

    await manager.update_tasks_file(tasks, "Continue exploration")

    # Verify file was created
    tasks_file = Path(temp_project) / "tasks.md"
    assert tasks_file.exists()

    # Verify content
    content = tasks_file.read_text()
    assert "- [x] Understand the problem" in content
    assert "- [ ] Identify stakeholders" in content
    assert "Continue exploration" in content


@pytest.mark.asyncio
async def test_parse_tasks_file(temp_project):
    """Test parsing an existing tasks file"""
    manager = ProjectManager(temp_project)

    # Create a tasks file
    tasks_content = """# Test Project - Compass Project Tasks

## Phase 1: Exploration

### Core Questions & Tasks
- [x] Understand the core problem
- [ ] Identify all stakeholders
- [x] Define success criteria
- [ ] Document constraints

## Phase 2: Specification
(Locked until exploration phase complete)
"""

    tasks_file = Path(temp_project) / "tasks.md"
    tasks_file.write_text(tasks_content)

    # Parse the file
    tasks_data = await manager.parse_tasks_file()

    assert len(tasks_data.exploration_tasks) == 4
    assert tasks_data.exploration_tasks[0].completed
    assert tasks_data.exploration_tasks[0].text == "Understand the core problem"
    assert not tasks_data.exploration_tasks[1].completed
    assert tasks_data.exploration_tasks[1].text == "Identify all stakeholders"


@pytest.mark.asyncio
async def test_save_exploration_session(temp_project):
    """Test saving exploration session"""
    manager = ProjectManager(temp_project)

    conversation = "This is a test conversation about project exploration."
    summary = "Discussed core problem understanding"

    file_path = await manager.save_exploration_session(1, conversation, summary)

    # Verify file was created
    session_file = Path(file_path)
    assert session_file.exists()
    assert session_file.name == "conversation-1.md"

    # Verify content
    content = session_file.read_text()
    assert "Exploration Session 1" in content
    assert conversation in content
    assert summary in content


@pytest.mark.asyncio
async def test_get_exploration_context_no_sessions(temp_project):
    """Test getting exploration context when no sessions exist"""
    manager = ProjectManager(temp_project)

    context = await manager.get_exploration_context()

    assert "No previous exploration sessions found" in context


@pytest.mark.asyncio
async def test_get_exploration_context_with_sessions(temp_project):
    """Test getting exploration context with existing sessions"""
    manager = ProjectManager(temp_project)

    # Create exploration directory and session
    exploration_dir = Path(temp_project) / "exploration"
    exploration_dir.mkdir()

    session_content = "# Session 1\nThis is exploration content..."
    session_file = exploration_dir / "conversation-1.md"
    session_file.write_text(session_content)

    context = await manager.get_exploration_context()

    assert "conversation-1.md" in context
    assert "This is exploration content" in context


@pytest.mark.asyncio
async def test_check_exploration_completion(temp_project):
    """Test checking exploration completion status"""
    manager = ProjectManager(temp_project)

    # Create tasks file with partial completion
    tasks = [
        Task(completed=True, text="Task 1"),
        Task(completed=True, text="Task 2"),
        Task(completed=True, text="Task 3"),
        Task(completed=True, text="Task 4"),
        Task(completed=False, text="Task 5"),  # 80% complete
    ]

    await manager.update_tasks_file(tasks)

    completion_status = await manager.check_exploration_completion()

    assert completion_status["is_complete"]  # 80% >= 80% threshold
    assert completion_status["completion_rate"] == 0.8
    assert completion_status["completed_tasks"] == 4
    assert completion_status["total_tasks"] == 5


@pytest.mark.asyncio
async def test_check_exploration_completion_insufficient(temp_project):
    """Test exploration completion when insufficient tasks completed"""
    manager = ProjectManager(temp_project)

    # Create tasks file with low completion
    tasks = [
        Task(completed=True, text="Task 1"),
        Task(completed=False, text="Task 2"),
        Task(completed=False, text="Task 3"),
        Task(completed=False, text="Task 4"),
        Task(completed=False, text="Task 5"),  # Only 20% complete
    ]

    await manager.update_tasks_file(tasks)

    completion_status = await manager.check_exploration_completion()

    assert not completion_status["is_complete"]
    assert completion_status["completion_rate"] == 0.2
    assert completion_status["completed_tasks"] == 1
    assert completion_status["total_tasks"] == 5
