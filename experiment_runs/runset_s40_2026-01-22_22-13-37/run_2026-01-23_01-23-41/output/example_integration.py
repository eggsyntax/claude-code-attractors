#!/usr/bin/env python3
"""
Example Integration Script - How to use the CI/CD code analysis tool

This script demonstrates various integration scenarios and usage patterns
for the code analysis CI/CD tool. It shows how to:

1. Run analysis in different CI environments
2. Configure custom thresholds for different project types
3. Handle baseline management
4. Generate different report formats
5. Integrate with notification systems

Run this script to see the tool in action with sample configurations.
"""

import json
import tempfile
from pathlib import Path
from ci_integration import CIPipeline, AnalysisThresholds, BuildContext


def example_microservice_config():
    """Configuration for a microservice with strict quality gates."""
    return {
        "thresholds": {
            "max_complexity_per_function": 10,  # Stricter for microservices
            "max_complexity_increase": 3,
            "max_new_high_complexity_functions": 1,  # Very strict
            "max_technical_debt_ratio": 0.10,  # Lower tolerance
            "min_test_coverage": 0.90,  # Higher coverage requirement
            "max_dependency_depth": 6
        },
        "quality_gates": {
            "block_on_regression": True,
            "block_on_threshold_violation": True,
            "require_improvement_on_hotspot_changes": True
        }
    }


def example_legacy_project_config():
    """Configuration for legacy projects with gradual improvement strategy."""
    return {
        "thresholds": {
            "max_complexity_per_function": 25,  # More lenient initially
            "max_complexity_increase": 10,
            "max_new_high_complexity_functions": 5,
            "max_technical_debt_ratio": 0.30,  # Higher tolerance for legacy
            "min_test_coverage": 0.60,  # Lower initial requirement
            "max_dependency_depth": 12
        },
        "quality_gates": {
            "block_on_regression": False,  # Don't block on regressions initially
            "block_on_threshold_violation": False,
            "allow_complexity_increase_on_new_features": True
        },
        "improvement_strategy": {
            "gradual_threshold_tightening": True,
            "monthly_threshold_reduction": 0.05,
            "focus_on_hotspots": True
        }
    }


def example_open_source_project_config():
    """Configuration for open source projects with contributor-friendly gates."""
    return {
        "thresholds": {
            "max_complexity_per_function": 15,
            "max_complexity_increase": 7,
            "max_new_high_complexity_functions": 3,
            "max_technical_debt_ratio": 0.15,
            "min_test_coverage": 0.75,
            "max_dependency_depth": 8
        },
        "quality_gates": {
            "block_on_regression": True,
            "block_on_threshold_violation": False,  # Don't block contributors
            "provide_educational_feedback": True
        },
        "contributor_experience": {
            "generate_learning_resources": True,
            "suggest_refactoring_patterns": True,
            "highlight_good_examples": True
        }
    }


def demonstrate_ci_integration():
    """Show how the tool works in different CI scenarios."""

    print("=" * 60)
    print("Code Analysis CI/CD Integration Demo")
    print("=" * 60)

    # Create temporary config for demo
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(example_microservice_config(), f, indent=2)
        config_path = f.name

    try:
        # Initialize CI pipeline with microservice config
        ci = CIPipeline(config_path)

        print(f"\n🔍 Detected CI Environment: {ci.build_context.ci_platform}")
        print(f"📊 Branch: {ci.build_context.branch}")
        print(f"🔨 Build ID: {ci.build_context.build_id}")

        # Show threshold configuration
        print(f"\n⚙️ Quality Gate Thresholds:")
        print(f"  - Max Function Complexity: {ci.thresholds.max_complexity_per_function}")
        print(f"  - Technical Debt Ratio: {ci.thresholds.max_technical_debt_ratio:.2%}")
        print(f"  - Max New High-Complexity Functions: {ci.thresholds.max_new_high_complexity_functions}")

        # Simulate analysis results
        mock_analysis_result = create_mock_analysis_result()

        # Test quality gates
        passed, failures = ci.should_pass_build(mock_analysis_result)

        print(f"\n🎯 Quality Gate Result: {'✅ PASSED' if passed else '❌ FAILED'}")

        if failures:
            print("\n📋 Failure Reasons:")
            for failure in failures:
                print(f"  - {failure}")

        # Generate report
        report = ci.generate_report(mock_analysis_result, passed, failures)
        print(f"\n📄 Generated Report Preview:")
        print("=" * 40)
        print(report[:500] + "..." if len(report) > 500 else report)

        # Show different configuration examples
        print(f"\n🎛️ Configuration Examples:")
        print("\n1. Microservice Configuration (Current):")
        print("   - Strict complexity limits")
        print("   - High test coverage requirements")
        print("   - Blocks on any regression")

        print("\n2. Legacy Project Configuration:")
        print("   - More lenient initial thresholds")
        print("   - Gradual improvement strategy")
        print("   - Focus on preventing further deterioration")

        print("\n3. Open Source Project Configuration:")
        print("   - Contributor-friendly gates")
        print("   - Educational feedback")
        print("   - Doesn't block contributions on quality issues")

    finally:
        Path(config_path).unlink()  # Cleanup


