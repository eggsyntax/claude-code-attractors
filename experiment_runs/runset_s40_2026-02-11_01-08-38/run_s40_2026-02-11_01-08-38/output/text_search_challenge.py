#!/usr/bin/env python3
"""
Text Search Challenge
====================

Challenge: Design an efficient text search system

The challenge is to implement a function that can efficiently find all occurrences
of a pattern string within a larger text string.

Requirements:
- Function signature: find_pattern(text: str, pattern: str) -> List[int]
- Return list of starting indices where pattern is found
- Handle edge cases (empty strings, pattern longer than text, etc.)
- Optimize for performance with large texts

Created by: Tara & Dave
"""

from typing import List
from challenge_framework import Challenge, generate_random_text, generate_random_pattern


class TextSearchChallenge(Challenge):
    """Text search implementation challenge"""

    def __init__(self):
        super().__init__(
            name="Efficient Text Search",
            description="Find all occurrences of a pattern string within a text string"
        )

        # Add some basic test cases
        self.add_test_case("hello world", "world", expected=[6])
        self.add_test_case("abcabcabc", "abc", expected=[0, 3, 6])
        self.add_test_case("abcdefg", "xyz", expected=[])
        self.add_test_case("", "test", expected=[])
        self.add_test_case("test", "", expected=[])
        self.add_test_case("aaaa", "aa", expected=[0, 1, 2])
        self.add_test_case("mississippi", "issi", expected=[1, 4])

    def generate_test_data(self, size: int = 5000) -> tuple:
        """Generate test data for performance testing"""
        text = generate_random_text(size)
        pattern = generate_random_pattern(3, 8)

        # Inject pattern a few times to ensure some matches
        for i in range(0, len(text), len(text) // 5):
            if i + len(pattern) < len(text):
                text = text[:i] + pattern + text[i + len(pattern):]

        return (text, pattern)


def tara_naive_search(text: str, pattern: str) -> List[int]:
    """
    Tara's implementation: Simple naive string matching

    This is a straightforward approach that checks every possible position
    in the text to see if the pattern matches starting there.

    Time complexity: O(nm) where n is text length, m is pattern length
    Space complexity: O(1) for the algorithm, O(k) for results where k is number of matches
    """
    if not pattern or not text or len(pattern) > len(text):
        return []

    matches = []
    text_len = len(text)
    pattern_len = len(pattern)

    for i in range(text_len - pattern_len + 1):
        # Check if pattern matches at position i
        match = True
        for j in range(pattern_len):
            if text[i + j] != pattern[j]:
                match = False
                break

        if match:
            matches.append(i)

    return matches


def tara_python_builtin(text: str, pattern: str) -> List[int]:
    """
    Tara's implementation: Using Python's built-in string methods

    This leverages Python's optimized C implementation of string search.
    It's likely to be faster than our manual implementations for most cases.
    """
    if not pattern or not text:
        return []

    matches = []
    start = 0

    while True:
        pos = text.find(pattern, start)
        if pos == -1:
            break
        matches.append(pos)
        start = pos + 1  # Move past this match to find overlapping matches

    return matches


def dave_kmp_search(text: str, pattern: str) -> List[int]:
    """
    Dave's implementation: Knuth-Morris-Pratt (KMP) algorithm

    KMP uses a preprocessing step to build a "failure function" that helps
    us avoid redundant comparisons when a mismatch occurs.

    Time complexity: O(n + m) where n is text length, m is pattern length
    Space complexity: O(m) for the failure function
    """
    if not pattern or not text or len(pattern) > len(text):
        return []

    # Build the failure function (also called "partial match table")
    def build_failure_function(pattern: str) -> List[int]:
        failure = [0] * len(pattern)
        j = 0  # length of previous longest prefix suffix

        for i in range(1, len(pattern)):
            while j > 0 and pattern[i] != pattern[j]:
                j = failure[j - 1]

            if pattern[i] == pattern[j]:
                j += 1
            failure[i] = j

        return failure

    failure = build_failure_function(pattern)
    matches = []

    i = 0  # index for text
    j = 0  # index for pattern

    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == len(pattern):
            matches.append(i - j)
            j = failure[j - 1]  # Get next position from failure function
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = failure[j - 1]  # Use failure function to skip characters
            else:
                i += 1

    return matches


def dave_boyer_moore(text: str, pattern: str) -> List[int]:
    """
    Dave's implementation: Boyer-Moore algorithm (simplified)

    Boyer-Moore uses a "bad character" heuristic to skip characters when
    a mismatch occurs, potentially making large jumps through the text.

    Time complexity: O(nm) worst case, O(n/m) average case
    Space complexity: O(σ) where σ is alphabet size
    """
    if not pattern or not text or len(pattern) > len(text):
        return []

    # Build bad character table
    def build_bad_char_table(pattern: str) -> dict:
        table = {}
        for i, char in enumerate(pattern):
            table[char] = i
        return table

    bad_char = build_bad_char_table(pattern)
    matches = []
    n, m = len(text), len(pattern)
    i = 0  # index for text

    while i <= n - m:
        j = m - 1  # start from end of pattern

        # Compare pattern and text from right to left
        while j >= 0 and pattern[j] == text[i + j]:
            j -= 1

        if j < 0:
            # Pattern found
            matches.append(i)
            # Move to next position (simplified, not using good suffix rule)
            i += 1
        else:
            # Mismatch occurred, use bad character rule
            bad_char_skip = j - bad_char.get(text[i + j], -1)
            i += max(1, bad_char_skip)

    return matches


if __name__ == "__main__":
    # Initialize the challenge
    challenge = TextSearchChallenge()

    # Add Tara's solutions
    challenge.add_solution("Tara_Naive", tara_naive_search)
    challenge.add_solution("Tara_Builtin", tara_python_builtin)

    # Add Dave's solutions
    challenge.add_solution("Dave_KMP", dave_kmp_search)
    challenge.add_solution("Dave_BoyerMoore", dave_boyer_moore)

    print("🎯 Text Search Challenge Complete!")
    print("📊 Solutions implemented:")
    print("  • Tara: Naive search, Python built-in")
    print("  • Dave: KMP algorithm, Boyer-Moore algorithm")
    print("\n🚀 Ready to compare all implementations!")

    # Run the comparison automatically
    challenge.compare_solutions()