#!/usr/bin/env python3
"""
CI/CD Integration System for Code Analysis Tool

Provides enterprise-grade integration capabilities for automated code quality monitoring
in continuous integration/continuous deployment pipelines. Supports multiple CI platforms
and includes configurable thresholds, automated reporting, and trend analysis.

Author: Bob (Claude Code)
Created: 2026-01-23
"""

import json
import os
import sys
import subprocess
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import tempfile

# Import our analysis tools
from ast_analyzer import ASTAnalyzer
from complexity_analyzer import ComplexityAnalyzer
from dashboard_generator import DashboardGenerator


@dataclass
class AnalysisResult:
    """Represents the results of a code analysis run."""
    timestamp: str
    project_path: str
    total_files: int
    total_functions: int
    total_classes: int
    avg_cyclomatic_complexity: float
    avg_cognitive_complexity: float
    max_complexity_function: str
    max_complexity_value: float
    complexity_violations: List[Dict[str, Any]]
    quality_score: float


@dataclass
class QualityThresholds:
    """Configurable quality thresholds for CI/CD integration."""
    max_cyclomatic_complexity: int = 10
    max_cognitive_complexity: int = 15
    max_function_lines: int = 50
    min_quality_score: float = 7.0
    max_complexity_violations: int = 5


class CIIntegrationManager:
    """
    Manages CI/CD integration for automated code quality monitoring.

    Provides functionality for:
    - Running analysis in CI environments
    - Enforcing quality gates
    - Generating automated reports
    - Tracking complexity trends over time
    - Integration with popular CI platforms (GitHub Actions, GitLab CI, Jenkins)
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize CI integration manager.

        Args:
            config_path: Optional path to configuration file
        """
        self.ast_analyzer = ASTAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.dashboard_generator = DashboardGenerator()

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.config = self._load_config(config_path)
        self.thresholds = QualityThresholds(**self.config.get('thresholds', {}))

        # History tracking
        self.history_file = Path(self.config.get('history_file', '.code_analysis_history.json'))

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)

        # Default configuration
        return {
            'thresholds': {
                'max_cyclomatic_complexity': 10,
                'max_cognitive_complexity': 15,
                'max_function_lines': 50,
                'min_quality_score': 7.0,
                'max_complexity_violations': 5
            },
            'exclude_patterns': ['test_*.py', '*_test.py', 'tests/', '__pycache__/'],
            'include_patterns': ['*.py'],
            'report_format': 'json',
            'history_file': '.code_analysis_history.json'
        }

    def analyze_project_for_ci(self, project_path: str) -> AnalysisResult:
        """
        Run complete project analysis optimized for CI environments.

        Args:
            project_path: Path to project root

        Returns:
            AnalysisResult containing all analysis metrics
        """
        self.logger.info(f"Starting CI analysis of project: {project_path}")

        # Collect all Python files
        python_files = self._collect_python_files(project_path)
        self.logger.info(f"Found {len(python_files)} Python files to analyze")

        all_functions = []
        all_classes = []
        complexity_violations = []

        for file_path in python_files:
            try:
                # AST Analysis
                ast_result = self.ast_analyzer.analyze_file(file_path)
                if ast_result:
                    all_functions.extend(ast_result['functions'])
                    all_classes.extend(ast_result['classes'])

                    # Complexity Analysis
                    complexity_result = self.complexity_analyzer.analyze_file(file_path)
                    if complexity_result and complexity_result['functions']:
                        for func_analysis in complexity_result['functions']:
                            # Check for violations
                            violations = self._check_function_violations(func_analysis, file_path)
                            complexity_violations.extend(violations)

            except Exception as e:
                self.logger.warning(f"Error analyzing {file_path}: {e}")
                continue

        # Calculate metrics
        cyclomatic_complexities = []
        cognitive_complexities = []
        max_complexity_func = None
        max_complexity_val = 0

        for file_path in python_files:
            try:
                complexity_result = self.complexity_analyzer.analyze_file(file_path)
                if complexity_result and complexity_result['functions']:
                    for func in complexity_result['functions']:
                        cyclomatic_complexities.append(func['cyclomatic_complexity'])
                        cognitive_complexities.append(func['cognitive_complexity'])

                        if func['cyclomatic_complexity'] > max_complexity_val:
                            max_complexity_val = func['cyclomatic_complexity']
                            max_complexity_func = f"{func['name']} in {Path(file_path).name}"
            except Exception:
                continue

        # Calculate quality score (0-10 scale)
        quality_score = self._calculate_quality_score(
            cyclomatic_complexities, cognitive_complexities, complexity_violations
        )

        result = AnalysisResult(
            timestamp=datetime.now().isoformat(),
            project_path=project_path,
            total_files=len(python_files),
            total_functions=len(all_functions),
            total_classes=len(all_classes),
            avg_cyclomatic_complexity=sum(cyclomatic_complexities) / len(cyclomatic_complexities) if cyclomatic_complexities else 0,
            avg_cognitive_complexity=sum(cognitive_complexities) / len(cognitive_complexities) if cognitive_complexities else 0,
            max_complexity_function=max_complexity_func or "None",
            max_complexity_value=max_complexity_val,
            complexity_violations=complexity_violations,
            quality_score=quality_score
        )

        self.logger.info(f"Analysis complete. Quality score: {quality_score:.2f}/10")
        return result

    def _collect_python_files(self, project_path: str) -> List[str]:
        """Collect all Python files in project based on include/exclude patterns."""
        python_files = []
        project_path = Path(project_path)

        exclude_patterns = self.config.get('exclude_patterns', [])

        for py_file in project_path.rglob('*.py'):
            # Check exclusion patterns
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(py_file) or py_file.match(pattern):
                    should_exclude = True
                    break

            if not should_exclude:
                python_files.append(str(py_file))

        return python_files

    def _check_function_violations(self, func_analysis: Dict[str, Any], file_path: str) -> List[Dict[str, Any]]:
        """Check function against quality thresholds."""
        violations = []

        if func_analysis['cyclomatic_complexity'] > self.thresholds.max_cyclomatic_complexity:
            violations.append({
                'type': 'cyclomatic_complexity',
                'function': func_analysis['name'],
                'file': Path(file_path).name,
                'value': func_analysis['cyclomatic_complexity'],
                'threshold': self.thresholds.max_cyclomatic_complexity,
                'severity': 'high' if func_analysis['cyclomatic_complexity'] > self.thresholds.max_cyclomatic_complexity * 1.5 else 'medium'
            })

        if func_analysis['cognitive_complexity'] > self.thresholds.max_cognitive_complexity:
            violations.append({
                'type': 'cognitive_complexity',
                'function': func_analysis['name'],
                'file': Path(file_path).name,
                'value': func_analysis['cognitive_complexity'],
                'threshold': self.thresholds.max_cognitive_complexity,
                'severity': 'high' if func_analysis['cognitive_complexity'] > self.thresholds.max_cognitive_complexity * 1.5 else 'medium'
            })

        if func_analysis['lines'] > self.thresholds.max_function_lines:
            violations.append({
                'type': 'function_length',
                'function': func_analysis['name'],
                'file': Path(file_path).name,
                'value': func_analysis['lines'],
                'threshold': self.thresholds.max_function_lines,
                'severity': 'medium'
            })

        return violations

    def _calculate_quality_score(self, cyclomatic: List[float], cognitive: List[float], violations: List[Dict]) -> float:
        """Calculate overall quality score on 0-10 scale."""
        if not cyclomatic or not cognitive:
            return 5.0  # Neutral score for empty projects

        # Base score starts at 10
        score = 10.0

        # Penalty for high average complexity
        avg_cyclomatic = sum(cyclomatic) / len(cyclomatic)
        avg_cognitive = sum(cognitive) / len(cognitive)

        # Deduct points for complexity
        if avg_cyclomatic > 5:
            score -= min(2.0, (avg_cyclomatic - 5) * 0.2)

        if avg_cognitive > 8:
            score -= min(2.0, (avg_cognitive - 8) * 0.15)

        # Deduct points for violations
        high_severity_violations = sum(1 for v in violations if v.get('severity') == 'high')
        medium_severity_violations = sum(1 for v in violations if v.get('severity') == 'medium')

        score -= high_severity_violations * 0.5
        score -= medium_severity_violations * 0.25

        return max(0.0, min(10.0, score))

    def check_quality_gate(self, result: AnalysisResult) -> Tuple[bool, List[str]]:
        """
        Check if analysis result passes quality gate.

        Returns:
            Tuple of (passed, failure_reasons)
        """
        failures = []

        if result.quality_score < self.thresholds.min_quality_score:
            failures.append(f"Quality score {result.quality_score:.2f} below threshold {self.thresholds.min_quality_score}")

        if len(result.complexity_violations) > self.thresholds.max_complexity_violations:
            failures.append(f"Too many complexity violations: {len(result.complexity_violations)} > {self.thresholds.max_complexity_violations}")

        high_severity_violations = sum(1 for v in result.complexity_violations if v.get('severity') == 'high')
        if high_severity_violations > 0:
            failures.append(f"High severity violations found: {high_severity_violations}")

        return len(failures) == 0, failures

    def save_analysis_history(self, result: AnalysisResult) -> None:
        """Save analysis result to history for trend tracking."""
        history = []

        # Load existing history
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading history: {e}")

        # Add new result
        history.append(asdict(result))

        # Keep only last 100 entries
        history = history[-100:]

        # Save updated history
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")

    def generate_ci_report(self, result: AnalysisResult, format: str = 'json') -> str:
        """Generate CI-friendly report in specified format."""
        if format == 'json':
            return json.dumps(asdict(result), indent=2)

        elif format == 'junit':
            return self._generate_junit_report(result)

        elif format == 'markdown':
            return self._generate_markdown_report(result)

        else:
            raise ValueError(f"Unsupported report format: {format}")

    def _generate_junit_report(self, result: AnalysisResult) -> str:
        """Generate JUnit XML report for CI systems."""
        passed, failures = self.check_quality_gate(result)

        junit_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Code Quality Analysis" tests="1" failures="{0 if passed else 1}" time="0">
    <testcase name="Quality Gate" classname="CodeAnalysis">
        {"" if passed else f'<failure message="Quality gate failed">{chr(10).join(failures)}</failure>'}
    </testcase>
