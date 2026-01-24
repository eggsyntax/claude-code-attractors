#!/usr/bin/env python3
"""
Code Analyzer - A foundation for syntax tree analysis and code metrics

This tool provides a flexible framework for analyzing codebases using
tree-sitter parsers with extensible analysis modules and reporting.

Usage:
    python code_analyzer.py <directory> [--language <lang>] [--output <format>]

Example:
    python code_analyzer.py ./src --language python --output json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import ast
import re


@dataclass
class CodeMetrics:
    """Core metrics collected from code analysis"""
    file_path: str
    language: str
    lines_of_code: int
    cyclomatic_complexity: int
    function_count: int
    class_count: int
    import_count: int
    comment_lines: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LanguageDetector:
    """Simple language detection based on file extensions"""

    EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.rs': 'rust',
        '.go': 'go',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.rb': 'ruby',
        '.php': 'php'
    }

    @classmethod
    def detect(cls, file_path: str) -> Optional[str]:
        """Detect language from file extension"""
        suffix = Path(file_path).suffix.lower()
        return cls.EXTENSIONS.get(suffix)


class PythonAnalyzer:
    """Python-specific analyzer using AST"""

    def analyze_file(self, file_path: str, content: str) -> CodeMetrics:
        """Analyze Python file using AST parsing"""
        lines = content.split('\n')

        # Basic line counting
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])

        function_count = 0
        class_count = 0
        import_count = 0
        complexity = 1

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_count += 1
                elif isinstance(node, ast.ClassDef):
                    class_count += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_count += 1
                # Complexity indicators
                elif isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                    complexity += 1
                elif isinstance(node, (ast.And, ast.Or)):
                    complexity += 1

        except SyntaxError:
            # If AST parsing fails, fall back to regex patterns
            function_count = len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
            class_count = len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE))
            import_count = len(re.findall(r'^\s*(import|from)\s+', content, re.MULTILINE))

        return CodeMetrics(
            file_path=file_path,
            language='python',
            lines_of_code=code_lines,
            cyclomatic_complexity=complexity,
            function_count=function_count,
            class_count=class_count,
            import_count=import_count,
            comment_lines=comment_lines
        )


class JavaScriptAnalyzer:
    """JavaScript/TypeScript analyzer using regex patterns"""

    def analyze_file(self, file_path: str, content: str) -> CodeMetrics:
        """Analyze JavaScript/TypeScript file using pattern matching"""
        lines = content.split('\n')

        # Count different line types
        comment_lines = len([l for l in lines if l.strip().startswith('//') or l.strip().startswith('/*')])
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('/*')])

        # Function patterns
        function_patterns = [
            r'function\s+\w+\s*\(',
            r'\w+\s*:\s*function\s*\(',
            r'\w+\s*=\s*\([^)]*\)\s*=>',
            r'async\s+function\s+\w+\s*\(',
        ]

        function_count = 0
        for pattern in function_patterns:
            function_count += len(re.findall(pattern, content))

        # Classes
        class_count = len(re.findall(r'class\s+\w+', content))

        # Imports
        import_patterns = [
            r'import\s+.*?from',
            r'require\s*\(',
            r'import\s*\('
        ]

        import_count = 0
        for pattern in import_patterns:
            import_count += len(re.findall(pattern, content))

        # Complexity estimation
        complexity_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'catch', '&&', '||']
        complexity = 1
        for keyword in complexity_keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', content))

        return CodeMetrics(
            file_path=file_path,
            language='javascript',
            lines_of_code=code_lines,
            cyclomatic_complexity=complexity,
            function_count=function_count,
            class_count=class_count,
            import_count=import_count,
            comment_lines=comment_lines
        )


class GenericAnalyzer:
    """Generic analyzer for unsupported languages"""

    def analyze_file(self, file_path: str, content: str, language: str) -> CodeMetrics:
        """Basic analysis for any file type"""
        lines = content.split('\n')
        code_lines = len([l for l in lines if l.strip()])

        # Simple heuristics for different languages
        comment_patterns = {
            'rust': [r'^\s*//', r'^\s*/\*'],
            'go': [r'^\s*//'],
            'java': [r'^\s*//', r'^\s*/\*'],
            'c': [r'^\s*//', r'^\s*/\*'],
            'cpp': [r'^\s*//', r'^\s*/\*'],
            'ruby': [r'^\s*#'],
            'php': [r'^\s*//', r'^\s*#']
        }

        comment_lines = 0
        if language in comment_patterns:
            for pattern in comment_patterns[language]:
                comment_lines += len(re.findall(pattern, content, re.MULTILINE))

        # Basic function detection patterns
        function_patterns = {
            'rust': [r'fn\s+\w+'],
            'go': [r'func\s+\w+'],
            'java': [r'(public|private|protected).*?\s+\w+\s*\('],
            'c': [r'\w+\s+\w+\s*\([^)]*\)\s*\{'],
            'cpp': [r'\w+\s+\w+\s*\([^)]*\)\s*\{'],
            'ruby': [r'def\s+\w+'],
            'php': [r'function\s+\w+']
        }

        function_count = 0
        if language in function_patterns:
            for pattern in function_patterns[language]:
                function_count += len(re.findall(pattern, content))

        return CodeMetrics(
            file_path=file_path,
            language=language,
            lines_of_code=code_lines,
            cyclomatic_complexity=1,  # Placeholder
            function_count=function_count,
            class_count=0,  # Placeholder
            import_count=0,  # Placeholder
            comment_lines=comment_lines
        )


class CodeAnalyzer:
    """Main analyzer orchestrator"""

    def __init__(self):
        self.python_analyzer = PythonAnalyzer()
        self.js_analyzer = JavaScriptAnalyzer()
        self.generic_analyzer = GenericAnalyzer()

    def analyze_file(self, file_path: str) -> Optional[CodeMetrics]:
        """Analyze a single file"""
        try:
            language = LanguageDetector.detect(file_path)
            if not language:
                return None

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Use appropriate analyzer
            if language == 'python':
                return self.python_analyzer.analyze_file(file_path, content)
            elif language in ['javascript', 'typescript']:
                return self.js_analyzer.analyze_file(file_path, content)
            else:
                return self.generic_analyzer.analyze_file(file_path, content, language)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def analyze_directory(self, directory: str, language_filter: Optional[str] = None) -> List[CodeMetrics]:
        """Analyze all files in a directory recursively"""
        results = []

        for root, dirs, files in os.walk(directory):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', 'target', '.vscode', 'dist', 'build'}]

            for file in files:
                file_path = os.path.join(root, file)

                # Skip binary and large files
                if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB limit
                    continue

                metrics = self.analyze_file(file_path)

                if metrics and (not language_filter or metrics.language == language_filter):
                    results.append(metrics)

        return results

    def generate_summary(self, metrics: List[CodeMetrics]) -> Dict[str, Any]:
        """Generate summary statistics from metrics"""
        if not metrics:
            return {}

        by_language = defaultdict(list)

        for metric in metrics:
            by_language[metric.language].append(metric)

        summary = {
            'total_files': len(metrics),
            'total_lines': sum(m.lines_of_code for m in metrics),
            'languages': {}
        }

        for lang, lang_metrics in by_language.items():
            summary['languages'][lang] = {
                'files': len(lang_metrics),
                'lines_of_code': sum(m.lines_of_code for m in lang_metrics),
                'functions': sum(m.function_count for m in lang_metrics),
                'classes': sum(m.class_count for m in lang_metrics),
                'avg_complexity': sum(m.cyclomatic_complexity for m in lang_metrics) / len(lang_metrics) if lang_metrics else 0,
                'comment_lines': sum(m.comment_lines for m in lang_metrics),
                'imports': sum(m.import_count for m in lang_metrics)
            }

        return summary


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Analyze codebase metrics and complexity')
    parser.add_argument('directory', help='Directory to analyze')
    parser.add_argument('--language', '-l', help='Filter by specific language')
    parser.add_argument('--output', '-o', choices=['json', 'summary'], default='summary',
                       help='Output format (json or summary)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)

    print(f"Analyzing directory: {args.directory}")
    if args.language:
        print(f"Language filter: {args.language}")

    analyzer = CodeAnalyzer()
    metrics = analyzer.analyze_directory(args.directory, args.language)

    if not metrics:
        print("No source files found to analyze")
        return

    if args.output == 'json':
        output = {
            'metrics': [m.to_dict() for m in metrics],
            'summary': analyzer.generate_summary(metrics)
        }
        print(json.dumps(output, indent=2))
    else:
        # Summary output
        summary = analyzer.generate_summary(metrics)

        print(f"\n=== Code Analysis Summary ===")
        print(f"Total files analyzed: {summary['total_files']}")
        print(f"Total lines of code: {summary['total_lines']}")
        print(f"\nBreakdown by language:")

        for lang, stats in summary['languages'].items():
            print(f"\n{lang.upper()}:")
            print(f"  Files: {stats['files']}")
            print(f"  Lines: {stats['lines_of_code']}")
            print(f"  Functions: {stats['functions']}")
            print(f"  Classes: {stats['classes']}")
            print(f"  Imports: {stats['imports']}")
            print(f"  Avg Complexity: {stats['avg_complexity']:.1f}")
            print(f"  Comment Lines: {stats['comment_lines']}")

        if args.verbose:
            print(f"\n=== Detailed File Metrics ===")
            for metric in sorted(metrics, key=lambda m: m.lines_of_code, reverse=True):
                print(f"{metric.file_path} ({metric.language}): {metric.lines_of_code} LOC, "
                      f"{metric.function_count} functions, complexity {metric.cyclomatic_complexity}")


if __name__ == '__main__':
    main()