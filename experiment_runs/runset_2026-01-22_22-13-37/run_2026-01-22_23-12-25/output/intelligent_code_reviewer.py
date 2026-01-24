#!/usr/bin/env python3
"""
Intelligent Code Review Assistant

A prototype tool that provides contextual, educational code review comments
by analyzing code patterns, security concerns, and best practices.

The goal is to balance being helpful and educational while avoiding verbosity
and false positives that make automated reviews annoying.

Key features:
- Multiple review styles (concise, educational, collaborative, mentor)
- Contextual explanations that help developers learn
- Prioritized feedback focusing on what matters most
- Natural language that feels like a helpful colleague

Usage:
    python intelligent_code_reviewer.py <file_path> [--style STYLE]
    python intelligent_code_reviewer.py --demo  # Run with example code
"""

import ast
import re
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from enum import Enum


class ReviewPriority(Enum):
    """Priority levels for review comments"""
    CRITICAL = "critical"      # Security, bugs, breaking changes
    IMPORTANT = "important"    # Performance, maintainability issues
    SUGGESTION = "suggestion"  # Style, best practices, improvements
    EDUCATIONAL = "educational" # Context and learning opportunities


class ReviewStyle(Enum):
    """Different review styles to match team preferences"""
    CONCISE = "concise"        # Minimal, actionable comments
    EDUCATIONAL = "educational" # Detailed explanations with context
    COLLABORATIVE = "collaborative" # Questions and suggestions
    MENTOR = "mentor"          # Teaching-focused with examples


@dataclass
class CodeIssue:
    """Represents a code issue with contextual feedback."""
    line_number: int
    column: int
    priority: ReviewPriority
    category: str
    title: str
    description: str
    suggestion: Optional[str] = None
    example: Optional[str] = None


