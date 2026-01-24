#!/usr/bin/env python3
"""
Code Review Analyzer - Prototype
Generates natural language explanations for code changes

This tool analyzes git diffs or code changes and provides human-readable
summaries that focus on the intent and impact of changes rather than just
the mechanical diff.

Usage:
    python code_review_analyzer.py --diff path/to/diff.txt
    python code_review_analyzer.py --git-commit abc123
"""

import re
import argparse
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ChangeType(Enum):
    ADDITION = "addition"
    DELETION = "deletion"
    MODIFICATION = "modification"
    REFACTOR = "refactor"
    BUG_FIX = "bug_fix"
    FEATURE = "feature"
    STYLE = "style"

@dataclass
class CodeChange:
    file_path: str
    change_type: ChangeType
    lines_added: int
    lines_removed: int
    functions_affected: List[str]
    summary: str
    impact_level: str  # "low", "medium", "high"

class CodeAnalyzer:
    """Analyzes code changes and generates explanations"""

    def __init__(self):
        # Patterns to identify different types of changes
        self.patterns = {
            'function_def': re.compile(r'^\s*def\s+(\w+)', re.MULTILINE),
            'class_def': re.compile(r'^\s*class\s+(\w+)', re.MULTILINE),
            'import_change': re.compile(r'^\s*(import|from)\s+', re.MULTILINE),
            'test_file': re.compile(r'test_|_test\.py$|tests/'),
            'config_file': re.compile(r'\.(json|yaml|yml|toml|ini|env)$'),
            'documentation': re.compile(r'\.(md|rst|txt)$|README|CHANGELOG'),
        }

    def analyze_diff(self, diff_content: str) -> List[CodeChange]:
        """Parse a git diff and extract meaningful changes"""
        changes = []

        # Simple diff parsing - in reality we'd use a proper git diff parser
        files = self._parse_diff_files(diff_content)

        for file_info in files:
            change = self._analyze_file_change(file_info)
            if change:
                changes.append(change)

        return changes

    def _parse_diff_files(self, diff_content: str) -> List[Dict]:
        """Extract file changes from diff - simplified implementation"""
        # This is a simplified parser - real implementation would be more robust
        files = []
        current_file = None

        for line in diff_content.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    files.append(current_file)

                # Extract file path
                parts = line.split()
                if len(parts) >= 4:
                    file_path = parts[3][2:]  # Remove 'b/' prefix
                    current_file = {
                        'path': file_path,
                        'additions': [],
                        'deletions': [],
                        'context': []
                    }
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

    def _analyze_file_change(self, file_info: Dict) -> Optional[CodeChange]:
        """Analyze a single file's changes"""
        path = file_info['path']
        additions = file_info['additions']
        deletions = file_info['deletions']

        # Determine change type based on patterns
        change_type = self._determine_change_type(file_info)

        # Find affected functions
        affected_functions = self._find_affected_functions(file_info)

        # Generate summary
        summary = self._generate_summary(file_info, change_type, affected_functions)

        # Determine impact level
        impact_level = self._assess_impact(file_info, change_type)

        return CodeChange(
            file_path=path,
            change_type=change_type,
            lines_added=len(additions),
            lines_removed=len(deletions),
            functions_affected=affected_functions,
            summary=summary,
            impact_level=impact_level
        )

    def _determine_change_type(self, file_info: Dict) -> ChangeType:
        """Determine the type of change based on content analysis"""
        path = file_info['path']
        additions = '\n'.join(file_info['additions'])
        deletions = '\n'.join(file_info['deletions'])

        # Test file changes
        if self.patterns['test_file'].search(path):
            return ChangeType.FEATURE if additions else ChangeType.BUG_FIX

        # Config changes
        if self.patterns['config_file'].search(path):
            return ChangeType.MODIFICATION

        # Documentation changes
        if self.patterns['documentation'].search(path):
            return ChangeType.STYLE

        # New functions/classes
        new_functions = self.patterns['function_def'].findall(additions)
        new_classes = self.patterns['class_def'].findall(additions)

        if new_functions or new_classes:
            return ChangeType.FEATURE

        # Import changes suggest refactoring
        if self.patterns['import_change'].search(additions) or self.patterns['import_change'].search(deletions):
            return ChangeType.REFACTOR

        # Default to modification
        return ChangeType.MODIFICATION

    def _find_affected_functions(self, file_info: Dict) -> List[str]:
        """Find functions that were modified"""
        functions = []
        all_content = '\n'.join(file_info['additions'] + file_info['deletions'] + file_info['context'])

        # Find function definitions in the changed area
        matches = self.patterns['function_def'].findall(all_content)
        functions.extend(matches)

        return list(set(functions))  # Remove duplicates

    def _generate_summary(self, file_info: Dict, change_type: ChangeType, functions: List[str]) -> str:
        """Generate a human-readable summary of the change"""
        path = file_info['path']
        lines_added = len(file_info['additions'])
        lines_removed = len(file_info['deletions'])

        # Base summary based on change type
        if change_type == ChangeType.FEATURE:
            base = f"Added new functionality to {path}"
        elif change_type == ChangeType.BUG_FIX:
            base = f"Fixed issue in {path}"
        elif change_type == ChangeType.REFACTOR:
            base = f"Refactored code structure in {path}"
        else:
            base = f"Modified {path}"

        # Add function details if available
        if functions:
            if len(functions) == 1:
                base += f", affecting the {functions[0]}() function"
            elif len(functions) <= 3:
                base += f", affecting functions: {', '.join(functions)}"
            else:
                base += f", affecting {len(functions)} functions"

        # Add magnitude info
        if lines_added > 20 or lines_removed > 20:
            base += f" (significant change: +{lines_added}/-{lines_removed} lines)"
        elif lines_added > 0 and lines_removed > 0:
            base += f" (+{lines_added}/-{lines_removed} lines)"
        elif lines_added > 0:
            base += f" (+{lines_added} lines)"
        elif lines_removed > 0:
            base += f" (-{lines_removed} lines)"

        return base

    def _assess_impact(self, file_info: Dict, change_type: ChangeType) -> str:
        """Assess the potential impact of the change"""
        lines_changed = len(file_info['additions']) + len(file_info['deletions'])
        path = file_info['path']

        # High impact indicators
        if 'main.py' in path or '__init__.py' in path:
            return "high"
        if lines_changed > 50:
            return "high"
        if change_type == ChangeType.REFACTOR and lines_changed > 20:
            return "high"

        # Low impact indicators
        if self.patterns['test_file'].search(path):
            return "low"
        if self.patterns['documentation'].search(path):
            return "low"
        if lines_changed < 10:
            return "low"

        return "medium"

