#!/usr/bin/env python3
"""
Demo script showing both code analyzers in action.
Compares basic regex-based analysis with tree-sitter analysis.
"""

import os
import sys
from pathlib import Path

# Add current directory to path to import our analyzers
sys.path.insert(0, str(Path(__file__).parent))

try:
    from code_analyzer import CodeAnalyzer as BasicAnalyzer
    from tree_sitter_analyzer import TreeSitterAnalyzer, PatternDetector, AnalysisReporter
    ANALYZERS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    ANALYZERS_AVAILABLE = False


def demo_basic_analysis():
    """Demonstrate the basic regex-based code analyzer."""
    print("=" * 60)
    print("BASIC CODE ANALYZER DEMO")
    print("=" * 60)

    if not ANALYZERS_AVAILABLE:
        print("Analyzers not available - cannot run demo")
        return

    analyzer = BasicAnalyzer()
    current_dir = Path(__file__).parent

    # Analyze the example file
    example_file = current_dir / "example_code.py"
    if not example_file.exists():
        print(f"Example file not found: {example_file}")
        return

    print(f"Analyzing: {example_file.name}")
    metrics = analyzer.analyze_file(str(example_file))

    if metrics:
        print(f"Language: {metrics.language}")
        print(f"Lines of Code: {metrics.lines_of_code}")
        print(f"Functions: {metrics.function_count}")
        print(f"Classes: {metrics.class_count}")
        print(f"Imports: {metrics.import_count}")
        print(f"Comment Lines: {metrics.comment_lines}")
        print(f"Cyclomatic Complexity: {metrics.cyclomatic_complexity}")

        # Show detailed breakdown
        print(f"\nComment Ratio: {metrics.comment_lines / max(metrics.lines_of_code, 1):.2%}")

    # Analyze directory
    print(f"\n--- Directory Analysis ---")
    results = analyzer.analyze_directory(str(current_dir))
    summary = analyzer.generate_summary(results)

    print(f"Total Files: {summary.get('total_files', 0)}")
    print(f"Total Lines: {summary.get('total_lines', 0)}")

    for lang, stats in summary.get('languages', {}).items():
        print(f"\n{lang.upper()}:")
        print(f"  Files: {stats['files']}")
        print(f"  Lines: {stats['lines_of_code']}")
        print(f"  Functions: {stats['functions']}")
        print(f"  Avg Complexity: {stats['avg_complexity']:.1f}")


def demo_tree_sitter_analysis():
    """Demonstrate the advanced tree-sitter analyzer."""
    print("\n" + "=" * 60)
    print("TREE-SITTER ANALYZER DEMO")
    print("=" * 60)

    if not ANALYZERS_AVAILABLE:
        print("Analyzers not available - cannot run demo")
        return

    analyzer = TreeSitterAnalyzer()
    pattern_detector = PatternDetector()
    current_dir = Path(__file__).parent

    # Analyze the example file
    example_file = current_dir / "example_code.py"
    if not example_file.exists():
        print(f"Example file not found: {example_file}")
        return

    print(f"Analyzing: {example_file.name}")
    result = analyzer.analyze_file(example_file)

    if result:
        print(f"Language: {result.language}")
        print(f"Functions Found: {len(result.functions)}")
        print(f"Classes Found: {len(result.classes)}")
        print(f"Imports Found: {len(result.imports)}")
        print(f"AST Complexity Score: {result.ast_complexity_score}")
        print(f"Maintainability Index: {result.maintainability_index}")

        if result.parse_errors:
            print(f"Parse Errors: {', '.join(result.parse_errors)}")

        # Show function details
        print(f"\n--- Function Details ---")
        for func in result.functions[:5]:  # Show first 5 functions
            print(f"Function: {func.name}")
            print(f"  Lines {func.start_line}-{func.end_line} ({func.lines_of_code} LOC)")
            print(f"  Parameters: {func.parameter_count}")
            print(f"  Complexity: {func.cyclomatic_complexity}")
            print(f"  Nesting Depth: {func.nesting_depth}")
            print(f"  Return Points: {func.return_points}")
            if func.calls_made:
                print(f"  Calls: {', '.join(func.calls_made[:5])}{'...' if len(func.calls_made) > 5 else ''}")

        # Detect patterns
        print(f"\n--- Pattern Detection ---")
        enabled_patterns = {'complexity', 'naming', 'structure', 'security', 'maintainability'}
        patterns = pattern_detector.detect_patterns(result, enabled_patterns)

        if patterns:
            print(f"Found {len(patterns)} patterns:")
            for pattern in patterns[:10]:  # Show first 10
                severity_icon = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(pattern.severity, '⚪')

                print(f"  {severity_icon} [{pattern.severity.upper()}] Line {pattern.line_number}: {pattern.message}")
                if pattern.suggestion:
                    print(f"     💡 {pattern.suggestion}")
        else:
            print("No patterns detected")

        # Generate summary report
        print(f"\n--- Summary Report ---")
        reporter = AnalysisReporter()
        summary_report = reporter.generate_summary_report([result], patterns)
        print(summary_report)


