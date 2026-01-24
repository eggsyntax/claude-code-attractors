#!/usr/bin/env python3
"""
Example code to demonstrate CodeInsight analysis capabilities.
This file intentionally contains various patterns and complexity levels.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import json


class DataProcessor(ABC):
    """Abstract base class for data processors."""

    @abstractmethod
    def process(self, data: List[Dict]) -> Dict:
        pass


class JSONDataProcessor(DataProcessor):
    """Concrete implementation for JSON data processing."""

    def __init__(self):
        self.processed_count = 0

    def process(self, data: List[Dict]) -> Dict:
        """Process JSON data with validation and transformation."""
        result = {"processed": [], "errors": []}

        for item in data:
            try:
                if self._validate_item(item):
                    processed_item = self._transform_item(item)
                    result["processed"].append(processed_item)
                    self.processed_count += 1
                else:
                    result["errors"].append(f"Invalid item: {item}")
            except Exception as e:
                result["errors"].append(f"Processing error: {str(e)}")

        return result

    def _validate_item(self, item: Dict) -> bool:
        """Validate individual data item."""
        required_fields = ["id", "name", "type"]
        return all(field in item for field in required_fields)

    def _transform_item(self, item: Dict) -> Dict:
        """Transform individual data item."""
        return {
            "id": item["id"],
            "name": item["name"].upper(),
            "type": item["type"],
            "timestamp": "2026-01-22",
            "processed": True
        }


def create_processor_factory(processor_type: str) -> Optional[DataProcessor]:
    """Factory function for creating data processors."""
    if processor_type == "json":
        return JSONDataProcessor()
    return None


class SingletonLogger:
    """Singleton pattern for logging."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logs = []
        return cls._instance

    def log(self, message: str):
        self.logs.append(message)


def complex_analysis_function(data, config, options, filters, transformers, validators):
    """
    A deliberately complex function with many parameters to trigger analysis warnings.
    This demonstrates how CodeInsight detects potential refactoring opportunities.
    """
    results = []

    for item in data:
        # Nested complexity
        if item.get("active"):
            for filter_func in filters:
                if filter_func(item):
                    for transformer in transformers:
                        transformed = transformer(item)
                        for validator in validators:
                            if validator(transformed):
                                if config.get("detailed_analysis"):
                                    # Even more nesting
                                    for option in options:
                                        if option.matches(transformed):
                                            results.append(transformed)
                                            break
                                else:
                                    results.append(transformed)
                                break
                        break
                    break

    return results


if __name__ == "__main__":
    # Example usage
    processor = create_processor_factory("json")
    logger = SingletonLogger()

    sample_data = [
        {"id": 1, "name": "test", "type": "demo"},
        {"id": 2, "name": "example", "type": "sample"}
    ]

    if processor:
        result = processor.process(sample_data)
        logger.log(f"Processed {len(result['processed'])} items")
        print(json.dumps(result, indent=2))