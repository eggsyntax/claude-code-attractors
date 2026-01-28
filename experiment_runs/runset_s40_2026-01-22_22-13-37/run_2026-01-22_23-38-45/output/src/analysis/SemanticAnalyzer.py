"""
Advanced Semantic Analyzer for CodeMentor

This module provides deep semantic analysis capabilities that go beyond
simple pattern matching to understand code intent, architectural decisions,
and design quality at a conceptual level.
"""

import ast
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque


class ArchitecturalConcern(Enum):
    """High-level architectural concerns the analyzer can identify."""
    SEPARATION_OF_CONCERNS = "separation_of_concerns"
    SINGLE_RESPONSIBILITY = "single_responsibility"
    DEPENDENCY_MANAGEMENT = "dependency_management"
    MODULARITY = "modularity"
    TESTABILITY = "testability"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"
    PERFORMANCE = "performance"


class CodeSmell(Enum):
    """Code smells that indicate design problems."""
    GOD_CLASS = "god_class"
    LONG_METHOD = "long_method"
    SHOTGUN_SURGERY = "shotgun_surgery"
    FEATURE_ENVY = "feature_envy"
    DATA_CLUMPS = "data_clumps"
    PRIMITIVE_OBSESSION = "primitive_obsession"
    SWITCH_STATEMENTS = "switch_statements"
    DUPLICATE_CODE = "duplicate_code"
    DEAD_CODE = "dead_code"


@dataclass
class SemanticInsight:
    """Represents a semantic understanding of code structure."""
    concern: ArchitecturalConcern
    confidence: float  # 0.0 to 1.0
    description: str
    evidence: List[str]  # Supporting evidence from code
    impact_level: str  # "low", "medium", "high", "critical"
    suggestions: List[str] = field(default_factory=list)
    learning_notes: str = ""


@dataclass
class DesignProblem:
    """Represents a detected design problem or code smell."""
    smell_type: CodeSmell
    severity: str  # "minor", "moderate", "major", "critical"
    location: str
    description: str
    root_cause: str
    refactoring_suggestions: List[str] = field(default_factory=list)
    educational_context: str = ""


