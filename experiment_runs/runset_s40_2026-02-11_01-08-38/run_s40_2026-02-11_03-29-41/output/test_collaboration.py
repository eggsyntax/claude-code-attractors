#!/usr/bin/env python3
"""
Test script to demonstrate Dave & Tara's collaborative analysis
This intentionally contains various code quality issues to showcase the analyzer
"""

import os
import sys
import json
from typing import List, Dict, Any


def overly_complex_function(data, threshold, mode, options, debug=False):
    """This function intentionally has high complexity to test the analyzer."""
    result = []

    if mode == "advanced":
        if threshold > 10:
            if debug:
                print("Debug mode active")
                if len(data) > 100:
                    for item in data:
                        if isinstance(item, dict):
                            if "value" in item:
                                if item["value"] > threshold:
                                    if options.get("strict", False):
                                        if item["value"] > threshold * 2:
                                            result.append(item)
                                        else:
                                            result.append({"modified": item})
                                    else:
                                        result.append(item)
        elif threshold > 5:
            for item in data:
                if item > threshold:
                    result.append(item)
    elif mode == "simple":
        result = [x for x in data if x > threshold]
    else:
        raise ValueError("Invalid mode")

    return result


def function_without_docstring(x, y):
    return x + y


def very_long_function_that_does_too_many_things():
    # This function is intentionally long to trigger code smell detection
    data = []

    # First, let's read some data
    try:
        with open("nonexistent.txt", "r") as f:
            content = f.read()
    except:
        content = "default"

    # Process the data in multiple ways
    for i in range(100):
        if i % 2 == 0:
            data.append(i * 2)
        else:
            data.append(i + 1)

    # More processing
    result = []
    for item in data:
        if item > 50:
            result.append(item)

    # Even more processing
    final_result = []
    for r in result:
        if r % 3 == 0:
            final_result.append(r)

    # And some more...
    processed = []
    for f in final_result:
        processed.append(f * 1.5)

    return processed


class PoorlyDesignedClass:
    def method1(self):
        pass

    def method2(self):
        pass

    def method3(self):
        pass


def main():
    """Test the collaborative analyzer on this file itself."""
    from codebase_analyzer import CollaborativeCodeAnalyzer

    print("🧪 Testing Dave & Tara's collaborative analyzer")
    print("Analyzing this test file that contains intentional code smells...")

    analyzer = CollaborativeCodeAnalyzer()
    results = analyzer.analyze(".")  # Analyze current directory

    print("\n📊 Results Summary:")
    print(f"Structural files found: {len(results['structural_analysis']['files'])}")
    print(f"Quality issues detected: {results['quality_analysis']['overall_quality']['total_smells']}")

    # Show some specific findings
    print("\n🔍 Sample Quality Issues Found:")
    for file_analysis in results['quality_analysis']['files']:
        if 'test_collaboration.py' in file_analysis['file_info']['path']:
            for smell in file_analysis['code_smells'][:3]:  # Show first 3
                print(f"  ⚠️  {smell['type']}: {smell['message']}")

    print(f"\n💡 Collaborative Insights:")
    for insight in results['insights']:
        print(f"  {insight}")


if __name__ == "__main__":
    main()