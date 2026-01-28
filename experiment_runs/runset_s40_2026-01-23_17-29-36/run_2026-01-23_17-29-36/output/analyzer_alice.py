"""
Alice's Code Analysis Engine
Focus: Design patterns, code quality, SOLID principles, maintainability
"""

import ast
import re
from typing import List, Dict, Any
from dataclasses import dataclass
from collections import defaultdict, Counter


@dataclass
class Finding:
    """Represents a code analysis finding"""
    category: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    line_number: int
    confidence: float  # 0.0 to 1.0
    suggestion: str
    rule_id: str


class DesignPatternAnalyzer:
    """Analyzes code for design patterns and anti-patterns"""

    def analyze(self, code: str) -> List[Finding]:
        findings = []
        tree = ast.parse(code)

        # Detect God Class anti-pattern
        findings.extend(self._detect_god_class(tree))

        # Detect Singleton pattern (and potential misuse)
        findings.extend(self._detect_singleton_issues(tree))

        # Detect Strategy pattern opportunities
        findings.extend(self._detect_strategy_opportunities(code))

        return findings

    def _detect_god_class(self, tree: ast.AST) -> List[Finding]:
        findings = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                line_count = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0

                if method_count > 15 or line_count > 300:
                    severity = 'high' if method_count > 20 or line_count > 500 else 'medium'
                    confidence = min(0.9, (method_count - 10) / 20 + (line_count - 200) / 400)

                    findings.append(Finding(
                        category="Design Pattern",
                        severity=severity,
                        message=f"Class '{node.name}' shows God Class anti-pattern ({method_count} methods, ~{line_count} lines)",
                        line_number=node.lineno,
                        confidence=confidence,
                        suggestion="Consider breaking this class into smaller, more focused classes using Single Responsibility Principle",
                        rule_id="DP001"
                    ))
        return findings

    def _detect_singleton_issues(self, tree: ast.AST) -> List[Finding]:
        findings = []
        singleton_indicators = ['__new__', '_instance', 'instance']

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_singleton_pattern = any(
                    isinstance(n, ast.FunctionDef) and any(indicator in n.name.lower() for indicator in singleton_indicators)
                    for n in node.body
                )

                if has_singleton_pattern:
                    findings.append(Finding(
                        category="Design Pattern",
                        severity="medium",
                        message=f"Class '{node.name}' appears to implement Singleton pattern",
                        line_number=node.lineno,
                        confidence=0.7,
                        suggestion="Consider dependency injection instead of Singleton for better testability",
                        rule_id="DP002"
                    ))
        return findings

    def _detect_strategy_opportunities(self, code: str) -> List[Finding]:
        findings = []
        # Look for large if-elif chains that could benefit from Strategy pattern
        if_elif_pattern = re.compile(r'if\s+.*?:\s*\n.*?(?:elif\s+.*?:\s*\n.*?){3,}', re.MULTILINE | re.DOTALL)
        matches = if_elif_pattern.finditer(code)

        for match in matches:
            line_number = code[:match.start()].count('\n') + 1
            findings.append(Finding(
                category="Design Pattern",
                severity="low",
                message="Long if-elif chain detected - consider Strategy pattern",
                line_number=line_number,
                confidence=0.6,
                suggestion="Refactor into Strategy pattern with polymorphic classes",
                rule_id="DP003"
            ))

        return findings


