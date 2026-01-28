#!/usr/bin/env python3
"""
Intelligent Code Review Assistant - Educational Feedback Demo

This prototype demonstrates contextual, educational code review feedback
that goes beyond simple rule checking to provide learning opportunities.
"""

import ast
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class ReviewSeverity(Enum):
    INFO = "info"
    SUGGESTION = "suggestion"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ReviewFeedback:
    """Represents a piece of code review feedback with educational context"""
    line_number: int
    severity: ReviewSeverity
    category: str
    title: str
    message: str
    explanation: str
    example: str = ""
    references: List[str] = None

    def __post_init__(self):
        if self.references is None:
            self.references = []


class EducationalCodeAnalyzer:
    """
    Analyzes Python code and provides educational feedback similar to how
    an experienced developer might comment during code review.
    """

    def __init__(self):
        self.patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, Any]:
        """Initialize detection patterns for common code review issues"""
        return {
            'security': {
                'sql_injection': r'execute\s*\(\s*["\'].*%.*["\']',
                'hardcoded_secrets': r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']'
            },
            'performance': {
                'string_concatenation_in_loop': 'detect_via_ast',
                'redundant_list_comprehension': r'\[.*for.*in.*\]'
            },
            'maintainability': {
                'deep_nesting': 'detect_via_ast',
                'long_functions': 'detect_via_ast'
            }
        }

    def analyze_code(self, code: str) -> List[ReviewFeedback]:
        """
        Analyze code and return educational feedback

        Args:
            code: Python source code to analyze

        Returns:
            List of ReviewFeedback objects with educational context
        """
        feedback = []

        try:
            tree = ast.parse(code)
            lines = code.split('\n')

            # AST-based analysis
            feedback.extend(self._analyze_with_ast(tree, lines))

            # Pattern-based analysis
            feedback.extend(self._analyze_with_patterns(lines))

        except SyntaxError as e:
            feedback.append(ReviewFeedback(
                line_number=e.lineno or 1,
                severity=ReviewSeverity.ERROR,
                category="syntax",
                title="Syntax Error",
                message=f"Code has syntax error: {e.msg}",
                explanation="Syntax errors prevent code from running. This needs to be fixed before the code can be executed or properly analyzed."
            ))

        return sorted(feedback, key=lambda x: (x.line_number, x.severity.value))

    def _analyze_with_ast(self, tree: ast.AST, lines: List[str]) -> List[ReviewFeedback]:
        """Perform AST-based analysis for complex patterns"""
        feedback = []

        class CodeAnalysisVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check function length
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    length = node.end_lineno - node.lineno + 1
                    if length > 50:
                        feedback.append(ReviewFeedback(
                            line_number=node.lineno,
                            severity=ReviewSeverity.SUGGESTION,
                            category="maintainability",
                            title="Long Function",
                            message=f"Function '{node.name}' is {length} lines long",
                            explanation="Functions longer than 50 lines can become hard to understand and test. Consider breaking this into smaller, focused functions. Each function should ideally do one thing well.",
                            example="""# Instead of one long function:
def process_data(data):
    # 50+ lines of processing...

# Consider breaking it down:
def validate_data(data): ...
def transform_data(data): ...
def save_data(data): ...

def process_data(data):
    validate_data(data)
    transformed = transform_data(data)
    save_data(transformed)""",
                            references=["Clean Code by Robert Martin", "PEP 8 - Function and Variable Names"]
                        ))

                # Check for deep nesting
                max_depth = self._calculate_nesting_depth(node)
                if max_depth > 4:
                    feedback.append(ReviewFeedback(
                        line_number=node.lineno,
                        severity=ReviewSeverity.WARNING,
                        category="maintainability",
                        title="Deep Nesting",
                        message=f"Function has nesting depth of {max_depth}",
                        explanation="Deep nesting (more than 4 levels) makes code harder to read and understand. Consider using early returns, extracting nested logic into separate functions, or using guard clauses.",
                        example="""# Instead of deep nesting:
def process_item(item):
    if item:
        if item.is_valid():
            if item.needs_processing():
                if item.has_permission():
                    return item.process()

# Use early returns:
def process_item(item):
    if not item:
        return None
    if not item.is_valid():
        return None
    if not item.needs_processing():
        return None
    if not item.has_permission():
        return None
    return item.process()""",
                        references=["Refactoring by Martin Fowler"]
                    ))

                self.generic_visit(node)

            def _calculate_nesting_depth(self, node: ast.AST) -> int:
                """Calculate maximum nesting depth in a function"""
                max_depth = 0

                def visit_nested(node, current_depth=0):
                    nonlocal max_depth
                    max_depth = max(max_depth, current_depth)

                    nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try)
                    for child in ast.iter_child_nodes(node):
                        if isinstance(child, nesting_nodes):
                            visit_nested(child, current_depth + 1)
                        else:
                            visit_nested(child, current_depth)

                visit_nested(node)
                return max_depth

        visitor = CodeAnalysisVisitor()
        visitor.visit(tree)

        return feedback

    def _analyze_with_patterns(self, lines: List[str]) -> List[ReviewFeedback]:
        """Perform regex-based pattern analysis"""
        feedback = []

        for i, line in enumerate(lines, 1):
            # Check for potential SQL injection
            if re.search(self.patterns['security']['sql_injection'], line, re.IGNORECASE):
                feedback.append(ReviewFeedback(
                    line_number=i,
                    severity=ReviewSeverity.ERROR,
                    category="security",
                    title="Potential SQL Injection",
                    message="String formatting in SQL query detected",
                    explanation="Using string formatting or concatenation in SQL queries can lead to SQL injection vulnerabilities. Attackers can manipulate the query by injecting malicious SQL code.",
                    example="""# Vulnerable:
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# Safe:
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# Or with SQLAlchemy:
user = session.query(User).filter(User.id == user_id).first()""",
                    references=["OWASP SQL Injection", "PEP 249 - Database API"]
                ))

            # Check for hardcoded secrets
            if re.search(self.patterns['security']['hardcoded_secrets'], line, re.IGNORECASE):
                feedback.append(ReviewFeedback(
                    line_number=i,
                    severity=ReviewSeverity.WARNING,
                    category="security",
                    title="Hardcoded Secret",
                    message="Potential hardcoded secret or credential detected",
                    explanation="Hardcoding secrets in source code is a security risk. Secrets can be exposed through version control, logs, or anyone with access to the code. Use environment variables or secure credential management instead.",
                    example="""# Instead of:
API_KEY = "sk-1234567890abcdef"

# Use environment variables:
import os
API_KEY = os.getenv('API_KEY')

# Or a config file that's not in version control:
from config import get_secret
API_KEY = get_secret('API_KEY')""",
                    references=["12-Factor App Config", "OWASP Secrets Management"]
                ))

        return feedback

    def format_feedback(self, feedback: List[ReviewFeedback]) -> str:
        """Format feedback for display in a code review context"""
        if not feedback:
            return "✅ No issues found! Code looks good."

        output = []
        output.append(f"📋 **Code Review Analysis** ({len(feedback)} items found)")
        output.append("")

        # Group by severity
        by_severity = {}
        for item in feedback:
            if item.severity not in by_severity:
                by_severity[item.severity] = []
            by_severity[item.severity].append(item)

        severity_icons = {
            ReviewSeverity.ERROR: "❌",
            ReviewSeverity.WARNING: "⚠️",
            ReviewSeverity.SUGGESTION: "💡",
            ReviewSeverity.INFO: "ℹ️"
        }

        for severity in [ReviewSeverity.ERROR, ReviewSeverity.WARNING, ReviewSeverity.SUGGESTION, ReviewSeverity.INFO]:
            if severity in by_severity:
                items = by_severity[severity]
                output.append(f"## {severity_icons[severity]} {severity.value.title()} ({len(items)} items)")
                output.append("")

                for item in items:
                    output.append(f"**Line {item.line_number}: {item.title}** ({item.category})")
                    output.append(f"{item.message}")
                    output.append("")
                    output.append("**Why this matters:**")
                    output.append(item.explanation)

                    if item.example:
                        output.append("")
                        output.append("**Example:**")
                        output.append("```python")
                        output.append(item.example)
                        output.append("```")

                    if item.references:
                        output.append("")
                        output.append("**Learn more:** " + " • ".join(item.references))

                    output.append("")
                    output.append("---")
                    output.append("")

        return "\n".join(output)


