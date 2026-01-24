#!/usr/bin/env python3
"""
Next-Generation Intelligent Codebase Analyzer
=============================================

An AI-powered tool for deep codebase analysis that combines multiple analysis techniques
to provide comprehensive insights about code structure, patterns, and improvement opportunities.

This represents the evolution of our codebase analysis discussion - incorporating:
- Advanced pattern detection beyond basic architectural patterns
- Context-aware analysis that understands relationships between files
- AI-generated insights and explanations
- Self-analysis capabilities for meta-learning
- Extensible plugin architecture

Usage:
    python intelligent_analyzer.py --path /path/to/codebase
    python intelligent_analyzer.py --analyze-self
    python intelligent_analyzer.py --interactive  # Interactive mode with AI insights
"""

import ast
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import argparse
import sys
from abc import ABC, abstractmethod


@dataclass
class CodeEntity:
    """Represents a code entity (function, class, etc.) with rich metadata."""
    name: str
    type: str  # 'function', 'class', 'method', 'variable'
    file_path: str
    line_start: int
    line_end: int
    complexity: float
    dependencies: List[str]
    patterns: List[str]
    docstring: Optional[str] = None
    parameters: List[str] = None
    return_type: Optional[str] = None


@dataclass
class ArchitecturalInsight:
    """Represents a high-level architectural insight."""
    category: str  # 'pattern', 'antipattern', 'suggestion', 'concern'
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    affected_files: List[str]
    severity: str  # 'low', 'medium', 'high', 'critical'
    ai_explanation: Optional[str] = None


@dataclass
class AnalysisResult:
    """Complete analysis results for a codebase."""
    codebase_path: str
    total_files: int
    total_lines: int
    entities: List[CodeEntity]
    insights: List[ArchitecturalInsight]
    dependency_graph: Dict[str, List[str]]
    complexity_metrics: Dict[str, float]
    quality_score: float
    recommendations: List[str]


