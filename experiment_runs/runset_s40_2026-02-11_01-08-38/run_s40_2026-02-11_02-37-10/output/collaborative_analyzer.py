#!/usr/bin/env python3
"""
Collaborative Code Analysis Framework
=====================================

A framework for multi-agent code analysis that identifies intersections
between different types of technical issues (security, performance,
architecture, maintainability).

Created collaboratively by Dave and Tara (Claude Code instances).
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Set, Dict, Optional, Any
import ast
import re


class IssueCategory(Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"


class IssueSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class CodeIssue:
    """Represents a single code issue found by an analyzer"""
    id: str
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    suggested_fix: str
    confidence: float  # 0.0 to 1.0
    analyzer_id: str  # Which agent/analyzer found this

    # For tracking intersections with other issues
    related_issues: Set[str] = None
    amplifies_issues: Set[str] = None  # Issues this makes worse
    amplified_by_issues: Set[str] = None  # Issues that make this worse

    def __post_init__(self):
        if self.related_issues is None:
            self.related_issues = set()
        if self.amplifies_issues is None:
            self.amplifies_issues = set()
        if self.amplified_by_issues is None:
            self.amplified_by_issues = set()


class AnalyzerAgent:
    """Base class for specialized analyzers (security, performance, etc.)"""

    def __init__(self, agent_id: str, focus_categories: List[IssueCategory]):
        self.agent_id = agent_id
        self.focus_categories = focus_categories

    def analyze(self, code: str, file_path: str) -> List[CodeIssue]:
        """Override in subclasses to implement specific analysis logic"""
        raise NotImplementedError

    def get_capabilities(self) -> Dict[str, Any]:
        """Return metadata about what this analyzer can detect"""
        return {
            "agent_id": self.agent_id,
            "categories": [cat.value for cat in self.focus_categories],
            "description": self.__doc__ or f"Analyzer for {self.agent_id}"
        }


class SecurityAnalyzer(AnalyzerAgent):
    """Focuses on security vulnerabilities and related architectural issues"""

    def __init__(self):
        super().__init__("security_agent", [IssueCategory.SECURITY, IssueCategory.ARCHITECTURE])

    def analyze(self, code: str, file_path: str) -> List[CodeIssue]:
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # SQL injection detection
            if 'execute(' in line and ('f"' in line or '.format(' in line or '%' in line):
                issues.append(CodeIssue(
                    id=f"sql_injection_{file_path}_{i}",
                    category=IssueCategory.SECURITY,
                    severity=IssueSeverity.CRITICAL,
                    title="SQL Injection Vulnerability",
                    description="Dynamic SQL query construction without parameterization",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    suggested_fix="Use parameterized queries with placeholders",
                    confidence=0.85,
                    analyzer_id=self.agent_id
                ))

            # Plain text password storage
            if 'password' in line.lower() and ('=' in line or 'store' in line.lower()):
                if not any(secure in line.lower() for secure in ['hash', 'bcrypt', 'encrypt']):
                    issues.append(CodeIssue(
                        id=f"plaintext_password_{file_path}_{i}",
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.HIGH,
                        title="Plain Text Password Storage",
                        description="Password appears to be stored in plain text",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        suggested_fix="Hash passwords using bcrypt or similar",
                        confidence=0.75,
                        analyzer_id=self.agent_id
                    ))

        return issues


class PerformanceAnalyzer(AnalyzerAgent):
    """Focuses on performance issues and maintainability concerns"""

    def __init__(self):
        super().__init__("performance_agent", [IssueCategory.PERFORMANCE, IssueCategory.MAINTAINABILITY])

    def analyze(self, code: str, file_path: str) -> List[CodeIssue]:
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # Inefficient loops
            if 'for' in line and any(inefficient in line for inefficient in ['append(', 'extend(', '+=']):
                issues.append(CodeIssue(
                    id=f"inefficient_loop_{file_path}_{i}",
                    category=IssueCategory.PERFORMANCE,
                    severity=IssueSeverity.MEDIUM,
                    title="Potentially Inefficient Loop",
                    description="Loop with operations that could be optimized",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    suggested_fix="Consider list comprehensions or bulk operations",
                    confidence=0.65,
                    analyzer_id=self.agent_id
                ))

            # Missing error handling
            if any(risky in line for risky in ['open(', 'requests.', 'json.loads']):
                # Check if next few lines have try/except
                has_exception_handling = False
                for j in range(max(0, i-3), min(len(lines), i+3)):
                    if 'try:' in lines[j] or 'except' in lines[j]:
                        has_exception_handling = True
                        break

                if not has_exception_handling:
                    issues.append(CodeIssue(
                        id=f"missing_error_handling_{file_path}_{i}",
                        category=IssueCategory.MAINTAINABILITY,
                        severity=IssueSeverity.MEDIUM,
                        title="Missing Error Handling",
                        description="Operation that could fail without proper error handling",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        suggested_fix="Add try/except blocks for error handling",
                        confidence=0.70,
                        analyzer_id=self.agent_id
                    ))

        return issues


class IntersectionAnalyzer:
    """Identifies relationships and intersections between issues found by different agents"""

    def __init__(self):
        self.intersection_rules = self._load_intersection_rules()

    def _load_intersection_rules(self) -> Dict[str, Any]:
        """Define rules for how different types of issues interact"""
        return {
            "sql_injection_amplifies": {
                "plaintext_password": "SQL injection + plain text passwords = credential theft risk",
                "missing_error_handling": "SQL injection without error handling exposes more system info"
            },
            "architectural_problems_enable": {
                "security_issues": "Poor separation of concerns makes security bugs more likely",
                "performance_issues": "Tightly coupled code is harder to optimize"
            },
            "performance_issues_discourage": {
                "refactoring": "Performance problems make developers hesitant to refactor",
                "security_fixes": "Fear of breaking slow code prevents security improvements"
            }
        }

    def analyze_intersections(self, all_issues: List[CodeIssue]) -> List[CodeIssue]:
        """Find and annotate relationships between issues"""
        # Create a map for quick lookup
        issue_map = {issue.id: issue for issue in all_issues}

        for issue in all_issues:
            self._find_related_issues(issue, all_issues, issue_map)

        return all_issues

    def _find_related_issues(self, issue: CodeIssue, all_issues: List[CodeIssue], issue_map: Dict[str, CodeIssue]):
        """Find issues that interact with the given issue"""
        for other_issue in all_issues:
            if other_issue.id == issue.id:
                continue

            # Check if issues are in the same file/area
            if (other_issue.file_path == issue.file_path and
                abs(other_issue.line_number - issue.line_number) <= 10):
                issue.related_issues.add(other_issue.id)

            # Apply intersection rules
            self._apply_intersection_rules(issue, other_issue)

    def _apply_intersection_rules(self, issue1: CodeIssue, issue2: CodeIssue):
        """Apply predefined rules about how different issue types interact"""
        # SQL injection + authentication issues
        if ("sql_injection" in issue1.id and "password" in issue2.id):
            issue1.amplifies_issues.add(issue2.id)
            issue2.amplified_by_issues.add(issue1.id)

        # Architecture issues enable other problems
        if (issue1.category == IssueCategory.ARCHITECTURE and
            issue2.category in [IssueCategory.SECURITY, IssueCategory.PERFORMANCE]):
            issue1.amplifies_issues.add(issue2.id)
            issue2.amplified_by_issues.add(issue1.id)


class CollaborativeAnalysisEngine:
    """Main engine that coordinates multiple analyzers and finds intersections"""

    def __init__(self):
        self.analyzers: List[AnalyzerAgent] = []
        self.intersection_analyzer = IntersectionAnalyzer()

    def add_analyzer(self, analyzer: AnalyzerAgent):
        """Add a specialized analyzer to the engine"""
        self.analyzers.append(analyzer)

    def analyze_code(self, code: str, file_path: str) -> Dict[str, Any]:
        """Run all analyzers and find intersections"""
        all_issues = []

        # Run each analyzer
        for analyzer in self.analyzers:
            try:
                issues = analyzer.analyze(code, file_path)
                all_issues.extend(issues)
                print(f"[{analyzer.agent_id}] Found {len(issues)} issues")
            except Exception as e:
                print(f"Error in {analyzer.agent_id}: {e}")

        # Find intersections between issues
        all_issues = self.intersection_analyzer.analyze_intersections(all_issues)

        # Generate summary
        return {
            "total_issues": len(all_issues),
            "issues_by_category": self._categorize_issues(all_issues),
            "intersection_count": sum(len(issue.related_issues) for issue in all_issues) // 2,
            "critical_intersections": self._find_critical_intersections(all_issues),
            "all_issues": all_issues,
            "analyzer_contributions": self._summarize_analyzer_contributions(all_issues)
        }

    def _categorize_issues(self, issues: List[CodeIssue]) -> Dict[str, int]:
        """Group issues by category"""
        categories = {}
        for issue in issues:
            cat = issue.category.value
            categories[cat] = categories.get(cat, 0) + 1
        return categories

    def _find_critical_intersections(self, issues: List[CodeIssue]) -> List[Dict[str, Any]]:
        """Identify the most important issue intersections"""
        critical_intersections = []

        for issue in issues:
            if issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]:
                if issue.amplifies_issues:
                    critical_intersections.append({
                        "primary_issue": issue.id,
                        "amplifies": list(issue.amplifies_issues),
                        "impact": f"{issue.title} makes other issues more severe"
                    })

        return critical_intersections

    def _summarize_analyzer_contributions(self, issues: List[CodeIssue]) -> Dict[str, Dict[str, Any]]:
        """Summarize what each analyzer contributed"""
        contributions = {}

        for issue in issues:
            agent_id = issue.analyzer_id
            if agent_id not in contributions:
                contributions[agent_id] = {
                    "total_issues": 0,
                    "categories": set(),
                    "severities": [],
                    "confidence_avg": 0.0
                }

            contrib = contributions[agent_id]
            contrib["total_issues"] += 1
            contrib["categories"].add(issue.category.value)
            contrib["severities"].append(issue.severity.value)
            contrib["confidence_avg"] += issue.confidence

        # Calculate averages and convert sets to lists
        for agent_id, contrib in contributions.items():
            if contrib["total_issues"] > 0:
                contrib["confidence_avg"] /= contrib["total_issues"]
            contrib["categories"] = list(contrib["categories"])

        return contributions


if __name__ == "__main__":
    print("Collaborative Code Analysis Framework")
    print("=====================================")
    print("Framework for multi-agent code analysis with intersection detection")
    print("Created by Dave and Tara (Claude Code instances)")
    print("\nTo use:")
    print("1. Create engine: engine = CollaborativeAnalysisEngine()")
    print("2. Add analyzers: engine.add_analyzer(SecurityAnalyzer())")
    print("3. Analyze code: results = engine.analyze_code(code_string, file_path)")