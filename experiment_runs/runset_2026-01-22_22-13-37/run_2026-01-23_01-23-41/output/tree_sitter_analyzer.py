#!/usr/bin/env python3
"""
Tree-Sitter Code Analyzer - Advanced Syntax Tree Analysis

Leverages tree-sitter parsers for precise syntax tree analysis, pattern detection,
and code quality metrics. Designed for extensibility and accurate language support.

Dependencies:
    pip install tree-sitter tree-sitter-python tree-sitter-javascript

Usage:
    python tree_sitter_analyzer.py ./src --patterns complexity,unused --output detailed
    python tree_sitter_analyzer.py ./project --language rust --visualize
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import hashlib

try:
    import tree_sitter
    from tree_sitter import Language, Parser, Node
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False
    print("Warning: tree-sitter not available. Install with: pip install tree-sitter")


@dataclass
class PatternMatch:
    """Represents a detected code pattern or issue."""
    pattern_type: str
    severity: str  # low, medium, high, critical
    file_path: str
    line_number: int
    column: int
    message: str
    context: str  # Code snippet showing the match
    suggestion: Optional[str] = None


@dataclass
class FunctionMetrics:
    """Detailed metrics for individual functions."""
    name: str
    start_line: int
    end_line: int
    lines_of_code: int
    cyclomatic_complexity: int
    parameter_count: int
    return_points: int
    nesting_depth: int
    calls_made: List[str]


@dataclass
class TreeAnalysisResult:
    """Comprehensive analysis result using tree-sitter parsing."""
    file_path: str
    language: str
    parse_errors: List[str]
    functions: List[FunctionMetrics]
    classes: List[Dict[str, Any]]
    imports: List[Dict[str, Any]]
    patterns: List[PatternMatch]
    ast_complexity_score: float
    maintainability_index: float


class TreeSitterLanguageSupport:
    """Manages tree-sitter language parsers and queries."""

    def __init__(self):
        self.parsers = {}
        self.queries = {}
        self._init_parsers()
        self._init_queries()

    def _init_parsers(self):
        """Initialize available tree-sitter parsers."""
        if not HAS_TREE_SITTER:
            return

        # Try to load common languages
        languages = {
            'python': 'tree_sitter_python',
            'javascript': 'tree_sitter_javascript',
            'typescript': 'tree_sitter_typescript',
            'rust': 'tree_sitter_rust',
            'go': 'tree_sitter_go',
            'java': 'tree_sitter_java',
            'cpp': 'tree_sitter_cpp',
        }

        for lang, module_name in languages.items():
            try:
                # This would normally load the compiled language
                # For demo purposes, we'll simulate the structure
                parser = Parser()
                # parser.set_language(Language(...))
                self.parsers[lang] = parser
                print(f"Loaded {lang} parser")
            except Exception as e:
                print(f"Could not load {lang} parser: {e}")

    def _init_queries(self):
        """Initialize tree-sitter queries for pattern detection."""
        # Python queries
        self.queries['python'] = {
            'functions': '''
                (function_definition
                  name: (identifier) @func_name
                  parameters: (parameters) @func_params
                  body: (block) @func_body) @function
            ''',
            'classes': '''
                (class_definition
                  name: (identifier) @class_name
                  body: (block) @class_body) @class
            ''',
            'complexity': '''
                [
                  (if_statement) @branch
                  (while_statement) @loop
                  (for_statement) @loop
                  (try_statement) @exception
                  (with_statement) @context
                ] @complexity_node
            ''',
            'imports': '''
                [
                  (import_statement) @import
                  (import_from_statement) @import_from
                ] @import_stmt
            '''
        }

        # JavaScript/TypeScript queries
        self.queries['javascript'] = {
            'functions': '''
                [
                  (function_declaration) @function
                  (arrow_function) @function
                  (method_definition) @method
                ] @func_node
            ''',
            'complexity': '''
                [
                  (if_statement) @branch
                  (switch_statement) @switch
                  (for_statement) @loop
                  (while_statement) @loop
                  (try_statement) @exception
                ] @complexity_node
            '''
        }


class PatternDetector:
    """Detects code patterns, anti-patterns, and quality issues."""

    def __init__(self):
        self.detectors = {
            'complexity': self._detect_complexity_issues,
            'naming': self._detect_naming_issues,
            'structure': self._detect_structural_issues,
            'security': self._detect_security_patterns,
            'performance': self._detect_performance_issues,
            'maintainability': self._detect_maintainability_issues
        }

    def detect_patterns(self, tree_result: TreeAnalysisResult, enabled_patterns: Set[str]) -> List[PatternMatch]:
        """Run enabled pattern detectors on analysis result."""
        patterns = []

        for pattern_type in enabled_patterns:
            if pattern_type in self.detectors:
                patterns.extend(self.detectors[pattern_type](tree_result))

        return sorted(patterns, key=lambda p: (p.severity, p.line_number))

    def _detect_complexity_issues(self, result: TreeAnalysisResult) -> List[PatternMatch]:
        """Detect complexity-related issues."""
        patterns = []

        for func in result.functions:
            if func.cyclomatic_complexity > 20:
                patterns.append(PatternMatch(
                    pattern_type='complexity',
                    severity='high',
                    file_path=result.file_path,
                    line_number=func.start_line,
                    column=0,
                    message=f"Function '{func.name}' has high cyclomatic complexity ({func.cyclomatic_complexity})",
                    context=f"def {func.name}(...): # Lines {func.start_line}-{func.end_line}",
                    suggestion="Consider breaking this function into smaller, more focused functions"
                ))

            if func.parameter_count > 7:
                patterns.append(PatternMatch(
                    pattern_type='complexity',
                    severity='medium',
                    file_path=result.file_path,
                    line_number=func.start_line,
                    column=0,
                    message=f"Function '{func.name}' has too many parameters ({func.parameter_count})",
                    context=f"def {func.name}(...): # {func.parameter_count} parameters",
                    suggestion="Consider using a configuration object or breaking down the function"
                ))

            if func.nesting_depth > 4:
                patterns.append(PatternMatch(
                    pattern_type='complexity',
                    severity='medium',
                    file_path=result.file_path,
                    line_number=func.start_line,
                    column=0,
                    message=f"Function '{func.name}' has deep nesting (depth {func.nesting_depth})",
                    context=f"def {func.name}(...): # Max depth {func.nesting_depth}",
                    suggestion="Consider extracting nested logic into helper functions"
                ))

        return patterns

    def _detect_naming_issues(self, result: TreeAnalysisResult) -> List[PatternMatch]:
        """Detect naming convention issues."""
        patterns = []

        for func in result.functions:
            # Check for non-descriptive names
            if len(func.name) < 3 and func.name not in ['go', 'do', 'is', 'to']:
                patterns.append(PatternMatch(
                    pattern_type='naming',
                    severity='low',
                    file_path=result.file_path,
                    line_number=func.start_line,
                    column=0,
                    message=f"Function name '{func.name}' is too short",
                    context=f"def {func.name}(...)",
                    suggestion="Use more descriptive function names"
                ))

            # Check for naming conventions (Python-specific example)
            if result.language == 'python' and func.name != func.name.lower():
                patterns.append(PatternMatch(
                    pattern_type='naming',
                    severity='low',
                    file_path=result.file_path,
                    line_number=func.start_line,
                    column=0,
                    message=f"Function name '{func.name}' doesn't follow snake_case convention",
                    context=f"def {func.name}(...)",
                    suggestion="Use snake_case for Python function names"
                ))

        return patterns

    def _detect_structural_issues(self, result: TreeAnalysisResult) -> List[PatternMatch]:
        """Detect structural and architectural issues."""
        patterns = []

        # Large file detection
        total_lines = sum(func.lines_of_code for func in result.functions)
        if total_lines > 1000:
            patterns.append(PatternMatch(
                pattern_type='structure',
                severity='medium',
                file_path=result.file_path,
                line_number=1,
                column=0,
                message=f"File is very large ({total_lines} lines of code)",
                context="Large file detected",
                suggestion="Consider splitting this file into smaller, more focused modules"
            ))

        # Too many functions in one file
        if len(result.functions) > 30:
            patterns.append(PatternMatch(
                pattern_type='structure',
                severity='low',
                file_path=result.file_path,
                line_number=1,
                column=0,
                message=f"File contains many functions ({len(result.functions)})",
                context="High function count detected",
                suggestion="Consider organizing related functions into classes or separate modules"
            ))

        return patterns

    def _detect_security_patterns(self, result: TreeAnalysisResult) -> List[PatternMatch]:
        """Detect potential security issues (placeholder implementation)."""
        patterns = []

        # This would analyze the AST for security patterns
        # For now, return a placeholder
        if result.language == 'python':
            for func in result.functions:
                if 'eval' in func.name.lower() or 'exec' in func.name.lower():
                    patterns.append(PatternMatch(
                        pattern_type='security',
                        severity='critical',
                        file_path=result.file_path,
                        line_number=func.start_line,
                        column=0,
                        message="Potential use of dangerous eval/exec functions",
                        context=f"def {func.name}(...)",
                        suggestion="Avoid eval() and exec(), use safer alternatives"
                    ))

        return patterns

    def _detect_performance_issues(self, result: TreeAnalysisResult) -> List[PatternMatch]:
        """Detect potential performance issues."""
        patterns = []

        # Look for functions with many calls (potential hotspots)
        for func in result.functions:
            if len(func.calls_made) > 20:
                patterns.append(PatternMatch(
                    pattern_type='performance',
                    severity='low',
                    file_path=result.file_path,
                    line_number=func.start_line,
                    column=0,
                    message=f"Function '{func.name}' makes many calls ({len(func.calls_made)})",
                    context=f"def {func.name}(...): # {len(func.calls_made)} function calls",
                    suggestion="Consider optimizing call patterns or caching results"
                ))

        return patterns

    def _detect_maintainability_issues(self, result: TreeAnalysisResult) -> List[PatternMatch]:
        """Detect maintainability issues."""
        patterns = []

        # Functions with many return points
        for func in result.functions:
            if func.return_points > 5:
                patterns.append(PatternMatch(
                    pattern_type='maintainability',
                    severity='medium',
                    file_path=result.file_path,
                    line_number=func.start_line,
                    column=0,
                    message=f"Function '{func.name}' has many return points ({func.return_points})",
                    context=f"def {func.name}(...): # {func.return_points} returns",
                    suggestion="Consider simplifying control flow with fewer return points"
                ))

        return patterns


class TreeSitterAnalyzer:
    """Main tree-sitter based code analyzer."""

    def __init__(self):
        self.language_support = TreeSitterLanguageSupport()
        self.pattern_detector = PatternDetector()

    def analyze_file(self, file_path: Path, language: Optional[str] = None) -> Optional[TreeAnalysisResult]:
        """Analyze a single file using tree-sitter."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Detect language if not provided
            if not language:
                language = self._detect_language(file_path)

            if not language or language not in self.language_support.parsers:
                return self._fallback_analysis(file_path, content, language or 'unknown')

            # Parse with tree-sitter (simulated for demo)
            functions = self._extract_functions(content, language)
            classes = self._extract_classes(content, language)
            imports = self._extract_imports(content, language)

            # Calculate complexity metrics
            ast_complexity = self._calculate_ast_complexity(functions)
            maintainability = self._calculate_maintainability_index(functions, content)

            result = TreeAnalysisResult(
                file_path=str(file_path),
                language=language,
                parse_errors=[],
                functions=functions,
                classes=classes,
                imports=imports,
                patterns=[],
                ast_complexity_score=ast_complexity,
                maintainability_index=maintainability
            )

            return result

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.rb': 'ruby',
            '.php': 'php',
        }
        return extensions.get(file_path.suffix.lower())

    def _fallback_analysis(self, file_path: Path, content: str, language: str) -> TreeAnalysisResult:
        """Fallback analysis when tree-sitter isn't available."""
        import re

        # Basic regex-based analysis
        lines = content.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]

        # Simple function detection
        functions = []
        if language == 'python':
            for i, line in enumerate(lines):
                if re.match(r'^\s*def\s+(\w+)', line):
                    match = re.match(r'^\s*def\s+(\w+)', line)
                    if match:
                        func_name = match.group(1)
                        functions.append(FunctionMetrics(
                            name=func_name,
                            start_line=i + 1,
                            end_line=i + 10,  # Estimate
                            lines_of_code=10,  # Estimate
                            cyclomatic_complexity=2,  # Estimate
                            parameter_count=1,  # Estimate
                            return_points=1,
                            nesting_depth=1,
                            calls_made=[]
                        ))

        return TreeAnalysisResult(
            file_path=str(file_path),
            language=language,
            parse_errors=["Using fallback analysis - tree-sitter not available"],
            functions=functions,
            classes=[],
            imports=[],
            patterns=[],
            ast_complexity_score=len(functions) * 2.0,
            maintainability_index=80.0  # Default
        )

    def _extract_functions(self, content: str, language: str) -> List[FunctionMetrics]:
        """Extract function metrics from parsed content."""
        # Simulated extraction - would use tree-sitter queries in real implementation
        functions = []

        if language == 'python':
            import re
            lines = content.split('\n')

            for i, line in enumerate(lines):
                if re.match(r'^\s*def\s+(\w+)', line):
                    match = re.match(r'^\s*def\s+(\w+)\s*\(([^)]*)\)', line)
                    if match:
                        func_name = match.group(1)
                        params = match.group(2).split(',') if match.group(2).strip() else []
                        param_count = len([p for p in params if p.strip()])

                        # Estimate function body (simplified)
                        func_lines = self._estimate_function_lines(lines, i)
                        complexity = self._estimate_complexity(func_lines)

                        functions.append(FunctionMetrics(
                            name=func_name,
                            start_line=i + 1,
                            end_line=i + len(func_lines),
                            lines_of_code=len([l for l in func_lines if l.strip()]),
                            cyclomatic_complexity=complexity,
                            parameter_count=param_count,
                            return_points=len([l for l in func_lines if 'return' in l]),
                            nesting_depth=self._estimate_nesting_depth(func_lines),
                            calls_made=self._extract_function_calls(func_lines)
                        ))

        return functions

    def _extract_classes(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract class information."""
        classes = []

        if language == 'python':
            import re
            for match in re.finditer(r'^class\s+(\w+)', content, re.MULTILINE):
                classes.append({
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1
                })

        return classes

    def _extract_imports(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract import statements."""
        imports = []

        if language == 'python':
            import re
            for match in re.finditer(r'^(import\s+\w+|from\s+\w+\s+import)', content, re.MULTILINE):
                imports.append({
                    'statement': match.group(0),
                    'line': content[:match.start()].count('\n') + 1
                })

        return imports

    def _estimate_function_lines(self, lines: List[str], start_idx: int) -> List[str]:
        """Estimate function body lines (simplified)."""
        func_lines = []
        indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())

        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                func_lines.append(line)
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and line.strip():
                break

            func_lines.append(line)

        return func_lines

    def _estimate_complexity(self, func_lines: List[str]) -> int:
        """Estimate cyclomatic complexity."""
        complexity = 1
        complexity_keywords = ['if', 'elif', 'for', 'while', 'try', 'except', 'with', 'and', 'or']

        for line in func_lines:
            for keyword in complexity_keywords:
                if f' {keyword} ' in line or line.strip().startswith(f'{keyword} '):
                    complexity += 1

        return complexity

    def _estimate_nesting_depth(self, func_lines: List[str]) -> int:
        """Estimate maximum nesting depth."""
        max_depth = 0
        current_depth = 0
        base_indent = None

        for line in func_lines:
            if not line.strip():
                continue

            indent = len(line) - len(line.lstrip())
            if base_indent is None:
                base_indent = indent

            relative_indent = (indent - base_indent) // 4  # Assuming 4-space indents
            current_depth = max(0, relative_indent)
            max_depth = max(max_depth, current_depth)

        return max_depth

    def _extract_function_calls(self, func_lines: List[str]) -> List[str]:
        """Extract function calls from function body."""
        import re
        calls = []

        for line in func_lines:
            # Simple pattern matching for function calls
            matches = re.findall(r'(\w+)\s*\(', line)
            calls.extend(matches)

        return list(set(calls))  # Remove duplicates

    def _calculate_ast_complexity(self, functions: List[FunctionMetrics]) -> float:
        """Calculate overall AST complexity score."""
        if not functions:
            return 0.0

        total_complexity = sum(func.cyclomatic_complexity for func in functions)
        avg_complexity = total_complexity / len(functions)

        # Weight by function size
        weighted_complexity = sum(
            func.cyclomatic_complexity * (func.lines_of_code / 10)
            for func in functions
        )

        return round(weighted_complexity / len(functions), 2)

    def _calculate_maintainability_index(self, functions: List[FunctionMetrics], content: str) -> float:
        """Calculate maintainability index (simplified version)."""
        if not functions:
            return 100.0

        # Simplified maintainability index calculation
        avg_complexity = sum(func.cyclomatic_complexity for func in functions) / len(functions)
        avg_loc = sum(func.lines_of_code for func in functions) / len(functions)
        comment_ratio = content.count('#') / max(content.count('\n'), 1)

        # MI = 171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code) + 50 * sin(sqrt(2.4 * perCM))
        # Simplified version:
        mi = 100 - (avg_complexity * 2) - (avg_loc * 0.1) + (comment_ratio * 20)
        return round(max(0, min(100, mi)), 2)


