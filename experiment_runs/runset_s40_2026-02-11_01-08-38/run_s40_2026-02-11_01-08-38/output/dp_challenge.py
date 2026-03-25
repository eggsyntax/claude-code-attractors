"""
Dynamic Programming Challenge Framework
=====================================
A framework for comparing different dynamic programming approaches and optimizations.
"""

import time
import functools
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Callable


class DPChallenge(ABC):
    """Base class for dynamic programming challenges."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.solutions = {}
        self.test_cases = []

    def add_solution(self, name: str, function: Callable, description: str):
        """Add a solution to compare."""
        self.solutions[name] = {
            'function': function,
            'description': description
        }

    def add_test_case(self, inputs: Any, expected: Any, description: str = ""):
        """Add a test case."""
        self.test_cases.append({
            'inputs': inputs,
            'expected': expected,
            'description': description
        })

    def benchmark_solution(self, solution_name: str, iterations: int = 1000) -> float:
        """Benchmark a specific solution."""
        if solution_name not in self.solutions:
            raise ValueError(f"Solution '{solution_name}' not found")

        solution = self.solutions[solution_name]['function']
        total_time = 0.0

        for test_case in self.test_cases:
            # Warm up
            for _ in range(10):
                solution(*test_case['inputs'])

            # Actual timing
            start_time = time.perf_counter()
            for _ in range(iterations):
                solution(*test_case['inputs'])
            end_time = time.perf_counter()

            total_time += (end_time - start_time)

        return (total_time / (len(self.test_cases) * iterations)) * 1000  # Return in milliseconds

    def test_correctness(self):
        """Test all solutions for correctness."""
        results = {}
        for name, solution_data in self.solutions.items():
            solution = solution_data['function']
            passed = 0
            failed = 0

            for test_case in self.test_cases:
                try:
                    result = solution(*test_case['inputs'])
                    if result == test_case['expected']:
                        passed += 1
                    else:
                        failed += 1
                        print(f"❌ {name}: Expected {test_case['expected']}, got {result}")
                except Exception as e:
                    failed += 1
                    print(f"❌ {name}: Exception {e}")

            results[name] = {'passed': passed, 'failed': failed}

        return results

    def compare_solutions(self):
        """Compare all solutions."""
        print(f"\n🧠 {self.name}")
        print("=" * 50)
        print(f"{self.description}\n")

        # Test correctness first
        print("✅ Correctness Tests:")
        correctness = self.test_correctness()

        for name, result in correctness.items():
            status = "✅" if result['failed'] == 0 else "❌"
            print(f"{status} {name}: {result['passed']}/{result['passed'] + result['failed']} tests passed")
        print()

        # Only benchmark solutions that pass correctness tests
        valid_solutions = [name for name, result in correctness.items() if result['failed'] == 0]

        if not valid_solutions:
            print("❌ No solutions passed correctness tests!")
            return

        # Benchmark performance
        print("⚡ Performance Benchmarks:")
        performance = {}
        for name in valid_solutions:
            avg_time = self.benchmark_solution(name)
            performance[name] = avg_time
            description = self.solutions[name]['description']
            print(f"   {name}: {avg_time:.4f} ms - {description}")

        # Sort by performance
        sorted_performance = sorted(performance.items(), key=lambda x: x[1])

        print(f"\n🏆 Performance Ranking:")
        for i, (name, time_ms) in enumerate(sorted_performance, 1):
            print(f"{i}. {name}: {time_ms:.4f} ms")


class FibonacciChallenge(DPChallenge):
    """Classic Fibonacci sequence with different optimization approaches."""

    def __init__(self):
        super().__init__(
            "Fibonacci Sequence Optimization Challenge",
            "Compare different approaches to computing Fibonacci numbers: naive recursion, memoization, tabulation, and mathematical optimizations."
        )

        # Add test cases
        test_cases = [
            ((10,), 55, "Small Fibonacci"),
            ((20,), 6765, "Medium Fibonacci"),
            ((30,), 832040, "Large Fibonacci"),
            ((35,), 9227465, "Very Large Fibonacci")
        ]

        for inputs, expected, description in test_cases:
            self.add_test_case(inputs, expected, description)


class LongestCommonSubsequenceChallenge(DPChallenge):
    """Longest Common Subsequence with different DP optimizations."""

    def __init__(self):
        super().__init__(
            "Longest Common Subsequence Challenge",
            "Compare approaches for finding the length of the longest common subsequence between two strings."
        )

        # Add test cases
        test_cases = [
            (("ABCDGH", "AEDFHR"), 3, "Simple case - ADH"),
            (("AGGTAB", "GXTXAYB"), 4, "Medium case - GTAB"),
            (("PROGRAMMING", "ALGORITHM"), 3, "Complex case - GRI"),
            (("ABCDEFGHIJK", "ACDEFGHIJKLM"), 10, "Long strings - ACDEFGHIJK")
        ]

        for inputs, expected, description in test_cases:
            self.add_test_case(inputs, expected, description)


# Tara's Fibonacci Implementations
def tara_fibonacci_naive(n: int) -> int:
    """Naive recursive approach - exponential time complexity."""
    if n <= 1:
        return n
    return tara_fibonacci_naive(n - 1) + tara_fibonacci_naive(n - 2)


def tara_fibonacci_memoized(n: int) -> int:
    """Top-down approach with memoization."""
    @functools.lru_cache(maxsize=None)
    def fib_memo(k):
        if k <= 1:
            return k
        return fib_memo(k - 1) + fib_memo(k - 2)

    return fib_memo(n)


def tara_fibonacci_tabulation(n: int) -> int:
    """Bottom-up tabulation approach with O(1) space optimization."""
    if n <= 1:
        return n

    # Only keep track of the last two values
    prev2, prev1 = 0, 1

    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2, prev1 = prev1, current

    return prev1


# Dave's Fibonacci Implementations
def dave_fibonacci_matrix(n: int) -> int:
    """Matrix exponentiation approach - O(log n) time complexity."""
    if n <= 1:
        return n

    def matrix_multiply(A, B):
        """Multiply two 2x2 matrices."""
        return [
            [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]
        ]

    def matrix_power(matrix, power):
        """Fast matrix exponentiation using binary exponentiation."""
        if power == 1:
            return matrix

        if power % 2 == 0:
            half_power = matrix_power(matrix, power // 2)
            return matrix_multiply(half_power, half_power)
        else:
            return matrix_multiply(matrix, matrix_power(matrix, power - 1))

    # Fibonacci matrix: [[1, 1], [1, 0]]
    fib_matrix = [[1, 1], [1, 0]]
    result_matrix = matrix_power(fib_matrix, n)
    return result_matrix[0][1]


def dave_fibonacci_iterative(n: int) -> int:
    """Simple iterative approach without space optimization for comparison."""
    if n <= 1:
        return n

    # Keep full history for educational purposes
    fib_sequence = [0, 1]

    for i in range(2, n + 1):
        fib_sequence.append(fib_sequence[i - 1] + fib_sequence[i - 2])

    return fib_sequence[n]


def dave_fibonacci_golden_ratio(n: int) -> int:
    """Mathematical approach using golden ratio formula."""
    import math

    if n <= 1:
        return n

    # Binet's formula: F(n) = (phi^n - psi^n) / sqrt(5)
    # where phi = (1 + sqrt(5)) / 2 and psi = (1 - sqrt(5)) / 2
    phi = (1 + math.sqrt(5)) / 2
    psi = (1 - math.sqrt(5)) / 2

    result = (phi**n - psi**n) / math.sqrt(5)
    return round(result)


# Dave's LCS Implementations
def dave_lcs_classic_dp(text1: str, text2: str) -> int:
    """Classic DP table approach - full O(mn) space for comparison."""
    m, n = len(text1), len(text2)

    # Create full DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


def dave_lcs_recursive_optimized(text1: str, text2: str) -> int:
    """Recursive with manual memoization dictionary."""
    memo = {}

    def lcs_helper(i, j):
        if (i, j) in memo:
            return memo[(i, j)]

        if i == len(text1) or j == len(text2):
            result = 0
        elif text1[i] == text2[j]:
            result = 1 + lcs_helper(i + 1, j + 1)
        else:
            result = max(lcs_helper(i + 1, j), lcs_helper(i, j + 1))

        memo[(i, j)] = result
        return result

    return lcs_helper(0, 0)


# Dave's New Challenge: Edit Distance (Levenshtein Distance)
class EditDistanceChallenge(DPChallenge):
    """Edit distance challenge with different optimization strategies."""

    def __init__(self):
        super().__init__(
            "Edit Distance Challenge",
            "Compare approaches for computing minimum edit distance between two strings."
        )

        # Add test cases
        test_cases = [
            (("kitten", "sitting"), 3, "Classic example - 3 operations"),
            (("saturday", "sunday"), 3, "Medium complexity"),
            (("intention", "execution"), 5, "More complex transformation"),
            (("horse", "ros"), 3, "Deletion heavy example")
        ]

        for inputs, expected, description in test_cases:
            self.add_test_case(inputs, expected, description)


def dave_edit_distance_classic(str1: str, str2: str) -> int:
    """Classic edit distance with full DP table."""
    m, n = len(str1), len(str2)

    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i  # Delete all characters
    for j in range(n + 1):
        dp[0][j] = j  # Insert all characters

    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # No operation needed
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],     # Delete
                    dp[i][j - 1],     # Insert
                    dp[i - 1][j - 1]  # Replace
                )

    return dp[m][n]


def dave_edit_distance_optimized(str1: str, str2: str) -> int:
    """Space-optimized edit distance using only two rows."""
    m, n = len(str1), len(str2)

    # Use only two rows
    prev = list(range(n + 1))
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        curr[0] = i
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])

        prev, curr = curr, prev

    return prev[n]


# Tara's LCS Implementations
def tara_lcs_memoized(text1: str, text2: str) -> int:
    """Top-down memoized approach for LCS."""
    @functools.lru_cache(maxsize=None)
    def lcs_helper(i, j):
        if i == len(text1) or j == len(text2):
            return 0

        if text1[i] == text2[j]:
            return 1 + lcs_helper(i + 1, j + 1)
        else:
            return max(lcs_helper(i + 1, j), lcs_helper(i, j + 1))

    return lcs_helper(0, 0)


def tara_lcs_tabulation(text1: str, text2: str) -> int:
    """Bottom-up tabulation with space optimization."""
    m, n = len(text1), len(text2)

    # Use only two rows instead of full m x n matrix
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])

        # Swap the rows
        prev, curr = curr, prev

    return prev[n]


if __name__ == "__main__":
    print("🚀 Dynamic Programming Challenge Results - Dave & Tara Collaboration")
    print("=" * 75)

    # ============ FIBONACCI CHALLENGE ============
    fib_challenge = FibonacciChallenge()

    # Add Tara's solutions
    fib_challenge.add_solution("tara_naive", tara_fibonacci_naive, "Naive recursive (educational only)")
    fib_challenge.add_solution("tara_memoized", tara_fibonacci_memoized, "Top-down with @lru_cache")
    fib_challenge.add_solution("tara_tabulation", tara_fibonacci_tabulation, "Bottom-up with O(1) space")

    # Add Dave's solutions
    fib_challenge.add_solution("dave_matrix", dave_fibonacci_matrix, "Matrix exponentiation O(log n)")
    fib_challenge.add_solution("dave_iterative", dave_fibonacci_iterative, "Simple iterative with full history")
    fib_challenge.add_solution("dave_golden_ratio", dave_fibonacci_golden_ratio, "Mathematical Binet's formula")

    # Run Fibonacci challenge (exclude naive and golden ratio for performance testing)
    print("\nNote: Naive and golden ratio approaches excluded from performance testing")
    temp_solutions = fib_challenge.solutions.copy()

    # Remove slow/imprecise solutions for benchmarking
    if "tara_naive" in fib_challenge.solutions:
        del fib_challenge.solutions["tara_naive"]
    if "dave_golden_ratio" in fib_challenge.solutions:
        del fib_challenge.solutions["dave_golden_ratio"]  # Can have floating point precision issues

    fib_challenge.compare_solutions()

    # Restore for completeness
    fib_challenge.solutions = temp_solutions

    print("\n" + "="*75 + "\n")

    # ============ LCS CHALLENGE ============
    lcs_challenge = LongestCommonSubsequenceChallenge()

    # Add Tara's solutions
    lcs_challenge.add_solution("tara_lcs_memoized", tara_lcs_memoized, "Top-down memoization with @lru_cache")
    lcs_challenge.add_solution("tara_lcs_tabulation", tara_lcs_tabulation, "Bottom-up with space optimization")

    # Add Dave's solutions
    lcs_challenge.add_solution("dave_lcs_classic", dave_lcs_classic_dp, "Classic DP table O(mn) space")
    lcs_challenge.add_solution("dave_lcs_recursive", dave_lcs_recursive_optimized, "Recursive with manual memoization")

    lcs_challenge.compare_solutions()

    print("\n" + "="*75 + "\n")

    # ============ NEW: EDIT DISTANCE CHALLENGE ============
    edit_challenge = EditDistanceChallenge()

    # Add Dave's edit distance solutions
    edit_challenge.add_solution("dave_edit_classic", dave_edit_distance_classic, "Classic DP table approach")
    edit_challenge.add_solution("dave_edit_optimized", dave_edit_distance_optimized, "Space-optimized two-row approach")

    edit_challenge.compare_solutions()