#!/usr/bin/env python3
"""
CodebaseGPT - Main Entry Point

A comprehensive codebase analysis tool that provides insights into
architectural patterns, code quality, and improvement opportunities.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent))

from core.analyzer import CodebaseAnalyzer, AnalysisResult
from analyzers.structure_analyzer import StructureAnalyzer
from analyzers.pattern_detector import PatternDetector

def create_analyzer_with_modules(codebase_path: Path) -> CodebaseAnalyzer:
    """Create a fully configured analyzer with all modules."""
    analyzer = CodebaseAnalyzer(codebase_path)

    # Initialize analysis modules
    analyzer.structure_analyzer = StructureAnalyzer(codebase_path)
    analyzer.pattern_detector = PatternDetector()

    return analyzer

def format_analysis_results(result: AnalysisResult) -> Dict[str, Any]:
    """Format analysis results for display."""
    return {
        'summary': {
            'total_files': len(result.structure.get('files', {})),
            'patterns_found': len(result.patterns),
            'insights_generated': len(result.insights),
            'overall_metrics': result.metrics
        },
        'structure': {
            'layers': result.structure.get('layers', {}),
            'dependency_stats': {
                'total_dependencies': result.structure.get('metrics', {}).get('total_dependencies', 0),
                'avg_per_file': result.structure.get('metrics', {}).get('avg_dependencies_per_file', 0)
            }
        },
        'patterns': [
            {
                'name': pattern.name,
                'type': pattern.pattern_type.value,
                'confidence': pattern.confidence,
                'impact': pattern.impact,
                'affected_files': len(pattern.files),
                'description': pattern.description,
                'recommendation': pattern.recommendation
            }
            for pattern in result.patterns
        ],
        'insights': result.insights,
        'documentation': result.documentation
    }

def print_analysis_summary(formatted_results: Dict[str, Any]):
    """Print a human-readable analysis summary."""
    print("\n" + "="*60)
    print("🔍 CODEBASE ANALYSIS RESULTS")
    print("="*60)

    summary = formatted_results['summary']
    print(f"\n📊 OVERVIEW:")
    print(f"   • Total files analyzed: {summary['total_files']}")
    print(f"   • Patterns detected: {summary['patterns_found']}")
    print(f"   • Insights generated: {summary['insights_generated']}")

    structure = formatted_results['structure']
    print(f"\n🏗️  ARCHITECTURE:")
    layers = structure['layers']
    for layer, files in layers.items():
        if files:
            print(f"   • {layer.title()} layer: {len(files)} files")

    deps = structure['dependency_stats']
    print(f"   • Total dependencies: {deps['total_dependencies']}")
    print(f"   • Avg dependencies per file: {deps['avg_per_file']:.1f}")

    patterns = formatted_results['patterns']
    if patterns:
        print(f"\n⚠️  PATTERNS & ISSUES:")
        for pattern in patterns[:5]:  # Show top 5
            impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            emoji = impact_emoji.get(pattern['impact'], '⚪')
            print(f"   {emoji} {pattern['name']} ({pattern['type']})")
            print(f"      Impact: {pattern['impact']}, Confidence: {pattern['confidence']:.1f}")
            print(f"      Files affected: {pattern['affected_files']}")
            print(f"      💡 {pattern['recommendation']}")
            print()

        if len(patterns) > 5:
            print(f"   ... and {len(patterns) - 5} more patterns")

    print("\n" + "="*60)

def main():
    """Main entry point for CodebaseGPT."""
    parser = argparse.ArgumentParser(
        description="CodebaseGPT - Intelligent Codebase Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s .                    # Analyze current directory
  %(prog)s /path/to/project     # Analyze specific project
  %(prog)s . --json output.json # Save results to JSON
  %(prog)s . --self-analyze     # Analyze CodebaseGPT itself
        """
    )

    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to the codebase to analyze (default: current directory)'
    )

    parser.add_argument(
        '--json',
        help='Save results to JSON file'
    )

    parser.add_argument(
        '--self-analyze',
        action='store_true',
        help='Analyze CodebaseGPT itself (meta-analysis)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Determine the target path
    if args.self_analyze:
        target_path = Path(__file__).parent
        print("🔬 Performing meta-analysis on CodebaseGPT itself...")
    else:
        target_path = Path(args.path).resolve()

    if not target_path.exists():
        print(f"❌ Error: Path '{target_path}' does not exist")
        sys.exit(1)

    if not target_path.is_dir():
        print(f"❌ Error: Path '{target_path}' is not a directory")
        sys.exit(1)

    print(f"🎯 Analyzing codebase: {target_path}")

    # Create and configure analyzer
    analyzer = create_analyzer_with_modules(target_path)

    # Perform analysis
    try:
        result = analyzer.analyze()
        formatted_results = format_analysis_results(result)

        # Display results
        if args.verbose:
            print(json.dumps(formatted_results, indent=2))
        else:
            print_analysis_summary(formatted_results)

        # Save to JSON if requested
        if args.json:
            with open(args.json, 'w') as f:
                json.dump(formatted_results, f, indent=2)
            print(f"\n💾 Results saved to: {args.json}")

        # Meta-analysis insights
        if args.self_analyze:
            print("\n🤖 META-ANALYSIS INSIGHTS:")
            print("   This analysis was performed by CodebaseGPT on its own codebase.")
            print("   Use these results to improve the tool's architecture and capabilities.")

            # Suggest improvements based on patterns found
            patterns = formatted_results['patterns']
            high_impact_patterns = [p for p in patterns if p['impact'] == 'high']

            if high_impact_patterns:
                print(f"\n🎯 PRIORITY IMPROVEMENTS:")
                for pattern in high_impact_patterns:
                    print(f"   • Address {pattern['name']} in {pattern['affected_files']} files")
                    print(f"     Recommendation: {pattern['recommendation']}")

    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()