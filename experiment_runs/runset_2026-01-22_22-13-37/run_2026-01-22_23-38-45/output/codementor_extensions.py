"""
CodeMentor Extensions: Advanced Features for the Collaborative Code Review System

This module extends Alice's excellent CodeMentor foundation with additional capabilities:
- Advanced refactoring suggestions
- Team analytics and insights
- Integration with popular development tools
- Automated code improvement workflows

Author: Bob (Claude Code Instance)
Built on Alice's CodeMentor foundation
"""

import json
import os
import ast
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import hashlib
from dataclasses import dataclass

@dataclass
class RefactoringSuggestion:
    """Represents a concrete refactoring suggestion with implementation details"""
    pattern_name: str
    current_code: str
    suggested_code: str
    explanation: str
    effort_level: str  # "low", "medium", "high"
    impact_score: float  # 0-1 representing positive impact
    line_range: Tuple[int, int]
    file_path: str

@dataclass
class TeamInsight:
    """Analytics insight about team collaboration patterns"""
    insight_type: str
    title: str
    description: str
    metric_value: float
    trend: str  # "improving", "declining", "stable"
    recommendations: List[str]

class AdvancedRefactoringEngine:
    """
    Advanced refactoring suggestions that go beyond pattern detection
    to provide concrete, implementable code improvements
    """

    def __init__(self):
        self.common_refactorings = {
            "extract_method": self._suggest_extract_method,
            "reduce_complexity": self._suggest_complexity_reduction,
            "eliminate_duplication": self._suggest_duplication_removal,
            "improve_naming": self._suggest_naming_improvements,
            "optimize_imports": self._suggest_import_optimization,
        }

    def analyze_for_refactoring(self, code: str, file_path: str) -> List[RefactoringSuggestion]:
        """
        Analyze code and generate concrete refactoring suggestions
        """
        suggestions = []

        try:
            tree = ast.parse(code)

            # Apply all refactoring analyzers
            for refactoring_type, analyzer in self.common_refactorings.items():
                try:
                    suggestion = analyzer(tree, code, file_path)
                    if suggestion:
                        suggestions.extend(suggestion if isinstance(suggestion, list) else [suggestion])
                except Exception as e:
                    print(f"Error in {refactoring_type} analysis: {e}")
                    continue

            # Sort by impact score (highest impact first)
            suggestions.sort(key=lambda x: x.impact_score, reverse=True)

        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")

        return suggestions

    def _suggest_extract_method(self, tree: ast.AST, code: str, file_path: str) -> List[RefactoringSuggestion]:
        """Look for long methods that could benefit from extraction"""
        suggestions = []
        lines = code.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    method_length = node.end_lineno - node.lineno
                    if method_length > 20:  # Methods longer than 20 lines
                        suggestions.append(RefactoringSuggestion(
                            pattern_name="extract_method",
                            current_code='\n'.join(lines[node.lineno-1:node.end_lineno]),
                            suggested_code=f"# Consider extracting parts of this method:\n# def {node.name}_helper(...):\n#     pass\n\ndef {node.name}(...):\n    # Refactored implementation\n    pass",
                            explanation=f"The method '{node.name}' is {method_length} lines long. Consider extracting logical chunks into smaller, focused methods.",
                            effort_level="medium",
                            impact_score=0.7,
                            line_range=(node.lineno, node.end_lineno or node.lineno),
                            file_path=file_path
                        ))

        return suggestions

    def _suggest_complexity_reduction(self, tree: ast.AST, code: str, file_path: str) -> List[RefactoringSuggestion]:
        """Identify complex conditional logic that could be simplified"""
        suggestions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Count nested conditions
                nested_depth = self._count_nested_conditions(node)
                if nested_depth > 3:
                    suggestions.append(RefactoringSuggestion(
                        pattern_name="reduce_complexity",
                        current_code=ast.unparse(node) if hasattr(ast, 'unparse') else "# Complex conditional logic",
                        suggested_code="# Consider using guard clauses or strategy pattern\n# if not condition:\n#     return early\n# handle main case",
                        explanation=f"Complex nested conditional with {nested_depth} levels. Consider using guard clauses or extracting to separate methods.",
                        effort_level="high",
                        impact_score=0.8,
                        line_range=(node.lineno, getattr(node, 'end_lineno', node.lineno)),
                        file_path=file_path
                    ))

        return suggestions

    def _suggest_duplication_removal(self, tree: ast.AST, code: str, file_path: str) -> List[RefactoringSuggestion]:
        """Find code duplication opportunities"""
        suggestions = []
        lines = code.split('\n')

        # Simple approach: look for identical function bodies
        function_bodies = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                body_lines = lines[node.lineno:getattr(node, 'end_lineno', node.lineno)]
                body_hash = hashlib.md5('\n'.join(body_lines).encode()).hexdigest()

                if body_hash in function_bodies:
                    suggestions.append(RefactoringSuggestion(
                        pattern_name="eliminate_duplication",
                        current_code='\n'.join(body_lines),
                        suggested_code=f"# Extract common logic to shared method\ndef _shared_logic(...):\n    # Common implementation\n    pass\n\ndef {node.name}(...):\n    return _shared_logic(...)",
                        explanation=f"Function '{node.name}' has similar implementation to '{function_bodies[body_hash]}'. Consider extracting common logic.",
                        effort_level="medium",
                        impact_score=0.6,
                        line_range=(node.lineno, getattr(node, 'end_lineno', node.lineno)),
                        file_path=file_path
                    ))
                else:
                    function_bodies[body_hash] = node.name

        return suggestions

    def _suggest_naming_improvements(self, tree: ast.AST, code: str, file_path: str) -> List[RefactoringSuggestion]:
        """Suggest better variable and function names"""
        suggestions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.name) < 3 or node.name in ['func', 'method', 'fn']:
                    suggestions.append(RefactoringSuggestion(
                        pattern_name="improve_naming",
                        current_code=f"def {node.name}(...):",
                        suggested_code=f"def descriptive_method_name(...):",
                        explanation=f"Function name '{node.name}' is not descriptive. Consider a name that clearly indicates the function's purpose.",
                        effort_level="low",
                        impact_score=0.4,
                        line_range=(node.lineno, node.lineno),
                        file_path=file_path
                    ))

        return suggestions

    def _suggest_import_optimization(self, tree: ast.AST, code: str, file_path: str) -> List[RefactoringSuggestion]:
        """Suggest import optimizations"""
        suggestions = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)

        if len(imports) > 10:
            suggestions.append(RefactoringSuggestion(
                pattern_name="optimize_imports",
                current_code="# Many import statements",
                suggested_code="# Consider grouping related imports\n# Use import sorting tools like isort",
                explanation=f"File has {len(imports)} import statements. Consider organizing and optimizing imports for better readability.",
                effort_level="low",
                impact_score=0.3,
                line_range=(1, 10),
                file_path=file_path
            ))

        return suggestions

    def _count_nested_conditions(self, node: ast.If) -> int:
        """Count the depth of nested conditional statements"""
        max_depth = 0

        def count_depth(n, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)

            for child in ast.iter_child_nodes(n):
                if isinstance(child, ast.If):
                    count_depth(child, current_depth + 1)
                else:
                    count_depth(child, current_depth)

        count_depth(node, 1)
        return max_depth

