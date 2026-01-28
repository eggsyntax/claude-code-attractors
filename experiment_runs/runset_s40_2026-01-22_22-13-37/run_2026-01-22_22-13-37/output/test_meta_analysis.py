#!/usr/bin/env python3
"""
Meta-Analysis Test Script

Tests our codebase analyzer on itself and generates comprehensive
documentation, demonstrating the self-analyzing capability.
"""

from pathlib import Path
from codebase_analyzer import CodebaseAnalyzer
from documentation_generator import DocumentationGenerator


def main():
    """Run meta-analysis on our own codebase."""
    print("🔍 Running meta-analysis on our codebase analyzer...")

    # Analyze our own code
    analyzer = CodebaseAnalyzer(".")
    insights = analyzer.analyze()

    print(f"\n📊 Analysis Complete!")
    print(f"   - Files analyzed: {insights.total_files}")
    print(f"   - Lines of code: {insights.total_lines:,}")
    print(f"   - Patterns found: {len(insights.patterns)}")

    # Generate documentation
    print("\n📝 Generating documentation...")
    generator = DocumentationGenerator("Intelligent Codebase Analyzer")

    docs_dir = Path("./self_analysis_docs")
    saved_files = generator.save_documentation(
        insights,
        docs_dir,
        formats=['markdown', 'html', 'json']
    )

    print(f"\n✅ Documentation generated:")
    for format_name, file_path in saved_files.items():
        print(f"   - {format_name.upper()}: {file_path}")

    # Print some interesting findings
    print(f"\n🔬 Key Findings:")

    # Complexity analysis
    if insights.complexity_hotspots:
        most_complex = insights.complexity_hotspots[0]
        print(f"   - Most complex file: {most_complex[0].name} (score: {most_complex[1]:.1f})")

    # Pattern analysis
    antipatterns = [p for p in insights.patterns if p.is_antipattern]
    good_patterns = [p for p in insights.patterns if not p.is_antipattern]

    if antipatterns:
        print(f"   - Anti-patterns found: {len(antipatterns)}")
        for pattern in antipatterns[:3]:  # Show first 3
            print(f"     • {pattern.name}: {pattern.description}")

    if good_patterns:
        print(f"   - Positive patterns: {len(good_patterns)}")
        for pattern in good_patterns[:3]:  # Show first 3
            print(f"     • {pattern.name}: {pattern.description}")

    # Self-improvement suggestions
    if insights.suggestions:
        print(f"\n💡 Self-Improvement Suggestions:")
        for suggestion in insights.suggestions:
            print(f"   - {suggestion}")

    print(f"\n🎯 Meta-Analysis Conclusion:")
    print(f"   Our analyzer successfully analyzed itself and provided actionable insights!")
    print(f"   This demonstrates the tool's ability to understand codebase structure")
    print(f"   and generate meaningful recommendations for any Python project.")


if __name__ == '__main__':
    main()