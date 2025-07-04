#!/usr/bin/env python3
"""
Comprehensive UAT Test Runner for MCP Fleet

Executes all User Acceptance Tests for MCP Fleet servers using Docker containers.
Provides unified reporting, error handling, and test orchestration.

Usage:
    python tests/uat/run_all_uat_tests.py
    python tests/uat/run_all_uat_tests.py --server memry
    python tests/uat/run_all_uat_tests.py --parallel
    python tests/uat/run_all_uat_tests.py --report-only
"""
import argparse
import concurrent.futures
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path.home() / "Documents" / "mcp-fleet-uat.log"),
    ],
)
logger = logging.getLogger(__name__)


class UATTestResult:
    """Container for UAT test results"""

    def __init__(self, server_name: str, test_file: str):
        self.server_name = server_name
        self.test_file = test_file
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None
        self.success: bool = False
        self.error_message: str | None = None
        self.output: str = ""
        self.docker_images_checked: list[str] = []

    @property
    def duration(self) -> float:
        """Test duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "server_name": self.server_name,
            "test_file": self.test_file,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration,
            "success": self.success,
            "error_message": self.error_message,
            "output_lines": len(self.output.split("\n")) if self.output else 0,
            "docker_images_checked": self.docker_images_checked,
        }


class UATTestRunner:
    """Main UAT test runner and orchestrator"""

    def __init__(self):
        self.results: list[UATTestResult] = []
        self.uat_dir = Path(__file__).parent
        self.report_dir = Path.home() / "Documents" / "mcp-fleet-uat-reports"
        self.report_dir.mkdir(exist_ok=True)

        # Define test configurations
        self.test_configs = {
            "memry": {
                "test_file": "test_enhanced_memry_docker_uat.py",
                "docker_image": "pazland/mcp-fleet-memry:latest",
                "description": "Enhanced memory management system testing",
            },
            "compass": {
                "test_file": "test_compass_docker_uat.py",
                "docker_image": "pazland/mcp-fleet-compass:latest",
                "description": "Project methodology workflow testing",
            },
            "tides": {
                "test_file": "test_tides_docker_uat.py",
                "docker_image": "pazland/mcp-fleet-tides:latest",
                "description": "Rhythmic workflow management testing",
            },
        }

    def check_docker_images(self) -> dict[str, bool]:
        """Check if required Docker images are available"""
        logger.info("🐳 Checking Docker images availability...")

        image_status = {}
        for server, config in self.test_configs.items():
            image = config["docker_image"]
            try:
                result = subprocess.run(
                    ["docker", "image", "inspect", image],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                image_status[server] = result.returncode == 0
                status = "✅" if result.returncode == 0 else "❌"
                logger.info(f"   {status} {server}: {image}")
            except subprocess.TimeoutExpired:
                image_status[server] = False
                logger.error(f"   ❌ {server}: Timeout checking {image}")
            except Exception as e:
                image_status[server] = False
                logger.error(f"   ❌ {server}: Error checking {image}: {e}")

        return image_status

    def check_prerequisites(self) -> bool:
        """Check all prerequisites for running UAT tests"""
        logger.info("🔍 Checking UAT test prerequisites...")

        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], capture_output=True, timeout=10)
            logger.info("   ✅ Docker is available")
        except Exception:
            logger.error("   ❌ Docker is not available or not installed")
            return False

        # Check test files exist
        missing_files = []
        for server, config in self.test_configs.items():
            test_file = self.uat_dir / config["test_file"]
            if not test_file.exists():
                missing_files.append(str(test_file))

        if missing_files:
            logger.error(f"   ❌ Missing test files: {missing_files}")
            return False

        logger.info("   ✅ All test files found")

        # Check Docker images
        image_status = self.check_docker_images()
        missing_images = [
            server for server, available in image_status.items() if not available
        ]

        if missing_images:
            logger.warning(f"   ⚠️  Missing Docker images for: {missing_images}")
            logger.warning("   These tests will be skipped")

        return True

    def run_single_test(self, server_name: str) -> UATTestResult:
        """Run UAT test for a single server"""
        config = self.test_configs[server_name]
        test_file = self.uat_dir / config["test_file"]

        result = UATTestResult(server_name, config["test_file"])
        result.start_time = datetime.now()

        logger.info(f"🚀 Starting {server_name} UAT test...")
        logger.info(f"   📋 Description: {config['description']}")
        logger.info(f"   📄 Test file: {config['test_file']}")

        try:
            # Run the test
            process = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                cwd=self.uat_dir,
            )

            result.output = process.stdout + process.stderr
            result.success = process.returncode == 0

            if result.success:
                logger.info(f"   ✅ {server_name} UAT test passed")
            else:
                result.error_message = (
                    f"Test failed with return code {process.returncode}"
                )
                logger.error(f"   ❌ {server_name} UAT test failed")
                logger.error(f"   Error: {result.error_message}")

                # Log last few lines of output for debugging
                if result.output:
                    last_lines = result.output.split("\n")[-10:]
                    logger.error("   Last 10 lines of output:")
                    for line in last_lines:
                        if line.strip():
                            logger.error(f"     {line}")

        except subprocess.TimeoutExpired:
            result.error_message = "Test timed out after 10 minutes"
            logger.error(f"   ⏰ {server_name} UAT test timed out")

        except Exception as e:
            result.error_message = f"Unexpected error: {str(e)}"
            logger.error(f"   💥 {server_name} UAT test crashed: {e}")

        finally:
            result.end_time = datetime.now()

        return result

    def run_tests_sequential(self, servers: list[str]) -> list[UATTestResult]:
        """Run tests sequentially"""
        logger.info("📋 Running UAT tests sequentially...")

        results = []
        for server in servers:
            result = self.run_single_test(server)
            results.append(result)
            self.results.append(result)

            # Brief pause between tests
            if server != servers[-1]:  # Not the last test
                logger.info("⏸️  Pausing 5 seconds between tests...")
                time.sleep(5)

        return results

    def run_tests_parallel(self, servers: list[str]) -> list[UATTestResult]:
        """Run tests in parallel"""
        logger.info("⚡ Running UAT tests in parallel...")

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tests
            future_to_server = {
                executor.submit(self.run_single_test, server): server
                for server in servers
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_server):
                server = future_to_server[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.results.append(result)
                except Exception as e:
                    logger.error(f"Error running {server} test: {e}")
                    # Create a failed result
                    result = UATTestResult(
                        server, self.test_configs[server]["test_file"]
                    )
                    result.start_time = datetime.now()
                    result.end_time = datetime.now()
                    result.error_message = f"Execution error: {str(e)}"
                    results.append(result)
                    self.results.append(result)

        return results

    def generate_report(self) -> dict:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.results)

        report = {
            "report_generated": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (
                    (passed_tests / total_tests * 100) if total_tests > 0 else 0
                ),
                "total_duration_seconds": total_duration,
            },
            "test_results": [result.to_dict() for result in self.results],
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(Path.cwd()),
            },
        }

        return report

    def save_report(self, report: dict) -> Path:
        """Save report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"uat_report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Report saved to: {report_file}")
        return report_file

    def print_summary(self, report: dict) -> None:
        """Print test summary to console"""
        print("\n" + "=" * 60)
        print("🧪 MCP FLEET UAT TEST SUMMARY")
        print("=" * 60)

        summary = report["summary"]
        print(f"📊 Tests Run: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"⏱️  Total Duration: {summary['total_duration_seconds']:.1f}s")

        print("\n📋 Individual Test Results:")
        for result in self.results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.server_name}: {result.duration:.1f}s")
            if not result.success and result.error_message:
                print(f"      Error: {result.error_message}")

        print("\n🎯 Overall Status:", end=" ")
        if summary["passed"] == summary["total_tests"]:
            print("🎉 ALL TESTS PASSED! MCP Fleet ready for production!")
        elif summary["passed"] > 0:
            print("⚠️  PARTIAL SUCCESS - Some servers need attention")
        else:
            print("🚨 ALL TESTS FAILED - Critical issues need resolution")

        print("=" * 60)

    def run(self, servers: list[str] | None = None, parallel: bool = False) -> bool:
        """Run UAT tests"""
        logger.info("🧪 MCP Fleet UAT Test Runner Starting...")

        # Check prerequisites
        if not self.check_prerequisites():
            logger.error("❌ Prerequisites not met, aborting UAT tests")
            return False

        # Determine which servers to test
        if servers is None:
            # Check which servers have available Docker images
            image_status = self.check_docker_images()
            servers = [
                server for server, available in image_status.items() if available
            ]

            if not servers:
                logger.error("❌ No Docker images available for testing")
                return False

        logger.info(f"🎯 Testing servers: {', '.join(servers)}")

        # Run tests
        start_time = datetime.now()
        if parallel:
            self.run_tests_parallel(servers)
        else:
            self.run_tests_sequential(servers)

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        logger.info(f"⏱️  Total test execution time: {total_duration:.1f}s")

        # Generate and save report
        report = self.generate_report()
        self.save_report(report)
        self.print_summary(report)

        # Return overall success
        return all(result.success for result in self.results)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MCP Fleet UAT Test Runner")
    parser.add_argument(
        "--server",
        choices=["memry", "compass", "tides"],
        help="Run tests for specific server only",
    )
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate report from previous test results only",
    )

    args = parser.parse_args()

    runner = UATTestRunner()

    if args.report_only:
        print("📊 Report-only mode not implemented yet")
        return

    servers = [args.server] if args.server else None

    success = runner.run(servers=servers, parallel=args.parallel)

    if success:
        print("\n🌟 All UAT tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some UAT tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
