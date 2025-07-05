# Review Claude Desktop Application Logs

Please review the Claude Desktop application logs to diagnose MCP server connection issues and errors.

Follow these steps:

1. **Locate Claude Desktop logs** on macOS at `~/Library/Logs/Claude/`
2. **Read recent log files** focusing on MCP-related errors
3. **Analyze connection issues** for tides, compass, and memry servers
4. **Check server startup errors** and configuration problems
5. **Identify common issues**:
   - Server startup failures
   - Python environment/dependency issues
   - Invalid JSON-RPC messages
   - Tool execution errors
   - Authentication problems
6. **Provide specific diagnosis** with recommended fixes
7. **Test server connections** if possible using direct MCP protocol

## Common Log Locations

```bash
# Claude Desktop logs (macOS)
~/Library/Logs/Claude/

# Look for recent files like:
# main.log
# renderer.log
# mcp-*.log
```

## Diagnostic Process

```bash
# Navigate to logs directory
cd ~/Library/Logs/Claude/

# Find recent log files
ls -la *.log | head -10

# Read recent logs focusing on MCP errors
tail -100 main.log | grep -i "mcp\|error\|fail"
tail -100 renderer.log | grep -i "mcp\|error\|fail"

# Check for server-specific errors
grep -r "tides\|compass\|memry" *.log | tail -20
```

## Common Issues to Look For

1. **Server Startup Failures**
   - Python interpreter not found
   - uv command not available
   - Working directory issues
   - Environment variable problems

2. **MCP Protocol Errors**
   - Invalid JSON-RPC messages
   - Tool schema validation failures
   - Transport connection issues
   - Timeout problems

3. **Configuration Issues**
   - Incorrect file paths in Claude Desktop config
   - Missing environment variables
   - Permission problems

4. **Dependency Problems**
   - Missing Python packages
   - uv workspace sync issues
   - Import errors in server code

## Analysis Output

Provide a structured analysis including:

1. **Error Summary** - What specific errors are occurring
2. **Root Cause** - Why the errors are happening
3. **Affected Servers** - Which MCP servers are failing
4. **Recommended Fixes** - Step-by-step resolution
5. **Prevention** - How to avoid similar issues

## Testing Server Health

After reviewing logs, test server connectivity:

```bash
# Test server startup directly
cd /path/to/mcp-fleet
uv run python servers/tides/main.py
uv run python servers/compass/main.py
uv run python servers/memry/main.py

# Check uv workspace health
uv sync
uv run pytest -x
```

## Usage

Use this command when Claude Desktop shows MCP connection errors:

```
/project:review-logs
```

This will systematically examine Claude Desktop logs and provide diagnosis for MCP server issues discovered after recent refactoring work.

## Requirements

- Access to `~/Library/Logs/Claude/` directory
- Basic understanding of MCP protocol and JSON-RPC
- Knowledge of the mcp-fleet server architecture