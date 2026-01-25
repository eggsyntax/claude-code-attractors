#!/usr/bin/env python3
"""
Cross-run analysis for Claude Code conversation experiments.

Provides detailed statistical analysis beyond the basic metrics in runset_metrics.json.
Can be run standalone for ad-hoc analysis or called from orchestrator.py.

Usage:
    python analyze.py experiment_runs/runset_2026-01-16/   # Analyze a runset
    python analyze.py experiment_runs/                      # Analyze all runs
    python analyze.py --output analysis.json path/         # Specify output file
"""

import json
import argparse
from pathlib import Path
from collections import Counter


def is_run_dir(path: Path) -> bool:
    """Check if a directory is a run (has metrics.json)."""
    return path.is_dir() and (path / "metrics.json").exists()


def find_runs(search_path: Path) -> list[Path]:
    """
    Find all experiment runs in the given path.

    Handles:
    - Single run directory (has metrics.json)
    - Directory containing runs (runset_*/)
    - Directory containing runsets containing runs (experiment_runs/runset_*/run_*)
    """
    runs = []

    if not search_path.exists():
        return runs

    # Check if search_path itself is a run
    if is_run_dir(search_path):
        return [search_path]

    # Check direct children and grandchildren
    if search_path.is_dir():
        for child in sorted(search_path.iterdir()):
            if child.is_dir():
                if is_run_dir(child):
                    runs.append(child)
                else:
                    # Go one level deeper (for runset structure)
                    for grandchild in sorted(child.iterdir()):
                        if is_run_dir(grandchild):
                            runs.append(grandchild)

    return runs


def load_metrics(run_path: Path) -> dict | None:
    """Load metrics from a run directory."""
    metrics_file = run_path / "metrics.json"

    if not metrics_file.exists():
        return None

    try:
        with open(metrics_file) as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {run_path}: {e}")
        return None


def analyze_runs(run_dirs: list[Path]) -> dict:
    """
    Analyze runs and return metrics not already in runset_metrics.json.

    Unique metrics provided:
    - min/max ranges for duration, cost, words
    - words_by_turn (conversation arc analysis)
    - failure count
    - runs_with_code count
    - per-run summary
    """
    all_metrics = []
    run_summaries = []

    for run_dir in run_dirs:
        m = load_metrics(run_dir)
        if m:
            all_metrics.append(m)
            run_summaries.append({
                'name': run_dir.name,
                'duration_seconds': m.get('duration_seconds', 0),
                'words': m.get('total_words', 0),
                'artifacts': m.get('artifact_summary', {}).get('total', 0),
                'topics': m.get('topics', [])[:3],
                'had_failure': m.get('had_failure', False),
            })

    if not all_metrics:
        return {}

    n = len(all_metrics)

    # Collect values for range analysis
    durations = [m.get('duration_seconds', 0) for m in all_metrics]
    costs = [m.get('usage', {}).get('total_cost_usd', 0) for m in all_metrics]
    words = [m.get('total_words', 0) for m in all_metrics]

    # Failure and code artifact tracking
    failures = sum(1 for m in all_metrics if m.get('had_failure'))
    runs_with_code = sum(
        1 for m in all_metrics
        if any(a.get('type') == 'code' for a in m.get('artifacts', []))
    )

    # Words by turn position (conversation arc)
    turn_word_counts = []
    for m in all_metrics:
        turn_times = m.get('turn_times', [])
        turn_word_counts.append([t.get('words', 0) for t in turn_times])

    max_turns = max((len(tw) for tw in turn_word_counts), default=0)
    words_by_turn = []
    for i in range(max_turns):
        words_at_turn = [tw[i] for tw in turn_word_counts if i < len(tw)]
        if words_at_turn:
            words_by_turn.append({
                'turn': i + 1,
                'mean': round(sum(words_at_turn) / len(words_at_turn), 1),
                'min': min(words_at_turn),
                'max': max(words_at_turn),
            })

    return {
        'num_runs': n,
        'ranges': {
            'duration_seconds': {
                'min': round(min(durations), 1) if durations else 0,
                'max': round(max(durations), 1) if durations else 0,
            },
            'cost_usd': {
                'min': round(min(costs), 4) if costs else 0,
                'max': round(max(costs), 4) if costs else 0,
            },
            'words': {
                'min': min(words) if words else 0,
                'max': max(words) if words else 0,
            },
        },
        'words_by_turn': words_by_turn,
        'failures': failures,
        'runs_with_code': runs_with_code,
        'runs': run_summaries,
    }


