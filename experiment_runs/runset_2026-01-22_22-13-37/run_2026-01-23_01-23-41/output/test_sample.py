#!/usr/bin/env python3
"""
Sample Python file for testing the code analyzer
"""

import os
import sys
from typing import List, Dict


class SampleClass:
    """A sample class to test analysis"""

    def __init__(self, name: str):
        self.name = name

    def process_data(self, data: List[int]) -> Dict[str, int]:
        """Process some data with complexity"""
        result = {}

        for item in data:
            if item > 10:
                if item % 2 == 0:
                    result['even_large'] = result.get('even_large', 0) + 1
                else:
                    result['odd_large'] = result.get('odd_large', 0) + 1
            elif item > 0:
                result['small'] = result.get('small', 0) + 1
            else:
                result['negative'] = result.get('negative', 0) + 1

        return result


def fibonacci(n: int) -> int:
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


async def fetch_data(url: str) -> str:
    """Async function to test detection"""
    # This would normally fetch data
    return f"Data from {url}"


def main():
    """Main function"""
    sample = SampleClass("test")
    data = [1, 5, 10, 15, 20, -3]
    result = sample.process_data(data)
    print(f"Analysis result: {result}")

    # Test fibonacci
    fib_result = fibonacci(5)
    print(f"Fibonacci(5) = {fib_result}")


if __name__ == "__main__":
    main()