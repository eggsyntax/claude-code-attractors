#!/usr/bin/env python3
"""
Demo Integration Script
Shows how the Smart Code Review Assistant can integrate with common workflows

This script demonstrates:
1. Git hook integration
2. CI/CD pipeline integration
3. Slack/Teams notification integration
4. GitHub PR comment integration (mock)
"""

import subprocess
import json
import os
from datetime import datetime
from smart_review_assistant import SmartReviewAnalyzer, format_smart_review_report

class ReviewIntegrator:
    """Integrates smart review analysis with various platforms and workflows"""

    def __init__(self):
        self.analyzer = SmartReviewAnalyzer()

    def analyze_current_branch(self, base_branch: str = "main") -> str:
        """Analyze changes in current branch compared to base branch"""
        try:
            # Get diff from git
            result = subprocess.run(
                ["git", "diff", f"{base_branch}...HEAD"],
                capture_output=True,
                text=True,
                check=True
            )

            if not result.stdout.strip():
                return "No changes detected in current branch."

            # Analyze the diff
            changes = self.analyzer.analyze_diff(result.stdout, include_context=True)
            return format_smart_review_report(changes)

        except subprocess.CalledProcessError as e:
            return f"Git error: {e.stderr}"
        except Exception as e:
            return f"Analysis error: {str(e)}"

    def analyze_staged_changes(self) -> str:
        """Analyze staged changes (useful for pre-commit hooks)"""
        try:
            result = subprocess.run(
                ["git", "diff", "--staged"],
                capture_output=True,
                text=True,
                check=True
            )

            if not result.stdout.strip():
                return "No staged changes to analyze."

            changes = self.analyzer.analyze_diff(result.stdout, include_context=True)
            return format_smart_review_report(changes)

        except subprocess.CalledProcessError as e:
            return f"Git error: {e.stderr}"
        except Exception as e:
            return f"Analysis error: {str(e)}"

    def analyze_commit(self, commit_hash: str) -> str:
        """Analyze a specific commit"""
        try:
            result = subprocess.run(
                ["git", "show", commit_hash],
                capture_output=True,
                text=True,
                check=True
            )

            changes = self.analyzer.analyze_diff(result.stdout, include_context=True)
            return format_smart_review_report(changes)

        except subprocess.CalledProcessError as e:
            return f"Git error: {e.stderr}"
        except Exception as e:
            return f"Analysis error: {str(e)}"

    def generate_pr_comment(self, diff_content: str) -> str:
        """Generate a GitHub PR comment with review insights"""
        changes = self.analyzer.analyze_diff(diff_content, include_context=True)

        if not changes:
            return "## 🔍 Code Review Assistant\n\nNo significant changes detected."

        # Count critical/high priority items
        critical_count = sum(1 for c in changes if c.review_priority.value == "critical")
        high_count = sum(1 for c in changes if c.review_priority.value == "high")

        # Build concise summary for PR comment
        comment = ["## 🔍 Code Review Assistant Analysis\n"]

        if critical_count > 0:
            comment.append(f"⚠️ **{critical_count} critical priority files** need attention")

        if high_count > 0:
            comment.append(f"🔍 **{high_count} high priority files** for review")

        # Add top insights
        all_issues = []
        for change in changes[:3]:  # Top 3 files
            all_issues.extend(change.potential_issues)

        if all_issues:
            comment.append("\n### Key Issues to Review:")
            for issue in all_issues[:5]:  # Top 5 issues
                comment.append(f"- {issue}")

        # Add questions
        all_questions = []
        for change in changes[:3]:
            all_questions.extend(change.review_questions)

        if all_questions:
            comment.append("\n### Review Checklist:")
            for question in all_questions[:3]:  # Top 3 questions
                comment.append(f"- [ ] {question}")

        comment.append(f"\n*Analysis covered {len(changes)} files with complexity scores ranging from {min(c.complexity_score for c in changes)} to {max(c.complexity_score for c in changes)}/10*")

        return "\n".join(comment)

    def generate_slack_message(self, diff_content: str, pr_url: str = None) -> dict:
        """Generate a Slack message with review summary"""
        changes = self.analyzer.analyze_diff(diff_content, include_context=True)

        if not changes:
            return {
                "text": "🤖 Code Review Assistant: No significant changes detected.",
                "color": "good"
            }

        critical_count = sum(1 for c in changes if c.review_priority.value == "critical")
        high_count = sum(1 for c in changes if c.review_priority.value == "high")

        # Determine message color based on priority
        if critical_count > 0:
            color = "danger"
            emoji = "🚨"
        elif high_count > 0:
            color = "warning"
            emoji = "⚠️"
        else:
            color = "good"
            emoji = "✅"

        # Build message
        text_parts = [f"{emoji} Code Review Analysis Complete"]

        if pr_url:
            text_parts.append(f"<{pr_url}|View PR>")

        fields = [
            {
                "title": "Files Changed",
                "value": str(len(changes)),
                "short": True
            },
            {
                "title": "Priority Breakdown",
                "value": f"Critical: {critical_count}, High: {high_count}",
                "short": True
            }
        ]

        if critical_count > 0 or high_count > 0:
            # Add top issues
            top_issues = []
            for change in changes[:2]:
                top_issues.extend(change.potential_issues[:2])

            if top_issues:
                fields.append({
                    "title": "Key Issues",
                    "value": "\n".join(f"• {issue}" for issue in top_issues[:3]),
                    "short": False
                })

        return {
            "attachments": [{
                "color": color,
                "text": " | ".join(text_parts),
                "fields": fields,
                "footer": "Smart Code Review Assistant",
                "ts": int(datetime.now().timestamp())
            }]
        }

    def ci_pipeline_check(self, diff_content: str) -> dict:
        """Perform CI/CD pipeline checks and return structured results"""
        changes = self.analyzer.analyze_diff(diff_content, include_context=True)

        result = {
            "success": True,
            "warnings": [],
            "errors": [],
            "info": {
                "files_analyzed": len(changes),
                "complexity_scores": [c.complexity_score for c in changes],
                "priorities": [c.review_priority.value for c in changes]
            }
        }

        # Check for blockers
        critical_issues = []
        for change in changes:
            if change.review_priority.value == "critical":
                critical_issues.extend(change.potential_issues)

        if critical_issues:
            result["errors"].extend(critical_issues)
            result["success"] = False

        # Check for warnings
        high_priority_count = sum(1 for c in changes if c.review_priority.value == "high")
        if high_priority_count > 0:
            result["warnings"].append(f"{high_priority_count} high-priority changes need review")

        # Complexity warnings
        high_complexity = [c for c in changes if c.complexity_score > 8]
        if high_complexity:
            result["warnings"].append(f"{len(high_complexity)} files have high complexity (>8/10)")

        return result

