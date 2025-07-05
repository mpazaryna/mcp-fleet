"""User Acceptance Tests for YogaTeach MCP Server with Docker deployment."""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any

from mcp_docker_client import MCPDockerClient


class TestYogaTeachDockerUAT:
    """User Acceptance Tests for YogaTeach server in Docker environment."""

    def __init__(self):
        self.client = None
        self.temp_storage_dir = None
        self.generated_files = []

    async def setup(self):
        """Setup test environment."""
        print("🧘 Setting up YogaTeach UAT environment...")
        
        # Create temporary storage directory
        self.temp_storage_dir = tempfile.mkdtemp(prefix="yogateach_uat_")
        print(f"   Storage directory: {self.temp_storage_dir}")
        
        # Create MCP client
        self.client = MCPDockerClient("yogateach")
        await self.client.connect()
        print("   ✅ Connected to YogaTeach MCP server")

    async def cleanup(self):
        """Cleanup test environment."""
        print("🧹 Cleaning up YogaTeach UAT environment...")
        
        if self.client:
            await self.client.close()
            print("   ✅ MCP client closed")
        
        # List generated files for review
        if self.generated_files:
            print(f"   📄 Generated {len(self.generated_files)} files:")
            for file_path in self.generated_files:
                if os.path.exists(file_path):
                    print(f"      - {file_path}")
                else:
                    print(f"      - {file_path} (not found)")

    async def initialize_server(self):
        """Initialize the MCP server."""
        print("🔧 Initializing YogaTeach MCP server...")
        
        response = await self.client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "yogateach-uat", "version": "1.0.0"},
            }
        )
        
        assert response["protocolVersion"] == "2024-11-05"
        assert response["serverInfo"]["name"] == "yogateach"
        print("   ✅ Server initialized successfully")

    async def test_list_tools(self):
        """Test listing available tools."""
        print("📋 Testing tool listing...")
        
        response = await self.client.send_request("tools/list", {})
        
        assert "tools" in response
        tools = response["tools"]
        assert len(tools) == 2
        
        tool_names = [tool["name"] for tool in tools]
        assert "create_setlist" in tool_names
        assert "create_talk" in tool_names
        
        print("   ✅ All expected tools available")
        print(f"      - create_setlist: {[t['description'] for t in tools if t['name'] == 'create_setlist'][0]}")
        print(f"      - create_talk: {[t['description'] for t in tools if t['name'] == 'create_talk'][0]}")

    async def test_create_beginner_setlist(self):
        """Test creating a beginner yoga setlist."""
        print("🧘‍♀️ Testing beginner setlist creation...")
        
        setlist_args = {
            "name": "Gentle Morning Flow",
            "duration": 30,
            "level": "beginner",
            "focus": "flexibility and relaxation",
            "considerations": "First-time yoga students, chairs available for support",
            "theme": "Starting Fresh"
        }
        
        response = await self.client.send_request(
            "tools/call",
            {
                "name": "create_setlist",
                "arguments": setlist_args
            }
        )
        
        assert "content" in response
        result = json.loads(response["content"][0]["text"])
        
        assert result["success"] is True
        assert result["name"] == "Gentle Morning Flow"
        assert result["content_type"] == "setlist"
        
        # Track generated file
        file_path = result["file_path"]
        self.generated_files.append(file_path)
        
        print(f"   ✅ Beginner setlist created: {result['content_id']}")
        print(f"      File: {file_path}")
        return result

    async def test_create_intermediate_setlist(self):
        """Test creating an intermediate yoga setlist."""
        print("🧘‍♂️ Testing intermediate setlist creation...")
        
        setlist_args = {
            "name": "Power Vinyasa Flow",
            "duration": 75,
            "level": "intermediate",
            "focus": "strength and balance",
            "considerations": "Arm balances included, modifications provided",
            "theme": "Building Inner Fire"
        }
        
        response = await self.client.send_request(
            "tools/call",
            {
                "name": "create_setlist",
                "arguments": setlist_args
            }
        )
        
        assert "content" in response
        result = json.loads(response["content"][0]["text"])
        
        assert result["success"] is True
        assert result["name"] == "Power Vinyasa Flow"
        assert result["content_type"] == "setlist"
        
        # Track generated file
        file_path = result["file_path"]
        self.generated_files.append(file_path)
        
        print(f"   ✅ Intermediate setlist created: {result['content_id']}")
        print(f"      File: {file_path}")
        return result

    async def test_create_dharma_talk(self):
        """Test creating a dharma talk."""
        print("🗣️ Testing dharma talk creation...")
        
        talk_args = {
            "name": "The Practice of Letting Go",
            "duration": 25,
            "topic": "non-attachment and letting go",
            "audience": "mixed-level practitioners",
            "style": "contemporary with traditional wisdom",
            "message": "True freedom comes from releasing what no longer serves us"
        }
        
        response = await self.client.send_request(
            "tools/call",
            {
                "name": "create_talk",
                "arguments": talk_args
            }
        )
        
        assert "content" in response
        result = json.loads(response["content"][0]["text"])
        
        assert result["success"] is True
        assert result["name"] == "The Practice of Letting Go"
        assert result["content_type"] == "talk"
        
        # Track generated file
        file_path = result["file_path"]
        self.generated_files.append(file_path)
        
        print(f"   ✅ Dharma talk created: {result['content_id']}")
        print(f"      File: {file_path}")
        return result

    async def test_create_restorative_setlist(self):
        """Test creating a restorative yoga setlist."""
        print("🛌 Testing restorative setlist creation...")
        
        setlist_args = {
            "name": "Deep Rest & Renewal",
            "duration": 60,
            "level": "all levels",
            "focus": "deep relaxation and stress relief",
            "considerations": "Props provided, suitable for pregnancy and injuries",
            "theme": "Nurturing Self-Care"
        }
        
        response = await self.client.send_request(
            "tools/call",
            {
                "name": "create_setlist",
                "arguments": setlist_args
            }
        )
        
        assert "content" in response
        result = json.loads(response["content"][0]["text"])
        
        assert result["success"] is True
        assert result["name"] == "Deep Rest & Renewal"
        assert result["content_type"] == "setlist"
        
        # Track generated file
        file_path = result["file_path"]
        self.generated_files.append(file_path)
        
        print(f"   ✅ Restorative setlist created: {result['content_id']}")
        print(f"      File: {file_path}")
        return result

    async def verify_file_generation(self):
        """Verify that files were actually generated."""
        print("📄 Verifying file generation...")
        
        if not self.generated_files:
            print("   ❌ No files were generated")
            return False
        
        verified_count = 0
        for file_path in self.generated_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"   ✅ {file_path} ({file_size} bytes)")
                verified_count += 1
                
                # Read a snippet to verify content
                with open(file_path, 'r') as f:
                    content = f.read()
                    if content.strip():
                        print(f"      Content preview: {content[:100]}...")
                    else:
                        print(f"      ❌ File is empty")
            else:
                print(f"   ❌ {file_path} not found")
        
        success_rate = verified_count / len(self.generated_files)
        print(f"   📊 File generation success rate: {success_rate:.1%} ({verified_count}/{len(self.generated_files)})")
        
        return success_rate >= 0.8  # 80% success rate threshold

    async def run_all_tests(self):
        """Run all UAT tests."""
        print("🧘 Starting YogaTeach UAT Test Suite")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            await self.setup()
            await self.initialize_server()
            await self.test_list_tools()
            
            # Test content creation
            await self.test_create_beginner_setlist()
            await self.test_create_intermediate_setlist()
            await self.test_create_restorative_setlist()
            await self.test_create_dharma_talk()
            
            # Verify file generation
            file_verification_passed = await self.verify_file_generation()
            
            end_time = time.time()
            duration = end_time - start_time
            
            print("=" * 50)
            print(f"🎉 YogaTeach UAT Test Suite completed in {duration:.2f} seconds")
            print(f"📊 Generated {len(self.generated_files)} content files")
            print(f"✅ File verification: {'PASSED' if file_verification_passed else 'FAILED'}")
            print("=" * 50)
            
            return file_verification_passed
            
        except Exception as e:
            print(f"❌ UAT test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.cleanup()


async def main():
    """Main entry point for UAT tests."""
    test_runner = TestYogaTeachDockerUAT()
    success = await test_runner.run_all_tests()
    
    if success:
        print("🎉 All YogaTeach UAT tests passed!")
        return 0
    else:
        print("❌ Some YogaTeach UAT tests failed.")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)