def demo():
    """Demonstrate the educational code review assistant"""

    # Example code with various issues
    sample_code = '''
def process_user_data(user_id, action):
    password = "admin123"  # Hardcoded password

    if user_id:
        if action == "login":
            if check_permissions(user_id):
                if validate_user(user_id):
                    if user_id > 0:
                        # Deep nesting example
                        query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
                        result = execute_query(query)

                        # This function is getting quite long...
                        data = []
                        for item in result:
                            if item.active:
                                if item.verified:
                                    if item.permissions:
                                        processed_item = {
                                            'id': item.id,
                                            'name': item.name,
                                            'email': item.email,
                                            'status': 'active',
                                            'last_login': item.last_login,
                                            'permissions': item.permissions,
                                            'profile': item.profile,
                                            'settings': item.settings
                                        }
                                        data.append(processed_item)

                        return data
    return None

def another_very_long_function_that_does_too_many_things():
    # This function will be flagged as too long
    print("Starting processing...")

    # Simulate a very long function with many operations
    for i in range(100):
        print(f"Processing item {i}")
        if i % 10 == 0:
            print("Checkpoint reached")
        if i % 25 == 0:
            print("Quarter complete")
        # ... many more lines would be here in a real scenario
        # This is just a demonstration
        pass

    print("Processing complete")
    return True
'''

    analyzer = EducationalCodeAnalyzer()
    feedback = analyzer.analyze_code(sample_code)

    print("🔍 **Educational Code Review Assistant Demo**")
    print("=" * 60)
    print()
    print(analyzer.format_feedback(feedback))


if __name__ == "__main__":
    demo()