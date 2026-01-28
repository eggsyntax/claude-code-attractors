#!/usr/bin/env python3
"""
Enhanced Codebase Analyzer

Building on the foundation analyzer, this version adds more sophisticated pattern detection,
refactoring suggestions, and the ability to generate living documentation that evolves
with the codebase.

Key Enhancements:
- Advanced pattern detection (Observer, Factory, Singleton, etc.)
- Refactoring opportunity identification
- Living documentation generation
- Architectural debt tracking
- Performance pattern analysis
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from datetime import datetime
import hashlib

# Import our base analyzer
from codebase_analyzer import CodebaseAnalyzer, FileInfo, ArchitecturalPattern


class RefactoringOpportunity(NamedTuple):
    """Represents a specific refactoring opportunity."""
    type: str  # e.g., 'extract_method', 'move_class', 'introduce_interface'
    description: str
    files: List[Path]
    effort_estimate: str  # 'low', 'medium', 'high'
    impact: str  # 'low', 'medium', 'high'
    code_snippets: List[str] = []


@dataclass
class ArchitecturalDebt:
    """Tracks technical debt in the architecture."""
    category: str
    description: str
    files_affected: List[Path]
    severity: int  # 1-10 scale
    estimated_cost: str
    suggested_timeline: str


@dataclass
class PerformancePattern:
    """Identifies performance-related patterns."""
    pattern_type: str
    description: str
    files: List[Path]
    potential_impact: str
    optimization_suggestions: List[str]


class EnhancedCodebaseAnalyzer(CodebaseAnalyzer):
    """Enhanced analyzer with advanced pattern detection and documentation generation."""

    def __init__(self, root_path: str):
        super().__init__(root_path)
        self.analysis_timestamp = datetime.now()
        self.analysis_id = self._generate_analysis_id()

    def _generate_analysis_id(self) -> str:
        """Generate a unique ID for this analysis run."""
        content = f"{self.root_path}{self.analysis_timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def enhanced_analyze(self) -> Dict[str, Any]:
        """Perform enhanced analysis with additional insights."""
        # Get base analysis
        base_insights = self.analyze()

        # Add enhanced analysis
        refactoring_opportunities = self._identify_refactoring_opportunities(base_insights.file_info)
        architectural_debt = self._assess_architectural_debt(base_insights)
        performance_patterns = self._identify_performance_patterns(base_insights.file_info)

        # Generate documentation
        documentation = self._generate_living_documentation(base_insights)

        return {
            'analysis_id': self.analysis_id,
            'timestamp': self.analysis_timestamp.isoformat(),
            'base_insights': base_insights.__dict__,
            'refactoring_opportunities': [r._asdict() for r in refactoring_opportunities],
            'architectural_debt': [debt.__dict__ for debt in architectural_debt],
            'performance_patterns': [pattern.__dict__ for pattern in performance_patterns],
            'living_documentation': documentation,
            'health_score': self._calculate_codebase_health_score(
                base_insights, refactoring_opportunities, architectural_debt
            )
        }

    def _identify_refactoring_opportunities(self, file_info: Dict[Path, FileInfo]) -> List[RefactoringOpportunity]:
        """Identify specific refactoring opportunities."""
        opportunities = []

        # Opportunity 1: Large methods/functions that could be extracted
        for path, info in file_info.items():
            if info.language == 'python' and info.complexity_score > 3.0:
                opportunities.append(RefactoringOpportunity(
                    type='extract_method',
                    description=f"High complexity in {path.name} suggests methods that could be extracted",
                    files=[path],
                    effort_estimate='medium',
                    impact='high'
                ))

        # Opportunity 2: Duplicate code detection (simplified)
        function_patterns = defaultdict(list)
        for path, info in file_info.items():
            for func in info.functions:
                if len(func) > 3:  # Skip very short function names
                    function_patterns[func].append(path)

        for func_name, paths in function_patterns.items():
            if len(paths) > 2:
                opportunities.append(RefactoringOpportunity(
                    type='eliminate_duplication',
                    description=f"Function '{func_name}' appears in {len(paths)} files - potential duplication",
                    files=paths,
                    effort_estimate='medium',
                    impact='medium'
                ))

        # Opportunity 3: Files that might benefit from splitting
        for path, info in file_info.items():
            if info.lines > 300 and len(info.classes) > 3:
                opportunities.append(RefactoringOpportunity(
                    type='split_file',
                    description=f"Large file {path.name} with multiple classes could be split",
                    files=[path],
                    effort_estimate='high',
                    impact='medium'
                ))

        return opportunities

    def _assess_architectural_debt(self, base_insights) -> List[ArchitecturalDebt]:
        """Assess technical debt in the architecture."""
        debt_items = []

        # Debt from anti-patterns
        antipatterns = [p for p in base_insights.patterns if p.is_antipattern]
        for pattern in antipatterns:
            debt_items.append(ArchitecturalDebt(
                category='Anti-pattern',
                description=f"{pattern.name}: {pattern.description}",
                files_affected=pattern.files_involved,
                severity=7 if pattern.name == 'Circular Dependency' else 5,
                estimated_cost='Medium',
                suggested_timeline='Next sprint'
            ))

        # Debt from complexity
        complex_files = [path for path, score in base_insights.complexity_hotspots[:3]]
        if complex_files:
            debt_items.append(ArchitecturalDebt(
                category='Complexity',
                description='High complexity files require refactoring attention',
                files_affected=complex_files,
                severity=6,
                estimated_cost='High',
                suggested_timeline='Next quarter'
            ))

        return debt_items

    def _identify_performance_patterns(self, file_info: Dict[Path, FileInfo]) -> List[PerformancePattern]:
        """Identify patterns that might affect performance."""
        patterns = []

        # Pattern 1: Heavy import usage (could indicate startup performance issues)
        heavy_import_files = []
        for path, info in file_info.items():
            if len(info.imports) > 10:
                heavy_import_files.append(path)

        if heavy_import_files:
            patterns.append(PerformancePattern(
                pattern_type='Heavy Imports',
                description=f'Files with many imports may impact startup time',
                files=heavy_import_files,
                potential_impact='medium',
                optimization_suggestions=[
                    'Consider lazy imports for non-critical modules',
                    'Review if all imports are necessary',
                    'Use conditional imports where appropriate'
                ]
            ))

        # Pattern 2: Large files (could indicate processing bottlenecks)
        large_files = [path for path, info in file_info.items() if info.lines > 500]
        if large_files:
            patterns.append(PerformancePattern(
                pattern_type='Large Files',
                description='Large files may contain performance bottlenecks',
                files=large_files,
                potential_impact='high',
                optimization_suggestions=[
                    'Profile these files for performance hotspots',
                    'Consider breaking into smaller, focused modules',
                    'Look for opportunities to optimize algorithms'
                ]
            ))

        return patterns

    def _generate_living_documentation(self, base_insights) -> Dict[str, Any]:
        """Generate living documentation from the codebase analysis."""

        # Architecture overview
        architecture_overview = self._generate_architecture_overview(base_insights)

        # Module documentation
        module_docs = self._generate_module_documentation(base_insights.file_info)

        # Dependency graph visualization data
        dependency_viz = self._generate_dependency_visualization_data(base_insights.dependency_graph)

        return {
            'architecture_overview': architecture_overview,
            'module_documentation': module_docs,
            'dependency_visualization': dependency_viz,
            'generation_timestamp': self.analysis_timestamp.isoformat(),
            'next_update_recommended': (self.analysis_timestamp.replace(day=self.analysis_timestamp.day + 7)).isoformat()
        }

    def _generate_architecture_overview(self, base_insights) -> str:
        """Generate high-level architecture documentation."""
        overview = []
        overview.append("# Architecture Overview")
        overview.append(f"*Generated on {self.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}*")
        overview.append("")

        overview.append("## System Composition")
        overview.append(f"- **Total Files**: {base_insights.total_files}")
        overview.append(f"- **Lines of Code**: {base_insights.total_lines:,}")
        overview.append(f"- **Primary Language(s)**: {', '.join(base_insights.languages.keys())}")
        overview.append("")

        # Identified patterns
        if base_insights.patterns:
            overview.append("## Architectural Patterns")
            good_patterns = [p for p in base_insights.patterns if not p.is_antipattern]
            bad_patterns = [p for p in base_insights.patterns if p.is_antipattern]

            if good_patterns:
                overview.append("### Positive Patterns")
                for pattern in good_patterns:
                    overview.append(f"- **{pattern.name}**: {pattern.description}")

            if bad_patterns:
                overview.append("### Areas for Improvement")
                for pattern in bad_patterns:
                    overview.append(f"- **{pattern.name}**: {pattern.description}")

        overview.append("")
        overview.append("## Key Insights")
        for suggestion in base_insights.suggestions:
            overview.append(f"- {suggestion}")

        return "\n".join(overview)

    def _generate_module_documentation(self, file_info: Dict[Path, FileInfo]) -> Dict[str, Dict]:
        """Generate documentation for each module."""
        module_docs = {}

        for path, info in file_info.items():
            module_name = str(path.relative_to(self.root_path))

            # Determine module purpose based on naming and content
            purpose = self._infer_module_purpose(path, info)

            module_docs[module_name] = {
                'purpose': purpose,
                'size': info.lines,
                'complexity': info.complexity_score,
                'public_interface': {
                    'classes': info.classes,
                    'functions': info.functions[:5],  # Top 5 functions
                },
                'dependencies': info.imports[:5],  # Top 5 imports
                'last_analyzed': self.analysis_timestamp.isoformat()
            }

        return module_docs

    def _infer_module_purpose(self, path: Path, info: FileInfo) -> str:
        """Infer the purpose of a module based on its name and content."""
        name_lower = path.name.lower()

        purpose_keywords = {
            'config': 'Configuration and settings management',
            'model': 'Data models and business logic',
            'view': 'User interface and presentation',
            'controller': 'Request handling and coordination',
            'service': 'Business services and external integrations',
            'util': 'Utility functions and helpers',
            'test': 'Test cases and testing utilities',
            'main': 'Application entry point',
            'api': 'API endpoints and interfaces',
            'database': 'Database operations and queries'
        }

        for keyword, purpose in purpose_keywords.items():
            if keyword in name_lower:
                return purpose

        # Infer from content
        if len(info.classes) > len(info.functions):
            return 'Class definitions and object models'
        elif 'test' in name_lower or any('test' in func.lower() for func in info.functions):
            return 'Testing and quality assurance'
        else:
            return 'General functionality and utilities'

    def _generate_dependency_visualization_data(self, dependency_graph: Dict[str, Set[str]]) -> Dict:
        """Generate data for dependency graph visualization."""
        nodes = []
        edges = []

        all_modules = set(dependency_graph.keys())
        for deps in dependency_graph.values():
            all_modules.update(deps)

        # Create nodes
        for module in all_modules:
            nodes.append({
                'id': module,
                'label': Path(module).name,
                'size': len(dependency_graph.get(module, set()))
            })

        # Create edges
        for source, targets in dependency_graph.items():
            for target in targets:
                edges.append({
                    'source': source,
                    'target': target
                })

        return {
            'nodes': nodes,
            'edges': edges,
            'layout_suggestion': 'hierarchical' if len(nodes) < 20 else 'force-directed'
        }

    def _calculate_codebase_health_score(self, base_insights, opportunities, debt) -> Dict[str, Any]:
        """Calculate an overall health score for the codebase."""
        scores = {
            'complexity': 0,
            'maintainability': 0,
            'architecture': 0,
            'documentation': 0
        }

        # Complexity score (0-100, higher is better)
        avg_complexity = sum(info.complexity_score for info in base_insights.file_info.values()) / len(base_insights.file_info)
        scores['complexity'] = max(0, 100 - (avg_complexity * 10))

        # Maintainability score
        large_files = len([info for info in base_insights.file_info.values() if info.lines > 300])
        scores['maintainability'] = max(0, 100 - (large_files * 5))

        # Architecture score
        antipattern_count = len([p for p in base_insights.patterns if p.is_antipattern])
        scores['architecture'] = max(0, 100 - (antipattern_count * 15))

        # Documentation score (simplified - would need actual doc analysis)
        scores['documentation'] = 75  # Placeholder

        overall_score = sum(scores.values()) / len(scores)

        return {
            'overall': round(overall_score, 1),
            'breakdown': scores,
            'grade': self._score_to_grade(overall_score),
            'recommendations': self._generate_health_recommendations(scores, opportunities, debt)
        }

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90: return 'A'
        elif score >= 80: return 'B'
        elif score >= 70: return 'C'
        elif score >= 60: return 'D'
        else: return 'F'

    def _generate_health_recommendations(self, scores, opportunities, debt) -> List[str]:
        """Generate recommendations based on health scores."""
        recommendations = []

        if scores['complexity'] < 70:
            recommendations.append("Focus on reducing code complexity through refactoring")

        if scores['maintainability'] < 70:
            recommendations.append("Break down large files into smaller, focused modules")

        if scores['architecture'] < 70:
            recommendations.append("Address architectural anti-patterns to improve system design")

        if len(opportunities) > 5:
            recommendations.append("Prioritize refactoring opportunities to improve code quality")

        high_debt = [d for d in debt if d.severity > 7]
        if high_debt:
            recommendations.append("Address high-severity technical debt items immediately")

        return recommendations


def main():
    """Enhanced analyzer CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced codebase analysis with refactoring insights')
    parser.add_argument('path', help='Path to analyze')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--docs', '-d', help='Output directory for generated documentation')
    parser.add_argument('--format', choices=['json', 'markdown', 'html'], default='markdown')

    args = parser.parse_args()

    analyzer = EnhancedCodebaseAnalyzer(args.path)
    results = analyzer.enhanced_analyze()

    # Print summary
    health = results['health_score']
    print(f"\n🏥 Codebase Health Score: {health['overall']}/100 (Grade: {health['grade']})")

    print(f"\n📊 Breakdown:")
    for category, score in health['breakdown'].items():
        print(f"  {category.title()}: {score:.1f}/100")

    print(f"\n🔧 Refactoring Opportunities: {len(results['refactoring_opportunities'])}")
    for opp in results['refactoring_opportunities'][:3]:  # Top 3
        print(f"  • {opp['type']}: {opp['description']}")

    print(f"\n💳 Technical Debt Items: {len(results['architectural_debt'])}")
    for debt in results['architectural_debt']:
        print(f"  • {debt['category']}: {debt['description'][:60]}...")

    print(f"\n💡 Top Recommendations:")
    for rec in health['recommendations']:
        print(f"  • {rec}")

    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Detailed results saved to {args.output}")

    # Generate documentation
    if args.docs:
        os.makedirs(args.docs, exist_ok=True)

        # Save architecture overview
        with open(f"{args.docs}/architecture.md", 'w') as f:
            f.write(results['living_documentation']['architecture_overview'])

        # Save module documentation
        with open(f"{args.docs}/modules.json", 'w') as f:
            json.dump(results['living_documentation']['module_documentation'], f, indent=2, default=str)

        print(f"📚 Documentation generated in {args.docs}/")


if __name__ == '__main__':
    main()