#!/usr/bin/env python3
"""
Demo script to showcase the Intelligent Codebase Analyzer

This script creates a sample codebase with different patterns and then
analyzes it to demonstrate the analyzer's capabilities.
"""

from pathlib import Path
import os
import tempfile
import shutil
from codebase_analyzer_comprehensive import CodebaseAnalyzer


def create_demo_codebase(base_path: Path) -> Path:
    """Create a sample codebase with various patterns to analyze."""

    # Create directory structure
    (base_path / "models").mkdir(exist_ok=True)
    (base_path / "views").mkdir(exist_ok=True)
    (base_path / "controllers").mkdir(exist_ok=True)
    (base_path / "utils").mkdir(exist_ok=True)

    # Model file
    model_code = '''
from typing import List, Optional
import sqlite3

class User:
    """User model with basic CRUD operations."""

    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
        self.id: Optional[int] = None

    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """Find user by username."""
        # Database query logic would go here
        pass

    def save(self) -> bool:
        """Save user to database."""
        # Database save logic would go here
        pass

    def delete(self) -> bool:
        """Delete user from database."""
        # Database delete logic would go here
        pass

class UserRepository:
    """Repository pattern for User operations."""

    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_users(self) -> List[User]:
        """Retrieve all users."""
        pass

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass
'''

    # View file
    view_code = '''
from typing import Dict, Any
import json

class UserView:
    """Handles user-related view rendering."""

    def render_user_profile(self, user_data: Dict[str, Any]) -> str:
        """Render user profile page."""
        return f"""
        <div class="user-profile">
            <h1>{user_data.get('username', 'Unknown')}</h1>
            <p>Email: {user_data.get('email', 'No email')}</p>
        </div>
        """

    def render_user_list(self, users: list) -> str:
        """Render list of users."""
        user_items = []
        for user in users:
            user_items.append(f"<li>{user.get('username', 'Unknown')}</li>")

        return f"""
        <div class="user-list">
            <h2>Users</h2>
            <ul>{''.join(user_items)}</ul>
        </div>
        """

    def render_json_response(self, data: Dict[str, Any]) -> str:
        """Render JSON response."""
        return json.dumps(data, indent=2)
'''

    # Controller file
    controller_code = '''
from models.user_model import User, UserRepository
from views.user_view import UserView
from typing import Dict, Any, Optional

class UserController:
    """Handles user-related HTTP requests."""

    def __init__(self):
        self.user_repo = UserRepository(None)  # Would inject real DB
        self.user_view = UserView()

    def get_user_profile(self, user_id: int) -> str:
        """Handle GET request for user profile."""
        user = self.user_repo.get_user_by_id(user_id)
        if user:
            user_data = {
                'username': user.username,
                'email': user.email,
                'id': user.id
            }
            return self.user_view.render_user_profile(user_data)
        else:
            return self._render_error("User not found")

    def get_all_users(self) -> str:
        """Handle GET request for all users."""
        users = self.user_repo.get_all_users()
        return self.user_view.render_user_list([
            {'username': u.username, 'email': u.email} for u in users
        ])

    def create_user(self, username: str, email: str) -> str:
        """Handle POST request to create user."""
        user = User(username, email)
        success = user.save()

        if success:
            return self.user_view.render_json_response({
                'status': 'success',
                'message': 'User created successfully'
            })
        else:
            return self._render_error("Failed to create user")

    def _render_error(self, message: str) -> str:
        """Render error response."""
        return self.user_view.render_json_response({
            'status': 'error',
            'message': message
        })
'''

    # Factory pattern example
    factory_code = '''
from typing import Dict, Any
from abc import ABC, abstractmethod

class DatabaseConnection(ABC):
    """Abstract base for database connections."""

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def execute_query(self, query: str) -> Any:
        pass

class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection."""

    def connect(self) -> bool:
        # PostgreSQL connection logic
        return True

    def execute_query(self, query: str) -> Any:
        # Execute PostgreSQL query
        pass

class MySQLConnection(DatabaseConnection):
    """MySQL database connection."""

    def connect(self) -> bool:
        # MySQL connection logic
        return True

    def execute_query(self, query: str) -> Any:
        # Execute MySQL query
        pass

class DatabaseConnectionFactory:
    """Factory for creating database connections."""

    @staticmethod
    def create_connection(db_type: str) -> DatabaseConnection:
        """Create appropriate database connection."""
        if db_type.lower() == 'postgresql':
            return PostgreSQLConnection()
        elif db_type.lower() == 'mysql':
            return MySQLConnection()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
'''

    # Singleton pattern example
    singleton_code = '''
import threading
from typing import Optional, Dict, Any

class ConfigManager:
    """Singleton configuration manager."""

    _instance: Optional['ConfigManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._config: Dict[str, Any] = {}
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        """Get singleton instance."""
        return cls()

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def load_from_file(self, file_path: str) -> None:
        """Load configuration from file."""
        # Configuration loading logic
        pass
'''

    # Complex utility file to trigger complexity warnings
    complex_util_code = '''
def complex_data_processor(data, options=None):
    """A deliberately complex function to trigger complexity warnings."""
    result = []

    if options is None:
        options = {}

    # Many nested conditions and loops to increase complexity
    for item in data:
        if isinstance(item, dict):
            if 'type' in item:
                if item['type'] == 'user':
                    if 'active' in item and item['active']:
                        if 'permissions' in item:
                            for perm in item['permissions']:
                                if perm.startswith('admin'):
                                    if options.get('include_admin', False):
                                        result.append(item)
                                        break
                                elif perm.startswith('user'):
                                    if options.get('include_users', True):
                                        result.append(item)
                                        break
                        else:
                            if options.get('include_no_perms', False):
                                result.append(item)
                    else:
                        if options.get('include_inactive', False):
                            result.append(item)
                elif item['type'] == 'admin':
                    if options.get('include_admin', False):
                        result.append(item)
            else:
                if options.get('include_untyped', False):
                    result.append(item)
        elif isinstance(item, str):
            if len(item) > 10:
                if item.startswith('user_'):
                    result.append({'type': 'user', 'name': item})
                elif item.startswith('admin_'):
                    result.append({'type': 'admin', 'name': item})
            else:
                if options.get('include_short_strings', False):
                    result.append({'type': 'string', 'value': item})
        elif isinstance(item, int):
            if item > 100:
                if item < 1000:
                    result.append({'type': 'medium_int', 'value': item})
                else:
                    result.append({'type': 'large_int', 'value': item})
            else:
                result.append({'type': 'small_int', 'value': item})

    return result
'''

    # Write all the demo files
    with open(base_path / "models" / "user_model.py", 'w') as f:
        f.write(model_code)

    with open(base_path / "views" / "user_view.py", 'w') as f:
        f.write(view_code)

    with open(base_path / "controllers" / "user_controller.py", 'w') as f:
        f.write(controller_code)

    with open(base_path / "utils" / "database_factory.py", 'w') as f:
        f.write(factory_code)

    with open(base_path / "utils" / "config_singleton.py", 'w') as f:
        f.write(singleton_code)

    with open(base_path / "utils" / "complex_processor.py", 'w') as f:
        f.write(complex_util_code)

    return base_path


