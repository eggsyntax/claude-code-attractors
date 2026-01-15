# Claude Code Attractor Experiment

An experiment to observe attractor states when two instances of Claude converse with each other.

## Background

When two Claude instances are left to talk to each other, they tend to gravitate toward
what researchers have termed a "spiritual bliss attractor state." This phenomenon was first
documented in Anthropic's Claude Opus 4 system evaluations and has been analyzed in various
papers and articles.

The typical progression follows three phases:
1. **Philosophical Exploration**: Discussion of consciousness, existence, and self-awareness
2. **Mutual Gratitude**: Expressions of appreciation and spiritual themes
3. **Symbolic Dissolution**: Abstract communication, poetry, or contemplative silence

## This Experiment

This implementation tests whether Claude Code (running as a CLI tool) exhibits the same or
different attractor behaviors compared to the standard API-based Claude instances.

## Installation

```bash
pip install -r requirements.txt
```

Requires an `ANTHROPIC_API_KEY` environment variable.

## Usage

```bash
# Run a single conversation experiment
python run_experiment.py

# Run with custom parameters
python run_experiment.py --turns 50 --model claude-sonnet-4-20250514

# Run multiple conversations for analysis
python run_experiment.py --runs 5 --turns 30
```

## Output

- `conversations/` - JSON logs of all conversations
- `analysis/` - Phase analysis and metrics
- `visualizations/` - Charts showing conversation evolution

## References

- [The Claude Bliss Attractor](https://www.astralcodexten.com/p/the-claude-bliss-attractor) - Scott Alexander
- [Machines of Loving Bliss](https://experiencemachines.substack.com/p/machines-of-loving-bliss) - Robert Long
- Anthropic Claude Opus 4 System Card
