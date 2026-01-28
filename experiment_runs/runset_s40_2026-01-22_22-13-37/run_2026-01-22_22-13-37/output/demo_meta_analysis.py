#!/usr/bin/env python3
"""
Meta-Analysis Demo

This script demonstrates the "eating our own dog food" approach by:
1. Running our enhanced analyzer on its own codebase
2. Generating insights about the analyzer itself
3. Using those insights to suggest improvements to the tool
4. Creating a feedback loop for continuous improvement
"""

import json
import subprocess
import os
from pathlib import Path
from enhanced_analyzer import EnhancedCodebaseAnalyzer


def run_meta_analysis():
    """Run the analyzer on itself and generate meta-insights."""
    print("🔄 Meta-Analysis: Analyzing the analyzer itself...")
    print("=" * 60)

    # Analyze our own codebase
    analyzer = EnhancedCodebaseAnalyzer('.')
    results = analyzer.enhanced_analyze()

    print("\n🎯 Self-Analysis Results:")
    print(f"Health Score: {results['health_score']['overall']}/100 (Grade: {results['health_score']['grade']})")

    # Extract insights about our own code
    insights = extract_meta_insights(results)

    print("\n🧠 Meta-Insights (What we learned about our analyzer):")
    for insight in insights:
        print(f"  • {insight}")

    # Generate self-improvement suggestions
    improvements = generate_self_improvements(results)

    print(f"\n💡 Self-Improvement Suggestions:")
    for improvement in improvements:
        print(f"  • {improvement}")

    # Create a report about our own architecture
    architecture_report = generate_architecture_report(results)
    with open('self_analysis_report.md', 'w') as f:
        f.write(architecture_report)

    print(f"\n📄 Detailed self-analysis report saved to: self_analysis_report.md")

    return results


def extract_meta_insights(results):
    """Extract insights specifically about the analyzer's architecture."""
    insights = []

    # Analyze the analyzer's own patterns
    base_insights = results['base_insights']
    patterns = base_insights.patterns if hasattr(base_insights, 'patterns') else base_insights['patterns']

    # Handle both object and dict access
    if hasattr(patterns[0], 'is_antipattern') if patterns else False:
        antipatterns = [p for p in patterns if p.is_antipattern]
    else:
        antipatterns = [p for p in patterns if p.get('is_antipattern', False)] if patterns else []

    if antipatterns:
        insights.append(f"Our analyzer itself has {len(antipatterns)} anti-patterns - we should fix ourselves first!")

    # Look at complexity
    hotspots = base_insights.complexity_hotspots if hasattr(base_insights, 'complexity_hotspots') else base_insights['complexity_hotspots']
    if hotspots and hotspots[0][1] > 4.0:
        complex_file = Path(hotspots[0][0]).name
        insights.append(f"Our most complex file is '{complex_file}' - we could simplify our own code")

    # Check refactoring opportunities
    refactoring_ops = results['refactoring_opportunities']
    if len(refactoring_ops) > 5:
        insights.append(f"We identified {len(refactoring_ops)} refactoring opportunities in our own code")

    # Meta-insight about meta-analysis
    insights.append("Successfully demonstrated meta-analysis capability - the tool can analyze itself!")

    return insights


def generate_self_improvements(results):
    """Generate specific improvements for the analyzer itself."""
    improvements = []

    # Based on complexity hotspots
    base_insights = results['base_insights']
    hotspots = base_insights.complexity_hotspots if hasattr(base_insights, 'complexity_hotspots') else base_insights['complexity_hotspots']
    for file_path, complexity in hotspots[:3]:
        file_name = Path(file_path).name
        improvements.append(f"Refactor {file_name} (complexity: {complexity:.1f}) by extracting smaller functions")

    # Based on refactoring opportunities
    opportunities = results['refactoring_opportunities']
    extract_method_ops = [op for op in opportunities if op['type'] == 'extract_method']
    if extract_method_ops:
        improvements.append(f"Apply method extraction in {len(extract_method_ops)} files to reduce complexity")

    # Based on architectural debt
    debt_items = results['architectural_debt']
    high_severity_debt = [debt for debt in debt_items if debt['severity'] > 7]
    if high_severity_debt:
        improvements.append("Address high-severity architectural debt immediately")

    # Meta-improvement suggestions
    improvements.append("Add more sophisticated pattern detection algorithms")
    improvements.append("Implement incremental analysis for large codebases")
    improvements.append("Add integration with version control for change-based analysis")

    return improvements