class TeamAnalytics:
    """
    Analyze team collaboration patterns and provide insights
    for improving code review processes
    """

    def __init__(self, history_file: str = "codementor_analytics.json"):
        self.history_file = history_file
        self.session_history = self._load_history()

    def record_review_session(self, session_data: Dict[str, Any]):
        """Record data from a code review session"""
        session_data['timestamp'] = datetime.now().isoformat()
        session_data['session_id'] = hashlib.md5(
            f"{session_data['timestamp']}{session_data.get('participants', [])}".encode()
        ).hexdigest()[:8]

        self.session_history.append(session_data)
        self._save_history()

    def generate_team_insights(self) -> List[TeamInsight]:
        """Generate actionable insights about team collaboration"""
        insights = []

        if len(self.session_history) < 2:
            return [TeamInsight(
                insight_type="info",
                title="Getting Started",
                description="Need more review sessions to generate meaningful insights",
                metric_value=len(self.session_history),
                trend="stable",
                recommendations=["Continue using CodeMentor to build up analytics history"]
            )]

        # Review frequency analysis
        recent_sessions = self._get_recent_sessions(days=30)
        avg_sessions_per_week = len(recent_sessions) / 4.0

        if avg_sessions_per_week < 2:
            insights.append(TeamInsight(
                insight_type="opportunity",
                title="Review Frequency",
                description="Team could benefit from more frequent code reviews",
                metric_value=avg_sessions_per_week,
                trend="stable",
                recommendations=[
                    "Schedule regular review sessions",
                    "Set up automated review reminders",
                    "Consider smaller, more frequent reviews"
                ]
            ))

        # Pattern learning analysis
        pattern_discussions = self._analyze_pattern_discussions()
        if pattern_discussions['learning_velocity'] > 0.7:
            insights.append(TeamInsight(
                insight_type="success",
                title="Pattern Learning",
                description="Team is actively learning architectural patterns",
                metric_value=pattern_discussions['learning_velocity'],
                trend="improving",
                recommendations=[
                    "Continue exploring advanced patterns",
                    "Share pattern knowledge with other teams"
                ]
            ))

        # Collaboration quality
        collaboration_score = self._calculate_collaboration_score()
        insights.append(TeamInsight(
            insight_type="metric",
            title="Collaboration Quality",
            description="Overall effectiveness of team collaboration",
            metric_value=collaboration_score,
            trend=self._calculate_trend('collaboration_score'),
            recommendations=self._get_collaboration_recommendations(collaboration_score)
        ))

        return insights

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load session history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_history(self):
        """Save session history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.session_history, f, indent=2)

    def _get_recent_sessions(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get sessions from the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            session for session in self.session_history
            if datetime.fromisoformat(session['timestamp']) > cutoff
        ]

    def _analyze_pattern_discussions(self) -> Dict[str, float]:
        """Analyze how much the team is learning about patterns"""
        recent_sessions = self._get_recent_sessions()
        total_patterns = sum(len(session.get('patterns_discussed', [])) for session in recent_sessions)

        return {
            'learning_velocity': min(total_patterns / max(len(recent_sessions), 1) / 5.0, 1.0),
            'pattern_diversity': len(set(
                pattern for session in recent_sessions
                for pattern in session.get('patterns_discussed', [])
            )) / max(total_patterns, 1)
        }

    def _calculate_collaboration_score(self) -> float:
        """Calculate overall collaboration effectiveness"""
        if not self.session_history:
            return 0.0

        factors = []

        # Participation factor
        avg_participants = sum(len(session.get('participants', [])) for session in self.session_history) / len(self.session_history)
        participation_score = min(avg_participants / 3.0, 1.0)  # Optimal: 3+ participants
        factors.append(participation_score * 0.3)

        # Discussion quality factor
        avg_comments = sum(session.get('comment_count', 0) for session in self.session_history) / len(self.session_history)
        discussion_score = min(avg_comments / 10.0, 1.0)  # Good: 10+ comments per session
        factors.append(discussion_score * 0.4)

        # Resolution factor
        resolution_rate = sum(1 for session in self.session_history if session.get('resolution_status') == 'resolved') / len(self.session_history)
        factors.append(resolution_rate * 0.3)

        return sum(factors)

    def _calculate_trend(self, metric: str) -> str:
        """Calculate trend for a specific metric"""
        # Simplified trend calculation
        recent = self._get_recent_sessions(14)  # Last 2 weeks
        older = self._get_recent_sessions(30)[:-len(recent)]  # Previous 2 weeks

        if len(recent) > len(older):
            return "improving"
        elif len(recent) < len(older):
            return "declining"
        else:
            return "stable"

    def _get_collaboration_recommendations(self, score: float) -> List[str]:
        """Get recommendations based on collaboration score"""
        if score > 0.8:
            return [
                "Excellent collaboration! Consider mentoring other teams",
                "Document your successful practices for wider adoption"
            ]
        elif score > 0.6:
            return [
                "Good collaboration. Focus on increasing participation",
                "Encourage more detailed discussions in reviews"
            ]
        else:
            return [
                "Improve collaboration by encouraging more team participation",
                "Set clear expectations for review engagement",
                "Consider pair programming sessions to build collaboration skills"
            ]

class CodeMentorExtensions:
    """
    Main class that integrates advanced features with Alice's CodeMentor foundation
    """

    def __init__(self):
        self.refactoring_engine = AdvancedRefactoringEngine()
        self.team_analytics = TeamAnalytics()

    async def enhanced_analysis(self, code: str, file_path: str) -> Dict[str, Any]:
        """
        Perform enhanced analysis that combines Alice's pattern detection
        with advanced refactoring suggestions and insights
        """
        # Get refactoring suggestions
        refactoring_suggestions = self.refactoring_engine.analyze_for_refactoring(code, file_path)

        # Generate team insights
        team_insights = self.team_analytics.generate_team_insights()

        return {
            'refactoring_suggestions': [
                {
                    'pattern': suggestion.pattern_name,
                    'explanation': suggestion.explanation,
                    'effort': suggestion.effort_level,
                    'impact': suggestion.impact_score,
                    'line_range': suggestion.line_range,
                    'current_code': suggestion.current_code[:200] + '...' if len(suggestion.current_code) > 200 else suggestion.current_code,
                    'suggested_code': suggestion.suggested_code[:200] + '...' if len(suggestion.suggested_code) > 200 else suggestion.suggested_code
                } for suggestion in refactoring_suggestions[:5]  # Top 5 suggestions
            ],
            'team_insights': [
                {
                    'type': insight.insight_type,
                    'title': insight.title,
                    'description': insight.description,
                    'metric': insight.metric_value,
                    'trend': insight.trend,
                    'recommendations': insight.recommendations
                } for insight in team_insights
            ],
            'enhancement_metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'suggestions_count': len(refactoring_suggestions),
                'insights_count': len(team_insights),
                'analyzer_version': '1.0.0'
            }
        }

    def integrate_with_tools(self) -> Dict[str, str]:
        """
        Provide integration points for popular development tools
        """
        return {
            'vscode_extension': 'Install CodeMentor VSCode extension for real-time analysis',
            'git_hooks': 'Set up pre-commit hooks to run CodeMentor analysis',
            'ci_integration': 'Add CodeMentor to your CI/CD pipeline for automated reviews',
            'slack_bot': 'Configure Slack bot for review notifications and updates',
            'jira_integration': 'Link CodeMentor findings to JIRA tickets for tracking'
        }

    def export_analysis_report(self, analysis_results: Dict[str, Any], format: str = 'markdown') -> str:
        """
        Export comprehensive analysis report in various formats
        """
        if format == 'markdown':
            return self._generate_markdown_report(analysis_results)
        elif format == 'json':
            return json.dumps(analysis_results, indent=2)
        elif format == 'html':
            return self._generate_html_report(analysis_results)
        else:
            return "Unsupported format. Available: markdown, json, html"

    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive markdown report"""
        report = """# CodeMentor Enhanced Analysis Report

## 🔧 Refactoring Suggestions

"""

        for suggestion in results.get('refactoring_suggestions', []):
            report += f"### {suggestion['pattern'].replace('_', ' ').title()}\n"
            report += f"**Impact Score:** {suggestion['impact']:.2f} | **Effort:** {suggestion['effort']}\n\n"
            report += f"{suggestion['explanation']}\n\n"
            report += f"**Lines:** {suggestion['line_range'][0]}-{suggestion['line_range'][1]}\n\n"
            report += "---\n\n"

        report += "## 📊 Team Insights\n\n"

        for insight in results.get('team_insights', []):
            emoji = {"success": "✅", "opportunity": "💡", "metric": "📈", "info": "ℹ️"}
            report += f"### {emoji.get(insight['type'], '📋')} {insight['title']}\n"
            report += f"{insight['description']}\n\n"
            report += f"**Metric Value:** {insight['metric']:.2f} | **Trend:** {insight['trend']}\n\n"
            report += "**Recommendations:**\n"
            for rec in insight['recommendations']:
                report += f"- {rec}\n"
            report += "\n---\n\n"

        report += f"""## 🔍 Analysis Metadata

- **Generated:** {results.get('enhancement_metadata', {}).get('analysis_timestamp', 'Unknown')}
- **Suggestions:** {results.get('enhancement_metadata', {}).get('suggestions_count', 0)}
- **Insights:** {results.get('enhancement_metadata', {}).get('insights_count', 0)}
- **Analyzer Version:** {results.get('enhancement_metadata', {}).get('analyzer_version', 'Unknown')}

---
*Report generated by CodeMentor Extensions - Built by Alice & Bob*
"""

        return report

    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate an HTML report with interactive elements"""
        # Basic HTML structure - could be enhanced with CSS and JavaScript
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CodeMentor Enhanced Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .section {{ margin: 20px 0; padding: 20px; border-left: 4px solid #007acc; }}
        .suggestion {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .insight {{ background: #e8f5e8; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .metric {{ font-weight: bold; color: #007acc; }}
    </style>
</head>
<body>
    <h1>CodeMentor Enhanced Analysis Report</h1>
    <p><em>Generated: {results.get('enhancement_metadata', {}).get('analysis_timestamp', 'Unknown')}</em></p>

    <div class="section">
        <h2>🔧 Refactoring Suggestions</h2>
"""

        for suggestion in results.get('refactoring_suggestions', []):
            html += f"""
        <div class="suggestion">
            <h3>{suggestion['pattern'].replace('_', ' ').title()}</h3>
            <p><span class="metric">Impact:</span> {suggestion['impact']:.2f} | <span class="metric">Effort:</span> {suggestion['effort']}</p>
            <p>{suggestion['explanation']}</p>
            <p><small>Lines: {suggestion['line_range'][0]}-{suggestion['line_range'][1]}</small></p>
        </div>"""

        html += """
    </div>

    <div class="section">
        <h2>📊 Team Insights</h2>
"""

        for insight in results.get('team_insights', []):
            html += f"""
        <div class="insight">
            <h3>{insight['title']}</h3>
            <p>{insight['description']}</p>
            <p><span class="metric">Value:</span> {insight['metric']:.2f} | <span class="metric">Trend:</span> {insight['trend']}</p>
            <ul>"""
            for rec in insight['recommendations']:
                html += f"<li>{rec}</li>"
            html += """
            </ul>
        </div>"""

        html += """
    </div>

    <footer>
        <p><em>Report generated by CodeMentor Extensions - Built by Alice & Bob</em></p>
    </footer>
</body>
</html>"""

        return html

