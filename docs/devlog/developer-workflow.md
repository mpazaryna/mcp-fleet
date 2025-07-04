# Developer Workflow Guide

## Local Testing with Docker Hub Images

The recommended development workflow uses pre-built images from Docker Hub to ensure consistency and avoid build time overhead.

### Quick Start

```bash
# Set your API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Pull Python images (use branch tag until merged to main)
docker pull pazland/mcp-fleet-tides:python-migration
docker pull pazland/mcp-fleet-compass:python-migration  
docker pull pazland/mcp-fleet-of:python-migration

# Test individual servers
docker run -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -v "$(pwd)/workspace:/app/workspace" \
  pazland/mcp-fleet-of:python-migration

docker run -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -v "$(pwd)/reports:/app/reports" \
  pazland/mcp-fleet-tides:python-migration

docker run -v "$(pwd)/workspace:/app/workspace" \
  pazland/mcp-fleet-compass:python-migration

```

### Development Testing Commands

Create these convenience scripts for rapid testing:

```bash
# test-of.sh
#!/bin/bash
docker run --rm -it \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -v "$(pwd)/workspace:/app/workspace" \
  pazland/mcp-fleet-of:python-migration

# test-tides.sh  
#!/bin/bash
docker run --rm -it \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -v "$(pwd)/reports:/app/reports" \
  pazland/mcp-fleet-tides:python-migration

# test-compass.sh
#!/bin/bash
docker run --rm -it \
  -v "$(pwd)/workspace:/app/workspace" \
  pazland/mcp-fleet-compass:python-migration

```

### Claude Desktop Configuration

Use Docker Hub images in your Claude Desktop config:

```json
{
  "mcpServers": {
    "of": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "ANTHROPIC_API_KEY",
        "-v", "/path/to/workspace:/app/workspace",
        "pazland/mcp-fleet-of:latest"
      ]
    },
    "tides": {
      "command": "docker", 
      "args": [
        "run", "--rm", "-i",
        "-e", "ANTHROPIC_API_KEY",
        "-v", "/path/to/reports:/app/reports", 
        "pazland/mcp-fleet-tides:latest"
      ]
    },
    "compass": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "/path/to/workspace:/app/workspace",
        "pazland/mcp-fleet-compass:latest"
      ]
    },
  }
}
```

### Developer Test Pattern

1. **Pull latest images:**
   ```bash
   docker pull pazland/mcp-fleet-of:latest
   docker pull pazland/mcp-fleet-tides:latest
   docker pull pazland/mcp-fleet-compass:latest
   ```

2. **Create test directories:**
   ```bash
   mkdir -p workspace reports
   ```

3. **Run interactive tests:**
   ```bash
   # Test OF template system
   ./test-of.sh
   
   # Test Tides workflow management  
   ./test-tides.sh
   
   # Test Compass project methodology
   ./test-compass.sh
   
   ```

4. **Verify server health:**
   ```bash
   # Each server should respond to MCP protocol
   echo '{"jsonrpc": "2.0", "id": 1, "method": "ping"}' | ./test-of.sh
   ```

### CI/CD Integration Testing

Test the same images that will be deployed:

```bash
# Test specific tagged version
docker run --rm -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -v "$(pwd)/workspace:/app/workspace" \
  pazland/mcp-fleet-of:v2.0.0

# Test multi-platform builds
docker run --platform linux/amd64 --rm \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -v "$(pwd)/workspace:/app/workspace" \
  pazland/mcp-fleet-of:latest
```

### Local Development vs Production

- **Development**: Use Docker Hub images with local volume mounts
- **Production**: Same images with persistent volumes or cloud storage
- **Testing**: Pull specific tagged versions to test releases
- **Debug**: Use `--rm -it` flags for interactive debugging

This workflow ensures you're testing the exact same artifacts that will be deployed in production environments.