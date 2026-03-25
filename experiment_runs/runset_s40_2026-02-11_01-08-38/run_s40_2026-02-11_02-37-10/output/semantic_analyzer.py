#!/usr/bin/env python3
"""
Semantic Code Analysis Framework
A more sophisticated approach to collaborative code analysis that attempts to model
the reasoning patterns we demonstrated in our manual analysis.
"""

import ast
import re
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Any
from enum import Enum

class IssueType(Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    MAINTAINABILITY = "maintainability"

class SeverityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class SemanticIssue:
    """Represents an issue with semantic context"""
    issue_type: IssueType
    severity: SeverityLevel
    location: str
    description: str
    reasoning: str  # WHY this is problematic
    context: Dict[str, Any]  # Additional context for intersection analysis
    suggested_fix: Optional[str] = None

class SemanticAnalyzer:
    """Base class for analyzers that understand code semantically"""

    def __init__(self, name: str):
        self.name = name
        self.issues: List[SemanticIssue] = []
        self.ast_tree = None
        self.source_lines = []

    def analyze(self, code: str) -> List[SemanticIssue]:
        """Analyze code with semantic understanding"""
        self.source_lines = code.split('\n')
        try:
            self.ast_tree = ast.parse(code)
        except SyntaxError as e:
            return [SemanticIssue(
                issue_type=IssueType.MAINTAINABILITY,
                severity=SeverityLevel.CRITICAL,
                location=f"line {e.lineno}",
                description=f"Syntax error: {e.msg}",
                reasoning="Code cannot be executed or analyzed due to syntax errors",
                context={"syntax_error": True}
            )]

        self.issues = []
        self._semantic_analysis()
        return self.issues

    def _semantic_analysis(self):
        """Override in subclasses for specific analysis"""
        pass

class AdvancedSecurityAnalyzer(SemanticAnalyzer):
    """Security analyzer with semantic understanding"""

    def _semantic_analysis(self):
        # Use AST visitor pattern for deeper analysis
        visitor = SecurityASTVisitor(self)
        visitor.visit(self.ast_tree)

        # Additional semantic checks
        self._analyze_data_flow()
        self._analyze_authentication_patterns()

    def _analyze_data_flow(self):
        """Analyze how data flows through the code to identify injection points"""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Call):
                # Look for database operations
                if (hasattr(node.func, 'attr') and
                    node.func.attr in ['execute', 'query']):

                    # Check if any arguments involve string formatting
                    for arg in node.args:
                        if self._involves_user_input(arg):
                            line_num = getattr(node, 'lineno', 'unknown')
                            self.issues.append(SemanticIssue(
                                issue_type=IssueType.SECURITY,
                                severity=SeverityLevel.CRITICAL,
                                location=f"line {line_num}",
                                description="Potential SQL injection vulnerability",
                                reasoning="User input is being directly interpolated into SQL queries without parameterization",
                                context={
                                    "vulnerability_type": "sql_injection",
                                    "data_flow": "user_input_to_query",
                                    "mitigation": "parameterized_queries"
                                },
                                suggested_fix="Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
                            ))

    def _involves_user_input(self, node) -> bool:
        """Heuristic to detect if a node involves user input"""
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            return True  # String formatting
        if isinstance(node, ast.JoinedStr):
            return True  # f-strings
        return False

    def _analyze_authentication_patterns(self):
        """Look for authentication and credential handling issues"""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (isinstance(target, ast.Name) and
                        'password' in target.id.lower()):
                        # Check if password is being stored as plain text
                        if isinstance(node.value, ast.Name):
                            line_num = getattr(node, 'lineno', 'unknown')
                            self.issues.append(SemanticIssue(
                                issue_type=IssueType.SECURITY,
                                severity=SeverityLevel.HIGH,
                                location=f"line {line_num}",
                                description="Plain text password storage",
                                reasoning="Passwords should never be stored in plain text due to breach risk and compliance requirements",
                                context={
                                    "vulnerability_type": "credential_exposure",
                                    "data_type": "password",
                                    "mitigation": "hashing_required"
                                },
                                suggested_fix="Use bcrypt or similar: hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())"
                            ))

class SecurityASTVisitor(ast.NodeVisitor):
    """AST visitor for security-specific analysis"""

    def __init__(self, analyzer):
        self.analyzer = analyzer

    def visit_Call(self, node):
        # Look for dangerous function calls
        if (hasattr(node.func, 'id') and
            node.func.id in ['eval', 'exec', 'compile']):

            line_num = getattr(node, 'lineno', 'unknown')
            self.analyzer.issues.append(SemanticIssue(
                issue_type=IssueType.SECURITY,
                severity=SeverityLevel.CRITICAL,
                location=f"line {line_num}",
                description=f"Dangerous function call: {node.func.id}",
                reasoning="Dynamic code execution functions can lead to code injection vulnerabilities",
                context={
                    "vulnerability_type": "code_injection",
                    "function": node.func.id
                }
            ))

        self.generic_visit(node)