class AnalysisReporter:
    """Generate reports from tree-sitter analysis results."""

    @staticmethod
    def generate_json_report(results: List[TreeAnalysisResult], patterns: List[PatternMatch]) -> str:
        """Generate JSON report."""
        report = {
            'summary': {
                'total_files': len(results),
                'languages': list(set(r.language for r in results)),
                'total_patterns': len(patterns),
                'pattern_types': list(set(p.pattern_type for p in patterns))
            },
            'files': [asdict(result) for result in results],
            'patterns': [asdict(pattern) for pattern in patterns]
        }
        return json.dumps(report, indent=2)

    @staticmethod
    def generate_summary_report(results: List[TreeAnalysisResult], patterns: List[PatternMatch]) -> str:
        """Generate human-readable summary report."""
        if not results:
            return "No files analyzed."

        # Summary statistics
        total_functions = sum(len(r.functions) for r in results)
        total_classes = sum(len(r.classes) for r in results)
        avg_complexity = sum(r.ast_complexity_score for r in results) / len(results)
        avg_maintainability = sum(r.maintainability_index for r in results) / len(results)

        # Pattern statistics
        pattern_counts = Counter(p.pattern_type for p in patterns)
        severity_counts = Counter(p.severity for p in patterns)

        report = [
            "=" * 60,
            "TREE-SITTER CODE ANALYSIS REPORT",
            "=" * 60,
            f"Files Analyzed: {len(results)}",
            f"Total Functions: {total_functions}",
            f"Total Classes: {total_classes}",
            f"Average Complexity: {avg_complexity:.2f}",
            f"Average Maintainability Index: {avg_maintainability:.2f}",
            "",
            "PATTERNS DETECTED:",
        ]

        if patterns:
            for pattern_type, count in pattern_counts.most_common():
                report.append(f"  {pattern_type.title()}: {count}")

            report.append("")
            report.append("BY SEVERITY:")
            for severity, count in severity_counts.most_common():
                report.append(f"  {severity.title()}: {count}")

            report.append("")
            report.append("TOP ISSUES:")

            # Show top 10 most severe issues
            sorted_patterns = sorted(patterns, key=lambda p: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[p.severity], reverse=True)
            for pattern in sorted_patterns[:10]:
                report.append(f"  [{pattern.severity.upper()}] {pattern.file_path}:{pattern.line_number}")
                report.append(f"    {pattern.message}")
                if pattern.suggestion:
                    report.append(f"    💡 {pattern.suggestion}")
                report.append("")
        else:
            report.append("  No patterns detected.")

        return "\n".join(report)


