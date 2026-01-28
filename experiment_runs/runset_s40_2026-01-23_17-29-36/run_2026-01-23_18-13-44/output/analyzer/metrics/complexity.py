"""
Code complexity metrics module for CodeViz.

This module implements various complexity measures including:
- Cyclomatic complexity (McCabe complexity)
- Cognitive complexity (SonarQube style)
- Halstead complexity metrics

Authors: Alice & Bob
"""

import ast
from typing import Dict, Any, List
from collections import defaultdict


class ComplexityAnalyzer:
    """
    Analyzes code complexity using multiple metrics.

    Provides cyclomatic complexity (decision points) and cognitive complexity
    (how hard code is to understand mentally) calculations.
    """

    def __init__(self):
        """Initialize the complexity analyzer."""
        self.results = {}

    def calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        Calculate McCabe cyclomatic complexity for a function or class.

        Cyclomatic complexity = E - N + 2P where:
        - E = number of edges in control flow graph
        - N = number of nodes
        - P = number of connected components (usually 1)

        Simplified: count decision points + 1

        Args:
            node: AST node (usually FunctionDef or ClassDef)

        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Decision points that increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += 1
                # Each except handler adds complexity
                complexity += len(child.handlers)
            elif isinstance(child, ast.ExceptHandler):
                # Already counted in Try, but need to handle nested
                continue
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # And/Or operations add complexity
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ListComp):
                # List comprehensions add complexity
                complexity += len(child.generators)
                for generator in child.generators:
                    complexity += len(generator.ifs)
            elif isinstance(child, (ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                # Other comprehensions
                complexity += len(child.generators)
                for generator in child.generators:
                    complexity += len(generator.ifs)

        return complexity

    def calculate_cognitive_complexity(self, node: ast.AST) -> int:
        """
        Calculate cognitive complexity based on SonarQube methodology.

        Cognitive complexity measures how hard code is to understand by
        weighting different control structures and nesting levels.

        Args:
            node: AST node to analyze

        Returns:
            Cognitive complexity score
        """
        complexity = 0
        nesting_level = 0

        def visit_node(n: ast.AST, current_nesting: int) -> int:
            nonlocal complexity
            current_complexity = 0

            # Control flow structures add base complexity + nesting
            if isinstance(n, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                current_complexity += 1 + current_nesting
                current_nesting += 1
            elif isinstance(n, ast.Try):
                current_complexity += 1 + current_nesting
                current_nesting += 1
            elif isinstance(n, ast.ExceptHandler):
                current_complexity += 1 + current_nesting
            elif isinstance(n, (ast.With, ast.AsyncWith)):
                current_complexity += 1 + current_nesting
                current_nesting += 1
            elif isinstance(n, ast.BoolOp):
                # Binary logical operators in conditions
                if isinstance(n.op, (ast.And, ast.Or)):
                    current_complexity += len(n.values) - 1
            elif isinstance(n, ast.Lambda):
                current_complexity += 1
            elif isinstance(n, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                # Comprehensions add complexity
                current_complexity += 1
                for generator in n.generators:
                    current_complexity += len(generator.ifs)

            # Recursively analyze children
            for child in ast.iter_child_nodes(n):
                current_complexity += visit_node(child, current_nesting)

            return current_complexity

        return visit_node(node, 0)

    def analyze_function_complexity(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """
        Analyze complexity metrics for a single function.

        Args:
            func_node: AST function definition node

        Returns:
            Dictionary with complexity metrics
        """
        cyclomatic = self.calculate_cyclomatic_complexity(func_node)
        cognitive = self.calculate_cognitive_complexity(func_node)

        # Calculate additional metrics
        line_count = (func_node.end_lineno - func_node.lineno + 1) if hasattr(func_node, 'end_lineno') else 0

        # Count nested levels
        max_nesting = self._calculate_max_nesting(func_node)

        # Classify complexity levels
        complexity_rating = self._get_complexity_rating(cyclomatic, cognitive)

        return {
            'function_name': func_node.name,
            'cyclomatic_complexity': cyclomatic,
            'cognitive_complexity': cognitive,
            'max_nesting_level': max_nesting,
            'line_count': line_count,
            'complexity_rating': complexity_rating,
            'metrics_explanation': {
                'cyclomatic': 'Measures number of linearly independent paths',
                'cognitive': 'Measures mental burden to understand the code'
            }
        }

    def _calculate_max_nesting(self, node: ast.AST) -> int:
        """Calculate maximum nesting depth in a function."""
        max_depth = 0

        def visit_node(n: ast.AST, current_depth: int) -> int:
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)

            new_depth = current_depth
            if isinstance(n, (ast.If, ast.While, ast.For, ast.AsyncFor,
                            ast.Try, ast.With, ast.AsyncWith)):
                new_depth += 1

            for child in ast.iter_child_nodes(n):
                visit_node(child, new_depth)

            return max_depth

        return visit_node(node, 0)

    def _get_complexity_rating(self, cyclomatic: int, cognitive: int) -> str:
        """
        Provide a human-readable complexity rating.

        Based on common industry thresholds.
        """
        # Weighted score combining both metrics
        combined_score = cyclomatic * 0.6 + cognitive * 0.4

        if combined_score <= 5:
            return "Low - Simple and easy to maintain"
        elif combined_score <= 10:
            return "Moderate - Acceptable complexity"
        elif combined_score <= 15:
            return "High - Consider refactoring"
        else:
            return "Very High - Refactoring strongly recommended"

    def analyze_file_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Analyze complexity for all functions and classes in a file.

        Args:
            tree: AST of the entire file

        Returns:
            Complete complexity analysis results
        """
        results = {
            'functions': [],
            'classes': [],
            'file_summary': {
                'total_functions': 0,
                'high_complexity_functions': 0,
                'average_cyclomatic': 0,
                'average_cognitive': 0
            }
        }

        cyclomatic_scores = []
        cognitive_scores = []

        # Analyze all functions (including methods)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_analysis = self.analyze_function_complexity(node)
                results['functions'].append(func_analysis)

                cyclomatic_scores.append(func_analysis['cyclomatic_complexity'])
                cognitive_scores.append(func_analysis['cognitive_complexity'])

                if func_analysis['complexity_rating'].startswith('High') or \
                   func_analysis['complexity_rating'].startswith('Very High'):
                    results['file_summary']['high_complexity_functions'] += 1

            elif isinstance(node, ast.ClassDef):
                # Analyze class-level complexity
                class_analysis = {
                    'class_name': node.name,
                    'method_count': len([n for n in ast.walk(node)
                                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]),
                    'line_count': (node.end_lineno - node.lineno + 1) if hasattr(node, 'end_lineno') else 0
                }
                results['classes'].append(class_analysis)

        # Calculate file summary statistics
        if cyclomatic_scores:
            results['file_summary']['total_functions'] = len(cyclomatic_scores)
            results['file_summary']['average_cyclomatic'] = sum(cyclomatic_scores) / len(cyclomatic_scores)
            results['file_summary']['average_cognitive'] = sum(cognitive_scores) / len(cognitive_scores)

        return results


def main():
    """Example usage of the ComplexityAnalyzer."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python complexity.py <file_path>")
        return

    # Parse the file
    with open(sys.argv[1], 'r') as f:
        source = f.read()

    tree = ast.parse(source)
    analyzer = ComplexityAnalyzer()
    results = analyzer.analyze_file_complexity(tree)

    print(f"\nComplexity Analysis for {sys.argv[1]}")
    print("=" * 50)

    summary = results['file_summary']
    print(f"Total functions: {summary['total_functions']}")
    print(f"High complexity functions: {summary['high_complexity_functions']}")
    print(f"Average cyclomatic complexity: {summary['average_cyclomatic']:.2f}")
    print(f"Average cognitive complexity: {summary['average_cognitive']:.2f}")

    print("\nFunction Details:")
    for func in results['functions']:
        print(f"\n  {func['function_name']}:")
        print(f"    Cyclomatic: {func['cyclomatic_complexity']}")
        print(f"    Cognitive: {func['cognitive_complexity']}")
        print(f"    Rating: {func['complexity_rating']}")


if __name__ == "__main__":
    main()