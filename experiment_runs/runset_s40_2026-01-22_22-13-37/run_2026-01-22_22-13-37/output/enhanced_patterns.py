#!/usr/bin/env python3
"""
Enhanced Pattern Detection Module

Extends the base analyzer with additional architectural pattern detection
including design patterns, code smells, and best practices.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from collections import Counter

from codebase_analyzer import ArchitecturalPattern, FileInfo


@dataclass
class DesignPatternMatch:
    """Represents a detected design pattern."""
    pattern_name: str
    pattern_type: str  # "creational", "structural", "behavioral"
    files_involved: List[Path]
    confidence: float
    evidence: List[str]
    benefits: List[str]


class EnhancedPatternDetector:
    """Enhanced pattern detector with support for more sophisticated analysis."""

    def __init__(self):
        self.design_patterns = {}
        self.code_smells = {}

    def detect_all_patterns(self, file_info: Dict[Path, FileInfo],
                          dependency_graph: Dict[str, Set[str]]) -> List[ArchitecturalPattern]:
        """Detect all available patterns and anti-patterns."""
        patterns = []

        # Design patterns
        patterns.extend(self._detect_singleton_pattern(file_info))
        patterns.extend(self._detect_factory_pattern(file_info))
        patterns.extend(self._detect_observer_pattern(file_info))
        patterns.extend(self._detect_decorator_pattern(file_info))

        # Code smells and anti-patterns
        patterns.extend(self._detect_long_parameter_lists(file_info))
        patterns.extend(self._detect_dead_code(file_info))
        patterns.extend(self._detect_duplicate_code(file_info))
        patterns.extend(self._detect_feature_envy(file_info, dependency_graph))

        # Architecture patterns
        patterns.extend(self._detect_layered_architecture(file_info))
        patterns.extend(self._detect_repository_pattern(file_info))

        return patterns

    def _detect_singleton_pattern(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect Singleton design pattern."""
        patterns = []

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Look for singleton indicators
                        has_instance_variable = False
                        has_new_override = False

                        for child in node.body:
                            if isinstance(child, ast.FunctionDef):
                                if child.name == '__new__':
                                    has_new_override = True
                            elif isinstance(child, ast.Assign):
                                for target in child.targets:
                                    if isinstance(target, ast.Name) and target.id in ['_instance', 'instance']:
                                        has_instance_variable = True

                        if has_instance_variable and has_new_override:
                            patterns.append(ArchitecturalPattern(
                                name="Singleton Pattern",
                                description=f"Class {node.name} implements Singleton pattern",
                                files_involved=[path],
                                confidence=0.8,
                                is_antipattern=False,
                                suggestions=[
                                    "Ensure thread safety if used in multithreaded environment",
                                    "Consider using dependency injection instead for better testability"
                                ]
                            ))

            except (SyntaxError, FileNotFoundError):
                continue

        return patterns

    def _detect_factory_pattern(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect Factory design pattern."""
        patterns = []

        factory_keywords = ['factory', 'creator', 'builder']

        for path, info in file_info.items():
            path_lower = str(path).lower()
            has_factory_name = any(keyword in path_lower for keyword in factory_keywords)
            has_create_methods = any('create' in func.lower() for func in info.functions)

            if has_factory_name or (has_create_methods and len(info.classes) > 0):
                patterns.append(ArchitecturalPattern(
                    name="Factory Pattern",
                    description=f"File {path.name} appears to implement Factory pattern",
                    files_involved=[path],
                    confidence=0.6 if has_factory_name else 0.4,
                    is_antipattern=False,
                    suggestions=[
                        "Ensure proper abstraction between factory and products",
                        "Consider using Abstract Factory for multiple product families"
                    ]
                ))

        return patterns

    def _detect_observer_pattern(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect Observer design pattern."""
        patterns = []

        observer_indicators = ['observer', 'listener', 'subscriber', 'notify', 'update']

        for path, info in file_info.items():
            observer_score = 0

            # Check file name
            path_lower = str(path).lower()
            if any(indicator in path_lower for indicator in observer_indicators[:3]):
                observer_score += 2

            # Check function names
            function_matches = sum(1 for func in info.functions
                                 if any(indicator in func.lower() for indicator in observer_indicators))
            observer_score += min(function_matches, 3)

            if observer_score >= 3:
                patterns.append(ArchitecturalPattern(
                    name="Observer Pattern",
                    description=f"File {path.name} implements Observer pattern",
                    files_involved=[path],
                    confidence=min(observer_score / 5.0, 0.9),
                    is_antipattern=False,
                    suggestions=[
                        "Consider using weak references to prevent memory leaks",
                        "Implement proper error handling for observer notifications"
                    ]
                ))

        return patterns

    def _detect_decorator_pattern(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect Decorator design pattern."""
        patterns = []

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            decorator_indicators = ['decorator', 'wrapper', 'mixin']
            path_lower = str(path).lower()

            has_decorator_name = any(indicator in path_lower for indicator in decorator_indicators)
            has_wrapper_methods = any('wrap' in func.lower() for func in info.functions)

            if has_decorator_name or has_wrapper_methods:
                patterns.append(ArchitecturalPattern(
                    name="Decorator Pattern",
                    description=f"File {path.name} implements Decorator pattern",
                    files_involved=[path],
                    confidence=0.7 if has_decorator_name else 0.5,
                    is_antipattern=False,
                    suggestions=[
                        "Ensure decorators maintain the same interface",
                        "Consider performance impact of nested decorators"
                    ]
                ))

        return patterns

    def _detect_long_parameter_lists(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect long parameter list code smell."""
        patterns = []
        problematic_files = []

        for path, info in file_info.items():
            if info.language != 'python':
                continue

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)

                long_param_functions = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        param_count = len(node.args.args)
                        if hasattr(node.args, 'posonlyargs'):
                            param_count += len(node.args.posonlyargs or [])
                        if hasattr(node.args, 'kwonlyargs'):
                            param_count += len(node.args.kwonlyargs or [])

                        if param_count > 5:  # Threshold for "too many parameters"
                            long_param_functions.append(f"{node.name} ({param_count} params)")

                if long_param_functions:
                    problematic_files.append(path)
                    patterns.append(ArchitecturalPattern(
                        name="Long Parameter List",
                        description=f"Functions in {path.name} have too many parameters: {', '.join(long_param_functions)}",
                        files_involved=[path],
                        confidence=0.9,
                        is_antipattern=True,
                        suggestions=[
                            "Consider using parameter objects or configuration classes",
                            "Break large functions into smaller, focused functions",
                            "Use dependency injection to reduce parameter passing"
                        ]
                    ))

            except (SyntaxError, FileNotFoundError):
                continue

        return patterns

    def _detect_dead_code(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect potential dead code."""
        patterns = []

        # Simple heuristic: functions/classes that are never referenced
        all_names = set()
        all_references = set()

        # First pass: collect all defined names
        for path, info in file_info.items():
            all_names.update(info.functions)
            all_names.update(info.classes)

        # Second pass: find references (simplified)
        for path, info in file_info.items():
            if info.language != 'python':
                continue

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Look for function/class calls
                    for name in all_names:
                        if name in content and f"def {name}" not in content and f"class {name}" not in content:
                            all_references.add(name)

            except FileNotFoundError:
                continue

        # Find potentially unused names
        potentially_unused = all_names - all_references

        if potentially_unused and len(potentially_unused) > 2:
            patterns.append(ArchitecturalPattern(
                name="Potential Dead Code",
                description=f"Found {len(potentially_unused)} potentially unused functions/classes",
                files_involved=list(file_info.keys())[:3],  # Sample of files
                confidence=0.5,  # Low confidence due to simplified analysis
                is_antipattern=True,
                suggestions=[
                    "Review and remove unused code to improve maintainability",
                    "Consider using code coverage tools to identify truly dead code",
                    "Document public APIs that might be used externally"
                ]
            ))

        return patterns

    def _detect_duplicate_code(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect potential code duplication."""
        patterns = []

        # Group files by similar function signatures
        function_signatures = defaultdict(list)

        for path, info in file_info.items():
            signature = tuple(sorted(info.functions))
            if len(signature) > 2:  # Only consider files with multiple functions
                function_signatures[signature].append(path)

        # Find groups with similar signatures
        duplicates = {sig: paths for sig, paths in function_signatures.items() if len(paths) > 1}

        if duplicates:
            for signature, paths in list(duplicates.items())[:3]:  # Limit to first 3 groups
                patterns.append(ArchitecturalPattern(
                    name="Potential Code Duplication",
                    description=f"Files {[p.name for p in paths]} have similar function signatures",
                    files_involved=paths,
                    confidence=0.6,
                    is_antipattern=True,
                    suggestions=[
                        "Extract common functionality into shared modules",
                        "Consider creating base classes or mixins",
                        "Use composition over inheritance where appropriate"
                    ]
                ))

        return patterns

    def _detect_feature_envy(self, file_info: Dict[Path, FileInfo],
                           dependency_graph: Dict[str, Set[str]]) -> List[ArchitecturalPattern]:
        """Detect feature envy code smell."""
        patterns = []

        # Files that import a lot from other modules might have feature envy
        for path, info in file_info.items():
            if len(info.imports) > 10:  # Threshold for "too many imports"
                # Count imports from internal modules
                internal_imports = sum(1 for imp in info.imports
                                     if any(str(other_path).replace('.py', '').split('/')[-1] in imp
                                           for other_path in file_info.keys()))

                if internal_imports > 5:
                    patterns.append(ArchitecturalPattern(
                        name="Feature Envy",
                        description=f"File {path.name} has excessive dependencies on other internal modules",
                        files_involved=[path],
                        confidence=0.7,
                        is_antipattern=True,
                        suggestions=[
                            "Consider moving functionality closer to the data it operates on",
                            "Review class responsibilities and redistribute methods",
                            "Use dependency injection to reduce coupling"
                        ]
                    ))

        return patterns

    def _detect_layered_architecture(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect layered architecture pattern."""
        patterns = []

        # Look for typical layer names
        layer_indicators = {
            'presentation': ['view', 'ui', 'web', 'api', 'controller'],
            'business': ['service', 'logic', 'domain', 'business'],
            'data': ['repository', 'dao', 'model', 'data', 'persistence']
        }

        detected_layers = {layer: [] for layer in layer_indicators}

        for path, info in file_info.items():
            path_lower = str(path).lower()

            for layer, indicators in layer_indicators.items():
                if any(indicator in path_lower for indicator in indicators):
                    detected_layers[layer].append(path)

        # If we have files in at least 2 layers, suggest layered architecture
        non_empty_layers = sum(1 for files in detected_layers.values() if files)

        if non_empty_layers >= 2:
            all_layer_files = sum(detected_layers.values(), [])
            patterns.append(ArchitecturalPattern(
                name="Layered Architecture",
                description=f"Codebase shows evidence of layered architecture with {non_empty_layers} layers",
                files_involved=all_layer_files,
                confidence=min(non_empty_layers / 3.0, 0.8),
                is_antipattern=False,
                suggestions=[
                    "Ensure dependencies flow in one direction (downward)",
                    "Keep layer responsibilities clearly separated",
                    "Consider using interfaces to decouple layers"
                ]
            ))

        return patterns

    def _detect_repository_pattern(self, file_info: Dict[Path, FileInfo]) -> List[ArchitecturalPattern]:
        """Detect Repository pattern implementation."""
        patterns = []

        repository_files = []
        for path, info in file_info.items():
            path_lower = str(path).lower()

            # Check for repository indicators
            has_repo_name = 'repository' in path_lower or 'repo' in path_lower
            has_crud_methods = any(method.lower() in ['save', 'find', 'delete', 'update', 'get', 'create']
                                 for method in info.functions)
            has_repo_classes = any('repository' in cls.lower() for cls in info.classes)

            if has_repo_name or has_repo_classes or (has_crud_methods and len(info.functions) > 3):
                repository_files.append(path)

        if repository_files:
            patterns.append(ArchitecturalPattern(
                name="Repository Pattern",
                description=f"Found {len(repository_files)} files implementing Repository pattern",
                files_involved=repository_files,
                confidence=0.7,
                is_antipattern=False,
                suggestions=[
                    "Ensure repositories abstract database access properly",
                    "Consider using generic repository interfaces",
                    "Keep business logic out of repositories"
                ]
            ))

        return patterns


# Make defaultdict available
from collections import defaultdict