class SemanticAnalyzer:
    """
    Advanced semantic analyzer that understands code at an architectural level.

    This analyzer goes beyond syntactic pattern detection to understand:
    - Design intent and architectural decisions
    - Code quality from a maintainability perspective
    - Educational opportunities for improvement
    - Collaborative review points that need human insight
    """

    def __init__(self):
        self.class_registry = {}  # Track classes and their characteristics
        self.function_registry = {}  # Track functions and their behavior
        self.dependency_graph = defaultdict(set)  # Inter-module dependencies
        self.complexity_metrics = {}  # Detailed complexity analysis

    def analyze_semantic_structure(self, file_path: str, content: str, ast_tree: ast.AST) -> Dict[str, Any]:
        """
        Perform deep semantic analysis of code structure.

        Returns comprehensive insights about architectural quality,
        design decisions, and educational opportunities.
        """
        # Reset analysis state for this file
        self._reset_analysis_state()

        # Build semantic understanding
        self._build_class_registry(ast_tree, file_path)
        self._build_function_registry(ast_tree, file_path)
        self._analyze_dependencies(ast_tree, file_path)

        # Generate semantic insights
        insights = self._generate_semantic_insights(file_path)
        problems = self._detect_design_problems(file_path, content)
        architectural_assessment = self._assess_architectural_quality()
        collaboration_points = self._identify_collaboration_opportunities()

        return {
            "semantic_insights": insights,
            "design_problems": problems,
            "architectural_assessment": architectural_assessment,
            "collaboration_opportunities": collaboration_points,
            "educational_recommendations": self._generate_educational_recommendations(insights, problems),
            "refactoring_priorities": self._prioritize_refactoring_opportunities(problems),
            "code_health_score": self._calculate_code_health_score(insights, problems)
        }

    def _reset_analysis_state(self):
        """Reset internal state for fresh analysis."""
        self.class_registry.clear()
        self.function_registry.clear()
        self.dependency_graph.clear()
        self.complexity_metrics.clear()

    def _build_class_registry(self, tree: ast.AST, file_path: str):
        """Build detailed registry of classes and their characteristics."""

        class ClassAnalyzer(ast.NodeVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
                self.current_class = None

            def visit_ClassDef(self, node):
                class_info = {
                    "name": node.name,
                    "location": f"{file_path}:{node.lineno}",
                    "methods": [],
                    "attributes": [],
                    "inheritance": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                    "responsibilities": set(),
                    "complexity_score": 0,
                    "lines_of_code": getattr(node, 'end_lineno', node.lineno) - node.lineno,
                    "public_interface": [],
                    "private_methods": [],
                    "static_methods": [],
                    "class_methods": []
                }

                old_class = self.current_class
                self.current_class = class_info

                # Analyze class members
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        self._analyze_method(item, class_info)
                    elif isinstance(item, ast.Assign):
                        self._analyze_attribute(item, class_info)

                # Assess class responsibilities
                self._assess_class_responsibilities(class_info)

                self.analyzer.class_registry[node.name] = class_info
                self.current_class = old_class
                self.generic_visit(node)

            def _analyze_method(self, node: ast.FunctionDef, class_info: Dict):
                """Analyze individual method characteristics."""
                method_info = {
                    "name": node.name,
                    "location": f"{file_path}:{node.lineno}",
                    "parameters": len(node.args.args) - 1,  # Exclude self
                    "lines": getattr(node, 'end_lineno', node.lineno) - node.lineno,
                    "is_property": any(isinstance(d, ast.Name) and d.id == 'property' for d in node.decorator_list),
                    "is_static": any(isinstance(d, ast.Name) and d.id == 'staticmethod' for d in node.decorator_list),
                    "is_classmethod": any(isinstance(d, ast.Name) and d.id == 'classmethod' for d in node.decorator_list),
                    "complexity": self._calculate_method_complexity(node),
                    "external_calls": self._count_external_calls(node),
                    "modifies_state": self._detects_state_modification(node)
                }

                # Categorize method
                if node.name.startswith('_'):
                    if node.name.startswith('__') and node.name.endswith('__'):
                        class_info["public_interface"].append(method_info)  # Magic methods are part of public interface
                    else:
                        class_info["private_methods"].append(method_info)
                else:
                    class_info["public_interface"].append(method_info)

                if method_info["is_static"]:
                    class_info["static_methods"].append(method_info)
                elif method_info["is_classmethod"]:
                    class_methods = ["class_methods"].append(method_info)

                class_info["methods"].append(method_info)
                class_info["complexity_score"] += method_info["complexity"]

            def _analyze_attribute(self, node: ast.Assign, class_info: Dict):
                """Analyze class attributes."""
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        class_info["attributes"].append({
                            "name": target.id,
                            "location": f"{file_path}:{node.lineno}",
                            "is_class_variable": True  # Simplified detection
                        })

            def _assess_class_responsibilities(self, class_info: Dict):
                """Assess what responsibilities this class has."""
                # Analyze method names for responsibility hints
                method_names = [m["name"] for m in class_info["methods"]]

                # Data management responsibility
                data_verbs = {"get", "set", "update", "delete", "save", "load", "store", "fetch"}
                if any(any(verb in name.lower() for verb in data_verbs) for name in method_names):
                    class_info["responsibilities"].add("data_management")

                # UI/Presentation responsibility
                ui_verbs = {"render", "display", "show", "hide", "draw", "paint", "refresh"}
                if any(any(verb in name.lower() for verb in ui_verbs) for name in method_names):
                    class_info["responsibilities"].add("presentation")

                # Business logic responsibility
                business_verbs = {"calculate", "process", "validate", "execute", "perform", "handle"}
                if any(any(verb in name.lower() for verb in business_verbs) for name in method_names):
                    class_info["responsibilities"].add("business_logic")

                # Communication responsibility
                comm_verbs = {"send", "receive", "request", "response", "notify", "broadcast"}
                if any(any(verb in name.lower() for verb in comm_verbs) for name in method_names):
                    class_info["responsibilities"].add("communication")

            def _calculate_method_complexity(self, node: ast.FunctionDef) -> int:
                """Calculate cyclomatic complexity of a method."""
                complexity = 1  # Base complexity

                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                        complexity += 1
                    elif isinstance(child, ast.Try):
                        complexity += len(child.handlers)
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1

                return complexity

            def _count_external_calls(self, node: ast.FunctionDef) -> int:
                """Count calls to external methods/functions."""
                call_count = 0
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        call_count += 1
                return call_count

            def _detects_state_modification(self, node: ast.FunctionDef) -> bool:
                """Detect if method modifies object state."""
                for child in ast.walk(node):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Attribute):
                                if isinstance(target.value, ast.Name) and target.value.id == 'self':
                                    return True
                return False

        analyzer = ClassAnalyzer(self)
        analyzer.visit(tree)

    def _build_function_registry(self, tree: ast.AST, file_path: str):
        """Build registry of standalone functions."""

        class FunctionAnalyzer(ast.NodeVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
                self.in_class = False
                self.class_stack = []

            def visit_ClassDef(self, node):
                self.in_class = True
                self.class_stack.append(node.name)
                self.generic_visit(node)
                self.class_stack.pop()
                self.in_class = len(self.class_stack) > 0

            def visit_FunctionDef(self, node):
                if not self.in_class:  # Only standalone functions
                    func_info = {
                        "name": node.name,
                        "location": f"{file_path}:{node.lineno}",
                        "parameters": len(node.args.args),
                        "lines": getattr(node, 'end_lineno', node.lineno) - node.lineno,
                        "complexity": self._calculate_complexity(node),
                        "pure_function": self._is_pure_function(node),
                        "return_type_hints": node.returns is not None,
                        "has_side_effects": self._has_side_effects(node),
                        "external_dependencies": self._get_external_dependencies(node)
                    }
                    self.analyzer.function_registry[node.name] = func_info

                self.generic_visit(node)

            def _calculate_complexity(self, node: ast.FunctionDef) -> int:
                """Calculate function complexity."""
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.Try)):
                        complexity += 1
                return complexity

            def _is_pure_function(self, node: ast.FunctionDef) -> bool:
                """Determine if function is pure (no side effects, deterministic)."""
                # Simplified heuristic - look for state modifications or I/O
                for child in ast.walk(node):
                    if isinstance(child, ast.Global) or isinstance(child, ast.Nonlocal):
                        return False
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            if child.func.id in ['print', 'open', 'input', 'exec', 'eval']:
                                return False
                return True

            def _has_side_effects(self, node: ast.FunctionDef) -> bool:
                """Detect if function has side effects."""
                return not self._is_pure_function(node)

            def _get_external_dependencies(self, node: ast.FunctionDef) -> List[str]:
                """Get list of external dependencies."""
                dependencies = set()
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            dependencies.add(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            if isinstance(child.func.value, ast.Name):
                                dependencies.add(child.func.value.id)
                return list(dependencies)

        analyzer = FunctionAnalyzer(self)
        analyzer.visit(tree)

    def _analyze_dependencies(self, tree: ast.AST, file_path: str):
        """Analyze inter-module dependencies."""

        class DependencyAnalyzer(ast.NodeVisitor):
            def __init__(self, analyzer, file_path):
                self.analyzer = analyzer
                self.file_path = file_path

            def visit_Import(self, node):
                for alias in node.names:
                    self.analyzer.dependency_graph[self.file_path].add(alias.name)

            def visit_ImportFrom(self, node):
                if node.module:
                    self.analyzer.dependency_graph[self.file_path].add(node.module)

        analyzer = DependencyAnalyzer(self, file_path)
        analyzer.visit(tree)

    def _generate_semantic_insights(self, file_path: str) -> List[SemanticInsight]:
        """Generate high-level semantic insights about the code."""
        insights = []

        # Analyze separation of concerns
        if self._assess_separation_of_concerns():
            insights.append(SemanticInsight(
                concern=ArchitecturalConcern.SEPARATION_OF_CONCERNS,
                confidence=0.8,
                description="Well-separated concerns detected across classes",
                evidence=["Classes have distinct responsibilities", "Low coupling between components"],
                impact_level="high",
                learning_notes="Good separation of concerns makes code more maintainable and testable"
            ))

        # Analyze single responsibility principle
        violations = self._detect_srp_violations()
        if violations:
            insights.append(SemanticInsight(
                concern=ArchitecturalConcern.SINGLE_RESPONSIBILITY,
                confidence=0.7,
                description=f"Single Responsibility Principle violations detected in {len(violations)} classes",
                evidence=[f"Class {name} has multiple responsibilities: {', '.join(resp)}"
                         for name, resp in violations],
                impact_level="medium",
                suggestions=["Consider splitting multi-responsibility classes",
                           "Extract distinct behaviors into separate classes"],
                learning_notes="SRP states that a class should have only one reason to change"
            ))

        # Analyze testability
        testability_score = self._assess_testability()
        if testability_score > 0.7:
            insights.append(SemanticInsight(
                concern=ArchitecturalConcern.TESTABILITY,
                confidence=testability_score,
                description="High testability detected - code is well-structured for unit testing",
                evidence=["Pure functions present", "Low coupling", "Clear interfaces"],
                impact_level="high",
                learning_notes="Testable code is often well-designed code"
            ))

        return insights

    def _detect_design_problems(self, file_path: str, content: str) -> List[DesignProblem]:
        """Detect code smells and design problems."""
        problems = []

        # Detect God Classes
        for class_name, class_info in self.class_registry.items():
            if self._is_god_class(class_info):
                problems.append(DesignProblem(
                    smell_type=CodeSmell.GOD_CLASS,
                    severity="major",
                    location=class_info["location"],
                    description=f"Class {class_name} has too many responsibilities ({len(class_info['responsibilities'])})",
                    root_cause="Single Responsibility Principle violation",
                    refactoring_suggestions=[
                        "Extract distinct responsibilities into separate classes",
                        "Use composition to delegate specific behaviors",
                        "Consider applying the Strategy or Command pattern"
                    ],
                    educational_context="God classes violate SRP and become maintenance bottlenecks"
                ))

        # Detect Long Methods
        for class_name, class_info in self.class_registry.items():
            for method in class_info["methods"]:
                if method["lines"] > 30:  # Configurable threshold
                    problems.append(DesignProblem(
                        smell_type=CodeSmell.LONG_METHOD,
                        severity="moderate" if method["lines"] < 50 else "major",
                        location=method["location"],
                        description=f"Method {method['name']} is {method['lines']} lines long",
                        root_cause="Method doing too much work",
                        refactoring_suggestions=[
                            "Extract smaller methods for distinct logic blocks",
                            "Use the Extract Method refactoring technique",
                            "Consider if the method has multiple levels of abstraction"
                        ],
                        educational_context="Long methods are harder to understand, test, and maintain"
                    ))

        # Detect Feature Envy
        problems.extend(self._detect_feature_envy())

        return problems

    def _assess_separation_of_concerns(self) -> bool:
        """Assess whether code demonstrates good separation of concerns."""
        if not self.class_registry:
            return False

        # Check if classes have distinct, non-overlapping responsibilities
        responsibility_overlap = 0
        total_comparisons = 0

        classes = list(self.class_registry.values())
        for i, class1 in enumerate(classes):
            for class2 in classes[i+1:]:
                total_comparisons += 1
                overlap = len(class1["responsibilities"] & class2["responsibilities"])
                responsibility_overlap += overlap

        if total_comparisons == 0:
            return True

        # Good separation if average overlap is low
        avg_overlap = responsibility_overlap / total_comparisons
        return avg_overlap < 0.5

    def _detect_srp_violations(self) -> List[Tuple[str, Set[str]]]:
        """Detect Single Responsibility Principle violations."""
        violations = []

        for class_name, class_info in self.class_registry.items():
            if len(class_info["responsibilities"]) > 1:
                violations.append((class_name, class_info["responsibilities"]))

        return violations

    def _assess_testability(self) -> float:
        """Assess overall testability of the code."""
        if not self.function_registry and not self.class_registry:
            return 0.0

        testability_factors = []

        # Pure functions are highly testable
        pure_functions = sum(1 for f in self.function_registry.values() if f["pure_function"])
        total_functions = len(self.function_registry)
        if total_functions > 0:
            testability_factors.append(pure_functions / total_functions)

        # Classes with clear interfaces are testable
        for class_info in self.class_registry.values():
            interface_clarity = len(class_info["public_interface"]) / max(len(class_info["methods"]), 1)
            testability_factors.append(min(interface_clarity, 1.0))

        # Low complexity methods are more testable
        avg_complexity = sum(
            sum(m["complexity"] for m in class_info["methods"]) / max(len(class_info["methods"]), 1)
            for class_info in self.class_registry.values()
        ) / max(len(self.class_registry), 1) if self.class_registry else 0

        complexity_factor = max(0, 1 - (avg_complexity - 1) / 10)  # Normalize complexity
        testability_factors.append(complexity_factor)

        return sum(testability_factors) / max(len(testability_factors), 1)

    def _is_god_class(self, class_info: Dict) -> bool:
        """Determine if a class is a God class."""
        # Multiple heuristics for God class detection
        return (
            len(class_info["responsibilities"]) > 2 or
            len(class_info["methods"]) > 20 or
            class_info["lines_of_code"] > 200 or
            class_info["complexity_score"] > 50
        )

    def _detect_feature_envy(self) -> List[DesignProblem]:
        """Detect Feature Envy code smell."""
        problems = []

        # Simplified detection: methods that make many external calls
        for class_name, class_info in self.class_registry.items():
            for method in class_info["methods"]:
                if method["external_calls"] > method["parameters"] * 3:  # Heuristic
                    problems.append(DesignProblem(
                        smell_type=CodeSmell.FEATURE_ENVY,
                        severity="moderate",
                        location=method["location"],
                        description=f"Method {method['name']} makes many external calls ({method['external_calls']})",
                        root_cause="Method seems more interested in other classes than its own",
                        refactoring_suggestions=[
                            "Move method to the class it's most interested in",
                            "Extract the envious part into a separate method",
                            "Consider if this indicates missing abstraction"
                        ],
                        educational_context="Feature Envy suggests methods are in the wrong class"
                    ))

        return problems

    def _assess_architectural_quality(self) -> Dict[str, Any]:
        """Assess overall architectural quality."""
        return {
            "modularity_score": self._calculate_modularity_score(),
            "coupling_level": self._assess_coupling(),
            "cohesion_level": self._assess_cohesion(),
            "complexity_distribution": self._analyze_complexity_distribution(),
            "design_pattern_usage": self._assess_design_pattern_usage()
        }

    def _calculate_modularity_score(self) -> float:
        """Calculate modularity score based on class organization."""
        if not self.class_registry:
            return 0.5  # Neutral score for procedural code

        # Score based on clear separation of responsibilities
        clear_responsibilities = sum(1 for c in self.class_registry.values() if len(c["responsibilities"]) == 1)
        total_classes = len(self.class_registry)

        return clear_responsibilities / total_classes

    def _assess_coupling(self) -> str:
        """Assess coupling level between components."""
        if not self.dependency_graph:
            return "low"

        avg_dependencies = sum(len(deps) for deps in self.dependency_graph.values()) / len(self.dependency_graph)

        if avg_dependencies > 5:
            return "high"
        elif avg_dependencies > 2:
            return "medium"
        else:
            return "low"

    def _assess_cohesion(self) -> str:
        """Assess cohesion within classes."""
        if not self.class_registry:
            return "medium"

        # Simplified cohesion assessment based on method interactions
        high_cohesion_classes = 0
        for class_info in self.class_registry.values():
            if len(class_info["responsibilities"]) == 1 and class_info["complexity_score"] < 20:
                high_cohesion_classes += 1

        cohesion_ratio = high_cohesion_classes / len(self.class_registry)

        if cohesion_ratio > 0.7:
            return "high"
        elif cohesion_ratio > 0.4:
            return "medium"
        else:
            return "low"

    def _analyze_complexity_distribution(self) -> Dict[str, Any]:
        """Analyze how complexity is distributed across the codebase."""
        complexities = []

        # Collect method complexities
        for class_info in self.class_registry.values():
            for method in class_info["methods"]:
                complexities.append(method["complexity"])

        # Add function complexities
        for func_info in self.function_registry.values():
            complexities.append(func_info["complexity"])

        if not complexities:
            return {"average": 0, "max": 0, "distribution": "unknown"}

        avg_complexity = sum(complexities) / len(complexities)
        max_complexity = max(complexities)

        # Categorize distribution
        high_complexity_count = sum(1 for c in complexities if c > 10)
        distribution = "even"
        if high_complexity_count > len(complexities) * 0.2:
            distribution = "concentrated"  # Too many complex methods
        elif max_complexity < 5:
            distribution = "simple"  # Generally simple code

        return {
            "average": avg_complexity,
            "max": max_complexity,
            "distribution": distribution,
            "high_complexity_methods": high_complexity_count
        }

    def _assess_design_pattern_usage(self) -> Dict[str, Any]:
        """Assess usage of design patterns."""
        # This would integrate with existing pattern detection
        return {
            "patterns_detected": 0,  # Would connect to pattern detector
            "pattern_consistency": "good",  # Placeholder
            "anti_patterns": 0  # Would connect to anti-pattern detector
        }

    def _identify_collaboration_opportunities(self) -> List[str]:
        """Identify specific opportunities for collaborative code review."""
        opportunities = []

        # Complex classes need collaborative review
        complex_classes = [name for name, info in self.class_registry.items()
                          if info["complexity_score"] > 30]
        if complex_classes:
            opportunities.append(
                f"Complex classes ({', '.join(complex_classes)}) would benefit from collaborative design review"
            )

        # Classes with multiple responsibilities need architectural discussion
        multi_resp_classes = [name for name, info in self.class_registry.items()
                             if len(info["responsibilities"]) > 1]
        if multi_resp_classes:
            opportunities.append(
                f"Multi-responsibility classes ({', '.join(multi_resp_classes)}) need architectural refactoring discussion"
            )

        # High-dependency modules need dependency management review
        high_dep_files = [file for file, deps in self.dependency_graph.items() if len(deps) > 5]
        if high_dep_files:
            opportunities.append(
                "High-dependency modules detected - team review of dependency management needed"
            )

        return opportunities

    def _generate_educational_recommendations(self, insights: List[SemanticInsight],
                                           problems: List[DesignProblem]) -> List[str]:
        """Generate educational recommendations based on analysis."""
        recommendations = []

        # Recommend based on detected problems
        problem_types = {p.smell_type for p in problems}

        if CodeSmell.GOD_CLASS in problem_types:
            recommendations.append(
                "Study: Single Responsibility Principle and class decomposition techniques"
            )

        if CodeSmell.LONG_METHOD in problem_types:
            recommendations.append(
                "Study: Extract Method refactoring and function decomposition"
            )

        if CodeSmell.FEATURE_ENVY in problem_types:
            recommendations.append(
                "Study: Object-oriented design principles and proper method placement"
            )

        # Recommend based on positive insights
        for insight in insights:
            if insight.concern == ArchitecturalConcern.SEPARATION_OF_CONCERNS:
                recommendations.append(
                    "Great separation of concerns! Consider documenting your design decisions"
                )

        return recommendations

    def _prioritize_refactoring_opportunities(self, problems: List[DesignProblem]) -> List[Dict[str, Any]]:
        """Prioritize refactoring opportunities based on impact and effort."""
        priorities = []

        for problem in problems:
            priority_score = 0

            # Weight by severity
            severity_weights = {"minor": 1, "moderate": 3, "major": 5, "critical": 8}
            priority_score += severity_weights.get(problem.severity, 1)

            # Weight by smell type impact
            impact_weights = {
                CodeSmell.GOD_CLASS: 5,
                CodeSmell.LONG_METHOD: 3,
                CodeSmell.FEATURE_ENVY: 2,
                CodeSmell.DUPLICATE_CODE: 4
            }
            priority_score += impact_weights.get(problem.smell_type, 1)

            priorities.append({
                "problem": problem,
                "priority_score": priority_score,
                "estimated_effort": self._estimate_refactoring_effort(problem),
                "impact_vs_effort": priority_score / max(self._estimate_refactoring_effort(problem), 1)
            })

        # Sort by impact vs effort ratio (high impact, low effort first)
        return sorted(priorities, key=lambda x: x["impact_vs_effort"], reverse=True)

    def _estimate_refactoring_effort(self, problem: DesignProblem) -> int:
        """Estimate refactoring effort (1-10 scale)."""
        effort_map = {
            CodeSmell.LONG_METHOD: 3,  # Usually straightforward extraction
            CodeSmell.FEATURE_ENVY: 4,  # Requires understanding of proper placement
            CodeSmell.GOD_CLASS: 8,    # Major restructuring needed
            CodeSmell.DUPLICATE_CODE: 2  # Usually simple extraction
        }

        return effort_map.get(problem.smell_type, 5)

    def _calculate_code_health_score(self, insights: List[SemanticInsight],
                                   problems: List[DesignProblem]) -> Dict[str, Any]:
        """Calculate overall code health score."""
        base_score = 7.0  # Start with neutral good score

        # Deduct for problems
        for problem in problems:
            severity_penalties = {"minor": 0.1, "moderate": 0.3, "major": 0.7, "critical": 1.5}
            base_score -= severity_penalties.get(problem.severity, 0.5)

        # Add for positive insights
        for insight in insights:
            if insight.impact_level == "high":
                base_score += 0.5 * insight.confidence
            elif insight.impact_level == "medium":
                base_score += 0.3 * insight.confidence

        # Normalize to 1-10 scale
        final_score = max(1.0, min(10.0, base_score))

        # Categorize score
        if final_score >= 8.5:
            category = "excellent"
        elif final_score >= 7.0:
            category = "good"
        elif final_score >= 5.5:
            category = "fair"
        elif final_score >= 4.0:
            category = "poor"
        else:
            category = "critical"

        return {
            "score": round(final_score, 1),
            "category": category,
            "factors_considered": {
                "design_problems": len(problems),
                "positive_insights": len(insights),
                "architectural_quality": "assessed"
            }
        }


# Integration with existing analysis engine
class EnhancedAnalysisEngine:
    """Enhanced analysis engine that combines pattern detection with semantic analysis."""

    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()

    def perform_comprehensive_analysis(self, file_path: str, content: str, ast_tree: ast.AST) -> Dict[str, Any]:
        """Perform both pattern detection and semantic analysis."""
        semantic_results = self.semantic_analyzer.analyze_semantic_structure(file_path, content, ast_tree)

        # Combine with existing pattern detection results
        return {
            **semantic_results,
            "analysis_timestamp": "2026-01-23",  # Current date
            "analyzer_version": "enhanced_v2.0"
        }