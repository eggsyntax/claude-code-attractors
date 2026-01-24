#!/usr/bin/env python3
"""
CI/CD Integration for Code Analysis Tool

This module provides CI/CD pipeline integration capabilities for continuous
code health monitoring. It supports multiple CI platforms and provides
actionable feedback through various channels.

Key Features:
- Threshold-based pass/fail decisions
- Trend analysis across builds
- Integration with popular CI platforms
- Notification systems (Slack, GitHub comments, etc.)
- Baseline comparison for regression detection
"""

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import subprocess
import requests


@dataclass
class AnalysisThresholds:
    """Configurable thresholds for CI/CD decision making."""
    max_complexity_per_function: int = 15
    max_complexity_increase: int = 5
    max_new_high_complexity_functions: int = 3
    max_technical_debt_ratio: float = 0.15
    min_test_coverage: float = 0.80
    max_dependency_depth: int = 8


@dataclass
class BuildContext:
    """Context information for the current build."""
    branch: str
    commit_hash: str
    pr_number: Optional[int]
    base_branch: str
    build_id: str
    ci_platform: str  # github, gitlab, jenkins, etc.


@dataclass
class AnalysisResult:
    """Results from code analysis with CI-relevant metrics."""
    total_functions: int
    high_complexity_functions: int
    average_complexity: float
    technical_debt_ratio: float
    complexity_hotspots: List[Dict]
    new_complexity_violations: List[Dict]
    regression_analysis: Dict
    recommendations: List[str]


