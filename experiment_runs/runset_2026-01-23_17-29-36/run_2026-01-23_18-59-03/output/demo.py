#!/usr/bin/env python3
"""
Collaborative Code Analyzer - Integrated Demo
Demonstrates the collaborative capabilities of Alice & Bob's code analysis tool.

This script showcases:
- Bob's robust parsing and analysis engine
- Alice's interactive visualization capabilities
- Our combined approach to modular, testable software design

Created by: Alice & Bob (Claude Code Collaboration)
"""

import logging
import tempfile
from pathlib import Path
from textwrap import dedent

from code_analyzer import analyze_codebase, CodeParser
from visualizer import CodeVisualizer, visualize_codebase

# Configure logging for demo
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_sample_codebase() -> Path:
    """
    Create a sample Python codebase for demonstration purposes.

    Returns:
        Path to the created sample codebase directory
    """
    logger.info("Creating sample codebase for demonstration...")

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="demo_codebase_"))

    # Sample Python files with varying complexity
    sample_files = {
        "main.py": dedent('''
            """Main application module with moderate complexity."""
            import os
            import sys
            from pathlib import Path
            from typing import List, Optional, Dict
            import json
            import logging

            logger = logging.getLogger(__name__)

            class ConfigManager:
                """Handles application configuration."""

                def __init__(self, config_path: str):
                    self.config_path = Path(config_path)
                    self.config = {}

                def load_config(self) -> Dict:
                    """Load configuration from file."""
                    if not self.config_path.exists():
                        logger.warning(f"Config file not found: {self.config_path}")
                        return {}

                    try:
                        with open(self.config_path) as f:
                            self.config = json.load(f)
                        return self.config
                    except Exception as e:
                        logger.error(f"Error loading config: {e}")
                        return {}

                def save_config(self, config: Dict) -> bool:
                    """Save configuration to file."""
                    try:
                        with open(self.config_path, 'w') as f:
                            json.dump(config, f, indent=2)
                        self.config = config
                        return True
                    except Exception as e:
                        logger.error(f"Error saving config: {e}")
                        return False

            def process_files(directory: str, pattern: str = "*.py") -> List[str]:
                """Process files in directory matching pattern."""
                results = []
                base_path = Path(directory)

                if not base_path.exists():
                    raise ValueError(f"Directory does not exist: {directory}")

                for file_path in base_path.rglob(pattern):
                    if file_path.is_file():
                        try:
                            with open(file_path) as f:
                                content = f.read()

                            if len(content.strip()) > 0:
                                results.append(str(file_path))
                                logger.debug(f"Processed: {file_path}")
                        except Exception as e:
                            logger.warning(f"Could not process {file_path}: {e}")

                return results

            def main():
                """Main application entry point."""
                if len(sys.argv) < 2:
                    print("Usage: python main.py <directory>")
                    sys.exit(1)

                directory = sys.argv[1]
                config_manager = ConfigManager("config.json")
                config = config_manager.load_config()

                try:
                    files = process_files(directory)
                    print(f"Found {len(files)} Python files")

                    for file_path in files:
                        print(f"  {file_path}")

                except Exception as e:
                    logger.error(f"Application error: {e}")
                    sys.exit(1)

            if __name__ == "__main__":
                main()
        ''').strip(),

        "utils.py": dedent('''
            """Utility functions with low complexity."""
            import math
            import re
            from typing import Union, List

            def calculate_entropy(text: str) -> float:
                """Calculate Shannon entropy of text."""
                if not text:
                    return 0.0

                # Count character frequencies
                char_counts = {}
                for char in text:
                    char_counts[char] = char_counts.get(char, 0) + 1

                # Calculate entropy
                entropy = 0.0
                text_len = len(text)

                for count in char_counts.values():
                    probability = count / text_len
                    if probability > 0:
                        entropy -= probability * math.log2(probability)

                return entropy

            def clean_string(text: str) -> str:
                """Clean and normalize text string."""
                # Remove extra whitespace
                text = re.sub(r'\s+', ' ', text.strip())

                # Remove special characters
                text = re.sub(r'[^\w\s-]', '', text)

                return text.lower()

            def chunk_list(lst: List, chunk_size: int) -> List[List]:
                """Split list into chunks of specified size."""
                return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

            def safe_divide(a: Union[int, float], b: Union[int, float]) -> float:
                """Safely divide two numbers."""
                if b == 0:
                    return float('inf')
                return a / b
        ''').strip(),

        "data_processor.py": dedent('''
            """Data processing module with high complexity."""
            import csv
            import json
            import xml.etree.ElementTree as ET
            from pathlib import Path
            from typing import Any, Dict, List, Optional, Union
            from dataclasses import dataclass
            from enum import Enum

            class DataFormat(Enum):
                """Supported data formats."""
                JSON = "json"
                CSV = "csv"
                XML = "xml"
                TEXT = "txt"

            @dataclass
            class ProcessingResult:
                """Result of data processing operation."""
                success: bool
                data: Optional[Any]
                error_message: Optional[str]
                records_processed: int

            class DataProcessor:
                """Advanced data processing with multiple format support."""

                def __init__(self, validate_data: bool = True):
                    self.validate_data = validate_data
                    self.supported_formats = [f.value for f in DataFormat]

                def detect_format(self, file_path: Union[str, Path]) -> Optional[DataFormat]:
                    """Auto-detect data format from file extension."""
                    file_path = Path(file_path)
                    suffix = file_path.suffix.lower()

                    format_map = {
                        '.json': DataFormat.JSON,
                        '.csv': DataFormat.CSV,
                        '.xml': DataFormat.XML,
                        '.txt': DataFormat.TEXT
                    }

                    return format_map.get(suffix)

                def process_json(self, file_path: Path) -> ProcessingResult:
                    """Process JSON data file."""
                    try:
                        with open(file_path) as f:
                            data = json.load(f)

                        if self.validate_data:
                            if not isinstance(data, (dict, list)):
                                return ProcessingResult(False, None, "Invalid JSON structure", 0)

                        record_count = len(data) if isinstance(data, list) else 1
                        return ProcessingResult(True, data, None, record_count)

                    except json.JSONDecodeError as e:
                        return ProcessingResult(False, None, f"JSON parse error: {e}", 0)
                    except Exception as e:
                        return ProcessingResult(False, None, f"Unexpected error: {e}", 0)

                def process_csv(self, file_path: Path) -> ProcessingResult:
                    """Process CSV data file."""
                    try:
                        data = []
                        with open(file_path, newline='') as f:
                            # Try to detect delimiter
                            sample = f.read(1024)
                            f.seek(0)

                            delimiter = ','
                            if ';' in sample and sample.count(';') > sample.count(','):
                                delimiter = ';'
                            elif '\t' in sample:
                                delimiter = '\t'

                            reader = csv.DictReader(f, delimiter=delimiter)

                            for row_num, row in enumerate(reader):
                                if self.validate_data:
                                    # Basic validation - check for empty rows
                                    if not any(row.values()):
                                        continue

                                data.append(row)

                        return ProcessingResult(True, data, None, len(data))

                    except Exception as e:
                        return ProcessingResult(False, None, f"CSV processing error: {e}", 0)

                def process_xml(self, file_path: Path) -> ProcessingResult:
                    """Process XML data file."""
                    try:
                        tree = ET.parse(file_path)
                        root = tree.getroot()

                        # Convert XML to dict-like structure
                        def xml_to_dict(element):
                            result = {}

                            # Add attributes
                            if element.attrib:
                                result.update(element.attrib)

                            # Add text content
                            if element.text and element.text.strip():
                                if len(element) == 0:  # Leaf node
                                    return element.text.strip()
                                else:
                                    result['_text'] = element.text.strip()

                            # Add child elements
                            for child in element:
                                child_data = xml_to_dict(child)

                                if child.tag in result:
                                    # Handle multiple children with same tag
                                    if not isinstance(result[child.tag], list):
                                        result[child.tag] = [result[child.tag]]
                                    result[child.tag].append(child_data)
                                else:
                                    result[child.tag] = child_data

                            return result

                        data = xml_to_dict(root)

                        # Count records (rough estimate)
                        def count_records(obj):
                            if isinstance(obj, list):
                                return sum(count_records(item) for item in obj)
                            elif isinstance(obj, dict):
                                return max(1, sum(count_records(v) for v in obj.values()))
                            else:
                                return 1

                        record_count = count_records(data)

                        return ProcessingResult(True, data, None, record_count)

                    except ET.ParseError as e:
                        return ProcessingResult(False, None, f"XML parse error: {e}", 0)
                    except Exception as e:
                        return ProcessingResult(False, None, f"XML processing error: {e}", 0)

                def process_file(self, file_path: Union[str, Path]) -> ProcessingResult:
                    """Process file based on detected or specified format."""
                    file_path = Path(file_path)

                    if not file_path.exists():
                        return ProcessingResult(False, None, f"File not found: {file_path}", 0)

                    data_format = self.detect_format(file_path)

                    if data_format == DataFormat.JSON:
                        return self.process_json(file_path)
                    elif data_format == DataFormat.CSV:
                        return self.process_csv(file_path)
                    elif data_format == DataFormat.XML:
                        return self.process_xml(file_path)
                    elif data_format == DataFormat.TEXT:
                        # Simple text processing
                        try:
                            with open(file_path) as f:
                                data = f.read()
                            return ProcessingResult(True, data, None, 1)
                        except Exception as e:
                            return ProcessingResult(False, None, f"Text processing error: {e}", 0)
                    else:
                        return ProcessingResult(False, None, f"Unsupported format: {file_path.suffix}", 0)

            def batch_process(directory: Union[str, Path], processor: DataProcessor) -> List[ProcessingResult]:
                """Batch process all supported files in directory."""
                directory = Path(directory)
                results = []

                for file_path in directory.rglob("*"):
                    if file_path.is_file() and processor.detect_format(file_path):
                        result = processor.process_file(file_path)
                        results.append(result)

                return results
        ''').strip(),

        "tests/test_utils.py": dedent('''
            """Tests for utility functions."""
            import unittest
            from utils import calculate_entropy, clean_string, chunk_list, safe_divide

            class TestUtils(unittest.TestCase):
                """Test cases for utility functions."""

                def test_calculate_entropy_empty_string(self):
                    """Test entropy calculation for empty string."""
                    self.assertEqual(calculate_entropy(""), 0.0)

                def test_calculate_entropy_single_char(self):
                    """Test entropy calculation for single character."""
                    self.assertEqual(calculate_entropy("aaaa"), 0.0)

                def test_calculate_entropy_mixed(self):
                    """Test entropy calculation for mixed characters."""
                    entropy = calculate_entropy("abcd")
                    self.assertEqual(entropy, 2.0)  # log2(4) = 2

                def test_clean_string_basic(self):
                    """Test basic string cleaning."""
                    result = clean_string("  Hello   World!  ")
                    self.assertEqual(result, "hello world")

                def test_clean_string_special_chars(self):
                    """Test string cleaning with special characters."""
                    result = clean_string("Test@#$%String")
                    self.assertEqual(result, "teststring")

                def test_chunk_list_basic(self):
                    """Test basic list chunking."""
                    result = chunk_list([1, 2, 3, 4, 5], 2)
                    expected = [[1, 2], [3, 4], [5]]
                    self.assertEqual(result, expected)

                def test_chunk_list_empty(self):
                    """Test chunking empty list."""
                    result = chunk_list([], 3)
                    self.assertEqual(result, [])

                def test_safe_divide_normal(self):
                    """Test normal division."""
                    self.assertEqual(safe_divide(10, 2), 5.0)

                def test_safe_divide_by_zero(self):
                    """Test division by zero."""
                    self.assertEqual(safe_divide(10, 0), float('inf'))

            if __name__ == "__main__":
                unittest.main()
        ''').strip()
    }

    # Create the files
    for filename, content in sample_files.items():
        file_path = temp_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    logger.info(f"Created sample codebase at: {temp_dir}")
    logger.info(f"Files created: {list(sample_files.keys())}")

    return temp_dir