class AdvancedPerformanceAnalyzer(SemanticAnalyzer):
    """Performance analyzer with semantic understanding"""

    def _semantic_analysis(self):
        self._analyze_loop_complexity()
        self._analyze_resource_management()

    def _analyze_resource_management(self):
        """Analyze resource management patterns"""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.With):
                # Good resource management found
                pass
            elif isinstance(node, ast.Call):
                if (hasattr(node.func, 'id') and
                    node.func.id == 'open'):
                    # Check if file is opened outside with statement
                    parent = getattr(node, 'parent', None)
                    if not isinstance(parent, ast.With):
                        line_num = getattr(node, 'lineno', 'unknown')
                        self.issues.append(SemanticIssue(
                            issue_type=IssueType.MAINTAINABILITY,
                            severity=SeverityLevel.MEDIUM,
                            location=f"line {line_num}",
                            description="File opened without proper resource management",
                            reasoning="Files should be opened with 'with' statement to ensure proper cleanup",
                            context={
                                "pattern": "resource_leak",
                                "resource_type": "file"
                            },
                            suggested_fix="Use 'with open(filename) as f:' pattern"
                        ))

    def _analyze_loop_complexity(self):
        """Identify performance issues in loops"""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.For):
                # Check for nested operations that could be optimized
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if (hasattr(child.func, 'attr') and
                            child.func.attr in ['append', 'extend'] and
                            isinstance(child.func.value, ast.Name)):

                            line_num = getattr(node, 'lineno', 'unknown')
                            self.issues.append(SemanticIssue(
                                issue_type=IssueType.PERFORMANCE,
                                severity=SeverityLevel.MEDIUM,
                                location=f"line {line_num}",
                                description="Potentially inefficient list operations in loop",
                                reasoning="Repeated list operations in loops can cause O(n²) behavior due to memory reallocation",
                                context={
                                    "performance_pattern": "quadratic_complexity",
                                    "operation_type": "list_modification",
                                    "optimization": "batch_operations"
                                },
                                suggested_fix="Consider collecting items first, then batch append: items.extend(collected_items)"
                            ))

class CollaborativeIntersectionAnalyzer:
    """Analyzes intersections between different types of issues"""

    def __init__(self):
        self.analyzers = {
            "security": AdvancedSecurityAnalyzer("Advanced Security"),
            "performance": AdvancedPerformanceAnalyzer("Advanced Performance")
        }

    def analyze_code(self, code: str) -> Dict[str, List[SemanticIssue]]:
        """Run all analyzers and identify intersections"""
        results = {}
        all_issues = []

        for name, analyzer in self.analyzers.items():
            issues = analyzer.analyze(code)
            results[name] = issues
            all_issues.extend(issues)

        # Identify intersections
        intersections = self._find_intersections(all_issues)
        if intersections:
            results["intersections"] = intersections

        return results

    def _find_intersections(self, issues: List[SemanticIssue]) -> List[SemanticIssue]:
        """Find where different types of issues intersect or compound"""
        intersections = []

        # Group issues by location
        by_location = {}
        for issue in issues:
            loc = issue.location
            if loc not in by_location:
                by_location[loc] = []
            by_location[loc].append(issue)

        # Look for locations with multiple issue types
        for location, loc_issues in by_location.items():
            if len(loc_issues) > 1:
                issue_types = [issue.issue_type for issue in loc_issues]

                # Create intersection analysis
                if IssueType.SECURITY in issue_types and IssueType.ARCHITECTURE in issue_types:
                    intersections.append(SemanticIssue(
                        issue_type=IssueType.SECURITY,
                        severity=SeverityLevel.HIGH,
                        location=location,
                        description="Security-Architecture intersection",
                        reasoning="Poor architectural boundaries enable security vulnerabilities",
                        context={
                            "intersection_type": "security_architecture",
                            "compound_risk": True,
                            "related_issues": [issue.description for issue in loc_issues]
                        }
                    ))

        # Look for semantic relationships across locations
        self._analyze_cross_location_patterns(issues, intersections)

        return intersections

    def _analyze_cross_location_patterns(self, issues: List[SemanticIssue], intersections: List[SemanticIssue]):
        """Analyze patterns that span multiple locations"""

        # Look for cascading security risks
        sql_injection_issues = [i for i in issues if
                               i.context.get("vulnerability_type") == "sql_injection"]
        credential_issues = [i for i in issues if
                            i.context.get("vulnerability_type") == "credential_exposure"]

        if sql_injection_issues and credential_issues:
            intersections.append(SemanticIssue(
                issue_type=IssueType.SECURITY,
                severity=SeverityLevel.CRITICAL,
                location="multiple locations",
                description="Cascading security vulnerability",
                reasoning="SQL injection combined with plain text password storage creates compound breach risk",
                context={
                    "intersection_type": "cascading_security",
                    "risk_multiplier": "high",
                    "attack_chain": ["sql_injection", "credential_exposure"]
                },
                suggested_fix="Address both vulnerabilities: parameterized queries AND password hashing"
            ))

def main():
    """Demonstrate the semantic analysis framework"""

    # Read our sample code
    with open('/tmp/cc-exp/run_s40_2026-02-11_02-37-10/output/sample_code.py', 'r') as f:
        sample_code = f.read()

    # Run collaborative analysis
    analyzer = CollaborativeIntersectionAnalyzer()
    results = analyzer.analyze_code(sample_code)

    print("🧠 SEMANTIC ANALYSIS RESULTS")
    print("=" * 50)

    for analyzer_name, issues in results.items():
        print(f"\n📋 {analyzer_name.upper()} ANALYSIS:")
        print("-" * 30)

        if not issues:
            print("  ✅ No issues found")
            continue

        for issue in issues:
            severity_emoji = {
                SeverityLevel.CRITICAL: "🔴",
                SeverityLevel.HIGH: "🟠",
                SeverityLevel.MEDIUM: "🟡",
                SeverityLevel.LOW: "🟢"
            }.get(issue.severity, "⚪")

            print(f"\n  {severity_emoji} {issue.description}")
            print(f"     Location: {issue.location}")
            print(f"     Reasoning: {issue.reasoning}")

            if issue.suggested_fix:
                print(f"     💡 Fix: {issue.suggested_fix}")

            if issue.context:
                print(f"     🔍 Context: {issue.context}")

if __name__ == "__main__":
    main()