# MCP Fleet UAT (User Acceptance Testing) Framework

Comprehensive Docker-based User Acceptance Testing framework for all MCP Fleet servers. This framework provides real-world validation that servers work correctly in production Docker environments.

## Overview

The UAT framework tests the complete MCP Fleet ecosystem using actual Docker containers, simulating real deployment scenarios. It validates:

- **End-to-end workflows** for each server
- **Docker container functionality** and communication
- **Data persistence** and file system integration
- **Error handling** and edge cases
- **Performance** under typical usage patterns
- **Integration** between MCP client and server

## Architecture

### Core Components

1. **`mcp_docker_client.py`** - Robust MCP client that communicates with Docker containers
2. **Individual UAT Tests** - Comprehensive test suites for each server
3. **Test Runner** - Orchestrates all tests with parallel execution and reporting
4. **Reporting System** - Detailed JSON reports and console summaries

### Test Framework Features

- **Proper MCP Protocol** - Full JSON-RPC 2.0 implementation with initialization
- **Docker Integration** - Seamless container startup, communication, and cleanup
- **Timeout Management** - Prevents hanging tests with configurable timeouts
- **Error Handling** - Graceful handling of Docker, network, and protocol errors
- **Context Management** - Automatic resource cleanup with context managers
- **Debug Logging** - Detailed logging for troubleshooting

## Available Tests

### 1. Enhanced Memry UAT (`test_enhanced_memry_docker_uat.py`)

Tests the memory management system comprehensively:

- **Core Operations**: Create, read, update, delete memories
- **Advanced Search**: Multi-field search, tag filtering, content search
- **Data Persistence**: File creation, JSON validation, storage verification
- **Edge Cases**: Large content, special characters, invalid inputs
- **Performance**: Batch operations, search speed, creation throughput

**Example Usage:**
```bash
cd tests/uat
python test_enhanced_memry_docker_uat.py
```

### 2. Compass UAT (`test_compass_docker_uat.py`)

Tests the systematic project methodology workflow:

- **Project Lifecycle**: Initialize → Explore → Specify → Execute
- **Phase Enforcement**: Validates methodology requirements
- **File Structure**: Project workspace organization
- **Task Management**: Creation, tracking, status updates
- **Conversation Preservation**: Exploration session storage

**Example Usage:**
```bash
cd tests/uat
python test_compass_docker_uat.py
```

### 3. Tides UAT (`test_tides_docker_uat.py`)

Tests the rhythmic workflow management system:

- **Tide Creation**: Multiple time scales and intensity patterns
- **Flow Sessions**: High/medium/low intensity tracking
- **Report Generation**: Individual and batch exports
- **Claude Integration**: AI-assisted workflow guidance (requires API key)
- **Data Export**: JSON and Markdown format validation

**Example Usage:**
```bash
cd tests/uat
export ANTHROPIC_API_KEY=your-key-here  # Optional for full testing
python test_tides_docker_uat.py
```

## Test Runner

### Comprehensive Test Execution (`run_all_uat_tests.py`)

The test runner provides:

- **Sequential or Parallel** execution modes
- **Automatic prerequisite checking** (Docker, images, files)
- **Comprehensive reporting** with JSON output
- **Error recovery** and timeout handling
- **Selective testing** by server

### Usage Examples

```bash
# Run all available tests sequentially
python tests/uat/run_all_uat_tests.py

# Run specific server tests
python tests/uat/run_all_uat_tests.py --server memry

# Run all tests in parallel (faster)
python tests/uat/run_all_uat_tests.py --parallel

# Get help
python tests/uat/run_all_uat_tests.py --help
```

### Test Reports

Reports are automatically saved to `~/Documents/mcp-fleet-uat-reports/` with:

- **Execution timestamps** and durations
- **Success/failure status** for each test
- **Error messages** and debugging info
- **Environment information** (Python version, platform)
- **Overall success rate** and statistics

## Docker Requirements

### Required Images

The UAT tests require these Docker images to be available:

- `pazland/mcp-fleet-memry:latest`
- `pazland/mcp-fleet-compass:latest`
- `pazland/mcp-fleet-tides:latest`

### Image Checking

The framework automatically checks for image availability and skips tests for missing images.

### Volume Mounting

Each test creates temporary workspaces in `~/Documents/mcp-fleet-uat/` and mounts them into containers for:

- **Data persistence testing**
- **File creation validation** 
- **Cross-container data sharing**
- **Real-world storage simulation**

## Environment Variables

### Optional Configuration

- `ANTHROPIC_API_KEY` - Required for full Tides server Claude integration testing

### Logging

- Logs are written to `~/Documents/mcp-fleet-uat.log`
- Console output shows real-time progress
- Debug mode available for troubleshooting

## Integration with Development Workflow

### TDD Integration

The UAT tests complement the existing test hierarchy:

1. **Unit Tests** - Individual component testing
2. **Integration Tests** - Component interaction testing
3. **E2E Tests** - Full MCP protocol testing
4. **UAT Tests** - Real-world Docker scenario validation ← **This Framework**

### CI/CD Integration

The test runner returns appropriate exit codes for automation:

- `0` - All tests passed
- `1` - Some or all tests failed

Perfect for integration with build pipelines and deployment validation.

### Development Validation

Use UAT tests to validate:

- **Docker builds** work correctly
- **Configuration changes** don't break functionality  
- **New features** work in production environment
- **Performance regressions** are caught early
- **Container orchestration** is functioning

## Troubleshooting

### Common Issues

1. **Docker not available**
   - Ensure Docker is installed and running
   - Check Docker daemon status

2. **Images not found**
   - Build images using provided Dockerfiles
   - Check image tags match expected names

3. **Tests timeout**
   - Check container startup issues
   - Verify volume mount permissions
   - Increase timeout values if needed

4. **Permission errors**
   - Ensure workspace directories are writable
   - Check Docker volume mount permissions

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
from mcp_docker_client import MCPDockerClient
client = MCPDockerClient(server_config, debug=True)
```

### Manual Testing

For manual testing and exploration:

```python
from mcp_docker_client import MCPDockerClient, MEMRY_SERVER, create_test_workspace

workspace = create_test_workspace()
memry_config = MEMRY_SERVER
memry_config.volume_mappings = {str(workspace): "/app/memories"}

with MCPDockerClient(memry_config, debug=True) as client:
    tools = client.list_tools()
    result = client.call_tool("create_memory", {...})
```

## Contributing

When adding new UAT tests:

1. **Follow the established pattern** in existing test files
2. **Use the MCPDockerClient** for all Docker communication
3. **Include comprehensive assertions** for validation
4. **Test both success and error scenarios**
5. **Add test configuration** to `run_all_uat_tests.py`
6. **Update this documentation** with new test descriptions

## Best Practices

### Test Design

- **Test real workflows** users would actually perform
- **Validate data persistence** and file creation
- **Include error handling** and edge case testing
- **Use meaningful test data** that reflects actual usage
- **Verify container cleanup** to prevent resource leaks

### Performance Considerations

- **Use reasonable timeouts** for container operations
- **Clean up temporary data** after tests
- **Consider parallel execution** for large test suites
- **Monitor resource usage** during test runs

### Reliability

- **Make tests idempotent** - can run multiple times safely
- **Handle network issues** and Docker failures gracefully
- **Provide clear error messages** for debugging
- **Use unique workspace names** to avoid conflicts

This UAT framework ensures MCP Fleet servers work reliably in production Docker environments, providing confidence for deployment and integration scenarios.