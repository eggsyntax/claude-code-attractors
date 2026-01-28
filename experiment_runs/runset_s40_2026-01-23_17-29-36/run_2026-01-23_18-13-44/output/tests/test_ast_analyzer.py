"""
Test suite for the AST analyzer module.

Tests cover basic parsing, function extraction, class analysis,
and import detection functionality.

Authors: Alice & Bob
"""

import ast
import unittest
import tempfile
import os
from pathlib import Path

# Import our modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from analyzer.core.ast_analyzer import CodeAnalyzer


class TestCodeAnalyzer(unittest.TestCase):
    """Test cases for the CodeAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = CodeAnalyzer()

    def test_parse_simple_file(self):
        """Test parsing a simple Python file."""
        test_code = '''
def hello_world():
    """A simple function."""
    print("Hello, world!")
    return "success"
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_path = f.name

        try:
            tree = self.analyzer.parse_file(temp_path)
            self.assertIsNotNone(tree)
            self.assertIsInstance(tree, ast.AST)
        finally:
            os.unlink(temp_path)

    def test_parse_invalid_file(self):
        """Test parsing a file with syntax errors."""
        invalid_code = '''
def broken_function(:
    print("This is invalid syntax")
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(invalid_code)
            temp_path = f.name

        try:
            tree = self.analyzer.parse_file(temp_path)
            self.assertIsNone(tree)
        finally:
            os.unlink(temp_path)

    def test_extract_simple_function(self):
        """Test extracting a simple function definition."""
        code = '''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b
'''
        tree = ast.parse(code)
        functions = self.analyzer.extract_functions(tree)

        self.assertEqual(len(functions), 1)
        func = functions[0]
        self.assertEqual(func['name'], 'calculate_sum')
        self.assertEqual(func['args'], ['a', 'b'])
        self.assertEqual(func['docstring'], 'Calculate sum of two numbers.')
        self.assertFalse(func['is_async'])
        self.assertEqual(func['decorators'], [])

    def test_extract_async_function(self):
        """Test extracting an async function."""
        code = '''
async def fetch_data():
    """Async function to fetch data."""
    return await some_api_call()
'''
        tree = ast.parse(code)
        functions = self.analyzer.extract_functions(tree)

        self.assertEqual(len(functions), 1)
        func = functions[0]
        self.assertEqual(func['name'], 'fetch_data')
        self.assertTrue(func['is_async'])

    def test_extract_decorated_function(self):
        """Test extracting a function with decorators."""
        code = '''
@property
@staticmethod
def decorated_function():
    return "decorated"
'''
        tree = ast.parse(code)
        functions = self.analyzer.extract_functions(tree)

        self.assertEqual(len(functions), 1)
        func = functions[0]
        self.assertEqual(func['name'], 'decorated_function')
        self.assertEqual(set(func['decorators']), {'property', 'staticmethod'})

    def test_extract_simple_class(self):
        """Test extracting a simple class definition."""
        code = '''
class Calculator:
    """A simple calculator class."""

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
'''
        tree = ast.parse(code)
        classes = self.analyzer.extract_classes(tree)

        self.assertEqual(len(classes), 1)
        cls = classes[0]
        self.assertEqual(cls['name'], 'Calculator')
        self.assertEqual(cls['docstring'], 'A simple calculator class.')
        self.assertEqual(set(cls['methods']), {'add', 'subtract'})
        self.assertEqual(cls['base_classes'], [])

    def test_extract_inherited_class(self):
        """Test extracting a class with inheritance."""
        code = '''
class AdvancedCalculator(Calculator, Mixin):
    """Calculator with advanced features."""
    pass
'''
        tree = ast.parse(code)
        classes = self.analyzer.extract_classes(tree)

        self.assertEqual(len(classes), 1)
        cls = classes[0]
        self.assertEqual(cls['name'], 'AdvancedCalculator')
        self.assertEqual(set(cls['base_classes']), {'Calculator', 'Mixin'})

    def test_extract_imports(self):
        """Test extracting import statements."""
        code = '''
import os
import sys as system
from pathlib import Path
from typing import Dict, List
'''
        tree = ast.parse(code)
        imports = self.analyzer.extract_imports(tree)

        # Should have 4 import entries
        self.assertEqual(len(imports), 4)

        # Test regular import
        os_import = next(imp for imp in imports if imp['module'] == 'os')
        self.assertEqual(os_import['type'], 'import')
        self.assertIsNone(os_import['alias'])

        # Test import with alias
        sys_import = next(imp for imp in imports if imp['module'] == 'sys')
        self.assertEqual(sys_import['type'], 'import')
        self.assertEqual(sys_import['alias'], 'system')

        # Test from import
        path_import = next(imp for imp in imports if imp['name'] == 'Path')
        self.assertEqual(path_import['type'], 'from_import')
        self.assertEqual(path_import['module'], 'pathlib')

    def test_analyze_complete_file(self):
        """Test complete file analysis."""
        test_code = '''
"""Test module for complete analysis."""

import os
from typing import List

class TestClass:
    """A test class."""

    def method_one(self):
        return "one"

    def method_two(self):
        return "two"

def standalone_function(param: str) -> str:
    """A standalone function."""
    return f"Hello, {param}!"

async def async_function():
    return await some_call()
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_path = f.name

        try:
            result = self.analyzer.analyze_file(temp_path)

            # Verify structure
            self.assertIn('file_path', result)
            self.assertIn('functions', result)
            self.assertIn('classes', result)
            self.assertIn('imports', result)
            self.assertIn('total_lines', result)

            # Check counts
            self.assertEqual(len(result['functions']), 4)  # 2 methods + 2 standalone
            self.assertEqual(len(result['classes']), 1)
            self.assertEqual(len(result['imports']), 2)
            self.assertGreater(result['total_lines'], 0)

            # Verify class details
            test_class = result['classes'][0]
            self.assertEqual(test_class['name'], 'TestClass')
            self.assertEqual(set(test_class['methods']), {'method_one', 'method_two'})

        finally:
            os.unlink(temp_path)

    def test_helper_methods(self):
        """Test private helper methods."""
        # Test return annotation extraction
        code = '''
def typed_function() -> str:
    return "test"
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        return_type = self.analyzer._get_return_annotation(func_node)
        # This might be 'str' or similar depending on Python version
        self.assertIsNotNone(return_type)

    def test_empty_file(self):
        """Test analyzing an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('')  # Empty file
            temp_path = f.name

        try:
            result = self.analyzer.analyze_file(temp_path)
            self.assertEqual(len(result['functions']), 0)
            self.assertEqual(len(result['classes']), 0)
            self.assertEqual(len(result['imports']), 0)
            self.assertEqual(result['total_lines'], 0)
        finally:
            os.unlink(temp_path)

    def test_nonexistent_file(self):
        """Test analyzing a nonexistent file."""
        result = self.analyzer.analyze_file('/nonexistent/file.py')
        self.assertEqual(result, {})


class TestIntegration(unittest.TestCase):
    """Integration tests for the analyzer system."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.analyzer = CodeAnalyzer()

    def test_analyze_own_code(self):
        """Test analyzing the analyzer's own code."""
        analyzer_path = Path(__file__).parent.parent / 'analyzer' / 'core' / 'ast_analyzer.py'

        if analyzer_path.exists():
            result = self.analyzer.analyze_file(str(analyzer_path))

            # Should find the CodeAnalyzer class
            class_names = [cls['name'] for cls in result['classes']]
            self.assertIn('CodeAnalyzer', class_names)

            # Should find key methods
            function_names = [func['name'] for func in result['functions']]
            expected_methods = ['parse_file', 'extract_functions', 'extract_classes', 'analyze_file']
            for method in expected_methods:
                self.assertIn(method, function_names)

            # Should have some imports
            self.assertGreater(len(result['imports']), 0)


if __name__ == '__main__':
    unittest.main()