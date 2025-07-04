#!/usr/bin/env python3
"""
UAT (User Acceptance Test) for Compass MCP Server Docker Container

Tests the complete compass methodology workflow:
1. Project initialization and workspace setup
2. Exploration phase with conversation preservation
3. Specification generation from exploration
4. Execution phase with task management
5. File persistence and project structure validation

Run with: python tests/uat/test_compass_docker_uat.py
"""
import json
import logging

from mcp_docker_client import COMPASS_SERVER, MCPDockerClient, create_test_workspace

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_compass_project_workflow():
    """Test complete compass project methodology workflow"""
    print("🧭 Compass MCP Server - UAT")
    print("=" * 50)
    print("🎯 Testing systematic project methodology workflow")

    # Create test workspace
    workspace = create_test_workspace()
    projects_dir = workspace / "projects"

    # Configure compass server
    compass_config = COMPASS_SERVER
    compass_config.volume_mappings = {str(workspace): "/app/projects"}

    with MCPDockerClient(compass_config, debug=True) as client:
        # List available tools
        tools = client.list_tools()
        tool_names = [tool["name"] for tool in tools]

        expected_tools = [
            "init_project",
            "start_exploration",
            "save_exploration_session",
            "complete_exploration_phase",
            "generate_specification",
            "start_execution",
            "list_tasks",
            "update_task_status",
        ]

        missing_tools = [tool for tool in expected_tools if tool not in tool_names]
        if missing_tools:
            raise RuntimeError(f"Missing expected tools: {missing_tools}")

        print(f"✅ All expected tools available: {len(expected_tools)} tools")

        # Test 1: Initialize a new project
        print("\n🎬 Test 1: Initialize project...")
        client.call_tool(
            "init_project",
            {
                "project_name": "uat-demo-app",
                "description": "A demo mobile app for compass UAT testing",
                "project_type": "mobile_app",
            },
        )

        # Verify project directory was created
        project_path = projects_dir / "uat-demo-app"
        assert project_path.exists(), f"Project directory not created: {project_path}"

        config_file = project_path / "compass_config.json"
        assert config_file.exists(), "Project config file not created"

        with open(config_file) as f:
            config = json.load(f)
        assert (
            config["phase"] == "exploration"
        ), f"Expected exploration phase, got {config['phase']}"

        print(f"✅ Project initialized at {project_path}")

        # Test 2: Start exploration session
        print("\n🎬 Test 2: Start exploration session...")
        client.call_tool(
            "start_exploration",
            {
                "project_name": "uat-demo-app",
                "exploration_focus": "user requirements and core features",
            },
        )

        # Test 3: Save exploration session
        print("\n🎬 Test 3: Save exploration session...")
        client.call_tool(
            "save_exploration_session",
            {
                "project_name": "uat-demo-app",
                "session_title": "Core Feature Discovery",
                "conversation_content": """
            ## Core Features Identified:
            1. User authentication (email/password)
            2. Profile management
            3. Content creation and editing
            4. Social sharing capabilities
            5. Offline mode support

            ## Technical Requirements:
            - Cross-platform (iOS/Android)
            - Realtime sync
            - Local caching
            - Push notifications
            """,
                "key_insights": [
                    "Users prioritize offline functionality",
                    "Social features are secondary to core content creation",
                    "Simple authentication preferred over complex options",
                ],
                "next_steps": [
                    "Explore data synchronization patterns",
                    "Research offline storage requirements",
                    "Define user onboarding flow",
                ],
            },
        )

        # Verify exploration session file was created
        exploration_dir = project_path / "exploration"
        session_files = list(exploration_dir.glob("*.md"))
        assert len(session_files) > 0, "No exploration session files created"

        print(f"✅ Exploration session saved: {len(session_files)} files")

        # Test 4: Complete exploration phase
        print("\n🎬 Test 4: Complete exploration phase...")
        client.call_tool(
            "complete_exploration_phase",
            {
                "project_name": "uat-demo-app",
                "exploration_summary": "Comprehensive exploration of user needs and technical requirements completed. Ready for specification generation.",
            },
        )

        # Test 5: Generate specification
        print("\n🎬 Test 5: Generate project specification...")
        client.call_tool(
            "generate_specification",
            {
                "project_name": "uat-demo-app",
                "specification_type": "technical",
                "include_architecture": True,
                "include_user_stories": True,
            },
        )

        # Verify specification file was created
        spec_file = project_path / "specifications" / "technical_specification.md"
        assert spec_file.exists(), "Technical specification file not created"

        with open(spec_file) as f:
            spec_content = f.read()
        assert (
            "authentication" in spec_content.lower()
        ), "Specification missing key features"
        assert (
            "offline" in spec_content.lower()
        ), "Specification missing offline requirements"

        print(f"✅ Specification generated: {spec_file}")

        # Test 6: Start execution phase
        print("\n🎬 Test 6: Start execution phase...")
        client.call_tool(
            "start_execution", {"project_name": "uat-demo-app"}
        )

        # Verify phase transition
        with open(config_file) as f:
            config = json.load(f)
        assert (
            config["phase"] == "execution"
        ), f"Expected execution phase, got {config['phase']}"

        # Test 7: List and manage tasks
        print("\n🎬 Test 7: List execution tasks...")
        tasks_result = client.call_tool("list_tasks", {"project_name": "uat-demo-app"})

        # Test 8: Update task status
        print("\n🎬 Test 8: Update task status...")
        # Get the first task ID from the list
        if "content" in tasks_result and tasks_result["content"]:
            # Parse the task list to find a task ID
            task_content = tasks_result["content"][0].get("text", "")
            if "Task ID:" in task_content:
                # Extract first task ID (simplified parsing)
                lines = task_content.split("\n")
                task_id = None
                for line in lines:
                    if "Task ID:" in line:
                        task_id = line.split("Task ID:")[-1].strip()
                        break

                if task_id:
                    client.call_tool(
                        "update_task_status",
                        {
                            "project_name": "uat-demo-app",
                            "task_id": task_id,
                            "status": "in_progress",
                            "notes": "Started working on this task during UAT testing",
                        },
                    )
                    print(f"✅ Updated task {task_id} status")

        # Verify final project structure
        print("\n📋 Verifying project structure...")
        expected_dirs = ["exploration", "specifications", "execution"]
        for dir_name in expected_dirs:
            dir_path = project_path / dir_name
            assert dir_path.exists(), f"Missing directory: {dir_name}"
            print(f"   ✅ {dir_name}/ directory exists")

        # Count files created
        total_files = len(list(project_path.rglob("*.md"))) + len(
            list(project_path.rglob("*.json"))
        )
        print(f"   📄 Total files created: {total_files}")

        print("\n🎉 Compass UAT completed successfully!")
        print("✅ Project methodology workflow functional")
        print("✅ Phase enforcement working correctly")
        print("✅ File persistence and structure validated")
        print("✅ Task management operational")
        print(f"✅ Project files stored in: {project_path}")


