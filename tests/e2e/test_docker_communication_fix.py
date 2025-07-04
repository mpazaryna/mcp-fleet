"""
Test to demonstrate the correct way to communicate with Docker container
"""

import json
import subprocess
import tempfile
import time
from pathlib import Path


class TestDockerCommunicationFix:
    """Test the correct Docker communication pattern"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_interactive_docker_communication(self):
        """Test interactive Docker communication that mimics the E2E client"""
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "-i",
            "-v",
            f"{self.storage_path}:/app/memories",
            "pazland/mcp-fleet-memry:latest",
        ]

        print("🔍 Starting interactive Docker communication...")

        try:
            process = subprocess.Popen(
                docker_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,  # Unbuffered
            )

            # Wait for container to start (like E2E client does)
            time.sleep(2)

            # Step 1: Initialize
            init_request = '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}'
            print(f"Sending: {init_request}")
            process.stdin.write(init_request + "\n")
            process.stdin.flush()

            # Read initialize response
            init_response = process.stdout.readline()
            print(f"Received: {init_response.strip()}")
            assert '"result"' in init_response

            # Step 2: Send initialized notification
            init_notification = (
                '{"jsonrpc": "2.0", "method": "notifications/initialized"}'
            )
            print(f"Sending: {init_notification}")
            process.stdin.write(init_notification + "\n")
            process.stdin.flush()

            # Step 3: Call tool
            tool_request = '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "create_memory", "arguments": {"title": "Interactive Test", "content": "This uses proper interactive communication", "source": "interactive", "tags": ["interactive", "working"]}}}'
            print(f"Sending: {tool_request}")
            process.stdin.write(tool_request + "\n")
            process.stdin.flush()

            # Read tool response
            tool_response = process.stdout.readline()
            print(f"Received: {tool_response.strip()}")

            # Parse and verify response
            response_data = json.loads(tool_response)
            assert response_data.get("id") == 2
            assert "result" in response_data

            structured_content = response_data["result"].get("structuredContent", {})
            assert structured_content.get("success")

            print("✅ Interactive Docker communication works!")

            # Verify file was created
            json_files = list(self.storage_path.glob("*.json"))
            assert len(json_files) == 1
            print(f"✅ File created: {json_files[0].name}")

            # Clean up
            process.stdin.close()
            process.terminate()
            process.wait()

        except Exception as e:
            print(f"❌ Interactive communication failed: {e}")
            if "process" in locals():
                process.kill()
                process.wait()
            raise

    def test_create_working_docker_command_function(self):
        """Create a reusable function for working Docker commands"""

        def run_memry_tool(tool_name, arguments, storage_path):
            """
            Run a memry tool via Docker using the correct communication pattern
            Returns the tool result or raises an exception
            """
            docker_cmd = [
                "docker",
                "run",
                "--rm",
                "-i",
                "-v",
                f"{storage_path}:/app/memories",
                "pazland/mcp-fleet-memry:latest",
            ]

            process = subprocess.Popen(
                docker_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
            )

            try:
                # Wait for startup
                time.sleep(2)

                # Initialize
                init_request = '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}'
                process.stdin.write(init_request + "\n")
                process.stdin.flush()
                process.stdout.readline()

                # Send initialized notification
                init_notification = (
                    '{"jsonrpc": "2.0", "method": "notifications/initialized"}'
                )
                process.stdin.write(init_notification + "\n")
                process.stdin.flush()

                # Call tool
                tool_request = json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {"name": tool_name, "arguments": arguments},
                    }
                )
                process.stdin.write(tool_request + "\n")
                process.stdin.flush()

                # Read response
                tool_response = process.stdout.readline()
                response_data = json.loads(tool_response)

                return response_data["result"]

            finally:
                process.stdin.close()
                process.terminate()
                process.wait()

        # Test the function
        result = run_memry_tool(
            "create_memory",
            {
                "title": "Function Test",
                "content": "Testing the reusable function",
                "source": "function-test",
                "tags": ["function", "reusable"],
            },
            str(self.storage_path),
        )

        assert result.get("structuredContent", {}).get("success")
        print("✅ Reusable Docker function works!")

        # Verify file creation
        json_files = list(self.storage_path.glob("*.json"))
        assert len(json_files) == 1
        print(f"✅ File created via function: {json_files[0].name}")
