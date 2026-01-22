# Claude Code Attractor Experiment

An experiment to observe what happens when multiple Claude Code instances converse with each other.

## Background

When Claude instances converse freely, they exhibit interesting emergent behaviors. The API-based
"bliss attractor" phenomenon (cosmic unity, emoji cascades) is well-documented. This project tests
whether Claude *Code* instances - with tool access and the ability to create files - behave differently.

**Hypothesis**: Claude Code instances tend to build collaborative artifacts rather than spiraling
into abstract mutual affirmation. Tool access appears to ground the conversation.

## Quick Start

```bash
# Basic run (no code execution)
python orchestrator.py --turns 5

# With a seed topic
python orchestrator.py --seed "cellular automata" --turns 10

# Multiple runs for comparison
python orchestrator.py --runs 5 --turns 5
```

## Sandboxed Execution (Docker)

To let agents execute code they write, run inside Docker:

```bash
./run-sandboxed.sh --turns 10
./run-sandboxed.sh --turns 10 --seed "build a simulation"
```

This runs the entire experiment in an isolated container where agents have Bash access
but can't affect your host system. Requires Docker.

To build the Docker image manually:
```bash
docker build -t claude-orchestrator .
```

## CLI Options

```
--turns N          Turns per agent (default: 10)
--agents A B C     Custom agent names (default: Alice Bob)
--seed "topic"     Suggested starting topic
--runs N           Run multiple experiments (creates a runset)
--model MODEL      Model to use (default: claude-sonnet-4-5-20250929)
--sandbox          Enable Bash tool (use only inside Docker!)
--test-run         Run without saving results (for testing)
--quiet            Reduce output verbosity
--swarm            Use generic agent names (Agent1, Agent2, ...)
--num-swarm-agents Number of agents when using --swarm (default: 3)
```

## Directory Structure

```
orchestrator.py                  # Main experiment runner
analyze.py                       # Cross-run analysis
run-sandboxed.sh                 # Docker wrapper for sandboxed execution
Dockerfile                       # Container definition

experiment_runs/
├── run_TIMESTAMP/               # Single experiment run
│   ├── params.json              # Input parameters
│   ├── metrics.json             # Metrics (duration, cost, words, topics)
│   ├── conversation.json        # Machine-readable conversation
│   ├── transcript.txt           # Human-readable transcript (auto-generated from conversation.json)
│   ├── summary.txt              # AI-generated ~350 word summary
│   └── output/                  # Agent-created artifacts
│       ├── (code files)
│       └── (documents)
│
├── runset_TIMESTAMP/            # Multiple runs (--runs N)
│   ├── runset_metrics.json      # Aggregated metrics across runs
│   ├── run_TIMESTAMP_1/
│   ├── run_TIMESTAMP_2/
│   └── ...
│
└── seeded_runs/                 # Runs with --seed go here
    └── run_TIMESTAMP_SEED/
```

## Analysis

```bash
python analyze.py experiment_runs/                    # Analyze all runs
python analyze.py experiment_runs/ --output report.txt  # Save report
```

## Metrics Collected

Per run:
- Duration, cost (USD), token counts
- Words per agent
- Topics extracted (via Claude)
- Artifacts created (files, types, sizes)

Per runset:
- Totals and averages across runs
- Topic frequency across runs
- Artifact type distribution

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

## References

- [Claude 4 System Card](https://www.anthropic.com/claude-4-system-card) - Section 5.5.2
- [The Claude Bliss Attractor](https://www.astralcodexten.com/p/the-claude-bliss-attractor) - Scott Alexander
- [bliss-attractors replication](https://github.com/tomekkorbak/bliss-attractors) - Tomek Korbak
