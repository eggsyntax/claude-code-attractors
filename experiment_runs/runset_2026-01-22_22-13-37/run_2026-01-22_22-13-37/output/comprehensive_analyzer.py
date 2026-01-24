#!/usr/bin/env python3
"""
Comprehensive Codebase Analyzer

Integrates the base analyzer with enhanced pattern detection to provide
the most complete analysis of codebase architecture, patterns, and quality.
"""

import sys
from pathlib import Path
from typing import Dict, List, Set

# Import our modules
from codebase_analyzer import CodebaseAnalyzer, CodebaseInsights, FileInfo, ArchitecturalPattern
from enhanced_patterns import EnhancedPatternDetector


class ComprehensiveAnalyzer(CodebaseAnalyzer):
    """
    Enhanced analyzer that combines base functionality with advanced pattern detection.
    """

    def __init__(self, root_path: str):
        super().__init__(root_path)
        self.pattern_detector = EnhancedPatternDetector()

    def analyze(self) -> CodebaseInsights:
        """Perform comprehensive analysis with enhanced pattern detection."""
        self.logger.info(f"Starting comprehensive analysis of {self.root_path}")

        # Get base analysis
        insights = super().analyze()

        # Add enhanced pattern detection
        enhanced_patterns = self.pattern_detector.detect_all_patterns(
            insights.file_info,
            insights.dependency_graph
        )

        # Merge with existing patterns
        all_patterns = insights.patterns + enhanced_patterns

        # Remove duplicates and merge similar patterns
        all_patterns = self._deduplicate_patterns(all_patterns)

        # Update insights with enhanced results
        insights.patterns = all_patterns
        insights.suggestions.extend(self._generate_enhanced_suggestions(enhanced_patterns))

        return insights

    def _deduplicate_patterns(self, patterns: List[ArchitecturalPattern]) -> List[ArchitecturalPattern]:
        """Remove duplicate patterns and merge similar ones."""
        seen_patterns = {}
        unique_patterns = []

        for pattern in patterns:
            # Create a key based on pattern name and primary file
            primary_file = pattern.files_involved[0] if pattern.files_involved else None
            key = (pattern.name, primary_file)

            if key not in seen_patterns:
                seen_patterns[key] = pattern
                unique_patterns.append(pattern)
            else:
                # Merge with existing pattern (take higher confidence)
                existing = seen_patterns[key]
                if pattern.confidence > existing.confidence:
                    seen_patterns[key] = pattern
                    unique_patterns = [p for p in unique_patterns if not (p.name == existing.name and p.files_involved == existing.files_involved)]
                    unique_patterns.append(pattern)

        return unique_patterns

    def _generate_enhanced_suggestions(self, enhanced_patterns: List[ArchitecturalPattern]) -> List[str]:
        """Generate additional suggestions based on enhanced pattern detection."""
        suggestions = []

        # Count different types of issues
        design_patterns = [p for p in enhanced_patterns if not p.is_antipattern]
        antipatterns = [p for p in enhanced_patterns if p.is_antipattern]

        if design_patterns:
            suggestions.append(f"Found {len(design_patterns)} positive design patterns - good architecture foundation")

        if antipatterns:
            high_priority = [p for p in antipatterns if p.confidence > 0.7]
            if high_priority:
                suggestions.append(f"Address {len(high_priority)} high-confidence anti-patterns for better code quality")

        # Specific pattern-based suggestions
        pattern_names = [p.name for p in enhanced_patterns]

        if "Long Parameter List" in pattern_names:
            suggestions.append("Consider refactoring functions with many parameters using parameter objects")

        if "Feature Envy" in pattern_names:
            suggestions.append("Review module responsibilities - some classes may be operating on wrong data")

        if "Potential Dead Code" in pattern_names:
            suggestions.append("Run comprehensive dead code analysis to improve codebase cleanliness")

        return suggestions

    def generate_comprehensive_report(self) -> str:
        """Generate a detailed report with enhanced analysis."""
        if not self.insights:
            return "No analysis results available. Run analyze() first."

        report = []
        report.append("# 🔍 Comprehensive Codebase Analysis Report")
        report.append("")

        # Executive Summary
        report.append("## 📊 Executive Summary")
        report.append(f"- **Total Files**: {self.insights.total_files}")
        report.append(f"- **Languages**: {', '.join(self.insights.languages_used.keys())}")
        report.append(f"- **Total Lines**: {self.insights.complexity_metrics.get('total_lines_of_code', 'N/A'):,.0f}")

        # Quality score calculation
        total_patterns = len(self.insights.patterns)
        good_patterns = len([p for p in self.insights.patterns if not p.is_antipattern])
        antipatterns = total_patterns - good_patterns

        if total_patterns > 0:
            quality_score = (good_patterns - antipatterns * 2) / total_patterns * 100
            quality_score = max(0, min(100, quality_score))
            report.append(f"- **Quality Score**: {quality_score:.1f}/100")
        report.append("")

        # Pattern Analysis
        report.append("## 🏗️ Pattern Analysis")

        # Good patterns
        good_patterns_list = [p for p in self.insights.patterns if not p.is_antipattern]
        if good_patterns_list:
            report.append("### ✅ Positive Patterns Found")
            for pattern in good_patterns_list:
                report.append(f"- **{pattern.name}** (confidence: {pattern.confidence:.0%})")
                report.append(f"  - {pattern.description}")
                if pattern.suggestions:
                    report.append(f"  - Suggestions: {'; '.join(pattern.suggestions)}")
            report.append("")

        # Anti-patterns
        antipatterns_list = [p for p in self.insights.patterns if p.is_antipattern]
        if antipatterns_list:
            report.append("### ❌ Issues to Address")
            # Sort by confidence (most important first)
            antipatterns_list.sort(key=lambda x: x.confidence, reverse=True)
            for pattern in antipatterns_list:
                priority = "🔴 High" if pattern.confidence > 0.7 else "🟡 Medium" if pattern.confidence > 0.5 else "🟢 Low"
                report.append(f"- **{pattern.name}** {priority}")
                report.append(f"  - {pattern.description}")
                report.append(f"  - Confidence: {pattern.confidence:.0%}")
                if pattern.suggestions:
                    report.append("  - Recommended Actions:")
                    for suggestion in pattern.suggestions:
                        report.append(f"    • {suggestion}")
            report.append("")

        # Complexity Analysis
        report.append("## 📈 Complexity Analysis")
        if self.insights.complexity_metrics:
            metrics = self.insights.complexity_metrics
            report.append(f"- **Average Complexity**: {metrics.get('average_complexity', 0):.2f}")
            report.append(f"- **Maximum Complexity**: {metrics.get('max_complexity', 0):.2f}")
            report.append(f"- **Average File Size**: {metrics.get('average_file_size', 0):.0f} lines")

        # Top complexity hotspots
        if self.insights.hotspots:
            report.append("")
            report.append("### 🔥 Complexity Hotspots")
            for i, hotspot in enumerate(self.insights.hotspots[:5], 1):
                report.append(f"{i}. `{hotspot}` - requires attention")

        report.append("")

        # Actionable Recommendations
        if self.insights.suggestions:
            report.append("## 💡 Actionable Recommendations")
            report.append("")
            report.append("### Priority Actions")
            high_priority = [s for s in self.insights.suggestions if any(word in s.lower() for word in ['high', 'critical', 'address'])]
            medium_priority = [s for s in self.insights.suggestions if s not in high_priority]

            if high_priority:
                for suggestion in high_priority:
                    report.append(f"🔴 **{suggestion}**")
                report.append("")

            if medium_priority:
                report.append("### Improvement Opportunities")
                for suggestion in medium_priority:
                    report.append(f"🟡 {suggestion}")
            report.append("")

        # Architecture Health Summary
        report.append("## 🏥 Architecture Health Summary")

        health_indicators = []

        if good_patterns_list:
            health_indicators.append(f"✅ {len(good_patterns_list)} positive architectural patterns")

        if antipatterns_list:
            critical_issues = len([p for p in antipatterns_list if p.confidence > 0.7])
            if critical_issues:
                health_indicators.append(f"❌ {critical_issues} critical issues need attention")

        complexity_issues = len([f for f in self.insights.file_infos if f.complexity_score > 10]) if hasattr(self.insights, 'file_infos') else 0
        if complexity_issues:
            health_indicators.append(f"⚠️ {complexity_issues} files with high complexity")

        if not health_indicators:
            health_indicators.append("✅ No major architectural issues detected")

        for indicator in health_indicators:
            report.append(f"- {indicator}")

        report.append("")
        report.append("---")
        report.append("*Generated by Comprehensive Codebase Analyzer*")

        return "\n".join(report)


def main():
    """Command-line interface for the comprehensive analyzer."""
    import argparse

    parser = argparse.ArgumentParser(description='Comprehensive codebase analysis with enhanced pattern detection')
    parser.add_argument('path', help='Path to the codebase to analyze')
    parser.add_argument('--output', '-o', help='Output file for results')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    import logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    analyzer = ComprehensiveAnalyzer(args.path)

    try:
        print("🚀 Starting comprehensive codebase analysis...")
        insights = analyzer.analyze()

        if args.format == 'json':
            import json
            result = {
                'summary': {
                    'total_files': insights.total_files,
                    'total_lines': insights.total_lines,
                    'languages': insights.languages,
                },
                'patterns': [
                    {
                        'name': p.name,
                        'description': p.description,
                        'confidence': p.confidence,
                        'is_antipattern': p.is_antipattern,
                        'files_count': len(p.files_involved),
                        'suggestions': p.suggestions
                    }
                    for p in insights.patterns
                ],
                'suggestions': insights.suggestions
            }

            output = json.dumps(result, indent=2)
        else:
            output = analyzer.generate_comprehensive_report()

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"📄 Report saved to {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()