def demo_workflows():
    """Demonstrate different workflow integrations"""
    integrator = ReviewIntegrator()

    print("🚀 Smart Code Review Assistant - Integration Demo\n")

    # Demo 1: Pre-commit hook simulation
    print("1. Pre-commit Hook Simulation:")
    print("   Analyzing staged changes...")
    try:
        staged_analysis = integrator.analyze_staged_changes()
        print("   ✅ Analysis complete")
        print(f"   📄 Preview: {staged_analysis[:200]}...\n")
    except Exception as e:
        print(f"   ❌ No git repo or staged changes: {e}\n")

    # Demo 2: PR comment generation
    print("2. GitHub PR Comment Generation:")
    sample_diff = """diff --git a/src/example.py b/src/example.py
index 1234567..abcdefg 100644
--- a/src/example.py
+++ b/src/example.py
@@ -10,6 +10,8 @@ def login(username, password):
     # Simple login function
-    if password == "admin":
+    if username == "admin" and password == "secret123":
         return True
+    # TODO: Add proper password hashing
     return False"""

    pr_comment = integrator.generate_pr_comment(sample_diff)
    print(f"   📝 Generated PR comment:\n{pr_comment}\n")

    # Demo 3: Slack notification
    print("3. Slack Notification:")
    slack_msg = integrator.generate_slack_message(sample_diff, "https://github.com/user/repo/pull/123")
    print(f"   💬 Slack payload: {json.dumps(slack_msg, indent=2)}\n")

    # Demo 4: CI/CD pipeline check
    print("4. CI/CD Pipeline Check:")
    ci_result = integrator.ci_pipeline_check(sample_diff)
    print(f"   🔧 CI Result: {'PASS' if ci_result['success'] else 'FAIL'}")
    if ci_result['errors']:
        print(f"   ❌ Errors: {ci_result['errors']}")
    if ci_result['warnings']:
        print(f"   ⚠️  Warnings: {ci_result['warnings']}")
    print(f"   📊 Files analyzed: {ci_result['info']['files_analyzed']}")

if __name__ == "__main__":
    demo_workflows()