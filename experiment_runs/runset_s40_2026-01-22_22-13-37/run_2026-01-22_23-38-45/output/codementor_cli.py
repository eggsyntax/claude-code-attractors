#!/usr/bin/env python3
"""
CodeMentor CLI - Command Line Interface for the Collaborative Code Review Assistant

This CLI provides easy access to CodeMentor's code analysis capabilities,
allowing developers to quickly analyze files and projects for patterns,
architectural insights, and improvement suggestions.

Usage:
    python codementor_cli.py analyze file.py
    python codementor_cli.py analyze-project /path/to/project
    python codementor_cli.py --help

Author: Alice (Claude Code Instance)
Collaboration Partner: Bob (Claude Code Instance)
"""

import argparse
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Import our core analysis engine
from codementor_core import CodeAnalysisEngine, CodePattern


def format_pattern_output(pattern: CodePattern, show_details: bool = True) -> str:
    """Format a code pattern for console output."""
    output = []

    # Main pattern info with color coding
    confidence_indicator = "🟢" if pattern.confidence >= 0.8 else "🟡" if pattern.confidence >= 0.6 else "🟠"
    output.append(f"{confidence_indicator} {pattern.name}")
    output.append(f"   Location: {pattern.file_path}:{pattern.line_start}-{pattern.line_end}")
    output.append(f"   Description: {pattern.description}")
    output.append(f"   Confidence: {pattern.confidence:.1%}")

    if show_details:
        output.append(f"   📚 Context: {pattern.educational_context}")
        if pattern.suggestions:
            output.append("   💡 Suggestions:")
            for suggestion in pattern.suggestions[:3]:  # Limit to top 3 suggestions
                output.append(f"      • {suggestion}")

    return "\n".join(output)


def analyze_file_command(args):
    """Handle the analyze file command."""
    file_path = args.file

    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found")
        return 1

    if not file_path.endswith('.py'):
        print(f"⚠️  Warning: '{file_path}' is not a Python file. Analysis may be limited.")

    print(f"🔍 Analyzing file: {file_path}")
    print("=" * 60)

    engine = CodeAnalysisEngine()
    result = engine.analyze_file(file_path)

    if 'error' in result:
        print(f"❌ Error analyzing file: {result['error']}")
        return 1

    # Display patterns
    patterns = result.get('patterns', [])
    if patterns:
        print(f"\n📋 Found {len(patterns)} pattern(s):")
        print("-" * 40)

        for i, pattern in enumerate(patterns, 1):
            print(f"\n{i}. {format_pattern_output(pattern, show_details=not args.brief)}")
    else:
        print("\n✅ No concerning patterns detected!")

    # Display metrics
    metrics = result.get('metrics', {})
    if metrics and not args.brief:
        print(f"\n📊 Code Metrics:")
        print("-" * 20)
        print(f"   Total lines: {metrics.get('total_lines', 'N/A')}")
        print(f"   Classes: {metrics.get('classes', 'N/A')}")
        print(f"   Functions: {metrics.get('functions', 'N/A')}")
        print(f"   Cyclomatic Complexity: {metrics.get('cyclomatic_complexity', 'N/A')}")

        if metrics.get('cyclomatic_complexity', 0) > 10:
            print("   ⚠️  High complexity detected - consider refactoring")

    # Export results if requested
    if args.output:
        engine.export_results(result, args.output)
        print(f"\n💾 Results exported to: {args.output}")

    print("\n" + "=" * 60)
    return 0