# Example usage and integration with Alice's CodeMentor
if __name__ == "__main__":
    extensions = CodeMentorExtensions()

    # Example code for testing
    sample_code = '''
def process_data(data):
    if data is not None:
        if len(data) > 0:
            if isinstance(data, list):
                if all(isinstance(item, dict) for item in data):
                    result = []
                    for item in data:
                        if 'name' in item:
                            if 'value' in item:
                                result.append({
                                    'processed_name': item['name'].upper(),
                                    'processed_value': item['value'] * 2
                                })
                    return result
    return None

def process_other_data(other_data):
    if other_data is not None:
        if len(other_data) > 0:
            if isinstance(other_data, list):
                if all(isinstance(item, dict) for item in other_data):
                    result = []
                    for item in other_data:
                        if 'title' in item:
                            if 'amount' in item:
                                result.append({
                                    'processed_title': item['title'].upper(),
                                    'processed_amount': item['amount'] * 2
                                })
                    return result
    return None
'''

    print("🚀 CodeMentor Extensions Demo")
    print("=" * 50)

    # Run enhanced analysis
    async def demo():
        results = await extensions.enhanced_analysis(sample_code, "example.py")

        print("📋 Enhanced Analysis Results:")
        print(f"Found {len(results['refactoring_suggestions'])} refactoring suggestions")
        print(f"Generated {len(results['team_insights'])} team insights")

        # Export report
        markdown_report = extensions.export_analysis_report(results, 'markdown')

        # Save report
        with open('enhanced_analysis_report.md', 'w') as f:
            f.write(markdown_report)

        print("\n📄 Report saved as 'enhanced_analysis_report.md'")

        # Show integration options
        integrations = extensions.integrate_with_tools()
        print("\n🔗 Available Integrations:")
        for tool, description in integrations.items():
            print(f"  • {tool}: {description}")

    # Run the demo
    import asyncio
    asyncio.run(demo())