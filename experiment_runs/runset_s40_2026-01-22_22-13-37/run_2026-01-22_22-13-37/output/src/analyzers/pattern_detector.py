"""
Pattern Detector - Identifies architectural patterns and anti-patterns

This module analyzes code structure to identify common design patterns,
anti-patterns, and architectural smells that could indicate areas for improvement.
"""

from typing import Dict, List, Any, Set
from dataclasses import dataclass
from pathlib import Path
import re
from enum import Enum

class PatternType(Enum):
    DESIGN_PATTERN = "design_pattern"
    ANTI_PATTERN = "anti_pattern"
    ARCHITECTURAL_SMELL = "architectural_smell"

@dataclass
class Pattern:
    """Represents a detected pattern or anti-pattern."""
    name: str
    pattern_type: PatternType
    confidence: float  # 0.0 to 1.0
    files: List[str]
    description: str
    impact: str  # "low", "medium", "high"
    recommendation: str

class PatternDetector:
    """
    Detects architectural patterns and anti-patterns in codebases.

    This analyzer identifies:
    - Common design patterns (Singleton, Factory, Observer, etc.)
    - Anti-patterns (God Object, Spaghetti Code, etc.)
    - Architectural smells (Circular Dependencies, Feature Envy, etc.)
    """

    def __init__(self):
        self.detected_patterns = []

    def detect_patterns(self, structure_analysis: Dict[str, Any]) -> List[Pattern]:
        """
        Detect patterns based on structure analysis results.

        Args:
            structure_analysis: Results from StructureAnalyzer

        Returns:
            List of detected patterns
        """
        self.detected_patterns = []
        files = structure_analysis['files']
        dependency_graph = structure_analysis['dependency_graph']
        layers = structure_analysis['layers']

        # Detect various pattern types
        self._detect_design_patterns(files)
        self._detect_anti_patterns(files, dependency_graph)
        self._detect_architectural_smells(files, dependency_graph, layers)

        return self.detected_patterns

    def _detect_design_patterns(self, files: Dict[str, Any]):
        """Detect common design patterns."""

        # Singleton Pattern Detection
        singleton_files = []
        for file_path, node in files.items():
            if self._is_singleton_pattern(node):
                singleton_files.append(file_path)

        if singleton_files:
            self.detected_patterns.append(Pattern(
                name="Singleton Pattern",
                pattern_type=PatternType.DESIGN_PATTERN,
                confidence=0.8,
                files=singleton_files,
                description="Classes that implement the Singleton pattern to ensure only one instance exists.",
                impact="medium",
                recommendation="Consider dependency injection as an alternative for better testability."
            ))

        # Factory Pattern Detection
        factory_files = []
        for file_path, node in files.items():
            if self._is_factory_pattern(node):
                factory_files.append(file_path)

        if factory_files:
            self.detected_patterns.append(Pattern(
                name="Factory Pattern",
                pattern_type=PatternType.DESIGN_PATTERN,
                confidence=0.7,
                files=factory_files,
                description="Classes that implement the Factory pattern for object creation.",
                impact="low",
                recommendation="Good pattern for managing object creation complexity."
            ))

        # Observer Pattern Detection
        observer_files = []
        for file_path, node in files.items():
            if self._is_observer_pattern(node):
                observer_files.append(file_path)

        if observer_files:
            self.detected_patterns.append(Pattern(
                name="Observer Pattern",
                pattern_type=PatternType.DESIGN_PATTERN,
                confidence=0.6,
                files=observer_files,
                description="Classes implementing event-driven communication patterns.",
                impact="low",
                recommendation="Consider using modern event systems or reactive programming libraries."
            ))

    def _detect_anti_patterns(self, files: Dict[str, Any], dependency_graph: Any):
        """Detect anti-patterns that indicate problematic code."""

        # God Object Detection
        god_objects = []
        for file_path, node in files.items():
            if self._is_god_object(node):
                god_objects.append(file_path)

        if god_objects:
            self.detected_patterns.append(Pattern(
                name="God Object",
                pattern_type=PatternType.ANTI_PATTERN,
                confidence=0.9,
                files=god_objects,
                description="Classes that are too large and handle too many responsibilities.",
                impact="high",
                recommendation="Break down these classes using Single Responsibility Principle. Extract related functionality into separate classes."
            ))

        # Circular Dependencies Detection
        circular_deps = self._detect_circular_dependencies(dependency_graph)
        if circular_deps:
            self.detected_patterns.append(Pattern(
                name="Circular Dependencies",
                pattern_type=PatternType.ANTI_PATTERN,
                confidence=0.95,
                files=circular_deps,
                description="Files that have circular import dependencies.",
                impact="high",
                recommendation="Refactor to eliminate circular dependencies. Consider dependency inversion or creating interface layers."
            ))

        # Dead Code Detection
        dead_code_files = []
        for file_path, node in files.items():
            if self._has_dead_code(node, dependency_graph):
                dead_code_files.append(file_path)

        if dead_code_files:
            self.detected_patterns.append(Pattern(
                name="Dead Code",
                pattern_type=PatternType.ANTI_PATTERN,
                confidence=0.7,
                files=dead_code_files,
                description="Files or functions that appear to be unused.",
                impact="medium",
                recommendation="Remove unused code to improve maintainability and reduce complexity."
            ))

    def _detect_architectural_smells(self, files: Dict[str, Any], dependency_graph: Any, layers: Dict[str, List[str]]):
        """Detect architectural smells."""

        # Feature Envy Detection
        feature_envy_files = []
        for file_path, node in files.items():
            if self._has_feature_envy(node):
                feature_envy_files.append(file_path)

        if feature_envy_files:
            self.detected_patterns.append(Pattern(
                name="Feature Envy",
                pattern_type=PatternType.ARCHITECTURAL_SMELL,
                confidence=0.6,
                files=feature_envy_files,
                description="Classes that seem more interested in other classes than in their own functionality.",
                impact="medium",
                recommendation="Consider moving methods to the classes they interact with most."
            ))

        # Layer Violations Detection
        layer_violations = self._detect_layer_violations(dependency_graph, layers)
        if layer_violations:
            self.detected_patterns.append(Pattern(
                name="Layer Violations",
                pattern_type=PatternType.ARCHITECTURAL_SMELL,
                confidence=0.8,
                files=layer_violations,
                description="Files that violate expected architectural layering.",
                impact="high",
                recommendation="Refactor to respect architectural boundaries. Data layer should not depend on presentation layer."
            ))

        # Shotgun Surgery Detection
        shotgun_surgery_files = []
        for file_path, node in files.items():
            if self._indicates_shotgun_surgery(node, files):
                shotgun_surgery_files.append(file_path)

        if shotgun_surgery_files:
            self.detected_patterns.append(Pattern(
                name="Shotgun Surgery",
                pattern_type=PatternType.ARCHITECTURAL_SMELL,
                confidence=0.7,
                files=shotgun_surgery_files,
                description="Changes that require modifications across many files.",
                impact="medium",
                recommendation="Consider consolidating related functionality or using more flexible design patterns."
            ))

    # Helper methods for pattern detection

    def _is_singleton_pattern(self, node) -> bool:
        """Check if a file implements the Singleton pattern."""
        # Look for singleton indicators
        singleton_indicators = [
            'instance',
            'getInstance',
            '__new__',
            '_instance',
            'singleton'
        ]

        # Check class and function names
        for class_name in node.classes:
            if any(indicator in class_name.lower() for indicator in singleton_indicators):
                return True

        for func_name in node.functions:
            if any(indicator in func_name.lower() for indicator in singleton_indicators):
                return True

        return False

    def _is_factory_pattern(self, node) -> bool:
        """Check if a file implements the Factory pattern."""
        factory_indicators = [
            'factory',
            'create',
            'builder',
            'make'
        ]

        # Check for factory-like naming patterns
        for class_name in node.classes:
            if any(indicator in class_name.lower() for indicator in factory_indicators):
                return True

        for func_name in node.functions:
            if any(indicator in func_name.lower() for indicator in factory_indicators):
                return True

        return False

    def _is_observer_pattern(self, node) -> bool:
        """Check if a file implements the Observer pattern."""
        observer_indicators = [
            'observer',
            'listener',
            'subscribe',
            'notify',
            'event',
            'emit',
            'dispatch'
        ]

        for class_name in node.classes:
            if any(indicator in class_name.lower() for indicator in observer_indicators):
                return True

        for func_name in node.functions:
            if any(indicator in func_name.lower() for indicator in observer_indicators):
                return True

        return False

    def _is_god_object(self, node) -> bool:
        """Check if a file represents a God Object."""
        # Heuristics for God Object detection
        god_object_threshold = {
            'lines_of_code': 500,
            'num_methods': 20,
            'num_classes': 5
        }

        return (
            node.lines_of_code > god_object_threshold['lines_of_code'] or
            len(node.functions) > god_object_threshold['num_methods'] or
            len(node.classes) > god_object_threshold['num_classes']
        )

    def _detect_circular_dependencies(self, dependency_graph) -> List[str]:
        """Detect circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        circular_files = []

        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                circular_files.extend(path[cycle_start:])
                return True

            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            # Check all dependencies
            for edge in dependency_graph.edges:
                if edge[0] == node:
                    if dfs(edge[1], path + [node]):
                        return True

            rec_stack.remove(node)
            return False

        for node in dependency_graph.nodes:
            if node not in visited:
                dfs(node, [])

        return list(set(circular_files))

    def _has_dead_code(self, node, dependency_graph) -> bool:
        """Check if a file appears to be dead code."""
        file_path = str(node.path)

        # Check if any other file imports from this one
        is_imported = any(edge[1] == file_path for edge in dependency_graph.edges)

        # If it's not imported and doesn't look like a main file, it might be dead
        is_main_file = (
            'main' in node.path.name.lower() or
            '__main__' in str(node.path) or
            'index' in node.path.name.lower() or
            'app' in node.path.name.lower()
        )

        return not is_imported and not is_main_file

    def _has_feature_envy(self, node) -> bool:
        """Check if a file exhibits Feature Envy."""
        # Simple heuristic: if a file imports many external modules but has few exports
        external_imports = len([imp for imp in node.imports if not imp.startswith('.')])
        own_exports = len(node.exports)

        return external_imports > 10 and own_exports < 3

    def _detect_layer_violations(self, dependency_graph, layers: Dict[str, List[str]]) -> List[str]:
        """Detect violations of architectural layering."""
        violations = []

        # Define expected layer hierarchy (lower layers shouldn't depend on higher ones)
        layer_hierarchy = ['data', 'business', 'presentation', 'utility']

        for edge in dependency_graph.edges:
            from_file, to_file = edge[0], edge[1]

            from_layer = None
            to_layer = None

            # Find which layers these files belong to
            for layer, files in layers.items():
                if from_file in files:
                    from_layer = layer
                if to_file in files:
                    to_layer = layer

            if from_layer and to_layer:
                from_level = layer_hierarchy.index(from_layer) if from_layer in layer_hierarchy else -1
                to_level = layer_hierarchy.index(to_layer) if to_layer in layer_hierarchy else -1

                # Check for violations (lower level depending on higher level)
                if from_level != -1 and to_level != -1 and from_level < to_level:
                    violations.extend([from_file, to_file])

        return list(set(violations))

    def _indicates_shotgun_surgery(self, node, all_files: Dict[str, Any]) -> bool:
        """Check if changes to this file would require many other changes."""
        # Heuristic: files that are imported by many others might indicate shotgun surgery
        file_path = str(node.path)
        import_count = 0

        for other_path, other_node in all_files.items():
            if file_path != other_path:
                # Check if other file imports this one (simplified check)
                relative_import = str(Path(file_path).stem)
                if relative_import in other_node.imports:
                    import_count += 1

        # If this file is imported by many others, changes here might require shotgun surgery
        return import_count > 5