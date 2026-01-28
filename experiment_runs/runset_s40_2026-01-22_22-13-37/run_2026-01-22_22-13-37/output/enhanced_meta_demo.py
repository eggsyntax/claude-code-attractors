#!/usr/bin/env python3
"""
Enhanced Meta-Analysis Demo

This script demonstrates the power of our intelligent codebase analyzer by:
1. Analyzing our analyzer tools themselves
2. Generating detailed insights about the analysis tools
3. Providing recommendations for improving the analyzer codebase
4. Creating visualizations of the analysis results

This is a perfect example of the AI-powered developer productivity tool we envisioned!
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any

# Add the current directory to Python path to import our analyzer
sys.path.insert(0, str(Path(__file__).parent))

from codebase_analyzer import CodebaseAnalyzer, ArchitecturalPattern


class MetaAnalysisReporter:
    """Enhanced reporter for meta-analysis of codebase analysis tools."""

    def __init__(self, analysis_results):
        self.results = analysis_results

    def generate_comprehensive_report(self) -> str:
        """Generate a detailed meta-analysis report."""
        report = []

        report.append("=" * 70)
        report.append("META-ANALYSIS: ANALYZING THE ANALYZER")
        report.append("=" * 70)

        report.append("\n🔍 EXECUTIVE SUMMARY")
        report.append("-" * 30)
        report.extend(self._generate_executive_summary())

        report.append("\n🏗️ ARCHITECTURAL INSIGHTS")
        report.append("-" * 30)
        report.extend(self._analyze_architecture())

        report.append("\n🔥 CODE QUALITY ANALYSIS")
        report.append("-" * 30)
        report.extend(self._analyze_code_quality())

        report.append("\n🎯 PATTERN ANALYSIS")
        report.append("-" * 30)
        report.extend(self._analyze_patterns())

        report.append("\n📊 COMPLEXITY ANALYSIS")
        report.append("-" * 30)
        report.extend(self._analyze_complexity())

        report.append("\n💡 IMPROVEMENT RECOMMENDATIONS")
        report.append("-" * 30)
        report.extend(self._generate_recommendations())

        report.append("\n🚀 NEXT STEPS")
        report.append("-" * 30)
        report.extend(self._suggest_next_steps())

        return "\n".join(report)

    def _generate_executive_summary(self) -> List[str]:
        """Generate executive summary of the meta-analysis."""
        summary = []

        total_files = self.results.total_files
        total_lines = self.results.total_lines
        avg_file_size = total_lines // total_files if total_files > 0 else 0

        summary.append(f"Analyzed {total_files} Python files containing {total_lines:,} lines of code")
        summary.append(f"Average file size: {avg_file_size} lines")

        # Categorize files by purpose
        analysis_files = []
        demo_files = []
        utility_files = []

        for path, info in self.results.file_info.items():
            filename = path.name.lower()
            if 'analyzer' in filename or 'pattern' in filename:
                analysis_files.append(path.name)
            elif 'demo' in filename or 'test' in filename:
                demo_files.append(path.name)
            else:
                utility_files.append(path.name)

        summary.append(f"\nFile categories identified:")
        summary.append(f"  • Analysis engines: {len(analysis_files)} files")
        summary.append(f"  • Demos & tests: {len(demo_files)} files")
        summary.append(f"  • Utilities: {len(utility_files)} files")

        # Key insights
        antipatterns = [p for p in self.results.patterns if p.is_antipattern]
        if antipatterns:
            summary.append(f"\n⚠️  Found {len(antipatterns)} anti-patterns that need attention")

        if self.results.complexity_hotspots:
            hottest = self.results.complexity_hotspots[0]
            summary.append(f"🔥 Most complex file: {hottest[0].name} (complexity: {hottest[1]:.1f})")

        return summary

    def _analyze_architecture(self) -> List[str]:
        """Analyze the architectural characteristics of the codebase."""
        insights = []

        # Analyze file relationships
        dependency_graph = self.results.dependency_graph

        if dependency_graph:
            most_imported = max(dependency_graph.items(), key=lambda x: len(x[1]), default=("", set()))[0]
            if most_imported:
                insights.append(f"📈 Most dependencies: {Path(most_imported).name}")

        # Analyze modularity
        single_file_modules = sum(1 for info in self.results.file_info.values() if len(info.imports) == 0)
        highly_coupled = sum(1 for info in self.results.file_info.values() if len(info.imports) > 10)

        insights.append(f"🔗 Modularity analysis:")
        insights.append(f"  • Self-contained modules: {single_file_modules}")
        insights.append(f"  • Highly coupled modules: {highly_coupled}")

        # Analyze code organization
        function_distribution = []
        class_distribution = []

        for info in self.results.file_info.values():
            function_distribution.append(len(info.functions))
            class_distribution.append(len(info.classes))

        avg_functions = sum(function_distribution) / len(function_distribution) if function_distribution else 0
        avg_classes = sum(class_distribution) / len(class_distribution) if class_distribution else 0

        insights.append(f"📦 Code organization:")
        insights.append(f"  • Average functions per file: {avg_functions:.1f}")
        insights.append(f"  • Average classes per file: {avg_classes:.1f}")

        return insights

    def _analyze_code_quality(self) -> List[str]:
        """Analyze overall code quality metrics."""
        quality = []

        # File size analysis
        file_sizes = [info.lines for info in self.results.file_info.values()]
        large_files = [size for size in file_sizes if size > 500]
        very_large_files = [size for size in file_sizes if size > 1000]

        quality.append(f"📏 File size distribution:")
        quality.append(f"  • Files > 500 lines: {len(large_files)}")
        quality.append(f"  • Files > 1000 lines: {len(very_large_files)}")

        if large_files:
            avg_large = sum(large_files) / len(large_files)
            quality.append(f"  • Average size of large files: {avg_large:.0f} lines")

        # Function/class analysis
        total_functions = sum(len(info.functions) for info in self.results.file_info.values())
        total_classes = sum(len(info.classes) for info in self.results.file_info.values())

        quality.append(f"\n🏗️ Code structure:")
        quality.append(f"  • Total functions defined: {total_functions}")
        quality.append(f"  • Total classes defined: {total_classes}")
        quality.append(f"  • Function-to-class ratio: {total_functions/total_classes:.1f}" if total_classes > 0 else "  • Function-to-class ratio: ∞")

        # Import analysis
        all_imports = []
        for info in self.results.file_info.values():
            all_imports.extend(info.imports)

        import_counter = Counter(all_imports)
        most_common_imports = import_counter.most_common(5)

        quality.append(f"\n📦 Import analysis:")
        quality.append(f"  • Unique imports: {len(set(all_imports))}")
        quality.append(f"  • Most used imports:")
        for imp, count in most_common_imports:
            quality.append(f"    - {imp}: {count} files")

        return quality

    def _analyze_patterns(self) -> List[str]:
        """Analyze identified patterns and anti-patterns."""
        pattern_analysis = []

        patterns = self.results.patterns
        antipatterns = [p for p in patterns if p.is_antipattern]
        good_patterns = [p for p in patterns if not p.is_antipattern]

        pattern_analysis.append(f"✅ Good patterns found: {len(good_patterns)}")
        for pattern in good_patterns:
            pattern_analysis.append(f"  • {pattern.name} (confidence: {pattern.confidence:.1%})")
            pattern_analysis.append(f"    {pattern.description}")

        pattern_analysis.append(f"\n❌ Anti-patterns found: {len(antipatterns)}")
        for pattern in antipatterns:
            pattern_analysis.append(f"  • {pattern.name} (confidence: {pattern.confidence:.1%})")
            pattern_analysis.append(f"    {pattern.description}")
            pattern_analysis.append(f"    Files affected: {len(pattern.files_involved)}")

        # Pattern implications
        if antipatterns:
            pattern_analysis.append(f"\n🎯 Pattern implications:")
            god_objects = [p for p in antipatterns if p.name == "God Object"]
            if god_objects:
                pattern_analysis.append(f"  • {len(god_objects)} files may benefit from decomposition")

            circular_deps = [p for p in antipatterns if "Circular" in p.name]
            if circular_deps:
                pattern_analysis.append(f"  • {len(circular_deps)} circular dependencies need refactoring")

        return pattern_analysis

    def _analyze_complexity(self) -> List[str]:
        """Analyze complexity distribution and hotspots."""
        complexity = []

        complexity_scores = [info.complexity_score for info in self.results.file_info.values()]
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0

        complexity.append(f"📊 Complexity metrics:")
        complexity.append(f"  • Average complexity: {avg_complexity:.2f}")

        # Categorize by complexity
        low_complexity = [s for s in complexity_scores if s < 2.0]
        medium_complexity = [s for s in complexity_scores if 2.0 <= s < 5.0]
        high_complexity = [s for s in complexity_scores if s >= 5.0]

        complexity.append(f"  • Low complexity files: {len(low_complexity)}")
        complexity.append(f"  • Medium complexity files: {len(medium_complexity)}")
        complexity.append(f"  • High complexity files: {len(high_complexity)}")

        # Hotspots analysis
        hotspots = self.results.complexity_hotspots[:5]
        complexity.append(f"\n🔥 Top complexity hotspots:")

        for i, (path, score) in enumerate(hotspots, 1):
            complexity.append(f"  {i}. {path.name}: {score:.2f}")

            # Get additional context for the hotspot
            file_info = self.results.file_info.get(path)
            if file_info:
                complexity.append(f"     ({file_info.lines} lines, {len(file_info.functions)} functions)")

        return complexity

    def _generate_recommendations(self) -> List[str]:
        """Generate specific improvement recommendations."""
        recommendations = []

        # Based on patterns found
        antipatterns = [p for p in self.results.patterns if p.is_antipattern]

        if antipatterns:
            recommendations.append("🔧 Immediate actions:")

            god_objects = [p for p in antipatterns if p.name == "God Object"]
            if god_objects:
                recommendations.append(f"  1. Refactor {len(god_objects)} God Object files:")
                for pattern in god_objects[:3]:  # Show top 3
                    filename = pattern.files_involved[0].name
                    recommendations.append(f"     • {filename} - break into smaller, focused modules")

        # Based on complexity
        high_complexity_files = [
            (path, score) for path, score in self.results.complexity_hotspots
            if score > 5.0
        ]

        if high_complexity_files:
            recommendations.append(f"  2. Reduce complexity in {len(high_complexity_files)} files:")
            for path, score in high_complexity_files[:3]:
                recommendations.append(f"     • {path.name} (complexity: {score:.1f})")

        # Architectural improvements
        recommendations.append(f"\n🏗️ Architectural improvements:")

        # Check for missing documentation patterns
        doc_files = [info for info in self.results.file_info.values() if 'doc' in str(info.path).lower()]
        if len(doc_files) == 0:
            recommendations.append("  • Add documentation generator modules")

        # Check for missing test patterns
        test_files = [info for info in self.results.file_info.values() if 'test' in str(info.path).lower()]
        if len(test_files) < 3:
            recommendations.append("  • Increase test coverage with dedicated test modules")

        # Suggest design patterns
        recommendations.append("  • Consider implementing Strategy pattern for different analysis types")
        recommendations.append("  • Add Factory pattern for creating different types of analyzers")

        return recommendations

    def _suggest_next_steps(self) -> List[str]:
        """Suggest next development steps."""
        next_steps = []

        next_steps.append("🎯 Development priorities:")
        next_steps.append("  1. Address identified anti-patterns")
        next_steps.append("  2. Reduce complexity in hotspot files")
        next_steps.append("  3. Add comprehensive test suite")
        next_steps.append("  4. Implement plugin architecture for extensibility")
        next_steps.append("  5. Add configuration management for analysis rules")

        next_steps.append("\n🚀 Feature enhancements:")
        next_steps.append("  • Add support for more languages (JavaScript, TypeScript, Java)")
        next_steps.append("  • Implement visual dependency graphs")
        next_steps.append("  • Add code quality metrics (maintainability index)")
        next_steps.append("  • Create web dashboard for results")
        next_steps.append("  • Integrate with CI/CD pipelines")

        next_steps.append("\n🤖 AI-powered features:")
        next_steps.append("  • Natural language explanations of patterns")
        next_steps.append("  • Automated refactoring suggestions")
        next_steps.append("  • Code quality scoring with explanations")
        next_steps.append("  • Intelligent documentation generation")

        return next_steps


def main():
    """Run the enhanced meta-analysis demo."""
    print("🔍 Starting Enhanced Meta-Analysis of Codebase Analysis Tools...")
    print("=" * 70)

    # Analyze the current directory
    analyzer = CodebaseAnalyzer(".")
    results = analyzer.analyze()

    # Generate comprehensive report
    reporter = MetaAnalysisReporter(results)
    report = reporter.generate_comprehensive_report()

    # Display the report
    print(report)

    # Save detailed results
    output_file = "meta_analysis_detailed.json"

    # Convert results to serializable format
    serializable_results = {
        "total_files": results.total_files,
        "total_lines": results.total_lines,
        "languages": results.languages,
        "patterns": [
            {
                "name": p.name,
                "description": p.description,
                "confidence": p.confidence,
                "is_antipattern": p.is_antipattern,
                "files_involved": [str(f) for f in p.files_involved],
                "suggestions": p.suggestions
            }
            for p in results.patterns
        ],
        "complexity_hotspots": [
            {"file": str(path), "complexity": score}
            for path, score in results.complexity_hotspots
        ],
        "suggestions": results.suggestions,
        "file_details": [
            {
                "path": str(path),
                "language": info.language,
                "lines": info.lines,
                "functions": len(info.functions),
                "classes": len(info.classes),
                "imports": len(info.imports),
                "complexity": info.complexity_score
            }
            for path, info in results.file_info.items()
        ]
    }

    with open(output_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)

    print(f"\n📁 Detailed results saved to: {output_file}")
    print("\n🎉 Meta-analysis complete! This demonstrates the power of our")
    print("   intelligent codebase analyzer - it can analyze and improve itself!")


if __name__ == "__main__":
    main()