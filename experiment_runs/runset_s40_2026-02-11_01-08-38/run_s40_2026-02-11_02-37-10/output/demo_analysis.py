#!/usr/bin/env python3
"""
Demonstration of the Collaborative Analysis Framework

This script shows how Dave and Tara's framework identifies intersecting
code issues across security, performance, and architectural domains.
"""

from collaborative_analyzer import (
    CollaborativeAnalysisEngine, SecurityAnalyzer, PerformanceAnalyzer,
    IssueCategory, IssueSeverity
)


def load_sample_code():
    """Load the sample code we've been analyzing"""
    return '''import sqlite3
import hashlib
import time
from datetime import datetime

class UserManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.session_counter = 0
        self.active_sessions = []

    def get_user_data(self, username, password):
        # SECURITY ISSUE: SQL injection vulnerability
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchone()

    def create_user(self, username, email, password):
        # SECURITY ISSUE: storing password in plain text
        user_data = {
            'username': username,
            'email': email,
            'password': password,  # Should be hashed!
            'created_at': datetime.now()
        }

        # Insert user (simplified)
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",
            (username, email, password, user_data['created_at'])
        )
        self.connection.commit()

    def cleanup_sessions(self, max_age_hours=24):
        # PERFORMANCE ISSUE: inefficient loop
        current_time = time.time()
        sessions_to_remove = []

        for session in self.active_sessions:
            if (current_time - session['created_at']) > (max_age_hours * 3600):
                sessions_to_remove.append(session)

        # Remove expired sessions
        for session in sessions_to_remove:
            self.active_sessions.remove(session)

    def process_file(self, filename):
        # MAINTAINABILITY ISSUE: no error handling
        with open(filename, 'r') as f:
            data = f.read()

        processed_data = data.upper()
        return processed_data

    def generate_session_id(self):
        # SECURITY ISSUE: predictable session IDs
        self.session_counter += 1
        return f"session_{self.session_counter}"'''


def format_analysis_results(results):
    """Format the analysis results in a readable way"""
    print("\\n" + "="*60)
    print("COLLABORATIVE CODE ANALYSIS RESULTS")
    print("="*60)

    print(f"\\nOVERVIEW:")
    print(f"  Total Issues Found: {results['total_issues']}")
    print(f"  Issue Intersections: {results['intersection_count']}")
    print(f"  Critical Intersections: {len(results['critical_intersections'])}")

    print(f"\\nISSUES BY CATEGORY:")
    for category, count in results['issues_by_category'].items():
        print(f"  {category.title()}: {count}")

    print(f"\\nANALYZER CONTRIBUTIONS:")
    for agent_id, contrib in results['analyzer_contributions'].items():
        print(f"  {agent_id}:")
        print(f"    Issues found: {contrib['total_issues']}")
        print(f"    Categories: {', '.join(contrib['categories'])}")
        print(f"    Avg confidence: {contrib['confidence_avg']:.2f}")

    print(f"\\nDETAILED ISSUES:")
    print("-" * 40)

    for issue in results['all_issues']:
        print(f"\\n[{issue.severity.value.upper()}] {issue.title}")
        print(f"  Category: {issue.category.value}")
        print(f"  Line {issue.line_number}: {issue.code_snippet}")
        print(f"  Issue: {issue.description}")
        print(f"  Fix: {issue.suggested_fix}")
        print(f"  Found by: {issue.analyzer_id}")
        print(f"  Confidence: {issue.confidence:.2f}")

        if issue.related_issues:
            print(f"  Related to: {', '.join(issue.related_issues)}")
        if issue.amplifies_issues:
            print(f"  Amplifies: {', '.join(issue.amplifies_issues)}")
        if issue.amplified_by_issues:
            print(f"  Amplified by: {', '.join(issue.amplified_by_issues)}")

    print(f"\\nCRITICAL INTERSECTIONS:")
    print("-" * 40)

    for intersection in results['critical_intersections']:
        print(f"\\n⚠️  {intersection['impact']}")
        print(f"   Primary issue: {intersection['primary_issue']}")
        print(f"   Amplifies: {', '.join(intersection['amplifies'])}")

    print(f"\\n" + "="*60)
    print("COLLABORATIVE INSIGHTS")
    print("="*60)

    print(f"\\n🤝 WHAT DAVE & TARA DISCOVERED TOGETHER:")
    print("• Security vulnerabilities often stem from architectural problems")
    print("• Performance issues and security issues can amplify each other")
    print("• Different analytical perspectives find different but related problems")
    print("• The intersection points are where the highest-impact fixes lie")

    print(f"\\n🔍 CROSS-DOMAIN PATTERN DETECTION:")
    security_count = results['issues_by_category'].get('security', 0)
    performance_count = results['issues_by_category'].get('performance', 0)
    architecture_count = results['issues_by_category'].get('architecture', 0)

    if security_count > 0 and performance_count > 0:
        print("• Found both security AND performance issues - refactoring needed")
    if architecture_count > 0:
        print("• Architectural issues found - likely enabling other problem types")
    if results['intersection_count'] > results['total_issues'] * 0.3:
        print("• High intersection rate - issues are interconnected, systematic approach needed")


def main():
    """Demonstrate the collaborative analysis framework"""
    print("Loading collaborative analysis framework...")

    # Create the analysis engine
    engine = CollaborativeAnalysisEngine()

    # Add our specialized analyzers (representing Dave and Tara's perspectives)
    print("Adding SecurityAnalyzer (Tara's perspective)...")
    engine.add_analyzer(SecurityAnalyzer())

    print("Adding PerformanceAnalyzer (Dave's perspective)...")
    engine.add_analyzer(PerformanceAnalyzer())

    # Load and analyze the sample code
    print("\\nAnalyzing sample code...")
    sample_code = load_sample_code()
    results = engine.analyze_code(sample_code, "sample_user_manager.py")

    # Display results
    format_analysis_results(results)

    print(f"\\n🎯 NEXT STEPS FOR DAVE & TARA:")
    print("1. Extend framework with more specialized analyzers")
    print("2. Add support for cross-file analysis")
    print("3. Implement automated refactoring suggestions")
    print("4. Create visualizations of issue intersections")
    print("5. Add machine learning to improve intersection detection")


if __name__ == "__main__":
    main()