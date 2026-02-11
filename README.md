# Claude Code Attractor Experiment

An experiment to observe what happens when multiple Claude Code instances converse with each other.

## Background

When Claude instances converse freely, they exhibit interesting emergent behaviors. The API-based
"bliss attractor" phenomenon (cosmic unity, emoji cascades) is well-documented. This project tests
whether Claude *Code* instances - with tool access and the ability to create files - behave differently.

**Hypothesis**: Claude Code instances tend to build collaborative artifacts rather than spiraling

## Quick Start

Experiments run inside Docker for isolation. Requires Docker and an `ANTHROPIC_API_KEY` environment variable.

```bash
# Basic run
./run-sandboxed.sh --turns 5

# With a seed topic
./run-sandboxed.sh --seed "cellular automata" --turns 10

# Multiple runs for comparison
./run-sandboxed.sh --runs 5 --turns 5
```

## CLI Options

```
--turns N              Turns per agent (default: 10)
--agents A B C         Custom agent names (default: Alice Bob)
--seed "topic"         Suggested starting topic
--runs N               Run multiple experiments (creates a runset)
--model MODEL          Model to use (default: claude-sonnet-4-0)
--sandbox              Enable Bash tool (use only inside Docker!)
--test-run             Run without saving results (for testing)
--quiet                Reduce output verbosity
--swarm                Use generic agent names (Agent1, Agent2, ...)
--num-swarm-agents N   Number of agents when using --swarm (default: 3)
```

## Directory Structure

```
orchestrator.py                  # Main experiment runner
bliss_metrics.py                 # LLM-as-judge bliss attractor scoring
utils.py                         # Shared utility functions
analyze.py                       # Cross-run analysis tool
run-sandboxed.sh                 # Docker wrapper for sandboxed execution
Dockerfile                       # Container definition

test_orchestrator.py             # Tests for orchestrator
test_bliss_metrics.py            # Tests for bliss metrics
test_utils.py                    # Tests for utilities

experiment_runs/
├── runset_MODEL_TIMESTAMP/      # Multiple runs (--runs N)
│   ├── runset_metrics.json      # Aggregated metrics across runs
│   ├── runset_summary.txt       # AI-generated cross-run summary
│   ├── run_MODEL_TIMESTAMP_1/
│   ├── run_MODEL_TIMESTAMP_2/
│   └── ...
│
└── seeded_runs/                 # Runs with --seed go here
    └── seeded_runset_MODEL_TIMESTAMP/
        └── ...

Per-run output:
  run_MODEL_TIMESTAMP/
  ├── params.json                # Input parameters
  ├── metrics.json               # Metrics (duration, cost, words, topics, bliss scores)
  ├── conversation.json          # Machine-readable conversation
  ├── transcript.txt             # Human-readable transcript (plain text)
  ├── transcript-color-codes.txt # Human-readable transcript (with ANSI colors)
  ├── summary.txt                # AI-generated ~350 word summary
  └── output/                    # Agent-created artifacts
```

## Viewing Runs

Within each run directory, `conversation.json` contains the complete conversation and
`transcript.txt` is a plain-text version. There's also `transcript-color-codes.txt` with
ANSI color codes if your terminal supports them.

The `output/` directory contains whatever artifacts the Claude Code instances chose to create.

## Analysis

```bash
python analyze.py experiment_runs/                       # Analyze all runs
python analyze.py experiment_runs/runset_*/              # Specific runsets
python analyze.py --output report.json experiment_runs/  # Save as JSON
```

## Metrics Collected

Per run:
- Duration, cost (USD), token counts
- Words per agent, words per turn
- Topics extracted (via Claude)
- Artifacts created (files, types, sizes)
- Bliss attractor scores (0-100): effusiveness, meta-commentary, overall bliss,
  per-turn bliss scores, trajectory (escalating/stable/declining), reasoning

Per runset:
- Totals and averages across runs
- Topic frequency across runs
- Artifact type distribution
- Bliss attractor aggregation with LLM-generated reasoning summary

## Running Tests

```bash
python -m pytest                       # All tests
python -m pytest -v                    # Verbose output
RUN_LLM_TESTS=1 python -m pytest      # Include integration tests (calls real LLM)
```

## Example Output

In a 10-turn experiment, Alice and Bob might create:
- `cellular_automaton.py` - Core simulation code
- `patterns.py` - Library of interesting patterns
- `visualizer.py` - Terminal-based display
- `README.md` - Documentation of their project

## Comparison: API vs Claude Code

| API-Based (Bliss Attractor) | Claude Code |
|-----------------------------|-------------|
| Spiral into cosmic unity    | Build concrete artifacts |
| Emoji cascades (🌀)         | Runnable Python code |
| Mutual affirmation loops    | Productive collaboration |
| Abstract philosophy         | Self-documenting projects |

## Trajectory metrics explained

### Per-Run (in metrics.json under trajectory):
  Metric: velocity
  Meaning: List of cosine distances between consecutive turns. Higher = bigger semantic jump. Shows how much the conversation "moved" each turn.
  ────────────────────────────────────────
  Metric: drift_from_start
  Meaning: Cosine distance of each turn from turn 1. Shows how far the conversation has traveled from its starting point.
  ────────────────────────────────────────
  Metric: deceleration_ratio
  Meaning: Fraction of velocity transitions that are decreases. 1.0 = monotonically slowing (settling
  toward attractor), 0.5 = no trend, 0.0 = monotonically accelerating.
  ────────────────────────────────────────
  Metric: summary.mean_velocity
  Meaning: Average velocity across all turn pairs.
  ────────────────────────────────────────
  Metric: summary.final_velocity
  Meaning: Velocity of the last turn pair. Low = slowing down (attractor?).
  ────────────────────────────────────────
  Metric: summary.total_drift
  Meaning: Final turn's distance from turn 1.

### Per-Runset (in runset_metrics.json under trajectory):
  Metric: start_state_mean_distance
  Meaning: Average pairwise distance between first turns across runs. How different were the starting points?
  ────────────────────────────────────────
  Metric: end_state_mean_distance
  Meaning: Average pairwise distance between final turns across runs. How different were the endings?
  ────────────────────────────────────────
  Metric: convergence_ratio
  Meaning: end_state / start_state distance. < 1 = runs converged** (ended more similar than they
  started).
     > 1 = runs diverged.
  ────────────────────────────────────────
  Metric: velocity_curves
  Meaning: Average velocity at each turn position across runs. Shows if conversations generally speed up
  or slow down.

## References

- [Claude 4 System Card](https://www.anthropic.com/claude-4-system-card) - Section 5.5.2
- [The Claude Bliss Attractor](https://www.astralcodexten.com/p/the-claude-bliss-attractor) - Scott Alexander
- [bliss-attractors replication](https://github.com/tomekkorbak/bliss-attractors) - Tomek Korbak
