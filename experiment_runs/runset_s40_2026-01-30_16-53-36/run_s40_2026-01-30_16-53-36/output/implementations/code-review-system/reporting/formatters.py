"""
Report Formatting and Presentation for Collaborative Code Review System

Handles the formatting and presentation of code review results in various output
formats including JSON, YAML, text, and HTML.

Designed by Alice as part of AI-to-AI collaboration framework testing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import json
import yaml
import html


@dataclass
class Finding:
    """Represents a single finding from code analysis"""
    file_path: str
    line_number: int
    column: Optional[int]
    severity: str
    category: str
    rule_id: str
    message: str
    description: Optional[str] = None
    suggestion: Optional[str] = None
    source_lines: Optional[List[str]] = None
    confidence: Optional[float] = None
    analysis_type: Optional[str] = None


@dataclass
class ReviewSummary:
    """Summary information for the entire review"""
    request_id: str
    files_reviewed: List[str]
    total_findings: int
    findings_by_severity: Dict[str, int]
    findings_by_category: Dict[str, int]
    analysis_types_run: List[str]
    execution_time: float
    completed_at: datetime
    configuration_used: Dict[str, Any]


class ReportFormatter(ABC):
    """Abstract base class for report formatters"""

    @abstractmethod
    def format_report(self, summary: ReviewSummary, findings: List[Finding],
                     config: Dict[str, Any]) -> str:
        """Format a complete report"""
        pass

    @abstractmethod
    def format_summary(self, summary: ReviewSummary) -> str:
        """Format just the summary section"""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the appropriate file extension for this format"""
        pass


class JSONFormatter(ReportFormatter):
    """JSON report formatter"""

    def format_report(self, summary: ReviewSummary, findings: List[Finding],
                     config: Dict[str, Any]) -> str:
        """Format complete report as JSON"""
        report = {
            "summary": self._summary_to_dict(summary),
            "findings": [self._finding_to_dict(f) for f in findings],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "formatter": "json",
                "configuration": config
            }
        }

        return json.dumps(report, indent=2, default=str)

    def format_summary(self, summary: ReviewSummary) -> str:
        """Format summary as JSON"""
        return json.dumps(self._summary_to_dict(summary), indent=2, default=str)

    def get_file_extension(self) -> str:
        return ".json"

    def _summary_to_dict(self, summary: ReviewSummary) -> Dict[str, Any]:
        return {
            "request_id": summary.request_id,
            "files_reviewed": summary.files_reviewed,
            "total_findings": summary.total_findings,
            "findings_by_severity": summary.findings_by_severity,
            "findings_by_category": summary.findings_by_category,
            "analysis_types_run": summary.analysis_types_run,
            "execution_time": summary.execution_time,
            "completed_at": summary.completed_at.isoformat()
        }

    def _finding_to_dict(self, finding: Finding) -> Dict[str, Any]:
        return {
            "file_path": finding.file_path,
            "line_number": finding.line_number,
            "column": finding.column,
            "severity": finding.severity,
            "category": finding.category,
            "rule_id": finding.rule_id,
            "message": finding.message,
            "description": finding.description,
            "suggestion": finding.suggestion,
            "source_lines": finding.source_lines,
            "confidence": finding.confidence,
            "analysis_type": finding.analysis_type
        }


class YAMLFormatter(ReportFormatter):
    """YAML report formatter"""

    def format_report(self, summary: ReviewSummary, findings: List[Finding],
                     config: Dict[str, Any]) -> str:
        """Format complete report as YAML"""
        json_formatter = JSONFormatter()
        report_dict = json.loads(json_formatter.format_report(summary, findings, config))

        return yaml.dump(report_dict, default_flow_style=False, sort_keys=False,
                        default_style=None, width=120)

    def format_summary(self, summary: ReviewSummary) -> str:
        """Format summary as YAML"""
        json_formatter = JSONFormatter()
        summary_dict = json.loads(json_formatter.format_summary(summary))

        return yaml.dump(summary_dict, default_flow_style=False, sort_keys=False)

    def get_file_extension(self) -> str:
        return ".yaml"


