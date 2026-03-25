"""
Testing Framework for Evolutionary Code Garden
Provides automated testing and metrics for code variants.
"""

import time
import sys
import traceback
from typing import Dict, Any, List, Callable
import importlib.util


class CodeTester:
    """Framework for testing and measuring code variants."""

    def __init__(self):
        self.test_suite = []
        self.performance_tests = []

    def run_full_evaluation(self, code_file_path: str) -> Dict[str, Any]:
        """Run comprehensive evaluation on a code variant."""
        results = {
            "functionality": {},
            "performance": {},
            "metrics": {},
            "errors": []
        }

        try:
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location("variant", code_file_path)
            variant_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(variant_module)

            # Test functionality
            results["functionality"] = self._test_functionality(variant_module)

            # Test performance
            results["performance"] = self._test_performance(variant_module)

            # Calculate code metrics
            results["metrics"] = self._calculate_metrics(code_file_path)

        except Exception as e:
            results["errors"].append({
                "type": "execution_error",
                "message": str(e),
                "traceback": traceback.format_exc()
            })

        return results

    def _test_functionality(self, module) -> Dict[str, Any]:
        """Test basic functionality of the BST implementation."""
        test_results = {}

        try:
            # Get the BST class
            if hasattr(module, 'BinarySearchTree'):
                BST = module.BinarySearchTree
            else:
                return {"error": "BinarySearchTree class not found"}

            # Test 1: Basic insertion and search
            bst = BST()
            test_values = [5, 3, 7, 2, 4, 6, 8]
            for val in test_values:
                bst.insert(val)

            test_results["basic_insertion"] = True

            # Test 2: Search functionality
            search_tests = []
            for val in test_values:
                search_tests.append(bst.search(val))
            search_tests.append(not bst.search(99))  # Should be False

            test_results["search_accuracy"] = all(search_tests)

            # Test 3: Traversal (if available)
            if hasattr(bst, 'inorder_traversal'):
                traversal = bst.inorder_traversal()
                expected = sorted(test_values)
                test_results["inorder_traversal"] = traversal == expected
            else:
                test_results["inorder_traversal"] = "not_implemented"

            # Test 4: Empty tree handling
            empty_bst = BST()
            test_results["empty_tree_search"] = not empty_bst.search(5)

            # Test 5: Duplicate handling
            dup_bst = BST()
            dup_bst.insert(5)
            dup_bst.insert(5)  # Insert duplicate
            test_results["duplicate_handling"] = True  # No crash

        except Exception as e:
            test_results["error"] = str(e)

        return test_results

    def _test_performance(self, module) -> Dict[str, float]:
        """Measure performance characteristics."""
        performance = {}

        try:
            if not hasattr(module, 'BinarySearchTree'):
                return {"error": "BinarySearchTree class not found"}

            BST = module.BinarySearchTree

            # Test insertion performance
            bst = BST()
            start_time = time.time()
            for i in range(1000):
                bst.insert(i)
            insertion_time = time.time() - start_time
            performance["insertion_time_1000"] = insertion_time

            # Test search performance
            start_time = time.time()
            for i in range(0, 1000, 10):  # Search every 10th element
                bst.search(i)
            search_time = time.time() - start_time
            performance["search_time_100_queries"] = search_time

            # Test traversal performance (if available)
            if hasattr(bst, 'inorder_traversal'):
                start_time = time.time()
                bst.inorder_traversal()
                traversal_time = time.time() - start_time
                performance["traversal_time_1000"] = traversal_time

        except Exception as e:
            performance["error"] = str(e)

        return performance

    def _calculate_metrics(self, code_file_path: str) -> Dict[str, float]:
        """Calculate code quality metrics."""
        metrics = {}

        try:
            with open(code_file_path, 'r') as f:
                code = f.read()

            # Basic metrics
            lines = code.split('\n')
            metrics["total_lines"] = len(lines)
            metrics["non_empty_lines"] = len([line for line in lines if line.strip()])
            metrics["comment_lines"] = len([line for line in lines if line.strip().startswith('#')])

            # Complexity indicators
            metrics["method_count"] = code.count('def ')
            metrics["class_count"] = code.count('class ')
            metrics["cyclomatic_complexity_estimate"] = (
                code.count('if ') + code.count('elif ') + code.count('while ') +
                code.count('for ') + code.count('except ') + 1
            )

            # Style indicators
            metrics["docstring_coverage"] = code.count('"""') / max(1, metrics["method_count"])

        except Exception as e:
            metrics["error"] = str(e)

        return metrics


# Standalone testing function for easy use
def test_bst_variant(code_file_path: str) -> Dict[str, Any]:
    """Convenient function to test a BST code variant."""
    tester = CodeTester()
    return tester.run_full_evaluation(code_file_path)


if __name__ == "__main__":
    # Test the seed program
    import os
    seed_path = os.path.join(os.path.dirname(__file__), "seed_program.py")
    if os.path.exists(seed_path):
        results = test_bst_variant(seed_path)
        print("🧪 Testing seed program:")
        print(f"Functionality: {results['functionality']}")
        print(f"Performance: {results['performance']}")
        print(f"Metrics: {results['metrics']}")
    else:
        print("Seed program not found!")