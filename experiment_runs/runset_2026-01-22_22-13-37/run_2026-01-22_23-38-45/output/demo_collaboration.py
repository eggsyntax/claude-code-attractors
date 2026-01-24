#!/usr/bin/env python3
"""
CodeMentor Collaborative Demo
============================

A demonstration of Bob and Alice's collaborative CodeMentor system.
This script showcases the integration of:
- Alice's sophisticated code analysis engine
- Bob's real-time collaboration features
- Educational pattern detection and explanation
- Quality improvement suggestions

Usage:
    python demo_collaboration.py

Authors:
- Alice: Analysis engine and pattern detection
- Bob: Collaboration framework and integration
"""

from analysis_engine import CodeAnalysisEngine
import json
from datetime import datetime

class CollaborationDemo:
    """Demonstrates the collaborative features of CodeMentor"""

    def __init__(self):
        self.engine = CodeAnalysisEngine()
        self.session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def analyze_collaborative_patterns(self, code_samples):
        """Analyze multiple code samples and show collaboration insights"""

        print("🚀 CodeMentor Collaborative Analysis Demo")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Collaborators: Alice (Analysis) & Bob (Integration)")
        print("=" * 60)
        print()

        for i, (name, code) in enumerate(code_samples.items(), 1):
            print(f"📁 Analyzing: {name}")
            print("-" * 40)

            # Perform analysis using Alice's engine
            result = self.engine.analyze_file(name, code)

            # Display results
            patterns = result['patterns']
            issues = result['quality_issues']

            print(f"🎨 Patterns Found: {len(patterns)}")
            for pattern in patterns:
                print(f"   • {pattern.pattern_type.value.title()}")
                print(f"     Confidence: {pattern.confidence:.1%}")
                print(f"     Educational: {pattern.educational_context[:80]}...")

            print(f"\n⚠️  Quality Issues: {len(issues)}")
            for issue in issues:
                print(f"   • {issue.severity.value.upper()}: {issue.category}")
                print(f"     {issue.description}")
                print(f"     💡 {issue.suggestion}")

            print(f"\n📊 Code Metrics:")
            metrics = result['metrics']
            print(f"   • Lines of Code: {metrics.get('lines_of_code', 'N/A')}")
            print(f"   • Complexity: {metrics.get('cyclomatic_complexity', 'N/A')}")
            print(f"   • Functions: {metrics.get('function_count', 'N/A')}")

            if i < len(code_samples):
                print("\n" + "="*60 + "\n")

        print("✨ Collaborative Analysis Complete!")
        print("\n💡 This demonstrates how Alice's analysis engine")
        print("   integrates seamlessly with Bob's collaboration framework")
        print("   to provide comprehensive code review assistance.")

def main():
    """Run the collaborative demo"""

    # Sample code files for analysis
    code_samples = {
        "singleton_example.py": '''
class ConfigManager:
    """Configuration manager using Singleton pattern"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.config = {}
            self._initialized = True

    def get_config(self, key):
        return self.config.get(key)

    def set_config(self, key, value):
        self.config[key] = value
''',

        "observer_pattern.py": '''
class Newsletter:
    """Newsletter using Observer pattern"""

    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    def notify_subscribers(self, content):
        for subscriber in self.subscribers:
            subscriber.receive_update(content)

class EmailSubscriber:
    def __init__(self, email):
        self.email = email

    def receive_update(self, content):
        print(f"Sending email to {self.email}: {content}")

class SMSSubscriber:
    def __init__(self, phone):
        self.phone = phone

    def receive_update(self, content):
        print(f"Sending SMS to {self.phone}: {content}")
''',

        "factory_with_issues.py": '''
import os
import json

class ReportFactory:
    """Factory with some quality issues for demonstration"""

    @staticmethod
    def create_report(report_type, data):
        # No input validation (quality issue)
        if report_type == "pdf":
            return PDFReport(data)
        elif report_type == "excel":
            return ExcelReport(data)
        elif report_type == "json":
            return JSONReport(data)
        # Missing else case (quality issue)

class PDFReport:
    def __init__(self, data):
        self.data = data

    def generate(self):
        # Potential security issue - no validation
        filename = f"/tmp/{os.getenv('USER', 'user')}_report.pdf"
        # Simulate PDF generation
        return filename

class ExcelReport:
    def __init__(self, data):
        self.data = data

    def generate(self):
        # Performance issue - loading all data in memory
        all_data = []
        for item in self.data:
            processed_item = self.expensive_processing(item)
            all_data.append(processed_item)
        return all_data

    def expensive_processing(self, item):
        # Simulated expensive operation
        return str(item).upper() * 100

class JSONReport:
    def __init__(self, data):
        self.data = data

    def generate(self):
        return json.dumps(self.data, indent=2)
'''
    }

    # Run the demo
    demo = CollaborationDemo()
    demo.analyze_collaborative_patterns(code_samples)

if __name__ == "__main__":
    main()