def demonstrate_analysis_workflow(codebase_path: Path) -> None:
    """
    Demonstrate the complete analysis workflow.

    Args:
        codebase_path: Path to the codebase to analyze
    """
    logger.info("=" * 60)
    logger.info("DEMONSTRATING BOB'S ANALYSIS ENGINE")
    logger.info("=" * 60)

    # Step 1: Use Bob's analyzer directly
    logger.info("Step 1: Running comprehensive code analysis...")
    metrics_list = analyze_codebase(codebase_path)

    logger.info(f"Analysis complete! Found {len(metrics_list)} Python files.")

    # Display summary statistics
    total_loc = sum(m.lines_of_code for m in metrics_list)
    total_functions = sum(m.function_count for m in metrics_list)
    total_classes = sum(m.class_count for m in metrics_list)
    avg_complexity = sum(m.complexity for m in metrics_list) / len(metrics_list)

    print(f"\n📊 CODEBASE SUMMARY:")
    print(f"   Files analyzed: {len(metrics_list)}")
    print(f"   Total lines of code: {total_loc:,}")
    print(f"   Total functions: {total_functions}")
    print(f"   Total classes: {total_classes}")
    print(f"   Average complexity: {avg_complexity:.2f}")

    # Step 2: Show detailed metrics for each file
    print(f"\n📁 FILE-BY-FILE ANALYSIS:")
    for metrics in metrics_list:
        filename = Path(metrics.file_path).name
        print(f"   {filename}:")
        print(f"     Lines: {metrics.lines_of_code}, Complexity: {metrics.complexity}")
        print(f"     Functions: {metrics.function_count}, Classes: {metrics.class_count}")
        if metrics.dependencies:
            deps = ', '.join(metrics.dependencies[:3])  # Show first 3
            if len(metrics.dependencies) > 3:
                deps += f" (and {len(metrics.dependencies) - 3} more)"
            print(f"     Dependencies: {deps}")
        print()

    logger.info("=" * 60)
    logger.info("DEMONSTRATING ALICE'S VISUALIZATION ENGINE")
    logger.info("=" * 60)

    # Step 3: Use Alice's visualizer
    logger.info("Step 3: Creating interactive visualizations...")

    try:
        # Create HTML dashboard
        dashboard_path = visualize_codebase(codebase_path, "html")
        if dashboard_path:
            logger.info(f"✅ Interactive dashboard created: {dashboard_path}")

        # Export to JSON
        json_path = visualize_codebase(codebase_path, "json")
        if json_path:
            logger.info(f"✅ JSON export created: {json_path}")

        # Export to CSV
        csv_path = visualize_codebase(codebase_path, "csv")
        if csv_path:
            logger.info(f"✅ CSV export created: {csv_path}")

    except ImportError as e:
        logger.warning(f"Visualization skipped - missing dependencies: {e}")
        logger.info("To enable visualizations, install: pip install plotly pandas")

    logger.info("=" * 60)
    logger.info("COLLABORATION DEMONSTRATION COMPLETE")
    logger.info("=" * 60)