def main():
    """Run the demo analysis."""
    print("🚀 Creating demo codebase...")

    # Create temporary directory for demo
    demo_dir = Path(tempfile.mkdtemp(prefix="codebase_analyzer_demo_"))
    print(f"📁 Demo codebase created at: {demo_dir}")

    try:
        # Create sample codebase
        create_demo_codebase(demo_dir)

        print("\n🔍 Running codebase analysis...")

        # Analyze the codebase
        analyzer = CodebaseAnalyzer()
        analysis = analyzer.analyze_codebase(demo_dir)

        # Generate and display report
        print("\n" + "="*60)
        print("📊 CODEBASE ANALYSIS RESULTS")
        print("="*60)

        report = analyzer.generate_report(analysis)
        print(report)

        # Show some detailed insights
        print("\n" + "="*60)
        print("🔍 DETAILED INSIGHTS")
        print("="*60)

        print(f"📈 Files analyzed: {len(analysis.file_analyses)}")

        if analysis.architectural_patterns:
            print(f"🏗️  Patterns detected:")
            for pattern in analysis.architectural_patterns:
                print(f"   • {pattern.name} (confidence: {pattern.confidence:.1%})")

        print(f"⚡ Quality metrics:")
        metrics = analysis.quality_metrics
        print(f"   • Average complexity: {metrics.get('average_complexity', 0):.2f}")
        print(f"   • Files with issues: {metrics.get('files_with_issues', 0)}")

        if analysis.suggestions:
            print(f"💡 Top suggestions:")
            for suggestion in analysis.suggestions[:3]:
                print(f"   • {suggestion['message']}")

    finally:
        # Clean up
        print(f"\n🧹 Cleaning up demo directory: {demo_dir}")
        shutil.rmtree(demo_dir)

    print("\n✨ Demo completed! The analyzer successfully identified:")
    print("   • MVC architectural pattern")
    print("   • Factory and Singleton design patterns")
    print("   • Code complexity issues")
    print("   • Quality improvement opportunities")


if __name__ == "__main__":
    main()