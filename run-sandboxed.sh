#!/bin/bash
#
# Run orchestrator inside Docker for sandboxed code execution.
# The --sandbox flag is automatically added.
#
# Usage:
#   ./run-sandboxed.sh --turns 5
#   ./run-sandboxed.sh --turns 10 --seed "cellular automata"
#   ./run-sandboxed.sh --runs 3 --turns 5
#   ./run-sandboxed.sh --rebuild --turns 5   # Force Docker image rebuild
#
# Environment variables:
#   ANTHROPIC_API_KEY - Required for Claude API access
#   OPENAI_API_KEY    - Optional, enables embedding-based trajectory analysis

set -e

# Check for --rebuild flag (must be first argument if present)
FORCE_REBUILD=false
if [ "$1" = "--rebuild" ]; then
    FORCE_REBUILD=true
    shift
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    exit 1
fi

# Note about optional embedding analysis
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Note: OPENAI_API_KEY not set - trajectory embedding analysis will be skipped"
fi

# Get the directory where this script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if rebuild is needed: image doesn't exist, --rebuild flag, or source files changed
NEEDS_BUILD=false
if [ "$FORCE_REBUILD" = true ]; then
    NEEDS_BUILD=true
elif ! docker image inspect claude-orchestrator >/dev/null 2>&1; then
    NEEDS_BUILD=true
else
    # Check if any source files are newer than the Docker image
    IMAGE_CREATED=$(docker image inspect claude-orchestrator --format '{{.Created}}' 2>/dev/null)
    if [ -n "$IMAGE_CREATED" ]; then
        IMAGE_TS=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${IMAGE_CREATED%%.*}" "+%s" 2>/dev/null || echo "0")
        for src in "$SCRIPT_DIR"/*.py "$SCRIPT_DIR"/Dockerfile; do
            if [ -f "$src" ]; then
                SRC_TS=$(stat -f "%m" "$src" 2>/dev/null || echo "0")
                if [ "$SRC_TS" -gt "$IMAGE_TS" ]; then
                    echo "Source file changed: $(basename "$src")"
                    NEEDS_BUILD=true
                    break
                fi
            fi
        done
    fi
fi

if [ "$NEEDS_BUILD" = true ]; then
    echo "Building Docker image..."
    docker build -t claude-orchestrator "$SCRIPT_DIR"
fi

# Create a temporary directory for this run only
# This ensures agents can't see past experiment runs
TEMP_OUTPUT=$(mktemp -d)
CLEANED_UP=false

# Cleanup function: move any results before deleting temp dir
cleanup() {
    if [ "$CLEANED_UP" = true ]; then
        return
    fi
    CLEANED_UP=true

    # Move any results to actual experiment_runs directory
    if [ -n "$(ls -A $TEMP_OUTPUT 2>/dev/null)" ]; then
        mkdir -p "$SCRIPT_DIR/experiment_runs"
        mv "$TEMP_OUTPUT"/* "$SCRIPT_DIR/experiment_runs/"
        echo ""
        echo "Results moved to $SCRIPT_DIR/experiment_runs/"
    fi

    # Clean up temp directory
    rm -rf "$TEMP_OUTPUT"
}

# Trap both normal exit and interrupt signals
trap cleanup EXIT
trap 'echo ""; echo "Interrupted - saving completed runs..."; cleanup; exit 130' INT TERM

# Run with sandbox and docker flags enabled
# -t: pseudo-TTY for proper output streaming
# PYTHONUNBUFFERED: disable Python output buffering
# Mount only temp dir - agents can't see past runs
docker run --rm -t \
    -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    ${OPENAI_API_KEY:+-e OPENAI_API_KEY="$OPENAI_API_KEY"} \
    -e PYTHONUNBUFFERED=1 \
    -v "$TEMP_OUTPUT:/app/experiment_runs" \
    claude-orchestrator \
    python orchestrator.py --docker --sandbox "$@"
