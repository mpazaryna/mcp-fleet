#!/bin/bash
# Deploy Tides MCP Server for Docker Desktop MCP Toolkit

set -e

echo "🌊 Deploying Tides MCP Server for Docker Desktop MCP Toolkit..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY environment variable is not set."
    echo "   Please set it with: export ANTHROPIC_API_KEY='your-api-key'"
    exit 1
fi

# Build base image if it doesn't exist
if ! docker image inspect mcp-fleet:base >/dev/null 2>&1; then
    echo "📦 Building base image..."
    docker build -t mcp-fleet:base .
fi

# Build Tides server with MCP-friendly tag
echo "🌊 Building Tides MCP server..."
docker build -t mcp/tides:latest -f Dockerfile.tides .

# Stop existing container if running
if docker ps -q -f name=tides-mcp >/dev/null 2>&1; then
    echo "🛑 Stopping existing Tides MCP container..."
    docker stop tides-mcp
    docker rm tides-mcp
fi

# Run the container with MCP Toolkit requirements
echo "🚀 Starting Tides MCP container..."
docker run -d \
    --name tides-mcp \
    -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
    --restart unless-stopped \
    --cpus="1" \
    --memory="2g" \
    mcp/tides:latest

echo "✅ Tides MCP Server deployed successfully!"
echo ""
echo "🔗 Next steps:"
echo "   1. Open Docker Desktop"
echo "   2. Go to MCP Toolkit tab"
echo "   3. Find 'tides-mcp' container"
echo "   4. Click 'Connect to Claude Desktop'"
echo ""
echo "🌊 Available tools in Claude Desktop:"
echo "   • create_tide - Create tidal workflows"
echo "   • list_tides - List all workflows"
echo "   • flow_tide - Start flow sessions"
echo ""
echo "📋 Container status:"
docker ps --filter name=tides-mcp --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"