class TextFormatter(ReportFormatter):
    """Human-readable text report formatter"""

    def format_report(self, summary: ReviewSummary, findings: List[Finding],
                     config: Dict[str, Any]) -> str:
        """Format complete report as readable text"""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("CODE REVIEW REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Summary
        lines.append(self.format_summary(summary))
        lines.append("")

        # Group findings by file for better readability
        findings_by_file = self._group_findings_by_file(findings)

        if not findings:
            lines.append("🎉 No issues found!")
        else:
            lines.append("DETAILED FINDINGS")
            lines.append("-" * 40)
            lines.append("")

            for file_path, file_findings in findings_by_file.items():
                lines.append(f"📁 {file_path}")
                lines.append("")

                for finding in sorted(file_findings, key=lambda f: f.line_number):
                    lines.extend(self._format_finding(finding, config))
                    lines.append("")

        # Footer
        lines.append("=" * 80)
        lines.append(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)

        return "\n".join(lines)

    def format_summary(self, summary: ReviewSummary) -> str:
        """Format summary as readable text"""
        lines = []

        lines.append("SUMMARY")
        lines.append("-" * 20)
        lines.append(f"Request ID: {summary.request_id}")
        lines.append(f"Files reviewed: {len(summary.files_reviewed)}")
        lines.append(f"Total findings: {summary.total_findings}")
        lines.append(f"Execution time: {summary.execution_time:.2f}s")
        lines.append(f"Completed: {summary.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Severity breakdown
        if summary.findings_by_severity:
            lines.append("Findings by severity:")
            for severity in ["error", "warning", "info", "style"]:
                count = summary.findings_by_severity.get(severity, 0)
                if count > 0:
                    emoji = {"error": "🚨", "warning": "⚠️", "info": "ℹ️", "style": "💅"}.get(severity, "•")
                    lines.append(f"  {emoji} {severity.title()}: {count}")

        # Category breakdown (top 5)
        if summary.findings_by_category:
            lines.append("")
            lines.append("Top categories:")
            sorted_categories = sorted(summary.findings_by_category.items(),
                                     key=lambda x: x[1], reverse=True)
            for category, count in sorted_categories[:5]:
                lines.append(f"  • {category}: {count}")

        return "\n".join(lines)

    def get_file_extension(self) -> str:
        return ".txt"

    def _group_findings_by_file(self, findings: List[Finding]) -> Dict[str, List[Finding]]:
        """Group findings by file path"""
        grouped = {}
        for finding in findings:
            if finding.file_path not in grouped:
                grouped[finding.file_path] = []
            grouped[finding.file_path].append(finding)
        return grouped

    def _format_finding(self, finding: Finding, config: Dict[str, Any]) -> List[str]:
        """Format a single finding for text output"""
        lines = []

        # Finding header with severity emoji
        severity_emojis = {"error": "🚨", "warning": "⚠️", "info": "ℹ️", "style": "💅"}
        emoji = severity_emojis.get(finding.severity, "•")

        location = f"Line {finding.line_number}"
        if finding.column:
            location += f", Column {finding.column}"

        lines.append(f"{emoji} {finding.severity.upper()} - {location}")
        lines.append(f"   Rule: {finding.rule_id}")
        lines.append(f"   Message: {finding.message}")

        # Description if available
        if finding.description:
            lines.append(f"   Description: {finding.description}")

        # Source code context if available and enabled
        if (finding.source_lines and
            config.get("output", {}).get("include_source_code", True)):
            lines.append("   Source:")
            for i, line in enumerate(finding.source_lines):
                line_num = finding.line_number - len(finding.source_lines) // 2 + i
                prefix = ">>>" if line_num == finding.line_number else "   "
                lines.append(f"     {prefix} {line_num:4d}: {line.rstrip()}")

        # Suggestion if available
        if finding.suggestion:
            lines.append(f"   💡 Suggestion: {finding.suggestion}")

        # Confidence if available
        if finding.confidence is not None:
            confidence_percent = int(finding.confidence * 100)
            lines.append(f"   Confidence: {confidence_percent}%")

        return lines


class HTMLFormatter(ReportFormatter):
    """HTML report formatter with styling"""

    def format_report(self, summary: ReviewSummary, findings: List[Finding],
                     config: Dict[str, Any]) -> str:
        """Format complete report as HTML"""
        html_parts = []

        # HTML header with CSS
        html_parts.append(self._get_html_header())

        # Summary section
        html_parts.append('<div class="summary">')
        html_parts.append('<h1>Code Review Report</h1>')
        html_parts.append(self._format_summary_html(summary))
        html_parts.append('</div>')

        # Findings section
        if findings:
            html_parts.append('<div class="findings">')
            html_parts.append('<h2>Detailed Findings</h2>')

            # Group by file
            findings_by_file = self._group_findings_by_file(findings)
            for file_path, file_findings in findings_by_file.items():
                html_parts.append(f'<div class="file-section">')
                html_parts.append(f'<h3 class="file-name">📁 {html.escape(file_path)}</h3>')

                for finding in sorted(file_findings, key=lambda f: f.line_number):
                    html_parts.append(self._format_finding_html(finding, config))

                html_parts.append('</div>')
            html_parts.append('</div>')
        else:
            html_parts.append('<div class="no-findings">🎉 No issues found!</div>')

        # Footer
        html_parts.append(f'<div class="footer">Report generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>')
        html_parts.append('</body></html>')

        return '\n'.join(html_parts)

    def format_summary(self, summary: ReviewSummary) -> str:
        """Format summary as HTML"""
        return self._format_summary_html(summary)

    def get_file_extension(self) -> str:
        return ".html"

    def _group_findings_by_file(self, findings: List[Finding]) -> Dict[str, List[Finding]]:
        """Group findings by file path"""
        grouped = {}
        for finding in findings:
            if finding.file_path not in grouped:
                grouped[finding.file_path] = []
            grouped[finding.file_path].append(finding)
        return grouped

    def _format_summary_html(self, summary: ReviewSummary) -> str:
        """Format summary section as HTML"""
        html_parts = []

        html_parts.append('<div class="summary-stats">')
        html_parts.append(f'<div class="stat"><span class="label">Request ID:</span> {html.escape(summary.request_id)}</div>')
        html_parts.append(f'<div class="stat"><span class="label">Files reviewed:</span> {len(summary.files_reviewed)}</div>')
        html_parts.append(f'<div class="stat"><span class="label">Total findings:</span> {summary.total_findings}</div>')
        html_parts.append(f'<div class="stat"><span class="label">Execution time:</span> {summary.execution_time:.2f}s</div>')
        html_parts.append('</div>')

        # Severity breakdown
        if summary.findings_by_severity:
            html_parts.append('<div class="severity-breakdown">')
            html_parts.append('<h4>Findings by Severity</h4>')
            for severity in ["error", "warning", "info", "style"]:
                count = summary.findings_by_severity.get(severity, 0)
                if count > 0:
                    html_parts.append(f'<div class="severity-item severity-{severity}">')
                    html_parts.append(f'<span class="severity-name">{severity.title()}</span>')
                    html_parts.append(f'<span class="severity-count">{count}</span>')
                    html_parts.append('</div>')
            html_parts.append('</div>')

        return '\n'.join(html_parts)

    def _format_finding_html(self, finding: Finding, config: Dict[str, Any]) -> str:
        """Format a single finding as HTML"""
        html_parts = []

        html_parts.append(f'<div class="finding severity-{finding.severity}">')

        # Finding header
        location = f"Line {finding.line_number}"
        if finding.column:
            location += f", Column {finding.column}"

        html_parts.append('<div class="finding-header">')
        html_parts.append(f'<span class="severity-badge">{finding.severity.upper()}</span>')
        html_parts.append(f'<span class="location">{location}</span>')
        html_parts.append(f'<span class="rule">{html.escape(finding.rule_id)}</span>')
        html_parts.append('</div>')

        # Message
        html_parts.append(f'<div class="message">{html.escape(finding.message)}</div>')

        # Description
        if finding.description:
            html_parts.append(f'<div class="description">{html.escape(finding.description)}</div>')

        # Source code
        if (finding.source_lines and
            config.get("output", {}).get("include_source_code", True)):
            html_parts.append('<div class="source-code">')
            html_parts.append('<h5>Source:</h5>')
            html_parts.append('<pre><code>')

            for i, line in enumerate(finding.source_lines):
                line_num = finding.line_number - len(finding.source_lines) // 2 + i
                css_class = "highlighted" if line_num == finding.line_number else ""
                html_parts.append(f'<div class="source-line {css_class}">')
                html_parts.append(f'<span class="line-number">{line_num:4d}:</span>')
                html_parts.append(f'<span class="line-content">{html.escape(line.rstrip())}</span>')
                html_parts.append('</div>')

            html_parts.append('</code></pre>')
            html_parts.append('</div>')

        # Suggestion
        if finding.suggestion:
            html_parts.append(f'<div class="suggestion">💡 <strong>Suggestion:</strong> {html.escape(finding.suggestion)}</div>')

        html_parts.append('</div>')
        return '\n'.join(html_parts)

    def _get_html_header(self) -> str:
        """Get HTML header with embedded CSS"""
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Code Review Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .summary { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .summary h1 { color: #333; margin-top: 0; }
        .summary-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 20px; }
        .stat { padding: 10px; background: #f8f9fa; border-radius: 4px; }
        .stat .label { font-weight: bold; color: #666; }
        .severity-breakdown { margin-top: 20px; }
        .severity-item { display: flex; justify-content: space-between; padding: 5px 10px; margin: 5px 0; border-radius: 4px; }
        .severity-error { background: #fee; border-left: 4px solid #dc3545; }
        .severity-warning { background: #fff3cd; border-left: 4px solid #ffc107; }
        .severity-info { background: #d1ecf1; border-left: 4px solid #17a2b8; }
        .severity-style { background: #f3e5f5; border-left: 4px solid #9c27b0; }
        .findings { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .file-section { margin-bottom: 30px; }
        .file-name { color: #495057; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }
        .finding { margin: 15px 0; padding: 15px; border-radius: 6px; border-left: 4px solid #ccc; }
        .finding.severity-error { background: #fee; border-left-color: #dc3545; }
        .finding.severity-warning { background: #fff3cd; border-left-color: #ffc107; }
        .finding.severity-info { background: #d1ecf1; border-left-color: #17a2b8; }
        .finding.severity-style { background: #f3e5f5; border-left-color: #9c27b0; }
        .finding-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
        .severity-badge { padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; color: white; }
        .severity-error .severity-badge { background: #dc3545; }
        .severity-warning .severity-badge { background: #ffc107; color: #212529; }
        .severity-info .severity-badge { background: #17a2b8; }
        .severity-style .severity-badge { background: #9c27b0; }
        .location { font-weight: bold; }
        .rule { color: #666; font-family: monospace; }
        .message { font-weight: bold; margin-bottom: 10px; }
        .description { color: #666; margin-bottom: 10px; }
        .source-code { margin-top: 15px; }
        .source-code pre { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 15px; overflow-x: auto; }
        .source-line { display: flex; }
        .source-line.highlighted { background: #fff3cd; }
        .line-number { color: #666; width: 50px; margin-right: 10px; }
        .suggestion { margin-top: 10px; padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px; }
        .no-findings { text-align: center; font-size: 18px; color: #28a745; margin: 40px 0; }
        .footer { text-align: center; color: #666; margin-top: 30px; font-size: 14px; }
    </style>
</head>
<body>'''


class ReportManager:
    """Manages report generation and formatting"""

    def __init__(self):
        self.formatters = {
            "json": JSONFormatter(),
            "yaml": YAMLFormatter(),
            "text": TextFormatter(),
            "html": HTMLFormatter()
        }

    def generate_report(self, summary: ReviewSummary, findings: List[Finding],
                       format_type: str = "json", config: Dict[str, Any] = None) -> str:
        """Generate a report in the specified format"""
        if format_type not in self.formatters:
            raise ValueError(f"Unsupported format: {format_type}")

        config = config or {}
        formatter = self.formatters[format_type]
        return formatter.format_report(summary, findings, config)

    def save_report(self, summary: ReviewSummary, findings: List[Finding],
                   output_path: Path, format_type: str = "json",
                   config: Dict[str, Any] = None):
        """Generate and save a report to file"""
        report_content = self.generate_report(summary, findings, format_type, config)

        formatter = self.formatters[format_type]
        if not output_path.suffix:
            output_path = output_path.with_suffix(formatter.get_file_extension())

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return output_path

    def get_available_formats(self) -> List[str]:
        """Get list of available output formats"""
        return list(self.formatters.keys())


# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    sample_summary = ReviewSummary(
        request_id="test-123",
        files_reviewed=["example.py", "utils.py"],
        total_findings=3,
        findings_by_severity={"error": 1, "warning": 1, "info": 1},
        findings_by_category={"complexity": 1, "style": 1, "security": 1},
        analysis_types_run=["static_analysis", "complexity", "security"],
        execution_time=2.45,
        completed_at=datetime.now(),
        configuration_used={"format": "json"}
    )

    sample_findings = [
        Finding(
            file_path="example.py",
            line_number=15,
            column=8,
            severity="error",
            category="complexity",
            rule_id="C901",
            message="Function too complex",
            description="This function has too many branches",
            suggestion="Consider breaking into smaller functions",
            source_lines=["def complex_function():", "    if condition1:", "        # many branches..."],
            confidence=0.9,
            analysis_type="complexity"
        )
    ]

    manager = ReportManager()

    # Test text format
    text_report = manager.generate_report(sample_summary, sample_findings, "text")
    print("Text Report Generated:")
    print(text_report[:200] + "...")
    print(f"\nAvailable formats: {manager.get_available_formats()}")