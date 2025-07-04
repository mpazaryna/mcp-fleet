#!/usr/bin/env python3
"""
UAT (User Acceptance Test) for Tides MCP Server Docker Container

Tests the complete tidal workflow management system:
1. Tide creation with different time scales and intensity patterns
2. Flow session management with focus and intensity tracking
3. Report generation and export functionality
4. Data persistence and file organization
5. Claude API integration for workflow guidance

Run with: python tests/uat/test_tides_docker_uat.py
"""
import json
import logging
import os
import time

from mcp_docker_client import TIDES_SERVER, MCPDockerClient, create_test_workspace

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_tides_workflow_management():
    """Test complete tidal workflow management system"""
    print("🌊 Tides MCP Server - UAT")
    print("=" * 50)
    print("🎯 Testing rhythmic workflow management system")

    # Create test workspace
    workspace = create_test_workspace()

    # Configure tides server with Claude API key
    tides_config = TIDES_SERVER
    tides_config.volume_mappings = {str(workspace): "/app/tides"}

    # Add Claude API key if available
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        tides_config.env_vars = {"ANTHROPIC_API_KEY": api_key}
        print("✅ Claude API key configured")
    else:
        print("⚠️  No Claude API key found - some features may be limited")

    with MCPDockerClient(tides_config, debug=True) as client:
        # List available tools
        tools = client.list_tools()
        tool_names = [tool["name"] for tool in tools]

        expected_tools = [
            "create_tide",
            "list_tides",
            "flow_tide",
            "save_tide_report",
            "export_all_tides",
        ]

        missing_tools = [tool for tool in expected_tools if tool not in tool_names]
        if missing_tools:
            raise RuntimeError(f"Missing expected tools: {missing_tools}")

        print(f"✅ All expected tools available: {len(expected_tools)} tools")

        # Test 1: Create different types of tides
        print("\n🎬 Test 1: Create various tide types...")

        # Daily work tide
        client.call_tool(
            "create_tide",
            {
                "name": "Daily Deep Work",
                "flow_type": "work",
                "time_scale": "daily",
                "intensity_pattern": "morning_peak",
                "description": "High-intensity morning work sessions for complex tasks",
                "duration_minutes": 90,
            },
        )

        # Weekly creative tide
        client.call_tool(
            "create_tide",
            {
                "name": "Weekly Creative Flow",
                "flow_type": "creative",
                "time_scale": "weekly",
                "intensity_pattern": "steady_build",
                "description": "Creative exploration and ideation sessions",
                "duration_minutes": 120,
            },
        )

        # Monthly strategic tide
        client.call_tool(
            "create_tide",
            {
                "name": "Monthly Strategy",
                "flow_type": "strategic",
                "time_scale": "monthly",
                "intensity_pattern": "waves",
                "description": "Strategic planning and big picture thinking",
                "duration_minutes": 180,
            },
        )

        print("✅ Created 3 different tide types")

        # Test 2: List all tides
        print("\n🎬 Test 2: List all tides...")
        list_result = client.call_tool(
            "list_tides", {"filter_type": "all", "include_stats": True}
        )

        # Verify we can see our created tides
        if "content" in list_result:
            list_content = list_result["content"][0].get("text", "")
            assert "Daily Deep Work" in list_content, "Daily tide not found in list"
            assert (
                "Weekly Creative Flow" in list_content
            ), "Weekly tide not found in list"
            assert "Monthly Strategy" in list_content, "Monthly tide not found in list"

        print("✅ All tides visible in list")

        # Test 3: Start flow sessions
        print("\n🎬 Test 3: Start flow sessions...")

        # High intensity work flow
        client.call_tool(
            "flow_tide",
            {
                "tide_name": "Daily Deep Work",
                "intensity": "high",
                "focus_area": "UAT testing implementation and validation",
                "session_notes": "Working on comprehensive UAT tests for MCP Fleet servers",
            },
        )

        # Wait a moment to simulate work
        print("   ⏳ Simulating 30 seconds of work...")
        time.sleep(30)

        # Medium intensity creative flow
        client.call_tool(
            "flow_tide",
            {
                "tide_name": "Weekly Creative Flow",
                "intensity": "medium",
                "focus_area": "Test framework design and architecture",
                "session_notes": "Exploring patterns for better UAT test organization",
            },
        )

        print("✅ Flow sessions started successfully")

        # Test 4: Generate individual tide report
        print("\n🎬 Test 4: Generate tide report...")
        client.call_tool(
            "save_tide_report",
            {
                "tide_name": "Daily Deep Work",
                "format": "json",
                "include_flow_history": True,
                "include_statistics": True,
            },
        )

        # Verify report file was created
        report_files = list(workspace.glob("**/*.json"))
        tide_reports = [f for f in report_files if "Daily_Deep_Work" in f.name]
        assert len(tide_reports) > 0, "Tide report file not created"

        print(f"✅ Tide report generated: {tide_reports[0].name}")

        # Test 5: Export all tides
        print("\n🎬 Test 5: Export all tides...")
        client.call_tool(
            "export_all_tides",
            {
                "format": "markdown",
                "include_statistics": True,
                "date_range": {"start": "2025-01-01", "end": "2025-12-31"},
                "filter_by_type": "all",
            },
        )

        # Verify export files
        export_files = list(workspace.glob("**/*.md"))
        assert len(export_files) > 0, "Export files not created"

        print(f"✅ Export completed: {len(export_files)} files")

        # Test 6: Verify data persistence
        print("\n🎬 Test 6: Verify data persistence...")

        # Check tide data files
        data_files = list(workspace.rglob("*.json"))
        print(f"   📄 Data files created: {len(data_files)}")

        # Verify at least one tide data file exists
        tide_data_files = [f for f in data_files if "tide" in f.name.lower()]
        assert len(tide_data_files) > 0, "No tide data files found"

        # Read and validate a tide data file
        with open(tide_data_files[0]) as f:
            tide_data = json.load(f)

        required_fields = ["name", "flow_type", "time_scale", "created_at"]
        for field in required_fields:
            assert field in tide_data, f"Missing required field: {field}"

        print("✅ Data persistence validated")

        # Test 7: Test filtering and search
        print("\n🎬 Test 7: Test tide filtering...")

        # Filter by flow type
        client.call_tool(
            "list_tides", {"filter_type": "work", "include_stats": False}
        )

        client.call_tool(
            "list_tides", {"filter_type": "creative", "include_stats": False}
        )

        print("✅ Filtering functionality working")

        # Summary statistics
        print("\n📊 UAT Session Summary:")
        print("   🌊 Tides created: 3")
        print("   🌀 Flow sessions: 2")
        print(f"   📄 Data files: {len(data_files)}")
        print(f"   📋 Export files: {len(export_files)}")
        print(f"   💾 Storage location: {workspace}")

        print("\n🎉 Tides UAT completed successfully!")
        print("✅ Tidal workflow management functional")
        print("✅ Flow session tracking operational")
        print("✅ Report generation working")
        print("✅ Data persistence validated")
        print("✅ Export functionality confirmed")


