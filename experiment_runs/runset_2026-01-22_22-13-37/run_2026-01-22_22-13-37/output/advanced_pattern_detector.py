#!/usr/bin/env python3
"""
Advanced Pattern Detection Engine

This module extends the basic pattern detection with more sophisticated
architectural pattern recognition, including:
- Design patterns (Singleton, Factory, Observer, etc.)
- Code smells and anti-patterns
- Performance patterns
- Security patterns
- Testing patterns
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter


@dataclass
class PatternMatch:
    """Represents a detected pattern match."""
    pattern_name: str
    description: str
    files: List[Path]
    confidence: float
    category: str  # 'design_pattern', 'anti_pattern', 'code_smell', 'security', 'performance'
    severity: str  # 'low', 'medium', 'high', 'critical'
    suggestions: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)


class AdvancedPatternDetector:
    """Advanced pattern detection with sophisticated analysis capabilities."""

    def __init__(self):
        self.pattern_matchers = {
            'singleton': self._detect_singleton_pattern,
            'factory': self._detect_factory_pattern,
            'observer': self._detect_observer_pattern,
            'strategy': self._detect_strategy_pattern,
            'dead_code': self._detect_dead_code,
            'long_parameter_list': self._detect_long_parameter_lists,
            'feature_envy': self._detect_feature_envy,
            'data_class': self._detect_data_classes,
            'large_class': self._detect_large_classes,
            'duplicate_code': self._detect_duplicate_code,
            'magic_numbers': self._detect_magic_numbers,
            'security_issues': self._detect_security_issues,
            'performance_issues': self._detect_performance_issues,
            'test_patterns': self._detect_test_patterns
        }

    def detect_all_patterns(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Run all pattern detection algorithms on the codebase."""
        all_patterns = []

        for pattern_name, detector_func in self.pattern_matchers.items():
            try:
                patterns = detector_func(file_info)
                all_patterns.extend(patterns)
            except Exception as e:
                print(f"Warning: Pattern detector '{pattern_name}' failed: {e}")

        return sorted(all_patterns, key=lambda p: p.confidence, reverse=True)

    def _detect_singleton_pattern(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect Singleton design pattern implementations."""
        patterns = []

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            try:
                with open(path, 'r') as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Look for singleton indicators
                        has_instance_var = False
                        has_new_override = False

                        for class_node in node.body:
                            if isinstance(class_node, ast.Assign):
                                for target in class_node.targets:
                                    if isinstance(target, ast.Name) and target.id == '_instance':
                                        has_instance_var = True
                            elif isinstance(class_node, ast.FunctionDef) and class_node.name == '__new__':
                                has_new_override = True

                        if has_instance_var and has_new_override:
                            patterns.append(PatternMatch(
                                pattern_name="Singleton Pattern",
                                description=f"Class {node.name} implements Singleton pattern",
                                files=[path],
                                confidence=0.8,
                                category='design_pattern',
                                severity='low',
                                suggestions=[
                                    "Consider using dependency injection instead of Singleton",
                                    "Ensure thread-safety if used in multithreaded environment",
                                    "Make sure the Singleton is truly necessary"
                                ],
                                evidence={'class_name': node.name, 'has_instance_var': True, 'has_new_override': True}
                            ))

            except (SyntaxError, UnicodeDecodeError):
                continue

        return patterns

    def _detect_factory_pattern(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect Factory design pattern implementations."""
        patterns = []

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            # Look for common factory pattern indicators
            factory_indicators = ['create_', 'make_', 'build_', 'get_instance', 'factory']

            factory_methods = []
            for func_name in info.functions:
                if any(indicator in func_name.lower() for indicator in factory_indicators):
                    factory_methods.append(func_name)

            if factory_methods:
                patterns.append(PatternMatch(
                    pattern_name="Factory Pattern",
                    description=f"Potential Factory pattern methods detected: {', '.join(factory_methods)}",
                    files=[path],
                    confidence=0.6,
                    category='design_pattern',
                    severity='low',
                    suggestions=[
                        "Ensure factory methods follow consistent naming conventions",
                        "Consider using Abstract Factory for complex object creation",
                        "Document the creation logic for maintainability"
                    ],
                    evidence={'factory_methods': factory_methods}
                ))

        return patterns

    def _detect_observer_pattern(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect Observer design pattern implementations."""
        patterns = []

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            # Look for observer pattern indicators
            observer_indicators = [
                'add_observer', 'remove_observer', 'notify', 'subscribe', 'unsubscribe',
                'addEventListener', 'on_', 'emit', 'trigger'
            ]

            observer_methods = []
            for func_name in info.functions:
                if any(indicator in func_name.lower() for indicator in observer_indicators):
                    observer_methods.append(func_name)

            if len(observer_methods) >= 2:  # Need at least add/remove or subscribe/notify
                patterns.append(PatternMatch(
                    pattern_name="Observer Pattern",
                    description=f"Observer pattern methods detected: {', '.join(observer_methods)}",
                    files=[path],
                    confidence=0.7,
                    category='design_pattern',
                    severity='low',
                    suggestions=[
                        "Ensure proper cleanup of observers to prevent memory leaks",
                        "Consider using weak references for observers",
                        "Implement error handling in notification methods"
                    ],
                    evidence={'observer_methods': observer_methods}
                ))

        return patterns

    def _detect_strategy_pattern(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect Strategy design pattern implementations."""
        patterns = []

        # Look for strategy pattern across multiple files
        strategy_files = []

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            # Strategy pattern indicators in file names and class names
            if any(indicator in str(path).lower() for indicator in ['strategy', 'handler', 'processor']):
                strategy_files.append(path)
                continue

            # Look for strategy-like class hierarchies
            if len(info.classes) > 0:
                for class_name in info.classes:
                    if any(indicator in class_name.lower() for indicator in ['strategy', 'handler', 'processor']):
                        strategy_files.append(path)
                        break

        if len(strategy_files) >= 2:
            patterns.append(PatternMatch(
                pattern_name="Strategy Pattern",
                description=f"Strategy pattern implementation detected across {len(strategy_files)} files",
                files=strategy_files,
                confidence=0.6,
                category='design_pattern',
                severity='low',
                suggestions=[
                    "Ensure all strategies implement a common interface",
                    "Consider using dependency injection for strategy selection",
                    "Document when to use each strategy variant"
                ],
                evidence={'strategy_files': [str(f) for f in strategy_files]}
            ))

        return patterns

    def _detect_dead_code(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect potentially dead/unused code."""
        patterns = []

        # Simple dead code detection - look for unused imports and functions
        all_function_names = set()
        all_class_names = set()

        # Collect all function and class names
        for info in file_info.values():
            all_function_names.update(info.functions)
            all_class_names.update(info.classes)

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            try:
                with open(path, 'r') as f:
                    content = f.read()

                # Look for functions that are never called
                unused_functions = []
                for func_name in info.functions:
                    # Simple heuristic - if function is not referenced elsewhere in the codebase
                    if func_name.count('_') == 0:  # Skip private functions
                        call_pattern = f'{func_name}\\('
                        if len(re.findall(call_pattern, content)) <= 1:  # Only definition, no calls
                            unused_functions.append(func_name)

                if unused_functions:
                    patterns.append(PatternMatch(
                        pattern_name="Dead Code",
                        description=f"Potentially unused functions: {', '.join(unused_functions)}",
                        files=[path],
                        confidence=0.5,
                        category='code_smell',
                        severity='medium',
                        suggestions=[
                            "Review and remove unused functions",
                            "Add unit tests to verify function usage",
                            "Consider marking internal functions as private with underscore prefix"
                        ],
                        evidence={'unused_functions': unused_functions}
                    ))

            except (SyntaxError, UnicodeDecodeError):
                continue

        return patterns

    def _detect_long_parameter_lists(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect functions with too many parameters."""
        patterns = []

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            try:
                with open(path, 'r') as f:
                    content = f.read()

                tree = ast.parse(content)
                long_param_functions = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        param_count = len(node.args.args) + len(node.args.posonlyargs) + len(node.args.kwonlyargs)
                        if node.args.vararg:
                            param_count += 1
                        if node.args.kwarg:
                            param_count += 1

                        if param_count > 5:  # Threshold for too many parameters
                            long_param_functions.append({
                                'name': node.name,
                                'param_count': param_count
                            })

                if long_param_functions:
                    func_descriptions = [f"{f['name']}({f['param_count']})" for f in long_param_functions]
                    patterns.append(PatternMatch(
                        pattern_name="Long Parameter List",
                        description=f"Functions with many parameters: {', '.join(func_descriptions)}",
                        files=[path],
                        confidence=0.8,
                        category='code_smell',
                        severity='medium',
                        suggestions=[
                            "Consider using parameter objects or dataclasses",
                            "Break down complex functions into smaller ones",
                            "Use keyword-only arguments for clarity",
                            "Consider using dependency injection"
                        ],
                        evidence={'long_param_functions': long_param_functions}
                    ))

            except (SyntaxError, UnicodeDecodeError):
                continue

        return patterns

    def _detect_feature_envy(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect feature envy code smell (method uses more of another class than its own)."""
        patterns = []

        # This is a simplified version - would need more sophisticated analysis
        for path, info in file_info.items():
            if info.language != 'python':
                continue

            # Look for excessive use of other modules
            if len(info.imports) > len(info.functions) + len(info.classes):
                patterns.append(PatternMatch(
                    pattern_name="Feature Envy",
                    description=f"File imports {len(info.imports)} modules but defines only {len(info.functions + info.classes)} items",
                    files=[path],
                    confidence=0.4,
                    category='code_smell',
                    severity='low',
                    suggestions=[
                        "Consider moving functionality closer to the data it operates on",
                        "Evaluate if some imports can be eliminated",
                        "Look for opportunities to create cohesive modules"
                    ],
                    evidence={
                        'import_count': len(info.imports),
                        'definition_count': len(info.functions) + len(info.classes)
                    }
                ))

        return patterns

    def _detect_data_classes(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect data classes (classes with mostly getters/setters)."""
        patterns = []

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            # Look for files that might be pure data containers
            getter_setter_indicators = ['get_', 'set_', '@property', '@setter']

            try:
                with open(path, 'r') as f:
                    content = f.read()

                if any(indicator in content for indicator in getter_setter_indicators):
                    if len(info.classes) > 0:
                        patterns.append(PatternMatch(
                            pattern_name="Data Class",
                            description=f"Potential data class detected with getter/setter methods",
                            files=[path],
                            confidence=0.6,
                            category='design_pattern',
                            severity='low',
                            suggestions=[
                                "Consider using @dataclass decorator for simple data containers",
                                "Evaluate if the class needs behavior beyond data storage",
                                "Use properties instead of explicit getters/setters where appropriate"
                            ],
                            evidence={'classes': info.classes}
                        ))

            except (UnicodeDecodeError):
                continue

        return patterns

    def _detect_large_classes(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect overly large classes."""
        patterns = []

        for path, info in file_info.items():
            if info.lines > 300 and len(info.classes) > 0:
                patterns.append(PatternMatch(
                    pattern_name="Large Class",
                    description=f"Large class detected ({info.lines} lines) - consider breaking into smaller classes",
                    files=[path],
                    confidence=0.7,
                    category='code_smell',
                    severity='medium',
                    suggestions=[
                        "Apply Single Responsibility Principle",
                        "Extract related functionality into separate classes",
                        "Consider using composition over inheritance",
                        "Identify and extract utility methods"
                    ],
                    evidence={'lines': info.lines, 'classes': info.classes}
                ))

        return patterns

    def _detect_duplicate_code(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect potential code duplication."""
        patterns = []

        # Simple duplication detection based on function names
        function_names = Counter()

        for path, info in file_info.items():
            for func_name in info.functions:
                function_names[func_name] += 1

        duplicated_names = [name for name, count in function_names.items() if count > 1]

        if duplicated_names:
            patterns.append(PatternMatch(
                pattern_name="Duplicate Code",
                description=f"Functions with identical names found: {', '.join(duplicated_names[:5])}",
                files=list(file_info.keys()),
                confidence=0.4,
                category='code_smell',
                severity='medium',
                suggestions=[
                    "Review functions with identical names for code duplication",
                    "Extract common functionality into shared modules",
                    "Consider using inheritance or composition to eliminate duplication",
                    "Implement consistent naming conventions"
                ],
                evidence={'duplicated_names': duplicated_names}
            ))

        return patterns

    def _detect_magic_numbers(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect magic numbers in code."""
        patterns = []

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            try:
                with open(path, 'r') as f:
                    content = f.read()

                # Look for numeric literals (excluding common ones like 0, 1, -1)
                magic_numbers = re.findall(r'\b(?!(?:0|1|-1|100|1000)\b)\d{2,}\b', content)

                if len(magic_numbers) > 3:  # Threshold for concern
                    patterns.append(PatternMatch(
                        pattern_name="Magic Numbers",
                        description=f"Multiple magic numbers detected: {len(magic_numbers)} instances",
                        files=[path],
                        confidence=0.6,
                        category='code_smell',
                        severity='low',
                        suggestions=[
                            "Replace magic numbers with named constants",
                            "Use enums for related magic numbers",
                            "Add comments explaining the significance of numbers",
                            "Consider using configuration files for adjustable values"
                        ],
                        evidence={'magic_numbers': magic_numbers[:10]}  # Show first 10
                    ))

            except (UnicodeDecodeError):
                continue

        return patterns

    def _detect_security_issues(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect potential security issues."""
        patterns = []

        security_red_flags = [
            ('eval(', 'Code injection risk'),
            ('exec(', 'Code injection risk'),
            ('os.system(', 'Command injection risk'),
            ('shell=True', 'Shell injection risk'),
            ('pickle.loads(', 'Deserialization risk'),
            ('input(', 'User input without validation'),
            ('raw_input(', 'User input without validation'),
            ('sql', 'Potential SQL injection')
        ]

        for path, info in file_info.items():
            try:
                with open(path, 'r') as f:
                    content = f.read()

                security_issues = []
                for pattern, description in security_red_flags:
                    if pattern in content.lower():
                        security_issues.append(description)

                if security_issues:
                    patterns.append(PatternMatch(
                        pattern_name="Security Issues",
                        description=f"Potential security risks detected: {', '.join(set(security_issues))}",
                        files=[path],
                        confidence=0.7,
                        category='security',
                        severity='high',
                        suggestions=[
                            "Validate and sanitize all user inputs",
                            "Use parameterized queries for database operations",
                            "Avoid using eval() and exec() with untrusted input",
                            "Use subprocess with shell=False when possible",
                            "Consider using safer serialization formats than pickle"
                        ],
                        evidence={'security_issues': security_issues}
                    ))

            except (UnicodeDecodeError):
                continue

        return patterns

    def _detect_performance_issues(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect potential performance issues."""
        patterns = []

        performance_red_flags = [
            (r'for.*in.*range\(len\(', 'Use enumerate instead of range(len())'),
            (r'\.append\(.*\)\s*$', 'Consider list comprehension'),
            (r'time\.sleep\(', 'Blocking sleep calls'),
            (r'\.sort\(\)\s*$', 'In-place sorting - consider sorted()'),
        ]

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            try:
                with open(path, 'r') as f:
                    content = f.read()

                performance_issues = []
                for pattern, description in performance_red_flags:
                    if re.search(pattern, content, re.MULTILINE):
                        performance_issues.append(description)

                if performance_issues:
                    patterns.append(PatternMatch(
                        pattern_name="Performance Issues",
                        description=f"Performance concerns: {', '.join(set(performance_issues))}",
                        files=[path],
                        confidence=0.5,
                        category='performance',
                        severity='medium',
                        suggestions=[
                            "Use list comprehensions where appropriate",
                            "Consider using enumerate() instead of range(len())",
                            "Evaluate if blocking operations can be made async",
                            "Profile code to identify actual bottlenecks"
                        ],
                        evidence={'performance_issues': performance_issues}
                    ))

            except (UnicodeDecodeError):
                continue

        return patterns

    def _detect_test_patterns(self, file_info: Dict[Path, Any]) -> List[PatternMatch]:
        """Detect testing patterns and issues."""
        patterns = []

        test_files = []
        test_indicators = ['test_', '_test', 'spec_', '_spec', 'tests']

        for path, info in file_info.items():
            if any(indicator in str(path).lower() for indicator in test_indicators):
                test_files.append(path)

        if not test_files:
            patterns.append(PatternMatch(
                pattern_name="Missing Tests",
                description="No test files detected in the codebase",
                files=list(file_info.keys()),
                confidence=0.8,
                category='code_smell',
                severity='high',
                suggestions=[
                    "Add unit tests to improve code reliability",
                    "Consider using pytest or unittest framework",
                    "Aim for high test coverage of critical functionality",
                    "Implement integration and end-to-end tests"
                ],
                evidence={'test_files_found': 0}
            ))
        else:
            # Analyze test quality
            total_files = len(file_info)
            test_ratio = len(test_files) / total_files

            if test_ratio < 0.3:  # Less than 30% test files
                patterns.append(PatternMatch(
                    pattern_name="Low Test Coverage",
                    description=f"Only {len(test_files)} test files for {total_files} total files ({test_ratio:.1%})",
                    files=test_files,
                    confidence=0.7,
                    category='code_smell',
                    severity='medium',
                    suggestions=[
                        "Increase test coverage for better code reliability",
                        "Add tests for critical business logic",
                        "Consider test-driven development practices",
                        "Use code coverage tools to identify untested code"
                    ],
                    evidence={
                        'test_files': len(test_files),
                        'total_files': total_files,
                        'test_ratio': test_ratio
                    }
                ))

        return patterns


def main():
    """Example usage of the Advanced Pattern Detector."""
    import sys
    import json
    from pathlib import Path

    if len(sys.argv) != 2:
        print("Usage: python advanced_pattern_detector.py <path_to_codebase>")
        sys.exit(1)

    # This is a simplified example - in practice, you'd integrate with the main analyzer
    detector = AdvancedPatternDetector()

    # Mock file info for demonstration
    file_info = {}
    root_path = Path(sys.argv[1])

    for py_file in root_path.glob("**/*.py"):
        try:
            with open(py_file, 'r') as f:
                content = f.read()

            # Simple mock FileInfo object
            class MockFileInfo:
                def __init__(self):
                    self.language = 'python'
                    self.lines = len(content.splitlines())
                    self.functions = []
                    self.classes = []
                    self.imports = []

            file_info[py_file] = MockFileInfo()

        except Exception:
            continue

    patterns = detector.detect_all_patterns(file_info)

    print(f"\n=== Advanced Pattern Detection Results ===")
    print(f"Analyzed {len(file_info)} Python files")
    print(f"Found {len(patterns)} patterns\n")

    for pattern in patterns:
        severity_icon = {'low': '🟡', 'medium': '🟠', 'high': '🔴', 'critical': '⚡'}
        category_icon = {
            'design_pattern': '🏗️',
            'anti_pattern': '❌',
            'code_smell': '👃',
            'security': '🔒',
            'performance': '⚡'
        }

        print(f"{severity_icon.get(pattern.severity, '⚪')} {category_icon.get(pattern.category, '📋')} {pattern.pattern_name} ({pattern.confidence:.0%} confidence)")
        print(f"   {pattern.description}")
        print(f"   Files: {len(pattern.files)}")

        if pattern.suggestions:
            print(f"   💡 {pattern.suggestions[0]}")
        print()


if __name__ == "__main__":
    main()