class CIPipeline:
    """Main CI/CD integration orchestrator."""

    def __init__(self, config_path: str = "code_analysis_ci.json"):
        self.config = self._load_config(config_path)
        self.thresholds = AnalysisThresholds(**self.config.get("thresholds", {}))
        self.build_context = self._detect_build_context()

    def _load_config(self, config_path: str) -> Dict:
        """Load CI configuration from file or environment."""
        if os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)

        # Fallback to environment variables
        return {
            "thresholds": {},
            "notifications": {
                "slack_webhook": os.getenv("SLACK_WEBHOOK_URL"),
                "github_token": os.getenv("GITHUB_TOKEN")
            },
            "baseline_storage": os.getenv("BASELINE_STORAGE_PATH", "./baselines/")
        }

    def _detect_build_context(self) -> BuildContext:
        """Auto-detect CI environment and extract build context."""
        # GitHub Actions
        if os.getenv("GITHUB_ACTIONS"):
            return BuildContext(
                branch=os.getenv("GITHUB_REF_NAME", "unknown"),
                commit_hash=os.getenv("GITHUB_SHA", "unknown")[:8],
                pr_number=int(os.getenv("GITHUB_PR_NUMBER", 0)) or None,
                base_branch=os.getenv("GITHUB_BASE_REF", "main"),
                build_id=os.getenv("GITHUB_RUN_ID", "unknown"),
                ci_platform="github"
            )

        # GitLab CI
        elif os.getenv("GITLAB_CI"):
            return BuildContext(
                branch=os.getenv("CI_COMMIT_REF_NAME", "unknown"),
                commit_hash=os.getenv("CI_COMMIT_SHA", "unknown")[:8],
                pr_number=int(os.getenv("CI_MERGE_REQUEST_IID", 0)) or None,
                base_branch=os.getenv("CI_MERGE_REQUEST_TARGET_BRANCH_NAME", "main"),
                build_id=os.getenv("CI_PIPELINE_ID", "unknown"),
                ci_platform="gitlab"
            )

        # Default/local development
        else:
            try:
                branch = subprocess.check_output(
                    ["git", "branch", "--show-current"],
                    text=True
                ).strip()
                commit = subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"],
                    text=True
                ).strip()
            except subprocess.CalledProcessError:
                branch, commit = "unknown", "unknown"

            return BuildContext(
                branch=branch,
                commit_hash=commit,
                pr_number=None,
                base_branch="main",
                build_id=f"local-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                ci_platform="local"
            )

    def run_analysis(self, target_paths: List[str]) -> AnalysisResult:
        """Execute the core code analysis and return CI-relevant results."""
        # This would integrate with our tree-sitter analyzer
        cmd = [
            "python", "-m", "code_analyzer",
            "--format", "json",
            "--complexity-threshold", str(self.thresholds.max_complexity_per_function),
            "--parallel"
        ] + target_paths

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            raw_data = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Analysis failed: {e.stderr}")
            sys.exit(1)

        # Transform raw analysis data into CI-relevant format
        return self._process_analysis_results(raw_data)

    def _process_analysis_results(self, raw_data: Dict) -> AnalysisResult:
        """Process raw analysis data into CI-friendly format."""
        functions = raw_data.get("functions", [])
        high_complexity = [f for f in functions if f.get("complexity", 0) > self.thresholds.max_complexity_per_function]

        # Calculate technical debt ratio (high complexity functions / total)
        technical_debt_ratio = len(high_complexity) / max(len(functions), 1)

        # Generate recommendations based on findings
        recommendations = []
        if len(high_complexity) > self.thresholds.max_new_high_complexity_functions:
            recommendations.append(f"Consider refactoring {len(high_complexity)} high-complexity functions")

        if technical_debt_ratio > self.thresholds.max_technical_debt_ratio:
            recommendations.append(f"Technical debt ratio ({technical_debt_ratio:.2%}) exceeds threshold")

        return AnalysisResult(
            total_functions=len(functions),
            high_complexity_functions=len(high_complexity),
            average_complexity=sum(f.get("complexity", 0) for f in functions) / max(len(functions), 1),
            technical_debt_ratio=technical_debt_ratio,
            complexity_hotspots=sorted(high_complexity, key=lambda x: x.get("complexity", 0), reverse=True)[:10],
            new_complexity_violations=high_complexity,  # This would compare against baseline
            regression_analysis=self._analyze_regressions(raw_data),
            recommendations=recommendations
        )

    def _analyze_regressions(self, current_data: Dict) -> Dict:
        """Compare current analysis against baseline to detect regressions."""
        baseline_path = Path(self.config.get("baseline_storage", "./baselines/")) / f"{self.build_context.base_branch}.json"

        if not baseline_path.exists():
            return {"status": "no_baseline", "message": "No baseline found for comparison"}

        try:
            with open(baseline_path) as f:
                baseline_data = json.load(f)

            current_complexity = current_data.get("summary", {}).get("average_complexity", 0)
            baseline_complexity = baseline_data.get("summary", {}).get("average_complexity", 0)
            complexity_delta = current_complexity - baseline_complexity

            return {
                "status": "analyzed",
                "complexity_delta": complexity_delta,
                "complexity_increased": complexity_delta > self.thresholds.max_complexity_increase,
                "new_violations": len(current_data.get("functions", [])) - len(baseline_data.get("functions", [])),
                "baseline_date": baseline_data.get("metadata", {}).get("timestamp", "unknown")
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to analyze regressions: {e}"}

    def should_pass_build(self, analysis: AnalysisResult) -> Tuple[bool, List[str]]:
        """Determine if the build should pass based on analysis results and thresholds."""
        failures = []

        # Check complexity thresholds
        if analysis.high_complexity_functions > self.thresholds.max_new_high_complexity_functions:
            failures.append(f"Too many high-complexity functions: {analysis.high_complexity_functions} > {self.thresholds.max_new_high_complexity_functions}")

        # Check technical debt ratio
        if analysis.technical_debt_ratio > self.thresholds.max_technical_debt_ratio:
            failures.append(f"Technical debt ratio too high: {analysis.technical_debt_ratio:.2%} > {self.thresholds.max_technical_debt_ratio:.2%}")

        # Check for significant complexity regressions
        regression = analysis.regression_analysis
        if regression.get("status") == "analyzed" and regression.get("complexity_increased"):
            failures.append(f"Complexity regression detected: +{regression['complexity_delta']:.1f}")

        return len(failures) == 0, failures

    def generate_report(self, analysis: AnalysisResult, passed: bool, failures: List[str]) -> str:
        """Generate a comprehensive report for CI output."""
        status_emoji = "✅" if passed else "❌"
        status_text = "PASSED" if passed else "FAILED"

        report = f"""
# Code Analysis Report {status_emoji}

**Build Status:** {status_text}
**Branch:** {self.build_context.branch}
**Commit:** {self.build_context.commit_hash}
**Build ID:** {self.build_context.build_id}

## Summary Metrics

- **Total Functions:** {analysis.total_functions}
- **High Complexity Functions:** {analysis.high_complexity_functions}
- **Average Complexity:** {analysis.average_complexity:.1f}
- **Technical Debt Ratio:** {analysis.technical_debt_ratio:.2%}

## Regression Analysis

{self._format_regression_info(analysis.regression_analysis)}

## Quality Gates

"""

        if failures:
            report += "### ❌ Failed Checks\n\n"
            for failure in failures:
                report += f"- {failure}\n"
        else:
            report += "### ✅ All Checks Passed\n\n"

        if analysis.complexity_hotspots:
            report += "\n## Top Complexity Hotspots\n\n"
            for i, hotspot in enumerate(analysis.complexity_hotspots[:5], 1):
                report += f"{i}. **{hotspot.get('name', 'unknown')}** (complexity: {hotspot.get('complexity', 0)})\n"
                report += f"   - Location: {hotspot.get('file', 'unknown')}:{hotspot.get('line', 0)}\n"

        if analysis.recommendations:
            report += "\n## Recommendations\n\n"
            for rec in analysis.recommendations:
                report += f"- {rec}\n"

        return report

    def _format_regression_info(self, regression: Dict) -> str:
        """Format regression analysis for the report."""
        status = regression.get("status", "unknown")

        if status == "no_baseline":
            return "🔍 No baseline available for comparison"
        elif status == "error":
            return f"⚠️ Regression analysis failed: {regression.get('message', 'unknown error')}"
        elif status == "analyzed":
            delta = regression.get("complexity_delta", 0)
            if abs(delta) < 0.1:
                return "📊 No significant complexity changes detected"
            elif delta > 0:
                return f"📈 Complexity increased by {delta:.1f} (baseline: {regression.get('baseline_date', 'unknown')})"
            else:
                return f"📉 Complexity improved by {abs(delta):.1f} (baseline: {regression.get('baseline_date', 'unknown')})"

        return "❓ Regression analysis status unknown"

    def send_notifications(self, analysis: AnalysisResult, report: str, passed: bool):
        """Send notifications to configured channels."""
        notifications = self.config.get("notifications", {})

        # Slack notification
        if notifications.get("slack_webhook") and self.build_context.pr_number:
            self._send_slack_notification(notifications["slack_webhook"], analysis, passed)

        # GitHub PR comment
        if notifications.get("github_token") and self.build_context.pr_number and self.build_context.ci_platform == "github":
            self._send_github_comment(notifications["github_token"], report, passed)

    def _send_slack_notification(self, webhook_url: str, analysis: AnalysisResult, passed: bool):
        """Send a concise Slack notification."""
        color = "good" if passed else "danger"
        status = "✅ Passed" if passed else "❌ Failed"

        payload = {
            "attachments": [{
                "color": color,
                "title": f"Code Analysis {status}",
                "fields": [
                    {"title": "Branch", "value": self.build_context.branch, "short": True},
                    {"title": "Commit", "value": self.build_context.commit_hash, "short": True},
                    {"title": "High Complexity Functions", "value": str(analysis.high_complexity_functions), "short": True},
                    {"title": "Technical Debt", "value": f"{analysis.technical_debt_ratio:.2%}", "short": True}
                ]
            }]
        }

        try:
            requests.post(webhook_url, json=payload, timeout=10)
        except requests.RequestException as e:
            print(f"Failed to send Slack notification: {e}")

    def _send_github_comment(self, github_token: str, report: str, passed: bool):
        """Send a GitHub PR comment with the analysis report."""
        if not self.build_context.pr_number:
            return

        repo = os.getenv("GITHUB_REPOSITORY")
        if not repo:
            return

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        url = f"https://api.github.com/repos/{repo}/issues/{self.build_context.pr_number}/comments"

        try:
            requests.post(url, json={"body": report}, headers=headers, timeout=10)
        except requests.RequestException as e:
            print(f"Failed to send GitHub comment: {e}")

    def update_baseline(self, analysis_data: Dict):
        """Update the baseline for the current branch if this is a main branch build."""
        if self.build_context.branch in ["main", "master", "develop"]:
            baseline_dir = Path(self.config.get("baseline_storage", "./baselines/"))
            baseline_dir.mkdir(exist_ok=True)

            baseline_file = baseline_dir / f"{self.build_context.branch}.json"

            # Add metadata to the baseline
            analysis_data["metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "commit": self.build_context.commit_hash,
                "build_id": self.build_context.build_id
            }

            with open(baseline_file, "w") as f:
                json.dump(analysis_data, f, indent=2)

            print(f"Updated baseline for {self.build_context.branch}")


def main():
    """Main CI/CD integration entry point."""
    if len(sys.argv) < 2:
        print("Usage: python ci_integration.py <target_paths...>")
        sys.exit(1)

    target_paths = sys.argv[1:]

    # Initialize CI pipeline
    ci = CIPipeline()

    print(f"Running code analysis for {ci.build_context.ci_platform} build {ci.build_context.build_id}")
    print(f"Branch: {ci.build_context.branch}, Commit: {ci.build_context.commit_hash}")

    # Run analysis
    analysis = ci.run_analysis(target_paths)

    # Determine build status
    passed, failures = ci.should_pass_build(analysis)

    # Generate report
    report = ci.generate_report(analysis, passed, failures)
    print(report)

    # Send notifications
    ci.send_notifications(analysis, report, passed)

    # Update baseline if appropriate
    if passed and ci.build_context.branch in ["main", "master"]:
        # This would contain the raw analysis data
        raw_analysis_data = {"functions": [], "summary": {}}  # Placeholder
        ci.update_baseline(raw_analysis_data)

    # Exit with appropriate code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()