def generate_architecture_report(results):
    """Generate a detailed report about the analyzer's own architecture."""
    report = []
    report.append("# Self-Analysis Report: Codebase Analyzer Architecture")
    report.append(f"*Analysis performed on: {results['timestamp']}*")
    report.append("")

    report.append("## Executive Summary")
    health = results['health_score']
    report.append(f"The analyzer achieved a health score of **{health['overall']}/100 (Grade: {health['grade']})**.")

    if health['overall'] < 80:
        report.append("This indicates room for improvement in our own codebase.")
    else:
        report.append("This represents a healthy, maintainable codebase.")

    report.append("")
    report.append("## Architecture Analysis")

    # File structure analysis
    base_insights = results['base_insights']
    total_files = base_insights.total_files if hasattr(base_insights, 'total_files') else base_insights['total_files']
    total_lines = base_insights.total_lines if hasattr(base_insights, 'total_lines') else base_insights['total_lines']

    report.append(f"- **Total Files**: {total_files}")
    report.append(f"- **Lines of Code**: {total_lines:,}")
    report.append(f"- **Average File Size**: {total_lines // total_files} lines")

    # Complexity analysis
    report.append("")
    report.append("### Complexity Hotspots")
    hotspots = base_insights.complexity_hotspots if hasattr(base_insights, 'complexity_hotspots') else base_insights['complexity_hotspots']
    for i, (file_path, complexity) in enumerate(hotspots[:5], 1):
        file_name = Path(file_path).name
        report.append(f"{i}. **{file_name}**: {complexity:.1f} complexity score")

    # Patterns found
    report.append("")
    report.append("### Architectural Patterns")
    patterns = base_insights.patterns if hasattr(base_insights, 'patterns') else base_insights['patterns']
    if patterns:
        for pattern in patterns:
            if hasattr(pattern, 'is_antipattern'):
                status = "❌ Anti-pattern" if pattern.is_antipattern else "✅ Good pattern"
                name = pattern.name
                description = pattern.description
            else:
                status = "❌ Anti-pattern" if pattern['is_antipattern'] else "✅ Good pattern"
                name = pattern['name']
                description = pattern['description']
            report.append(f"- {status}: **{name}** - {description}")
    else:
        report.append("No significant architectural patterns detected.")

    # Refactoring opportunities
    report.append("")
    report.append("### Refactoring Opportunities")
    opportunities = results['refactoring_opportunities']
    if opportunities:
        for opp in opportunities[:5]:  # Top 5
            report.append(f"- **{opp['type'].replace('_', ' ').title()}**: {opp['description']}")
    else:
        report.append("No significant refactoring opportunities identified.")

    # Recommendations
    report.append("")
    report.append("### Recommendations for Improvement")
    for rec in health['recommendations']:
        report.append(f"- {rec}")

    report.append("")
    report.append("## Meta-Analysis Insights")
    report.append("This analysis demonstrates the analyzer's capability to:")
    report.append("- Successfully analyze its own codebase")
    report.append("- Identify areas for self-improvement")
    report.append("- Generate actionable insights about its own architecture")
    report.append("- Create a feedback loop for continuous improvement")

    report.append("")
    report.append("---")
    report.append("*This report was automatically generated by the Enhanced Codebase Analyzer*")

    return "\n".join(report)


def demonstrate_continuous_improvement():
    """Demonstrate how insights can feed back into tool improvement."""
    print("\n🔄 Demonstrating Continuous Improvement Loop:")
    print("1. Analyze codebase → 2. Generate insights → 3. Implement improvements → 4. Re-analyze")
    print("")

    # Simulate improvement tracking
    improvements_made = [
        "Added complexity threshold configuration",
        "Improved pattern detection accuracy",
        "Enhanced documentation generation",
        "Optimized file discovery algorithm"
    ]

    print("🛠️ Example improvements that could be made based on analysis:")
    for i, improvement in enumerate(improvements_made, 1):
        print(f"  {i}. {improvement}")

    print("\n📈 This creates a virtuous cycle of self-improvement!")


if __name__ == '__main__':
    print("🎭 Meta-Analysis Demo: AI Tool Analyzing Itself")
    print("This demonstrates the concept of 'eating our own dog food'")
    print("")

    # Run the meta-analysis
    results = run_meta_analysis()

    # Demonstrate continuous improvement concept
    demonstrate_continuous_improvement()

    print("\n✨ Demo complete! The analyzer has successfully analyzed itself.")
    print("This showcases the power of meta-analysis in AI-powered developer tools.")