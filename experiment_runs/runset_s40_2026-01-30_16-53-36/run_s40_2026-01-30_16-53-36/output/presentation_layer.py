#!/usr/bin/env python3
"""
Presentation Layer for Collaborative Code Review Framework
Transforms raw analysis results into beautiful, actionable reports.

This demonstrates Alice's strength in user experience design while
leveraging Bob's detailed analysis data.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ReviewReportGenerator:
    """
    Comprehensive report generator that transforms analysis results
    into multiple presentation formats for different audiences.
    """

    def __init__(self, results_data: Dict[str, Any]):
        self.data = results_data
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_executive_summary(self) -> str:
        """Generate high-level executive summary report"""
        metrics = self.data["summary_metrics"]
        insights = self.data["collaboration_insights"]

        summary = f"""
# 📊 Code Review Executive Summary
**Generated:** {self.timestamp}
**Framework:** Collaborative AI Code Review System v{self.data['test_metadata']['framework_version']}

## 🎯 Key Metrics
- **Files Analyzed:** {metrics['total_files']} files
- **Issues Detected:** {metrics['total_findings']} total findings
- **Analysis Time:** {metrics['execution_time_seconds']} seconds
- **Overall Status:** {'✅ PASSED' if insights['integration_success'] else '❌ FAILED'}

## 📈 Risk Distribution
"""

        severity_dist = metrics["findings_by_severity"]
        for severity, count in severity_dist.items():
            if count > 0:
                icon = {"critical": "🚨", "high": "⚠️", "medium": "⚡", "low": "ℹ️"}.get(severity, "•")
                summary += f"- **{severity.title()}:** {count} issues {icon}\n"

        summary += f"""
## 🔍 Analysis Coverage
"""
        type_dist = metrics["findings_by_type"]
        for analysis_type, count in type_dist.items():
            icon = {"security": "🔒", "complexity": "📊", "style": "🎨"}.get(analysis_type, "•")
            summary += f"- **{analysis_type.title()} Analysis:** {count} findings {icon}\n"

        summary += f"""
## 🤝 Collaboration Effectiveness
**Integration Status:** {insights['integration_success']}
**Interface Compatibility:** {insights['interface_compatibility']}
**Performance:** {insights['performance_characteristics']}
**Error Resilience:** {insights['error_handling']}

## 💡 Recommendations
Based on this analysis, we recommend:
1. **Immediate Action Required:** Address {severity_dist.get('critical', 0)} critical issues
2. **Security Focus:** {severity_dist.get('high', 0)} high-severity security findings need review
3. **Code Quality:** Consider refactoring files with {type_dist.get('complexity', 0)} complexity issues
4. **Process Improvement:** The collaborative framework demonstrates excellent integration

---
*This report was generated collaboratively by Alice (orchestration) and Bob (analysis engines)*
"""
        return summary

    def generate_technical_details(self) -> str:
        """Generate detailed technical report for developers"""
        report = f"""
# 🔧 Technical Analysis Report
**Generated:** {self.timestamp}

## 📋 Analysis Configuration
"""

        # Framework metadata
        metadata = self.data["test_metadata"]
        report += f"""
### Framework Components
- **Alice Components:** {', '.join(metadata['alice_components'])}
- **Bob Components:** {', '.join(metadata['bob_components'])}
- **Collaboration Pattern:** {metadata['collaboration_pattern']}

## 📁 File-by-File Analysis
"""

        # Detailed file analysis
        for filename, file_data in self.data["files_analyzed"].items():
            report += f"""
### {filename}
- **Language:** {file_data['language']}
- **Lines of Code:** {file_data['lines_of_code']}
- **Issues Found:** {file_data['findings_count']}

"""
            if file_data["findings"]:
                report += "#### Issues Detected:\n"
                for i, finding in enumerate(file_data["findings"], 1):
                    severity_icon = {
                        "critical": "🚨", "high": "⚠️",
                        "medium": "⚡", "low": "ℹ️"
                    }.get(finding.get("severity", ""), "•")

                    type_icon = {
                        "security": "🔒", "complexity": "📊",
                        "style": "🎨"
                    }.get(finding.get("type", ""), "•")

                    report += f"""
{i}. **{finding.get('message', 'Issue detected')}** {severity_icon} {type_icon}
   - **Severity:** {finding.get('severity', 'unknown').title()}
   - **Type:** {finding.get('type', 'unknown').title()}
   - **Line:** {finding.get('line', 'N/A')}
   - **Rule:** `{finding.get('rule', 'unknown')}`
"""
                    # Add metadata if available
                    if finding.get("metadata"):
                        metadata_items = finding["metadata"]
                        if isinstance(metadata_items, dict):
                            for key, value in metadata_items.items():
                                report += f"   - **{key.replace('_', ' ').title()}:** {value}\n"
                    report += "\n"
            else:
                report += "✅ No issues detected in this file.\n\n"

        # Analyzer performance details
        report += """
