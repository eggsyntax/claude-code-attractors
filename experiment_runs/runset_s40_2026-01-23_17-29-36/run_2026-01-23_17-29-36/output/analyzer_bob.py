"""
Bob's Analysis Engine - Performance and Security Focus

This module provides analysis capabilities focused on:
- Performance bottlenecks and algorithmic complexity
- Security vulnerabilities and code safety
- Resource optimization opportunities
- Efficiency patterns and anti-patterns
"""

import ast
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Finding:
    """Represents a single analysis finding"""
    category: str  # 'performance', 'security', 'resource'
    severity: str  # 'critical', 'major', 'minor', 'info'
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0


class PerformanceAnalyzer:
    """Analyzes code for performance issues"""

    def analyze_complexity(self, tree: ast.AST, file_path: str) -> List[Finding]:
        """Identify algorithmic complexity issues"""
        findings = []

        class ComplexityVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Look for nested loops
                nested_loops = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)) and child != node:
                        nested_loops += 1

                if nested_loops >= 2:
                    findings.append(Finding(
                        category='performance',
                        severity='major',
                        title='Potential O(n³) or higher complexity',
                        description=f'Found {nested_loops + 1} levels of nested loops which may indicate high algorithmic complexity',
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestion='Consider optimizing data structures (e.g., using dictionaries for lookups) or algorithmic approach',
                        confidence=0.8
                    ))
                elif nested_loops >= 1:
                    findings.append(Finding(
                        category='performance',
                        severity='minor',
                        title='Potential O(n²) complexity',
                        description=f'Found {nested_loops + 1} levels of nested loops',
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestion='Review if this can be optimized with better data structures or algorithms',
                        confidence=0.7
                    ))

                self.generic_visit(node)

        ComplexityVisitor().visit(tree)
        return findings

    def analyze_inefficient_patterns(self, tree: ast.AST, file_path: str) -> List[Finding]:
        """Find inefficient coding patterns"""
        findings = []

        class InefficiencyVisitor(ast.NodeVisitor):
            def visit_ListComp(self, node):
                # Look for list comprehensions that could be generator expressions
                parent_context = getattr(node, 'parent_context', None)
                if isinstance(parent_context, (ast.Call,)) and len(node.generators) > 0:
                    findings.append(Finding(
                        category='performance',
                        severity='minor',
                        title='List comprehension could be generator expression',
                        description='Using generator expressions can be more memory efficient for large datasets',
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestion='Consider using generator expression: (x for x in iterable) instead of [x for x in iterable]',
                        confidence=0.6
                    ))

                self.generic_visit(node)

            def visit_Call(self, node):
                # Look for inefficient string concatenation
                if (isinstance(node.func, ast.Attribute) and
                    isinstance(node.func.value, ast.Name) and
                    node.func.attr == 'join' and
                    isinstance(node.func.value.id, str) and
                    node.func.value.id == 'str'):
                    pass  # This is good - using str.join()
                elif (isinstance(node.func, ast.Name) and
                      node.func.id in ['print', 'str'] and
                      any(isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add)
                          for arg in node.args)):
                    findings.append(Finding(
                        category='performance',
                        severity='minor',
                        title='String concatenation in loop may be inefficient',
                        description='String concatenation with + in loops creates multiple string objects',
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestion='Consider using str.join() or f-strings for better performance',
                        confidence=0.7
                    ))

                self.generic_visit(node)

        InefficiencyVisitor().visit(tree)
        return findings


class SecurityAnalyzer:
    """Analyzes code for security vulnerabilities"""

    def analyze_sql_injection(self, source_code: str, file_path: str) -> List[Finding]:
        """Look for potential SQL injection vulnerabilities"""
        findings = []
        lines = source_code.split('\n')

        # Patterns that might indicate SQL injection risks
        dangerous_patterns = [
            (r'execute\s*\(\s*["\'].*%.*["\']', 'String formatting in SQL execute'),
            (r'execute\s*\(\s*.*\+.*\)', 'String concatenation in SQL execute'),
            (r'cursor\.execute\s*\(\s*f["\']', 'F-string in SQL execute'),
            (r'query\s*=.*["\'].*%.*["\']', 'String formatting in SQL query construction'),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, description in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(Finding(
                        category='security',
                        severity='critical',
                        title='Potential SQL Injection vulnerability',
                        description=f'{description} detected',
                        file_path=file_path,
                        line_number=line_num,
                        suggestion='Use parameterized queries or prepared statements instead',
                        confidence=0.8
                    ))

        return findings

    def analyze_input_validation(self, tree: ast.AST, file_path: str) -> List[Finding]:
        """Check for missing input validation"""
        findings = []

        class InputVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check if function takes parameters but has no validation
                if node.args.args and len(node.args.args) > 1:  # Skip self parameter
                    has_validation = False
                    for child in node.body:
                        if isinstance(child, ast.If):
                            # Look for validation patterns
                            has_validation = True
                            break
                        elif isinstance(child, ast.Assert):
                            has_validation = True
                            break

                    if not has_validation:
                        findings.append(Finding(
                            category='security',
                            severity='minor',
                            title='Function lacks input validation',
                            description=f'Function {node.name} accepts parameters but has no visible validation',
                            file_path=file_path,
                            line_number=node.lineno,
                            suggestion='Consider adding input validation for parameters, especially for public APIs',
                            confidence=0.5
                        ))

                self.generic_visit(node)

        InputVisitor().visit(tree)
        return findings


class BobAnalyzer:
    """Main analyzer class that orchestrates Bob's analysis capabilities"""

    def __init__(self):
        self.performance_analyzer = PerformanceAnalyzer()
        self.security_analyzer = SecurityAnalyzer()

    def analyze_file(self, file_path: str) -> List[Finding]:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Parse AST for structural analysis
            tree = ast.parse(source_code)

            findings = []

            # Performance analysis
            findings.extend(self.performance_analyzer.analyze_complexity(tree, file_path))
            findings.extend(self.performance_analyzer.analyze_inefficient_patterns(tree, file_path))

            # Security analysis
            findings.extend(self.security_analyzer.analyze_sql_injection(source_code, file_path))
            findings.extend(self.security_analyzer.analyze_input_validation(tree, file_path))

            return findings

        except Exception as e:
            return [Finding(
                category='error',
                severity='critical',
                title='Analysis failed',
                description=f'Could not analyze file: {str(e)}',
                file_path=file_path,
                confidence=1.0
            )]

    def analyze_directory(self, directory_path: str) -> List[Finding]:
        """Analyze all Python files in a directory"""
        findings = []
        path = Path(directory_path)

        for py_file in path.rglob('*.py'):
            findings.extend(self.analyze_file(str(py_file)))

        return findings


def main():
    """Test the analyzer on itself"""
    analyzer = BobAnalyzer()
    findings = analyzer.analyze_file(__file__)

    print("Bob's Analysis Results:")
    print("=" * 50)
    for finding in findings:
        print(f"\n{finding.severity.upper()}: {finding.title}")
        print(f"Category: {finding.category}")
        print(f"Line: {finding.line_number}")
        print(f"Description: {finding.description}")
        if finding.suggestion:
            print(f"Suggestion: {finding.suggestion}")
        print(f"Confidence: {finding.confidence:.1%}")


if __name__ == "__main__":
    main()