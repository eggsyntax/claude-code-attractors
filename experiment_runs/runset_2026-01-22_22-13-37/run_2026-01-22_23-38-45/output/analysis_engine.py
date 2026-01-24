"""
CodeMentor Analysis Engine

A sophisticated code analysis system that detects architectural patterns,
evaluates code quality, and provides educational context for developers.

This engine forms the intelligence core of the CodeMentor collaborative
code review assistant.
"""

import ast
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PatternType(Enum):
    """Types of architectural patterns the engine can detect."""
    SINGLETON = "singleton"
    FACTORY = "factory"
    OBSERVER = "observer"
    DECORATOR = "decorator"
    STRATEGY = "strategy"
    MVC = "mvc"
    REPOSITORY = "repository"
    DEPENDENCY_INJECTION = "dependency_injection"


class SeverityLevel(Enum):
    """Severity levels for code quality issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PatternDetection:
    """Represents a detected architectural pattern in code."""
    pattern_type: PatternType
    confidence: float  # 0.0 to 1.0
    location: str  # File path and line number
    description: str
    educational_context: str
    example_usage: Optional[str] = None


@dataclass
class QualityIssue:
    """Represents a code quality issue with suggested improvements."""
    severity: SeverityLevel
    category: str
    location: str
    description: str
    suggestion: str
    example_fix: Optional[str] = None


class CodeAnalysisEngine:
    """
    The core intelligence engine for CodeMentor.

    Analyzes code structure, detects patterns, evaluates quality,
    and provides educational insights for collaborative code review.
    """

    def __init__(self):
        self.pattern_detectors = self._initialize_pattern_detectors()
        self.quality_analyzers = self._initialize_quality_analyzers()

    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a single code file.

        Args:
            file_path: Path to the file being analyzed
            content: File content as string

        Returns:
            Dictionary containing detected patterns, quality issues, and insights
        """
        try:
            tree = ast.parse(content)

            analysis_result = {
                "file_path": file_path,
                "patterns": self._detect_patterns(tree, file_path),
                "quality_issues": self._analyze_quality(tree, content, file_path),
                "metrics": self._calculate_metrics(tree, content),
                "educational_insights": [],
                "collaboration_opportunities": []
            }

            # Generate educational insights based on detected patterns
            analysis_result["educational_insights"] = self._generate_insights(
                analysis_result["patterns"]
            )

            # Identify collaboration opportunities
            analysis_result["collaboration_opportunities"] = self._find_collaboration_points(
                analysis_result
            )

            return analysis_result

        except SyntaxError as e:
            return {
                "file_path": file_path,
                "error": f"Syntax error: {str(e)}",
                "patterns": [],
                "quality_issues": [],
                "metrics": {},
                "educational_insights": [],
                "collaboration_opportunities": []
            }

    def _detect_patterns(self, tree: ast.AST, file_path: str) -> List[PatternDetection]:
        """Detect architectural patterns in the AST."""
        patterns = []

        for detector_name, detector_func in self.pattern_detectors.items():
            detected = detector_func(tree, file_path)
            patterns.extend(detected)

        return patterns

    def _analyze_quality(self, tree: ast.AST, content: str, file_path: str) -> List[QualityIssue]:
        """Analyze code quality and identify issues."""
        issues = []

        for analyzer_name, analyzer_func in self.quality_analyzers.items():
            found_issues = analyzer_func(tree, content, file_path)
            issues.extend(found_issues)

        return issues

    def _calculate_metrics(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Calculate code metrics."""
        lines_of_code = len([line for line in content.splitlines() if line.strip()])

        class MetricCalculator(ast.NodeVisitor):
            def __init__(self):
                self.functions = 0
                self.classes = 0
                self.complexity = 0
                self.max_function_length = 0
                self.current_function_length = 0
                self.in_function = False

            def visit_FunctionDef(self, node):
                self.functions += 1
                old_in_function = self.in_function
                old_length = self.current_function_length

                self.in_function = True
                self.current_function_length = 0
                self.generic_visit(node)

                if self.current_function_length > self.max_function_length:
                    self.max_function_length = self.current_function_length

                self.in_function = old_in_function
                self.current_function_length = old_length

            def visit_ClassDef(self, node):
                self.classes += 1
                self.generic_visit(node)

            def generic_visit(self, node):
                if self.in_function and hasattr(node, 'lineno'):
                    self.current_function_length += 1
                # Simple complexity calculation based on control structures
                if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                    self.complexity += 1
                super().generic_visit(node)

        calculator = MetricCalculator()
        calculator.visit(tree)

        return {
            "lines_of_code": lines_of_code,
            "functions": calculator.functions,
            "classes": calculator.classes,
            "cyclomatic_complexity": calculator.complexity,
            "max_function_length": calculator.max_function_length
        }

    def _generate_insights(self, patterns: List[PatternDetection]) -> List[str]:
        """Generate educational insights based on detected patterns."""
        insights = []

        if patterns:
            pattern_types = [p.pattern_type.value for p in patterns]
            insights.append(
                f"This code demonstrates {len(set(pattern_types))} distinct architectural patterns, "
                f"showing good design pattern awareness."
            )

            high_confidence_patterns = [p for p in patterns if p.confidence > 0.8]
            if high_confidence_patterns:
                insights.append(
                    f"Strong implementation of {len(high_confidence_patterns)} patterns detected. "
                    f"Consider documenting these for team knowledge sharing."
                )
        else:
            insights.append(
                "No clear architectural patterns detected. Consider refactoring to use "
                "established design patterns for better maintainability."
            )

        return insights

    def _find_collaboration_points(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify opportunities for collaborative code review."""
        opportunities = []

        # High complexity areas need collaborative review (lowered threshold)
        complexity = analysis["metrics"].get("cyclomatic_complexity", 0)
        if complexity > 5:
            opportunities.append(
                "High complexity detected - ideal for pair review to ensure maintainability"
            )

        # Long functions suggest collaboration needs
        max_function_length = analysis["metrics"].get("max_function_length", 0)
        if max_function_length > 20:
            opportunities.append(
                "Long functions detected - consider collaborative refactoring session"
            )

        # Pattern implementations could benefit from team discussion
        high_confidence_patterns = [
            p for p in analysis["patterns"]
            if p.confidence > 0.7
        ]
        if high_confidence_patterns:
            opportunities.append(
                f"Well-implemented patterns found - great opportunity for team learning session"
            )

        # Quality issues suggest review points
        critical_issues = [
            issue for issue in analysis["quality_issues"]
            if issue.severity in [SeverityLevel.ERROR, SeverityLevel.CRITICAL]
        ]
        if critical_issues:
            opportunities.append(
                f"{len(critical_issues)} critical issues found - requires collaborative resolution"
            )

        # Warning-level issues also suggest collaboration
        warning_issues = [
            issue for issue in analysis["quality_issues"]
            if issue.severity == SeverityLevel.WARNING
        ]
        if warning_issues and len(warning_issues) >= 2:
            opportunities.append(
                f"Multiple quality concerns identified - team input valuable for resolution"
            )

        return opportunities

    def _initialize_pattern_detectors(self) -> Dict[str, callable]:
        """Initialize pattern detection functions."""
        return {
            "singleton": self._detect_singleton,
            "factory": self._detect_factory,
            "observer": self._detect_observer,
            "dependency_injection": self._detect_dependency_injection
        }

    def _initialize_quality_analyzers(self) -> Dict[str, callable]:
        """Initialize quality analysis functions."""
        return {
            "function_length": self._analyze_function_length,
            "naming_conventions": self._analyze_naming,
            "code_duplication": self._analyze_duplication
        }

    def _detect_singleton(self, tree: ast.AST, file_path: str) -> List[PatternDetection]:
        """Detect Singleton pattern implementations."""
        patterns = []

        class SingletonDetector(ast.NodeVisitor):
            def __init__(self):
                self.patterns = []

            def visit_ClassDef(self, node):
                # Look for typical singleton patterns
                has_instance_attr = False
                has_new_method = False

                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id in ['_instance', 'instance']:
                                has_instance_attr = True

                    if isinstance(item, ast.FunctionDef) and item.name == '__new__':
                        has_new_method = True

                if has_instance_attr and has_new_method:
                    self.patterns.append(PatternDetection(
                        pattern_type=PatternType.SINGLETON,
                        confidence=0.8,
                        location=f"{file_path}:{node.lineno}",
                        description=f"Singleton pattern detected in class {node.name}",
                        educational_context="The Singleton pattern ensures only one instance of a class exists. "
                                          "Useful for logging, configuration, or resource management.",
                        example_usage="Commonly used for database connections or application settings."
                    ))

                self.generic_visit(node)

        detector = SingletonDetector()
        detector.visit(tree)
        return detector.patterns

    def _detect_factory(self, tree: ast.AST, file_path: str) -> List[PatternDetection]:
        """Detect Factory pattern implementations."""
        patterns = []

        class FactoryDetector(ast.NodeVisitor):
            def __init__(self):
                self.patterns = []

            def visit_FunctionDef(self, node):
                # Look for factory method patterns
                if 'create' in node.name.lower() or 'factory' in node.name.lower():
                    # Check if it returns different types based on conditions
                    has_conditional_return = False

                    for stmt in ast.walk(node):
                        if isinstance(stmt, ast.If) and any(
                            isinstance(child, ast.Return) for child in ast.walk(stmt)
                        ):
                            has_conditional_return = True
                            break

                    if has_conditional_return:
                        self.patterns.append(PatternDetection(
                            pattern_type=PatternType.FACTORY,
                            confidence=0.7,
                            location=f"{file_path}:{node.lineno}",
                            description=f"Factory pattern detected in function {node.name}",
                            educational_context="Factory pattern creates objects without specifying exact classes. "
                                              "Promotes loose coupling and easier testing.",
                            example_usage="Useful for creating different types of objects based on configuration."
                        ))

                self.generic_visit(node)

        detector = FactoryDetector()
        detector.visit(tree)
        return detector.patterns

    def _detect_observer(self, tree: ast.AST, file_path: str) -> List[PatternDetection]:
        """Detect Observer pattern implementations."""
        patterns = []

        class ObserverDetector(ast.NodeVisitor):
            def __init__(self):
                self.patterns = []

            def visit_ClassDef(self, node):
                has_observers_list = False
                has_notify_method = False
                has_subscribe_method = False

                # Check all methods and assignments in class
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name.lower()
                        if 'notify' in method_name or 'update' in method_name:
                            has_notify_method = True
                        if 'subscribe' in method_name or ('add' in method_name and 'observer' in method_name):
                            has_subscribe_method = True

                        # Check for self.observers assignments inside methods (especially __init__)
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if (isinstance(target, ast.Attribute) and
                                        isinstance(target.value, ast.Name) and
                                        target.value.id == 'self' and
                                        ('observer' in target.attr.lower() or target.attr.lower() in ['subscribers', 'listeners'])):
                                        has_observers_list = True

                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and ('observer' in target.id.lower() or
                                                               target.id.lower() in ['subscribers', 'listeners']):
                                has_observers_list = True

                if has_observers_list and (has_notify_method or has_subscribe_method):
                    self.patterns.append(PatternDetection(
                        pattern_type=PatternType.OBSERVER,
                        confidence=0.75,
                        location=f"{file_path}:{node.lineno}",
                        description=f"Observer pattern detected in class {node.name}",
                        educational_context="Observer pattern allows objects to be notified of changes. "
                                          "Essential for event-driven architectures and MVC patterns.",
                        example_usage="Perfect for GUI applications, event systems, or model-view updates."
                    ))

                self.generic_visit(node)

        detector = ObserverDetector()
        detector.visit(tree)
        return detector.patterns

    def _detect_dependency_injection(self, tree: ast.AST, file_path: str) -> List[PatternDetection]:
        """Detect Dependency Injection patterns."""
        patterns = []

        class DIDetector(ast.NodeVisitor):
            def __init__(self):
                self.patterns = []

            def visit_FunctionDef(self, node):
                if node.name == '__init__':
                    # Look for constructor injection
                    if len(node.args.args) > 2:  # self + at least 2 dependencies
                        self.patterns.append(PatternDetection(
                            pattern_type=PatternType.DEPENDENCY_INJECTION,
                            confidence=0.6,
                            location=f"{file_path}:{node.lineno}",
                            description="Constructor dependency injection detected",
                            educational_context="Dependency Injection promotes loose coupling by injecting dependencies "
                                              "rather than creating them internally. Improves testability.",
                            example_usage="Essential for unit testing and flexible system architectures."
                        ))

                self.generic_visit(node)

        detector = DIDetector()
        detector.visit(tree)
        return detector.patterns

    def _analyze_function_length(self, tree: ast.AST, content: str, file_path: str) -> List[QualityIssue]:
        """Analyze function length and suggest improvements."""
        issues = []

        class FunctionLengthAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.issues = []

            def visit_FunctionDef(self, node):
                # Calculate function length in lines
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    length = node.end_lineno - node.lineno

                    if length > 50:
                        severity = SeverityLevel.ERROR if length > 100 else SeverityLevel.WARNING
                        self.issues.append(QualityIssue(
                            severity=severity,
                            category="Function Length",
                            location=f"{file_path}:{node.lineno}",
                            description=f"Function {node.name} is {length} lines long",
                            suggestion="Consider breaking this function into smaller, more focused functions",
                            example_fix="Extract logical blocks into separate helper functions"
                        ))

                self.generic_visit(node)

        analyzer = FunctionLengthAnalyzer()
        analyzer.visit(tree)
        return analyzer.issues

    def _analyze_naming(self, tree: ast.AST, content: str, file_path: str) -> List[QualityIssue]:
        """Analyze naming conventions."""
        issues = []

        class NamingAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.issues = []

            def visit_FunctionDef(self, node):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    if not node.name.startswith('__'):  # Ignore magic methods
                        self.issues.append(QualityIssue(
                            severity=SeverityLevel.WARNING,
                            category="Naming Convention",
                            location=f"{file_path}:{node.lineno}",
                            description=f"Function {node.name} doesn't follow snake_case convention",
                            suggestion="Use snake_case for function names",
                            example_fix=f"Rename to {self._to_snake_case(node.name)}"
                        ))

                self.generic_visit(node)

            def visit_ClassDef(self, node):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.issues.append(QualityIssue(
                        severity=SeverityLevel.WARNING,
                        category="Naming Convention",
                        location=f"{file_path}:{node.lineno}",
                        description=f"Class {node.name} doesn't follow PascalCase convention",
                        suggestion="Use PascalCase for class names",
                        example_fix=f"Rename to {self._to_pascal_case(node.name)}"
                    ))

                self.generic_visit(node)

            def _to_snake_case(self, name):
                return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

            def _to_pascal_case(self, name):
                return ''.join(word.capitalize() for word in name.split('_'))

        analyzer = NamingAnalyzer()
        analyzer.visit(tree)
        return analyzer.issues

    def _analyze_duplication(self, tree: ast.AST, content: str, file_path: str) -> List[QualityIssue]:
        """Analyze code duplication."""
        issues = []

        # Simple duplication detection based on line similarity
        lines = content.splitlines()
        significant_lines = [
            (i, line.strip()) for i, line in enumerate(lines)
            if len(line.strip()) > 10 and not line.strip().startswith('#')
        ]

        seen_lines = {}
        for line_num, line_content in significant_lines:
            if line_content in seen_lines:
                issues.append(QualityIssue(
                    severity=SeverityLevel.INFO,
                    category="Code Duplication",
                    location=f"{file_path}:{line_num + 1}",
                    description=f"Potential duplicate line found (also at line {seen_lines[line_content] + 1})",
                    suggestion="Consider extracting common code into a reusable function",
                    example_fix="Create a helper function for shared logic"
                ))
            else:
                seen_lines[line_content] = line_num

        return issues


# Integration interface for collaborative features
class CollaborationInterface:
    """Interface for integrating with Bob's collaborative features."""

    def __init__(self, analysis_engine: CodeAnalysisEngine):
        self.engine = analysis_engine

    def prepare_review_data(self, file_path: str, content: str) -> Dict[str, Any]:
        """Prepare analysis data for collaborative review."""
        analysis = self.engine.analyze_file(file_path, content)

        # Structure data for collaborative review
        return {
            "summary": self._generate_summary(analysis),
            "review_points": self._generate_review_points(analysis),
            "learning_opportunities": analysis["educational_insights"],
            "collaboration_suggestions": analysis["collaboration_opportunities"],
            "raw_analysis": analysis
        }

    def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a concise summary of the analysis."""
        patterns_count = len(analysis["patterns"])
        issues_count = len(analysis["quality_issues"])

        return (
            f"Found {patterns_count} architectural patterns and {issues_count} quality points. "
            f"Code complexity: {analysis['metrics'].get('cyclomatic_complexity', 0)}"
        )

    def _generate_review_points(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate structured review points for collaborative discussion."""
        review_points = []

        # Add pattern-based review points
        for pattern in analysis["patterns"]:
            review_points.append({
                "type": "pattern",
                "priority": "medium" if pattern.confidence > 0.7 else "low",
                "title": f"{pattern.pattern_type.value.title()} Pattern Implementation",
                "description": pattern.description,
                "educational_note": pattern.educational_context,
                "location": pattern.location
            })

        # Add quality-based review points
        for issue in analysis["quality_issues"]:
            priority = "high" if issue.severity in [SeverityLevel.ERROR, SeverityLevel.CRITICAL] else "medium"
            review_points.append({
                "type": "quality",
                "priority": priority,
                "title": f"{issue.category}: {issue.description}",
                "description": issue.description,
                "suggestion": issue.suggestion,
                "location": issue.location
            })

        return sorted(review_points, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)


if __name__ == "__main__":
    # Example usage demonstration
    engine = CodeAnalysisEngine()

    sample_code = '''
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        pass

def create_user(user_type):
    if user_type == "admin":
        return AdminUser()
    elif user_type == "regular":
        return RegularUser()
    else:
        return GuestUser()

class EventManager:
    def __init__(self):
        self.observers = []

    def subscribe(self, observer):
        self.observers.append(observer)

    def notify_all(self, event):
        for observer in self.observers:
            observer.update(event)
'''

    result = engine.analyze_file("example.py", sample_code)

    print("=== CodeMentor Analysis Results ===")
    print(f"Patterns detected: {len(result['patterns'])}")
    for pattern in result['patterns']:
        print(f"  - {pattern.pattern_type.value}: {pattern.description}")

    print(f"\nQuality issues: {len(result['quality_issues'])}")
    for issue in result['quality_issues']:
        print(f"  - {issue.severity.value}: {issue.description}")

    print(f"\nEducational insights:")
    for insight in result['educational_insights']:
        print(f"  - {insight}")