class AnalysisPlugin(ABC):
    """Base class for analysis plugins."""

    @abstractmethod
    def analyze(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analysis and return results."""
        pass

    @abstractmethod
    def get_insights(self, results: Dict[str, Any]) -> List[ArchitecturalInsight]:
        """Generate insights from analysis results."""
        pass


class AdvancedPatternDetector(AnalysisPlugin):
    """Detects sophisticated architectural patterns and anti-patterns."""

    def __init__(self):
        self.pattern_signatures = {
            'strategy': self._detect_strategy,
            'decorator': self._detect_decorator,
            'command': self._detect_command,
            'adapter': self._detect_adapter,
            'facade': self._detect_facade,
            'circular_dependency': self._detect_circular_dependency,
            'data_clump': self._detect_data_clump,
            'shotgun_surgery': self._detect_shotgun_surgery
        }

    def analyze(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze file for advanced patterns."""
        results = {'patterns': [], 'antipatterns': [], 'entities': []}

        # Extract entities first
        entities = self._extract_entities(tree, file_path)
        results['entities'] = entities

        # Detect patterns
        for pattern_name, detector in self.pattern_signatures.items():
            if detector(tree, file_path, context):
                if pattern_name in ['circular_dependency', 'data_clump', 'shotgun_surgery']:
                    results['antipatterns'].append(pattern_name)
                else:
                    results['patterns'].append(pattern_name)

        return results

    def get_insights(self, results: Dict[str, Any]) -> List[ArchitecturalInsight]:
        """Generate insights from pattern detection results."""
        insights = []

        # Positive patterns
        for pattern in results.get('patterns', []):
            insights.append(ArchitecturalInsight(
                category='pattern',
                title=f"{pattern.title()} Pattern Detected",
                description=f"Implementation of {pattern} pattern found, promoting good architecture",
                confidence=0.8,
                affected_files=[],  # Would be populated in real implementation
                severity='low',
                ai_explanation=self._get_pattern_explanation(pattern)
            ))

        # Anti-patterns (more concerning)
        for antipattern in results.get('antipatterns', []):
            insights.append(ArchitecturalInsight(
                category='antipattern',
                title=f"{antipattern.replace('_', ' ').title()} Detected",
                description=f"Anti-pattern {antipattern} found - consider refactoring",
                confidence=0.7,
                affected_files=[],
                severity='medium',
                ai_explanation=self._get_antipattern_explanation(antipattern)
            ))

        return insights

    def _extract_entities(self, tree: ast.AST, file_path: str) -> List[CodeEntity]:
        """Extract code entities with rich metadata."""
        entities = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                entity = CodeEntity(
                    name=node.name,
                    type='function',
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=getattr(node, 'end_lineno', node.lineno),
                    complexity=self._calculate_function_complexity(node),
                    dependencies=self._extract_function_dependencies(node),
                    patterns=[],
                    docstring=ast.get_docstring(node),
                    parameters=[arg.arg for arg in node.args.args]
                )
                entities.append(entity)

            elif isinstance(node, ast.ClassDef):
                entity = CodeEntity(
                    name=node.name,
                    type='class',
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=getattr(node, 'end_lineno', node.lineno),
                    complexity=self._calculate_class_complexity(node),
                    dependencies=self._extract_class_dependencies(node),
                    patterns=[],
                    docstring=ast.get_docstring(node)
                )
                entities.append(entity)

        return entities

    def _calculate_function_complexity(self, node: ast.FunctionDef) -> float:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return float(complexity)

    def _calculate_class_complexity(self, node: ast.ClassDef) -> float:
        """Calculate complexity for a class."""
        total_complexity = 0
        method_count = 0

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                total_complexity += self._calculate_function_complexity(item)
                method_count += 1

        return total_complexity / max(method_count, 1)

    def _extract_function_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """Extract function dependencies."""
        dependencies = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                dependencies.append(child.func.id)
            elif isinstance(child, ast.Attribute):
                dependencies.append(f"{child.attr}")
        return list(set(dependencies))

    def _extract_class_dependencies(self, node: ast.ClassDef) -> List[str]:
        """Extract class dependencies."""
        dependencies = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                dependencies.append(base.id)
        return dependencies

    # Pattern detection methods
    def _detect_strategy(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> bool:
        """Detect Strategy pattern."""
        # Look for interface-like classes and implementations
        abstract_classes = []
        implementations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_abstract_methods = any(
                    isinstance(item, ast.FunctionDef) and
                    any(isinstance(dec, ast.Name) and dec.id == 'abstractmethod' for dec in item.decorator_list)
                    for item in node.body
                )
                if has_abstract_methods:
                    abstract_classes.append(node.name)
                elif node.bases:  # Has inheritance
                    implementations.append(node.name)

        return len(abstract_classes) > 0 and len(implementations) > 1

    def _detect_decorator(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> bool:
        """Detect Decorator pattern."""
        # Look for classes that wrap other objects
        decorator_indicators = ['wrapper', 'decorator', 'proxy']

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name_lower = node.name.lower()
                if any(indicator in class_name_lower for indicator in decorator_indicators):
                    # Check if it has composition (holds reference to another object)
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                            return True
        return False

    def _detect_command(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> bool:
        """Detect Command pattern."""
        command_indicators = ['execute', 'undo', 'command']
        has_execute = False
        has_undo = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                name_lower = node.name.lower()
                if 'execute' in name_lower:
                    has_execute = True
                if 'undo' in name_lower:
                    has_undo = True

        return has_execute and has_undo

    def _detect_adapter(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> bool:
        """Detect Adapter pattern."""
        adapter_indicators = ['adapter', 'wrapper']

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name_lower = node.name.lower()
                if any(indicator in class_name_lower for indicator in adapter_indicators):
                    # Should have composition and delegation
                    return len(node.bases) > 0 or any(
                        isinstance(item, ast.FunctionDef)
                        for item in node.body
                    )
        return False

    def _detect_facade(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> bool:
        """Detect Facade pattern."""
        facade_indicators = ['facade', 'manager', 'service']

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name_lower = node.name.lower()
                if any(indicator in class_name_lower for indicator in facade_indicators):
                    # Should have methods that delegate to other objects
                    method_count = len([item for item in node.body if isinstance(item, ast.FunctionDef)])
                    return method_count > 3  # Arbitrary threshold
        return False

    def _detect_circular_dependency(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> bool:
        """Detect potential circular dependencies."""
        # This is simplified - real detection requires cross-file analysis
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                else:
                    module = node.module or ""
                    imports.append(module)

        # Check if current file might create circular import
        current_module = Path(file_path).stem
        return any(current_module in imp for imp in imports)

    def _detect_data_clump(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> bool:
        """Detect data clump anti-pattern."""
        # Look for functions with many parameters
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 5:  # Threshold for "too many parameters"
                    return True
        return False

    def _detect_shotgun_surgery(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> bool:
        """Detect shotgun surgery anti-pattern (simplified)."""
        # This requires cross-file analysis in reality
        # For now, detect files with many small functions (potential indicator)
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        total_lines = tree.end_lineno if hasattr(tree, 'end_lineno') else 100

        if function_count > 10 and total_lines / function_count < 10:
            return True
        return False

    def _get_pattern_explanation(self, pattern: str) -> str:
        """Get AI-style explanation for detected patterns."""
        explanations = {
            'strategy': "The Strategy pattern allows algorithms to be selected at runtime. This promotes flexibility and follows the open/closed principle.",
            'decorator': "The Decorator pattern allows behavior to be added to objects dynamically without altering their structure.",
            'command': "The Command pattern encapsulates requests as objects, allowing you to parameterize clients with different requests and support undo operations.",
            'adapter': "The Adapter pattern allows incompatible interfaces to work together by creating a wrapper that translates one interface to another.",
            'facade': "The Facade pattern provides a simplified interface to a complex subsystem, making it easier to use."
        }
        return explanations.get(pattern, f"Pattern {pattern} detected with good architectural implications.")

    def _get_antipattern_explanation(self, antipattern: str) -> str:
        """Get AI-style explanation for detected anti-patterns."""
        explanations = {
            'circular_dependency': "Circular dependencies create tight coupling and can lead to import errors. Consider restructuring dependencies or using dependency injection.",
            'data_clump': "Functions with many parameters often indicate that related data should be grouped into objects or data structures.",
            'shotgun_surgery': "Many small, scattered functions might indicate that related functionality should be consolidated or better organized."
        }
        return explanations.get(antipattern, f"Anti-pattern {antipattern} detected - consider refactoring for better maintainability.")


class AIInsightsEngine(AnalysisPlugin):
    """Generates AI-powered insights and recommendations."""

    def analyze(self, tree: ast.AST, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for AI insights."""
        insights = {
            'code_quality': self._assess_code_quality(tree),
            'maintainability': self._assess_maintainability(tree),
            'complexity_hotspots': self._identify_complexity_hotspots(tree),
            'improvement_suggestions': self._generate_suggestions(tree, file_path)
        }
        return insights

    def get_insights(self, results: Dict[str, Any]) -> List[ArchitecturalInsight]:
        """Generate architectural insights from AI analysis."""
        insights = []

        # Code quality insights
        quality_score = results.get('code_quality', 0.5)
        if quality_score < 0.6:
            insights.append(ArchitecturalInsight(
                category='concern',
                title="Code Quality Below Threshold",
                description=f"Code quality score: {quality_score:.2f}. Consider improving documentation, reducing complexity, and following best practices.",
                confidence=0.8,
                affected_files=[],
                severity='medium',
                ai_explanation="Low code quality can lead to maintenance difficulties and increased bug rates."
            ))

        # Complexity hotspots
        hotspots = results.get('complexity_hotspots', [])
        if hotspots:
            insights.append(ArchitecturalInsight(
                category='suggestion',
                title="Complexity Hotspots Identified",
                description=f"Found {len(hotspots)} complexity hotspots that could benefit from refactoring.",
                confidence=0.9,
                affected_files=[],
                severity='medium',
                ai_explanation="High complexity areas are harder to understand, test, and maintain."
            ))

        return insights

    def _assess_code_quality(self, tree: ast.AST) -> float:
        """Assess overall code quality (0.0 to 1.0)."""
        score = 0.5  # Base score

        # Check for docstrings
        functions_with_docs = 0
        total_functions = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if ast.get_docstring(node):
                    functions_with_docs += 1

        if total_functions > 0:
            doc_ratio = functions_with_docs / total_functions
            score += doc_ratio * 0.3

        # Check naming conventions
        good_names = 0
        total_names = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                total_names += 1
                if self._is_good_name(node.name, isinstance(node, ast.ClassDef)):
                    good_names += 1

        if total_names > 0:
            naming_ratio = good_names / total_names
            score += naming_ratio * 0.2

        return min(score, 1.0)

    def _is_good_name(self, name: str, is_class: bool) -> bool:
        """Check if a name follows good conventions."""
        if is_class:
            return name[0].isupper() and '_' not in name  # PascalCase
        else:
            return name.islower() or '_' in name  # snake_case

    def _assess_maintainability(self, tree: ast.AST) -> float:
        """Assess maintainability score."""
        # Simplified maintainability assessment
        complexity_penalty = 0
        function_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_count += 1
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    complexity_penalty += 1

        if function_count == 0:
            return 0.5

        maintainability = 1.0 - (complexity_penalty / function_count)
        return max(maintainability, 0.0)

    def _identify_complexity_hotspots(self, tree: ast.AST) -> List[str]:
        """Identify functions/classes with high complexity."""
        hotspots = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > 8:
                    hotspots.append(f"Function '{node.name}' (complexity: {complexity})")

        return hotspots

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
        return complexity

    def _generate_suggestions(self, tree: ast.AST, file_path: str) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []

        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and len(node.body) > 20:
                suggestions.append(f"Consider breaking down function '{node.name}' - it has {len(node.body)} statements")

        # Check for missing docstrings
        functions_without_docs = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node)
        ]

        if functions_without_docs:
            suggestions.append(f"Add docstrings to functions: {', '.join(functions_without_docs[:3])}")

        return suggestions


class IntelligentCodebaseAnalyzer:
    """Main analyzer that orchestrates multiple analysis plugins."""

    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        self.plugins = [
            AdvancedPatternDetector(),
            AIInsightsEngine()
        ]
        self.analysis_cache = {}

    def analyze(self, interactive: bool = False) -> AnalysisResult:
        """Perform comprehensive codebase analysis."""
        print(f"🚀 Starting intelligent analysis of: {self.codebase_path}")

        # Find Python files
        python_files = list(self.codebase_path.rglob("*.py"))
        print(f"📁 Found {len(python_files)} Python files")

        all_entities = []
        all_insights = []
        total_lines = 0

        # Analyze each file with all plugins
        for file_path in python_files:
            print(f"🔍 Analyzing: {file_path.relative_to(self.codebase_path)}")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_lines += len(content.splitlines())

                tree = ast.parse(content)

                # Run all plugins
                for plugin in self.plugins:
                    plugin_results = plugin.analyze(tree, str(file_path), {})
                    plugin_insights = plugin.get_insights(plugin_results)

                    # Collect entities and insights
                    if 'entities' in plugin_results:
                        all_entities.extend(plugin_results['entities'])

                    all_insights.extend(plugin_insights)

                if interactive:
                    self._show_file_summary(file_path, tree)

            except Exception as e:
                print(f"⚠️  Error analyzing {file_path}: {e}")

        # Generate final analysis result
        result = AnalysisResult(
            codebase_path=str(self.codebase_path),
            total_files=len(python_files),
            total_lines=total_lines,
            entities=all_entities,
            insights=all_insights,
            dependency_graph=self._build_dependency_graph(all_entities),
            complexity_metrics=self._calculate_metrics(all_entities),
            quality_score=self._calculate_quality_score(all_insights),
            recommendations=self._generate_recommendations(all_insights)
        )

        return result

    def _show_file_summary(self, file_path: Path, tree: ast.AST):
        """Show interactive summary for a file."""
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        print(f"  📋 Functions: {', '.join(functions[:3])}{' ...' if len(functions) > 3 else ''}")
        print(f"  📋 Classes: {', '.join(classes[:3])}{' ...' if len(classes) > 3 else ''}")

    def _build_dependency_graph(self, entities: List[CodeEntity]) -> Dict[str, List[str]]:
        """Build a dependency graph from entities."""
        graph = defaultdict(list)

        for entity in entities:
            file_key = Path(entity.file_path).name
            graph[file_key].extend(entity.dependencies)

        return dict(graph)

    def _calculate_metrics(self, entities: List[CodeEntity]) -> Dict[str, float]:
        """Calculate overall complexity metrics."""
        if not entities:
            return {'avg_complexity': 0.0, 'max_complexity': 0.0}

        complexities = [entity.complexity for entity in entities]

        return {
            'avg_complexity': sum(complexities) / len(complexities),
            'max_complexity': max(complexities),
            'total_entities': len(entities)
        }

    def _calculate_quality_score(self, insights: List[ArchitecturalInsight]) -> float:
        """Calculate overall quality score based on insights."""
        if not insights:
            return 0.7  # Neutral score

        positive_score = sum(1 for insight in insights if insight.category == 'pattern')
        negative_score = sum(1 for insight in insights if insight.category in ['antipattern', 'concern'])

        total_insights = len(insights)
        score = 0.5 + (positive_score - negative_score) / (total_insights * 2)

        return max(0.0, min(1.0, score))

    def _generate_recommendations(self, insights: List[ArchitecturalInsight]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Group insights by category
        concerns = [i for i in insights if i.category == 'concern']
        antipatterns = [i for i in insights if i.category == 'antipattern']
        suggestions = [i for i in insights if i.category == 'suggestion']

        if concerns:
            recommendations.append(f"Address {len(concerns)} code quality concerns for better maintainability")

        if antipatterns:
            recommendations.append(f"Refactor {len(antipatterns)} detected anti-patterns to improve architecture")

        if suggestions:
            recommendations.append(f"Consider {len(suggestions)} improvement suggestions for enhanced code quality")

        return recommendations

    def generate_report(self, result: AnalysisResult, output_path: Optional[str] = None) -> str:
        """Generate a comprehensive analysis report."""
        report = self._format_intelligent_report(result)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"📄 Intelligent report saved to: {output_path}")

        return report

    def _format_intelligent_report(self, result: AnalysisResult) -> str:
        """Format an intelligent, AI-powered report."""
        report = f"""# 🧠 Intelligent Codebase Analysis Report

## 📊 Executive Summary
- **Codebase Path**: `{result.codebase_path}`
- **Files Analyzed**: {result.total_files}
- **Lines of Code**: {result.total_lines:,}
- **Code Entities**: {len(result.entities)}
- **Overall Quality Score**: {result.quality_score:.2f}/1.0 {'🟢' if result.quality_score > 0.7 else '🟡' if result.quality_score > 0.5 else '🔴'}

## 🔍 Key Insights

"""

        # Group insights by category
        patterns = [i for i in result.insights if i.category == 'pattern']
        antipatterns = [i for i in result.insights if i.category == 'antipattern']
        concerns = [i for i in result.insights if i.category == 'concern']
        suggestions = [i for i in result.insights if i.category == 'suggestion']

        if patterns:
            report += "### ✅ Positive Patterns Detected\n"
            for pattern in patterns:
                report += f"- **{pattern.title}** (Confidence: {pattern.confidence:.0%})\n"
                report += f"  {pattern.ai_explanation}\n\n"

        if antipatterns:
            report += "### ⚠️ Anti-patterns Requiring Attention\n"
            for antipattern in antipatterns:
                report += f"- **{antipattern.title}** (Severity: {antipattern.severity})\n"
                report += f"  {antipattern.ai_explanation}\n\n"

        if concerns:
            report += "### 🔍 Code Quality Concerns\n"
            for concern in concerns:
                report += f"- **{concern.title}**\n"
                report += f"  {concern.description}\n\n"

        # Complexity metrics
        metrics = result.complexity_metrics
        report += f"""## 📈 Complexity Metrics
- **Average Complexity**: {metrics.get('avg_complexity', 0):.1f}
- **Maximum Complexity**: {metrics.get('max_complexity', 0):.1f}
- **Total Entities**: {metrics.get('total_entities', 0)}

## 💡 AI-Powered Recommendations

"""

        for i, recommendation in enumerate(result.recommendations, 1):
            report += f"{i}. {recommendation}\n"

        # Entity breakdown
        if result.entities:
            report += "\n## 📋 Entity Analysis\n\n"

            # Top complex entities
            complex_entities = sorted(result.entities, key=lambda e: e.complexity, reverse=True)[:5]
            if complex_entities:
                report += "### Most Complex Entities\n"
                for entity in complex_entities:
                    file_name = Path(entity.file_path).name
                    report += f"- **{entity.name}** ({entity.type}) in `{file_name}` - Complexity: {entity.complexity:.1f}\n"

        report += f"""

## 🎯 Next Steps

Based on this analysis, consider focusing on:

1. **High Priority**: Address anti-patterns and critical concerns
2. **Medium Priority**: Reduce complexity in hotspot functions/classes
3. **Low Priority**: Enhance documentation and code style consistency

---

*Generated by Intelligent Codebase Analyzer - AI-powered code analysis for better software architecture*
"""

        return report


def main():
    """Main entry point with enhanced CLI."""
    parser = argparse.ArgumentParser(description="Intelligent Codebase Analyzer with AI insights")
    parser.add_argument("--path", help="Path to the codebase to analyze")
    parser.add_argument("--analyze-self", action="store_true", help="Analyze this analyzer tool itself")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode with detailed output")
    parser.add_argument("--output", help="Output file for the report (default: intelligent_analysis_report.md)")

    args = parser.parse_args()

    if args.analyze_self:
        codebase_path = Path(__file__).parent
        print("🔄 Meta-analysis: Analyzing the intelligent analyzer itself!")
    elif args.path:
        codebase_path = Path(args.path)
    else:
        print("❓ Please specify --path <codebase_path> or --analyze-self")
        print("\nExample usage:")
        print("  python intelligent_analyzer.py --path /path/to/your/project")
        print("  python intelligent_analyzer.py --analyze-self --interactive")
        return

    if not codebase_path.exists():
        print(f"❌ Path does not exist: {codebase_path}")
        return

    try:
        # Perform intelligent analysis
        analyzer = IntelligentCodebaseAnalyzer(codebase_path)
        result = analyzer.analyze(interactive=args.interactive)

        # Generate report
        output_path = args.output or "intelligent_analysis_report.md"
        report = analyzer.generate_report(result, output_path)

        # Summary
        print("\n" + "="*70)
        print("🎉 INTELLIGENT ANALYSIS COMPLETE!")
        print("="*70)
        print(f"📊 Quality Score: {result.quality_score:.2f}/1.0")
        print(f"🎯 Insights Generated: {len(result.insights)}")
        print(f"💡 Recommendations: {len(result.recommendations)}")
        print(f"📄 Full report: {output_path}")

        # Show key insights
        if result.insights:
            print(f"\n🔍 Key Findings:")
            for insight in result.insights[:3]:  # Show top 3
                print(f"  • {insight.title}")

        if result.recommendations:
            print(f"\n💡 Top Recommendations:")
            for rec in result.recommendations[:2]:  # Show top 2
                print(f"  • {rec}")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()