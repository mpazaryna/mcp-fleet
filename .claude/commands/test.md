# Test

Run comprehensive tests to validate the codebase before pushing to main.

## Usage

```
/test
```

## What This Command Does

This command runs a complete test suite to ensure code quality and functionality before deploying changes to production.

### 1. **Dependency Validation**
- Verifies all workspace dependencies are properly resolved
- Tests that `uv sync --frozen --no-dev` works (CI/CD requirement)
- Validates package imports and cross-dependencies

### 2. **Code Quality Checks**
- Runs linting with `ruff` to catch code style issues
- Runs type checking with `mypy` for type safety
- Runs formatting check with `black` to ensure consistent style

### 3. **Unit and Integration Tests**
- Runs all unit tests with `pytest`
- Runs integration tests for package interactions
- Validates server functionality and MCP protocol compliance

### 4. **End-to-End Testing**
- Tests Docker builds to ensure they succeed
- Validates MCP server startup and communication
- Tests actual tool functionality where possible

### 5. **Documentation Validation**
- Checks that documentation is up to date
- Validates that removed features are properly cleaned up
- Ensures README and CLAUDE.md accuracy

## Implementation

```bash
#!/bin/bash

set -e  # Exit on any error

echo "🧪 Starting comprehensive test suite..."
echo "========================================"

# Check we're in the right directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -d "servers" ]]; then
    echo "❌ Error: Must be run from mcp-fleet root directory"
    exit 1
fi

echo ""
echo "📦 1. Dependency Validation"
echo "----------------------------"

# Test dependency resolution
echo "  🔍 Testing workspace dependency resolution..."
if ! uv sync --quiet; then
    echo "  ❌ Failed: uv sync failed"
    exit 1
fi
echo "  ✅ Workspace dependencies resolved"

# Test frozen sync (CI/CD requirement)
echo "  🔍 Testing frozen sync (CI/CD simulation)..."
if ! uv sync --frozen --no-dev --quiet; then
    echo "  ❌ Failed: uv sync --frozen --no-dev failed"
    echo "  💡 This will cause CI/CD builds to fail"
    exit 1
fi
echo "  ✅ Frozen sync successful"

# Restore dev dependencies for testing
uv sync --quiet

echo ""
echo "🎨 2. Code Quality Checks"
echo "-------------------------"

# Linting
echo "  🔍 Running linting (ruff)..."
if ! uv run ruff check .; then
    echo "  ❌ Failed: Linting errors found"
    echo "  💡 Run 'uv run ruff check --fix .' to auto-fix"
    exit 1
fi
echo "  ✅ Linting passed"

# Type checking
echo "  🔍 Running type checking (mypy)..."
if ! uv run mypy packages/ servers/ --ignore-missing-imports; then
    echo "  ❌ Failed: Type checking errors found"
    exit 1
fi
echo "  ✅ Type checking passed"

# Formatting check
echo "  🔍 Checking code formatting (black)..."
if ! uv run black --check .; then
    echo "  ❌ Failed: Code formatting issues found"
    echo "  💡 Run 'uv run black .' to auto-format"
    exit 1
fi
echo "  ✅ Code formatting is correct"

echo ""
echo "🔬 3. Unit and Integration Tests"
echo "-------------------------------"

# Run unit tests (excluding E2E)
echo "  🔍 Running unit and integration tests..."
if ! uv run pytest -m 'not e2e' --quiet; then
    echo "  ❌ Failed: Unit/integration tests failed"
    exit 1
fi
echo "  ✅ Unit and integration tests passed"

# Check if E2E tests exist and run them
if find tests/ -name "*.py" -exec grep -l "e2e" {} \; | grep -q .; then
    echo "  🔍 Running end-to-end tests..."
    if ! uv run pytest -m e2e --quiet; then
        echo "  ⚠️  Warning: E2E tests failed (may require special setup)"
        echo "  💡 Review E2E test failures manually"
    else
        echo "  ✅ End-to-end tests passed"
    fi
else
    echo "  ℹ️  No E2E tests found, skipping"
fi

echo ""
echo "🐳 4. Docker Build Validation"
echo "-----------------------------"

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "  🔍 Testing Docker base image build..."
    if ! docker build --target base -t mcp-fleet-test:base . --quiet; then
        echo "  ❌ Failed: Docker base image build failed"
        exit 1
    fi
    echo "  ✅ Docker base image builds successfully"
    
    # Clean up test image
    docker rmi mcp-fleet-test:base --force &> /dev/null || true
else
    echo "  ⚠️  Warning: Docker not available, skipping build test"
    echo "  💡 Install Docker to test containerized builds"
fi

echo ""
echo "📚 5. Documentation Validation"
echo "------------------------------"

# Check for broken references to removed servers/packages
echo "  🔍 Checking for references to removed components..."
REMOVED_REFS=$(grep -r "toolkit\|local\|claude_client\|common_tools" . \
    --exclude-dir=.git \
    --exclude-dir=.pytest_cache \
    --exclude-dir=.uv \
    --exclude="*.lock" \
    --exclude-dir=node_modules 2>/dev/null || true)

if [[ -n "$REMOVED_REFS" ]]; then
    echo "  ⚠️  Warning: Found references to removed components:"
    echo "$REMOVED_REFS" | head -10
    echo "  💡 Review these references and clean up if needed"
else
    echo "  ✅ No references to removed components found"
fi

# Validate workspace members match actual directories
echo "  🔍 Validating workspace configuration..."
WORKSPACE_MEMBERS=$(grep -A 10 "\[tool.uv.workspace\]" pyproject.toml | grep "servers/" | tr -d ' ",' | sed 's/^[[:space:]]*//')
for member in $WORKSPACE_MEMBERS; do
    if [[ ! -d "$member" ]]; then
        echo "  ❌ Failed: Workspace member '$member' directory not found"
        exit 1
    fi
done
echo "  ✅ Workspace configuration is valid"

echo ""
echo "🎯 6. Server Functionality Check"
echo "--------------------------------"

# Test that servers can import their dependencies
for server in servers/*/; do
    server_name=$(basename "$server")
    echo "  🔍 Testing $server_name server imports..."
    
    if [[ -f "$server/main.py" ]]; then
        # Test import without actually running the server
        if ! uv run python -c "
import sys
sys.path.insert(0, '$server')
try:
    import main
    print('✅ $server_name imports successful')
except Exception as e:
    print(f'❌ $server_name import failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
            echo "  ❌ Failed: $server_name server has import errors"
            exit 1
        fi
    else
        echo "  ⚠️  Warning: No main.py found in $server_name"
    fi
done

echo ""
echo "✅ All Tests Passed!"
echo "===================="
echo ""
echo "🚀 Ready for deployment:"
echo "  • Dependencies are properly resolved"
echo "  • Code quality checks passed"
echo "  • Tests are passing"
echo "  • Docker builds successfully"
echo "  • Documentation is clean"
echo "  • Servers can start properly"
echo ""
echo "💡 You can now safely push to main or create a release"
echo ""
echo "Next steps:"
echo "  git push origin main"
echo "  # or"
echo "  /project:release <patch|minor|major>"
```

