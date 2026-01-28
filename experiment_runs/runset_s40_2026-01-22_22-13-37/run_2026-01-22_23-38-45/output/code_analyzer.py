#!/usr/bin/env python3
"""
CodeMentor Analysis Engine - The Intelligence Layer

This module provides sophisticated code analysis capabilities for detecting
architectural patterns, code smells, and opportunities for improvement.
It serves as the core intelligence engine for the CodeMentor collaborative
code review assistant.

Author: Alice (Claude Code Instance)
"""

import ast
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class PatternType(Enum):
    """Types of patterns that can be detected in code"""
    DESIGN_PATTERN = "design_pattern"
    ARCHITECTURAL_PATTERN = "architectural_pattern"
    CODE_SMELL = "code_smell"
    BEST_PRACTICE = "best_practice"
    ANTI_PATTERN = "anti_pattern"


class Severity(Enum):
    """Severity levels for analysis findings"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnalysisResult:
    """Represents a single analysis finding"""
    pattern_type: PatternType
    pattern_name: str
    description: str
    file_path: str
    line_number: int
    severity: Severity
    educational_context: str
    suggestions: List[str]
    code_snippet: Optional[str] = None


class CodeAnalyzer:
    """
    Core analysis engine that examines code for patterns, smells, and improvement opportunities.

    This analyzer combines static analysis with pattern recognition to provide
    educational insights about code structure and quality.
    """

    def __init__(self):
        self.results: List[AnalysisResult] = []
        self.pattern_detectors = [
            self._detect_singleton_pattern,
            self._detect_factory_pattern,
            self._detect_observer_pattern,
            self._detect_long_methods,
            self._detect_large_classes,
            self._detect_duplicate_code,
            self._detect_magic_numbers,
            self._detect_god_objects,
            self._detect_feature_envy
        ]

    def analyze_file(self, file_path: str) -> List[AnalysisResult]:
        """
        Analyze a single Python file for patterns and issues.

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            List of analysis results found in the file
        """
        if not os.path.exists(file_path) or not file_path.endswith('.py'):
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            self.results = []

            # Run all pattern detectors
            for detector in self.pattern_detectors:
                detector(tree, file_path, content)

            return self.results.copy()

        except Exception as e:
            return [AnalysisResult(
                pattern_type=PatternType.CODE_SMELL,
                pattern_name="parse_error",
                description=f"Failed to parse file: {str(e)}",
                file_path=file_path,
                line_number=1,
                severity=Severity.HIGH,
                educational_context="This file contains syntax errors that prevent analysis.",
                suggestions=["Fix syntax errors before analysis"]
            )]

    def analyze_directory(self, directory_path: str) -> List[AnalysisResult]:
        """
        Recursively analyze all Python files in a directory.

        Args:
            directory_path: Path to the directory to analyze

        Returns:
            Combined list of analysis results from all files
        """
        all_results = []

        for root, dirs, files in os.walk(directory_path):
            # Skip common build/cache directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache', 'node_modules'}]

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    results = self.analyze_file(file_path)
                    all_results.extend(results)

        return all_results

    def _detect_singleton_pattern(self, tree: ast.AST, file_path: str, content: str):
        """Detect singleton pattern implementations"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for singleton indicators
                has_new_method = False
                has_instance_attr = False

                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == '__new__':
                        has_new_method = True
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and 'instance' in target.id.lower():
                                has_instance_attr = True

                if has_new_method or has_instance_attr:
                    self.results.append(AnalysisResult(
                        pattern_type=PatternType.DESIGN_PATTERN,
                        pattern_name="Singleton Pattern",
                        description=f"Class '{node.name}' appears to implement the Singleton pattern",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=Severity.INFO,
                        educational_context="The Singleton pattern ensures a class has only one instance. "
                                          "While useful in some cases, it can make testing difficult and "
                                          "introduce global state issues.",
                        suggestions=[
                            "Consider if dependency injection would be better",
                            "Ensure thread safety if needed",
                            "Make the singleton easily testable with mock objects"
                        ]
                    ))

    def _detect_factory_pattern(self, tree: ast.AST, file_path: str, content: str):
        """Detect factory pattern implementations"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for factory method indicators
                if ('create' in node.name.lower() or
                    'factory' in node.name.lower() or
                    'make' in node.name.lower()):

                    # Check if it returns different types based on parameters
                    returns_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))

                    if returns_count > 1:
                        self.results.append(AnalysisResult(
                            pattern_type=PatternType.DESIGN_PATTERN,
                            pattern_name="Factory Pattern",
                            description=f"Function '{node.name}' appears to implement a factory pattern",
                            file_path=file_path,
                            line_number=node.lineno,
                            severity=Severity.INFO,
                            educational_context="Factory patterns provide an interface for creating objects "
                                              "without specifying their exact classes. This promotes loose "
                                              "coupling and makes code more flexible.",
                            suggestions=[
                                "Document the types of objects this factory can create",
                                "Consider using abstract base classes for return types",
                                "Ensure consistent error handling for invalid inputs"
                            ]
                        ))

    def _detect_observer_pattern(self, tree: ast.AST, file_path: str, content: str):
        """Detect observer pattern implementations"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_observers_list = False
                has_notify_method = False

                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and 'observer' in target.id.lower():
                                has_observers_list = True
                    elif isinstance(item, ast.FunctionDef) and 'notify' in item.name.lower():
                        has_notify_method = True

                if has_observers_list and has_notify_method:
                    self.results.append(AnalysisResult(
                        pattern_type=PatternType.DESIGN_PATTERN,
                        pattern_name="Observer Pattern",
                        description=f"Class '{node.name}' implements the Observer pattern",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=Severity.INFO,
                        educational_context="The Observer pattern defines a one-to-many dependency "
                                          "between objects so that when one object changes state, "
                                          "all dependents are notified automatically.",
                        suggestions=[
                            "Ensure observers are properly removed to prevent memory leaks",
                            "Consider weak references for observer storage",
                            "Handle exceptions in observer notifications gracefully"
                        ]
                    ))

    def _detect_long_methods(self, tree: ast.AST, file_path: str, content: str):
        """Detect methods that are too long"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 10

                if lines > 50:  # Configurable threshold
                    self.results.append(AnalysisResult(
                        pattern_type=PatternType.CODE_SMELL,
                        pattern_name="Long Method",
                        description=f"Method '{node.name}' is {lines} lines long",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=Severity.MEDIUM,
                        educational_context="Long methods are harder to understand, test, and maintain. "
                                          "They often violate the Single Responsibility Principle.",
                        suggestions=[
                            "Extract smaller methods with clear responsibilities",
                            "Look for logical groupings of statements to extract",
                            "Consider if the method is doing too many things"
                        ]
                    ))

    def _detect_large_classes(self, tree: ast.AST, file_path: str, content: str):
        """Detect classes that are too large"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = sum(1 for item in node.body if isinstance(item, ast.FunctionDef))
                lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 10

                if method_count > 20 or lines > 500:
                    self.results.append(AnalysisResult(
                        pattern_type=PatternType.CODE_SMELL,
                        pattern_name="Large Class",
                        description=f"Class '{node.name}' has {method_count} methods and {lines} lines",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=Severity.MEDIUM,
                        educational_context="Large classes often have too many responsibilities "
                                          "and become difficult to understand and maintain.",
                        suggestions=[
                            "Consider breaking into smaller, focused classes",
                            "Look for cohesive groups of methods to extract",
                            "Apply the Single Responsibility Principle"
                        ]
                    ))

    def _detect_duplicate_code(self, tree: ast.AST, file_path: str, content: str):
        """Detect potential code duplication (simplified)"""
        lines = content.split('\n')
        line_hashes = {}

        for i, line in enumerate(lines):
            stripped = line.strip()
            if len(stripped) > 10 and not stripped.startswith('#'):  # Ignore short lines and comments
                if stripped in line_hashes:
                    self.results.append(AnalysisResult(
                        pattern_type=PatternType.CODE_SMELL,
                        pattern_name="Duplicate Code",
                        description="Potential duplicate line detected",
                        file_path=file_path,
                        line_number=i + 1,
                        severity=Severity.LOW,
                        educational_context="Code duplication leads to maintenance issues. "
                                          "When bugs are fixed in one place, they may remain in copies.",
                        suggestions=[
                            "Extract common code into functions",
                            "Use parameterization to handle variations",
                            "Consider inheritance or composition patterns"
                        ]
                    ))
                line_hashes[stripped] = i + 1

    def _detect_magic_numbers(self, tree: ast.AST, file_path: str, content: str):
        """Detect magic numbers in code"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Ignore common "safe" numbers
                if node.value not in {0, 1, -1, 2, 10, 100}:
                    self.results.append(AnalysisResult(
                        pattern_type=PatternType.CODE_SMELL,
                        pattern_name="Magic Number",
                        description=f"Magic number '{node.value}' found",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=Severity.LOW,
                        educational_context="Magic numbers make code harder to understand and maintain. "
                                          "Their meaning is not clear from context.",
                        suggestions=[
                            "Replace with named constants",
                            "Add comments explaining the number's significance",
                            "Consider configuration or constants module"
                        ]
                    ))

    def _detect_god_objects(self, tree: ast.AST, file_path: str, content: str):
        """Detect potential God objects (classes that do too much)"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                import_count = 0
                method_count = sum(1 for item in node.body if isinstance(item, ast.FunctionDef))

                # Count different types of operations
                has_file_ops = False
                has_network_ops = False
                has_db_ops = False
                has_ui_ops = False

                for item in ast.walk(node):
                    if isinstance(item, ast.Name):
                        name = item.id.lower()
                        if any(x in name for x in ['file', 'open', 'write', 'read']):
                            has_file_ops = True
                        elif any(x in name for x in ['request', 'http', 'url']):
                            has_network_ops = True
                        elif any(x in name for x in ['sql', 'query', 'database']):
                            has_db_ops = True
                        elif any(x in name for x in ['render', 'display', 'view']):
                            has_ui_ops = True

                responsibility_count = sum([has_file_ops, has_network_ops, has_db_ops, has_ui_ops])

                if method_count > 15 and responsibility_count > 2:
                    self.results.append(AnalysisResult(
                        pattern_type=PatternType.ANTI_PATTERN,
                        pattern_name="God Object",
                        description=f"Class '{node.name}' appears to have too many responsibilities",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=Severity.HIGH,
                        educational_context="God objects violate the Single Responsibility Principle "
                                          "by handling too many different concerns, making them "
                                          "difficult to test and maintain.",
                        suggestions=[
                            "Split into smaller, focused classes",
                            "Use composition to delegate responsibilities",
                            "Apply domain-driven design principles"
                        ]
                    ))

    def _detect_feature_envy(self, tree: ast.AST, file_path: str, content: str):
        """Detect feature envy - methods that seem more interested in other classes"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                external_calls = 0
                self_calls = 0

                for item in ast.walk(node):
                    if isinstance(item, ast.Attribute):
                        if isinstance(item.value, ast.Name) and item.value.id == 'self':
                            self_calls += 1
                        else:
                            external_calls += 1

                if external_calls > 5 and external_calls > self_calls * 2:
                    self.results.append(AnalysisResult(
                        pattern_type=PatternType.CODE_SMELL,
                        pattern_name="Feature Envy",
                        description=f"Method '{node.name}' seems more interested in other objects",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=Severity.MEDIUM,
                        educational_context="Feature envy occurs when a method uses more features "
                                          "of another class than its own, suggesting it might "
                                          "belong in that other class.",
                        suggestions=[
                            "Consider moving method to the class it envies",
                            "Extract method parameters to reduce dependencies",
                            "Use dependency injection to improve structure"
                        ]
                    ))


def format_analysis_report(results: List[AnalysisResult]) -> str:
    """
    Format analysis results into a readable report.

    Args:
        results: List of analysis results to format

    Returns:
        Formatted report as a string
    """
    if not results:
        return "✅ No issues found! Code looks clean."

    # Group results by severity
    by_severity = {}
    for result in results:
        if result.severity not in by_severity:
            by_severity[result.severity] = []
        by_severity[result.severity].append(result)

    report = ["🔍 CodeMentor Analysis Report", "=" * 40, ""]

    # Summary
    total_issues = len(results)
    report.append(f"📊 Found {total_issues} items of interest:")
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
        count = len(by_severity.get(severity, []))
        if count > 0:
            emoji = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "⚡", "LOW": "💡", "INFO": "ℹ️"}[severity.name]
            report.append(f"  {emoji} {severity.name}: {count}")

    report.extend(["", "📋 Detailed Findings:", "-" * 20])

    # Detailed results
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
        if severity not in by_severity:
            continue

        for result in by_severity[severity]:
            report.extend([
                f"",
                f"🔸 {result.pattern_name} ({result.pattern_type.value})",
                f"   📁 {result.file_path}:{result.line_number}",
                f"   📝 {result.description}",
                f"   🎓 {result.educational_context}",
                f"   💡 Suggestions:"
            ])

            for suggestion in result.suggestions:
                report.append(f"      • {suggestion}")

    return "\n".join(report)


if __name__ == "__main__":
    import sys

    analyzer = CodeAnalyzer()

    if len(sys.argv) != 2:
        print("Usage: python code_analyzer.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isfile(target):
        results = analyzer.analyze_file(target)
    elif os.path.isdir(target):
        results = analyzer.analyze_directory(target)
    else:
        print(f"Error: '{target}' is not a valid file or directory")
        sys.exit(1)

    print(format_analysis_report(results))