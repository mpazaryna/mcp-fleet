"""
Test to compare working E2E approach vs direct docker commands
"""
import asyncio
import tempfile
import subprocess
import json
from pathlib import Path
import pytest
from .mcp_docker_client import create_memry_client


class TestDockerCommandComparison:
    """Compare different ways of calling Docker to identify the timeout issue"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_working_e2e_approach(self):
        """Test the working E2E approach for comparison"""
        client = create_memry_client(str(self.storage_path))
        
        async with client.connect() as mcp:
            result = await mcp.call_tool("create_memory", {
                "title": "E2E Working Test",
                "content": "This works perfectly",
                "source": "e2e-working",
                "tags": ["working"]
            })
            
            assert result.get("structuredContent", {}).get("success") == True
            print("✅ E2E approach works perfectly")

    def test_direct_docker_command_issue(self):
        """Test the direct docker command that was hanging"""
        # This is the command that was timing out
        docker_input = '''{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "method": "notifications/initialized"}
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "create_memory", "arguments": {"title": "Direct Test", "content": "Testing direct command", "source": "direct", "tags": ["direct"]}}}'''
        
        docker_cmd = [
            "docker", "run", "--rm", "-i",
            "-v", f"{self.storage_path}:/app/memories",
            "pazland/mcp-fleet-memry:latest"
        ]
        
        print(f"🔍 Running direct docker command...")
        print(f"Command: {' '.join(docker_cmd)}")
        print(f"Input: {docker_input}")
        
        try:
            # Use timeout to prevent hanging
            result = subprocess.run(
                docker_cmd,
                input=docker_input,
                text=True,
                capture_output=True,
                timeout=10  # 10 second timeout
            )
            
            print(f"Return code: {result.returncode}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            
            # Check if we got the expected response
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('{"jsonrpc":'):
                        try:
                            response = json.loads(line)
                            if response.get("id") == 2:  # Tool call response
                                print("✅ Direct docker command worked!")
                                return
                        except json.JSONDecodeError:
                            continue
            
            print("❌ Direct docker command didn't return expected response")
            
        except subprocess.TimeoutExpired:
            print("❌ Direct docker command timed out after 10 seconds")
            # This confirms the timeout issue
            
        except Exception as e:
            print(f"❌ Direct docker command failed: {e}")

    def test_docker_with_proper_input_buffering(self):
        """Test docker command with proper input handling"""
        # Try with explicit newlines and proper JSON formatting
        docker_input_lines = [
            '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}',
            '{"jsonrpc": "2.0", "method": "notifications/initialized"}',
            '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "create_memory", "arguments": {"title": "Buffered Test", "content": "Testing with proper buffering", "source": "buffered", "tags": ["buffered"]}}}'
        ]
        
        docker_cmd = [
            "docker", "run", "--rm", "-i",
            "-v", f"{self.storage_path}:/app/memories",
            "pazland/mcp-fleet-memry:latest"
        ]
        
        print(f"🔍 Testing with proper input buffering...")
        
        try:
            process = subprocess.Popen(
                docker_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # Unbuffered
            )
            
            # Send each line separately
            for line in docker_input_lines:
                print(f"Sending: {line}")
                process.stdin.write(line + '\n')
                process.stdin.flush()
                
                # Try to read response
                import select
                import sys
                
                # Wait for output with timeout
                ready, _, _ = select.select([process.stdout], [], [], 2.0)
                if ready:
                    response = process.stdout.readline()
                    if response:
                        print(f"Received: {response.strip()}")
            
            # Close stdin and wait
            process.stdin.close()
            stdout, stderr = process.communicate(timeout=5)
            
            print(f"Final stdout: {stdout}")
            print(f"Final stderr: {stderr}")
            print("✅ Buffered approach completed")
            
        except subprocess.TimeoutExpired:
            print("❌ Buffered approach also timed out")
            process.kill()
            
        except Exception as e:
            print(f"❌ Buffered approach failed: {e}")