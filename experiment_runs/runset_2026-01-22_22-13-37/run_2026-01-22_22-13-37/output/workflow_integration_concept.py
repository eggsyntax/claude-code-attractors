"""
Intelligent Codebase Analysis - Workflow Integration Concept

This extends our codebase analyzer into practical developer workflows,
demonstrating how AI-powered analysis can be embedded into daily development tasks.
"""

import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
from pathlib import Path
import json

@dataclass
class CodeChange:
    """Represents a code change with context."""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    lines_changed: int
    complexity_delta: int
    related_files: List[str]

@dataclass
class ImpactAnalysis:
    """Analysis of how changes affect the broader codebase."""
    affected_modules: List[str]
    potential_breaking_changes: List[str]
    suggested_tests: List[str]
    documentation_updates: List[str]
    refactoring_opportunities: List[str]

class IntelligentWorkflowIntegrator:
    """
    Integrates codebase analysis intelligence into development workflows.

    This demonstrates how our pattern detection and architectural understanding
    can provide real-time guidance during development.
    """

    def __init__(self, analyzer_engine):
        self.analyzer = analyzer_engine
        self.change_history = []
        self.workflow_hooks = {}

    async def analyze_pre_commit(self, staged_files: List[str]) -> ImpactAnalysis:
        """
        Analyze staged changes before commit to provide intelligent insights.

        This is where our architectural understanding really shines - we can
        predict ripple effects and suggest improvements before code is committed.
        """
        analysis = ImpactAnalysis([], [], [], [], [])

        for file_path in staged_files:
            # Use our pattern detection to understand the change context
            patterns = await self.analyzer.detect_patterns_in_file(file_path)

            # Analyze architectural impact
            if any(p.pattern_type == 'architectural_boundary' for p in patterns):
                analysis.potential_breaking_changes.append(
                    f"Changes to {file_path} may affect module boundaries"
                )

            # Suggest related tests based on our dependency understanding
            related_test_files = await self._find_related_tests(file_path)
            analysis.suggested_tests.extend(related_test_files)

            # Identify refactoring opportunities
            if await self._detect_code_duplication(file_path):
                analysis.refactoring_opportunities.append(
                    f"Consider extracting common patterns from {file_path}"
                )

        return analysis

    async def generate_smart_pr_description(self, changed_files: List[str]) -> str:
        """
        Generate intelligent PR descriptions using our architectural understanding.

        Instead of generic descriptions, we can explain the architectural
        significance and impact of changes.
        """
        architectural_summary = await self.analyzer.analyze_architectural_changes(changed_files)

        description_parts = [
            "## Architectural Impact",
            architectural_summary.get('impact_summary', 'No significant architectural changes detected.'),
            "",
            "## Pattern Analysis"
        ]

        patterns_affected = architectural_summary.get('patterns_affected', [])
        if patterns_affected:
            for pattern in patterns_affected:
                description_parts.append(f"- **{pattern['type']}**: {pattern['description']}")
        else:
            description_parts.append("- No established patterns significantly modified")

        description_parts.extend([
            "",
            "## Suggested Review Focus",
            "Based on the architectural analysis, reviewers should pay particular attention to:"
        ])

        focus_areas = architectural_summary.get('review_focus', [])
        for area in focus_areas:
            description_parts.append(f"- {area}")

        return "\n".join(description_parts)

    async def suggest_refactoring_session(self, codebase_path: str) -> Dict:
        """
        Analyze the entire codebase and suggest a focused refactoring session.

        This uses our pattern detection to identify the highest-impact refactoring
        opportunities across the codebase.
        """
        all_patterns = await self.analyzer.analyze_full_codebase(codebase_path)

        # Group patterns by refactoring potential
        refactoring_opportunities = {
            'high_impact': [],
            'medium_impact': [],
            'low_impact': []
        }

        for pattern in all_patterns:
            impact_score = self._calculate_refactoring_impact(pattern)

            if impact_score > 8:
                refactoring_opportunities['high_impact'].append(pattern)
            elif impact_score > 5:
                refactoring_opportunities['medium_impact'].append(pattern)
            else:
                refactoring_opportunities['low_impact'].append(pattern)

        return {
            'opportunities': refactoring_opportunities,
            'suggested_order': self._prioritize_refactoring(refactoring_opportunities),
            'estimated_files_affected': self._estimate_refactoring_scope(refactoring_opportunities)
        }

    def register_workflow_hook(self, event: str, handler: Callable):
        """Register handlers for different workflow events."""
        if event not in self.workflow_hooks:
            self.workflow_hooks[event] = []
        self.workflow_hooks[event].append(handler)

    async def _find_related_tests(self, file_path: str) -> List[str]:
        """Find test files related to the changed file using our dependency analysis."""
        # This would use our architectural understanding to find related tests
        # For now, return a placeholder
        return [f"tests/test_{Path(file_path).stem}.py"]

    async def _detect_code_duplication(self, file_path: str) -> bool:
        """Detect if the file has patterns that suggest duplication."""
        # Use our pattern detection to identify duplication
        patterns = await self.analyzer.detect_patterns_in_file(file_path)
        return any(p.pattern_type == 'duplication' for p in patterns)

    def _calculate_refactoring_impact(self, pattern) -> int:
        """Calculate the potential impact of refactoring this pattern."""
        # Score based on complexity, number of files affected, etc.
        base_score = 5

        if pattern.complexity > 10:
            base_score += 3

        if len(pattern.affected_files) > 5:
            base_score += 2

        return min(base_score, 10)

    def _prioritize_refactoring(self, opportunities) -> List[str]:
        """Suggest the order for tackling refactoring opportunities."""
        # Start with high-impact, low-risk changes
        return [
            "Address high-impact architectural improvements first",
            "Focus on patterns affecting multiple modules",
            "Consider medium-impact changes that reduce complexity",
            "Low-impact changes can be addressed in maintenance cycles"
        ]

    def _estimate_refactoring_scope(self, opportunities) -> Dict[str, int]:
        """Estimate how many files would be affected by each category."""
        return {
            'high_impact': sum(len(getattr(op, 'affected_files', [])) for op in opportunities['high_impact']),
            'medium_impact': sum(len(getattr(op, 'affected_files', [])) for op in opportunities['medium_impact']),
            'low_impact': sum(len(getattr(op, 'affected_files', [])) for op in opportunities['low_impact'])
        }

