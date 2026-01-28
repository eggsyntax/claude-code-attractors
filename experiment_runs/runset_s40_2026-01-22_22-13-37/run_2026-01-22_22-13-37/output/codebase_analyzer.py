#!/usr/bin/env python3
"""
Intelligent Codebase Analyzer

A tool for context-aware code analysis that understands project structure,
identifies patterns and anti-patterns, and generates actionable insights
for improving code quality and architecture.

This analyzer goes beyond simple static analysis to provide semantic
understanding of codebases and their architectural decisions.
"""

import os
import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import re


@dataclass
class FileInfo:
    """Information about a single source file."""
    path: Path
    size: int
    lines: int
    language: str
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    complexity_score: float = 0.0


@dataclass
class ArchitecturalPattern:
    """Represents an identified architectural pattern."""
    name: str
    description: str
    files_involved: List[Path]
    confidence: float
    is_antipattern: bool = False
    suggestions: List[str] = field(default_factory=list)


@dataclass
class CodebaseInsights:
    """Complete analysis results for a codebase."""
    total_files: int
    total_lines: int
    languages: Dict[str, int]
    file_info: Dict[Path, FileInfo]
    patterns: List[ArchitecturalPattern]
    dependency_graph: Dict[str, Set[str]]
    complexity_hotspots: List[Tuple[Path, float]]
    suggestions: List[str] = field(default_factory=list)


