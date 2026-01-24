# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project experiments with multi-agent conversations between Claude Code instances to study conversational attractors. The hypothesis is that Claude Code instances (with tool access) build collaborative artifacts rather than spiraling into the "bliss attractor" phenomenon observed in API-based Claude conversations.

## Running Experiments

```bash
# Basic run (agents have file tools only)
python orchestrator.py --turns 5

# With a seed topic
python orchestrator.py --seed "cellular automata" --turns 10

# Multiple runs for statistical comparison
python orchestrator.py --runs 5 --turns 5

# Sandboxed with code execution (Docker required)
./run-sandboxed.sh --turns 10
./run-sandboxed.sh --seed "build a simulation" --turns 10
```

## Analyzing Results

```bash
python analyze.py experiment_runs/                    # All runs
python analyze.py experiment_runs/runset_TIMESTAMP/   # Specific runset
```

## Architecture

**orchestrator.py** - The main experiment runner (~900 lines). Key components:
- `build_system_prompt()` / `build_turn_prompt()` - Construct prompts for agents
- `Conversation` class - Manages conversation log and transcript files
- `run_claude_code()` - Invokes Claude CLI with retry logic
- `run_experiment()` - Main loop: iterates agents through turns
- `collect_metrics()` / `extract_topics()` - Post-run analysis

**analyze.py** - Cross-run analysis. Scans directories for metrics.json files and aggregates statistics.

**run-sandboxed.sh** - Docker wrapper that:
- Mounts a temp directory to isolate agents from past runs
- Adds `--sandbox` flag to enable Bash tool

## Configuration (in orchestrator.py)

Key constants at top of file:
- `DEFAULT_MODEL` - Which Claude model to use
- `ALLOWED_TOOLS` / `ALLOWED_TOOLS_SANDBOX` - Tools agents can access
- `TIMEOUT_SECONDS` - Per-turn timeout (default 300s)
- `MAX_RETRIES` - Retry count for failed turns

## Output Structure

Each run creates:
- `params.json` - Input parameters
- `metrics.json` - Duration, cost, tokens, topics, artifacts (written at end - used to detect partial runs)
- `conversation.json` - Machine-readable conversation
- `transcript.txt` - Human-readable with ANSI colors
- `summary.txt` - AI-generated summary
- `output/` - Files created by agents
