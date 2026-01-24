#!/usr/bin/env python3
"""
Demonstration script for the Intelligent Codebase Analyzer

This script showcases the analyzer's capabilities by running it on sample
codebases and generating detailed reports.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import our analyzer
sys.path.insert(0, str(Path(__file__).parent))

from codebase_analyzer import CodebaseAnalyzer, ArchitecturalPattern


def create_sample_codebase():
    """Create a sample codebase structure to demonstrate the analyzer."""
    sample_dir = Path("sample_project")
    sample_dir.mkdir(exist_ok=True)

    # Create a models directory with some sample files
    models_dir = sample_dir / "models"
    models_dir.mkdir(exist_ok=True)

    (models_dir / "user.py").write_text("""
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def validate_email(self):
        return "@" in self.email

    def get_profile(self):
        return {"username": self.username, "email": self.email}

    def update_password(self, new_password):
        # Complex password validation logic
        if len(new_password) < 8:
            return False
        if not any(c.isupper() for c in new_password):
            return False
        if not any(c.islower() for c in new_password):
            return False
        if not any(c.isdigit() for c in new_password):
            return False
        return True
""")

    (models_dir / "product.py").write_text("""
from .user import User

class Product:
    def __init__(self, name, price, category):
        self.name = name
        self.price = price
        self.category = category

    def calculate_discount(self, user_type):
        if user_type == "premium":
            return self.price * 0.9
        elif user_type == "regular":
            return self.price * 0.95
        else:
            return self.price

    def is_available(self):
        return True
""")

    # Create controllers directory
    controllers_dir = sample_dir / "controllers"
    controllers_dir.mkdir(exist_ok=True)

    (controllers_dir / "user_controller.py").write_text("""
from models.user import User

