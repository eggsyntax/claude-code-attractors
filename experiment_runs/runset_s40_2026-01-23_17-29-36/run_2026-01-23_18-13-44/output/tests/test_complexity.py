"""
Test suite for the complexity analysis module.

Tests cover cyclomatic complexity, cognitive complexity,
and overall file analysis functionality.

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
from analyzer.metrics.complexity import ComplexityAnalyzer


class TestComplexityAnalyzer(unittest.TestCase):
    """Test cases for complexity analysis functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ComplexityAnalyzer()

    def test_simple_function_complexity(self):
        """Test complexity of a simple function (should be 1)."""
        code = '''
def simple_function():
    """A simple function with no branches."""
    x = 1
    y = 2
    return x + y
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        cyclomatic = self.analyzer.calculate_cyclomatic_complexity(func_node)
        cognitive = self.analyzer.calculate_cognitive_complexity(func_node)

        self.assertEqual(cyclomatic, 1)  # No branches = complexity 1
        self.assertEqual(cognitive, 0)   # No mental burden

    def test_if_statement_complexity(self):
        """Test complexity of a function with if statements."""
        code = '''
def function_with_if(x):
    """Function with conditional logic."""
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        cyclomatic = self.analyzer.calculate_cyclomatic_complexity(func_node)
        cognitive = self.analyzer.calculate_cognitive_complexity(func_node)

        self.assertEqual(cyclomatic, 3)  # if + elif = 2 decision points + 1
        self.assertGreater(cognitive, 0)

    def test_loop_complexity(self):
        """Test complexity of functions with loops."""
        code = '''
def function_with_loops(items):
    """Function with loop structures."""
    result = []
    for item in items:
        if item % 2 == 0:
            result.append(item * 2)
    return result
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        cyclomatic = self.analyzer.calculate_cyclomatic_complexity(func_node)
        cognitive = self.analyzer.calculate_cognitive_complexity(func_node)

        self.assertEqual(cyclomatic, 3)  # for loop + if = 2 + 1
        self.assertGreater(cognitive, 1)  # Nesting should increase cognitive load

    def test_nested_complexity(self):
        """Test complexity with nested control structures."""
        code = '''
def nested_function(data):
    """Function with nested structures."""
    for outer in data:
        if outer:
            for inner in outer:
                if inner > 0:
                    try:
                        result = process(inner)
                        if result:
                            return result
                    except Exception:
                        continue
    return None
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        cyclomatic = self.analyzer.calculate_cyclomatic_complexity(func_node)
        cognitive = self.analyzer.calculate_cognitive_complexity(func_node)

        self.assertGreater(cyclomatic, 5)  # Multiple decision points
        self.assertGreater(cognitive, 5)   # High nesting should increase cognitive load

    def test_boolean_operations(self):
        """Test complexity with boolean operations."""
        code = '''
def boolean_logic(a, b, c):
    """Function with boolean operations."""
    if a and b or c:
        return True
    elif a or (b and c):
        return False
    return None
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        cyclomatic = self.analyzer.calculate_cyclomatic_complexity(func_node)

        # Should account for boolean operations
        self.assertGreater(cyclomatic, 2)

    def test_comprehensions(self):
        """Test complexity with list comprehensions."""
        code = '''
def with_comprehensions(data):
    """Function using comprehensions."""
    evens = [x for x in data if x % 2 == 0]
    odds_dict = {x: x**2 for x in data if x % 2 == 1}
    return evens, odds_dict
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        cyclomatic = self.analyzer.calculate_cyclomatic_complexity(func_node)
        cognitive = self.analyzer.calculate_cognitive_complexity(func_node)

        self.assertGreater(cyclomatic, 1)  # Comprehensions add complexity
        self.assertGreater(cognitive, 0)

    def test_exception_handling(self):
        """Test complexity with exception handling."""
        code = '''
def with_exceptions(data):
    """Function with exception handling."""
    try:
        result = risky_operation(data)
        return result
    except ValueError:
        return "value_error"
    except TypeError:
        return "type_error"
    except Exception as e:
        log_error(e)
        return "general_error"
    finally:
        cleanup()
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        cyclomatic = self.analyzer.calculate_cyclomatic_complexity(func_node)

        # Try + 3 except handlers = 4 additional complexity
        self.assertEqual(cyclomatic, 5)  # 1 + 1 (try) + 3 (handlers)

    def test_analyze_function_complexity(self):
        """Test the complete function analysis."""
        code = '''