# Example integration with popular development tools
class GitIntegration:
    """Example of how this could integrate with Git workflows."""

    def __init__(self, workflow_integrator: IntelligentWorkflowIntegrator):
        self.integrator = workflow_integrator

    async def pre_commit_hook(self):
        """Git pre-commit hook that provides intelligent analysis."""
        staged_files = self._get_staged_files()
        analysis = await self.integrator.analyze_pre_commit(staged_files)

        if analysis.potential_breaking_changes:
            print("⚠️  Potential breaking changes detected:")
            for change in analysis.potential_breaking_changes:
                print(f"   {change}")

            # Could prompt for confirmation or suggest alternatives

        if analysis.suggested_tests:
            print("🧪 Consider running these tests:")
            for test in analysis.suggested_tests:
                print(f"   {test}")

    def _get_staged_files(self) -> List[str]:
        """Get list of staged files (would use git commands in practice)."""
        return []  # Placeholder

# Example usage demonstrating the concept
async def demonstrate_workflow_integration():
    """Show how this would work in practice."""

    # This would connect to our actual analyzer
    analyzer = None  # Placeholder for our codebase analyzer
    integrator = IntelligentWorkflowIntegrator(analyzer)

    # Example: Pre-commit analysis
    print("=== Pre-commit Analysis ===")
    changed_files = ["src/analyzer.py", "src/patterns.py"]
    # analysis = await integrator.analyze_pre_commit(changed_files)

    print("=== Smart PR Description Generation ===")
    # pr_description = await integrator.generate_smart_pr_description(changed_files)
    # print(pr_description)

    print("=== Refactoring Session Planning ===")
    # refactoring_plan = await integrator.suggest_refactoring_session("/path/to/codebase")

    print("This demonstrates how AI-powered codebase analysis becomes a living")
    print("part of the development workflow, not just a one-time analysis tool.")

if __name__ == "__main__":
    asyncio.run(demonstrate_workflow_integration())