#!/usr/bin/env python3
"""
CodeInsight: An Intelligent Codebase Analyzer

A tool for systematically analyzing codebases to identify architectural patterns,
potential issues, and improvement opportunities. This analyzer focuses on:

1. Context-aware code analysis across multiple files
2. Pattern recognition for common architectural designs
3. Identification of potential refactoring opportunities
4. Dynamic documentation generation

Usage:
    python code_insight.py /path/to/codebase

Example:
    python code_insight.py . --output-format json --include-patterns "*.py,*.js,*.ts"
"""

import os
import ast
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""
    path: str
    language: str
    lines_of_code: int
    complexity_score: float
    functions: List[str]
    classes: List[str]
    imports: List[str]
    potential_issues: List[str]
    architectural_patterns: List[str]


@dataclass
class CodebaseAnalysis:
    """Complete analysis results for a codebase."""
    total_files: int
    languages: Dict[str, int]
    total_lines: int
    complexity_distribution: Dict[str, int]
    common_patterns: List[str]
    dependency_graph: Dict[str, List[str]]
    refactoring_opportunities: List[str]
    file_analyses: List[FileAnalysis]


class CodeInsightAnalyzer:
    """Main analyzer class for intelligent codebase analysis."""

    def __init__(self, root_path: str, include_patterns: List[str] = None):
        self.root_path = Path(root_path)
        self.include_patterns = include_patterns or ["*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c"]
        self.file_analyses: List[FileAnalysis] = []
        self.language_processors = {
            '.py': self._analyze_python_file,
            '.js': self._analyze_javascript_file,
            '.ts': self._analyze_typescript_file,
        }

    def analyze(self) -> CodebaseAnalysis:
        """Perform comprehensive codebase analysis."""
        print(f"🔍 Starting analysis of codebase at: {self.root_path}")

        # Discover and analyze all relevant files
        files = self._discover_files()
        print(f"📁 Found {len(files)} files to analyze")

        for file_path in files:
            try:
                analysis = self._analyze_file(file_path)
                if analysis:
                    self.file_analyses.append(analysis)
            except Exception as e:
                print(f"⚠️ Error analyzing {file_path}: {e}")

        # Generate aggregate analysis
        return self._generate_aggregate_analysis()

    def _discover_files(self) -> List[Path]:
        """Discover all files matching include patterns."""
        files = []
        for pattern in self.include_patterns:
            # Simple glob-like pattern matching
            extension = pattern.replace('*', '')
            for file_path in self.root_path.rglob('*' + extension):
                if file_path.is_file() and not self._should_ignore(file_path):
                    files.append(file_path)
        return sorted(set(files))

    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        ignore_patterns = {
            '.git', '__pycache__', 'node_modules', '.pytest_cache',
            'venv', 'env', '.venv', 'dist', 'build', '.tox'
        }
        return any(part in ignore_patterns for part in file_path.parts)

    def _analyze_file(self, file_path: Path) -> Optional[FileAnalysis]:
        """Analyze a single file."""
        try:
            suffix = file_path.suffix.lower()
            if suffix in self.language_processors:
                return self.language_processors[suffix](file_path)
            else:
                # Basic analysis for unsupported file types
                return self._analyze_generic_file(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    def _analyze_python_file(self, file_path: Path) -> FileAnalysis:
        """Detailed analysis of Python files using AST."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Fallback to basic analysis if parsing fails
            return self._analyze_generic_file(file_path)

        functions = []
        classes = []
        imports = []
        complexity_score = 0
        potential_issues = []
        patterns = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                # Simple complexity metric based on nested structures
                complexity_score += self._calculate_node_complexity(node)

                # Check for potential issues
                if len(node.args.args) > 6:
                    potential_issues.append(f"Function '{node.name}' has many parameters ({len(node.args.args)})")

            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

                # Detect architectural patterns
                if any(base.id == 'ABC' for base in node.bases if isinstance(base, ast.Name)):
                    patterns.append("Abstract Base Class")

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                else:
                    imports.append(node.module or "")

        # Detect more architectural patterns
        if any('factory' in func.lower() for func in functions):
            patterns.append("Factory Pattern")
        if any('singleton' in cls.lower() for cls in classes):
            patterns.append("Singleton Pattern")

        lines_of_code = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])

        return FileAnalysis(
            path=str(file_path.relative_to(self.root_path)),
            language="Python",
            lines_of_code=lines_of_code,
            complexity_score=complexity_score,
            functions=functions,
            classes=classes,
            imports=list(set(imports)),
            potential_issues=potential_issues,
            architectural_patterns=patterns
        )

    def _analyze_javascript_file(self, file_path: Path) -> FileAnalysis:
        """Basic analysis for JavaScript files."""
        # For now, implement basic text-based analysis
        # In a full implementation, we'd use a JS parser like esprima
        return self._analyze_generic_file(file_path, language="JavaScript")

    def _analyze_typescript_file(self, file_path: Path) -> FileAnalysis:
        """Basic analysis for TypeScript files."""
        # For now, implement basic text-based analysis
        # In a full implementation, we'd use the TypeScript compiler API
        return self._analyze_generic_file(file_path, language="TypeScript")

    def _analyze_generic_file(self, file_path: Path, language: str = "Unknown") -> FileAnalysis:
        """Basic analysis for any text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        lines_of_code = len([line for line in lines if line.strip()])

        return FileAnalysis(
            path=str(file_path.relative_to(self.root_path)),
            language=language,
            lines_of_code=lines_of_code,
            complexity_score=0,
            functions=[],
            classes=[],
            imports=[],
            potential_issues=[],
            architectural_patterns=[]
        )

    def _calculate_node_complexity(self, node: ast.AST) -> float:
        """Calculate complexity score for an AST node."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)

        return complexity

    def _generate_aggregate_analysis(self) -> CodebaseAnalysis:
        """Generate aggregate analysis from individual file analyses."""
        languages = Counter(analysis.language for analysis in self.file_analyses)
        total_lines = sum(analysis.lines_of_code for analysis in self.file_analyses)

        # Complexity distribution
        complexity_ranges = {"Low (1-5)": 0, "Medium (6-15)": 0, "High (16+)": 0}
        for analysis in self.file_analyses:
            if analysis.complexity_score <= 5:
                complexity_ranges["Low (1-5)"] += 1
            elif analysis.complexity_score <= 15:
                complexity_ranges["Medium (6-15)"] += 1
            else:
                complexity_ranges["High (16+)"] += 1

        # Common patterns
        all_patterns = []
        for analysis in self.file_analyses:
            all_patterns.extend(analysis.architectural_patterns)
        common_patterns = [pattern for pattern, count in Counter(all_patterns).most_common(10)]

        # Generate refactoring opportunities
        refactoring_opportunities = []
        high_complexity_files = [a for a in self.file_analyses if a.complexity_score > 15]
        if high_complexity_files:
            refactoring_opportunities.append(f"Consider refactoring {len(high_complexity_files)} high-complexity files")

        large_files = [a for a in self.file_analyses if a.lines_of_code > 500]
        if large_files:
            refactoring_opportunities.append(f"Consider breaking down {len(large_files)} large files (>500 LOC)")

        # Simple dependency graph (imports)
        dependency_graph = {}
        for analysis in self.file_analyses:
            if analysis.imports:
                dependency_graph[analysis.path] = analysis.imports

        return CodebaseAnalysis(
            total_files=len(self.file_analyses),
            languages=dict(languages),
            total_lines=total_lines,
            complexity_distribution=complexity_ranges,
            common_patterns=common_patterns,
            dependency_graph=dependency_graph,
            refactoring_opportunities=refactoring_opportunities,
            file_analyses=self.file_analyses
        )


def main():
    """Main entry point for CodeInsight analyzer."""
    parser = argparse.ArgumentParser(description="Intelligent Codebase Analyzer")
    parser.add_argument("path", help="Path to the codebase to analyze")
    parser.add_argument("--output-format", choices=["json", "text"], default="text",
                       help="Output format (default: text)")
    parser.add_argument("--include-patterns", nargs="*",
                       default=["*.py", "*.js", "*.ts", "*.java"],
                       help="File patterns to include in analysis")
    parser.add_argument("--output-file", help="Save output to file")

    args = parser.parse_args()

    # Create analyzer and run analysis
    analyzer = CodeInsightAnalyzer(args.path, args.include_patterns)
    analysis = analyzer.analyze()

    # Format output
    if args.output_format == "json":
        output = json.dumps(asdict(analysis), indent=2)
    else:
        output = format_text_report(analysis)

    # Output results
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(output)
        print(f"📊 Analysis saved to: {args.output_file}")
    else:
        print(output)


def format_text_report(analysis: CodebaseAnalysis) -> str:
    """Format analysis results as a readable text report."""
    report = []
    report.append("=" * 60)
    report.append("🔍 CODEBASE ANALYSIS REPORT")
    report.append("=" * 60)
    report.append("")

    # Overview
    report.append("📊 OVERVIEW")
    report.append(f"  Total Files: {analysis.total_files}")
    report.append(f"  Total Lines: {analysis.total_lines:,}")
    report.append(f"  Languages: {', '.join(f'{lang} ({count})' for lang, count in analysis.languages.items())}")
    report.append("")

    # Complexity Distribution
    report.append("🎯 COMPLEXITY DISTRIBUTION")
    for range_name, count in analysis.complexity_distribution.items():
        percentage = (count / analysis.total_files * 100) if analysis.total_files > 0 else 0
        report.append(f"  {range_name}: {count} files ({percentage:.1f}%)")
    report.append("")

    # Common Patterns
    if analysis.common_patterns:
        report.append("🏗️ ARCHITECTURAL PATTERNS")
        for pattern in analysis.common_patterns[:5]:
            report.append(f"  • {pattern}")
        report.append("")

    # Refactoring Opportunities
    if analysis.refactoring_opportunities:
        report.append("🔧 REFACTORING OPPORTUNITIES")
        for opportunity in analysis.refactoring_opportunities:
            report.append(f"  • {opportunity}")
        report.append("")

    # Top Complex Files
    complex_files = sorted([f for f in analysis.file_analyses if f.complexity_score > 0],
                          key=lambda x: x.complexity_score, reverse=True)[:5]
    if complex_files:
        report.append("⚡ MOST COMPLEX FILES")
        for file_analysis in complex_files:
            report.append(f"  • {file_analysis.path} (complexity: {file_analysis.complexity_score:.1f})")
        report.append("")

    report.append("=" * 60)
    return "\n".join(report)


if __name__ == "__main__":
    main()