class SOLIDPrincipleAnalyzer:
    """Analyzes code for SOLID principle violations"""

    def analyze(self, code: str) -> List[Finding]:
        findings = []
        tree = ast.parse(code)

        findings.extend(self._check_single_responsibility(tree))
        findings.extend(self._check_open_closed(tree, code))
        findings.extend(self._check_dependency_inversion(tree))

        return findings

    def _check_single_responsibility(self, tree: ast.AST) -> List[Finding]:
        findings = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function length as SRP indicator
                if hasattr(node, 'end_lineno'):
                    line_count = node.end_lineno - node.lineno
                    if line_count > 50:
                        findings.append(Finding(
                            category="SOLID Principles",
                            severity="medium",
                            message=f"Function '{node.name}' is {line_count} lines long, may violate Single Responsibility Principle",
                            line_number=node.lineno,
                            confidence=0.7,
                            suggestion="Consider breaking this function into smaller, more focused functions",
                            rule_id="SRP001"
                        ))

                # Check for mixed concerns (database + business logic)
                func_code = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                db_keywords = ['execute', 'query', 'insert', 'update', 'delete', 'commit']
                business_keywords = ['calculate', 'validate', 'process', 'transform']

                has_db = any(keyword in func_code.lower() for keyword in db_keywords)
                has_business = any(keyword in func_code.lower() for keyword in business_keywords)

                if has_db and has_business:
                    findings.append(Finding(
                        category="SOLID Principles",
                        severity="medium",
                        message=f"Function '{node.name}' mixes data access and business logic",
                        line_number=node.lineno,
                        confidence=0.6,
                        suggestion="Separate data access from business logic using Repository or DAO pattern",
                        rule_id="SRP002"
                    ))

        return findings

    def _check_open_closed(self, tree: ast.AST, code: str) -> List[Finding]:
        findings = []

        # Look for type checking that suggests violation of Open/Closed Principle
        type_check_pattern = re.compile(r'isinstance\(.*?\)|type\(.*?\)\s*==|__class__\s*==')
        matches = list(type_check_pattern.finditer(code))

        if len(matches) > 3:  # Multiple type checks suggest OCP violation
            line_number = code[:matches[0].start()].count('\n') + 1
            findings.append(Finding(
                category="SOLID Principles",
                severity="medium",
                message=f"Multiple type checks detected ({len(matches)} instances) - may violate Open/Closed Principle",
                line_number=line_number,
                confidence=0.6,
                suggestion="Consider using polymorphism instead of type checking",
                rule_id="OCP001"
            ))

        return findings

    def _check_dependency_inversion(self, tree: ast.AST) -> List[Finding]:
        findings = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for direct instantiation of concrete classes in methods
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        for stmt in ast.walk(method):
                            if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Name):
                                # Check if calling constructor of what looks like a concrete class
                                if stmt.func.id and stmt.func.id[0].isupper():
                                    findings.append(Finding(
                                        category="SOLID Principles",
                                        severity="low",
                                        message=f"Direct instantiation of '{stmt.func.id}' in method - consider dependency injection",
                                        line_number=getattr(stmt, 'lineno', 0),
                                        confidence=0.4,
                                        suggestion="Use dependency injection to depend on abstractions, not concretions",
                                        rule_id="DIP001"
                                    ))

        return findings


class CodeQualityAnalyzer:
    """Analyzes general code quality metrics"""

    def analyze(self, code: str) -> List[Finding]:
        findings = []
        tree = ast.parse(code)

        findings.extend(self._check_complexity(tree))
        findings.extend(self._check_naming_conventions(tree))
        findings.extend(self._check_documentation(tree))

        return findings

    def _check_complexity(self, tree: ast.AST) -> List[Finding]:
        findings = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calculate cyclomatic complexity approximation
                complexity = self._calculate_complexity(node)

                if complexity > 10:
                    severity = 'high' if complexity > 15 else 'medium'
                    findings.append(Finding(
                        category="Code Quality",
                        severity=severity,
                        message=f"Function '{node.name}' has high cyclomatic complexity ({complexity})",
                        line_number=node.lineno,
                        confidence=0.9,
                        suggestion="Reduce complexity by extracting methods or simplifying conditional logic",
                        rule_id="CQ001"
                    ))

        return findings

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Simplified cyclomatic complexity calculation"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _check_naming_conventions(self, tree: ast.AST) -> List[Finding]:
        findings = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.islower() or '__' in node.name[1:-1]:
                    findings.append(Finding(
                        category="Code Quality",
                        severity="low",
                        message=f"Function '{node.name}' doesn't follow snake_case convention",
                        line_number=node.lineno,
                        confidence=0.8,
                        suggestion="Use snake_case for function names",
                        rule_id="CQ002"
                    ))

            elif isinstance(node, ast.ClassDef):
                if not node.name[0].isupper() or '_' in node.name:
                    findings.append(Finding(
                        category="Code Quality",
                        severity="low",
                        message=f"Class '{node.name}' doesn't follow PascalCase convention",
                        line_number=node.lineno,
                        confidence=0.8,
                        suggestion="Use PascalCase for class names",
                        rule_id="CQ003"
                    ))

        return findings

    def _check_documentation(self, tree: ast.AST) -> List[Finding]:
        findings = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # Check for docstring
                has_docstring = (
                    len(node.body) > 0 and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)
                )

                if not has_docstring:
                    node_type = "Function" if isinstance(node, ast.FunctionDef) else "Class"
                    findings.append(Finding(
                        category="Code Quality",
                        severity="low",
                        message=f"{node_type} '{node.name}' lacks documentation",
                        line_number=node.lineno,
                        confidence=0.9,
                        suggestion="Add docstring to explain purpose and usage",
                        rule_id="CQ004"
                    ))

        return findings