def complex_function(data):
    """A moderately complex function."""
    if not data:
        return []

    result = []
    for item in data:
        if isinstance(item, dict):
            for key, value in item.items():
                if value is not None:
                    result.append(f"{key}: {value}")
        elif isinstance(item, str):
            result.append(item.upper())

    return result
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        analysis = self.analyzer.analyze_function_complexity(func_node)

        # Verify analysis structure
        expected_keys = [
            'function_name', 'cyclomatic_complexity', 'cognitive_complexity',
            'max_nesting_level', 'line_count', 'complexity_rating', 'metrics_explanation'
        ]
        for key in expected_keys:
            self.assertIn(key, analysis)

        self.assertEqual(analysis['function_name'], 'complex_function')
        self.assertGreater(analysis['cyclomatic_complexity'], 1)
        self.assertGreater(analysis['cognitive_complexity'], 0)
        self.assertGreater(analysis['max_nesting_level'], 1)
        self.assertIsInstance(analysis['complexity_rating'], str)

    def test_complexity_rating(self):
        """Test complexity rating classifications."""
        # Test with different complexity levels
        ratings = [
            self.analyzer._get_complexity_rating(1, 0),    # Low
            self.analyzer._get_complexity_rating(5, 3),    # Low-Moderate
            self.analyzer._get_complexity_rating(10, 8),   # High
            self.analyzer._get_complexity_rating(20, 15)   # Very High
        ]

        self.assertTrue(ratings[0].startswith('Low'))
        self.assertTrue(ratings[-1].startswith('Very High'))

    def test_max_nesting_calculation(self):
        """Test maximum nesting level calculation."""
        code = '''
def deeply_nested():
    """Function with deep nesting."""
    if True:                    # Level 1
        for i in range(10):     # Level 2
            if i % 2 == 0:      # Level 3
                try:            # Level 4
                    with open('file') as f:  # Level 5
                        if f.read():         # Level 6
                            pass
                except:
                    pass
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        max_nesting = self.analyzer._calculate_max_nesting(func_node)
        self.assertGreaterEqual(max_nesting, 5)  # Should detect deep nesting

    def test_file_complexity_analysis(self):
        """Test analyzing complexity for an entire file."""
        code = '''
def simple_func():
    return 1

def moderate_func(x):
    if x > 0:
        return x * 2
    return 0

class TestClass:
    def method_one(self):
        for i in range(10):
            if i % 2:
                yield i

    def method_two(self, data):
        try:
            result = []
            for item in data:
                if item:
                    result.append(process(item))
            return result
        except Exception:
            return []
'''
        tree = ast.parse(code)
        results = self.analyzer.analyze_file_complexity(tree)

        # Verify structure
        self.assertIn('functions', results)
        self.assertIn('classes', results)
        self.assertIn('file_summary', results)

        # Should find 4 functions (2 standalone + 2 methods)
        self.assertEqual(len(results['functions']), 4)
        self.assertEqual(len(results['classes']), 1)

        # Verify summary statistics
        summary = results['file_summary']
        self.assertEqual(summary['total_functions'], 4)
        self.assertGreater(summary['average_cyclomatic'], 0)
        self.assertGreaterEqual(summary['average_cognitive'], 0)

        # Check that class information is captured
        test_class = results['classes'][0]
        self.assertEqual(test_class['class_name'], 'TestClass')
        self.assertEqual(test_class['method_count'], 2)

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Empty function
        code = '''
def empty_func():
    pass
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        analysis = self.analyzer.analyze_function_complexity(func_node)
        self.assertEqual(analysis['cyclomatic_complexity'], 1)
        self.assertEqual(analysis['cognitive_complexity'], 0)

    def test_real_world_example(self):
        """Test with a realistic function example."""
        code = '''
def process_user_data(users, filters=None):
    """Process user data with optional filters."""
    if not users:
        return []

    if filters is None:
        filters = {}

    processed = []
    for user in users:
        # Skip inactive users
        if not user.get('active', True):
            continue

        # Apply age filter
        if 'min_age' in filters and user.get('age', 0) < filters['min_age']:
            continue

        if 'max_age' in filters and user.get('age', 100) > filters['max_age']:
            continue

        # Apply role filter
        user_roles = user.get('roles', [])
        if 'required_roles' in filters:
            if not any(role in user_roles for role in filters['required_roles']):
                continue

        # Process the user
        processed_user = {
            'id': user['id'],
            'name': user.get('name', 'Unknown'),
            'email': user.get('email', '').lower(),
            'roles': user_roles
        }

        # Add computed fields
        if user.get('birth_date'):
            try:
                processed_user['age_computed'] = calculate_age(user['birth_date'])
            except ValueError:
                processed_user['age_computed'] = None

        processed.append(processed_user)

    return processed
'''
        tree = ast.parse(code)
        func_node = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef))

        analysis = self.analyzer.analyze_function_complexity(func_node)

        # This is a moderately complex function
        self.assertGreater(analysis['cyclomatic_complexity'], 5)
        self.assertGreater(analysis['cognitive_complexity'], 3)
        self.assertGreater(analysis['max_nesting_level'], 1)

        # Should suggest consideration for refactoring
        rating = analysis['complexity_rating']
        self.assertTrue('Moderate' in rating or 'High' in rating)


if __name__ == '__main__':
    unittest.main()