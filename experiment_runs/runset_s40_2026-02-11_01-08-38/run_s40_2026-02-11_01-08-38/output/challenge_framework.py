#!/usr/bin/env python3
"""
Collaborative Coding Challenge Framework
========================================

A framework for Dave and Tara to pose challenges, implement solutions,
and compare different approaches with performance analysis.

Created by: Tara & Dave
Date: 2026-02-11
"""

import time
import random
import string
from typing import List, Callable, Dict, Any, Tuple
from abc import ABC, abstractmethod


class Challenge(ABC):
    """Base class for coding challenges"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.solutions: Dict[str, Callable] = {}
        self.test_cases: List[Tuple] = []

    def add_solution(self, author: str, solution: Callable) -> None:
        """Add a solution implementation"""
        self.solutions[author] = solution

    def add_test_case(self, *args, expected=None) -> None:
        """Add a test case for the challenge"""
        self.test_cases.append((args, expected))

    @abstractmethod
    def generate_test_data(self, size: int = 1000) -> Any:
        """Generate test data for performance analysis"""
        pass

    def run_tests(self) -> Dict[str, bool]:
        """Run all test cases against all solutions"""
        results = {}
        for author, solution in self.solutions.items():
            results[author] = []
            for test_args, expected in self.test_cases:
                try:
                    result = solution(*test_args)
                    if expected is not None:
                        results[author].append(result == expected)
                    else:
                        results[author].append(True)  # Assume correct if no expected result
                except Exception as e:
                    print(f"Error in {author}'s solution: {e}")
                    results[author].append(False)
        return results

    def benchmark_solutions(self, test_data: Any, iterations: int = 1000) -> Dict[str, float]:
        """Benchmark all solutions with given test data"""
        results = {}
        for author, solution in self.solutions.items():
            start_time = time.perf_counter()
            for _ in range(iterations):
                try:
                    solution(*test_data)
                except Exception as e:
                    print(f"Benchmark error in {author}'s solution: {e}")
                    results[author] = float('inf')
                    break
            else:
                end_time = time.perf_counter()
                results[author] = (end_time - start_time) / iterations
        return results

    def compare_solutions(self) -> None:
        """Run comprehensive comparison of all solutions"""
        print(f"\n🎯 Challenge: {self.name}")
        print(f"📝 Description: {self.description}")
        print("=" * 60)

        # Run correctness tests
        print("\n🧪 Correctness Tests:")
        test_results = self.run_tests()
        for author, results in test_results.items():
            passed = sum(results)
            total = len(results)
            print(f"  {author}: {passed}/{total} tests passed")

        # Run performance benchmarks
        print("\n⚡ Performance Benchmarks:")
        test_data = self.generate_test_data()
        benchmark_results = self.benchmark_solutions(test_data)

        # Sort by performance
        sorted_results = sorted(benchmark_results.items(), key=lambda x: x[1])
        for i, (author, avg_time) in enumerate(sorted_results):
            if avg_time == float('inf'):
                print(f"  {i+1}. {author}: FAILED")
            else:
                print(f"  {i+1}. {author}: {avg_time*1000:.4f} ms per operation")

        print("\n" + "=" * 60)


def generate_random_text(length: int) -> str:
    """Utility function to generate random text for testing"""
    return ''.join(random.choices(string.ascii_lowercase + ' ', k=length))


def generate_random_pattern(min_length: int = 3, max_length: int = 10) -> str:
    """Utility function to generate random search patterns"""
    length = random.randint(min_length, max_length)
    return ''.join(random.choices(string.ascii_lowercase, k=length))


if __name__ == "__main__":
    print("Collaborative Coding Challenge Framework initialized!")
    print("Ready for Dave and Tara to start implementing solutions! 🚀")