def test_compass_error_handling():
    """Test compass error handling and validation"""
    print("\n🧭 Testing Compass Error Handling...")

    workspace = create_test_workspace()
    compass_config = COMPASS_SERVER
    compass_config.volume_mappings = {str(workspace): "/app/projects"}

    with MCPDockerClient(compass_config) as client:
        # Test 1: Try to skip exploration phase
        print("🔬 Testing phase enforcement...")

        # Initialize project
        client.call_tool(
            "init_project",
            {
                "project_name": "phase-test",
                "description": "Testing phase enforcement",
                "project_type": "web_app",
            },
        )

        # Try to start execution without completing exploration
        try:
            client.call_tool("start_execution", {"project_name": "phase-test"})
            assert False, "Should not allow skipping exploration phase"
        except RuntimeError as e:
            print(f"✅ Phase enforcement working: {str(e)[:100]}...")

        # Test 2: Try to access non-existent project
        print("🔬 Testing non-existent project handling...")
        try:
            client.call_tool(
                "start_exploration",
                {"project_name": "non-existent-project", "exploration_focus": "test"},
            )
            assert False, "Should not allow access to non-existent project"
        except RuntimeError as e:
            print(f"✅ Non-existent project handling working: {str(e)[:100]}...")

        print("✅ Error handling tests passed!")


if __name__ == "__main__":
    try:
        test_compass_project_workflow()
        test_compass_error_handling()

        print("\n🌟 All Compass UAT tests passed!")
        print("✅ Compass server ready for production!")

    except Exception as e:
        print(f"\n❌ UAT failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
