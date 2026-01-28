#!/usr/bin/env python3
"""
Intelligent Code Review Assistant - Proof of Concept

This demonstrates the core concept of providing contextual, educational
feedback during code reviews rather than just flagging issues.
"""

import ast
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Category(Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"


@dataclass
class ReviewSuggestion:
    """A code review suggestion with educational context."""
    line_number: int
    severity: Severity
    category: Category
    title: str
    explanation: str
    suggestion: str
    example: Optional[str] = None
    resources: List[str] = None

    def format_feedback(self) -> str:
        """Format the suggestion as human-readable feedback."""
        feedback = f"📍 Line {self.line_number} - {self.severity.value.upper()}: {self.title}\n\n"
        feedback += f"💡 **Why this matters**: {self.explanation}\n\n"
        feedback += f"🔧 **Suggested fix**: {self.suggestion}\n"

        if self.example:
            feedback += f"\n📝 **Example**:\n```python\n{self.example}\n```\n"

        if self.resources:
            feedback += f"\n📚 **Learn more**: {', '.join(self.resources)}\n"

        return feedback


class CodeAnalyzer:
    """Analyzes Python code for review suggestions."""

    def __init__(self):
        self.suggestions: List[ReviewSuggestion] = []

    def analyze_code(self, code: str) -> List[ReviewSuggestion]:
        """Analyze code and return educational suggestions."""
        self.suggestions = []

        try:
            tree = ast.parse(code)
            self._analyze_ast(tree, code.split('\n'))
        except SyntaxError as e:
            self.suggestions.append(ReviewSuggestion(
                line_number=e.lineno or 1,
                severity=Severity.ERROR,
                category=Category.STYLE,
                title="Syntax Error",
                explanation="Python couldn't parse this code due to invalid syntax.",
                suggestion="Fix the syntax error before proceeding with the review.",
            ))

        return self.suggestions

    def _analyze_ast(self, tree: ast.AST, lines: List[str]):
        """Walk the AST and analyze patterns."""
        for node in ast.walk(tree):
            self._check_sql_injection(node, lines)
            self._check_hardcoded_secrets(node, lines)
            self._check_inefficient_loops(node, lines)
            self._check_exception_handling(node, lines)

    def _check_sql_injection(self, node: ast.AST, lines: List[str]):
        """Check for potential SQL injection vulnerabilities."""
        if isinstance(node, ast.Call) and hasattr(node.func, 'attr'):
            if node.func.attr in ['execute', 'executemany']:
                # Check if using string formatting in SQL
                if node.args and isinstance(node.args[0], (ast.BinOp, ast.JoinedStr)):
                    self.suggestions.append(ReviewSuggestion(
                        line_number=node.lineno,
                        severity=Severity.ERROR,
                        category=Category.SECURITY,
                        title="Potential SQL Injection Vulnerability",
                        explanation="String concatenation or f-strings in SQL queries can allow attackers to inject malicious SQL code, potentially compromising your database.",
                        suggestion="Use parameterized queries instead of string formatting. This separates SQL logic from data, making injection attacks impossible.",
                        example="# Instead of:\ncursor.execute(f'SELECT * FROM users WHERE id = {user_id}')\n\n# Use:\ncursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
                        resources=["https://owasp.org/www-community/attacks/SQL_Injection"]
                    ))

    def _check_hardcoded_secrets(self, node: ast.AST, lines: List[str]):
        """Check for hardcoded secrets."""
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id.lower()
                    if any(keyword in var_name for keyword in ['password', 'secret', 'key', 'token']):
                        if isinstance(node.value, ast.Constant):
                            self.suggestions.append(ReviewSuggestion(
                                line_number=node.lineno,
                                severity=Severity.WARNING,
                                category=Category.SECURITY,
                                title="Hardcoded Secret Detected",
                                explanation="Hardcoding secrets in source code is dangerous because they can be exposed in version control, logs, or to anyone with access to the code.",
                                suggestion="Store secrets in environment variables or a secure configuration management system.",
                                example="# Instead of:\napi_key = 'sk-1234567890abcdef'\n\n# Use:\nimport os\napi_key = os.getenv('API_KEY')\nif not api_key:\n    raise ValueError('API_KEY environment variable is required')"
                            ))

    def _check_inefficient_loops(self, node: ast.AST, lines: List[str]):
        """Check for potentially inefficient loop patterns."""
        if isinstance(node, ast.For):
            # Check for list appending in loops that could be list comprehensions
            if isinstance(node.target, ast.Name) and len(node.body) == 1:
                stmt = node.body[0]
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    if (hasattr(stmt.value.func, 'attr') and
                        stmt.value.func.attr == 'append'):
                        self.suggestions.append(ReviewSuggestion(
                            line_number=node.lineno,
                            severity=Severity.INFO,
                            category=Category.PERFORMANCE,
                            title="Consider List Comprehension",
                            explanation="List comprehensions are generally faster and more Pythonic than building lists with loops and append() calls. They're also more readable for simple transformations.",
                            suggestion="Consider using a list comprehension if the logic is simple enough.",
                            example="# Instead of:\nresults = []\nfor item in items:\n    results.append(transform(item))\n\n# Consider:\nresults = [transform(item) for item in items]"
                        ))

    def _check_exception_handling(self, node: ast.AST, lines: List[str]):
        """Check for problematic exception handling patterns."""
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:  # bare except:
                self.suggestions.append(ReviewSuggestion(
                    line_number=node.lineno,
                    severity=Severity.WARNING,
                    category=Category.MAINTAINABILITY,
                    title="Bare except clause",
                    explanation="Bare 'except:' clauses catch ALL exceptions, including system exits and keyboard interrupts. This can make debugging difficult and hide unexpected errors.",
                    suggestion="Catch specific exception types that you can actually handle meaningfully.",
                    example="# Instead of:\ntry:\n    risky_operation()\nexcept:\n    print('Something went wrong')\n\n# Use:\ntry:\n    risky_operation()\nexcept ValueError as e:\n    print(f'Invalid value: {e}')\nexcept requests.RequestException as e:\n    print(f'Network error: {e}')"
                ))


def demo_review():
    """Demonstrate the code review assistant with example code."""

    # Example code with various issues
    problematic_code = '''
import sqlite3

password = "super_secret_123"

def get_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # This is vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)

    try:
        result = cursor.fetchone()
        return result
    except:
        return None
    finally:
        conn.close()

def process_items(items):
    results = []
    for item in items:
        results.append(item.upper())
    return results
'''

    analyzer = CodeAnalyzer()
    suggestions = analyzer.analyze_code(problematic_code)

    print("🔍 Code Review Results")
    print("=" * 50)

    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion.format_feedback()}")
        print("-" * 50)


if __name__ == "__main__":
    demo_review()