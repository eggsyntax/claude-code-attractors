#!/usr/bin/env python3
"""
Example usage of the Intelligent Code Reviewer

This demonstrates how to use the code reviewer both as a library
and as a command-line tool.
"""

from intelligent_code_reviewer import IntelligentCodeReviewer, format_review


def demonstrate_library_usage():
    """Show how to use the reviewer as a library."""

    # Some code with various issues
    problematic_code = '''
def calculate_stats(data):
    results = []
    f = open("results.txt", "w")

    for i in range(len(data)):
        try:
            value = eval(data[i])
            if value > 50:
                if value < 500:
                    results.append(value * 1.5)
        except:
            pass

    f.write(str(results))
    return results

def process_df(df):
    # Process some dataframe
    return df.head(25)
    '''

    print("🔍 Analyzing Code as Library")
    print("=" * 40)

    reviewer = IntelligentCodeReviewer()
    issues = reviewer.review_code(problematic_code, "problematic_example.py")

    print(format_review(issues, "problematic_example.py"))


def demonstrate_good_practices():
    """Show what the improved code might look like."""

    improved_code = '''
import json
from typing import List, Optional

MULTIPLIER = 1.5
UPPER_THRESHOLD = 500
LOWER_THRESHOLD = 50
MAX_PREVIEW_ROWS = 25

def calculate_stats(data_strings: List[str]) -> List[float]:
    """Calculate statistics from string data, applying thresholds and multiplier."""
    results = []

    with open("results.txt", "w") as output_file:
        for data_string in data_strings:
            try:
                value = json.loads(data_string)  # Safer than eval
                processed_value = _process_value(value)
                if processed_value is not None:
                    results.append(processed_value)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Warning: Could not parse '{data_string}': {e}")

        output_file.write(str(results))

    return results

def _process_value(value: float) -> Optional[float]:
    """Process a single value with threshold checks."""
    if LOWER_THRESHOLD < value < UPPER_THRESHOLD:
        return value * MULTIPLIER
    return None

def process_sales_data(sales_dataframe):
    """Process sales dataframe and return preview."""
    return sales_dataframe.head(MAX_PREVIEW_ROWS)
    '''

    print("\n\n✨ Improved Version")
    print("=" * 40)

    reviewer = IntelligentCodeReviewer()
    issues = reviewer.review_code(improved_code, "improved_example.py")

    print(format_review(issues, "improved_example.py"))


if __name__ == "__main__":
    print("📋 Intelligent Code Reviewer - Usage Examples\n")

    demonstrate_library_usage()
    demonstrate_good_practices()

    print("\n" + "=" * 60)
    print("💡 Command Line Usage:")
    print("  python intelligent_code_reviewer.py --demo")
    print("  python intelligent_code_reviewer.py your_file.py")
    print("=" * 60)