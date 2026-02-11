#!/usr/bin/env python3
"""
CodeCraft - Intelligent Code Analysis & Refactoring System
Built collaboratively by Alice & Bob (Claude Code instances)

Entry point for the CodeCraft system.
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core.analyzer import CodeAnalyzer
from core.reporter import Reporter
from utils.config import Config

console = Console()

def main():
    parser = argparse.ArgumentParser(
        description="CodeCraft: Intelligent Code Analysis & Refactoring System"
    )
    parser.add_argument("path", help="Path to analyze (file or directory)")
    parser.add_argument(
        "--language",
        choices=["python", "javascript", "java", "go", "auto"],
        default="auto",
        help="Target programming language (auto-detect by default)"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["console", "json", "html"],
        default="console",
        help="Output format"
    )
    parser.add_argument(
        "--rules", "-r",
        help="Path to custom rules configuration"
    )
    parser.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Minimum severity level to report"
    )

    args = parser.parse_args()

    # Display banner
    banner = Text("CodeCraft", style="bold blue")
    banner.append(" - AI-Powered Code Analysis", style="dim")
    console.print(Panel(banner, expand=False))

    # Initialize components
    config = Config(args.rules) if args.rules else Config()
    analyzer = CodeAnalyzer(config)
    reporter = Reporter(args.output)

    # Analyze code
    target_path = Path(args.path)
    if not target_path.exists():
        console.print(f"[red]Error: Path {args.path} does not exist[/red]")
        sys.exit(1)

    console.print(f"[green]Analyzing:[/green] {target_path}")

    try:
        results = analyzer.analyze(target_path, language=args.language)
        filtered_results = [r for r in results if r.severity_level >= config.get_severity_threshold(args.severity)]

        reporter.generate_report(filtered_results, target_path)

        console.print(f"\n[green]Analysis complete![/green] Found {len(filtered_results)} issues")

    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()