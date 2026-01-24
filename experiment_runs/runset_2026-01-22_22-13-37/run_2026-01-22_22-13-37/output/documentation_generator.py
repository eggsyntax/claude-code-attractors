#!/usr/bin/env python3
"""
Dynamic Documentation Generator

Generates living documentation that stays in sync with code changes
by analyzing codebase structure and creating comprehensive, readable
documentation with architectural insights and improvement suggestions.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from codebase_analyzer import CodebaseInsights, ArchitecturalPattern, FileInfo

# Optional markdown dependency
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


class DocumentationGenerator:
    """
    Generates comprehensive, living documentation from codebase analysis results.

    This generator creates documentation that includes:
    - Project overview and statistics
    - Architectural insights and patterns
    - File and module documentation
    - Improvement suggestions
    - Dependency visualizations
    """

    def __init__(self, project_name: str = None):
        self.project_name = project_name or "Analyzed Project"
        self.timestamp = datetime.now().isoformat()

    def generate_markdown(self, insights: CodebaseInsights) -> str:
        """
        Generate comprehensive markdown documentation from analysis results.

        Args:
            insights: Complete codebase analysis results

        Returns:
            str: Formatted markdown documentation
        """
        sections = [
            self._generate_header(),
            self._generate_overview(insights),
            self._generate_architecture_section(insights),
            self._generate_patterns_section(insights.patterns),
            self._generate_complexity_section(insights),
            self._generate_files_section(insights.file_info),
            self._generate_suggestions_section(insights.suggestions),
            self._generate_dependencies_section(insights.dependency_graph),
            self._generate_footer()
        ]

        return "\n\n".join(sections)

    def generate_html(self, insights: CodebaseInsights) -> str:
        """
        Generate HTML documentation with enhanced styling.

        Args:
            insights: Complete codebase analysis results

        Returns:
            str: Formatted HTML documentation
        """
        markdown_content = self.generate_markdown(insights)

        # Convert markdown to HTML
        if MARKDOWN_AVAILABLE:
            html_body = markdown.markdown(
                markdown_content,
                extensions=['tables', 'toc', 'codehilite', 'fenced_code']
            )
        else:
            # Simple markdown-to-HTML conversion for basic formatting
            html_body = self._simple_markdown_to_html(markdown_content)

        # Wrap in complete HTML document with styling
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.project_name} - Codebase Analysis</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
</body>
</html>
"""

    def _generate_header(self) -> str:
        """Generate documentation header."""
        return f"""# {self.project_name} - Codebase Analysis

**Generated:** {self.timestamp}
**Tool:** Intelligent Codebase Analyzer

This document provides a comprehensive analysis of the codebase structure,
architectural patterns, and improvement opportunities."""

    def _generate_overview(self, insights: CodebaseInsights) -> str:
        """Generate project overview section."""
        language_details = []
        for lang, count in sorted(insights.languages.items(), key=lambda x: x[1], reverse=True):
            language_details.append(f"- **{lang.title()}**: {count} files")

        return f"""## 📊 Project Overview

| Metric | Value |
|--------|-------|
| **Total Files** | {insights.total_files:,} |
| **Total Lines of Code** | {insights.total_lines:,} |
| **Programming Languages** | {len(insights.languages)} |
| **Patterns Identified** | {len(insights.patterns)} |
| **Complexity Hotspots** | {len(insights.complexity_hotspots)} |

### Languages Distribution

{chr(10).join(language_details)}"""

    def _generate_architecture_section(self, insights: CodebaseInsights) -> str:
        """Generate architecture insights section."""
        # Calculate some architectural metrics
        avg_file_size = insights.total_lines / insights.total_files if insights.total_files > 0 else 0

        # Analyze dependency complexity
        total_deps = sum(len(deps) for deps in insights.dependency_graph.values())
        avg_deps = total_deps / len(insights.dependency_graph) if insights.dependency_graph else 0

        return f"""## 🏗️ Architectural Insights

### Structure Metrics

- **Average File Size**: {avg_file_size:.0f} lines
- **Average Dependencies per Module**: {avg_deps:.1f}
- **Dependency Graph Complexity**: {'High' if avg_deps > 5 else 'Moderate' if avg_deps > 2 else 'Low'}

### Architecture Assessment

{self._assess_architecture_quality(insights)}"""

    def _assess_architecture_quality(self, insights: CodebaseInsights) -> str:
        """Assess overall architecture quality."""
        score = 100
        issues = []

        # Check for anti-patterns
        antipatterns = [p for p in insights.patterns if p.is_antipattern]
        if antipatterns:
            score -= len(antipatterns) * 15
            issues.append(f"Found {len(antipatterns)} anti-pattern(s)")

        # Check file size distribution
        large_files = [info for info in insights.file_info.values() if info.lines > 500]
        if large_files:
            score -= len(large_files) * 5
            issues.append(f"{len(large_files)} files exceed 500 lines")

        # Check complexity
        high_complexity = [info for info in insights.file_info.values() if info.complexity_score > 5.0]
        if high_complexity:
            score -= len(high_complexity) * 10
            issues.append(f"{len(high_complexity)} files have high complexity")

        score = max(0, score)  # Don't go below 0

        quality_level = "Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Improvement"

        result = f"**Overall Architecture Score**: {score}/100 ({quality_level})"

        if issues:
            result += f"\n\n**Areas for Improvement:**\n" + "\n".join(f"- {issue}" for issue in issues)

        return result

    def _generate_patterns_section(self, patterns: List[ArchitecturalPattern]) -> str:
        """Generate patterns analysis section."""
        if not patterns:
            return "## 🔍 Architectural Patterns\n\nNo specific patterns detected in this codebase."

        good_patterns = [p for p in patterns if not p.is_antipattern]
        antipatterns = [p for p in patterns if p.is_antipattern]

        content = ["## 🔍 Architectural Patterns"]

        if good_patterns:
            content.append("### ✅ Positive Patterns")
            for pattern in good_patterns:
                content.append(self._format_pattern(pattern))

        if antipatterns:
            content.append("### ❌ Anti-Patterns (Needs Attention)")
            for pattern in antipatterns:
                content.append(self._format_pattern(pattern))

        return "\n\n".join(content)

    def _format_pattern(self, pattern: ArchitecturalPattern) -> str:
        """Format a single pattern for documentation."""
        confidence_bar = "█" * int(pattern.confidence * 10) + "░" * (10 - int(pattern.confidence * 10))

        content = [
            f"#### {pattern.name}",
            f"**Confidence**: {pattern.confidence:.1%} `{confidence_bar}`",
            f"**Description**: {pattern.description}",
            f"**Files Involved**: {len(pattern.files_involved)}"
        ]

        if pattern.files_involved:
            files_list = "\n".join(f"- `{file}`" for file in pattern.files_involved[:5])
            if len(pattern.files_involved) > 5:
                files_list += f"\n- ... and {len(pattern.files_involved) - 5} more"
            content.append(f"**Files**:\n{files_list}")

        if pattern.suggestions:
            suggestions_list = "\n".join(f"- {suggestion}" for suggestion in pattern.suggestions)
            content.append(f"**Suggestions**:\n{suggestions_list}")

        return "\n".join(content)

    def _generate_complexity_section(self, insights: CodebaseInsights) -> str:
        """Generate complexity analysis section."""
        content = ["## 📈 Complexity Analysis"]

        if not insights.complexity_hotspots:
            content.append("No complexity hotspots identified.")
            return "\n\n".join(content)

        content.append("### Top Complexity Hotspots")
        content.append("| Rank | File | Complexity Score | Recommendation |")
        content.append("|------|------|------------------|----------------|")

        for i, (path, score) in enumerate(insights.complexity_hotspots[:10], 1):
            recommendation = self._get_complexity_recommendation(score)
            filename = path.name if hasattr(path, 'name') else str(path)
            content.append(f"| {i} | `{filename}` | {score:.1f} | {recommendation} |")

        # Add complexity distribution
        scores = [score for _, score in insights.complexity_hotspots]
        if scores:
            avg_complexity = sum(scores) / len(scores)
            content.append(f"\n**Average Complexity**: {avg_complexity:.1f}")

        return "\n\n".join(content)

    def _get_complexity_recommendation(self, score: float) -> str:
        """Get recommendation based on complexity score."""
        if score > 10:
            return "🚨 Refactor urgently"
        elif score > 5:
            return "⚠️ Consider refactoring"
        elif score > 2:
            return "📝 Monitor closely"
        else:
            return "✅ Acceptable"

    def _generate_files_section(self, file_info: Dict[Path, FileInfo]) -> str:
        """Generate detailed files section."""
        content = ["## 📁 File Analysis"]

        # Group files by language
        by_language = {}
        for path, info in file_info.items():
            if info.language not in by_language:
                by_language[info.language] = []
            by_language[info.language].append((path, info))

        for language in sorted(by_language.keys()):
            files = by_language[language]
            content.append(f"### {language.title()} Files ({len(files)})")

            # Sort by complexity/size for most interesting files first
            files.sort(key=lambda x: (x[1].complexity_score, x[1].lines), reverse=True)

            content.append("| File | Lines | Functions | Classes | Complexity |")
            content.append("|------|-------|-----------|---------|------------|")

            for path, info in files[:10]:  # Show top 10 per language
                filename = path.name if hasattr(path, 'name') else str(path)
                content.append(
                    f"| `{filename}` | {info.lines} | {len(info.functions)} | "
                    f"{len(info.classes)} | {info.complexity_score:.1f} |"
                )

            if len(files) > 10:
                content.append(f"*... and {len(files) - 10} more files*")

        return "\n\n".join(content)

    def _generate_suggestions_section(self, suggestions: List[str]) -> str:
        """Generate improvement suggestions section."""
        if not suggestions:
            return "## 💡 Improvement Suggestions\n\nNo specific suggestions at this time - codebase looks good!"

        content = [
            "## 💡 Improvement Suggestions",
            "Based on the analysis, here are prioritized suggestions for improving the codebase:"
        ]

        for i, suggestion in enumerate(suggestions, 1):
            content.append(f"{i}. {suggestion}")

        return "\n\n".join(content)

    def _generate_dependencies_section(self, dependency_graph: Dict[str, set]) -> str:
        """Generate dependency analysis section."""
        if not dependency_graph:
            return "## 🔗 Dependencies\n\nNo internal dependencies detected."

        content = ["## 🔗 Dependency Analysis"]

        # Calculate dependency metrics
        total_edges = sum(len(deps) for deps in dependency_graph.values())
        most_depended = max(dependency_graph.items(), key=lambda x: len(x[1])) if dependency_graph else None

        content.append(f"- **Total Internal Dependencies**: {total_edges}")
        content.append(f"- **Modules with Dependencies**: {len(dependency_graph)}")

        if most_depended:
            content.append(f"- **Most Connected Module**: `{most_depended[0]}` ({len(most_depended[1])} dependencies)")

        # Show top dependencies
        sorted_deps = sorted(dependency_graph.items(), key=lambda x: len(x[1]), reverse=True)

        content.append("\n### Top Dependencies")
        content.append("| Module | Dependencies Count | Depends On |")
        content.append("|--------|-------------------|------------|")

        for module, deps in sorted_deps[:10]:
            deps_str = ", ".join(f"`{dep}`" for dep in list(deps)[:3])
            if len(deps) > 3:
                deps_str += f" + {len(deps) - 3} more"
            content.append(f"| `{module}` | {len(deps)} | {deps_str} |")

        return "\n\n".join(content)

    def _generate_footer(self) -> str:
        """Generate documentation footer."""
        return f"""---

## 📝 About This Analysis

This documentation was automatically generated by the Intelligent Codebase Analyzer.
The analysis provides insights into code structure, patterns, and improvement opportunities.

**Last Updated**: {self.timestamp}
**Analysis Method**: Static analysis with pattern recognition
**Confidence Levels**: Based on heuristics and structural analysis

For questions about this analysis or to re-run with updated code, use the codebase analyzer tool."""

    def _get_css_styles(self) -> str:
        """Get CSS styles for HTML output."""
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }

        .container {
            background-color: #fff;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }

        h1 { border-bottom: 3px solid #3498db; padding-bottom: 0.5rem; }
        h2 { border-bottom: 2px solid #95a5a6; padding-bottom: 0.3rem; }

        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }

        table th, table td {
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }

        table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }

        table tr:nth-child(even) {
            background-color: #f8f9fa;
        }

        code {
            background-color: #f1f2f6;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }

        pre {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
        }

        .pattern-good { color: #27ae60; }
        .pattern-bad { color: #e74c3c; }

        .complexity-low { color: #27ae60; }
        .complexity-medium { color: #f39c12; }
        .complexity-high { color: #e74c3c; }

        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 1rem;
            margin-left: 0;
            background-color: #f8f9fa;
            padding: 1rem;
        }
        """

    def save_documentation(self, insights: CodebaseInsights, output_dir: Path,
                          formats: List[str] = None) -> Dict[str, Path]:
        """
        Save documentation in specified formats.

        Args:
            insights: Analysis results to document
            output_dir: Directory to save documentation
            formats: List of formats ('markdown', 'html', 'json')

        Returns:
            Dict mapping format names to saved file paths
        """
        if formats is None:
            formats = ['markdown', 'html']

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        saved_files = {}

        if 'markdown' in formats:
            md_content = self.generate_markdown(insights)
            md_path = output_dir / 'codebase_analysis.md'
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            saved_files['markdown'] = md_path

        if 'html' in formats:
            html_content = self.generate_html(insights)
            html_path = output_dir / 'codebase_analysis.html'
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            saved_files['html'] = html_path

        if 'json' in formats:
            json_path = output_dir / 'codebase_analysis.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                # Convert insights to JSON-serializable format
                json_data = {
                    'timestamp': self.timestamp,
                    'project_name': self.project_name,
                    'total_files': insights.total_files,
                    'total_lines': insights.total_lines,
                    'languages': insights.languages,
                    'patterns': [
                        {
                            'name': p.name,
                            'description': p.description,
                            'confidence': p.confidence,
                            'is_antipattern': p.is_antipattern,
                            'suggestions': p.suggestions,
                            'files_involved': [str(f) for f in p.files_involved]
                        }
                        for p in insights.patterns
                    ],
                    'complexity_hotspots': [(str(path), score) for path, score in insights.complexity_hotspots],
                    'suggestions': insights.suggestions
                }
                json.dump(json_data, f, indent=2)
            saved_files['json'] = json_path

        return saved_files

    def _simple_markdown_to_html(self, markdown_content: str) -> str:
        """Simple markdown to HTML conversion without external dependencies."""
        import re

        html = markdown_content

        # Convert headers
        html = re.sub(r'^### (.*)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*)', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Convert tables (basic)
        html = re.sub(r'^\|(.+)\|', r'<tr><td>\1</td></tr>', html, flags=re.MULTILINE)
        html = html.replace('<td>', '<td>').replace('</td>', '</td>')

        # Convert code blocks
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

        # Convert bold
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)

        # Convert lists
        html = re.sub(r'^- (.*)', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Convert paragraphs
        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'

        return html


def main():
    """Example usage of the DocumentationGenerator."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Generate documentation from codebase analysis')
    parser.add_argument('analysis_file', help='Path to JSON analysis results file')
    parser.add_argument('--output', '-o', default='./docs', help='Output directory for documentation')
    parser.add_argument('--project-name', '-n', help='Project name for documentation')
    parser.add_argument('--formats', '-f', nargs='+', default=['markdown', 'html'],
                       choices=['markdown', 'html', 'json'], help='Output formats')

    args = parser.parse_args()

    # Load analysis results
    try:
        with open(args.analysis_file, 'r') as f:
            analysis_data = json.load(f)
    except Exception as e:
        print(f"Error loading analysis file: {e}")
        sys.exit(1)

    # Generate documentation
    generator = DocumentationGenerator(args.project_name)

    # Note: This is a simplified example - in practice, you'd need to
    # reconstruct the CodebaseInsights object from the JSON data

    print(f"Documentation generator created. Use it programmatically with CodebaseInsights objects.")
    print(f"Example: generator.save_documentation(insights, Path('{args.output}'), {args.formats})")


if __name__ == '__main__':
    main()