"""
Core AST analysis module for CodeViz.

This module provides the foundation for parsing and analyzing Python code
using the Abstract Syntax Tree (AST) approach.

Authors: Alice & Bob
"""

import ast
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path


class CodeAnalyzer:
    """
    Main analyzer class that processes Python source code and extracts
    structural information using AST parsing.
    """

    def __init__(self, source_path: Optional[str] = None):
        """
        Initialize the analyzer with optional source path.

        Args:
            source_path: Path to the source file or directory to analyze
        """
        self.source_path = source_path
        self.analysis_results = {}

    def parse_file(self, file_path: str) -> Optional[ast.AST]:
        """
        Parse a single Python file and return its AST.

        Args:
            file_path: Path to the Python file

        Returns:
            AST object or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source = file.read()
            return ast.parse(source, filename=file_path)
        except (SyntaxError, FileNotFoundError, UnicodeDecodeError) as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Extract function definitions and their metadata from AST.

        Args:
            tree: AST object to analyze

        Returns:
            List of function metadata dictionaries
        """
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno if hasattr(node, 'end_lineno') else None,
                    'args': [arg.arg for arg in node.args.args],
                    'returns': self._get_return_annotation(node),
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list],
                    'docstring': ast.get_docstring(node)
                }
                functions.append(func_info)

        return functions

    def extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Extract class definitions and their metadata from AST.

        Args:
            tree: AST object to analyze

        Returns:
            List of class metadata dictionaries
        """
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(item.name)

                class_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno if hasattr(node, 'end_lineno') else None,
                    'base_classes': [self._get_base_class_name(base) for base in node.bases],
                    'methods': methods,
                    'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list],
                    'docstring': ast.get_docstring(node)
                }
                classes.append(class_info)

        return classes

    def extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Extract import statements and their details from AST.

        Args:
            tree: AST object to analyze

        Returns:
            List of import metadata dictionaries
        """
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno,
                        'level': node.level
                    })

        return imports

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Perform complete analysis of a single Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            Dictionary containing all analysis results
        """
        tree = self.parse_file(file_path)
        if not tree:
            return {}

        return {
            'file_path': file_path,
            'functions': self.extract_functions(tree),
            'classes': self.extract_classes(tree),
            'imports': self.extract_imports(tree),
            'total_lines': len(open(file_path, 'r').readlines()) if Path(file_path).exists() else 0
        }

    def _get_return_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Helper to extract return type annotation as string."""
        if node.returns:
            return ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        return None

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Helper to extract decorator name as string."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
            return decorator.func.id
        return str(decorator)

    def _get_base_class_name(self, base: ast.expr) -> str:
        """Helper to extract base class name as string."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else str(base)
        return str(base)


def main():
    """Example usage of the CodeAnalyzer."""
    if len(sys.argv) < 2:
        print("Usage: python ast_analyzer.py <file_path>")
        return

    analyzer = CodeAnalyzer()
    result = analyzer.analyze_file(sys.argv[1])

    print(f"Analysis of {result.get('file_path', 'unknown')}")
    print(f"Lines: {result.get('total_lines', 0)}")
    print(f"Functions: {len(result.get('functions', []))}")
    print(f"Classes: {len(result.get('classes', []))}")
    print(f"Imports: {len(result.get('imports', []))}")


if __name__ == "__main__":
    main()