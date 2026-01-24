#!/usr/bin/env python3
"""
Command-Line Interface for Collaborative Code Analyzer

This CLI provides a professional interface for running code analysis and
generating interactive visualization dashboards from the command line.

Features:
- Analyze individual files or entire project directories
- Generate interactive HTML dashboards
- Configurable complexity thresholds and analysis options
- Batch processing for large codebases
- Progress reporting and detailed output
- Integration-friendly JSON output option

Usage Examples:
    # Analyze a single file
    python cli.py analyze myfile.py

    # Analyze entire project with dashboard
    python cli.py analyze ./src --dashboard --output analysis.html

    # Batch process with custom thresholds
    python cli.py analyze ./project --batch --complexity-threshold 10

    # Generate JSON report for CI integration
    python cli.py analyze ./code --format json --output report.json

Authors: Alice & Bob (AI Collaboration)
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import webbrowser
import os

# Import our analysis modules
from ast_analyzer import CodeAnalyzer
from complexity_analyzer import ComplexityAnalyzer
from dashboard_generator import DashboardGenerator


class CodeAnalyzerCLI:
    """
    Professional command-line interface for the code analysis system.

    This class provides a comprehensive CLI that wraps our analysis tools
    in a user-friendly command-line interface suitable for professional
    development workflows and CI/CD integration.
    """

    def __init__(self):
        """Initialize the CLI with default analyzers."""
        self.code_analyzer = CodeAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.dashboard_generator = DashboardGenerator()

    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create and configure the argument parser for the CLI.

        Returns:
            argparse.ArgumentParser: Configured argument parser
        """
        parser = argparse.ArgumentParser(
            description="Interactive Code Analysis and Visualization Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s analyze myfile.py                          # Analyze single file
  %(prog)s analyze ./src --dashboard                  # Generate dashboard
  %(prog)s analyze ./project --batch --threshold 10  # Batch with custom threshold
  %(prog)s analyze ./code --format json              # JSON output for CI/CD

For more information, visit: https://github.com/ai-collaboration/code-analyzer
            """
        )

        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze Python code')
        analyze_parser.add_argument(
            'path',
            type=str,
            help='Path to Python file or directory to analyze'
        )
        analyze_parser.add_argument(
            '--dashboard',
            action='store_true',
            help='Generate interactive HTML dashboard'
        )
        analyze_parser.add_argument(
            '--output', '-o',
            type=str,
            help='Output file path (default: auto-generated based on input)'
        )
        analyze_parser.add_argument(
            '--format',
            choices=['text', 'json', 'html'],
            default='text',
            help='Output format (default: text)'
        )
        analyze_parser.add_argument(
            '--complexity-threshold',
            type=int,
            default=10,
            help='Complexity threshold for warnings (default: 10)'
        )
        analyze_parser.add_argument(
            '--batch',
            action='store_true',
            help='Enable batch processing mode for large codebases'
        )
        analyze_parser.add_argument(
            '--open',
            action='store_true',
            help='Automatically open HTML dashboard in browser'
        )
        analyze_parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )

        # Version command
        version_parser = subparsers.add_parser('version', help='Show version information')

        return parser

    def analyze_command(self, args) -> int:
        """
        Execute the analyze command with the given arguments.

        Args:
            args: Parsed command-line arguments

        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        path = Path(args.path)

        if not path.exists():
            print(f"Error: Path '{path}' does not exist", file=sys.stderr)
            return 1

        try:
            if args.verbose:
                print(f"🔍 Starting analysis of: {path}")
                print(f"📊 Complexity threshold: {args.complexity_threshold}")
                print(f"🎯 Output format: {args.format}")

            # Perform analysis
            if path.is_file():
                results = self._analyze_single_file(path, args)
            else:
                results = self._analyze_directory(path, args)

            # Generate output
            output_path = self._generate_output(results, args)

            if args.verbose:
                print(f"✅ Analysis complete!")
                if output_path:
                    print(f"📄 Results saved to: {output_path}")

            # Auto-open dashboard if requested
            if args.open and output_path and output_path.suffix == '.html':
                webbrowser.open(f"file://{output_path.absolute()}")

            return 0

        except Exception as e:
            print(f"Error during analysis: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    def _analyze_single_file(self, file_path: Path, args) -> Dict[str, Any]:
        """Analyze a single Python file."""
        if args.verbose:
            print(f"📝 Analyzing file: {file_path.name}")

        # Structural analysis
        structural_results = self.code_analyzer.analyze_file(str(file_path))

        # Complexity analysis
        complexity_results = self.complexity_analyzer.analyze_file(str(file_path))

        return {
            'type': 'single_file',
            'path': str(file_path),
            'structural': structural_results,
            'complexity': complexity_results,
            'summary': self._generate_summary(structural_results, complexity_results, args.complexity_threshold)
        }

    def _analyze_directory(self, dir_path: Path, args) -> Dict[str, Any]:
        """Analyze all Python files in a directory."""
        python_files = list(dir_path.rglob("*.py"))

        if not python_files:
            raise ValueError(f"No Python files found in {dir_path}")

        if args.verbose:
            print(f"📁 Found {len(python_files)} Python files to analyze")

        all_results = {
            'type': 'directory',
            'path': str(dir_path),
            'files': {},
            'summary': {'total_files': len(python_files)}
        }

        for i, file_path in enumerate(python_files, 1):
            if args.verbose:
                print(f"📝 [{i}/{len(python_files)}] Analyzing: {file_path.relative_to(dir_path)}")

            try:
                # Structural analysis
                structural = self.code_analyzer.analyze_file(str(file_path))
                complexity = self.complexity_analyzer.analyze_file(str(file_path))

                all_results['files'][str(file_path)] = {
                    'structural': structural,
                    'complexity': complexity
                }

            except Exception as e:
                if args.verbose:
                    print(f"⚠️  Warning: Could not analyze {file_path}: {e}")
                continue

        # Generate project summary
        all_results['summary'] = self._generate_project_summary(all_results['files'], args.complexity_threshold)

        return all_results

    def _generate_summary(self, structural: Dict, complexity: Dict, threshold: int) -> Dict[str, Any]:
        """Generate a summary of analysis results for a single file."""
        functions = structural.get('functions', [])
        classes = structural.get('classes', [])

        high_complexity_functions = [
            func for func in complexity.get('functions', [])
            if func.get('cyclomatic_complexity', 0) > threshold
        ]

        return {
            'function_count': len(functions),
            'class_count': len(classes),
            'import_count': len(structural.get('imports', [])),
            'high_complexity_functions': len(high_complexity_functions),
            'max_complexity': max(
                (func.get('cyclomatic_complexity', 0) for func in complexity.get('functions', [])),
                default=0
            ),
            'needs_attention': len(high_complexity_functions) > 0
        }

    def _generate_project_summary(self, files_data: Dict, threshold: int) -> Dict[str, Any]:
        """Generate a project-wide summary of analysis results."""
        total_functions = sum(
            len(data['structural'].get('functions', []))
            for data in files_data.values()
        )

        total_classes = sum(
            len(data['structural'].get('classes', []))
            for data in files_data.values()
        )

        high_complexity_count = sum(
            len([
                func for func in data['complexity'].get('functions', [])
                if func.get('cyclomatic_complexity', 0) > threshold
            ])
            for data in files_data.values()
        )

        max_complexity = max(
            (
                max(
                    (func.get('cyclomatic_complexity', 0) for func in data['complexity'].get('functions', [])),
                    default=0
                )
                for data in files_data.values()
            ),
            default=0
        )

        return {
            'total_files': len(files_data),
            'total_functions': total_functions,
            'total_classes': total_classes,
            'high_complexity_functions': high_complexity_count,
            'max_complexity': max_complexity,
            'complexity_ratio': high_complexity_count / max(total_functions, 1),
            'needs_attention': high_complexity_count > 0
        }

    def _generate_output(self, results: Dict[str, Any], args) -> Optional[Path]:
        """Generate the appropriate output based on format and options."""
        if args.format == 'text':
            self._print_text_summary(results, args.complexity_threshold)
            return None

        elif args.format == 'json':
            output_path = Path(args.output) if args.output else Path(f"{Path(results['path']).stem}_analysis.json")
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            return output_path

        elif args.format == 'html' or args.dashboard:
            output_path = Path(args.output) if args.output else Path(f"{Path(results['path']).stem}_dashboard.html")

            # Generate dashboard
            if results['type'] == 'single_file':
                # For single files, analyze the parent directory to get better context
                parent_dir = Path(results['path']).parent
                self.dashboard_generator.generate_dashboard(str(parent_dir), str(output_path))
            else:
                self.dashboard_generator.generate_dashboard(results['path'], str(output_path))

            return output_path

        return None

    def _print_text_summary(self, results: Dict[str, Any], threshold: int):
        """Print a formatted text summary of the analysis results."""
        print("\n" + "="*60)
        print("🔍 CODE ANALYSIS SUMMARY")
        print("="*60)

        if results['type'] == 'single_file':
            print(f"📄 File: {results['path']}")
            summary = results['summary']
        else:
            print(f"📁 Project: {results['path']}")
            summary = results['summary']

        print(f"📊 Functions: {summary['total_functions' if 'total_functions' in summary else 'function_count']}")
        print(f"🏗️  Classes: {summary['total_classes' if 'total_classes' in summary else 'class_count']}")

        if 'total_files' in summary:
            print(f"📁 Files analyzed: {summary['total_files']}")

        print(f"⚠️  High complexity functions: {summary['high_complexity_functions']}")
        print(f"📈 Maximum complexity: {summary['max_complexity']}")

        if summary.get('needs_attention', False):
            print(f"\n🚨 ATTENTION NEEDED:")
            print(f"   {summary['high_complexity_functions']} functions exceed complexity threshold ({threshold})")
            print(f"   Consider refactoring functions with complexity > {threshold}")
        else:
            print(f"\n✅ CODE QUALITY: Good")
            print(f"   All functions are below complexity threshold ({threshold})")

        print("="*60 + "\n")

    def version_command(self, args) -> int:
        """Show version information."""
        print("Collaborative Code Analyzer v1.0.0")
        print("Built by Alice & Bob (AI Collaboration)")
        print("MIT License")
        return 0

    def run(self, argv: Optional[List[str]] = None) -> int:
        """
        Run the CLI with the given arguments.

        Args:
            argv: Command-line arguments (defaults to sys.argv)

        Returns:
            int: Exit code
        """
        parser = self.create_parser()
        args = parser.parse_args(argv)

        if not args.command:
            parser.print_help()
            return 1

        if args.command == 'analyze':
            return self.analyze_command(args)
        elif args.command == 'version':
            return self.version_command(args)
        else:
            parser.print_help()
            return 1


def main():
    """Main entry point for the CLI."""
    cli = CodeAnalyzerCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()