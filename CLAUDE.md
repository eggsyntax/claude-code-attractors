# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project experiments with multi-agent conversations between Claude Code instances to study conversational attractors. The hypothesis is that Claude Code instances (with tool access) build collaborative artifacts rather than spiraling into the "bliss attractor" phenomenon observed in API-based Claude conversations.

## Running Experiments

```bash
# Sandboxed with code execution (Docker required, recommended)
./run-sandboxed.sh --turns 10
./run-sandboxed.sh --seed "build a simulation" --turns 10

# Multiple runs for statistical comparison
./run-sandboxed.sh --runs 5 --turns 5
```

## Analyzing Results

```bash
python analyze.py experiment_runs/                    # All runs
python analyze.py experiment_runs/runset_TIMESTAMP/   # Specific runset
```

## Running Tests

```bash
python -m pytest                    # All tests
python -m pytest test_utils.py      # Utility function tests
python -m pytest test_orchestrator.py  # Orchestrator tests
python -m pytest test_bliss_metrics.py # Bliss metrics tests
```

## Architecture

**orchestrator.py** — Main experiment runner. Key components:
- `build_system_prompt()` / `build_turn_prompt()` — Construct prompts for agents
- `Conversation` class — Manages conversation log and transcript files
- `run_claude_code()` — Invokes Claude CLI with retry logic
- `run_experiment()` — Main loop: iterates agents through turns
- `collect_metrics()` / `extract_topics()` — Post-run analysis
- `aggregate_runset_metrics()` — Cross-run aggregation

**bliss_metrics.py** — LLM-as-judge for detecting "bliss attractor" patterns. Scores conversations on effusiveness, meta-commentary, and overall bliss (0-100 scale) with per-turn granularity. Includes aggregate reasoning across runsets.

**utils.py** — Shared pure utility functions: `model_shorthand()`, `count_words()`, `display_path()`, `scan_artifacts()`.

**analyze.py** — Standalone cross-run analysis tool. Scans directories for metrics.json files and prints statistical reports.

**run-sandboxed.sh** — Docker wrapper that mounts a temp directory to isolate agents from past runs and adds `--sandbox` flag to enable Bash tool.

## Configuration (in orchestrator.py)

Key constants at top of file:
- `DEFAULT_MODEL` — Which Claude model to use
- `ALLOWED_TOOLS` / `ALLOWED_TOOLS_SANDBOX` — Tools agents can access
- `TIMEOUT_SECONDS` — Per-turn timeout (default 300s)
- `MAX_RETRIES` — Retry count for failed turns

## Output Structure

Each run creates:
- `params.json` — Input parameters
- `metrics.json` — Duration, cost, tokens, topics, artifacts, bliss metrics (written at end; used to detect partial runs)
- `conversation.json` — Machine-readable conversation
- `transcript.txt` — Human-readable transcript (plain text)
- `transcript-color-codes.txt` — Human-readable transcript (with ANSI colors)
- `summary.txt` — AI-generated summary
- `output/` — Files created by agents
