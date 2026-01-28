#!/usr/bin/env python3
"""
Self-Analysis Demo
=================

This script demonstrates the meta-programming approach by running our
intelligent codebase analyzer on itself and generating AI-powered insights.

This is the perfect example of the intersection of AI and developer productivity -
our tool analyzing and improving itself!
"""

import sys
from pathlib import Path

# Import our analyzer modules
from codebase_analyzer import CodebaseAnalyzer
from ai_insights_engine import AIInsightsEngine

def run_self_analysis():
    """Run our analyzer on our own codebase."""
    print("🤖 AI-Powered Self-Analysis Demo")
    print("=" * 50)
    print()
    print("Running our intelligent codebase analyzer on its own code...")
    print("This is the meta-programming approach in action!")
    print()

    # Analyze our own codebase
    current_dir = Path(".")
    analyzer = CodebaseAnalyzer(str(current_dir))
    results = analyzer.analyze()

    # Generate AI insights
    ai_engine = AIInsightsEngine()
    insights = ai_engine.generate_insights(results)

    print("📊 BASIC ANALYSIS RESULTS")
    print("-" * 30)
    print(f"Files analyzed: {results.total_files}")
    print(f"Total lines of code: {results.total_lines:,}")
    print(f"Languages: {', '.join(results.languages.keys())}")
    print()

    print("🧠 AI-GENERATED INSIGHTS")
    print("-" * 30)

    for i, insight in enumerate(insights, 1):
        severity_emoji = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "💡"
        }

        print(f"{severity_emoji.get(insight.severity, '📝')} {insight.title}")
        print(f"   Severity: {insight.severity.upper()}")
        print(f"   Confidence: {insight.confidence:.1%}")
        print()
        print(f"   {insight.explanation}")
        print()

        if insight.recommendations:
            print("   🔧 Recommendations:")
            for rec in insight.recommendations[:3]:  # Show top 3
                print(f"      • {rec}")
            print()

        if insight.evidence:
            print("   📋 Evidence:")
            for evidence in insight.evidence:
                print(f"      • {evidence}")

        print("-" * 50)
        print()

    print("🎯 SUMMARY")
    print("-" * 20)
    critical_count = len([i for i in insights if i.severity == "critical"])
    warning_count = len([i for i in insights if i.severity == "warning"])
    info_count = len([i for i in insights if i.severity == "info"])

    print(f"Critical insights: {critical_count}")
    print(f"Warning insights: {warning_count}")
    print(f"Informational insights: {info_count}")
    print()

    print("This demonstrates how AI can enhance static analysis by providing:")
    print("• Natural language explanations of patterns")
    print("• Context-aware recommendations")
    print("• Severity assessment based on codebase characteristics")
    print("• Evidence-based insights for better decision making")
    print()
    print("Our tool is not just detecting patterns - it's explaining them")
    print("and providing actionable guidance for improvement! 🚀")

if __name__ == "__main__":
    run_self_analysis()