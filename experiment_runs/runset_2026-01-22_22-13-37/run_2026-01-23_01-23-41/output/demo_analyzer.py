#!/usr/bin/env python3
"""
Demo script showcasing the code analyzer capabilities
"""

import os
import json
from code_analyzer import CodeAnalyzer, AnalysisResult

def run_analysis_demo():
    """Run a comprehensive demo of the code analyzer"""
    print("🔍 Code Analysis Demo")
    print("=" * 50)

    analyzer = CodeAnalyzer()

    # Test files to analyze
    test_files = [
        "test_example.py",
        "javascript_example.js",
        "code_analyzer.py"
    ]

    results = []
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\nAnalyzing {file_path}...")
            result = analyzer.analyze_file(file_path)
            if result:
                results.append(result)
                print_analysis_highlights(result)
        else:
            print(f"⚠️ File not found: {file_path}")

    # Overall summary
    print("\n" + "=" * 50)
    print("📊 Overall Analysis Summary")
    print("=" * 50)

    if results:
        total_lines = sum(r.metrics.total_lines for r in results)
        total_functions = sum(r.metrics.function_count for r in results)
        total_classes = sum(r.metrics.class_count for r in results)
        avg_complexity = sum(r.metrics.complexity_score for r in results) / len(results)

        print(f"Files analyzed: {len(results)}")
        print(f"Total lines: {total_lines}")
        print(f"Total functions: {total_functions}")
        print(f"Total classes: {total_classes}")
        print(f"Average complexity: {avg_complexity:.1f}")

        # Language breakdown
        languages = {}
        for result in results:
            languages[result.language] = languages.get(result.language, 0) + 1

        print(f"\nLanguages detected:")
        for lang, count in languages.items():
            print(f"  • {lang}: {count} file(s)")

        # Complexity analysis
        print(f"\nComplexity Analysis:")
        for result in results:
            complexity_level = "Low" if result.metrics.complexity_score < 10 else \
                             "Medium" if result.metrics.complexity_score < 25 else "High"
            print(f"  • {os.path.basename(result.file_path)}: "
                  f"{result.metrics.complexity_score:.1f} ({complexity_level})")

        # Most complex functions
        print(f"\nFunction Analysis:")
        all_functions = []
        for result in results:
            for func in result.structure.get("functions", []):
                all_functions.append({
                    "name": func["name"],
                    "file": os.path.basename(result.file_path),
                    "args": func["args"],
                    "line": func["line"],
                    "is_async": func.get("is_async", False)
                })

        # Sort by argument count (parameter complexity indicator)
        all_functions.sort(key=lambda f: f["args"], reverse=True)

        print("Functions with most parameters:")
        for func in all_functions[:5]:  # Top 5
            async_indicator = " [async]" if func["is_async"] else ""
            print(f"  • {func['name']}() in {func['file']}: "
                  f"{func['args']} params{async_indicator} (line {func['line']})")

    print("\n✨ Analysis complete!")

def print_analysis_highlights(result: AnalysisResult):
    """Print key highlights from an analysis result"""
    metrics = result.metrics
    structure = result.structure

    print(f"  Language: {result.language}")
    print(f"  Lines of code: {metrics.lines_of_code}")
    print(f"  Functions: {metrics.function_count}")
    print(f"  Classes: {metrics.class_count}")
    print(f"  Complexity score: {metrics.complexity_score:.1f}")

    # Highlight async functions
    async_functions = [f for f in structure.get("functions", []) if f.get("is_async")]
    if async_functions:
        print(f"  Async functions: {len(async_functions)}")

    # Highlight high-parameter functions
    high_param_functions = [f for f in structure.get("functions", []) if f.get("args", 0) > 4]
    if high_param_functions:
        print(f"  Functions with >4 parameters: {len(high_param_functions)}")

    if result.errors:
        print(f"  ⚠️ Errors: {len(result.errors)}")

if __name__ == "__main__":
    run_analysis_demo()