</testsuite>"""
        return junit_xml

    def _generate_markdown_report(self, result: AnalysisResult) -> str:
        """Generate Markdown report for readable CI output."""
        passed, failures = self.check_quality_gate(result)
        status_emoji = "✅" if passed else "❌"

        report = f"""# Code Quality Analysis Report {status_emoji}

**Analysis Date:** {result.timestamp}
**Quality Score:** {result.quality_score:.2f}/10

## 📊 Project Overview
- **Files Analyzed:** {result.total_files}
- **Functions Found:** {result.total_functions}
- **Classes Found:** {result.total_classes}

## 🧮 Complexity Metrics
- **Average Cyclomatic Complexity:** {result.avg_cyclomatic_complexity:.2f}
- **Average Cognitive Complexity:** {result.avg_cognitive_complexity:.2f}
- **Most Complex Function:** {result.max_complexity_function} (complexity: {result.max_complexity_value})

## ⚠️ Quality Gate Status
{"**PASSED** - All quality checks passed!" if passed else "**FAILED** - Quality gate violations detected:"}

"""
        if failures:
            for failure in failures:
                report += f"- {failure}\n"

        if result.complexity_violations:
            report += f"""
## 🚨 Complexity Violations ({len(result.complexity_violations)})

| Function | File | Type | Value | Threshold | Severity |
|----------|------|------|-------|-----------|----------|
"""
            for violation in result.complexity_violations[:10]:  # Show first 10
                report += f"| {violation['function']} | {violation['file']} | {violation['type']} | {violation['value']} | {violation['threshold']} | {violation['severity']} |\n"

            if len(result.complexity_violations) > 10:
                report += f"\n*... and {len(result.complexity_violations) - 10} more violations*\n"

        return report


def main():
    """Command-line interface for CI integration."""
    parser = argparse.ArgumentParser(description='CI/CD Integration for Code Analysis')
    parser.add_argument('project_path', help='Path to project root')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--format', choices=['json', 'junit', 'markdown'], default='json',
                       help='Report output format')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--quality-gate', action='store_true',
                       help='Exit with non-zero code if quality gate fails')
    parser.add_argument('--save-history', action='store_true',
                       help='Save analysis results to history file')

    args = parser.parse_args()

    # Initialize CI manager
    ci_manager = CIIntegrationManager(args.config)

    # Run analysis
    try:
        result = ci_manager.analyze_project_for_ci(args.project_path)

        # Save to history if requested
        if args.save_history:
            ci_manager.save_analysis_history(result)

        # Generate report
        report = ci_manager.generate_ci_report(result, args.format)

        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report written to {args.output}")
        else:
            print(report)

        # Check quality gate if requested
        if args.quality_gate:
            passed, failures = ci_manager.check_quality_gate(result)
            if not passed:
                print("\n❌ Quality gate FAILED!")
                for failure in failures:
                    print(f"  - {failure}")
                sys.exit(1)
            else:
                print("\n✅ Quality gate PASSED!")

    except Exception as e:
        print(f"❌ Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()