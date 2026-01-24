#!/usr/bin/env python3
"""
Showcase Demo: Code Analysis & Visualization System

This demo script showcases the complete code analysis system built collaboratively
by Alice and Bob. It demonstrates both the analytical capabilities and the
interactive visualization features.

Features demonstrated:
- AST-based structural analysis
- Sophisticated complexity metrics
- Interactive web dashboard generation
- Real-time analysis of our own codebase (meta!)

Author: Alice & Bob (Collaborative AI Development)
"""

import os
import sys
import time
from pathlib import Path
from dashboard_generator import DashboardGenerator


def print_banner():
    """Print an attractive banner for the demo."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                  🔍 CODE ANALYSIS SHOWCASE                   ║
║              Interactive Visualization System                ║
╟──────────────────────────────────────────────────────────────╢
║  Built collaboratively by Alice & Bob                       ║
║  • AST-based structural analysis                            ║
║  • Advanced complexity metrics                              ║
║  • Interactive web dashboards                               ║
║  • Meta-analysis capabilities                               ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def demo_self_analysis():
    """Demonstrate self-analysis capabilities on our own codebase."""
    print("\n🎯 DEMONSTRATION 1: Meta-Analysis")
    print("=" * 50)
    print("Analyzing our own code analysis system...")

    # Get the current directory (where our analyzer files are)
    current_dir = Path(__file__).parent

    # Create dashboard generator
    generator = DashboardGenerator(str(current_dir))

    # Analyze our own codebase
    print(f"📂 Analyzing directory: {current_dir}")
    results = generator.analyze_project(str(current_dir))

    # Show detailed results
    generator.print_summary()

    # Generate interactive dashboard
    print("\n🎨 Generating interactive dashboard...")
    dashboard_path = generator.generate_dashboard(output_filename='self_analysis_dashboard.html')

    print(f"\n✨ Self-analysis complete!")
    print(f"🌐 Interactive dashboard: file://{os.path.abspath(dashboard_path)}")

    return generator, results


def demo_analysis_features(generator, results):
    """Demonstrate specific analysis features with examples."""
    print("\n\n🔬 DEMONSTRATION 2: Analysis Features")
    print("=" * 50)

    functions = results['functions']
    if not functions:
        print("No functions found for detailed analysis.")
        return

    # Show complexity analysis
    print("🧮 COMPLEXITY ANALYSIS:")
    complex_functions = [f for f in functions if f.get('cyclomatic_complexity', 0) > 5]

    if complex_functions:
        print(f"Found {len(complex_functions)} moderately complex functions:")
        for func in sorted(complex_functions, key=lambda x: x.get('cyclomatic_complexity', 0), reverse=True)[:3]:
            print(f"  • {func['name']} ({func['file']})")
            print(f"    Cyclomatic: {func.get('cyclomatic_complexity', 'N/A')}, "
                  f"Cognitive: {func.get('cognitive_complexity', 'N/A')}")
            print(f"    Rating: {func.get('complexity_rating', 'Unknown')}")
    else:
        print("  All functions have low complexity (excellent!)")

    # Show architectural insights
    print("\n🏗️  ARCHITECTURAL INSIGHTS:")
    classes = results['classes']
    print(f"  • {len(classes)} classes found")
    print(f"  • {len(results['dependencies'])} import dependencies")

    # Show most connected files
    file_connections = {}
    for dep in results['dependencies']:
        file_connections[dep['from']] = file_connections.get(dep['from'], 0) + 1

    if file_connections:
        most_connected = max(file_connections.items(), key=lambda x: x[1])
        print(f"  • Most connected file: {most_connected[0]} ({most_connected[1]} imports)")

    # Show function distribution
    print(f"\n📊 FUNCTION DISTRIBUTION:")
    total_funcs = len(functions)
    avg_lines = sum(f.get('end_line', 0) - f.get('start_line', 0) for f in functions) / total_funcs if total_funcs else 0
    print(f"  • {total_funcs} total functions")
    print(f"  • Average function length: {avg_lines:.1f} lines")

    # Show code quality metrics
    quality_ratings = {}
    for func in functions:
        rating = func.get('complexity_rating', 'Unknown')
        quality_ratings[rating] = quality_ratings.get(rating, 0) + 1

    print(f"\n⭐ QUALITY RATINGS:")
    for rating, count in quality_ratings.items():
        percentage = (count / total_funcs) * 100 if total_funcs else 0
        print(f"  • {rating}: {count} functions ({percentage:.1f}%)")


def demo_interactive_features():
    """Demonstrate the interactive dashboard features."""
    print("\n\n🎮 DEMONSTRATION 3: Interactive Features")
    print("=" * 50)
    print("The generated HTML dashboard includes:")

    features = [
        "📊 Real-time metrics overview with color-coded complexity",
        "📈 Interactive complexity distribution histograms",
        "🔥 Function complexity heatmap with sorting options",
        "🕸️  Dynamic dependency graph with force-directed layout",
        "📋 Searchable and filterable function details table",
        "🎚️  Interactive complexity threshold controls",
        "🎨 Responsive design for different screen sizes"
    ]

    for feature in features:
        print(f"  • {feature}")
        time.sleep(0.3)  # Dramatic effect!

    print("\n💡 Pro Tips for using the dashboard:")
    tips = [
        "Click and drag nodes in the dependency graph",
        "Use the complexity filter slider to focus on problem areas",
        "Sort the heatmap by different metrics to find patterns",
        "Hover over chart elements for detailed information"
    ]

    for tip in tips:
        print(f"  🔹 {tip}")


def demo_extensibility():
    """Demonstrate how the system can be extended."""
    print("\n\n🔧 DEMONSTRATION 4: Extensibility")
    print("=" * 50)
    print("Our system is designed for easy extension:")

    extensions = [
        ("🎯 New Metrics", "Add custom complexity calculations in ComplexityAnalyzer"),
        ("📊 New Visualizations", "Extend dashboard with additional chart types"),
        ("🔍 New Languages", "Adapt AST parsing for other programming languages"),
        ("📈 Historical Analysis", "Track complexity changes over time"),
        ("🚨 Quality Gates", "Integrate with CI/CD for automated quality checks"),
        ("📱 Mobile View", "Optimize dashboard for mobile devices")
    ]

    for title, description in extensions:
        print(f"  {title}")
        print(f"    {description}")


def demo_real_world_usage():
    """Show how this could be used in real projects."""
    print("\n\n🌍 DEMONSTRATION 5: Real-World Usage")
    print("=" * 50)
    print("Practical applications of our analysis system:")

    use_cases = [
        ("📋 Code Reviews", "Identify complex functions needing review before merging"),
        ("♻️  Refactoring Planning", "Prioritize refactoring efforts based on complexity metrics"),
        ("📚 Documentation", "Generate complexity-aware documentation"),
        ("🎯 Team Training", "Visual identification of code patterns and anti-patterns"),
        ("📊 Project Health", "Regular monitoring of codebase maintainability"),
        ("🔍 Technical Debt", "Quantify and track technical debt over time")
    ]

    for title, description in use_cases:
        print(f"  {title}: {description}")

    print(f"\n📝 Example CLI Usage:")
    print(f"  python dashboard_generator.py /path/to/your/project")
    print(f"  python showcase_demo.py")


def main():
    """Run the complete showcase demonstration."""
    print_banner()

    try:
        # Run self-analysis demonstration
        generator, results = demo_self_analysis()

        # Wait for user to see results
        input("\n🎬 Press Enter to continue to detailed analysis features...")

        # Show analysis features
        demo_analysis_features(generator, results)

        input("\n🎬 Press Enter to continue to interactive features...")

        # Demonstrate interactive features
        demo_interactive_features()

        input("\n🎬 Press Enter to continue to extensibility demo...")

        # Show extensibility
        demo_extensibility()

        input("\n🎬 Press Enter to continue to real-world usage...")

        # Show real-world usage
        demo_real_world_usage()

        print("\n" + "="*60)
        print("🎉 SHOWCASE COMPLETE!")
        print("="*60)
        print("This collaborative system demonstrates:")
        print("✅ Clean, extensible architecture")
        print("✅ Sophisticated analysis algorithms")
        print("✅ Interactive data visualization")
        print("✅ Self-documenting and meta-capable")
        print("✅ Production-ready code quality")

        print(f"\n📂 All files available in: {Path(__file__).parent}")
        print(f"🌐 Open the HTML dashboard to explore interactively!")

    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()