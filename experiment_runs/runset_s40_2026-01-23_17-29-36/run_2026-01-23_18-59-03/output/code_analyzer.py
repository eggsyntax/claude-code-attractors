#!/usr/bin/env python3
"""
Collaborative Code Analyzer - Main Module
A tool for analyzing and visualizing code structure and metrics.

Created by: Alice & Bob (Claude Code Collaboration)
"""

import ast
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

# Configure logging per CLAUDE.md guidelines
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CodeMetrics:
    """Container for code analysis metrics."""
    file_path: str
    lines_of_code: int
    complexity: int
    function_count: int
    class_count: int
    import_count: int
    functions: List[str]
    classes: List[str]
    dependencies: List[str]


class CodeParser:
    """Handles parsing Python source code into analyzable structures."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def parse_file(self, file_path: Union[str, Path]) -> Optional[ast.AST]:
        """
        Parse a Python file and return its AST.

        Args:
            file_path: Path to the Python file to parse

        Returns:
            Parsed AST or None if parsing fails
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            self.logger.error(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
        return None

    def extract_metrics(self, tree: ast.AST, file_path: str) -> CodeMetrics:
        """
        Extract basic metrics from an AST.

        Args:
            tree: The AST to analyze
            file_path: Path of the source file

        Returns:
            CodeMetrics object with extracted information
        """
        functions = []
        classes = []
        dependencies = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                else:  # ImportFrom
                    if node.module:
                        dependencies.append(node.module)

        # Calculate lines of code (simplified - could be more sophisticated)
        lines_of_code = len([node for node in ast.walk(tree) if hasattr(node, 'lineno')])

        # Basic complexity (simplified cyclomatic complexity)
        complexity = self._calculate_complexity(tree)

        return CodeMetrics(
            file_path=file_path,
            lines_of_code=lines_of_code,
            complexity=complexity,
            function_count=len(functions),
            class_count=len(classes),
            import_count=len(dependencies),
            functions=functions,
            classes=classes,
            dependencies=dependencies
        )

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate basic cyclomatic complexity."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With,
                               ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity


def analyze_codebase(directory: Union[str, Path]) -> List[CodeMetrics]:
    """
    Analyze all Python files in a directory.

    Args:
        directory: Path to the directory to analyze

    Returns:
        List of CodeMetrics for all analyzed files
    """
    directory = Path(directory)
    parser = CodeParser()
    results = []

    logger.info(f"Starting analysis of codebase: {directory}")

    python_files = list(directory.rglob("*.py"))
    logger.info(f"Found {len(python_files)} Python files")

    for file_path in python_files:
        logger.debug(f"Analyzing: {file_path}")
        tree = parser.parse_file(file_path)
        if tree:
            metrics = parser.extract_metrics(tree, str(file_path))
            results.append(metrics)

    logger.info(f"Analysis complete. Processed {len(results)} files successfully")
    return results


if __name__ == "__main__":
    # Simple CLI for testing
    import sys

    if len(sys.argv) != 2:
        print("Usage: python code_analyzer.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    metrics = analyze_codebase(directory)

    # Output summary
    total_loc = sum(m.lines_of_code for m in metrics)
    total_functions = sum(m.function_count for m in metrics)
    total_classes = sum(m.class_count for m in metrics)

    print(f"\nCodebase Analysis Summary:")
    print(f"Files analyzed: {len(metrics)}")
    print(f"Total lines of code: {total_loc}")
    print(f"Total functions: {total_functions}")
    print(f"Total classes: {total_classes}")
    print(f"Average complexity: {sum(m.complexity for m in metrics) / len(metrics):.2f}")