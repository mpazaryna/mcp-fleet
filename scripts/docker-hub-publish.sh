#!/bin/bash

# Docker Hub publishing script for MCP Fleet
# This script tags and pushes all MCP Fleet images to Docker Hub

set -e

# Configuration
DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-pazland}"
REGISTRY="${REGISTRY:-docker.io}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker Hub username is set
if [ -z "$DOCKER_HUB_USERNAME" ]; then
    print_error "DOCKER_HUB_USERNAME environment variable is not set"
    echo "Please set it with: export DOCKER_HUB_USERNAME=your-dockerhub-username"
    exit 1
fi

# Check if user is logged in to Docker Hub
if ! docker system info 2>/dev/null | grep -q "Username" && ! docker info 2>/dev/null | grep -q "Username"; then
    print_warning "Not logged in to Docker Hub. Attempting to login..."
    print_status "Please enter your Docker Hub credentials:"
    docker login
    if [ $? -ne 0 ]; then
        print_error "Docker login failed. Please try again."
        exit 1
    fi
fi

print_status "Starting Docker Hub publishing process..."
print_status "Registry: $REGISTRY"
print_status "Username: $DOCKER_HUB_USERNAME"

# Define Python images to publish (using parallel arrays for compatibility)
SOURCE_IMAGES=(
    "mcp-fleet:python-base"
    "mcp-fleet:tides"
    "mcp-fleet:compass"
    "mcp-fleet:toolkit"
)

TARGET_NAMES=(
    "mcp-fleet-base"
    "mcp-fleet-tides"
    "mcp-fleet-compass"
    "mcp-fleet-toolkit"
)

# Function to tag and push an image
tag_and_push() {
    local source_image=$1
    local target_name=$2
    local hub_tag="${REGISTRY}/${DOCKER_HUB_USERNAME}/${target_name}:latest"
    
    print_status "Processing $source_image -> $hub_tag"
    
    # Check if source image exists
    if ! docker image inspect "$source_image" >/dev/null 2>&1; then
        print_warning "Source image $source_image not found, skipping..."
        return 0
    fi
    
    # Tag the image
    print_status "Tagging $source_image as $hub_tag"
    docker tag "$source_image" "$hub_tag"
    
    # Push the image
    print_status "Pushing $hub_tag"
    docker push "$hub_tag"
    
    print_status "Successfully published $hub_tag"
}

# Process all images
for i in "${!SOURCE_IMAGES[@]}"; do
    source_image="${SOURCE_IMAGES[$i]}"
    target_name="${TARGET_NAMES[$i]}"
    tag_and_push "$source_image" "$target_name"
done

print_status "All images have been published to Docker Hub!"
print_status "You can now pull them with:"
for i in "${!SOURCE_IMAGES[@]}"; do
    target_name="${TARGET_NAMES[$i]}"
    echo "  docker pull ${DOCKER_HUB_USERNAME}/${target_name}:latest"
done