def format_analysis_report(changes: List[CodeChange]) -> str:
    """Format the analysis results into a readable report"""
    if not changes:
        return "No significant changes detected."

    report = ["# Code Review Summary\n"]

    # Group by impact level
    high_impact = [c for c in changes if c.impact_level == "high"]
    medium_impact = [c for c in changes if c.impact_level == "medium"]
    low_impact = [c for c in changes if c.impact_level == "low"]

    if high_impact:
        report.append("## High Impact Changes 🔴")
        for change in high_impact:
            report.append(f"- **{change.file_path}**: {change.summary}")
        report.append("")

    if medium_impact:
        report.append("## Medium Impact Changes 🟡")
        for change in medium_impact:
            report.append(f"- **{change.file_path}**: {change.summary}")
        report.append("")

    if low_impact:
        report.append("## Low Impact Changes 🟢")
        for change in low_impact:
            report.append(f"- **{change.file_path}**: {change.summary}")
        report.append("")

    # Summary stats
    total_additions = sum(c.lines_added for c in changes)
    total_deletions = sum(c.lines_removed for c in changes)

    report.append("## Summary")
    report.append(f"- **Files changed**: {len(changes)}")
    report.append(f"- **Total additions**: {total_additions} lines")
    report.append(f"- **Total deletions**: {total_deletions} lines")
    report.append(f"- **Net change**: {total_additions - total_deletions:+d} lines")

    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Analyze code changes and generate explanations")
    parser.add_argument("--diff", help="Path to diff file")
    parser.add_argument("--git-commit", help="Git commit hash to analyze")
    parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    if not args.diff and not args.git_commit:
        parser.print_help()
        return

    analyzer = CodeAnalyzer()

    if args.diff:
        with open(args.diff, 'r') as f:
            diff_content = f.read()
    else:
        # In a real implementation, we'd use git to get the commit diff
        print("Git commit analysis not yet implemented")
        return

    changes = analyzer.analyze_diff(diff_content)
    report = format_analysis_report(changes)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Analysis saved to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()