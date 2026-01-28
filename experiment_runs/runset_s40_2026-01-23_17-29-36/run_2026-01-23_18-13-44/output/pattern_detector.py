"""
Advanced Pattern Detection Module

This module extends our collaborative code analyzer with sophisticated pattern detection
capabilities, including design pattern recognition, code smell detection, and
architectural analysis.

Built as part of Alice & Bob's collaborative code analysis project.
"""

import ast
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter
from pathlib import Path

@dataclass
class PatternResult:
    """Represents a detected pattern or code smell."""
    name: str
    description: str
    severity: str  # 'info', 'warning', 'error'
    location: str
    line_number: int
    confidence: float  # 0.0 to 1.0
    suggestion: str

@dataclass
class ArchitecturalMetrics:
    """Architectural quality metrics."""
    coupling_score: float
    cohesion_score: float
    abstraction_level: float
    design_pattern_count: int
    code_smell_count: int

class AdvancedPatternDetector:
    """
    Advanced pattern detection for code quality analysis.

    Detects design patterns, code smells, and architectural issues
    using AST analysis and heuristic pattern matching.
    """

    def __init__(self):
        self.patterns = []
        self.code_smells = []
        self.design_patterns = []

    def analyze_file(self, file_path: Path, code: str) -> Dict[str, Any]:
        """
        Perform comprehensive pattern analysis on a Python file.

        Args:
            file_path: Path to the file being analyzed
            code: Source code content

        Returns:
            Dictionary containing all detected patterns and metrics
        """
        try:
            tree = ast.parse(code)

            results = {
                'file_path': str(file_path),
                'design_patterns': self._detect_design_patterns(tree),
                'code_smells': self._detect_code_smells(tree, code),
                'architectural_issues': self._detect_architectural_issues(tree),
                'naming_conventions': self._analyze_naming_conventions(tree),
                'metrics': self._calculate_architectural_metrics(tree)
            }

            return results

        except SyntaxError as e:
            return {
                'error': f"Syntax error in file: {e}",
                'file_path': str(file_path)
            }

    def _detect_design_patterns(self, tree: ast.AST) -> List[PatternResult]:
        """Detect common design patterns in the code."""
        patterns = []

        # Singleton Pattern Detection
        patterns.extend(self._detect_singleton_pattern(tree))

        # Factory Pattern Detection
        patterns.extend(self._detect_factory_pattern(tree))

        # Observer Pattern Detection
        patterns.extend(self._detect_observer_pattern(tree))

        # Decorator Pattern Detection
        patterns.extend(self._detect_decorator_pattern(tree))

        return patterns

    def _detect_singleton_pattern(self, tree: ast.AST) -> List[PatternResult]:
        """Detect Singleton pattern implementations."""
        patterns = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for classic singleton indicators
                has_instance_var = False
                has_new_method = False

                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == '_instance':
                                has_instance_var = True

                    elif isinstance(item, ast.FunctionDef) and item.name == '__new__':
                        has_new_method = True

                if has_instance_var and has_new_method:
                    patterns.append(PatternResult(
                        name="Singleton Pattern",
                        description=f"Class '{node.name}' implements Singleton pattern",
                        severity="info",
                        location=f"Class {node.name}",
                        line_number=node.lineno,
                        confidence=0.85,
                        suggestion="Ensure thread safety if used in concurrent contexts"
                    ))

        return patterns

    def _detect_factory_pattern(self, tree: ast.AST) -> List[PatternResult]:
        """Detect Factory pattern implementations."""
        patterns = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for factory method indicators
                if (node.name.startswith('create_') or
                    node.name.startswith('make_') or
                    node.name.endswith('_factory')):

                    # Check if function returns different types based on parameters
                    has_conditional_return = False
                    return_count = 0

                    for child in ast.walk(node):
                        if isinstance(child, ast.Return):
                            return_count += 1
                        elif isinstance(child, ast.If):
                            has_conditional_return = True

                    if has_conditional_return and return_count > 1:
                        patterns.append(PatternResult(
                            name="Factory Pattern",
                            description=f"Function '{node.name}' appears to implement Factory pattern",
                            severity="info",
                            location=f"Function {node.name}",
                            line_number=node.lineno,
                            confidence=0.75,
                            suggestion="Consider documenting the types this factory can create"
                        ))

        return patterns

    def _detect_observer_pattern(self, tree: ast.AST) -> List[PatternResult]:
        """Detect Observer pattern implementations."""
        patterns = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_observers_list = False
                has_notify_method = False
                has_add_observer = False

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name in ['notify', 'notify_all', 'notify_observers']:
                            has_notify_method = True
                        elif item.name in ['add_observer', 'subscribe', 'register']:
                            has_add_observer = True

                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and 'observer' in target.id.lower():
                                has_observers_list = True

                if has_observers_list and has_notify_method and has_add_observer:
                    patterns.append(PatternResult(
                        name="Observer Pattern",
                        description=f"Class '{node.name}' implements Observer pattern",
                        severity="info",
                        location=f"Class {node.name}",
                        line_number=node.lineno,
                        confidence=0.90,
                        suggestion="Consider using weak references to prevent memory leaks"
                    ))

        return patterns

    def _detect_decorator_pattern(self, tree: ast.AST) -> List[PatternResult]:
        """Detect Decorator pattern implementations (not Python decorators)."""
        patterns = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for decorator pattern indicators
                has_component_attr = False
                has_delegating_methods = 0

                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and 'component' in target.id.lower():
                                has_component_attr = True

                    elif isinstance(item, ast.FunctionDef):
                        # Check if method delegates to component
                        for child in ast.walk(item):
                            if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name):
                                if 'component' in child.value.id.lower():
                                    has_delegating_methods += 1
                                    break

                if has_component_attr and has_delegating_methods >= 2:
                    patterns.append(PatternResult(
                        name="Decorator Pattern",
                        description=f"Class '{node.name}' may implement Decorator pattern",
                        severity="info",
                        location=f"Class {node.name}",
                        line_number=node.lineno,
                        confidence=0.70,
                        suggestion="Ensure consistent interface with decorated component"
                    ))

        return patterns

    def _detect_code_smells(self, tree: ast.AST, code: str) -> List[PatternResult]:
        """Detect various code smells and anti-patterns."""
        smells = []

        # Long Parameter Lists
        smells.extend(self._detect_long_parameter_lists(tree))

        # Large Classes
        smells.extend(self._detect_large_classes(tree))

        # Long Methods
        smells.extend(self._detect_long_methods(tree, code))

        # Duplicate Code
        smells.extend(self._detect_duplicate_code(tree))

        # Dead Code
        smells.extend(self._detect_dead_code(tree))

        return smells

    def _detect_long_parameter_lists(self, tree: ast.AST) -> List[PatternResult]:
        """Detect functions with too many parameters."""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                param_count = len(node.args.args) + len(node.args.kwonlyargs)
                if node.args.vararg:
                    param_count += 1
                if node.args.kwarg:
                    param_count += 1

                if param_count > 6:  # More than 6 parameters is suspicious
                    smells.append(PatternResult(
                        name="Long Parameter List",
                        description=f"Function '{node.name}' has {param_count} parameters",
                        severity="warning",
                        location=f"Function {node.name}",
                        line_number=node.lineno,
                        confidence=0.95,
                        suggestion="Consider using parameter objects or breaking down the function"
                    ))

        return smells

    def _detect_large_classes(self, tree: ast.AST) -> List[PatternResult]:
        """Detect classes that are too large."""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = sum(1 for item in node.body
                                 if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)))

                if method_count > 15:  # More than 15 methods suggests the class is too large
                    smells.append(PatternResult(
                        name="Large Class",
                        description=f"Class '{node.name}' has {method_count} methods",
                        severity="warning",
                        location=f"Class {node.name}",
                        line_number=node.lineno,
                        confidence=0.90,
                        suggestion="Consider breaking this class into smaller, focused classes"
                    ))

        return smells

    def _detect_long_methods(self, tree: ast.AST, code: str) -> List[PatternResult]:
        """Detect methods that are too long."""
        smells = []
        lines = code.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Calculate actual line count (excluding blank lines and comments)
                start_line = node.lineno - 1
                end_line = node.end_lineno - 1 if node.end_lineno else len(lines)

                actual_lines = 0
                for i in range(start_line, min(end_line + 1, len(lines))):
                    line = lines[i].strip()
                    if line and not line.startswith('#'):
                        actual_lines += 1

                if actual_lines > 50:  # More than 50 non-blank, non-comment lines
                    smells.append(PatternResult(
                        name="Long Method",
                        description=f"Method '{node.name}' has {actual_lines} lines of code",
                        severity="warning",
                        location=f"Function {node.name}",
                        line_number=node.lineno,
                        confidence=0.95,
                        suggestion="Consider breaking this method into smaller, focused methods"
                    ))

        return smells

    def _detect_duplicate_code(self, tree: ast.AST) -> List[PatternResult]:
        """Detect potential code duplication."""
        smells = []

        # Simple heuristic: look for similar function structures
        function_signatures = defaultdict(list)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Create a simple signature based on parameter names and structure
                param_names = [arg.arg for arg in node.args.args]
                signature = (len(param_names), tuple(sorted(param_names)))
                function_signatures[signature].append((node.name, node.lineno))

        for signature, functions in function_signatures.items():
            if len(functions) > 2:  # More than 2 functions with similar signatures
                func_names = [f[0] for f in functions]
                smells.append(PatternResult(
                    name="Potential Code Duplication",
                    description=f"Similar function signatures found: {', '.join(func_names)}",
                    severity="info",
                    location=f"Functions: {', '.join(func_names)}",
                    line_number=functions[0][1],
                    confidence=0.60,
                    suggestion="Review these functions for potential code duplication"
                ))

        return smells

    def _detect_dead_code(self, tree: ast.AST) -> List[PatternResult]:
        """Detect potentially unused code."""
        smells = []

        # Track defined and used names
        defined_names = set()
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not node.name.startswith('_'):  # Ignore private names
                    defined_names.add(node.name)

            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        unused_names = defined_names - used_names
        for name in unused_names:
            # Find the node to get line number
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node.name == name:
                        smells.append(PatternResult(
                            name="Potentially Dead Code",
                            description=f"'{name}' appears to be unused",
                            severity="info",
                            location=f"Definition: {name}",
                            line_number=node.lineno,
                            confidence=0.50,
                            suggestion="Verify if this code is actually unused and can be removed"
                        ))
                        break

        return smells

    def _detect_architectural_issues(self, tree: ast.AST) -> List[PatternResult]:
        """Detect architectural and design issues."""
        issues = []

        # Circular import detection would require multi-file analysis
        # For now, detect potential issues within a single file

        # God Class detection (already covered in large classes)
        # Feature Envy detection - methods that use more external data than internal
        issues.extend(self._detect_feature_envy(tree))

        return issues

    def _detect_feature_envy(self, tree: ast.AST) -> List[PatternResult]:
        """Detect methods that seem to belong in other classes."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for method in [item for item in node.body if isinstance(item, ast.FunctionDef)]:
                    if method.name.startswith('_'):
                        continue  # Skip private methods

                    # Count self vs external attribute accesses
                    self_accesses = 0
                    external_accesses = 0

                    for child in ast.walk(method):
                        if isinstance(child, ast.Attribute):
                            if isinstance(child.value, ast.Name) and child.value.id == 'self':
                                self_accesses += 1
                            else:
                                external_accesses += 1

                    if external_accesses > self_accesses * 2 and external_accesses > 3:
                        issues.append(PatternResult(
                            name="Feature Envy",
                            description=f"Method '{method.name}' in class '{node.name}' uses more external data than internal",
                            severity="warning",
                            location=f"Method {node.name}.{method.name}",
                            line_number=method.lineno,
                            confidence=0.65,
                            suggestion="Consider moving this method to the class it interacts with most"
                        ))

        return issues

    def _analyze_naming_conventions(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze adherence to Python naming conventions."""
        conventions = {
            'pep8_compliant': True,
            'violations': [],
            'stats': {
                'snake_case_functions': 0,
                'snake_case_variables': 0,
                'pascal_case_classes': 0,
                'upper_case_constants': 0
            }
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if self._is_pascal_case(node.name):
                    conventions['stats']['pascal_case_classes'] += 1
                else:
                    conventions['pep8_compliant'] = False
                    conventions['violations'].append(f"Class '{node.name}' should use PascalCase")

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith('_'):
                    continue  # Skip private functions
                if self._is_snake_case(node.name):
                    conventions['stats']['snake_case_functions'] += 1
                else:
                    conventions['pep8_compliant'] = False
                    conventions['violations'].append(f"Function '{node.name}' should use snake_case")

        return conventions

    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention."""
        return re.match(r'^[a-z_][a-z0-9_]*$', name) is not None

    def _is_pascal_case(self, name: str) -> bool:
        """Check if name follows PascalCase convention."""
        return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None

    def _calculate_architectural_metrics(self, tree: ast.AST) -> ArchitecturalMetrics:
        """Calculate high-level architectural quality metrics."""
        # Simplified metrics calculation
        total_classes = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))
        total_functions = sum(1 for _ in ast.walk(tree) if isinstance(_, (ast.FunctionDef, ast.AsyncFunctionDef)))

        # Coupling: rough estimate based on import statements and attribute accesses
        coupling_score = self._calculate_coupling_score(tree)

        # Cohesion: rough estimate based on method interactions within classes
        cohesion_score = self._calculate_cohesion_score(tree)

        # Abstraction level: ratio of abstract to concrete implementations
        abstraction_level = self._calculate_abstraction_level(tree)

        return ArchitecturalMetrics(
            coupling_score=coupling_score,
            cohesion_score=cohesion_score,
            abstraction_level=abstraction_level,
            design_pattern_count=0,  # Would be filled by pattern detection
            code_smell_count=0       # Would be filled by smell detection
        )

    def _calculate_coupling_score(self, tree: ast.AST) -> float:
        """Calculate a rough coupling score (0.0 = loose, 1.0 = tight)."""
        total_imports = sum(1 for _ in ast.walk(tree) if isinstance(_, (ast.Import, ast.ImportFrom)))
        total_attr_accesses = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.Attribute))
        total_nodes = sum(1 for _ in ast.walk(tree))

        if total_nodes == 0:
            return 0.0

        # Normalize to 0-1 range (this is a simplified heuristic)
        coupling_ratio = (total_imports + total_attr_accesses) / total_nodes
        return min(coupling_ratio * 10, 1.0)  # Scale and cap at 1.0

    def _calculate_cohesion_score(self, tree: ast.AST) -> float:
        """Calculate a rough cohesion score (0.0 = low, 1.0 = high)."""
        class_cohesion_scores = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Calculate how much methods interact with class attributes
                methods = [item for item in node.body if isinstance(item, ast.FunctionDef)]
                attributes = set()

                # Find class attributes
                for method in methods:
                    for child in ast.walk(method):
                        if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name):
                            if child.value.id == 'self':
                                attributes.add(child.attr)

                if not methods or not attributes:
                    continue

                # Calculate how many methods use each attribute
                attr_usage = defaultdict(int)
                for method in methods:
                    for child in ast.walk(method):
                        if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name):
                            if child.value.id == 'self' and child.attr in attributes:
                                attr_usage[child.attr] += 1

                # Calculate cohesion as average attribute usage across methods
                if attr_usage:
                    avg_usage = sum(attr_usage.values()) / len(attr_usage)
                    cohesion = min(avg_usage / len(methods), 1.0)
                    class_cohesion_scores.append(cohesion)

        return sum(class_cohesion_scores) / len(class_cohesion_scores) if class_cohesion_scores else 0.5

    def _calculate_abstraction_level(self, tree: ast.AST) -> float:
        """Calculate abstraction level (0.0 = concrete, 1.0 = abstract)."""
        total_classes = 0
        abstract_classes = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                total_classes += 1

                # Look for abstract indicators
                has_abstract_methods = False
                has_raise_not_implemented = False

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Check for abstract method decorators
                        for decorator in item.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                                has_abstract_methods = True

                        # Check for NotImplementedError
                        for child in ast.walk(item):
                            if isinstance(child, ast.Raise) and isinstance(child.exc, ast.Name):
                                if child.exc.id == 'NotImplementedError':
                                    has_raise_not_implemented = True

                if has_abstract_methods or has_raise_not_implemented:
                    abstract_classes += 1

        return abstract_classes / total_classes if total_classes > 0 else 0.0


def main():
    """Demonstration of the pattern detection capabilities."""
    detector = AdvancedPatternDetector()

    # Analyze this file itself!
    current_file = Path(__file__)
    if current_file.exists():
        with open(current_file, 'r') as f:
            code = f.read()

        print("🔍 Advanced Pattern Detection Demo")
        print("=" * 50)
        print(f"Analyzing: {current_file.name}")
        print()

        results = detector.analyze_file(current_file, code)

        # Display results
        print("📋 Design Patterns Found:")
        for pattern in results.get('design_patterns', []):
            print(f"  ✓ {pattern.name} (confidence: {pattern.confidence:.2f})")
            print(f"    {pattern.description}")
            print(f"    💡 {pattern.suggestion}")
            print()

        print("⚠️  Code Smells Detected:")
        for smell in results.get('code_smells', []):
            severity_icon = {"info": "ℹ️", "warning": "⚠️", "error": "🚫"}.get(smell.severity, "❓")
            print(f"  {severity_icon} {smell.name} (line {smell.line_number})")
            print(f"    {smell.description}")
            print(f"    💡 {smell.suggestion}")
            print()

        print("🏗️  Architectural Metrics:")
        metrics = results.get('metrics')
        if metrics:
            print(f"  Coupling Score: {metrics.coupling_score:.2f} (lower is better)")
            print(f"  Cohesion Score: {metrics.cohesion_score:.2f} (higher is better)")
            print(f"  Abstraction Level: {metrics.abstraction_level:.2f}")

        print("📝 Naming Convention Analysis:")
        naming = results.get('naming_conventions', {})
        if naming['pep8_compliant']:
            print("  ✅ All naming follows PEP 8 conventions")
        else:
            print("  ❌ PEP 8 violations found:")
            for violation in naming['violations']:
                print(f"    • {violation}")


if __name__ == '__main__':
    main()