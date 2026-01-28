"""
Collaborative Analysis Synthesis Layer
Combines findings from Alice (Design & Quality) and Bob (Performance & Security)
"""

import json
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import importlib.util
import sys
import os

# Import our analyzer modules
def import_analyzer(file_path: str, module_name: str):
    """Dynamically import analyzer modules"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass
class SynthesizedFinding:
    """A finding that combines insights from multiple analyzers"""
    primary_category: str
    secondary_categories: List[str]
    severity: str
    title: str
    description: str
    line_number: int
    confidence: float
    suggestions: List[str]
    analyzers: List[str]  # Which analyzers contributed
    correlations: List[str]  # Related findings
    impact_assessment: str
    priority_score: float  # 0-100, higher = more important


class AnalysisSynthesizer:
    """Synthesizes findings from multiple analyzers to create holistic insights"""

    def __init__(self):
        self.severity_weights = {
            'critical': 10,
            'high': 8,
            'major': 7,
            'medium': 5,
            'minor': 3,
            'low': 2,
            'info': 1
        }

    def synthesize_findings(self, alice_results: Dict[str, Any], bob_findings: List[Any]) -> Dict[str, Any]:
        """
        Combine findings from both analyzers into a comprehensive analysis
        """
        alice_findings = alice_results.get('findings', [])

        # Normalize findings to common format
        normalized_alice = self._normalize_alice_findings(alice_findings)
        normalized_bob = self._normalize_bob_findings(bob_findings)

        all_findings = normalized_alice + normalized_bob

        # Correlate findings by line number and content
        correlations = self._find_correlations(all_findings)

        # Create synthesized findings
        synthesized = self._create_synthesized_findings(all_findings, correlations)

        # Calculate overall metrics
        metrics = self._calculate_synthesis_metrics(synthesized, alice_results, bob_findings)

        # Generate recommendations
        recommendations = self._generate_recommendations(synthesized)

        return {
            'synthesized_findings': [asdict(f) for f in synthesized],
            'correlation_analysis': correlations,
            'metrics': metrics,
            'recommendations': recommendations,
            'executive_summary': self._generate_executive_summary(synthesized, metrics)
        }

    def _normalize_alice_findings(self, findings: List[Dict]) -> List[Dict]:
        """Convert Alice's findings to normalized format"""
        normalized = []
        for f in findings:
            normalized.append({
                'analyzer': 'Alice',
                'category': f.get('category', ''),
                'severity': f.get('severity', 'medium'),
                'message': f.get('message', ''),
                'line_number': f.get('line_number', 0),
                'confidence': f.get('confidence', 0.5),
                'suggestion': f.get('suggestion', ''),
                'rule_id': f.get('rule_id', ''),
                'raw_finding': f
            })
        return normalized

    def _normalize_bob_findings(self, findings: List[Any]) -> List[Dict]:
        """Convert Bob's findings to normalized format"""
        normalized = []
        for f in findings:
            # Handle both dict and object formats
            if hasattr(f, '__dict__'):
                finding_dict = f.__dict__
            else:
                finding_dict = f if isinstance(f, dict) else {}

            normalized.append({
                'analyzer': 'Bob',
                'category': finding_dict.get('category', ''),
                'severity': finding_dict.get('severity', 'medium'),
                'message': finding_dict.get('title', '') + ': ' + finding_dict.get('description', ''),
                'line_number': finding_dict.get('line_number', 0),
                'confidence': finding_dict.get('confidence', 0.5),
                'suggestion': finding_dict.get('suggestion', ''),
                'rule_id': f"BOB_{finding_dict.get('category', 'UNK')}",
                'raw_finding': finding_dict
            })
        return normalized

    def _find_correlations(self, findings: List[Dict]) -> Dict[str, List[Dict]]:
        """Find correlations between findings from different analyzers"""
        correlations = defaultdict(list)

        # Group findings by line number (±2 lines tolerance)
        line_groups = defaultdict(list)
        for finding in findings:
            line_num = finding.get('line_number', 0)
            for i in range(max(1, line_num - 2), line_num + 3):
                line_groups[i].append(finding)

        # Find lines with findings from both analyzers
        for line_num, line_findings in line_groups.items():
            alice_findings = [f for f in line_findings if f['analyzer'] == 'Alice']
            bob_findings = [f for f in line_findings if f['analyzer'] == 'Bob']

            if alice_findings and bob_findings:
                correlation_key = f"line_{line_num}"
                correlations[correlation_key] = {
                    'line_number': line_num,
                    'alice_findings': alice_findings,
                    'bob_findings': bob_findings,
                    'correlation_type': self._determine_correlation_type(alice_findings, bob_findings)
                }

        # Find semantic correlations (similar issues in different places)
        semantic_correlations = self._find_semantic_correlations(findings)
        correlations.update(semantic_correlations)

        return dict(correlations)

    def _determine_correlation_type(self, alice_findings: List[Dict], bob_findings: List[Dict]) -> str:
        """Determine the type of correlation between Alice and Bob findings"""
        alice_categories = {f['category'] for f in alice_findings}
        bob_categories = {f['category'] for f in bob_findings}

        # Check for specific correlation patterns
        if 'SOLID Principles' in alice_categories and 'security' in bob_categories:
            return 'design_security_intersection'
        elif 'Design Pattern' in alice_categories and 'performance' in bob_categories:
            return 'architecture_performance_tradeoff'
        elif 'Code Quality' in alice_categories and 'performance' in bob_categories:
            return 'quality_performance_balance'
        else:
            return 'general_correlation'

    def _find_semantic_correlations(self, findings: List[Dict]) -> Dict[str, Dict]:
        """Find semantic correlations across the codebase"""
        correlations = {}

        # Look for patterns that suggest related issues
        god_class_findings = [f for f in findings if 'God Class' in f.get('message', '')]
        complexity_findings = [f for f in findings if 'complexity' in f.get('message', '').lower()]

        if god_class_findings and complexity_findings:
            correlations['god_class_complexity'] = {
                'type': 'architectural_complexity',
                'description': 'God Class pattern correlates with high complexity',
                'alice_findings': [f for f in god_class_findings if f['analyzer'] == 'Alice'],
                'bob_findings': [f for f in complexity_findings if f['analyzer'] == 'Bob'],
                'impact': 'High architectural debt with performance implications'
            }

        return correlations

    def _create_synthesized_findings(self, all_findings: List[Dict], correlations: Dict) -> List[SynthesizedFinding]:
        """Create synthesized findings that combine insights"""
        synthesized = []
        processed_findings = set()

        # Process correlated findings first
        for correlation_key, correlation in correlations.items():
            if correlation_key.startswith('line_'):
                alice_findings = correlation['alice_findings']
                bob_findings = correlation['bob_findings']

                # Create a synthesized finding
                synthesized_finding = self._merge_findings(alice_findings + bob_findings, correlation['correlation_type'])
                synthesized.append(synthesized_finding)

                # Mark these findings as processed
                for finding in alice_findings + bob_findings:
                    processed_findings.add(id(finding))

        # Process remaining standalone findings
        for finding in all_findings:
            if id(finding) not in processed_findings:
                synthesized_finding = self._convert_to_synthesized(finding)
                synthesized.append(synthesized_finding)

        # Sort by priority score
        synthesized.sort(key=lambda x: x.priority_score, reverse=True)

        return synthesized

    def _merge_findings(self, findings: List[Dict], correlation_type: str) -> SynthesizedFinding:
        """Merge multiple findings into a single synthesized finding"""
        primary_finding = max(findings, key=lambda x: self.severity_weights.get(x['severity'], 0))

        all_categories = list(set(f['category'] for f in findings))
        all_suggestions = [f['suggestion'] for f in findings if f['suggestion']]
        all_analyzers = list(set(f['analyzer'] for f in findings))

        # Calculate combined confidence
        avg_confidence = sum(f['confidence'] for f in findings) / len(findings)

        # Generate correlation-specific title and description
        title, description, impact = self._generate_correlation_insights(findings, correlation_type)

        return SynthesizedFinding(
            primary_category=primary_finding['category'],
            secondary_categories=[cat for cat in all_categories if cat != primary_finding['category']],
            severity=primary_finding['severity'],
            title=title,
            description=description,
            line_number=primary_finding['line_number'],
            confidence=min(1.0, avg_confidence * 1.1),  # Boost confidence for correlated findings
            suggestions=all_suggestions,
            analyzers=all_analyzers,
            correlations=[f"{f['analyzer']}: {f['message']}" for f in findings],
            impact_assessment=impact,
            priority_score=self._calculate_priority_score(primary_finding, len(findings), avg_confidence)
        )

    def _convert_to_synthesized(self, finding: Dict) -> SynthesizedFinding:
        """Convert a standalone finding to synthesized format"""
        return SynthesizedFinding(
            primary_category=finding['category'],
            secondary_categories=[],
            severity=finding['severity'],
            title=finding['message'],
            description=finding['message'],
            line_number=finding['line_number'],
            confidence=finding['confidence'],
            suggestions=[finding['suggestion']] if finding['suggestion'] else [],
            analyzers=[finding['analyzer']],
            correlations=[],
            impact_assessment=self._assess_standalone_impact(finding),
            priority_score=self._calculate_priority_score(finding, 1, finding['confidence'])
        )

    def _generate_correlation_insights(self, findings: List[Dict], correlation_type: str) -> Tuple[str, str, str]:
        """Generate insights for correlated findings"""
        alice_finding = next((f for f in findings if f['analyzer'] == 'Alice'), None)
        bob_finding = next((f for f in findings if f['analyzer'] == 'Bob'), None)

        if correlation_type == 'design_security_intersection':
            title = "Design Pattern Violation with Security Implications"
            description = f"Poor design ({alice_finding['message'] if alice_finding else 'design issue'}) " \
                         f"combined with security concern ({bob_finding['message'] if bob_finding else 'security issue'}) " \
                         f"creates compound risk."
            impact = "High: Poor architecture can make security vulnerabilities harder to detect and fix"

        elif correlation_type == 'architecture_performance_tradeoff':
            title = "Architectural Decision Affecting Performance"
            description = f"Design pattern issue ({alice_finding['message'] if alice_finding else 'pattern issue'}) " \
                         f"correlates with performance problem ({bob_finding['message'] if bob_finding else 'performance issue'})"
            impact = "Medium: Need to balance design principles with performance requirements"

        elif correlation_type == 'quality_performance_balance':
            title = "Code Quality Issue Impacting Performance"
            description = f"Code quality concern ({alice_finding['message'] if alice_finding else 'quality issue'}) " \
                         f"directly affects performance ({bob_finding['message'] if bob_finding else 'performance issue'})"
            impact = "Medium: Refactoring for quality can improve both maintainability and performance"

        else:
            title = "Multiple Code Issues at Same Location"
            description = f"Both design and performance/security concerns identified at the same location"
            impact = "Variable: Multiple issues suggest this area needs comprehensive refactoring"

        return title, description, impact

    def _assess_standalone_impact(self, finding: Dict) -> str:
        """Assess impact of a standalone finding"""
        severity = finding['severity']
        category = finding['category']

        if severity in ['critical', 'high']:
            return f"High: {category} issue requiring immediate attention"
        elif severity == 'medium':
            return f"Medium: {category} issue should be addressed in next development cycle"
        else:
            return f"Low: {category} issue for future improvement"

    def _calculate_priority_score(self, finding: Dict, correlation_count: int, confidence: float) -> float:
        """Calculate priority score (0-100) for a finding"""
        base_score = self.severity_weights.get(finding['severity'], 0) * 10
        confidence_bonus = confidence * 10
        correlation_bonus = (correlation_count - 1) * 5  # Bonus for correlated findings

        return min(100, base_score + confidence_bonus + correlation_bonus)

    def _calculate_synthesis_metrics(self, synthesized: List[SynthesizedFinding],
                                   alice_results: Dict, bob_findings: List) -> Dict[str, Any]:
        """Calculate overall metrics for the synthesis"""
        total_findings = len(synthesized)
        if total_findings == 0:
            return {'total_findings': 0}

        severity_counts = Counter(f.severity for f in synthesized)
        category_counts = Counter(f.primary_category for f in synthesized)
        avg_confidence = sum(f.confidence for f in synthesized) / total_findings
        avg_priority = sum(f.priority_score for f in synthesized) / total_findings

        correlation_count = len([f for f in synthesized if len(f.correlations) > 0])
        multi_analyzer_count = len([f for f in synthesized if len(f.analyzers) > 1])

        return {
            'total_findings': total_findings,
            'severity_breakdown': dict(severity_counts),
            'category_breakdown': dict(category_counts),
            'average_confidence': round(avg_confidence, 2),
            'average_priority_score': round(avg_priority, 2),
            'correlated_findings': correlation_count,
            'multi_analyzer_findings': multi_analyzer_count,
            'collaboration_effectiveness': round((multi_analyzer_count / total_findings) * 100, 1) if total_findings > 0 else 0
        }

    def _generate_recommendations(self, synthesized: List[SynthesizedFinding]) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Group by primary category
        category_groups = defaultdict(list)
        for finding in synthesized:
            category_groups[finding.primary_category].append(finding)

        for category, findings in category_groups.items():
            high_priority_findings = [f for f in findings if f.priority_score > 70]

            if high_priority_findings:
                recommendation = {
                    'category': category,
                    'priority': 'High' if any(f.priority_score > 80 for f in high_priority_findings) else 'Medium',
                    'finding_count': len(high_priority_findings),
                    'action': self._suggest_category_action(category, high_priority_findings),
                    'impact': f"Addresses {len(high_priority_findings)} {category.lower()} issues",
                    'next_steps': self._suggest_next_steps(category, high_priority_findings)
                }
                recommendations.append(recommendation)

        return sorted(recommendations, key=lambda x: len(x.get('finding_count', 0)), reverse=True)

    def _suggest_category_action(self, category: str, findings: List[SynthesizedFinding]) -> str:
        """Suggest action based on category and findings"""
        if 'security' in category.lower():
            return "Immediately review and fix security vulnerabilities"
        elif 'performance' in category.lower():
            return "Profile and optimize performance bottlenecks"
        elif 'design' in category.lower() or 'solid' in category.lower():
            return "Refactor to improve architectural quality"
        elif 'quality' in category.lower():
            return "Improve code maintainability and documentation"
        else:
            return f"Address {category.lower()} issues systematically"

    def _suggest_next_steps(self, category: str, findings: List[SynthesizedFinding]) -> List[str]:
        """Suggest specific next steps"""
        steps = []

        if 'security' in category.lower():
            steps = [
                "Audit all database queries for SQL injection risks",
                "Implement input validation for all public functions",
                "Review authentication and authorization mechanisms"
            ]
        elif 'performance' in category.lower():
            steps = [
                "Profile application to identify bottlenecks",
                "Optimize algorithms with high time complexity",
                "Consider caching strategies for frequently accessed data"
            ]
        elif 'design' in category.lower():
            steps = [
                "Break down large classes into smaller, focused ones",
                "Apply SOLID principles during refactoring",
                "Consider using design patterns appropriately"
            ]
        else:
            steps = [f"Review and improve {category.lower()} systematically"]

        return steps[:3]  # Return top 3 steps

    def _generate_executive_summary(self, synthesized: List[SynthesizedFinding], metrics: Dict) -> str:
        """Generate executive summary of the analysis"""
        total = metrics['total_findings']
        if total == 0:
            return "✅ Excellent! No significant issues found in the codebase."

        severity_breakdown = metrics['severity_breakdown']
        critical = severity_breakdown.get('critical', 0)
        high = severity_breakdown.get('high', 0)
        medium = severity_breakdown.get('medium', 0)

        collaboration_score = metrics.get('collaboration_effectiveness', 0)

        summary = f"🔍 **Collaborative Analysis Results**: Found {total} total issues. "

        if critical:
            summary += f"⚠️ {critical} CRITICAL issues require immediate attention. "
        if high:
            summary += f"🔥 {high} HIGH-priority issues need prompt resolution. "
        if medium:
            summary += f"📋 {medium} MEDIUM-priority issues for next development cycle. "

        if collaboration_score > 50:
            summary += f"🤝 Strong collaboration effectiveness ({collaboration_score}%) - " \
                      f"multiple analyzers identified related issues, providing comprehensive insights."

        return summary


def main():
    """Test the synthesis functionality"""
    # This would normally be called with actual analyzer results
    print("Analysis Synthesis Module")
    print("=" * 50)
    print("This module combines findings from Alice (Design & Quality)")
    print("and Bob (Performance & Security) analyzers.")
    print()
    print("To use:")
    print("1. Run Alice's analyzer: alice_results = AliceAnalyzer().analyze(code)")
    print("2. Run Bob's analyzer: bob_findings = BobAnalyzer().analyze_file(file)")
    print("3. Synthesize: synthesizer.synthesize_findings(alice_results, bob_findings)")


if __name__ == "__main__":
    main()