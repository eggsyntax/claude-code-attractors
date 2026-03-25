#!/usr/bin/env python3
"""
Collaborative Codebase Analyzer
A tool demonstrating AI-collaborative development by Dave and Tara

Usage: python codebase_collaboration_analyzer.py <project_path>
"""

import sys
import json
from pathlib import Path
import argparse

# Import our collaborative components
from codebase_analyzer import CodebaseAnalyzer
from collaboration_patterns import PatternDetector

class CollaborationCLI:
    """Unified interface for our collaborative analysis system"""

    def analyze_project(self, project_path: str, output_file: str = None):
        """Complete analysis pipeline"""
        print(f"🔍 Analyzing codebase: {project_path}")

        # Dave's component: Extract raw data
        print("📊 Extracting code structure...")
        analyzer = CodebaseAnalyzer(project_path)
        analyzer.discover_files()
        analyzer.parse_entities()

        # Convert to analysis format
        analysis = {
            'files': {path: file_info.to_dict() for path, file_info in analyzer.files.items()},
            'entities': {path: [entity.to_dict() for entity in entities]
                        for path, entities in analyzer.entities.items()}
        }

        # Tara's component: Detect patterns
        print("🧠 Detecting collaboration patterns...")
        detector = PatternDetector(analysis)
        pattern_list = detector.detect_all_patterns()

        # Format patterns for report
        patterns = self._format_patterns(pattern_list)

        # Generate comprehensive report
        report = self._generate_report(analysis, patterns)

        if output_file:
            self._save_report(report, output_file)
            print(f"💾 Report saved to: {output_file}")
        else:
            self._print_report(report)

        return report

    def _format_patterns(self, pattern_list):
        """Convert pattern list to dictionary format for reporting"""
        patterns_by_type = {}
        for pattern in pattern_list:
            pattern_type = pattern.pattern_type
            if pattern_type not in patterns_by_type:
                patterns_by_type[pattern_type] = []

            patterns_by_type[pattern_type].append({
                'description': pattern.description,
                'confidence': pattern.confidence,
                'files': list(pattern.files),
                'metadata': pattern.metadata
            })

        return patterns_by_type

    def _generate_report(self, analysis, patterns):
        """Combine analysis and patterns into comprehensive report"""
        return {
            "metadata": {
                "total_files": len(analysis["files"]),
                "total_entities": sum(len(entities) for entities in analysis["entities"].values()),
                "analyzer": "Dave's CodebaseAnalyzer",
                "detector": "Tara's PatternDetector"
            },
            "codebase_structure": analysis,
            "collaboration_patterns": patterns,
            "recommendations": self._generate_recommendations(patterns)
        }

    def _generate_recommendations(self, patterns):
        """Generate actionable collaboration recommendations"""
        recommendations = []

        # High-confidence temporal clusters suggest team coordination needs
        high_temporal = [p for p in patterns.get("temporal_clusters", [])
                        if p["confidence"] > 0.7]
        if high_temporal:
            recommendations.append({
                "type": "team_coordination",
                "priority": "high",
                "description": f"Found {len(high_temporal)} file groups that are frequently modified together. Consider assigning these to coordinated development teams."
            })

        # Integration points suggest architecture review needs
        integration_points = patterns.get("integration_points", [])
        if integration_points:
            recommendations.append({
                "type": "architecture_review",
                "priority": "medium",
                "description": f"Found {len(integration_points)} critical integration points. These files may benefit from architectural review to manage complexity."
            })

        return recommendations

    def _print_report(self, report):
        """Pretty print the analysis report"""
        print("\n" + "="*60)
        print("📋 COLLABORATION ANALYSIS REPORT")
        print("="*60)

        meta = report["metadata"]
        print(f"📁 Files analyzed: {meta['total_files']}")
        print(f"🔧 Code entities: {meta['total_entities']}")

        patterns = report["collaboration_patterns"]
        print(f"\n🎯 DETECTED PATTERNS:")

        for pattern_type, pattern_list in patterns.items():
            if pattern_list:
                print(f"\n  {pattern_type.replace('_', ' ').title()}: {len(pattern_list)} found")
                # Show highest confidence example
                if pattern_list:
                    best = max(pattern_list, key=lambda x: x["confidence"])
                    print(f"    Best match: {best['description']} (confidence: {best['confidence']:.2f})")

        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. [{rec['priority'].upper()}] {rec['description']}")

    def _save_report(self, report, filepath):
        """Save comprehensive report to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Analyze codebase for collaboration patterns")
    parser.add_argument("project_path", nargs='?', help="Path to the project to analyze")
    parser.add_argument("-o", "--output", help="Output file for detailed JSON report")
    parser.add_argument("--demo", action="store_true", help="Run on demo codebase")

    args = parser.parse_args()

    cli = CollaborationCLI()

    if args.demo:
        # Create a demo project structure for testing
        demo_path = "/tmp/demo_project"
        create_demo_project(demo_path)
        args.project_path = demo_path
    elif not args.project_path:
        parser.error("project_path is required when not using --demo")

    try:
        cli.analyze_project(args.project_path, args.output)
    except Exception as e:
        print(f"❌ Error analyzing project: {e}")
        return 1

    return 0

def create_demo_project(path):
    """Create a small demo project to test our analyzer"""
    Path(path).mkdir(exist_ok=True)

    # Create some interconnected Python files
    files = {
        "main.py": '''
from utils.database import connect_db
from api.handlers import UserHandler
from models.user import User

def main():
    db = connect_db()
    handler = UserHandler(db)
    user = User("test@example.com")
    return handler.create_user(user)
''',
        "utils/__init__.py": "",
        "utils/database.py": '''
import sqlite3

def connect_db():
    return sqlite3.connect("app.db")

class DatabaseManager:
    def __init__(self, connection):
        self.conn = connection
''',
        "api/__init__.py": "",
        "api/handlers.py": '''
from models.user import User
from utils.database import DatabaseManager

class UserHandler:
    def __init__(self, db):
        self.db = DatabaseManager(db)

    def create_user(self, user):
        # Implementation here
        pass
''',
        "models/__init__.py": "",
        "models/user.py": '''
class User:
    def __init__(self, email):
        self.email = email
        self.id = None

    def validate(self):
        return "@" in self.email
'''
    }

    for filepath, content in files.items():
        full_path = Path(path) / filepath
        full_path.parent.mkdir(exist_ok=True)
        full_path.write_text(content)

if __name__ == "__main__":
    sys.exit(main())