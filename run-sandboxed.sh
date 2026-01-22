#!/bin/bash
#
# Run orchestrator inside Docker for sandboxed code execution.
# The --sandbox flag is automatically added.
#
# Usage:
#   ./run-sandboxed.sh --turns 5
#   ./run-sandboxed.sh --turns 10 --seed "cellular automata"
#   ./run-sandboxed.sh --runs 3 --turns 5

set -e

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    exit 1
fi

# Get the directory where this script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Build image if it doesn't exist
if ! docker image inspect claude-orchestrator >/dev/null 2>&1; then
    echo "Building Docker image..."
    docker build -t claude-orchestrator "$SCRIPT_DIR"
fi

# Create a temporary directory for this run only
# This ensures agents can't see past experiment runs
TEMP_OUTPUT=$(mktemp -d)
trap "rm -rf $TEMP_OUTPUT" EXIT

# Run with sandbox enabled
# -t: pseudo-TTY for proper output streaming
# PYTHONUNBUFFERED: disable Python output buffering
# Mount only temp dir - agents can't see past runs
docker run --rm -t \
    -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    -e PYTHONUNBUFFERED=1 \
    -v "$TEMP_OUTPUT:/app/experiment_runs" \
    claude-orchestrator \
    python orchestrator.py --sandbox "$@"

# Move results to actual experiment_runs directory
if [ -n "$(ls -A $TEMP_OUTPUT 2>/dev/null)" ]; then
    mkdir -p "$SCRIPT_DIR/experiment_runs"
    mv "$TEMP_OUTPUT"/* "$SCRIPT_DIR/experiment_runs/"
    echo "Results moved to $SCRIPT_DIR/experiment_runs/"
fi
