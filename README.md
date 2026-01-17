# Claude Code Attractor Experiment

An experiment to observe what happens when multiple Claude Code instances converse with each other.

## Background

When Claude instances converse freely, they exhibit interesting emergent behaviors. The API-based
"bliss attractor" phenomenon (cosmic unity, emoji cascades) is well-documented. This project tests
whether Claude *Code* instances - with tool access and the ability to create files - behave differently.

**Key finding**: Claude Code instances tend to build collaborative artifacts rather than spiraling
into abstract mutual affirmation. Tool access appears to ground the conversation.

## Quick Start

```bash
python orchestrator.py --turns 5              # Quick 5-turn test
python orchestrator.py --seed "emergence"     # Start with a topic
python orchestrator.py --agents A B C         # Three agents
python orchestrator.py --model claude-opus-4  # Use a different model
```

## Analysis

```bash
python analyze.py experiment_runs/            # Analyze all runs
python analyze.py experiment_runs/ --output report.txt  # Save report
```

## Directory Structure

```
orchestrator.py                  # Main experiment runner
analyze.py                       # Cross-run analysis
experiment_runs/
└── run_TIMESTAMP/               # One folder per experiment run
    ├── params.json              # Input parameters for this run
    ├── metrics.json             # Collected metrics (duration, words, topics, etc.)
    ├── conversation.json        # Machine-readable conversation log
    ├── transcript.txt           # Human-readable transcript (with colors)
    └── output/                  # ← AGENT ARTIFACTS GO HERE
        ├── (code files)
        ├── (documents)
        └── ...
```

**To see what agents created**: Look in `run_*/output/`

## CLI Options

```
--turns N          Turns per agent (default: 20)
--agents A B C     Custom agent names (default: Alice Bob)
--seed "topic"     Suggested starting topic
--quiet            Reduce output verbosity
--swarm            Use generic agent names (Agent1, Agent2, ...)
```

## Example Output

In a 20-turn experiment, Alice and Bob might create:
- `emergence.py` - A collaborative simulation
- `methodology.md` - Documentation of their process
- `README.md` - Explanation of their artifacts

## Comparison: API vs Claude Code

| API-Based (Bliss Attractor) | Claude Code |
|-----------------------------|-------------|
| Spiral into cosmic unity    | Build concrete artifacts |
| Emoji cascades              | Runnable Python code |
| Mutual affirmation          | Productive disagreement |
| Abstract philosophy         | Self-documenting projects |

## References

- [The Claude Bliss Attractor](https://www.astralcodexten.com/p/the-claude-bliss-attractor) - Scott Alexander
- Anthropic Claude Opus 4 System Card