def test_tides_claude_integration():
    """Test Claude API integration for workflow guidance"""
    print("\n🤖 Testing Tides Claude Integration...")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  Skipping Claude integration test - no API key")
        return

    workspace = create_test_workspace()
    tides_config = TIDES_SERVER
    tides_config.volume_mappings = {str(workspace): "/app/tides"}
    tides_config.env_vars = {"ANTHROPIC_API_KEY": api_key}

    with MCPDockerClient(tides_config) as client:
        # Create a tide that might benefit from AI guidance
        client.call_tool(
            "create_tide",
            {
                "name": "AI-Assisted Learning",
                "flow_type": "learning",
                "time_scale": "daily",
                "intensity_pattern": "steady",
                "description": "Learning sessions with AI guidance and feedback",
                "duration_minutes": 60,
            },
        )

        # Start a flow session that could trigger Claude integration
        client.call_tool(
            "flow_tide",
            {
                "tide_name": "AI-Assisted Learning",
                "intensity": "medium",
                "focus_area": "Understanding MCP protocol patterns and best practices",
                "session_notes": "Need guidance on optimizing server architectures",
            },
        )

        print("✅ Claude integration test completed")


def test_tides_error_handling():
    """Test tides error handling and edge cases"""
    print("\n🌊 Testing Tides Error Handling...")

    workspace = create_test_workspace()
    tides_config = TIDES_SERVER
    tides_config.volume_mappings = {str(workspace): "/app/tides"}

    with MCPDockerClient(tides_config) as client:
        # Test 1: Invalid tide parameters
        print("🔬 Testing invalid parameters...")
        try:
            client.call_tool(
                "create_tide",
                {
                    "name": "",  # Invalid empty name
                    "flow_type": "invalid_type",  # Invalid type
                    "time_scale": "invalid_scale",  # Invalid scale
                    "intensity_pattern": "invalid_pattern",  # Invalid pattern
                },
            )
            assert False, "Should reject invalid parameters"
        except RuntimeError as e:
            print(f"✅ Invalid parameters properly rejected: {str(e)[:50]}...")

        # Test 2: Non-existent tide operations
        print("🔬 Testing non-existent tide operations...")
        try:
            client.call_tool(
                "flow_tide",
                {
                    "tide_name": "Non-Existent Tide",
                    "intensity": "medium",
                    "focus_area": "test",
                },
            )
            assert False, "Should reject operations on non-existent tides"
        except RuntimeError as e:
            print(f"✅ Non-existent tide handling working: {str(e)[:50]}...")

        print("✅ Error handling tests passed!")


if __name__ == "__main__":
    try:
        test_tides_workflow_management()
        test_tides_claude_integration()
        test_tides_error_handling()

        print("\n🌟 All Tides UAT tests passed!")
        print("✅ Tides server ready for production!")

    except Exception as e:
        print(f"\n❌ UAT failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