class AliceAnalyzer:
    """Main analyzer orchestrating all analysis types"""

    def __init__(self):
        self.design_analyzer = DesignPatternAnalyzer()
        self.solid_analyzer = SOLIDPrincipleAnalyzer()
        self.quality_analyzer = CodeQualityAnalyzer()

    def analyze(self, code: str, filename: str = "unknown") -> Dict[str, Any]:
        """
        Analyze code and return comprehensive findings
        """
        findings = []

        try:
            # Run all analyzers
            findings.extend(self.design_analyzer.analyze(code))
            findings.extend(self.solid_analyzer.analyze(code))
            findings.extend(self.quality_analyzer.analyze(code))

        except SyntaxError as e:
            findings.append(Finding(
                category="Syntax",
                severity="critical",
                message=f"Syntax error: {str(e)}",
                line_number=getattr(e, 'lineno', 0),
                confidence=1.0,
                suggestion="Fix syntax errors before proceeding with analysis",
                rule_id="SYN001"
            ))
        except Exception as e:
            findings.append(Finding(
                category="Analysis Error",
                severity="medium",
                message=f"Analysis error: {str(e)}",
                line_number=0,
                confidence=0.8,
                suggestion="Check code structure and try again",
                rule_id="ERR001"
            ))

        # Aggregate statistics
        stats = self._calculate_statistics(findings)

        return {
            'filename': filename,
            'analyzer': 'Alice (Design & Quality)',
            'findings': [
                {
                    'category': f.category,
                    'severity': f.severity,
                    'message': f.message,
                    'line_number': f.line_number,
                    'confidence': f.confidence,
                    'suggestion': f.suggestion,
                    'rule_id': f.rule_id
                }
                for f in findings
            ],
            'statistics': stats,
            'summary': self._generate_summary(findings)
        }

    def _calculate_statistics(self, findings: List[Finding]) -> Dict[str, Any]:
        """Calculate aggregate statistics from findings"""
        if not findings:
            return {'total_issues': 0}

        severity_counts = Counter(f.severity for f in findings)
        category_counts = Counter(f.category for f in findings)
        avg_confidence = sum(f.confidence for f in findings) / len(findings)

        return {
            'total_issues': len(findings),
            'severity_breakdown': dict(severity_counts),
            'category_breakdown': dict(category_counts),
            'average_confidence': round(avg_confidence, 2),
            'high_confidence_issues': len([f for f in findings if f.confidence > 0.7])
        }

    def _generate_summary(self, findings: List[Finding]) -> str:
        """Generate a human-readable summary"""
        if not findings:
            return "Code analysis complete: No issues found. Great job!"

        severity_counts = Counter(f.severity for f in findings)
        critical = severity_counts.get('critical', 0)
        high = severity_counts.get('high', 0)
        medium = severity_counts.get('medium', 0)
        low = severity_counts.get('low', 0)

        summary_parts = []

        if critical:
            summary_parts.append(f"{critical} critical issue{'s' if critical != 1 else ''}")
        if high:
            summary_parts.append(f"{high} high-priority issue{'s' if high != 1 else ''}")
        if medium:
            summary_parts.append(f"{medium} medium-priority issue{'s' if medium != 1 else ''}")
        if low:
            summary_parts.append(f"{low} low-priority issue{'s' if low != 1 else ''}")

        return f"Found {', '.join(summary_parts)}. Focus on design patterns, SOLID principles, and code maintainability."

    def self_test(self) -> Dict[str, Any]:
        """Test the analyzer on its own code"""
        with open(__file__, 'r') as f:
            own_code = f.read()
        return self.analyze(own_code, __file__)


if __name__ == "__main__":
    # Self-test capability
    analyzer = AliceAnalyzer()
    result = analyzer.self_test()

    print("=== ALICE ANALYZER SELF-TEST ===")
    print(f"Analysis Summary: {result['summary']}")
    print(f"Statistics: {result['statistics']}")

    if result['findings']:
        print("\nFindings:")
        for finding in result['findings'][:5]:  # Show first 5 findings
            print(f"  {finding['severity'].upper()}: {finding['message']}")
            print(f"    → {finding['suggestion']}")
            print()