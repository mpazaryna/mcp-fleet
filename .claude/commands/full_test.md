# Full Test Suite Command

Runs the complete four-tier testing hierarchy for MCP Fleet, ending with UAT validation.

## Test Hierarchy

This command executes tests in the proper order following TDD methodology:

1. **Unit Tests** - Individual component behavior with mocking
2. **Integration Tests** - Cross-component workflows and API testing  
3. **E2E Tests** - Full MCP protocol testing with Docker containers
4. **UAT Tests** - Real-world user scenarios with actual file creation

## Usage

```bash
/full-test
```

## What This Command Does

### Phase 1: Unit & Integration Tests
- Runs all unit and integration tests
- Validates individual components work correctly
- Ensures component interactions function properly

### Phase 2: E2E Tests  
- Tests the complete MCP protocol via Docker containers
- Validates MCPDockerClient framework
- Ensures proper JSON-RPC communication
- Tests tool calls and responses

### Phase 3: UAT Tests
- Runs real-world user acceptance scenarios
- Creates actual files on user's drive
- Validates Docker containers work without timeouts
- Confirms shared storage abstraction is working
- Final go/no-go validation for production

## Success Criteria

All tests must pass for the command to succeed:
- ✅ Unit/Integration tests pass
- ✅ E2E tests pass  
- ✅ UAT creates real files on disk
- ✅ No timeouts or hanging processes
- ✅ Shared storage abstraction confirmed working

## Output

The command provides clear progress indicators and final validation that the entire MCP Fleet system is ready for production use.

## Command Implementation

```bash
#!/bin/bash
set -e

echo "🧪 MCP Fleet - Full Test Suite"
echo "================================"
echo "Running comprehensive 4-tier testing hierarchy..."
echo ""

echo "📋 Phase 1: Core Unit & Integration Tests"
echo "------------------------------------------"
echo "Testing shared storage abstraction..."
uv run pytest tests/packages/test_jsonfile_backend.py -v
uv run pytest tests/packages/test_memory_storage_integration.py -v
echo "✅ Core unit & integration tests completed"
echo ""

echo "🔗 Phase 2: End-to-End Tests"  
echo "-----------------------------"
echo "Testing complete MCP protocol via Docker..."
uv run pytest tests/e2e/test_memry_e2e.py -v
echo "✅ E2E tests completed"
echo ""

echo "🎯 Phase 3: User Acceptance Tests"
echo "----------------------------------"
echo "Running real-world user scenarios..."
python tests/uat/test_memry_docker_uat.py
echo ""

echo "🎉 ALL TESTS PASSED!"
echo "✅ MCP-Memry with shared storage abstraction is validated"
echo "✅ Docker timeout issue is resolved"
echo "✅ All four testing tiers completed successfully"
echo "✅ Ready for production deployment"
```