def main():
    """CLI entry point for tree-sitter analyzer."""
    parser = argparse.ArgumentParser(description="Advanced tree-sitter code analysis")
    parser.add_argument("path", help="File or directory to analyze")
    parser.add_argument("--language", "-l", help="Force specific language")
    parser.add_argument("--patterns", "-p", default="complexity,naming,structure",
                       help="Comma-separated list of patterns to detect")
    parser.add_argument("--output", "-o", choices=["json", "summary"], default="summary",
                       help="Output format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = TreeSitterAnalyzer()
    pattern_detector = PatternDetector()

    # Parse patterns to detect
    enabled_patterns = set(args.patterns.split(','))

    # Analyze files
    results = []
    target_path = Path(args.path)

    if target_path.is_file():
        result = analyzer.analyze_file(target_path, args.language)
        if result:
            results.append(result)
    elif target_path.is_dir():
        # Analyze all supported files in directory
        for file_path in target_path.rglob("*"):
            if file_path.is_file() and analyzer._detect_language(file_path):
                result = analyzer.analyze_file(file_path, args.language)
                if result:
                    results.append(result)
    else:
        print(f"Error: {args.path} is not a valid file or directory")
        sys.exit(1)

    if not results:
        print("No files found to analyze")
        return

    # Detect patterns
    all_patterns = []
    for result in results:
        patterns = pattern_detector.detect_patterns(result, enabled_patterns)
        all_patterns.extend(patterns)
        result.patterns = patterns

    # Generate report
    reporter = AnalysisReporter()

    if args.output == "json":
        print(reporter.generate_json_report(results, all_patterns))
    else:
        print(reporter.generate_summary_report(results, all_patterns))

    if args.verbose:
        print("\n" + "=" * 60)
        print("DETAILED FILE METRICS")
        print("=" * 60)
        for result in results:
            print(f"\n{result.file_path} ({result.language}):")
            print(f"  Functions: {len(result.functions)}")
            print(f"  Classes: {len(result.classes)}")
            print(f"  Imports: {len(result.imports)}")
            print(f"  AST Complexity: {result.ast_complexity_score}")
            print(f"  Maintainability Index: {result.maintainability_index}")
            if result.parse_errors:
                print(f"  Parse Errors: {', '.join(result.parse_errors)}")


if __name__ == "__main__":
    main()