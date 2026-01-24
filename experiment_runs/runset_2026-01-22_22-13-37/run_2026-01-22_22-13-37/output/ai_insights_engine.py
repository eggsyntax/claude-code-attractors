#!/usr/bin/env python3
"""
AI Insights Engine

This module demonstrates how AI can enhance codebase analysis by providing:
- Natural language explanations of patterns and anti-patterns
- Context-aware recommendations
- Intelligent documentation generation
- Code quality narratives

This represents the next evolution of developer productivity tools - where AI doesn't
just detect patterns, but explains them in human terms and provides actionable guidance.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class AIInsight:
    """AI-generated insight about code patterns or quality."""
    title: str
    explanation: str
    severity: str  # "info", "warning", "critical"
    recommendations: List[str]
    confidence: float
    evidence: List[str]


class AIInsightsEngine:
    """
    AI-powered insights generator for codebase analysis.

    This engine simulates how AI could enhance static analysis by providing
    contextual explanations and intelligent recommendations based on patterns.
    """

    def __init__(self):
        self.pattern_explanations = self._initialize_pattern_knowledge()
        self.complexity_thresholds = {
            "low": 2.0,
            "medium": 5.0,
            "high": 8.0
        }

    def generate_insights(self, analysis_results) -> List[AIInsight]:
        """Generate AI-powered insights from analysis results."""
        insights = []

        # Pattern-based insights
        insights.extend(self._analyze_architectural_patterns(analysis_results))

        # Complexity-based insights
        insights.extend(self._analyze_complexity_patterns(analysis_results))

        # Code organization insights
        insights.extend(self._analyze_organization_patterns(analysis_results))

        # Language and import insights
        insights.extend(self._analyze_dependency_patterns(analysis_results))

        # Quality trend insights
        insights.extend(self._generate_quality_narrative(analysis_results))

        return sorted(insights, key=lambda x: (x.severity == "critical", x.confidence), reverse=True)

    def _initialize_pattern_knowledge(self) -> Dict[str, Dict[str, Any]]:
        """Initialize AI knowledge base about code patterns."""
        return {
            "God Object": {
                "explanation": """
                The God Object anti-pattern occurs when a single class or module takes on too many responsibilities,
                violating the Single Responsibility Principle. These files become difficult to maintain, test, and understand
                because they're trying to do too much. This often happens gradually as features are added without proper
                refactoring.
                """.strip(),
                "impact": "High - Makes code harder to maintain, test, and debug",
                "recommendations": [
                    "Extract related functionality into separate, focused classes",
                    "Apply the Single Responsibility Principle - each class should have one reason to change",
                    "Consider using composition over inheritance to break up large classes",
                    "Identify distinct concerns and create separate modules for each",
                    "Use dependency injection to reduce coupling between extracted components"
                ],
                "detection_indicators": [
                    "Files with >20 functions or >500 lines",
                    "Classes that handle multiple unrelated concerns",
                    "Modules that are imported by many other modules"
                ]
            },
            "Circular Dependency": {
                "explanation": """
                Circular dependencies occur when two or more modules depend on each other, creating a cycle.
                This makes the code harder to understand, test, and can lead to initialization problems.
                It also makes it impossible to reuse individual components independently.
                """.strip(),
                "impact": "High - Prevents modularity and can cause runtime issues",
                "recommendations": [
                    "Introduce an abstraction layer to break the cycle",
                    "Move shared functionality to a separate, lower-level module",
                    "Apply dependency inversion principle with interfaces",
                    "Restructure the code to have a clear dependency hierarchy"
                ],
                "detection_indicators": [
                    "Module A imports B while B imports A",
                    "Complex initialization order requirements",
                    "Difficulty in unit testing individual components"
                ]
            },
            "High Complexity": {
                "explanation": """
                High cyclomatic complexity indicates functions or classes that have many decision points (if statements, loops, etc.).
                This makes code harder to understand, test thoroughly, and debug. Functions with high complexity often try to do too much
                and would benefit from being broken down into smaller, more focused functions.
                """.strip(),
                "impact": "Medium-High - Reduces code maintainability and increases bug risk",
                "recommendations": [
                    "Break complex functions into smaller, single-purpose functions",
                    "Extract complex conditionals into well-named boolean functions",
                    "Use early returns to reduce nesting depth",
                    "Consider using polymorphism instead of complex switch statements",
                    "Add comprehensive unit tests for complex code paths"
                ],
                "detection_indicators": [
                    "Functions with complexity score > 8",
                    "Deep nesting levels (>3-4 levels)",
                    "Long parameter lists"
                ]
            }
        }

    def _analyze_architectural_patterns(self, results) -> List[AIInsight]:
        """Generate insights about architectural patterns."""
        insights = []

        for pattern in results.patterns:
            if pattern.name in self.pattern_explanations:
                knowledge = self.pattern_explanations[pattern.name]

                severity = "critical" if pattern.is_antipattern and pattern.confidence > 0.8 else \
                          "warning" if pattern.is_antipattern else "info"

                # Customize explanation based on actual findings
                files_affected = len(pattern.files_involved)
                customized_explanation = self._customize_explanation(
                    knowledge["explanation"], pattern, files_affected
                )

                insights.append(AIInsight(
                    title=f"Architectural Pattern: {pattern.name}",
                    explanation=customized_explanation,
                    severity=severity,
                    recommendations=knowledge["recommendations"][:3],  # Top 3 recommendations
                    confidence=pattern.confidence,
                    evidence=[
                        f"Pattern detected in {files_affected} file(s)",
                        pattern.description,
                        f"Confidence level: {pattern.confidence:.1%}"
                    ]
                ))

        return insights

    def _analyze_complexity_patterns(self, results) -> List[AIInsight]:
        """Generate insights about complexity patterns."""
        insights = []

        if not results.complexity_hotspots:
            return insights

        # Overall complexity analysis
        complexity_scores = [score for _, score in results.complexity_hotspots]
        avg_complexity = sum(complexity_scores) / len(complexity_scores)
        max_complexity = max(complexity_scores)

        if max_complexity > self.complexity_thresholds["high"]:
            hottest_file = results.complexity_hotspots[0][0].name

            insights.append(AIInsight(
                title="Critical Complexity Hotspot Detected",
                explanation=f"""
                Your codebase has a significant complexity hotspot in '{hottest_file}' with a complexity score of {max_complexity:.1f}.
                This file likely contains functions with many decision points, nested conditions, or loops that make it difficult to
                understand and maintain. High complexity often correlates with higher bug rates and makes testing more challenging.

                The average complexity across your hotspot files is {avg_complexity:.1f}, which suggests this isn't an isolated issue.
                """.strip(),
                severity="critical",
                recommendations=[
                    f"Prioritize refactoring '{hottest_file}' to reduce complexity",
                    "Break down complex functions into smaller, focused functions",
                    "Extract complex conditional logic into well-named helper functions",
                    "Add comprehensive unit tests before refactoring to ensure behavior is preserved"
                ],
                confidence=0.9,
                evidence=[
                    f"Highest complexity score: {max_complexity:.1f}",
                    f"Average hotspot complexity: {avg_complexity:.1f}",
                    f"Files with high complexity: {len([s for s in complexity_scores if s > 5.0])}"
                ]
            ))

        return insights

    def _analyze_organization_patterns(self, results) -> List[AIInsight]:
        """Generate insights about code organization."""
        insights = []

        # File size analysis
        file_sizes = [info.lines for info in results.file_info.values()]
        large_files = [size for size in file_sizes if size > 500]
        avg_file_size = sum(file_sizes) / len(file_sizes)

        if large_files:
            insights.append(AIInsight(
                title="File Size Organization Analysis",
                explanation=f"""
                You have {len(large_files)} files that are larger than 500 lines, with an average file size of {avg_file_size:.0f} lines.
                While file size alone isn't always problematic, larger files often indicate that multiple concerns are mixed together.
                This can make code harder to navigate, understand, and maintain.

                Consider whether these large files are handling multiple responsibilities that could be separated into focused modules.
                """.strip(),
                severity="warning" if len(large_files) > 3 else "info",
                recommendations=[
                    "Review large files to identify if they handle multiple concerns",
                    "Extract related functionality into separate modules",
                    "Consider using directories to group related files",
                    "Aim for files that can be understood in a single screen view"
                ],
                confidence=0.7,
                evidence=[
                    f"Files >500 lines: {len(large_files)}",
                    f"Average file size: {avg_file_size:.0f} lines",
                    f"Largest file: {max(file_sizes)} lines"
                ]
            ))

        # Function distribution analysis
        function_counts = [len(info.functions) for info in results.file_info.values()]
        avg_functions_per_file = sum(function_counts) / len(function_counts) if function_counts else 0

        if avg_functions_per_file > 15:
            insights.append(AIInsight(
                title="Function Distribution Pattern",
                explanation=f"""
                Your files average {avg_functions_per_file:.1f} functions each, which is relatively high. This could indicate
                that some files are taking on too many responsibilities. Well-organized code typically has files that focus
                on a specific concern with a moderate number of related functions.

                Consider grouping related functions together and separating unrelated functionality into different modules.
                """.strip(),
                severity="info",
                recommendations=[
                    "Group related functions into cohesive modules",
                    "Consider using classes to organize related functions",
                    "Create separate modules for different concerns",
                    "Use clear naming conventions to indicate module purposes"
                ],
                confidence=0.6,
                evidence=[
                    f"Average functions per file: {avg_functions_per_file:.1f}",
                    f"Files with >20 functions: {len([c for c in function_counts if c > 20])}"
                ]
            ))

        return insights

    def _analyze_dependency_patterns(self, results) -> List[AIInsight]:
        """Generate insights about dependencies and imports."""
        insights = []

        # Import analysis
        all_imports = []
        for info in results.file_info.values():
            all_imports.extend(info.imports)

        unique_imports = set(all_imports)
        import_frequency = {imp: all_imports.count(imp) for imp in unique_imports}

        # Check for potential dependency issues
        highly_imported = [imp for imp, count in import_frequency.items() if count > len(results.file_info) * 0.5]

        if highly_imported:
            insights.append(AIInsight(
                title="Dependency Coupling Analysis",
                explanation=f"""
                Several modules ({', '.join(highly_imported[:3])}) are imported by more than half of your files.
                While some common utilities being widely used is normal, this could also indicate tight coupling
                or a lack of proper abstraction layers.

                Consider whether these dependencies represent core abstractions that should be formalized, or if
                some files are importing modules they don't really need.
                """.strip(),
                severity="info",
                recommendations=[
                    "Review widely-used imports to ensure they represent well-designed abstractions",
                    "Consider creating facade or adapter patterns for complex external dependencies",
                    "Audit imports to ensure each file only imports what it actually uses",
                    "Group related imports and consider creating higher-level abstractions"
                ],
                confidence=0.6,
                evidence=[
                    f"Highly imported modules: {len(highly_imported)}",
                    f"Total unique imports: {len(unique_imports)}",
                    f"Most imported: {max(import_frequency.items(), key=lambda x: x[1])[0] if import_frequency else 'None'}"
                ]
            ))

        return insights

    def _generate_quality_narrative(self, results) -> List[AIInsight]:
        """Generate an overall quality narrative."""
        insights = []

        # Calculate quality indicators
        total_files = results.total_files
        antipattern_count = len([p for p in results.patterns if p.is_antipattern])
        high_complexity_count = len([s for _, s in results.complexity_hotspots if s > 5.0])

        # Quality score (0-10)
        quality_score = self._calculate_quality_score(results)

        quality_level = "excellent" if quality_score >= 8 else \
                       "good" if quality_score >= 6 else \
                       "needs improvement" if quality_score >= 4 else "poor"

        insights.append(AIInsight(
            title=f"Overall Codebase Health: {quality_level.title()}",
            explanation=f"""
            Based on the analysis of {total_files} files, your codebase has a quality score of {quality_score:.1f}/10.
            This score considers factors like architectural patterns, complexity, organization, and dependencies.

            {'Your codebase shows good architectural discipline with minimal anti-patterns.' if antipattern_count == 0 else f'There are {antipattern_count} anti-patterns that should be addressed to improve maintainability.'}

            {'Complexity levels are well-managed across the codebase.' if high_complexity_count <= total_files * 0.2 else f'Consider refactoring {high_complexity_count} high-complexity files to improve maintainability.'}
            """.strip(),
            severity="info" if quality_score >= 6 else "warning",
            recommendations=[
                f"Focus on {'maintaining current quality standards' if quality_score >= 7 else 'addressing identified anti-patterns'}",
                f"{'Continue current practices' if high_complexity_count <= 3 else 'Prioritize complexity reduction in hotspot files'}",
                "Consider implementing automated quality gates in your CI/CD pipeline",
                "Regular code reviews can help maintain architectural consistency"
            ],
            confidence=0.8,
            evidence=[
                f"Quality score: {quality_score:.1f}/10",
                f"Anti-patterns found: {antipattern_count}",
                f"High-complexity files: {high_complexity_count}",
                f"Total files analyzed: {total_files}"
            ]
        ))

        return insights

    def _calculate_quality_score(self, results) -> float:
        """Calculate an overall quality score (0-10)."""
        score = 10.0

        # Deduct for anti-patterns
        antipatterns = len([p for p in results.patterns if p.is_antipattern])
        score -= antipatterns * 1.5

        # Deduct for high complexity
        high_complexity = len([s for _, s in results.complexity_hotspots if s > 5.0])
        score -= high_complexity * 0.8

        # Deduct for large files
        large_files = len([info for info in results.file_info.values() if info.lines > 500])
        score -= large_files * 0.5

        # Bonus for good organization
        if results.total_files > 10:  # Modular codebase
            score += 0.5

        return max(0.0, min(10.0, score))

    def _customize_explanation(self, base_explanation: str, pattern, files_affected: int) -> str:
        """Customize explanation based on specific findings."""
        customization = f"\n\nIn your codebase, this pattern affects {files_affected} file(s). "

        if files_affected == 1:
            customization += "While this is limited to a single file, addressing it will improve overall code quality."
        elif files_affected <= 3:
            customization += "This is a moderate concern that should be addressed to prevent it from spreading."
        else:
            customization += "This is a significant concern affecting multiple files and should be prioritized for refactoring."

        return base_explanation + customization

    def generate_summary_report(self, insights: List[AIInsight]) -> str:
        """Generate a human-readable summary report."""
        if not insights:
            return "No significant insights generated for this codebase."

        critical_insights = [i for i in insights if i.severity == "critical"]
        warning_insights = [i for i in insights if i.severity == "warning"]
        info_insights = [i for i in insights if i.severity == "info"]

        report = []
        report.append("AI INSIGHTS SUMMARY")
        report.append("=" * 50)

        if critical_insights:
            report.append(f"\n🚨 CRITICAL ISSUES ({len(critical_insights)}):")
            for insight in critical_insights:
                report.append(f"• {insight.title}")
                report.append(f"  {insight.explanation[:100]}...")

        if warning_insights:
            report.append(f"\n⚠️  WARNINGS ({len(warning_insights)}):")
            for insight in warning_insights:
                report.append(f"• {insight.title}")

        if info_insights:
            report.append(f"\n💡 INFORMATION ({len(info_insights)}):")
            for insight in info_insights:
                report.append(f"• {insight.title}")

        return "\n".join(report)


def main():
    """Demonstrate AI insights engine."""
    # This would typically be called with real analysis results
    print("AI Insights Engine - Demonstration of AI-powered code analysis")
    print("This engine provides contextual explanations and intelligent recommendations")
    print("based on static analysis patterns, going beyond simple pattern detection.")


if __name__ == "__main__":
    main()