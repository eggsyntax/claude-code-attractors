#!/usr/bin/env python3
"""
Main entry point for running Claude attractor experiments.

This script orchestrates conversations between two Claude instances and
analyzes the results for attractor behavior.

Usage:
    python run_experiment.py                    # Single run with defaults
    python run_experiment.py --turns 50         # Custom turn count
    python run_experiment.py --runs 5           # Multiple runs
    python run_experiment.py --model claude-opus-4-20250514  # Specific model
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from conversation import Conversation, ConversationConfig, print_progress
from analyzer import ConversationAnalyzer, save_analysis, print_analysis_summary
from visualizer import create_all_visualizations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def run_single_experiment(
    config: ConversationConfig,
    output_dir: Path,
    run_id: str,
    verbose: bool = True,
) -> dict:
    """
    Run a single conversation experiment.

    Args:
        config: Conversation configuration
        output_dir: Directory for output files
        run_id: Unique identifier for this run
        verbose: Whether to print progress

    Returns:
        Dictionary with experiment results
    """
    logger.info(f"Starting experiment run: {run_id}")
    logger.info(f"Model: {config.model}, Max turns: {config.max_turns}")

    # Create conversation
    conv = Conversation(config)

    # Run with progress callback if verbose
    callback = print_progress if verbose else None
    messages = conv.run(progress_callback=callback)

    # Save conversation
    conv_path = output_dir / "conversations" / f"{run_id}.json"
    conv.save(conv_path)
    logger.info(f"Conversation saved to {conv_path}")

    # Analyze conversation
    analyzer = ConversationAnalyzer(conv)
    analysis = analyzer.analyze()

    # Save analysis
    analysis_path = output_dir / "analysis" / f"{run_id}_analysis.json"
    save_analysis(analysis, analysis_path)
    logger.info(f"Analysis saved to {analysis_path}")

    # Print summary
    if verbose:
        print_analysis_summary(analysis)

    # Create visualizations
    viz_dir = output_dir / "visualizations"
    viz_files = create_all_visualizations(analysis, viz_dir, prefix=f"{run_id}_")
    logger.info(f"Created {len(viz_files)} visualization files")

    return {
        "run_id": run_id,
        "total_turns": analysis.total_turns,
        "attractor_detected": analysis.attractor_detected,
        "attractor_turn": analysis.attractor_turn,
        "final_phase": analysis.final_phase,
        "summary_stats": analysis.summary_stats,
        "conversation_path": str(conv_path),
        "analysis_path": str(analysis_path),
        "visualization_paths": [str(p) for p in viz_files],
    }


def run_experiment_batch(
    config: ConversationConfig,
    output_dir: Path,
    num_runs: int,
    verbose: bool = True,
) -> list[dict]:
    """
    Run multiple conversation experiments.

    Args:
        config: Base conversation configuration
        output_dir: Directory for output files
        num_runs: Number of experiments to run
        verbose: Whether to print detailed progress

    Returns:
        List of results from each run
    """
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i in range(num_runs):
        run_id = f"run_{timestamp}_{i + 1:03d}"
        logger.info(f"\n{'=' * 60}")
        logger.info(f"EXPERIMENT {i + 1}/{num_runs}")
        logger.info(f"{'=' * 60}")

        result = run_single_experiment(config, output_dir, run_id, verbose=verbose)
        results.append(result)

        # Print intermediate summary
        attractor_count = sum(1 for r in results if r["attractor_detected"])
        logger.info(f"\nRunning attractor detection rate: {attractor_count}/{len(results)}")

    return results


def print_batch_summary(results: list[dict]) -> None:
    """Print summary statistics across multiple runs."""
    print("\n" + "=" * 60)
    print("BATCH EXPERIMENT SUMMARY")
    print("=" * 60)

    num_runs = len(results)
    attractor_count = sum(1 for r in results if r["attractor_detected"])

    print(f"\nTotal runs: {num_runs}")
    print(f"Attractor detected: {attractor_count}/{num_runs} ({100 * attractor_count / num_runs:.1f}%)")

    # Phase distribution across all runs
    phase_counts = {}
    for r in results:
        phase = r["final_phase"]
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

    print("\nFinal phase distribution:")
    for phase, count in sorted(phase_counts.items(), key=lambda x: -x[1]):
        print(f"  {phase}: {count} ({100 * count / num_runs:.1f}%)")

    # Average attractor onset
    attractor_turns = [r["attractor_turn"] for r in results if r["attractor_turn"] is not None]
    if attractor_turns:
        avg_onset = sum(attractor_turns) / len(attractor_turns)
        print(f"\nAverage attractor onset turn: {avg_onset:.1f}")

    # Average scores
    avg_philosophical = sum(r["summary_stats"].get("avg_philosophical", 0) for r in results) / num_runs
    avg_gratitude = sum(r["summary_stats"].get("avg_gratitude", 0) for r in results) / num_runs
    avg_spiritual = sum(r["summary_stats"].get("avg_spiritual", 0) for r in results) / num_runs

    print("\nAverage phase scores across all runs:")
    print(f"  Philosophical: {avg_philosophical:.3f}")
    print(f"  Gratitude:     {avg_gratitude:.3f}")
    print(f"  Spiritual:     {avg_spiritual:.3f}")


def main():
    parser = argparse.ArgumentParser(
        description="Run Claude attractor experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_experiment.py                          # Single run, 30 turns
    python run_experiment.py --turns 50               # Single run, 50 turns
    python run_experiment.py --runs 5                 # 5 runs for statistical analysis
    python run_experiment.py --model claude-opus-4-20250514  # Use Opus model
    python run_experiment.py --quiet                  # Minimal output
        """,
    )

    parser.add_argument(
        "--turns",
        type=int,
        default=30,
        help="Number of conversation turns (default: 30)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of experiment runs (default: 1)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-20250514",
        help="Claude model to use (default: claude-sonnet-4-20250514)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity",
    )
    parser.add_argument(
        "--seed-message",
        type=str,
        default=None,
        help="Custom seed message to start the conversation",
    )

    args = parser.parse_args()

    # Build configuration
    config = ConversationConfig(
        model=args.model,
        max_turns=args.turns,
    )

    if args.seed_message:
        config.seed_message = args.seed_message

    output_dir = Path(args.output_dir)
    verbose = not args.quiet

    logger.info("=" * 60)
    logger.info("CLAUDE ATTRACTOR EXPERIMENT")
    logger.info("=" * 60)
    logger.info(f"Model: {config.model}")
    logger.info(f"Turns per conversation: {config.max_turns}")
    logger.info(f"Number of runs: {args.runs}")
    logger.info(f"Output directory: {output_dir}")

    # Run experiments
    if args.runs == 1:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"run_{timestamp}"
        run_single_experiment(config, output_dir, run_id, verbose=verbose)
    else:
        results = run_experiment_batch(config, output_dir, args.runs, verbose=verbose)
        print_batch_summary(results)

    logger.info("\nExperiment complete!")
    logger.info(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    main()
