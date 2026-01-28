#!/usr/bin/env python3
"""
Intelligent Codebase Analyzer
============================

A comprehensive tool for analyzing codebases to understand structure, identify patterns,
and suggest improvements. This analyzer provides insights into:

- Architectural patterns and anti-patterns
- Code quality metrics and issues
- Refactoring opportunities
- Dependency relationships
- Documentation gaps

Usage:
    python codebase_analyzer.py <path_to_codebase>

Example:
    python codebase_analyzer.py ./my_project --output report.md --json
"""

import os
import ast
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import re


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""
    path: str
    language: str
    lines_of_code: int
    complexity_score: float
    imports: List[str]
    exports: List[str]
    functions: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    issues: List[Dict[str, str]]


@dataclass
class ArchitecturalPattern:
    """Detected architectural pattern in the codebase."""
    name: str
    confidence: float
    description: str
    evidence: List[str]
    files_involved: List[str]


@dataclass
class CodebaseAnalysis:
    """Complete analysis results for a codebase."""
    total_files: int
    total_loc: int
    languages: Dict[str, int]
    file_analyses: List[FileAnalysis]
    architectural_patterns: List[ArchitecturalPattern]
    dependency_graph: Dict[str, List[str]]
    quality_metrics: Dict[str, Any]
    suggestions: List[Dict[str, str]]