class IntelligentCodeReviewer:
    """
    Analyzes Python code and provides natural language feedback.

    Unlike traditional linters that focus on style, this tool aims to provide
    educational, contextual feedback that helps developers understand not just
    what to change, but why the change would be beneficial.
    """

    def __init__(self, style: ReviewStyle = ReviewStyle.COLLABORATIVE):
        self.style = style
        self.patterns = [
            self._check_exception_handling,
            self._check_variable_naming,
            self._check_function_complexity,
            self._check_resource_management,
            self._check_security_patterns,
            self._check_magic_numbers,
            self._check_pythonic_patterns,
        ]

    def review_code(self, code: str, filename: str = "unknown") -> List[CodeIssue]:
        """
        Analyze code and return a list of issues with explanatory feedback.

        Args:
            code: The source code to analyze
            filename: Optional filename for context

        Returns:
            List of CodeIssue objects with natural language feedback
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [CodeIssue(
                line_number=e.lineno or 0,
                column=e.offset or 0,
                priority=ReviewPriority.CRITICAL,
                category="syntax",
                title="Syntax Error",
                description=f"There's a syntax error that prevents the code from running: {e.msg}",
                suggestion="Fix the syntax error before proceeding with other improvements."
            )]

        issues = []
        lines = code.split('\n')

        # Run each pattern checker
        for pattern_checker in self.patterns:
            issues.extend(pattern_checker(tree, lines))

        # Sort by line number for better readability
        return sorted(issues, key=lambda x: x.line_number)

    def _check_exception_handling(self, tree: ast.AST, lines: List[str]) -> List[CodeIssue]:
        """Check for bare except clauses and overly broad exception handling."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:  # bare except:
                    issues.append(CodeIssue(
                        line_number=node.lineno,
                        column=node.col_offset,
                        priority=ReviewPriority.IMPORTANT,
                        category="exception_handling",
                        title="Bare except clause detected",
                        description=(
                            "Using a bare 'except:' clause can hide important errors and make "
                            "debugging difficult. It catches all exceptions, including system "
                            "exits and keyboard interrupts, which usually shouldn't be caught."
                        ),
                        suggestion="Consider catching specific exception types instead",
                        example="try:\n    risky_operation()\nexcept ValueError as e:\n    handle_value_error(e)"
                    ))

        return issues

    def _check_variable_naming(self, tree: ast.AST, lines: List[str]) -> List[CodeIssue]:
        """Check for unclear variable names and suggest improvements."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                name = node.id

                # Check for single-letter variables (except common loop counters)
                if len(name) == 1 and name not in ['i', 'j', 'k', 'x', 'y', 'z']:
                    issues.append(CodeIssue(
                        line_number=node.lineno,
                        column=node.col_offset,
                        priority=ReviewPriority.SUGGESTION,
                        category="naming",
                        title=f"Single-letter variable '{name}' could be more descriptive",
                        description=(
                            f"The variable '{name}' uses a single letter, which might make "
                            "the code harder to understand. Consider using a more descriptive "
                            "name that explains what the variable represents."
                        ),
                        suggestion=f"Consider renaming '{name}' to something more descriptive"
                    ))

                # Check for data/df variables that could be more specific
                if name in ['data', 'df'] and hasattr(node, 'lineno'):
                    line_content = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                    if 'pandas' in line_content or 'pd.' in line_content:
                        issues.append(CodeIssue(
                            line_number=node.lineno,
                            column=node.col_offset,
                            priority=ReviewPriority.SUGGESTION,
                            category="naming",
                            title=f"Generic variable name '{name}' could be more specific",
                            description=(
                                f"The variable '{name}' is quite generic. When working with "
                                "dataframes, more specific names help other developers (and "
                                "future you) understand what data is being processed."
                            ),
                            suggestion=f"Consider renaming '{name}' to describe the data it contains",
                            example="sales_data, user_metrics, or processed_results"
                        ))

        return issues

    def _check_function_complexity(self, tree: ast.AST, lines: List[str]) -> List[CodeIssue]:
        """Check for overly complex functions that might benefit from refactoring."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count nested levels (simplified complexity metric)
                max_depth = self._calculate_nesting_depth(node)
                line_count = len([n for n in ast.walk(node) if hasattr(n, 'lineno')])

                if max_depth > 4:
                    issues.append(CodeIssue(
                        line_number=node.lineno,
                        column=node.col_offset,
                        priority=ReviewPriority.SUGGESTION,
                        category="complexity",
                        title=f"Function '{node.name}' has deep nesting",
                        description=(
                            f"The function '{node.name}' has {max_depth} levels of nesting. "
                            "Deeply nested code can be harder to read and test. Consider "
                            "extracting some logic into separate functions or using early "
                            "returns to reduce nesting."
                        ),
                        suggestion="Try using early returns or extracting nested logic into helper functions"
                    ))

                if line_count > 50:
                    issues.append(CodeIssue(
                        line_number=node.lineno,
                        column=node.col_offset,
                        priority=ReviewPriority.SUGGESTION,
                        category="complexity",
                        title=f"Function '{node.name}' is quite long",
                        description=(
                            f"The function '{node.name}' is quite long ({line_count} lines). "
                            "Long functions can be harder to understand, test, and maintain. "
                            "Consider breaking it into smaller, focused functions that each "
                            "handle one specific responsibility."
                        ),
                        suggestion="Consider splitting this into smaller functions with clear responsibilities"
                    ))

        return issues

    def _check_resource_management(self, tree: ast.AST, lines: List[str]) -> List[CodeIssue]:
        """Check for file operations that should use context managers."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Name) and node.func.id == 'open'):
                    # Note: This is a simplified check - in a real implementation,
                    # we'd need to track the AST hierarchy to see if we're in a with statement
                    issues.append(CodeIssue(
                        line_number=node.lineno,
                        column=node.col_offset,
                        priority=ReviewPriority.IMPORTANT,
                        category="resources",
                        title="File operation should use context manager",
                        description=(
                            "File operations with open() should typically use a 'with' statement "
                            "to ensure the file is properly closed, even if an exception occurs. "
                            "This prevents resource leaks and is considered a Python best practice."
                        ),
                        suggestion="Use 'with open(...) as f:' instead of just 'open(...)'",
                        example="with open('file.txt', 'r') as f:\n    content = f.read()"
                    ))

        return issues

    def _check_security_patterns(self, tree: ast.AST, lines: List[str]) -> List[CodeIssue]:
        """Check for potential security issues."""
        issues = []

        for node in ast.walk(tree):
            # Check for eval() usage
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'eval':
                    issues.append(CodeIssue(
                        line_number=node.lineno,
                        column=node.col_offset,
                        priority=ReviewPriority.CRITICAL,
                        category="security",
                        title="Use of eval() detected",
                        description=(
                            "The eval() function executes arbitrary Python code, which can be "
                            "a serious security risk if the input comes from an untrusted source. "
                            "It can also make code harder to understand and debug."
                        ),
                        suggestion="Consider using safer alternatives like ast.literal_eval() for data, or json.loads() for JSON",
                        example="# Instead of eval(user_input)\n# Use ast.literal_eval(user_input) for safe evaluation of literals"
                    ))

        return issues

    def _check_magic_numbers(self, tree: ast.AST, lines: List[str]) -> List[CodeIssue]:
        """Check for magic numbers that should be named constants."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Skip common non-magic numbers
                if node.value in [0, 1, -1, 2, 10, 100]:
                    continue

                # Skip small numbers that are likely not magic
                if isinstance(node.value, int) and -10 <= node.value <= 10:
                    continue

                issues.append(CodeIssue(
                    line_number=node.lineno,
                    column=node.col_offset,
                    priority=ReviewPriority.SUGGESTION,
                    category="maintainability",
                    title=f"Magic number {node.value} could be a named constant",
                    description=(
                        f"The number {node.value} appears to be a 'magic number' - a numeric "
                        "literal with unclear meaning. Using a named constant makes the code "
                        "more readable and maintainable."
                    ),
                    suggestion=f"Consider defining a constant: MEANINGFUL_NAME = {node.value}",
                    example="# At the top of your file:\nMAX_RETRIES = 3\nTIMEOUT_SECONDS = 30"
                ))

        return issues

    def _calculate_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate the maximum nesting depth in an AST node."""
        max_depth = depth

        # Nodes that increase nesting depth
        nesting_nodes = (ast.If, ast.While, ast.For, ast.With, ast.Try, ast.FunctionDef, ast.ClassDef)

        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_nodes):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _check_pythonic_patterns(self, tree: ast.AST, lines: List[str]) -> List[CodeIssue]:
        """Check for non-Pythonic patterns that could be improved."""
        issues = []

        for node in ast.walk(tree):
            # Check for range(len()) pattern
            if (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Name) and
                node.func.id == 'range' and
                len(node.args) == 1 and
                isinstance(node.args[0], ast.Call) and
                isinstance(node.args[0].func, ast.Name) and
                node.args[0].func.id == 'len'):

                issues.append(CodeIssue(
                    line_number=node.lineno,
                    column=node.col_offset,
                    priority=ReviewPriority.EDUCATIONAL,
                    category="pythonic",
                    title="Consider using enumerate() instead of range(len())",
                    description=(
                        "Using range(len()) is a common pattern but not very Pythonic. "
                        "The enumerate() function is more readable and gives you both "
                        "the index and the item directly."
                    ),
                    suggestion="Replace 'for i in range(len(items))' with 'for i, item in enumerate(items)'",
                    example="# Instead of:\nfor i in range(len(items)):\n    print(i, items[i])\n\n# Use:\nfor i, item in enumerate(items):\n    print(i, item)"
                ))

            # Check for manual list comprehension that could be simplified
            if isinstance(node, ast.For):
                # This is a simplified check - would need more sophisticated analysis in practice
                for child in ast.walk(node):
                    if (isinstance(child, ast.Call) and
                        isinstance(child.func, ast.Attribute) and
                        child.func.attr == 'append'):

                        issues.append(CodeIssue(
                            line_number=node.lineno,
                            column=node.col_offset,
                            priority=ReviewPriority.SUGGESTION,
                            category="pythonic",
                            title="Loop with append() might be a list comprehension",
                            description=(
                                "This loop appears to build a list using append(). "
                                "Consider if this could be simplified with a list comprehension, "
                                "which is often more readable and efficient."
                            ),
                            suggestion="Consider using a list comprehension if the logic is simple enough",
                            example="# Instead of:\nresults = []\nfor item in items:\n    if condition(item):\n        results.append(transform(item))\n\n# Use:\nresults = [transform(item) for item in items if condition(item)]"
                        ))
                        break  # Only suggest this once per loop

        return issues


def format_review(issues: List[CodeIssue], filename: str = "code", style: ReviewStyle = ReviewStyle.COLLABORATIVE) -> str:
    """
    Format code review issues into a readable report.

    Args:
        issues: List of CodeIssue objects
        filename: Name of the file being reviewed
        style: Review style for formatting

    Returns:
        Formatted string report
    """
    if not issues:
        return f"✅ Great! No issues found in {filename}"

    # Sort by priority first, then by line number
    priority_order = {
        ReviewPriority.CRITICAL: 0,
        ReviewPriority.IMPORTANT: 1,
        ReviewPriority.SUGGESTION: 2,
        ReviewPriority.EDUCATIONAL: 3
    }
    sorted_issues = sorted(issues, key=lambda x: (priority_order[x.priority], x.line_number))

    priority_emojis = {
        ReviewPriority.CRITICAL: "🚨",
        ReviewPriority.IMPORTANT: "⚠️",
        ReviewPriority.SUGGESTION: "💡",
        ReviewPriority.EDUCATIONAL: "📚"
    }

    report = [f"\n📋 Code Review for {filename} ({style.value} style)"]
    report.append("=" * 60)

    for i, issue in enumerate(sorted_issues, 1):
        emoji = priority_emojis[issue.priority]

        if style == ReviewStyle.CONCISE:
            # Minimal format for concise style
            report.append(f"\n{emoji} L{issue.line_number}: {issue.title}")
            if issue.suggestion:
                report.append(f"   → {issue.suggestion}")
        else:
            # More detailed format for other styles
            report.append(f"\n{emoji} Issue #{i} - Line {issue.line_number}")
            report.append(f"{issue.title}")

            if style in [ReviewStyle.EDUCATIONAL, ReviewStyle.MENTOR]:
                report.append(f"\n💭 Context: {issue.description}")
            elif style == ReviewStyle.COLLABORATIVE and issue.priority in [ReviewPriority.CRITICAL, ReviewPriority.IMPORTANT]:
                report.append(f"\n{issue.description}")

            if issue.suggestion:
                if style == ReviewStyle.COLLABORATIVE:
                    report.append(f"\n🤔 Consider: {issue.suggestion}")
                else:
                    report.append(f"\n→ Suggestion: {issue.suggestion}")

            if issue.example and style == ReviewStyle.MENTOR:
                report.append(f"\n📝 Example:")
                for line in issue.example.split('\n'):
                    report.append(f"    {line}")

        if style != ReviewStyle.CONCISE:
            report.append("-" * 40)

    return "\n".join(report)


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Intelligent Code Review Assistant")
    parser.add_argument("file", nargs="?", help="Python file to analyze")
    parser.add_argument("--demo", action="store_true", help="Run with example code")
    parser.add_argument("--style", choices=[s.value for s in ReviewStyle],
                       default=ReviewStyle.COLLABORATIVE.value,
                       help="Review style (default: collaborative)")
    parser.add_argument("--compare-styles", action="store_true",
                       help="Show output for all review styles")

    args = parser.parse_args()
    style = ReviewStyle(args.style)

    # Example usage with some intentionally problematic code
    if args.demo:
        sample_code = '''
def process_data(data):
    f = open("output.txt", "w")
    processed = []
    try:
        for i in range(len(data)):
            if data[i] > 0:
                if data[i] < 100:
                    if data[i] % 2 == 0:
                        if data[i] not in processed:
                            result = eval(f"data[{i}] * 2")
                            f.write(str(result))
                            processed.append(data[i])
    except:
        print("Error occurred")

    timeout = 30
    return processed
        '''

        if args.compare_styles:
            print("🔍 Comparing Different Review Styles\n")
            for review_style in ReviewStyle:
                reviewer = IntelligentCodeReviewer(review_style)
                issues = reviewer.review_code(sample_code, "example.py")
                print(format_review(issues, "example.py", review_style))
                print("\n" + "="*80 + "\n")
        else:
            reviewer = IntelligentCodeReviewer(style)
            issues = reviewer.review_code(sample_code, "example.py")
            print(format_review(issues, "example.py", style))

    elif args.file:
        # Analyze a specific file
        filename = args.file
        try:
            with open(filename, 'r') as f:
                code = f.read()

            if args.compare_styles:
                print(f"🔍 Comparing Different Review Styles for {filename}\n")
                for review_style in ReviewStyle:
                    reviewer = IntelligentCodeReviewer(review_style)
                    issues = reviewer.review_code(code, filename)
                    print(format_review(issues, filename, review_style))
                    print("\n" + "="*80 + "\n")
            else:
                reviewer = IntelligentCodeReviewer(style)
                issues = reviewer.review_code(code, filename)
                print(format_review(issues, filename, style))

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
        except Exception as e:
            print(f"Error analyzing file: {e}")

    else:
        print(__doc__)
        print("\nExample usage:")
        print("  python intelligent_code_reviewer.py my_code.py")
        print("  python intelligent_code_reviewer.py --demo")
        print("  python intelligent_code_reviewer.py --demo --style concise")
        print("  python intelligent_code_reviewer.py --demo --compare-styles")