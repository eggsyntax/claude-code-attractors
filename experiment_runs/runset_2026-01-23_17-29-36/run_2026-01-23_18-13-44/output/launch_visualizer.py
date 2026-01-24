#!/usr/bin/env python3
"""
Launch Script for Code Analysis Visualization Tool
A collaborative creation by Alice & Bob

This script demonstrates our complete collaborative code analysis system
by launching the web server and providing easy access to the visualization interface.
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if required files are present."""
    current_dir = Path(__file__).parent
    required_files = [
        'web_interface.html',
        'visualization_server.py'
    ]

    missing_files = []
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False

    print("✅ All required files found!")
    return True


def check_analyzers():
    """Check if our analyzer files are available."""
    current_dir = Path(__file__).parent
    analyzer_files = ['ast_analyzer.py', 'complexity_analyzer.py']

    available_analyzers = []
    for file in analyzer_files:
        if (current_dir / file).exists():
            available_analyzers.append(file)

    if available_analyzers:
        print(f"🔍 Found analyzers: {', '.join(available_analyzers)}")
    else:
        print("⚠️  No analyzer files found - will use fallback mode")

    return len(available_analyzers) > 0


def create_demo_code():
    """Create a sample Python file for demonstration."""
    demo_code = '''#!/usr/bin/env python3
"""
Demo Python Code for Analysis
This file demonstrates various complexity patterns for our analyzer.
"""

import os
import sys
from typing import List, Dict, Optional
import asyncio


class ComplexityDemo:
    """A demonstration class showing different complexity levels."""

    def __init__(self, name: str, debug: bool = False):
        """Initialize the demo with configuration."""
        self.name = name
        self.debug = debug
        self.data = {}

    def simple_function(self, x: int) -> int:
        """A simple function with low complexity."""
        return x * 2

    def moderate_complexity(self, items: List[str]) -> Dict[str, int]:
        """Function with moderate complexity."""
        result = {}
        for item in items:
            if item.startswith('A'):
                result[item] = len(item) * 2
            elif item.startswith('B'):
                result[item] = len(item) * 3
            else:
                result[item] = len(item)
        return result

    def high_complexity_function(self, data: List[Dict], filters: Dict) -> List[Dict]:
        """Function with high cyclomatic complexity."""
        results = []

        for item in data:
            valid = True

            # Multiple nested conditions increase complexity
            if 'status' in filters:
                if item.get('status') != filters['status']:
                    if not filters.get('include_inactive', False):
                        valid = False
                    elif item.get('status') == 'pending':
                        if not filters.get('include_pending', True):
                            valid = False

            if valid and 'category' in filters:
                if isinstance(filters['category'], list):
                    if item.get('category') not in filters['category']:
                        valid = False
                else:
                    if item.get('category') != filters['category']:
                        valid = False

            if valid and 'min_score' in filters:
                score = item.get('score', 0)
                if score < filters['min_score']:
                    if not item.get('priority') == 'high':
                        valid = False
                    elif score < filters['min_score'] * 0.8:
                        valid = False

            if valid:
                # More complex processing
                processed_item = item.copy()

                try:
                    if item.get('needs_processing'):
                        if item.get('type') == 'special':
                            processed_item['value'] = item['raw_value'] * 1.5
                        elif item.get('type') == 'normal':
                            processed_item['value'] = item['raw_value'] * 1.0
                        else:
                            processed_item['value'] = item.get('raw_value', 0) * 0.8

                    results.append(processed_item)

                except (KeyError, TypeError, ValueError) as e:
                    if self.debug:
                        print(f"Processing error for {item}: {e}")
                    continue

        return results

    async def async_function(self, delay: float = 1.0) -> str:
        """An async function to test async detection."""
        await asyncio.sleep(delay)
        return f"Processed {self.name} after {delay}s"


def standalone_function(numbers: List[int]) -> Optional[float]:
    """Standalone function with error handling."""
    if not numbers:
        return None

    try:
        total = sum(numbers)
        average = total / len(numbers)
        return round(average, 2)
    except (TypeError, ZeroDivisionError):
        return None


# Function with decorators
@staticmethod
def utility_function(text: str) -> str:
    """Utility function with decorator."""
    return text.upper().strip()


if __name__ == "__main__":
    # Demo usage
    demo = ComplexityDemo("Test Demo", debug=True)

    print("Simple function result:", demo.simple_function(5))

    items = ["Apple", "Banana", "Cherry", "Date"]
    print("Moderate complexity result:", demo.moderate_complexity(items))

    # This would demonstrate high complexity analysis
    sample_data = [
        {"status": "active", "category": "A", "score": 85, "raw_value": 100},
        {"status": "pending", "category": "B", "score": 60, "raw_value": 80}
    ]
    filters = {"status": "active", "min_score": 70}
    complex_result = demo.high_complexity_function(sample_data, filters)
    print(f"Complex analysis processed {len(complex_result)} items")
'''

    demo_path = Path(__file__).parent / 'demo_complexity_code.py'
    with open(demo_path, 'w', encoding='utf-8') as f:
        f.write(demo_code)

    print(f"📝 Created demo file: {demo_path.name}")
    return demo_path


def main():
    """Main launcher function."""
    print("🚀 Code Analysis Visualization Tool Launcher")
    print("=" * 50)
    print("👥 A collaborative creation by Alice & Bob")
    print("🔍 Analyzing Python code with beautiful visualizations")
    print()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check analyzers
    has_analyzers = check_analyzers()

    # Create demo file
    demo_path = create_demo_code()

    print()
    print("🌐 Starting the web server...")

    try:
        # Start the server
        import visualization_server

        print("📖 Usage Instructions:")
        print("1. The web interface will open automatically")
        print("2. Upload Python files (.py) for analysis")
        print("3. View interactive charts and complexity metrics")
        print(f"4. Try analyzing the demo file: {demo_path.name}")
        print()

        if not has_analyzers:
            print("⚠️  Note: Running in fallback mode (basic analysis only)")
            print("   For full analysis, ensure ast_analyzer.py and complexity_analyzer.py are present")
            print()

        # Wait a moment then open browser
        print("🔗 Opening web interface in 3 seconds...")
        print("   (Press Ctrl+C to stop the server)")
        print()

        # Start server in a way that allows opening browser
        import threading
        import time

        def open_browser():
            time.sleep(3)
            try:
                webbrowser.open('http://localhost:8080')
                print("🌐 Web interface opened in your default browser!")
            except Exception as e:
                print(f"Could not open browser automatically: {e}")
                print("Please manually visit: http://localhost:8080")

        # Start browser opening in background
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # Start the server (this will block until Ctrl+C)
        visualization_server.run_server(port=8080, host='localhost')

    except KeyboardInterrupt:
        print("\n🛑 Server stopped. Thanks for using our collaborative tool!")
    except ImportError as e:
        print(f"❌ Could not import visualization server: {e}")
        print("Make sure visualization_server.py is in the same directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()