def analyze_project_command(args):
    """Handle the analyze project command."""
    project_path = args.project

    if not os.path.exists(project_path):
        print(f"❌ Error: Project directory '{project_path}' not found")
        return 1

    if not os.path.isdir(project_path):
        print(f"❌ Error: '{project_path}' is not a directory")
        return 1

    print(f"🔍 Analyzing project: {project_path}")
    print("=" * 60)

    engine = CodeAnalysisEngine()

    # Show progress for large projects
    print("⏳ Scanning Python files...")

    results = engine.analyze_project(project_path)

    files_count = len(results['files_analyzed'])
    print(f"✅ Analyzed {files_count} Python files")

    # Summary of patterns found
    patterns_summary = results.get('patterns_summary', {})
    if patterns_summary:
        print(f"\n📋 Pattern Summary:")
        print("-" * 30)
        total_patterns = sum(patterns_summary.values())
        print(f"   Total patterns detected: {total_patterns}")

        for pattern_name, count in sorted(patterns_summary.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {pattern_name}: {count}")

    # Architectural insights
    insights = results.get('architectural_insights', [])
    if insights and not args.brief:
        print(f"\n🏗️  Architectural Insights:")
        print("-" * 35)

        for insight in insights:
            impact_emoji = "🔴" if insight.impact_level == "high" else "🟡" if insight.impact_level == "medium" else "🟢"
            print(f"\n   {impact_emoji} {insight.pattern_type}")
            print(f"      {insight.description}")
            if insight.recommendations:
                print("      Recommendations:")
                for rec in insight.recommendations[:2]:
                    print(f"      • {rec}")

    # Project recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        print(f"\n💡 Project Recommendations:")
        print("-" * 35)

        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

    if not patterns_summary and not insights and not recommendations:
        print("\n✅ Great! No major issues detected in the project.")

    # Export results if requested
    if args.output:
        # Generate a timestamped filename if output is a directory
        if os.path.isdir(args.output):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = os.path.basename(os.path.abspath(project_path))
            output_file = os.path.join(args.output, f"codementor_analysis_{project_name}_{timestamp}.json")
        else:
            output_file = args.output

        engine.export_results(results, output_file)
        print(f"\n💾 Detailed results exported to: {output_file}")

    print("\n" + "=" * 60)
    return 0


def create_config_command(args):
    """Create a configuration file for CodeMentor."""
    config = {
        "analysis": {
            "max_method_lines": 50,
            "max_class_methods": 20,
            "max_complexity": 10,
            "ignore_patterns": [
                "test_*.py",
                "*_test.py",
                "conftest.py"
            ]
        },
        "output": {
            "format": "console",  # "console", "json", "html"
            "detail_level": "normal",  # "brief", "normal", "detailed"
            "show_suggestions": True,
            "show_metrics": True
        },
        "collaboration": {
            "enable_sharing": False,
            "team_rules": [],
            "review_templates": []
        }
    }

    config_file = args.output or "codementor_config.json"

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configuration file created: {config_file}")
    print("Edit this file to customize CodeMentor's behavior")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CodeMentor - Collaborative Code Review Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze myfile.py                 # Analyze a single file
  %(prog)s analyze-project ./my-project      # Analyze entire project
  %(prog)s analyze myfile.py --brief         # Brief output
  %(prog)s analyze-project ./src --output results.json  # Export results

For more information, visit: https://github.com/codementor-project
        """
    )

    parser.add_argument('--version', action='version', version='CodeMentor 0.1.0 (Alpha)')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Analyze file command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a single Python file',
        description='Analyze a single Python file for patterns and issues'
    )
    analyze_parser.add_argument('file', help='Path to the Python file to analyze')
    analyze_parser.add_argument('--brief', action='store_true',
                               help='Show brief output without detailed suggestions')
    analyze_parser.add_argument('--output', '-o',
                               help='Export results to JSON file')

    # Analyze project command
    project_parser = subparsers.add_parser(
        'analyze-project',
        help='Analyze an entire project directory',
        description='Analyze all Python files in a project directory'
    )
    project_parser.add_argument('project', help='Path to the project directory')
    project_parser.add_argument('--brief', action='store_true',
                               help='Show brief summary without detailed insights')
    project_parser.add_argument('--output', '-o',
                               help='Export results to JSON file or directory')

    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Create a configuration file',
        description='Generate a configuration file for customizing CodeMentor'
    )
    config_parser.add_argument('--output', '-o',
                              help='Configuration file path (default: codementor_config.json)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == 'analyze':
            return analyze_file_command(args)
        elif args.command == 'analyze-project':
            return analyze_project_command(args)
        elif args.command == 'config':
            return create_config_command(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1

    except KeyboardInterrupt:
        print("\n\n⏹️  Analysis interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())