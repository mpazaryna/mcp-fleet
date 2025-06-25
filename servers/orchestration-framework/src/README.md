# Orchestration Framework - AI-Assisted Project Management

# Initialize a project
deno run --allow-read --allow-write --allow-net --allow-env src/explore.ts init "learning photography"

# Navigate to project
cd learning-photography

# Check status
deno run --allow-read --allow-write --allow-net --allow-env ../src/explore.ts status

# Start exploration
deno run --allow-read --allow-write --allow-net --allow-env ../src/explore.ts explore