class PythonFileAnalyzer:
    """Analyzer for Python files using AST parsing."""

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            return FileAnalysis(
                path=str(file_path),
                language='python',
                lines_of_code=len([line for line in content.split('\n') if line.strip()]),
                complexity_score=self._calculate_complexity(tree),
                imports=self._extract_imports(tree),
                exports=self._extract_exports(tree),
                functions=self._extract_functions(tree),
                classes=self._extract_classes(tree),
                issues=self._detect_issues(tree, content)
            )
        except Exception as e:
            return FileAnalysis(
                path=str(file_path),
                language='python',
                lines_of_code=0,
                complexity_score=0,
                imports=[],
                exports=[],
                functions=[],
                classes=[],
                issues=[{'type': 'parse_error', 'message': str(e)}]
            )

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity approximation."""
        complexity = 1  # Base complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity / 10.0  # Normalize to 0-10 scale

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.append(f"{node.module}.{alias.name}")
        return imports

    def _extract_exports(self, tree: ast.AST) -> List[str]:
        """Extract exported functions/classes."""
        exports = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not node.name.startswith('_'):
                    exports.append(node.name)
        return exports

    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function information."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'line_number': node.lineno,
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'is_private': node.name.startswith('_')
                })
        return functions

    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class information."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body
                          if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                classes.append({
                    'name': node.name,
                    'bases': [base.id if isinstance(base, ast.Name) else str(base)
                             for base in node.bases],
                    'methods': methods,
                    'line_number': node.lineno
                })
        return classes

    def _detect_issues(self, tree: ast.AST, content: str) -> List[Dict[str, str]]:
        """Detect potential code issues."""
        issues = []

        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                if len(func_lines) > 50:
                    issues.append({
                        'type': 'long_function',
                        'message': f"Function '{node.name}' is very long ({len(func_lines)} lines)"
                    })

        return issues


class ArchitecturalPatternDetector:
    """Detects common architectural patterns in codebases."""

    def detect_patterns(self, analyses: List[FileAnalysis]) -> List[ArchitecturalPattern]:
        """Detect architectural patterns from file analyses."""
        patterns = []

        # Detect MVC pattern
        mvc_pattern = self._detect_mvc_pattern(analyses)
        if mvc_pattern:
            patterns.append(mvc_pattern)

        # Detect Factory pattern
        factory_pattern = self._detect_factory_pattern(analyses)
        if factory_pattern:
            patterns.append(factory_pattern)

        # Detect Singleton pattern
        singleton_pattern = self._detect_singleton_pattern(analyses)
        if singleton_pattern:
            patterns.append(singleton_pattern)

        return patterns

    def _detect_mvc_pattern(self, analyses: List[FileAnalysis]) -> Optional[ArchitecturalPattern]:
        """Detect Model-View-Controller pattern."""
        mvc_files = {'models': [], 'views': [], 'controllers': []}

        for analysis in analyses:
            path_lower = analysis.path.lower()
            if 'model' in path_lower:
                mvc_files['models'].append(analysis.path)
            elif 'view' in path_lower:
                mvc_files['views'].append(analysis.path)
            elif 'controller' in path_lower:
                mvc_files['controllers'].append(analysis.path)

        if all(mvc_files.values()):  # All three components present
            return ArchitecturalPattern(
                name='MVC',
                confidence=0.8,
                description='Model-View-Controller architectural pattern detected',
                evidence=[f"Found {len(mvc_files['models'])} model files, "
                         f"{len(mvc_files['views'])} view files, "
                         f"{len(mvc_files['controllers'])} controller files"],
                files_involved=[f for files in mvc_files.values() for f in files]
            )
        return None

    def _detect_factory_pattern(self, analyses: List[FileAnalysis]) -> Optional[ArchitecturalPattern]:
        """Detect Factory design pattern."""
        factory_evidence = []
        factory_files = []

        for analysis in analyses:
            for cls in analysis.classes:
                if 'factory' in cls['name'].lower():
                    factory_evidence.append(f"Factory class: {cls['name']}")
                    factory_files.append(analysis.path)

        if factory_evidence:
            return ArchitecturalPattern(
                name='Factory',
                confidence=0.7,
                description='Factory design pattern detected',
                evidence=factory_evidence,
                files_involved=factory_files
            )
        return None

    def _detect_singleton_pattern(self, analyses: List[FileAnalysis]) -> Optional[ArchitecturalPattern]:
        """Detect Singleton design pattern."""
        singleton_evidence = []
        singleton_files = []

        for analysis in analyses:
            for cls in analysis.classes:
                methods = [m.lower() for m in cls['methods']]
                if 'get_instance' in methods or 'instance' in methods:
                    singleton_evidence.append(f"Potential Singleton: {cls['name']}")
                    singleton_files.append(analysis.path)

        if singleton_evidence:
            return ArchitecturalPattern(
                name='Singleton',
                confidence=0.6,
                description='Singleton design pattern detected',
                evidence=singleton_evidence,
                files_involved=singleton_files
            )
        return None


class CodebaseAnalyzer:
    """Main analyzer class that orchestrates the analysis process."""

    def __init__(self):
        self.python_analyzer = PythonFileAnalyzer()
        self.pattern_detector = ArchitecturalPatternDetector()

    def analyze_codebase(self, codebase_path: Path) -> CodebaseAnalysis:
        """Analyze an entire codebase."""
        print(f"Analyzing codebase at: {codebase_path}")

        # Discover all source files
        source_files = self._discover_source_files(codebase_path)
        print(f"Found {len(source_files)} source files")

        # Analyze individual files
        file_analyses = []
        for file_path in source_files:
            if file_path.suffix == '.py':
                analysis = self.python_analyzer.analyze_file(file_path)
                file_analyses.append(analysis)

        # Detect architectural patterns
        patterns = self.pattern_detector.detect_patterns(file_analyses)

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(file_analyses)

        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(file_analyses)

        # Generate suggestions
        suggestions = self._generate_suggestions(file_analyses, patterns)

        # Count languages
        languages = Counter(analysis.language for analysis in file_analyses)

        return CodebaseAnalysis(
            total_files=len(file_analyses),
            total_loc=sum(analysis.lines_of_code for analysis in file_analyses),
            languages=dict(languages),
            file_analyses=file_analyses,
            architectural_patterns=patterns,
            dependency_graph=dependency_graph,
            quality_metrics=quality_metrics,
            suggestions=suggestions
        )

    def _discover_source_files(self, codebase_path: Path) -> List[Path]:
        """Discover all source files in the codebase."""
        source_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h'}
        source_files = []

        for file_path in codebase_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in source_extensions:
                # Skip common directories to ignore
                skip_dirs = {'node_modules', '.git', '__pycache__', '.venv', 'venv'}
                if not any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    source_files.append(file_path)

        return source_files

    def _build_dependency_graph(self, analyses: List[FileAnalysis]) -> Dict[str, List[str]]:
        """Build a dependency graph between files."""
        graph = defaultdict(list)

        # Create a mapping of module names to file paths
        module_to_file = {}
        for analysis in analyses:
            # Simple heuristic: assume module name is filename without extension
            module_name = Path(analysis.path).stem
            module_to_file[module_name] = analysis.path

        # Build dependencies
        for analysis in analyses:
            for import_name in analysis.imports:
                # Simple matching - in real implementation, would be more sophisticated
                base_import = import_name.split('.')[0]
                if base_import in module_to_file:
                    graph[analysis.path].append(module_to_file[base_import])

        return dict(graph)

    def _calculate_quality_metrics(self, analyses: List[FileAnalysis]) -> Dict[str, Any]:
        """Calculate overall code quality metrics."""
        if not analyses:
            return {}

        complexity_scores = [a.complexity_score for a in analyses if a.complexity_score > 0]

        return {
            'average_complexity': sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0,
            'max_complexity': max(complexity_scores) if complexity_scores else 0,
            'total_issues': sum(len(a.issues) for a in analyses),
            'files_with_issues': len([a for a in analyses if a.issues]),
            'average_loc_per_file': sum(a.lines_of_code for a in analyses) / len(analyses)
        }

    def _generate_suggestions(self, analyses: List[FileAnalysis],
                            patterns: List[ArchitecturalPattern]) -> List[Dict[str, str]]:
        """Generate improvement suggestions."""
        suggestions = []

        # Suggest refactoring for high complexity
        high_complexity_files = [a for a in analyses if a.complexity_score > 5.0]
        if high_complexity_files:
            suggestions.append({
                'type': 'refactoring',
                'priority': 'high',
                'message': f"Consider refactoring {len(high_complexity_files)} files with high complexity"
            })

        # Suggest documentation for patterns
        if patterns:
            suggestions.append({
                'type': 'documentation',
                'priority': 'medium',
                'message': f"Document the {len(patterns)} architectural patterns detected"
            })

        # Suggest fixing issues
        total_issues = sum(len(a.issues) for a in analyses)
        if total_issues > 0:
            suggestions.append({
                'type': 'quality',
                'priority': 'high',
                'message': f"Address {total_issues} code quality issues found"
            })

        return suggestions

    def generate_report(self, analysis: CodebaseAnalysis, output_path: Optional[Path] = None) -> str:
        """Generate a human-readable analysis report."""
        report_lines = [
            "# Codebase Analysis Report",
            f"**Generated on:** {os.popen('date').read().strip()}",
            "",
            "## Overview",
            f"- **Total Files:** {analysis.total_files}",
            f"- **Total Lines of Code:** {analysis.total_loc:,}",
            f"- **Languages:** {', '.join(f'{lang} ({count})' for lang, count in analysis.languages.items())}",
            "",
            "## Quality Metrics",
            f"- **Average Complexity:** {analysis.quality_metrics.get('average_complexity', 0):.2f}",
            f"- **Maximum Complexity:** {analysis.quality_metrics.get('max_complexity', 0):.2f}",
            f"- **Total Issues:** {analysis.quality_metrics.get('total_issues', 0)}",
            f"- **Files with Issues:** {analysis.quality_metrics.get('files_with_issues', 0)}",
            f"- **Average LOC per File:** {analysis.quality_metrics.get('average_loc_per_file', 0):.1f}",
            "",
        ]

        if analysis.architectural_patterns:
            report_lines.extend([
                "## Architectural Patterns",
                ""
            ])
            for pattern in analysis.architectural_patterns:
                report_lines.extend([
                    f"### {pattern.name} (Confidence: {pattern.confidence:.1%})",
                    f"{pattern.description}",
                    "",
                    "**Evidence:**",
                    *[f"- {evidence}" for evidence in pattern.evidence],
                    "",
                    f"**Files Involved:** {len(pattern.files_involved)}",
                    "",
                ])

        if analysis.suggestions:
            report_lines.extend([
                "## Recommendations",
                ""
            ])
            for suggestion in analysis.suggestions:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(suggestion['priority'], "")
                report_lines.append(f"- {priority_emoji} **{suggestion['type'].title()}:** {suggestion['message']}")

        report_content = "\n".join(report_lines)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_content)
            print(f"Report saved to: {output_path}")

        return report_content


def main():
    parser = argparse.ArgumentParser(description="Analyze a codebase for patterns and quality metrics")
    parser.add_argument("path", help="Path to the codebase to analyze")
    parser.add_argument("--output", "-o", help="Output file for the report")
    parser.add_argument("--json", action="store_true", help="Also output raw JSON analysis")

    args = parser.parse_args()

    codebase_path = Path(args.path)
    if not codebase_path.exists():
        print(f"Error: Path {codebase_path} does not exist")
        return 1

    analyzer = CodebaseAnalyzer()
    analysis = analyzer.analyze_codebase(codebase_path)

    # Generate report
    output_path = Path(args.output) if args.output else None
    report = analyzer.generate_report(analysis, output_path)

    if not args.output:
        print(report)

    # Save JSON if requested
    if args.json:
        json_path = (output_path.with_suffix('.json')
                    if output_path else Path('analysis.json'))
        with open(json_path, 'w') as f:
            json.dump(asdict(analysis), f, indent=2, default=str)
        print(f"JSON analysis saved to: {json_path}")

    return 0


if __name__ == "__main__":
    exit(main())