def compare_analyzers():
    """Compare results from both analyzers."""
    print("\n" + "=" * 60)
    print("ANALYZER COMPARISON")
    print("=" * 60)

    if not ANALYZERS_AVAILABLE:
        print("Analyzers not available - cannot run comparison")
        return

    current_dir = Path(__file__).parent
    example_file = current_dir / "example_code.py"

    if not example_file.exists():
        print(f"Example file not found: {example_file}")
        return

    # Run both analyzers
    basic_analyzer = BasicAnalyzer()
    tree_analyzer = TreeSitterAnalyzer()

    basic_metrics = basic_analyzer.analyze_file(str(example_file))
    tree_result = tree_analyzer.analyze_file(example_file)

    if basic_metrics and tree_result:
        print("COMPARISON RESULTS:")
        print(f"{'Metric':<25} {'Basic':<10} {'Tree-sitter':<15} {'Difference'}")
        print("-" * 60)

        basic_funcs = basic_metrics.function_count
        tree_funcs = len(tree_result.functions)
        print(f"{'Functions':<25} {basic_funcs:<10} {tree_funcs:<15} {tree_funcs - basic_funcs:+d}")

        basic_classes = basic_metrics.class_count
        tree_classes = len(tree_result.classes)
        print(f"{'Classes':<25} {basic_classes:<10} {tree_classes:<15} {tree_classes - basic_classes:+d}")

        basic_complexity = basic_metrics.cyclomatic_complexity
        tree_complexity = tree_result.ast_complexity_score
        print(f"{'Complexity':<25} {basic_complexity:<10} {tree_complexity:<15.2f} {tree_complexity - basic_complexity:+.2f}")

        print(f"\nADVANTAGES OF TREE-SITTER ANALYSIS:")
        print("• More accurate function and class detection")
        print("• Detailed per-function metrics (parameters, nesting, etc.)")
        print("• Pattern detection and code quality insights")
        print("• Maintainability index calculation")
        print("• AST-based complexity analysis")
        print("• Precise syntax understanding")


def show_analysis_examples():
    """Show examples of what each analyzer can detect."""
    print("\n" + "=" * 60)
    print("ANALYSIS CAPABILITIES")
    print("=" * 60)

    examples = {
        "High Complexity": {
            "description": "Functions with high cyclomatic complexity",
            "example": "process_data() - 7+ decision points, multiple nested conditions"
        },
        "Deep Nesting": {
            "description": "Functions with excessive nesting depth",
            "example": "analyze_patterns() - nested if statements 4+ levels deep"
        },
        "Too Many Parameters": {
            "description": "Functions with parameter count > 7",
            "example": "process_data() - 7 parameters, hard to use and test"
        },
        "Security Issues": {
            "description": "Dangerous function usage",
            "example": "risky_function() - uses eval() and exec()"
        },
        "Naming Issues": {
            "description": "Poor function naming conventions",
            "example": "x() - too short and non-descriptive"
        },
        "Multiple Returns": {
            "description": "Functions with many return points",
            "example": "calculate_complex_metric() - 6 return statements"
        }
    }

    print("The tree-sitter analyzer can detect these patterns:\n")
    for pattern_name, info in examples.items():
        print(f"🔍 {pattern_name}")
        print(f"   {info['description']}")
        print(f"   Example: {info['example']}\n")


def main():
    """Main demo function."""
    print("CODE ANALYSIS TOOLS DEMONSTRATION")
    print("This demo shows two complementary approaches to code analysis:\n")
    print("1. Basic Analysis: Fast regex-based parsing for quick metrics")
    print("2. Tree-sitter Analysis: Precise AST-based analysis with pattern detection\n")

    try:
        # Run demonstrations
        demo_basic_analysis()
        demo_tree_sitter_analysis()
        compare_analyzers()
        show_analysis_examples()

        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("\nNext steps you could explore:")
        print("• Add support for more languages (Rust, Go, TypeScript)")
        print("• Integrate real tree-sitter parsers for more accuracy")
        print("• Add custom pattern detection rules")
        print("• Create IDE integrations or CI/CD plugins")
        print("• Build visualization dashboards for code metrics")
        print("• Add performance hotspot detection")

    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()