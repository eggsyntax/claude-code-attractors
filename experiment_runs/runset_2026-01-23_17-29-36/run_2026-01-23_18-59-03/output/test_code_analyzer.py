#!/usr/bin/env python3
"""
Test suite for the Collaborative Code Analyzer.
Following CLAUDE.md guidelines: write tests BEFORE implementation.

Created by: Alice & Bob (Claude Code Collaboration)
"""

import ast
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

from code_analyzer import CodeParser, CodeMetrics, analyze_codebase


class TestCodeParser(unittest.TestCase):
    """Test cases for the CodeParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CodeParser()

    def test_parse_simple_file(self):
        """Test parsing a simple Python file."""
        sample_code = '''
def hello_world():
    """A simple function."""
    print("Hello, World!")
    return True

class TestClass:
    """A simple class."""
    def method(self):
        if True:
            return "test"
'''

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code)
            temp_path = f.name

        try:
            tree = self.parser.parse_file(temp_path)
            self.assertIsInstance(tree, ast.AST)
            self.assertIsInstance(tree, ast.Module)
        finally:
            Path(temp_path).unlink()

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist."""
        result = self.parser.parse_file("/nonexistent/path.py")
        self.assertIsNone(result)

    def test_parse_invalid_syntax(self):
        """Test parsing a file with invalid Python syntax."""
        invalid_code = "def incomplete_function("

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(invalid_code)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            self.assertIsNone(result)
        finally:
            Path(temp_path).unlink()

    def test_extract_metrics_simple_code(self):
        """Test metric extraction from simple code."""
        sample_code = '''
import os
from pathlib import Path

def function_one():
    if True:
        return 1
    else:
        return 0

def function_two():
    for i in range(10):
        if i > 5:
            print(i)

class MyClass:
    def method_one(self):
        pass
'''
        tree = ast.parse(sample_code)
        metrics = self.parser.extract_metrics(tree, "test_file.py")

        self.assertIsInstance(metrics, CodeMetrics)
        self.assertEqual(metrics.file_path, "test_file.py")
        self.assertEqual(metrics.function_count, 3)  # function_one, function_two, method_one
        self.assertEqual(metrics.class_count, 1)     # MyClass
        self.assertEqual(metrics.import_count, 2)    # os, pathlib
        self.assertIn("function_one", metrics.functions)
        self.assertIn("function_two", metrics.functions)
        self.assertIn("method_one", metrics.functions)
        self.assertIn("MyClass", metrics.classes)
        self.assertIn("os", metrics.dependencies)
        self.assertIn("pathlib", metrics.dependencies)

    def test_complexity_calculation(self):
        """Test cyclomatic complexity calculation."""
        # Simple function with no branches
        simple_code = '''
def simple():
    print("hello")
    return True
'''
        tree = ast.parse(simple_code)
        metrics = self.parser.extract_metrics(tree, "simple.py")
        self.assertEqual(metrics.complexity, 1)  # Base complexity

        # Function with if statement
        complex_code = '''
def complex_function(x):
    if x > 0:
        if x > 10:
            return "big"
        else:
            return "small"
    elif x < 0:
        return "negative"
    else:
        return "zero"
'''
        tree = ast.parse(complex_code)
        metrics = self.parser.extract_metrics(tree, "complex.py")
        self.assertGreater(metrics.complexity, 1)

    def test_empty_file(self):
        """Test handling of empty Python files."""
        empty_code = ""
        tree = ast.parse(empty_code)
        metrics = self.parser.extract_metrics(tree, "empty.py")

        self.assertEqual(metrics.function_count, 0)
        self.assertEqual(metrics.class_count, 0)
        self.assertEqual(metrics.import_count, 0)
        self.assertEqual(len(metrics.functions), 0)
        self.assertEqual(len(metrics.classes), 0)
        self.assertEqual(len(metrics.dependencies), 0)


class TestCodebaseAnalysis(unittest.TestCase):
    """Test cases for codebase analysis functionality."""

    def test_analyze_single_file_directory(self):
        """Test analyzing a directory with a single Python file."""
        sample_code = '''
def test_function():
    """Test function for analysis."""
    return "success"

class TestClass:
    def test_method(self):
        return True
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text(sample_code)

            results = analyze_codebase(temp_dir)

            self.assertEqual(len(results), 1)
            self.assertIsInstance(results[0], CodeMetrics)
            self.assertEqual(results[0].function_count, 2)  # test_function + test_method
            self.assertEqual(results[0].class_count, 1)     # TestClass

    def test_analyze_empty_directory(self):
        """Test analyzing an empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results = analyze_codebase(temp_dir)
            self.assertEqual(len(results), 0)

    def test_analyze_directory_with_non_python_files(self):
        """Test analyzing a directory with mixed file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Python file
            python_file = Path(temp_dir) / "code.py"
            python_file.write_text("def hello(): pass")

            # Create non-Python file
            text_file = Path(temp_dir) / "readme.txt"
            text_file.write_text("This is not Python code")

            results = analyze_codebase(temp_dir)

            self.assertEqual(len(results), 1)  # Only Python file should be analyzed
            self.assertTrue(results[0].file_path.endswith("code.py"))

    def test_analyze_nested_directories(self):
        """Test analyzing nested directory structures."""
        sample_code = "def nested_function(): return 'nested'"

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested directory structure
            nested_dir = Path(temp_dir) / "subdir" / "nested"
            nested_dir.mkdir(parents=True)

            # Create Python files at different levels
            (Path(temp_dir) / "root.py").write_text(sample_code)
            (Path(temp_dir) / "subdir" / "sub.py").write_text(sample_code)
            (nested_dir / "nested.py").write_text(sample_code)

            results = analyze_codebase(temp_dir)

            self.assertEqual(len(results), 3)  # Should find all three files
            file_names = [Path(result.file_path).name for result in results]
            self.assertIn("root.py", file_names)
            self.assertIn("sub.py", file_names)
            self.assertIn("nested.py", file_names)


class TestCodeMetrics(unittest.TestCase):
    """Test cases for the CodeMetrics dataclass."""

    def test_code_metrics_creation(self):
        """Test creating a CodeMetrics instance."""
        metrics = CodeMetrics(
            file_path="/test/path.py",
            lines_of_code=100,
            complexity=5,
            function_count=3,
            class_count=1,
            import_count=2,
            functions=["func1", "func2", "func3"],
            classes=["Class1"],
            dependencies=["os", "sys"]
        )

        self.assertEqual(metrics.file_path, "/test/path.py")
        self.assertEqual(metrics.lines_of_code, 100)
        self.assertEqual(metrics.complexity, 5)
        self.assertEqual(metrics.function_count, 3)
        self.assertEqual(metrics.class_count, 1)
        self.assertEqual(metrics.import_count, 2)
        self.assertEqual(len(metrics.functions), 3)
        self.assertEqual(len(metrics.classes), 1)
        self.assertEqual(len(metrics.dependencies), 2)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)