class CodebaseAnalyzer:
    """
    Main analyzer class for intelligent codebase analysis.

    This analyzer provides context-aware analysis by understanding:
    - File relationships and dependencies
    - Architectural patterns and anti-patterns
    - Code complexity and quality metrics
    - Refactoring opportunities
    """

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.logger = logging.getLogger(__name__)
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }

    def analyze(self) -> CodebaseInsights:
        """
        Perform comprehensive codebase analysis.

        Returns:
            CodebaseInsights: Complete analysis results
        """
        self.logger.info(f"Starting analysis of {self.root_path}")

        # Discover all source files
        files = self._discover_files()

        # Analyze individual files
        file_info = {}
        for file_path in files:
            info = self._analyze_file(file_path)
            if info:
                file_info[file_path] = info

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(file_info)

        # Identify architectural patterns
        patterns = self._identify_patterns(file_info, dependency_graph)

        # Calculate complexity hotspots
        complexity_hotspots = self._identify_complexity_hotspots(file_info)

        # Generate high-level insights and suggestions
        suggestions = self._generate_suggestions(file_info, patterns, complexity_hotspots)

        # Compile language statistics
        languages = defaultdict(int)
        total_lines = 0
        for info in file_info.values():
            languages[info.language] += 1
            total_lines += info.lines

        return CodebaseInsights(
            total_files=len(file_info),
            total_lines=total_lines,
            languages=dict(languages),
            file_info=file_info,
            patterns=patterns,
            dependency_graph=dependency_graph,
            complexity_hotspots=complexity_hotspots,
            suggestions=suggestions
        )

    def _discover_files(self) -> List[Path]:
        """Discover all analyzable source files in the codebase."""
        files = []

        for root, dirs, filenames in os.walk(self.root_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                'node_modules', '__pycache__', 'venv', 'env', 'build', 'dist', 'target'
            }]

            for filename in filenames:
                path = Path(root) / filename
                if path.suffix.lower() in self.supported_extensions:
                    files.append(path)

        return files

    def _analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        """Analyze a single source file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            language = self.supported_extensions.get(file_path.suffix.lower(), 'unknown')
            lines = len(content.splitlines())
            size = len(content)

            info = FileInfo(
                path=file_path,
                size=size,
                lines=lines,
                language=language
            )

            # Language-specific analysis
            if language == 'python':
                self._analyze_python_file(content, info)
            elif language in ['javascript', 'typescript']:
                self._analyze_js_file(content, info)

            return info

        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_path}: {e}")
            return None

    def _analyze_python_file(self, content: str, info: FileInfo):
        """Analyze Python-specific features."""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    info.functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    info.classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        info.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        info.imports.append(node.module)

            # Calculate cyclomatic complexity (simplified)
            info.complexity_score = self._calculate_python_complexity(tree)

        except SyntaxError:
            self.logger.warning(f"Syntax error in Python file {info.path}")

    def _analyze_js_file(self, content: str, info: FileInfo):
        """Analyze JavaScript/TypeScript features (basic pattern matching)."""
        # Simple regex-based analysis for JS/TS
        function_pattern = r'(?:function\s+(\w+)|(\w+)\s*[:=]\s*(?:function|\([^)]*\)\s*=>))'
        class_pattern = r'class\s+(\w+)'
        import_pattern = r'import.*?from\s+[\'"]([^\'"]+)[\'"]'

        info.functions = re.findall(function_pattern, content)
        info.functions = [f[0] or f[1] for f in info.functions if f[0] or f[1]]

        info.classes = re.findall(class_pattern, content)
        info.imports = re.findall(import_pattern, content)

        # Simple complexity estimation
        info.complexity_score = self._calculate_js_complexity(content)

    def _calculate_python_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity for Python code."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity / 10.0  # Normalize

    def _calculate_js_complexity(self, content: str) -> float:
        """Calculate complexity for JavaScript/TypeScript (simplified)."""
        # Count control flow statements
        complexity_patterns = [
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
            r'\bswitch\b', r'\btry\b', r'\bcatch\b'
        ]

        complexity = 1
        for pattern in complexity_patterns:
            complexity += len(re.findall(pattern, content))

        return complexity / 10.0

    def _build_dependency_graph(self, file_info: Dict[Path, FileInfo]) -> Dict[str, Set[str]]:
        """Build a dependency graph from import relationships."""
        graph = defaultdict(set)

        for path, info in file_info.items():
            module_name = str(path.relative_to(self.root_path))

            for import_name in info.imports:
                # Try to resolve import to actual files
                resolved_path = self._resolve_import(import_name, path)
                if resolved_path and resolved_path in file_info:
                    graph[module_name].add(str(resolved_path.relative_to(self.root_path)))

        return dict(graph)

    def _resolve_import(self, import_name: str, current_file: Path) -> Optional[Path]:
        """Attempt to resolve an import to an actual file path."""
        # Simplified resolution - would need more sophisticated logic for real use
        if import_name.startswith('.'):
            # Relative import
            base_dir = current_file.parent
            import_path = base_dir / (import_name.lstrip('.') + '.py')
            if import_path.exists():
                return import_path

        return None

    def _identify_patterns(self, file_info: Dict[Path, FileInfo],
                          dependency_graph: Dict[str, Set[str]]) -> List[ArchitecturalPattern]:
        """Identify architectural patterns and anti-patterns."""
        patterns = []

        # Pattern: God Object (large classes with many methods)
        patterns.extend(self._detect_god_objects(file_info))

        # Pattern: Circular Dependencies
        patterns.extend(self._detect_circular_dependencies(dependency_graph))

        # Pattern: MVC-like structure
        patterns.extend(self._detect_mvc_pattern(file_info))

        return patterns

    def _detect_god_objects(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect god object anti-pattern."""
        patterns = []

        for path, info in file_info.items():
            if len(info.classes) > 0 and len(info.functions) > 20:  # Arbitrary threshold
                patterns.append(ArchitecturalPattern(
                    name="God Object",
                    description=f"File {path.name} contains a large number of functions/methods",
                    files_involved=[path],
                    confidence=0.7,
                    is_antipattern=True,
                    suggestions=[
                        "Consider breaking this into smaller, more focused classes",
                        "Apply Single Responsibility Principle",
                        "Extract related functionality into separate modules"
                    ]
                ))

        return patterns

    def _detect_circular_dependencies(self, dependency_graph: Dict[str, Set[str]]) -> List[ArchitecturalPattern]:
        """Detect circular dependency anti-pattern."""
        patterns = []

        # Simple cycle detection (would need more sophisticated algorithm for complex cases)
        for module, deps in dependency_graph.items():
            for dep in deps:
                if dep in dependency_graph and module in dependency_graph[dep]:
                    patterns.append(ArchitecturalPattern(
                        name="Circular Dependency",
                        description=f"Circular dependency between {module} and {dep}",
                        files_involved=[Path(module), Path(dep)],
                        confidence=0.9,
                        is_antipattern=True,
                        suggestions=[
                            "Introduce abstraction layer to break the cycle",
                            "Move shared code to a separate module",
                            "Consider dependency inversion principle"
                        ]
                    ))

        return patterns

    def _detect_mvc_pattern(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect MVC-like architectural pattern."""
        mvc_keywords = {
            'model': ['model', 'entity', 'data'],
            'view': ['view', 'template', 'ui', 'component'],
            'controller': ['controller', 'handler', 'service']
        }

        mvc_files = {'model': [], 'view': [], 'controller': []}

        for path, info in file_info.items():
            path_lower = str(path).lower()

            for mvc_type, keywords in mvc_keywords.items():
                if any(keyword in path_lower for keyword in keywords):
                    mvc_files[mvc_type].append(path)

        # If we have files in all three categories, suggest MVC pattern
        if all(mvc_files.values()):
            return [ArchitecturalPattern(
                name="MVC Pattern",
                description="Codebase appears to follow MVC architectural pattern",
                files_involved=sum(mvc_files.values(), []),
                confidence=0.6,
                is_antipattern=False,
                suggestions=[
                    "Ensure clear separation of concerns between layers",
                    "Consider using dependency injection for loose coupling"
                ]
            )]

        return []

    def _identify_complexity_hotspots(self, file_info: Dict[Path, FileInfo]) -> List[Tuple[Path, float]]:
        """Identify files with high complexity scores."""
        hotspots = [(path, info.complexity_score) for path, info in file_info.items()]
        hotspots.sort(key=lambda x: x[1], reverse=True)
        return hotspots[:10]  # Top 10 most complex files

    def _generate_suggestions(self, file_info: Dict[Path, FileInfo],
                             patterns: List[ArchitecturalPattern],
                             hotspots: List[Tuple[Path, float]]) -> List[str]:
        """Generate high-level improvement suggestions."""
        suggestions = []

        # File size suggestions
        large_files = [info for info in file_info.values() if info.lines > 500]
        if large_files:
            suggestions.append(f"Consider splitting {len(large_files)} large files (>500 lines) into smaller modules")

        # Complexity suggestions
        if hotspots and hotspots[0][1] > 5.0:
            suggestions.append("High complexity detected - consider refactoring complex functions")

        # Pattern-based suggestions
        antipatterns = [p for p in patterns if p.is_antipattern]
        if antipatterns:
            suggestions.append(f"Address {len(antipatterns)} architectural anti-patterns found")

        # Language diversity
        languages = set(info.language for info in file_info.values())
        if len(languages) > 3:
            suggestions.append("Consider standardizing on fewer programming languages")

        return suggestions


def main():
    """Example usage of the CodebaseAnalyzer."""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze a codebase for patterns and insights')
    parser.add_argument('path', help='Path to the codebase to analyze')
    parser.add_argument('--output', '-o', help='Output file for results (JSON format)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    analyzer = CodebaseAnalyzer(args.path)
    insights = analyzer.analyze()

    # Print summary
    print(f"\n=== Codebase Analysis Results ===")
    print(f"Total files: {insights.total_files}")
    print(f"Total lines: {insights.total_lines:,}")
    print(f"Languages: {', '.join(insights.languages.keys())}")

    print(f"\n=== Patterns Found ({len(insights.patterns)}) ===")
    for pattern in insights.patterns:
        marker = "❌" if pattern.is_antipattern else "✅"
        print(f"{marker} {pattern.name} (confidence: {pattern.confidence:.1%})")
        print(f"   {pattern.description}")

    print(f"\n=== Complexity Hotspots ===")
    for path, score in insights.complexity_hotspots[:5]:
        print(f"📊 {path.name}: {score:.1f}")

    print(f"\n=== Suggestions ===")
    for suggestion in insights.suggestions:
        print(f"💡 {suggestion}")

    # Save detailed results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(insights.__dict__, f, indent=2, default=str)
        print(f"\nDetailed results saved to {args.output}")


if __name__ == '__main__':
    main()