# Dockerfile for sandboxed Claude Code experiment runs
#
# Build:
#   docker build -t claude-orchestrator .
#
# Run:
#   docker run --rm \
#     -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
#     -v $(pwd)/experiment_runs:/app/experiment_runs \
#     claude-orchestrator \
#     python orchestrator.py --turns 5

FROM python:3.11-slim

# Install Node.js (required for Claude CLI)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Claude CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Set up working directory
WORKDIR /app

# Copy orchestrator code
COPY orchestrator.py .
COPY analyze.py .

# Create experiment_runs directory (will be mounted over)
RUN mkdir -p experiment_runs

# Default command
CMD ["python", "orchestrator.py", "--help"]
