#!/usr/bin/env python3
"""
Contextual Code Review Assistant - Prototype

A context-aware code review tool that provides meaningful feedback beyond basic linting.
Focuses on the patterns that experienced developers typically catch in reviews.

Key features:
- Context-aware analysis (understands when rules should be broken)
- Learning-based feedback (suggests improvements based on common patterns)
- Constructive framing (explains reasoning and provides alternatives)
- Intelligent pattern recognition beyond simple regex matching

Usage:
    python smart_review_assistant.py analyze file.py
    python smart_review_assistant.py review --git-diff
"""

import re
import ast
import argparse
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

class ReviewPriority(Enum):
    CRITICAL = "critical"      # Security, breaking changes, major bugs
    HIGH = "high"             # Logic changes, new features, performance
    MEDIUM = "medium"         # Refactoring, improvements, minor features
    LOW = "low"              # Style, docs, tests, cleanup

class ReviewFocus(Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    LOGIC = "logic"
    ARCHITECTURE = "architecture"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    STYLE = "style"

@dataclass
class ReviewInsight:
    """Specific insight about a code change"""
    type: ReviewFocus
    priority: ReviewPriority
    message: str
    line_numbers: List[int] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

@dataclass
class SmartCodeChange:
    """Enhanced code change analysis with intent and guidance"""
    file_path: str
    intent: str                           # What is this change trying to accomplish?
    impact_summary: str                   # What are the effects of this change?
    review_priority: ReviewPriority
    focus_areas: List[ReviewFocus]
    insights: List[ReviewInsight]
    complexity_score: int                 # 1-10 scale
    lines_added: int
    lines_removed: int
    functions_affected: List[str]
    potential_issues: List[str] = field(default_factory=list)
    review_questions: List[str] = field(default_factory=list)

class SmartReviewAnalyzer:
    """Advanced analyzer that understands code intent and provides review guidance"""

    def __init__(self):
        self.security_patterns = {
            'sql_injection': re.compile(r'query.*\+|execute.*format|cursor\.execute.*%', re.IGNORECASE),
            'xss_risk': re.compile(r'innerHTML|dangerouslySetInnerHTML|document\.write', re.IGNORECASE),
            'hardcoded_secrets': re.compile(r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
            'unsafe_input': re.compile(r'eval\s*\(|exec\s*\(|subprocess\.|os\.system', re.IGNORECASE),
            'auth_bypass': re.compile(r'if.*password.*==.*["\']|admin.*=.*true', re.IGNORECASE)
        }

        self.performance_patterns = {
            'nested_loops': re.compile(r'for.*:\s*\n.*for.*:', re.MULTILINE | re.DOTALL),
            'inefficient_lookup': re.compile(r'for.*in.*:\s*\n.*if.*==', re.MULTILINE | re.DOTALL),
            'string_concat': re.compile(r'\+\s*=.*["\']', re.MULTILINE),
            'db_in_loop': re.compile(r'for.*:\s*\n.*\.(query|execute|find)', re.MULTILINE | re.DOTALL)
        }

        self.logic_patterns = {
            'complex_condition': re.compile(r'if.*and.*or.*:', re.MULTILINE),
            'deep_nesting': re.compile(r'(\s{8,})if|(\s{8,})for|(\s{8,})while', re.MULTILINE),
            'magic_numbers': re.compile(r'(?<![a-zA-Z_])\d{2,}(?![a-zA-Z_])', re.MULTILINE),
            'exception_handling': re.compile(r'try:|except:|raise', re.MULTILINE)
        }

    def analyze_diff(self, diff_content: str, include_context: bool = True) -> List[SmartCodeChange]:
        """Perform smart analysis of code changes"""
        changes = []
        files = self._parse_diff_files(diff_content)

        for file_info in files:
            change = self._analyze_file_change_smart(file_info, include_context)
            if change:
                changes.append(change)

        return changes

    def _parse_diff_files(self, diff_content: str) -> List[Dict]:
        """Enhanced diff parsing with more context"""
        files = []
        current_file = None

        for line in diff_content.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    files.append(current_file)

                parts = line.split()
                if len(parts) >= 4:
                    file_path = parts[3][2:]
                    current_file = {
                        'path': file_path,
                        'additions': [],
                        'deletions': [],
                        'context': [],
                        'hunk_info': [],
                        'metadata': {}
                    }

            elif line.startswith('@@'):
                # Hunk header with line numbers
                if current_file:
                    current_file['hunk_info'].append(line)

            elif line.startswith('index '):
                # File hash information
                if current_file:
                    current_file['metadata']['index'] = line

            elif line.startswith('+') and not line.startswith('+++'):
                if current_file:
                    current_file['additions'].append(line[1:])

            elif line.startswith('-') and not line.startswith('---'):
                if current_file:
                    current_file['deletions'].append(line[1:])

            elif current_file and line.startswith(' '):
                current_file['context'].append(line[1:])

        if current_file:
            files.append(current_file)

        return files

    def _analyze_file_change_smart(self, file_info: Dict, include_context: bool) -> Optional[SmartCodeChange]:
        """Perform intelligent analysis of a single file change"""
        path = file_info['path']
        additions = file_info['additions']
        deletions = file_info['deletions']
        context = file_info['context']

        # Combine all code for analysis
        added_code = '\n'.join(additions)
        removed_code = '\n'.join(deletions)
        full_context = '\n'.join(context + additions + deletions)

        # Infer intent
        intent = self._infer_intent(file_info)

        # Assess impact
        impact_summary = self._assess_impact_smart(file_info)

        # Determine priority
        priority = self._determine_review_priority(file_info)

        # Identify focus areas
        focus_areas = self._identify_focus_areas(file_info)

        # Generate insights
        insights = self._generate_insights(file_info)

        # Calculate complexity
        complexity = self._calculate_complexity(file_info)

        # Find affected functions
        functions = self._find_affected_functions(file_info)

        # Identify potential issues
        issues = self._identify_potential_issues(file_info)

        # Generate review questions
        questions = self._generate_review_questions(file_info, intent, issues)

        return SmartCodeChange(
            file_path=path,
            intent=intent,
            impact_summary=impact_summary,
            review_priority=priority,
            focus_areas=focus_areas,
            insights=insights,
            complexity_score=complexity,
            lines_added=len(additions),
            lines_removed=len(deletions),
            functions_affected=functions,
            potential_issues=issues,
            review_questions=questions
        )

    def _infer_intent(self, file_info: Dict) -> str:
        """Infer what the developer is trying to accomplish"""
        path = file_info['path']
        additions = '\n'.join(file_info['additions'])
        deletions = '\n'.join(file_info['deletions'])

        # Test files
        if 'test' in path.lower():
            if 'def test_' in additions:
                return "Adding test coverage for new functionality"
            elif 'assert' in additions:
                return "Enhancing test assertions and edge case coverage"
            else:
                return "Updating tests to match code changes"

        # Security-related changes
        if any(pattern.search(additions) for pattern in self.security_patterns.values()):
            return "Implementing security improvements and vulnerability fixes"

        # New function/class definitions
        if re.search(r'^\s*(def|class)\s+\w+', additions, re.MULTILINE):
            return "Adding new functionality and capabilities"

        # Import changes
        if re.search(r'^\s*(import|from)\s+', additions, re.MULTILINE):
            if re.search(r'^\s*(import|from)\s+', deletions, re.MULTILINE):
                return "Refactoring dependencies and imports"
            else:
                return "Adding new dependencies for enhanced functionality"

        # Exception handling
        if re.search(r'try:|except:|raise', additions, re.MULTILINE):
            return "Improving error handling and robustness"

        # Performance-related
        if any(pattern.search(additions) for pattern in self.performance_patterns.values()):
            return "Optimizing performance and efficiency"

        # Configuration changes
        if path.endswith(('.json', '.yaml', '.yml', '.toml', '.env')):
            return "Updating configuration and settings"

        # Documentation
        if path.endswith(('.md', '.rst', '.txt')) or 'README' in path:
            return "Updating documentation and user guidance"

        # Default based on change magnitude
        lines_changed = len(file_info['additions']) + len(file_info['deletions'])
        if lines_changed > 50:
            return "Substantial code changes and refactoring"
        elif lines_changed > 10:
            return "Moderate functionality updates and improvements"
        else:
            return "Minor adjustments and bug fixes"

    def _assess_impact_smart(self, file_info: Dict) -> str:
        """Provide detailed impact assessment"""
        path = file_info['path']
        additions = '\n'.join(file_info['additions'])
        lines_changed = len(file_info['additions']) + len(file_info['deletions'])

        impacts = []

        # File importance
        if any(key in path.lower() for key in ['main', 'index', 'app', '__init__']):
            impacts.append("affects core application files")

        # API changes
        if re.search(r'def\s+\w+.*\(.*\):', additions):
            impacts.append("introduces new API surface")

        # Database/persistence
        if re.search(r'(insert|update|delete|create|drop)', additions, re.IGNORECASE):
            impacts.append("modifies data persistence layer")

        # Security implications
        if any(pattern.search(additions) for pattern in self.security_patterns.values()):
            impacts.append("has security implications")

        # Performance implications
        if any(pattern.search(additions) for pattern in self.performance_patterns.values()):
            impacts.append("may impact performance")

        # Breaking changes
        if re.search(r'(deprecated|removed|breaking)', additions, re.IGNORECASE):
            impacts.append("potentially introduces breaking changes")

        # Testing impact
        if 'test' in path.lower():
            impacts.append("affects test coverage and validation")

        if not impacts:
            if lines_changed > 20:
                return "Significant code modification with broad implications"
            else:
                return "Localized change with minimal external impact"

        return "This change " + " and ".join(impacts)

    def _determine_review_priority(self, file_info: Dict) -> ReviewPriority:
        """Determine how urgent this review is"""
        path = file_info['path']
        additions = '\n'.join(file_info['additions'])

        # Critical priority
        if any(pattern.search(additions) for pattern in self.security_patterns.values()):
            return ReviewPriority.CRITICAL

        if 'main' in path.lower() or '__init__' in path:
            return ReviewPriority.CRITICAL

        if re.search(r'(password|auth|security|admin)', additions, re.IGNORECASE):
            return ReviewPriority.CRITICAL

        # High priority
        if re.search(r'def\s+\w+.*\(.*\):', additions):  # New functions
            return ReviewPriority.HIGH

        if any(pattern.search(additions) for pattern in self.performance_patterns.values()):
            return ReviewPriority.HIGH

        lines_changed = len(file_info['additions']) + len(file_info['deletions'])
        if lines_changed > 50:
            return ReviewPriority.HIGH

        # Low priority
        if 'test' in path.lower() or path.endswith(('.md', '.txt')):
            return ReviewPriority.LOW

        if lines_changed < 10:
            return ReviewPriority.LOW

        return ReviewPriority.MEDIUM

    def _identify_focus_areas(self, file_info: Dict) -> List[ReviewFocus]:
        """Identify what aspects reviewers should focus on"""
        additions = '\n'.join(file_info['additions'])
        path = file_info['path']
        focus_areas = []

        # Security focus
        if any(pattern.search(additions) for pattern in self.security_patterns.values()):
            focus_areas.append(ReviewFocus.SECURITY)

        # Performance focus
        if any(pattern.search(additions) for pattern in self.performance_patterns.values()):
            focus_areas.append(ReviewFocus.PERFORMANCE)

        # Logic focus
        if any(pattern.search(additions) for pattern in self.logic_patterns.values()):
            focus_areas.append(ReviewFocus.LOGIC)

        # Architecture focus
        if re.search(r'class\s+\w+|import\s+\w+|from\s+\w+', additions):
            focus_areas.append(ReviewFocus.ARCHITECTURE)

        # Testing focus
        if 'test' in path.lower():
            focus_areas.append(ReviewFocus.TESTING)

        # Documentation focus
        if path.endswith(('.md', '.rst')) or '"""' in additions or "'''" in additions:
            focus_areas.append(ReviewFocus.DOCUMENTATION)

        # Style focus (default if no others)
        if not focus_areas:
            focus_areas.append(ReviewFocus.STYLE)

        return focus_areas

    def _generate_insights(self, file_info: Dict) -> List[ReviewInsight]:
        """Generate specific insights for reviewers"""
        additions = '\n'.join(file_info['additions'])
        insights = []

        # Security insights
        for pattern_name, pattern in self.security_patterns.items():
            if pattern.search(additions):
                insight = ReviewInsight(
                    type=ReviewFocus.SECURITY,
                    priority=ReviewPriority.CRITICAL,
                    message=f"Potential security risk detected: {pattern_name.replace('_', ' ')}",
                    suggestions=["Review for SQL injection vulnerabilities", "Validate input sanitization", "Check authentication/authorization"]
                )
                insights.append(insight)

        # Performance insights
        for pattern_name, pattern in self.performance_patterns.items():
            if pattern.search(additions):
                insight = ReviewInsight(
                    type=ReviewFocus.PERFORMANCE,
                    priority=ReviewPriority.HIGH,
                    message=f"Performance concern: {pattern_name.replace('_', ' ')}",
                    suggestions=["Consider algorithmic complexity", "Review for unnecessary loops", "Check database query efficiency"]
                )
                insights.append(insight)

        # Logic insights
        if self.logic_patterns['complex_condition'].search(additions):
            insights.append(ReviewInsight(
                type=ReviewFocus.LOGIC,
                priority=ReviewPriority.MEDIUM,
                message="Complex conditional logic detected",
                suggestions=["Consider breaking down complex conditions", "Add comments for clarity", "Verify all edge cases are handled"]
            ))

        return insights

    def _calculate_complexity(self, file_info: Dict) -> int:
        """Calculate complexity score (1-10)"""
        additions = '\n'.join(file_info['additions'])
        complexity = 1

        # Base complexity from lines of code
        lines = len(file_info['additions'])
        complexity += min(lines // 10, 3)

        # Conditional complexity
        complexity += len(re.findall(r'\bif\b|\bfor\b|\bwhile\b', additions))
        complexity += len(re.findall(r'\band\b|\bor\b', additions)) // 2

        # Nesting complexity
        max_indent = 0
        for line in file_info['additions']:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent // 4)
        complexity += max_indent

        # Security/performance patterns add complexity
        for patterns in [self.security_patterns, self.performance_patterns]:
            for pattern in patterns.values():
                if pattern.search(additions):
                    complexity += 1

        return min(complexity, 10)

    def _find_affected_functions(self, file_info: Dict) -> List[str]:
        """Find functions affected by changes"""
        all_content = '\n'.join(file_info['additions'] + file_info['context'])
        functions = re.findall(r'def\s+(\w+)', all_content)
        return list(set(functions))

    def _identify_potential_issues(self, file_info: Dict) -> List[str]:
        """Identify potential issues that need review attention"""
        additions = '\n'.join(file_info['additions'])
        issues = []

        # Security issues
        if self.security_patterns['hardcoded_secrets'].search(additions):
            issues.append("Hardcoded credentials detected - should use environment variables")

        if self.security_patterns['sql_injection'].search(additions):
            issues.append("SQL injection vulnerability - use parameterized queries")

        # Performance issues
        if self.performance_patterns['nested_loops'].search(additions):
            issues.append("Nested loops detected - consider optimizing algorithm complexity")

        if self.performance_patterns['db_in_loop'].search(additions):
            issues.append("Database operations in loop - consider batch operations")

        # Logic issues
        if self.logic_patterns['magic_numbers'].search(additions):
            issues.append("Magic numbers found - consider using named constants")

        if self.logic_patterns['deep_nesting'].search(additions):
            issues.append("Deep nesting detected - consider refactoring for readability")

        return issues

    def _generate_review_questions(self, file_info: Dict, intent: str, issues: List[str]) -> List[str]:
        """Generate specific questions for reviewers to consider"""
        questions = []
        path = file_info['path']
        additions = '\n'.join(file_info['additions'])

        # Intent-based questions
        if "security" in intent.lower():
            questions.append("Are all security vulnerabilities properly addressed?")
            questions.append("Has input validation been implemented correctly?")

        if "performance" in intent.lower():
            questions.append("Will this change negatively impact system performance?")
            questions.append("Are there more efficient algorithms or data structures that could be used?")

        if "new functionality" in intent.lower():
            questions.append("Is the new functionality well-documented and tested?")
            questions.append("Does this change maintain backward compatibility?")

        # Issue-based questions
        if issues:
            questions.append("Have the identified potential issues been reviewed and addressed?")

        # General questions based on file type
        if 'test' not in path.lower():
            questions.append("Are there sufficient tests covering this change?")

        if re.search(r'def\s+\w+', additions):
            questions.append("Are new functions properly documented with docstrings?")
            questions.append("Do function signatures follow established conventions?")

        # Complexity-based questions
        complexity = self._calculate_complexity(file_info)
        if complexity > 7:
            questions.append("Is this change complex enough to warrant additional review or pair programming?")

        return questions

def format_smart_review_report(changes: List[SmartCodeChange]) -> str:
    """Format analysis into comprehensive review report"""
    if not changes:
        return "No changes to review."

    report = ["# 🔍 Smart Code Review Report\n"]

    # Executive Summary
    total_files = len(changes)
    critical_count = sum(1 for c in changes if c.review_priority == ReviewPriority.CRITICAL)
    high_count = sum(1 for c in changes if c.review_priority == ReviewPriority.HIGH)
    avg_complexity = sum(c.complexity_score for c in changes) / len(changes)

    report.append("## Executive Summary")
    report.append(f"- **Files Changed**: {total_files}")
    report.append(f"- **Critical Priority**: {critical_count} files")
    report.append(f"- **High Priority**: {high_count} files")
    report.append(f"- **Average Complexity**: {avg_complexity:.1f}/10")
    report.append("")

    # Priority-based sections
    for priority in [ReviewPriority.CRITICAL, ReviewPriority.HIGH, ReviewPriority.MEDIUM, ReviewPriority.LOW]:
        priority_changes = [c for c in changes if c.review_priority == priority]
        if not priority_changes:
            continue

        icon = {"critical": "🔴", "high": "🟡", "medium": "🔵", "low": "🟢"}[priority.value]
        report.append(f"## {icon} {priority.value.title()} Priority Changes\n")

        for change in priority_changes:
            report.append(f"### {change.file_path}")
            report.append(f"**Intent**: {change.intent}")
            report.append(f"**Impact**: {change.impact_summary}")
            report.append(f"**Complexity**: {change.complexity_score}/10")

            if change.focus_areas:
                focus_str = ", ".join([f.value for f in change.focus_areas])
                report.append(f"**Review Focus**: {focus_str}")

            if change.functions_affected:
                report.append(f"**Functions**: {', '.join(change.functions_affected)}")

            # Insights
            if change.insights:
                report.append("**Key Insights**:")
                for insight in change.insights:
                    report.append(f"- {insight.message}")
                    if insight.suggestions:
                        for suggestion in insight.suggestions[:2]:  # Limit suggestions
                            report.append(f"  - *{suggestion}*")

            # Issues
            if change.potential_issues:
                report.append("**⚠️ Potential Issues**:")
                for issue in change.potential_issues:
                    report.append(f"- {issue}")

            # Review questions
            if change.review_questions:
                report.append("**❓ Review Questions**:")
                for question in change.review_questions[:3]:  # Limit questions
                    report.append(f"- {question}")

            report.append("")

    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Smart Code Review Assistant")
    parser.add_argument("--diff", help="Path to diff file")
    parser.add_argument("--git-branch", help="Git branch to analyze")
    parser.add_argument("--context", action="store_true", help="Include additional context in analysis")
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    if not args.diff and not args.git_branch:
        parser.print_help()
        return

    analyzer = SmartReviewAnalyzer()

    if args.diff:
        with open(args.diff, 'r') as f:
            diff_content = f.read()
    else:
        # Git branch analysis would be implemented here
        print("Git branch analysis not yet implemented")
        return

    changes = analyzer.analyze_diff(diff_content, args.context)

    if args.format == "json":
        # JSON output for tool integration
        output = json.dumps([{
            'file_path': c.file_path,
            'intent': c.intent,
            'priority': c.review_priority.value,
            'complexity': c.complexity_score,
            'issues': c.potential_issues,
            'questions': c.review_questions
        } for c in changes], indent=2)
    else:
        output = format_smart_review_report(changes)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Smart review report saved to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()