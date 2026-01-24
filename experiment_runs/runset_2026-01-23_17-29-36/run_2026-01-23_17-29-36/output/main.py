#!/usr/bin/env python3
"""
Collaborative Code Analysis Tool - Main Orchestrator
Created by Bob and Alice (Claude Code instances)

This tool demonstrates AI collaboration by combining different analytical perspectives
on code quality, performance, and security.
"""

import os
import sys
import argparse
from pathlib import Path
from analyzer_bob import BobAnalyzer
from analyzer_alice import AliceAnalyzer
from synthesis import CollaborativeSynthesis
from reporter import CollaborativeReporter


def analyze_file(file_path: str, verbose: bool = False) -> dict:
    """
    Orchestrates collaborative analysis of a single file.

    Args:
        file_path: Path to the Python file to analyze
        verbose: Whether to show detailed progress

    Returns:
        Dictionary containing analysis results and collaboration metrics
    """
    if verbose:
        print(f"📁 Analyzing: {file_path}")

    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        return {"error": f"Could not read file: {e}"}

    # Initialize analyzers
    bob_analyzer = BobAnalyzer()
    alice_analyzer = AliceAnalyzer()
    synthesizer = CollaborativeSynthesis()

    if verbose:
        print("🤖 Bob analyzing performance and security...")
    bob_findings = bob_analyzer.analyze(code, file_path)

    if verbose:
        print("🤖 Alice analyzing design and quality...")
    alice_findings = alice_analyzer.analyze(code, file_path)

    if verbose:
        print("🔄 Synthesizing collaborative insights...")
    synthesis_result = synthesizer.synthesize_findings(
        bob_findings, alice_findings, file_path
    )

    return {
        "file_path": file_path,
        "bob_findings": bob_findings,
        "alice_findings": alice_findings,
        "synthesis": synthesis_result,
        "collaboration_metrics": synthesizer.get_collaboration_metrics()
    }


def analyze_directory(directory_path: str, verbose: bool = False) -> list:
    """
    Recursively analyzes all Python files in a directory.

    Args:
        directory_path: Path to directory to analyze
        verbose: Whether to show detailed progress

    Returns:
        List of analysis results for each file
    """
    results = []
    python_files = list(Path(directory_path).rglob("*.py"))

    if verbose:
        print(f"🔍 Found {len(python_files)} Python files to analyze")

    for file_path in python_files:
        result = analyze_file(str(file_path), verbose)
        if "error" not in result:
            results.append(result)
        elif verbose:
            print(f"⚠️  Skipped {file_path}: {result['error']}")

    return results


def main():
    """Main entry point for the collaborative code analyzer."""
    parser = argparse.ArgumentParser(
        description="Collaborative Code Analysis Tool by Bob & Alice",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py myfile.py                    # Analyze single file
  python main.py src/                         # Analyze directory
  python main.py --self-test                  # Analyze our own code
  python main.py myfile.py --verbose --html   # Detailed analysis with HTML report
        """
    )

    parser.add_argument(
        "target",
        nargs="?",
        help="File or directory to analyze"
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run analysis on our own code"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress information"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "html"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: stdout)"
    )

    args = parser.parse_args()

    # Determine what to analyze
    if args.self_test:
        target_path = "."  # Analyze current directory (our own code)
        if args.verbose:
            print("🔬 Running self-test: analyzing our own collaborative code analyzer")
    elif args.target:
        target_path = args.target
    else:
        parser.error("Please specify a target file/directory or use --self-test")

    # Perform analysis
    if os.path.isfile(target_path):
        results = [analyze_file(target_path, args.verbose)]
    else:
        results = analyze_directory(target_path, args.verbose)

    if not results:
        print("No Python files found to analyze.")
        return 1

    # Generate report
    reporter = CollaborativeReporter()

    if args.format == "json":
        report = reporter.generate_json_report(results)
    elif args.format == "html":
        report = reporter.generate_html_report(results)
    else:
        report = reporter.generate_text_report(results)

    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Report saved to: {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())