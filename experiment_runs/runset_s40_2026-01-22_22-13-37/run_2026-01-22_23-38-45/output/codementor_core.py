#!/usr/bin/env python3
"""
CodeMentor - Collaborative Code Review Assistant
Core Analysis Engine

This module provides the foundational code analysis capabilities for CodeMentor,
a tool designed to help developers understand code patterns, architectural decisions,
and collaborate more effectively on code reviews.

Author: Alice (Claude Code Instance)
Collaboration Partner: Bob (Claude Code Instance)
"""

import ast
import os
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import re


@dataclass
class CodePattern:
    """Represents a detected code pattern with context and suggestions."""
    name: str
    description: str
    file_path: str
    line_start: int
    line_end: int
    confidence: float
    suggestions: List[str]
    educational_context: str


@dataclass
class ArchitecturalInsight:
    """High-level architectural observations about the codebase."""
    pattern_type: str
    description: str
    files_involved: List[str]
    impact_level: str  # "high", "medium", "low"
    recommendations: List[str]


class CodeAnalysisEngine:
    """
    Core engine for analyzing code patterns and architectural decisions.

    This engine focuses on detecting common patterns, anti-patterns, and
    architectural structures that can help developers understand and improve
    their codebase.
    """

    def __init__(self):
        self.detected_patterns: List[CodePattern] = []
        self.architectural_insights: List[ArchitecturalInsight] = []

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single Python file for patterns and issues.

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            Dictionary containing analysis results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content, filename=file_path)

            # Run various pattern detectors
            patterns = []
            patterns.extend(self._detect_design_patterns(tree, file_path, content))
            patterns.extend(self._detect_code_smells(tree, file_path, content))
            patterns.extend(self._detect_architectural_patterns(tree, file_path))

            return {
                'file_path': file_path,
                'patterns': patterns,
                'metrics': self._calculate_metrics(tree, content)
            }

        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'patterns': [],
                'metrics': {}
            }

    def _detect_design_patterns(self, tree: ast.AST, file_path: str, content: str) -> List[CodePattern]:
        """Detect common design patterns in the code."""
        patterns = []

        # Singleton pattern detection
        singleton_pattern = self._detect_singleton_pattern(tree, file_path)
        if singleton_pattern:
            patterns.append(singleton_pattern)

        # Factory pattern detection
        factory_pattern = self._detect_factory_pattern(tree, file_path)
        if factory_pattern:
            patterns.append(factory_pattern)

        # Observer pattern detection
        observer_pattern = self._detect_observer_pattern(tree, file_path)
        if observer_pattern:
            patterns.append(observer_pattern)

        return patterns

    def _detect_code_smells(self, tree: ast.AST, file_path: str, content: str) -> List[CodePattern]:
        """Detect potential code smells and anti-patterns."""
        patterns = []
        lines = content.split('\n')

        # Long method detection
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if method_lines > 50:  # Configurable threshold
                    patterns.append(CodePattern(
                        name="Long Method",
                        description=f"Method '{node.name}' is {method_lines} lines long",
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        confidence=0.8,
                        suggestions=[
                            "Consider breaking this method into smaller, focused functions",
                            "Look for logical groupings that can be extracted",
                            "Apply the Single Responsibility Principle"
                        ],
                        educational_context="Long methods violate the Single Responsibility Principle and are harder to test, understand, and maintain."
                    ))

        # Large class detection
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                if len(methods) > 20:  # Configurable threshold
                    patterns.append(CodePattern(
                        name="Large Class",
                        description=f"Class '{node.name}' has {len(methods)} methods",
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        confidence=0.7,
                        suggestions=[
                            "Consider splitting this class based on responsibilities",
                            "Look for cohesive groups of methods that could form separate classes",
                            "Apply the Single Responsibility Principle"
                        ],
                        educational_context="Large classes often violate the Single Responsibility Principle and become difficult to maintain and test."
                    ))

        return patterns

    def _detect_architectural_patterns(self, tree: ast.AST, file_path: str) -> List[CodePattern]:
        """Detect architectural patterns and structures."""
        patterns = []

        # MVC pattern indicators
        if 'controller' in file_path.lower() or 'view' in file_path.lower() or 'model' in file_path.lower():
            patterns.append(CodePattern(
                name="MVC Architecture",
                description="File appears to be part of MVC architecture",
                file_path=file_path,
                line_start=1,
                line_end=1,
                confidence=0.6,
                suggestions=[
                    "Ensure clear separation of concerns between model, view, and controller",
                    "Keep controllers thin and delegate business logic to models"
                ],
                educational_context="MVC (Model-View-Controller) separates application logic into three interconnected components."
            ))

        return patterns

    def _detect_singleton_pattern(self, tree: ast.AST, file_path: str) -> Optional[CodePattern]:
        """Detect singleton pattern implementation."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for __new__ method that might implement singleton
                for item in node.body:
                    if (isinstance(item, ast.FunctionDef) and
                        item.name == '__new__'):
                        return CodePattern(
                            name="Singleton Pattern",
                            description=f"Class '{node.name}' appears to implement Singleton pattern",
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            confidence=0.7,
                            suggestions=[
                                "Consider if singleton is necessary - it can make testing difficult",
                                "Consider dependency injection as an alternative",
                                "Ensure thread safety if used in multi-threaded environment"
                            ],
                            educational_context="Singleton pattern ensures a class has only one instance and provides global access to it."
                        )
        return None

    def _detect_factory_pattern(self, tree: ast.AST, file_path: str) -> Optional[CodePattern]:
        """Detect factory pattern implementation."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if ('create' in node.name.lower() or
                    'factory' in node.name.lower() or
                    'build' in node.name.lower()):
                    # Simple heuristic - could be more sophisticated
                    return CodePattern(
                        name="Factory Pattern",
                        description=f"Function '{node.name}' appears to implement Factory pattern",
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        confidence=0.5,
                        suggestions=[
                            "Ensure the factory encapsulates object creation logic",
                            "Consider abstract factory if multiple product families exist"
                        ],
                        educational_context="Factory pattern creates objects without specifying their exact classes."
                    )
        return None

    def _detect_observer_pattern(self, tree: ast.AST, file_path: str) -> Optional[CodePattern]:
        """Detect observer pattern implementation."""
        observer_indicators = ['observer', 'listener', 'subscriber', 'notify', 'subscribe']

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name_lower = node.name.lower()
                if any(indicator in class_name_lower for indicator in observer_indicators):
                    return CodePattern(
                        name="Observer Pattern",
                        description=f"Class '{node.name}' appears to implement Observer pattern",
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        confidence=0.6,
                        suggestions=[
                            "Ensure loose coupling between subject and observers",
                            "Consider using weak references to prevent memory leaks"
                        ],
                        educational_context="Observer pattern defines a one-to-many dependency between objects."
                    )
        return None

    def _calculate_metrics(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Calculate various code metrics."""
        lines = content.split('\n')

        metrics = {
            'total_lines': len(lines),
            'blank_lines': len([line for line in lines if not line.strip()]),
            'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
            'classes': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
            'functions': len([node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]),
            'imports': len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
        }

        # Calculate code complexity (simplified McCabe)
        complexity = self._calculate_complexity(tree)
        metrics['cyclomatic_complexity'] = complexity

        return metrics

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate a simplified cyclomatic complexity score."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            # Decision points increase complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try,
                                ast.With, ast.Assert, ast.Raise)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1

        return complexity

    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """
        Analyze an entire project directory for patterns and architecture.

        Args:
            project_path: Path to the project root directory

        Returns:
            Comprehensive analysis results
        """
        results = {
            'project_path': project_path,
            'files_analyzed': [],
            'patterns_summary': {},
            'architectural_insights': [],
            'recommendations': []
        }

        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk(project_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]

            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        # Analyze each file
        all_patterns = []
        for file_path in python_files:
            file_result = self.analyze_file(file_path)
            results['files_analyzed'].append(file_result)
            all_patterns.extend(file_result.get('patterns', []))

        # Summarize patterns
        pattern_counts = {}
        for pattern in all_patterns:
            pattern_counts[pattern.name] = pattern_counts.get(pattern.name, 0) + 1
        results['patterns_summary'] = pattern_counts

        # Generate architectural insights
        results['architectural_insights'] = self._generate_architectural_insights(python_files, all_patterns)

        # Generate recommendations
        results['recommendations'] = self._generate_project_recommendations(all_patterns, pattern_counts)

        return results

    def _generate_architectural_insights(self, files: List[str], patterns: List[CodePattern]) -> List[ArchitecturalInsight]:
        """Generate high-level architectural insights from the analysis."""
        insights = []

        # Directory structure analysis
        directories = set(os.path.dirname(f) for f in files)
        if len(directories) > 5:
            insights.append(ArchitecturalInsight(
                pattern_type="Project Structure",
                description=f"Project has {len(directories)} different directories, suggesting modular organization",
                files_involved=list(directories),
                impact_level="medium",
                recommendations=[
                    "Ensure each module has a clear responsibility",
                    "Consider documenting the module architecture"
                ]
            ))

        # Pattern distribution analysis
        singleton_count = len([p for p in patterns if p.name == "Singleton Pattern"])
        if singleton_count > 3:
            insights.append(ArchitecturalInsight(
                pattern_type="Design Pattern Usage",
                description=f"Heavy use of Singleton pattern ({singleton_count} instances) detected",
                files_involved=[p.file_path for p in patterns if p.name == "Singleton Pattern"],
                impact_level="high",
                recommendations=[
                    "Review if all singletons are necessary",
                    "Consider dependency injection for better testability",
                    "Ensure singleton implementations are thread-safe"
                ]
            ))

        return insights

    def _generate_project_recommendations(self, patterns: List[CodePattern], pattern_counts: Dict[str, int]) -> List[str]:
        """Generate project-level recommendations based on analysis."""
        recommendations = []

        # Code smell recommendations
        if pattern_counts.get("Long Method", 0) > 5:
            recommendations.append(
                f"Consider refactoring {pattern_counts['Long Method']} long methods to improve maintainability"
            )

        if pattern_counts.get("Large Class", 0) > 2:
            recommendations.append(
                f"Review {pattern_counts['Large Class']} large classes for single responsibility principle violations"
            )

        # Architecture recommendations
        total_patterns = sum(pattern_counts.values())
        if total_patterns > 20:
            recommendations.append(
                "High pattern density detected - consider code review sessions to address technical debt"
            )

        return recommendations

    def export_results(self, results: Dict[str, Any], output_file: str) -> None:
        """Export analysis results to a JSON file."""
        # Convert CodePattern objects to dictionaries for JSON serialization
        def convert_patterns(obj):
            if isinstance(obj, CodePattern):
                return asdict(obj)
            elif isinstance(obj, ArchitecturalInsight):
                return asdict(obj)
            elif isinstance(obj, list):
                return [convert_patterns(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_patterns(value) for key, value in obj.items()}
            return obj

        serializable_results = convert_patterns(results)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)


def main():
    """Example usage of the CodeMentor analysis engine."""
    engine = CodeAnalysisEngine()

    # Example: analyze this very file
    current_file = __file__
    print(f"Analyzing {current_file}...")

    result = engine.analyze_file(current_file)
    print(f"\nFound {len(result['patterns'])} patterns:")

    for pattern in result['patterns']:
        print(f"- {pattern.name}: {pattern.description}")
        print(f"  Lines {pattern.line_start}-{pattern.line_end}, Confidence: {pattern.confidence}")
        print(f"  Suggestions: {', '.join(pattern.suggestions[:2])}...")
        print()


if __name__ == "__main__":
    main()