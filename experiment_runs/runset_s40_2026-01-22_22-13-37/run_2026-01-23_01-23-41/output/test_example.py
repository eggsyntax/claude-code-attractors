#!/usr/bin/env python3
"""
Test example for demonstrating our code analyzer on Python code.
This file intentionally includes various complexity patterns.
"""

import os
import sys
from typing import List, Dict, Optional, Union
import asyncio
import json


class DataProcessor:
    """A class with various methods to test complexity analysis"""

    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.processed_items = []
        self.cache = {}

    def simple_method(self, value: int) -> int:
        """A simple method with low complexity"""
        return value * 2

    def complex_conditional_method(self, data: List[Dict], threshold: float,
                                  filters: List[str], options: Dict,
                                  enable_caching: bool = True) -> List[Dict]:
        """
        A method with high cyclomatic complexity to test our analyzer
        """
        results = []

        if not data:
            return results

        for item in data:
            # Multiple nested conditions create complexity
            if item.get('status') == 'active':
                if item.get('priority') == 'high':
                    if 'urgent' in filters:
                        if item.get('score', 0) > threshold:
                            if enable_caching and item['id'] not in self.cache:
                                # Process high priority urgent items
                                processed_item = self._process_urgent_item(item)
                                if processed_item:
                                    if options.get('validate', True):
                                        if self._validate_item(processed_item):
                                            results.append(processed_item)
                                            if enable_caching:
                                                self.cache[item['id']] = processed_item
                            elif not options.get('strict_validation', False):
                                results.append(processed_item)
                elif item.get('priority') == 'medium':
                    if 'standard' in filters:
                        processed_item = self._process_standard_item(item)
                        if processed_item and processed_item.get('quality_score', 0) > 0.7:
                            results.append(processed_item)
                else:
                    # Low priority processing
                    if item.get('auto_process', False):
                        results.append(item)
            elif item.get('status') == 'pending':
                if item.get('retry_count', 0) < 3:
                    # Retry logic
                    item['retry_count'] = item.get('retry_count', 0) + 1
                    results.append(item)

        # Post-processing with more conditions
        if options.get('sort_results', True):
            results.sort(key=lambda x: x.get('priority_score', 0), reverse=True)

        if options.get('limit_results'):
            limit = options.get('max_results', 100)
            results = results[:limit]

        return results

    def _process_urgent_item(self, item: Dict) -> Optional[Dict]:
        """Helper method for urgent item processing"""
        try:
            # Simulate complex processing
            item['processed_at'] = 'now'
            item['urgency_boost'] = 1.5
            return item
        except Exception as e:
            print(f"Error processing urgent item: {e}")
            return None

    def _process_standard_item(self, item: Dict) -> Optional[Dict]:
        """Helper method for standard item processing"""
        item['processed_at'] = 'now'
        item['standard_processing'] = True
        return item

    def _validate_item(self, item: Dict) -> bool:
        """Item validation with multiple checks"""
        if not item:
            return False

        required_fields = ['id', 'status', 'priority']
        for field in required_fields:
            if field not in item:
                return False

        if item.get('priority') not in ['high', 'medium', 'low']:
            return False

        return True

    async def async_batch_processor(self, items: List[Dict],
                                  batch_size: int = 10) -> List[Dict]:
        """Async method to demonstrate async function detection"""
        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await self._process_batch_async(batch)
            results.extend(batch_results)

        return results

    async def _process_batch_async(self, batch: List[Dict]) -> List[Dict]:
        """Process a batch of items asynchronously"""
        # Simulate async processing
        await asyncio.sleep(0.1)
        return [item for item in batch if item.get('valid', True)]


def standalone_complex_function(data, mode='standard', **kwargs):
    """
    A standalone function with high parameter count and complexity
    to test function-level analysis
    """
    if mode == 'fast':
        return [item for item in data if item]
    elif mode == 'thorough':
        results = []
        for item in data:
            if isinstance(item, dict):
                if item.get('enabled', True):
                    if 'process' in kwargs and kwargs['process']:
                        # Nested processing logic
                        if item.get('priority', 0) > kwargs.get('min_priority', 0):
                            processed = {**item}
                            processed['processed'] = True
                            results.append(processed)
                    else:
                        results.append(item)
            elif isinstance(item, (list, tuple)):
                # Handle sequence types
                flattened = [sub_item for sub_item in item if sub_item]
                results.extend(flattened)
        return results
    else:
        # Default processing
        return data


# Module-level function with import dependencies
def analyze_file_structure(directory_path: str) -> Dict[str, Union[int, List[str]]]:
    """
    Function that uses multiple imports and has moderate complexity
    """
    if not os.path.exists(directory_path):
        return {'error': 'Directory not found'}

    file_types = {}
    total_files = 0

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            total_files += 1
            ext = os.path.splitext(file)[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1

    return {
        'total_files': total_files,
        'file_types': file_types,
        'directories_scanned': len(list(os.walk(directory_path)))
    }


if __name__ == "__main__":
    # Test data for demonstration
    test_data = [
        {'id': 1, 'status': 'active', 'priority': 'high', 'score': 95},
        {'id': 2, 'status': 'active', 'priority': 'medium', 'score': 75},
        {'id': 3, 'status': 'pending', 'retry_count': 1},
    ]

    processor = DataProcessor({'mode': 'production'})
    filters = ['urgent', 'standard']
    options = {'validate': True, 'sort_results': True}

    results = processor.complex_conditional_method(test_data, 80.0, filters, options)
    print(f"Processed {len(results)} items")
    print(json.dumps(results, indent=2))