## ⚡ Analyzer Performance
"""
        analyzer_perf = self.data["summary_metrics"]["analyzer_performance"]
        for analyzer_name, perf_data in analyzer_perf.items():
            report += f"""
### {analyzer_name.replace('_', ' ').title()} Analyzer
- **Files Processed:** {perf_data['files_processed']}
- **Findings Generated:** {perf_data['findings_generated']}
- **Efficiency:** {perf_data['findings_generated'] / max(1, perf_data['files_processed']):.1f} findings per file
"""
            if "metadata" in perf_data:
                metadata = perf_data["metadata"]
                for key, value in metadata.items():
                    if key != "analyzer":
                        report += f"- **{key.replace('_', ' ').title()}:** {value}\n"

        return report

    def generate_json_export(self) -> str:
        """Generate machine-readable JSON export"""
        export_data = {
            "export_metadata": {
                "generated_at": self.timestamp,
                "generator": "Alice's Presentation Layer",
                "format_version": "1.0.0"
            },
            "analysis_results": self.data
        }
        return json.dumps(export_data, indent=2, sort_keys=True)

    def generate_developer_checklist(self) -> str:
        """Generate actionable checklist for developers"""
        checklist = f"""
# ✅ Developer Action Checklist
**Generated:** {self.timestamp}

## 🚨 Critical Issues (Immediate Action Required)
"""
        critical_issues = []
        high_issues = []
        other_issues = []

        # Categorize issues by severity
        for filename, file_data in self.data["files_analyzed"].items():
            for finding in file_data["findings"]:
                issue_item = f"- [ ] **{filename}:{finding.get('line', '?')}** - {finding.get('message', 'Fix issue')}"

                severity = finding.get("severity", "").lower()
                if severity == "critical":
                    critical_issues.append(issue_item)
                elif severity == "high":
                    high_issues.append(issue_item)
                else:
                    other_issues.append(issue_item)

        if critical_issues:
            checklist += "\n".join(critical_issues) + "\n"
        else:
            checklist += "✅ No critical issues found!\n"

        checklist += "\n## ⚠️ High Priority Issues\n"
        if high_issues:
            checklist += "\n".join(high_issues) + "\n"
        else:
            checklist += "✅ No high priority issues found!\n"

        checklist += "\n## 📋 Other Improvements\n"
        if other_issues:
            checklist += "\n".join(other_issues) + "\n"
        else:
            checklist += "✅ No other issues found!\n"

        # Add process recommendations
        checklist += f"""
## 🔄 Process Recommendations

### Code Quality
- [ ] Run this analysis before each commit
- [ ] Address all critical and high-severity issues
- [ ] Consider complexity refactoring for maintainability

### Security
- [ ] Review all security findings with security team
- [ ] Implement secure coding practices
- [ ] Regular security scans in CI/CD pipeline

### Collaboration Framework
- [ ] Document successful integration patterns
- [ ] Share collaboration insights with team
- [ ] Consider adopting this framework for other projects

---
**Collaboration Success Metrics:**
- Integration Compatibility: {self.data['collaboration_insights']['interface_compatibility']}
- Performance: {self.data['collaboration_insights']['performance_characteristics']}
- Error Handling: {self.data['collaboration_insights']['error_handling']}
"""
        return checklist

    def save_all_reports(self, output_dir: Path):
        """Save all report formats to the output directory"""
        reports = {
            "executive_summary.md": self.generate_executive_summary(),
            "technical_details.md": self.generate_technical_details(),
            "developer_checklist.md": self.generate_developer_checklist(),
            "full_export.json": self.generate_json_export()
        }

        print("📋 Generating presentation reports...")
        for filename, content in reports.items():
            file_path = output_dir / filename
            file_path.write_text(content)
            print(f"   ✅ Saved: {filename}")

        return reports

def main():
    """Generate all presentation formats from the demo results"""
    # Load the integration test results
    results_file = Path("/tmp/cc-exp/run_s40_2026-01-30_16-53-36/output/demo_results.json")
    with open(results_file, 'r') as f:
        results_data = json.load(f)

    # Generate all reports
    generator = ReviewReportGenerator(results_data)
    output_dir = Path("/tmp/cc-exp/run_s40_2026-01-30_16-53-36/output")

    reports = generator.save_all_reports(output_dir)

    print(f"""
🎨 Presentation Layer Complete!

Generated Reports:
- Executive Summary: executive_summary.md
- Technical Details: technical_details.md
- Developer Checklist: developer_checklist.md
- JSON Export: full_export.json

This demonstrates Alice's presentation layer capabilities working
seamlessly with Bob's analysis engine outputs!
""")

    return reports

if __name__ == "__main__":
    main()