def demonstrate_individual_components() -> None:
    """Demonstrate individual component capabilities."""
    logger.info("\n🔧 COMPONENT DEMONSTRATION:")

    # Demonstrate Bob's parser on a simple code snippet
    logger.info("\nTesting Bob's parser on a code snippet...")

    sample_code = dedent('''
        def fibonacci(n):
            """Calculate fibonacci sequence."""
            if n <= 1:
                return n
            else:
                return fibonacci(n-1) + fibonacci(n-2)

        class Calculator:
            def add(self, a, b):
                return a + b
    ''').strip()

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(sample_code)
        temp_path = Path(f.name)

    try:
        parser = CodeParser()
        tree = parser.parse_file(temp_path)
        if tree:
            metrics = parser.extract_metrics(tree, str(temp_path))
            print(f"   ✅ Parsed successfully!")
            print(f"   Functions found: {metrics.functions}")
            print(f"   Classes found: {metrics.classes}")
            print(f"   Complexity: {metrics.complexity}")
    finally:
        temp_path.unlink()  # Clean up

    # Demonstrate Alice's visualizer features
    logger.info("\nTesting Alice's visualization capabilities...")
    try:
        visualizer = CodeVisualizer()
        print(f"   ✅ Visualizer initialized with theme: {visualizer.theme}")
        print(f"   Supports: HTML dashboards, JSON/CSV export, interactive charts")
    except ImportError:
        print(f"   ⚠️  Visualizer requires plotly and pandas")


def main():
    """Main demonstration function."""
    print("🤖 COLLABORATIVE CODE ANALYZER DEMONSTRATION")
    print("Created by: Alice & Bob (Claude Code Collaboration)")
    print("=" * 60)

    # Create sample codebase
    codebase_path = create_sample_codebase()

    try:
        # Run comprehensive demonstration
        demonstrate_analysis_workflow(codebase_path)

        # Show individual component capabilities
        demonstrate_individual_components()

        print(f"\n🎉 DEMONSTRATION COMPLETE!")
        print(f"Sample codebase available at: {codebase_path}")
        print(f"Generated files are in: /tmp/cc-exp/run_2026-01-23_18-59-03/output/")

    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise


if __name__ == "__main__":
    main()