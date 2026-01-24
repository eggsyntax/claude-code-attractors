#!/usr/bin/env python3
"""
Demo script to showcase the CodeViz analyzer capabilities.

This script demonstrates both the AST analysis and complexity metrics
by analyzing our own code.

Authors: Alice & Bob
"""

import sys
import json
from pathlib import Path

# Import our analyzer modules
from analyzer.core.ast_analyzer import CodeAnalyzer
from analyzer.metrics.complexity import ComplexityAnalyzer


def analyze_file_complete(file_path: str) -> dict:
    """
    Perform complete analysis of a Python file including structure and complexity.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        Dictionary with complete analysis results
    """
    # Basic structural analysis
    ast_analyzer = CodeAnalyzer()
    structural_results = ast_analyzer.analyze_file(file_path)

    if not structural_results:
        return {"error": f"Could not analyze {file_path}"}

    # Complexity analysis
    complexity_analyzer = ComplexityAnalyzer()
    tree = ast_analyzer.parse_file(file_path)

    if tree:
        complexity_results = complexity_analyzer.analyze_file_complexity(tree)
    else:
        complexity_results = {"error": "Could not parse file for complexity analysis"}

    # Combine results
    return {
        "file_path": file_path,
        "structural_analysis": structural_results,
        "complexity_analysis": complexity_results,
        "summary": create_analysis_summary(structural_results, complexity_results)
    }


def create_analysis_summary(structural: dict, complexity: dict) -> dict:
    """Create a high-level summary of the analysis."""
    summary = {
        "lines_of_code": structural.get("total_lines", 0),
        "total_functions": len(structural.get("functions", [])),
        "total_classes": len(structural.get("classes", [])),
        "total_imports": len(structural.get("imports", [])),
    }

    if "file_summary" in complexity:
        comp_summary = complexity["file_summary"]
        summary.update({
            "avg_cyclomatic_complexity": round(comp_summary.get("average_cyclomatic", 0), 2),
            "avg_cognitive_complexity": round(comp_summary.get("average_cognitive", 0), 2),
            "high_complexity_functions": comp_summary.get("high_complexity_functions", 0),
        })

        # Calculate maintainability score (0-100)
        avg_cyclomatic = comp_summary.get("average_cyclomatic", 1)
        avg_cognitive = comp_summary.get("average_cognitive", 0)
        high_complexity_ratio = comp_summary.get("high_complexity_functions", 0) / max(summary["total_functions"], 1)

        maintainability = max(0, min(100, 100 - (avg_cyclomatic * 5) - (avg_cognitive * 3) - (high_complexity_ratio * 30)))
        summary["maintainability_score"] = round(maintainability, 1)

    return summary


def print_analysis_report(analysis: dict) -> None:
    """Print a nicely formatted analysis report."""
    print("\n" + "=" * 60)
    print(f"CODEVIZ ANALYSIS REPORT")
    print("=" * 60)

    if "error" in analysis:
        print(f"ERROR: {analysis['error']}")
        return

    print(f"File: {analysis['file_path']}")
    print(f"Analyzed by: Alice & Bob's CodeViz Tool")
    print("-" * 60)

    # Summary section
    summary = analysis.get("summary", {})
    print("SUMMARY:")
    print(f"  Lines of Code: {summary.get('lines_of_code', 0)}")
    print(f"  Functions: {summary.get('total_functions', 0)}")
    print(f"  Classes: {summary.get('total_classes', 0)}")
    print(f"  Imports: {summary.get('total_imports', 0)}")
    print(f"  Avg Cyclomatic Complexity: {summary.get('avg_cyclomatic_complexity', 0)}")
    print(f"  Avg Cognitive Complexity: {summary.get('avg_cognitive_complexity', 0)}")
    print(f"  High Complexity Functions: {summary.get('high_complexity_functions', 0)}")
    print(f"  Maintainability Score: {summary.get('maintainability_score', 0)}/100")

    # Function details
    structural = analysis.get("structural_analysis", {})
    complexity = analysis.get("complexity_analysis", {})

    if "functions" in complexity:
        print("\nFUNCTION COMPLEXITY DETAILS:")
        for func in complexity["functions"]:
            rating = func.get("complexity_rating", "Unknown")
            print(f"  {func.get('function_name', 'unknown')}:")
            print(f"    Cyclomatic: {func.get('cyclomatic_complexity', 0)}")
            print(f"    Cognitive: {func.get('cognitive_complexity', 0)}")
            print(f"    Nesting: {func.get('max_nesting_level', 0)}")
            print(f"    Rating: {rating}")
            if rating.startswith("High") or rating.startswith("Very High"):
                print(f"    ⚠️  Consider refactoring this function")

    # Class details
    if structural.get("classes"):
        print("\nCLASSES:")
        for cls in structural["classes"]:
            methods = cls.get("methods", [])
            print(f"  {cls.get('name', 'unknown')}: {len(methods)} methods")

    # Import analysis
    if structural.get("imports"):
        print(f"\nIMPORTS: {len(structural['imports'])} modules imported")

    print("\n" + "=" * 60)


def main():
    """Main demo function."""
    print("CodeViz Demo - Collaborative Code Analysis Tool")
    print("Built by Alice & Bob")

    # Demo files to analyze
    demo_files = [
        "analyzer/core/ast_analyzer.py",
        "analyzer/metrics/complexity.py",
        "demo.py"  # Analyze ourselves!
    ]

    for file_path in demo_files:
        if Path(file_path).exists():
            print(f"\n🔍 Analyzing {file_path}...")
            analysis = analyze_file_complete(file_path)
            print_analysis_report(analysis)
        else:
            print(f"\n❌ File not found: {file_path}")

    print("\n🎉 Demo complete! The analyzer successfully analyzed itself.")
    print("This demonstrates the meta-capability we built together!")


if __name__ == "__main__":
    main()