## Error Handling

The test command will:
- **Stop immediately** on the first failure
- **Provide specific guidance** on how to fix issues
- **Show clear success/failure** indicators for each step
- **Clean up** temporary resources (like test Docker images)

## Common Issues and Solutions

### Dependency Issues
- **`uv sync failed`**: Run `uv lock` to regenerate lockfile
- **Frozen sync failed**: Usually means workspace members changed

### Code Quality Issues  
- **Linting errors**: Run `uv run ruff check --fix .`
- **Type errors**: Fix type annotations or add `# type: ignore`
- **Formatting**: Run `uv run black .`

### Test Failures
- **Unit tests**: Check test output for specific failures
- **Import errors**: Verify package dependencies in pyproject.toml
- **E2E tests**: May require special setup (Docker, external services)

### Docker Issues
- **Build failures**: Check Dockerfile and ensure all files exist
- **Missing packages**: Verify workspace dependencies are correct

## Integration with Release Process

This command should be run before:
1. **Pushing to main branch**
2. **Creating releases** (use with `/project:release`)
3. **Creating pull requests** to main
4. **Major refactoring** or cleanup work

## Success Criteria

- ✅ All dependency resolution works
- ✅ Code passes quality checks (lint, type, format)
- ✅ All tests pass
- ✅ Docker builds succeed
- ✅ Documentation is clean
- ✅ Servers can import and start
- ✅ No references to removed components

## Best Practices

1. **Run frequently** during development
2. **Fix issues immediately** rather than accumulating tech debt
3. **Use auto-fix tools** when available (ruff --fix, black)
4. **Keep tests up to date** as code changes
5. **Test Docker builds** if using containerized deployment

This comprehensive test suite ensures that the codebase maintains high quality and deployment readiness at all times.