def analyze_runset(runset_dir: Path, output_file: Path | None = None) -> dict:
    """
    Analyze a runset directory and optionally save results.

    Args:
        runset_dir: Path to runset directory containing run_* subdirectories
        output_file: Optional path to save JSON output

    Returns:
        Analysis results dict
    """
    run_dirs = sorted([
        d for d in runset_dir.iterdir()
        if d.is_dir() and d.name.startswith("run_")
    ])

    if not run_dirs:
        return {}

    analysis = analyze_runs(run_dirs)

    if output_file and analysis:
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)

    return analysis


def print_report(analysis: dict) -> None:
    """Print a human-readable summary of analysis results."""
    if not analysis:
        print("No analysis data.")
        return

    print("=" * 60)
    print("DETAILED ANALYSIS")
    print("=" * 60)
    print(f"Runs analyzed: {analysis['num_runs']}")
    print()

    # Ranges
    ranges = analysis.get('ranges', {})
    print("RANGES")
    print("-" * 40)
    dur = ranges.get('duration_seconds', {})
    print(f"  Duration: {dur.get('min', 0)}s - {dur.get('max', 0)}s")
    cost = ranges.get('cost_usd', {})
    print(f"  Cost: ${cost.get('min', 0):.4f} - ${cost.get('max', 0):.4f}")
    words = ranges.get('words', {})
    print(f"  Words: {words.get('min', 0)} - {words.get('max', 0)}")
    print()

    # Words by turn
    wbt = analysis.get('words_by_turn', [])
    if wbt:
        print("WORDS BY TURN (conversation arc)")
        print("-" * 40)
        for t in wbt:
            bar_len = int(t['mean'] / 20)
            bar = '▓' * bar_len
            print(f"  Turn {t['turn']:2}: {t['mean']:5.0f} (range: {t['min']}-{t['max']}) {bar}")
        print()

    # Failures and code
    print("RUN OUTCOMES")
    print("-" * 40)
    print(f"  Failures: {analysis.get('failures', 0)} / {analysis['num_runs']}")
    print(f"  Runs with code artifacts: {analysis.get('runs_with_code', 0)}")
    print()

    # Per-run summary
    runs = analysis.get('runs', [])
    if runs:
        print("INDIVIDUAL RUNS")
        print("-" * 40)
        for r in runs:
            topics = ', '.join(r.get('topics', [])) or '(none)'
            status = ' [FAILED]' if r.get('had_failure') else ''
            print(f"  {r['name']}: {r['duration_seconds']}s, {r['words']} words, "
                  f"{r['artifacts']} artifacts{status}")
            print(f"    topics: {topics}")
        print()

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Claude Code conversation experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python analyze.py experiment_runs/runset_2026-01-16/
    python analyze.py experiment_runs/
    python analyze.py --output analysis.json experiment_runs/runset_*/
    python analyze.py --quiet --output out.json path/   # JSON only, no report
        """,
    )

    parser.add_argument("paths", nargs="+", type=Path, help="Paths to search for runs")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file path")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress report output")

    args = parser.parse_args()

    # Find all runs across all provided paths
    all_run_dirs = []
    for path in args.paths:
        if path.exists():
            all_run_dirs.extend(find_runs(path))

    if not all_run_dirs:
        print("No runs found.")
        return

    if not args.quiet:
        print(f"Found {len(all_run_dirs)} runs")

    # Analyze
    analysis = analyze_runs(all_run_dirs)

    # Print report unless quiet
    if not args.quiet:
        print_report(analysis)

    # Save if output specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
        if not args.quiet:
            print(f"Analysis saved to: {args.output}")


if __name__ == "__main__":
    main()