class UserController:
    def __init__(self):
        self.users = []

    def create_user(self, username, email):
        user = User(username, email)
        if user.validate_email():
            self.users.append(user)
            return user
        return None

    def get_user(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None

    def update_user(self, username, email=None):
        user = self.get_user(username)
        if user:
            if email:
                user.email = email
            return user
        return None

    # This is a complex method that does too many things (god object pattern)
    def process_user_data(self, user_data):
        # Validation
        if not user_data.get('username'):
            return False
        if not user_data.get('email'):
            return False

        # Creation
        user = self.create_user(user_data['username'], user_data['email'])
        if not user:
            return False

        # Additional processing
        if user_data.get('preferences'):
            self.process_preferences(user, user_data['preferences'])
        if user_data.get('settings'):
            self.process_settings(user, user_data['settings'])
        if user_data.get('notifications'):
            self.process_notifications(user, user_data['notifications'])

        return True

    def process_preferences(self, user, preferences):
        # Complex preference processing
        pass

    def process_settings(self, user, settings):
        # Complex settings processing
        pass

    def process_notifications(self, user, notifications):
        # Complex notification processing
        pass
""")

    # Create views directory
    views_dir = sample_dir / "views"
    views_dir.mkdir(exist_ok=True)

    (views_dir / "user_view.py").write_text("""
from controllers.user_controller import UserController

class UserView:
    def __init__(self):
        self.controller = UserController()

    def render_user_list(self):
        html = "<ul>"
        for user in self.controller.users:
            html += f"<li>{user.username} - {user.email}</li>"
        html += "</ul>"
        return html

    def render_user_profile(self, username):
        user = self.controller.get_user(username)
        if user:
            profile = user.get_profile()
            return f"<h1>{profile['username']}</h1><p>{profile['email']}</p>"
        return "<p>User not found</p>"
""")

    # Create a large file to trigger complexity warnings
    (sample_dir / "large_module.py").write_text("""
# This is intentionally a large file to demonstrate the analyzer's
# ability to detect files that should be refactored

class LargeClass:
    def __init__(self):
        self.data = {}

    def method_1(self):
        for i in range(100):
            if i % 2 == 0:
                for j in range(10):
                    if j % 3 == 0:
                        self.data[f"key_{i}_{j}"] = i * j
                    elif j % 3 == 1:
                        self.data[f"alt_{i}_{j}"] = i + j
                    else:
                        self.data[f"other_{i}_{j}"] = i - j
        return self.data

    def method_2(self):
        result = []
        for key, value in self.data.items():
            if "key_" in key:
                if value > 100:
                    for x in range(value):
                        if x % 5 == 0:
                            result.append(x * 2)
                        elif x % 5 == 1:
                            result.append(x * 3)
                        elif x % 5 == 2:
                            result.append(x * 4)
                        else:
                            result.append(x)
            elif "alt_" in key:
                for y in range(min(value, 50)):
                    if y < 10:
                        result.append(y)
                    elif y < 20:
                        result.append(y * 2)
                    else:
                        result.append(y * 3)
        return result

    def method_3(self):
        # More complex nested logic
        processed = {}
        for i in range(50):
            if i % 2 == 0:
                for j in range(i):
                    if j % 3 == 0:
                        for k in range(j):
                            if k % 2 == 0:
                                processed[f"complex_{i}_{j}_{k}"] = i + j + k
                            else:
                                processed[f"simple_{i}_{j}_{k}"] = i * j * k
        return processed

    # Many more methods to increase complexity...
    def method_4(self): pass
    def method_5(self): pass
    def method_6(self): pass
    def method_7(self): pass
    def method_8(self): pass
    def method_9(self): pass
    def method_10(self): pass
    def method_11(self): pass
    def method_12(self): pass
    def method_13(self): pass
    def method_14(self): pass
    def method_15(self): pass
    def method_16(self): pass
    def method_17(self): pass
    def method_18(self): pass
    def method_19(self): pass
    def method_20(self): pass
    def method_21(self): pass
    def method_22(self): pass
    def method_23(self): pass
    def method_24(self): pass
    def method_25(self): pass
""")

    return sample_dir


def analyze_codebase(path):
    """Analyze a codebase and print detailed results."""
    print(f"🔍 Analyzing codebase at: {path}")
    print("=" * 60)

    analyzer = CodebaseAnalyzer(str(path))
    insights = analyzer.analyze()

    # Overview
    print("\n📊 OVERVIEW")
    print(f"Total files analyzed: {insights.total_files}")
    print(f"Total lines of code: {insights.total_lines:,}")
    print(f"Programming languages: {', '.join(insights.languages.keys())}")

    # Language breakdown
    print(f"\n🗣️ LANGUAGE DISTRIBUTION")
    for lang, count in sorted(insights.languages.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / insights.total_files) * 100
        print(f"  {lang.capitalize()}: {count} files ({percentage:.1f}%)")

    # Architectural patterns
    print(f"\n🏗️ ARCHITECTURAL PATTERNS ({len(insights.patterns)})")
    if insights.patterns:
        for pattern in insights.patterns:
            status = "❌ Anti-pattern" if pattern.is_antipattern else "✅ Good pattern"
            print(f"  {status}: {pattern.name}")
            print(f"    Confidence: {pattern.confidence:.0%}")
            print(f"    Description: {pattern.description}")
            print(f"    Files involved: {len(pattern.files_involved)}")
            if pattern.suggestions:
                print("    Suggestions:")
                for suggestion in pattern.suggestions:
                    print(f"      • {suggestion}")
            print()
    else:
        print("  No specific patterns detected")

    # Complexity hotspots
    print(f"\n🔥 COMPLEXITY HOTSPOTS")
    for i, (path, score) in enumerate(insights.complexity_hotspots[:5], 1):
        print(f"  {i}. {path.name}: {score:.1f} complexity score")

    # Dependency graph
    print(f"\n🔗 DEPENDENCIES")
    if insights.dependency_graph:
        for module, deps in list(insights.dependency_graph.items())[:5]:
            if deps:
                print(f"  {Path(module).name} depends on:")
                for dep in deps:
                    print(f"    • {Path(dep).name}")
    else:
        print("  No internal dependencies detected")

    # General suggestions
    print(f"\n💡 IMPROVEMENT SUGGESTIONS")
    if insights.suggestions:
        for suggestion in insights.suggestions:
            print(f"  • {suggestion}")
    else:
        print("  No major issues detected - great job!")

    print("\n" + "=" * 60)
    return insights


def demonstrate_capabilities():
    """Run a complete demonstration of the analyzer capabilities."""
    print("🚀 INTELLIGENT CODEBASE ANALYZER DEMONSTRATION")
    print("=" * 60)

    # First, create a sample codebase
    print("\n1. Creating sample codebase...")
    sample_dir = create_sample_codebase()
    print(f"✅ Sample codebase created at: {sample_dir.absolute()}")

    # Analyze the sample codebase
    print("\n2. Analyzing sample codebase...")
    sample_insights = analyze_codebase(sample_dir)

    # Analyze the analyzer itself (meta-analysis)
    print("\n\n🔄 META-ANALYSIS: Analyzing the analyzer tool itself...")
    current_dir = Path(__file__).parent
    analyzer_insights = analyze_codebase(current_dir)

    # Compare results
    print(f"\n📋 COMPARISON SUMMARY")
    print(f"Sample project: {sample_insights.total_files} files, {sample_insights.total_lines} lines")
    print(f"Analyzer project: {analyzer_insights.total_files} files, {analyzer_insights.total_lines} lines")

    # Clean up
    try:
        import shutil
        shutil.rmtree(sample_dir)
        print(f"\n🧹 Cleaned up sample directory")
    except:
        print(f"\n⚠️ Note: Sample directory {sample_dir} was not cleaned up")

    print("\n✨ Demonstration complete!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Analyze a specific directory provided as argument
        target_path = Path(sys.argv[1])
        if target_path.exists():
            analyze_codebase(target_path)
        else:
            print(f"Error: Directory {target_path} does not exist")
    else:
        # Run the full demonstration
        demonstrate_capabilities()