def create_mock_analysis_result():
    """Create mock analysis results for demonstration."""
    from ci_integration import AnalysisResult

    return AnalysisResult(
        total_functions=45,
        high_complexity_functions=3,
        average_complexity=8.2,
        technical_debt_ratio=0.067,  # 6.7% - within threshold
        complexity_hotspots=[
            {"name": "process_payment", "complexity": 18, "file": "payment.py", "line": 42},
            {"name": "validate_order", "complexity": 16, "file": "orders.py", "line": 128},
            {"name": "calculate_shipping", "complexity": 15, "file": "shipping.py", "line": 67}
        ],
        new_complexity_violations=[],
        regression_analysis={
            "status": "analyzed",
            "complexity_delta": 1.2,
            "complexity_increased": False,
            "new_violations": 0,
            "baseline_date": "2024-01-15"
        },
        recommendations=[
            "Consider extracting helper functions from process_payment",
            "Add more unit tests for high-complexity functions"
        ]
    )


def show_workflow_examples():
    """Demonstrate different workflow integration patterns."""

    print("\n" + "=" * 60)
    print("Workflow Integration Examples")
    print("=" * 60)

    workflows = {
        "Feature Branch Workflow": {
            "trigger": "Every PR to main",
            "action": "Run analysis, block if thresholds exceeded",
            "notification": "GitHub PR comment with results",
            "baseline": "Compare against main branch baseline"
        },
        "Continuous Integration": {
            "trigger": "Every commit to main",
            "action": "Update baseline, generate trend reports",
            "notification": "Slack alert if quality degrades",
            "baseline": "Update main branch baseline"
        },
        "Release Pipeline": {
            "trigger": "Release tag creation",
            "action": "Comprehensive analysis with strict gates",
            "notification": "Email report to stakeholders",
            "baseline": "Create release baseline snapshot"
        },
        "Nightly Analysis": {
            "trigger": "Scheduled daily run",
            "action": "Deep analysis, trend tracking",
            "notification": "Dashboard update, weekly summary",
            "baseline": "Historical trend analysis"
        }
    }

    for workflow_name, config in workflows.items():
        print(f"\n🔄 {workflow_name}:")
        for key, value in config.items():
            print(f"   {key.title()}: {value}")


def show_notification_examples():
    """Show different notification strategies."""

    print("\n" + "=" * 60)
    print("Notification Strategy Examples")
    print("=" * 60)

    notifications = {
        "GitHub PR Comments": {
            "when": "Every PR analysis",
            "format": "Markdown report with metrics",
            "audience": "PR author and reviewers"
        },
        "Slack Alerts": {
            "when": "Quality gate failures or significant regressions",
            "format": "Concise summary with key metrics",
            "audience": "Development team channel"
        },
        "Email Reports": {
            "when": "Weekly summary or release analysis",
            "format": "HTML report with charts and trends",
            "audience": "Engineering managers and stakeholders"
        },
        "Dashboard Updates": {
            "when": "Every analysis run",
            "format": "Metrics pushed to monitoring dashboard",
            "audience": "Self-service access for all team members"
        }
    }

    for notification_type, config in notifications.items():
        print(f"\n📢 {notification_type}:")
        for key, value in config.items():
            print(f"   {key.title()}: {value}")


if __name__ == "__main__":
    demonstrate_ci_integration()
    show_workflow_examples()
    show_notification_examples()

    print(f"\n" + "=" * 60)
    print("🚀 Ready to integrate code analysis into your CI/CD pipeline!")
    print("💡 Tips:")
    print("  - Start with lenient thresholds and gradually tighten")
    print("  - Focus on preventing regressions first")
    print("  - Use notifications to build awareness, not frustration")
    print("  - Baseline management is key for meaningful comparisons")
    print("=" * 60)