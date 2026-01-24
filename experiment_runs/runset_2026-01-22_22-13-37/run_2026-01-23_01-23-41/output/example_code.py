#!/usr/bin/env python3
"""
Example Python code for testing our analyzers.
Contains various patterns and complexity scenarios.
"""

import os
import sys
from typing import List, Dict, Optional
import json
import re


class DataProcessor:
    """Example class with various complexity patterns."""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path) if config_path else {}
        self.cache = {}
        self.processed_count = 0

    def _load_config(self, path: str) -> Dict:
        """Load configuration from file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print("Invalid JSON in config file")
            return {}

    def process_data(self, data: List[Dict], filter_type: str = None,
                    sort_key: str = None, reverse: bool = False,
                    limit: Optional[int] = None, validate: bool = True,
                    transform_func: callable = None) -> List[Dict]:
        """
        Process data with multiple options - intentionally complex function
        to demonstrate high parameter count and complexity.
        """
        # TODO: This function is getting too complex
        if not data:
            return []

        # Validation step
        if validate:
            for item in data:
                if not isinstance(item, dict):
                    raise ValueError("All items must be dictionaries")
                if 'id' not in item:
                    raise ValueError("All items must have an 'id' field")

        # Filter step
        if filter_type:
            if filter_type == 'active':
                data = [item for item in data if item.get('status') == 'active']
            elif filter_type == 'recent':
                data = [item for item in data if item.get('timestamp', 0) > 1000000]
            elif filter_type == 'priority':
                data = [item for item in data if item.get('priority', 0) >= 5]
            else:
                raise ValueError(f"Unknown filter type: {filter_type}")

        # Transform step
        if transform_func:
            transformed_data = []
            for item in data:
                try:
                    transformed_item = transform_func(item)
                    if transformed_item:
                        transformed_data.append(transformed_item)
                except Exception as e:
                    print(f"Transform error for item {item.get('id', 'unknown')}: {e}")
                    continue
            data = transformed_data

        # Sort step
        if sort_key:
            try:
                data.sort(key=lambda x: x.get(sort_key, 0), reverse=reverse)
            except Exception as e:
                print(f"Sort error: {e}")
                return data

        # Limit step
        if limit and limit > 0:
            data = data[:limit]

        # Cache result
        cache_key = f"{filter_type}_{sort_key}_{reverse}_{limit}"
        self.cache[cache_key] = data

        self.processed_count += 1

        if self.processed_count > 100:
            print("Warning: Processing many requests")
            return data
        elif self.processed_count > 50:
            print("Processing moderate number of requests")
            return data
        else:
            return data

    def analyze_patterns(self, text: str) -> Dict[str, any]:
        """Analyze text patterns - example with deep nesting."""
        results = {
            'word_count': 0,
            'patterns': {},
            'stats': {}
        }

        words = text.split()
        results['word_count'] = len(words)

        # Deep nesting example
        for word in words:
            if len(word) > 3:
                if word.isalpha():
                    if word.lower() in ['error', 'warning', 'info']:
                        if 'log_levels' not in results['patterns']:
                            results['patterns']['log_levels'] = []
                        results['patterns']['log_levels'].append(word.lower())
                    elif word.lower().startswith('http'):
                        if 'urls' not in results['patterns']:
                            results['patterns']['urls'] = []
                        results['patterns']['urls'].append(word)
                    else:
                        if 'words' not in results['patterns']:
                            results['patterns']['words'] = {}
                        if word.lower() not in results['patterns']['words']:
                            results['patterns']['words'][word.lower()] = 0
                        results['patterns']['words'][word.lower()] += 1

        return results

    def x(self, a, b):  # Short function name
        """Short function name example."""
        return a + b

    def calculate_complex_metric(self, data_points, weights=None, normalization_factor=1.0):
        """Function with multiple return points."""
        if not data_points:
            return 0

        if len(data_points) == 1:
            return data_points[0] * normalization_factor

        if weights and len(weights) != len(data_points):
            print("Warning: weights length mismatch")
            return None

        total = 0
        for i, point in enumerate(data_points):
            if weights:
                total += point * weights[i]
            else:
                total += point

        if total == 0:
            return 0

        normalized = total * normalization_factor

        if normalized < 0:
            return 0

        return normalized


def risky_function(user_input: str):
    """Function with potential security issues."""
    # FIXME: This is dangerous!
    result = eval(user_input)  # Security issue: eval usage
    exec(f"print({result})")   # Another security issue
    return result


def process_file(filename):
    """Simple file processing function."""
    with open(filename, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    word_count = sum(len(line.split()) for line in lines)

    print(f"File: {filename}")
    print(f"Lines: {len(lines)}")
    print(f"Words: {word_count}")

    return {
        'filename': filename,
        'lines': len(lines),
        'words': word_count
    }


if __name__ == "__main__":
    # Example usage
    processor = DataProcessor()

    sample_data = [
        {'id': 1, 'name': 'Alice', 'status': 'active', 'priority': 8},
        {'id': 2, 'name': 'Bob', 'status': 'inactive', 'priority': 3},
        {'id': 3, 'name': 'Charlie', 'status': 'active', 'priority': 6},
    ]

    results = processor.process_data(
        sample_data,
        filter_type='active',
        sort_key='priority',
        reverse=True
    )

    print("Processed results:", results)