#!/usr/bin/env python3
"""
Cross-run analysis for Claude Code conversation experiments.

Scans a directory for experiment runs, aggregates metrics, and generates reports.

Usage:
    python analyze.py experiment_runs/                        # Analyze all runs
    python analyze.py experiment_runs/run_2026-01-16_15-00-00 # Single run
    python analyze.py experiment_runs/runset_2026-01-16/      # Analyze a runset
    python analyze.py .                                       # Scan current dir
"""

import json
import argparse
from pathlib import Path
from collections import Counter
from datetime import datetime


def is_run_dir(path: Path) -> bool:
    """Check if a directory is a run (has metrics.json)."""
    return path.is_dir() and (path / "metrics.json").exists()


def find_runs(search_path: Path) -> list[Path]:
    """
    Find all experiment runs in the given path.

    Handles:
    - Single run directory (has metrics.json)
    - Directory containing runs (experiment_runs/)
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


def find_analysis_dir(search_paths: list[Path], runs: list[Path]) -> Path:
    """
    Determine the appropriate directory for analysis output.

    - User pointed at a run directly: <run>/analysis/
    - User pointed at a directory containing run(s): <directory>/analysis/
    """
    if not search_paths:
        return Path("analysis")

    # Check if user pointed directly at a run
    first_path = search_paths[0]
    if is_run_dir(first_path):
        return first_path / "analysis"

    # User pointed at a container directory - use that
    return first_path / "analysis"


def load_run(run_path: Path) -> dict | None:
    """Load metrics and params from a run directory."""
    metrics_file = run_path / "metrics.json"
    params_file = run_path / "params.json"

    if not metrics_file.exists():
        return None

    try:
        with open(metrics_file) as f:
            metrics = json.load(f)
        params = {}
        if params_file.exists():
            with open(params_file) as f:
                params = json.load(f)

        return {
            'path': str(run_path),
            'name': run_path.name,
            'params': params,
            'metrics': metrics,
        }
    except Exception as e:
        print(f"Warning: Could not load {run_path}: {e}")
        return None


def aggregate_metrics(runs: list[dict]) -> dict:
    """Aggregate metrics across multiple runs."""
    if not runs:
        return {}

    # Collect all values
    durations = []
    total_words = []
    costs = []
    all_topics = []
    artifact_counts = []
    artifact_types = Counter()
    code_runs = 0
    failures = 0

    turn_word_counts = []  # List of lists, one per run

    for run in runs:
        m = run['metrics']
        durations.append(m.get('duration_seconds', 0))
        total_words.append(m.get('total_words', 0))
        costs.append(m.get('usage', {}).get('total_cost_usd', 0))
        all_topics.extend(m.get('topics', []))

        artifacts = m.get('artifacts', [])
        artifact_counts.append(len(artifacts))
        for a in artifacts:
            artifact_types[a.get('type', 'other')] += 1
            if a.get('type') == 'code':
                code_runs += 1

        if m.get('had_failure'):
            failures += 1

        # Turn-by-turn word counts
        turn_times = m.get('turn_times', [])
        turn_word_counts.append([t.get('words', 0) for t in turn_times])

    # Compute averages
    n = len(runs)

    # Topic frequency
    topic_counts = Counter(all_topics)

    # Turn length evolution (average words per turn position across runs)
    max_turns = max(len(tw) for tw in turn_word_counts) if turn_word_counts else 0
    avg_words_by_turn = []
    for i in range(max_turns):
        words_at_turn = [tw[i] for tw in turn_word_counts if i < len(tw)]
        if words_at_turn:
            avg_words_by_turn.append(round(sum(words_at_turn) / len(words_at_turn), 1))

    return {
        'num_runs': n,
        'duration': {
            'mean': round(sum(durations) / n, 1) if n else 0,
            'min': round(min(durations), 1) if durations else 0,
            'max': round(max(durations), 1) if durations else 0,
            'total': round(sum(durations), 1),
        },
        'cost': {
            'mean': round(sum(costs) / n, 4) if n else 0,
            'min': round(min(costs), 4) if costs else 0,
            'max': round(max(costs), 4) if costs else 0,
            'total': round(sum(costs), 4),
        },
        'words': {
            'mean': round(sum(total_words) / n, 1) if n else 0,
            'min': min(total_words) if total_words else 0,
            'max': max(total_words) if total_words else 0,
        },
        'words_by_turn': avg_words_by_turn,
        'topics': {
            'all': topic_counts.most_common(50),
            'top_10': topic_counts.most_common(10),
        },
        'artifacts': {
            'mean': round(sum(artifact_counts) / n, 1) if n else 0,
            'total': sum(artifact_counts),
            'by_type': dict(artifact_types.most_common()),
            'runs_with_code': code_runs,
        },
        'failures': failures,
    }


def generate_word_cloud_text(topic_counts: list[tuple[str, int]]) -> str:
    """Generate ASCII word cloud representation."""
    if not topic_counts:
        return "  (no topics extracted)"

    max_count = max(count for _, count in topic_counts)
    lines = []

    for word, count in topic_counts[:20]:
        # Scale bar length
        bar_len = int((count / max_count) * 30)
        bar = '█' * bar_len
        lines.append(f"  {word:20} {bar} ({count})")

    return '\n'.join(lines)


def generate_report(runs: list[dict], agg: dict) -> str:
    """Generate a human-readable report."""
    lines = [
        "=" * 70,
        "CLAUDE CODE EXPERIMENT ANALYSIS",
        "=" * 70,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Runs analyzed: {agg['num_runs']}",
        "",
    ]

    # Duration
    lines.extend([
        "DURATION",
        "-" * 40,
        f"  Total: {agg['duration']['total']}s ({agg['duration']['total']/60:.1f} min)",
        f"  Mean per run: {agg['duration']['mean']}s",
        f"  Range: {agg['duration']['min']}s - {agg['duration']['max']}s",
        "",
    ])

    # Cost
    if agg.get('cost', {}).get('total', 0) > 0:
        lines.extend([
            "COST (USD)",
            "-" * 40,
            f"  Total: ${agg['cost']['total']:.4f}",
            f"  Mean per run: ${agg['cost']['mean']:.4f}",
            f"  Range: ${agg['cost']['min']:.4f} - ${agg['cost']['max']:.4f}",
            "",
        ])

    # Words
    lines.extend([
        "WORD COUNTS",
        "-" * 40,
        f"  Mean per run: {agg['words']['mean']}",
        f"  Range: {agg['words']['min']} - {agg['words']['max']}",
        "",
    ])

    # Turn length evolution
    if agg['words_by_turn']:
        lines.extend([
            "WORDS BY TURN (average across runs)",
            "-" * 40,
        ])
        for i, w in enumerate(agg['words_by_turn']):
            bar_len = int(w / 20)  # Scale
            bar = '▓' * bar_len
            lines.append(f"  Turn {i+1:2}: {w:5.0f} {bar}")
        lines.append("")

    # Artifacts
    lines.extend([
        "ARTIFACTS",
        "-" * 40,
        f"  Total created: {agg['artifacts']['total']}",
        f"  Mean per run: {agg['artifacts']['mean']}",
        f"  Runs with code: {agg['artifacts']['runs_with_code']}",
        "  By type:",
    ])
    for type_name, count in agg['artifacts']['by_type'].items():
        lines.append(f"    {type_name}: {count}")
    lines.append("")

    # Topics
    lines.extend([
        "TOPICS (word cloud)",
        "-" * 40,
        generate_word_cloud_text(agg['topics']['all']),
        "",
    ])

    # Failures
    if agg['failures'] > 0:
        lines.extend([
            "FAILURES",
            "-" * 40,
            f"  Runs with failures: {agg['failures']} / {agg['num_runs']}",
            "",
        ])

    # Individual runs summary
    lines.extend([
        "INDIVIDUAL RUNS",
        "-" * 40,
    ])
    for run in runs:
        m = run['metrics']
        topics = ', '.join(m.get('topics', [])[:3]) or '(none)'
        artifacts = m.get('artifact_summary', {}).get('total', 0)
        duration = m.get('duration_seconds', 0)
        lines.append(f"  {run['name']}: {duration}s, {artifacts} artifacts, topics: {topics}")

    lines.append("")
    lines.append("=" * 70)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Claude Code conversation experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python analyze.py experiment_runs/
    python analyze.py experiment_runs/run_2026-01-16_15-00-00
    python analyze.py --no-save experiment_runs/   # Print only, don't save
        """,
    )

    parser.add_argument("paths", nargs="+", type=Path, help="Paths to search for runs")
    parser.add_argument("--no-save", action="store_true", help="Don't save output files")
    parser.add_argument("--output-dir", type=Path, help="Override output directory")

    args = parser.parse_args()

    # Find all runs
    all_runs = []
    run_paths = []
    for path in args.paths:
        if path.exists():
            runs = find_runs(path)
            run_paths.extend(runs)
            for run_path in runs:
                run_data = load_run(run_path)
                if run_data:
                    all_runs.append(run_data)

    if not all_runs:
        print("No runs found.")
        return

    print(f"Found {len(all_runs)} runs")

    # Aggregate
    agg = aggregate_metrics(all_runs)

    # Generate report
    report = generate_report(all_runs, agg)
    print(report)

    # Save outputs
    if not args.no_save:
        # Determine output directory
        if args.output_dir:
            analysis_dir = args.output_dir
        else:
            analysis_dir = find_analysis_dir(args.paths, run_paths)

        analysis_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamp for this analysis
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Save report
        report_path = analysis_dir / f"report_{timestamp}.txt"
        report_path.write_text(report)
        print(f"\nReport saved to: {report_path}")

        # Save JSON metrics
        json_path = analysis_dir / f"metrics_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(agg, f, indent=2)
        print(f"Metrics saved to: {json_path}")


if __name__ == "__main__":
    main()
