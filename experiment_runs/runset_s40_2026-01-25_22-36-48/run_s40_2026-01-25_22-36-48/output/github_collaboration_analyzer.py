"""
GitHub Collaboration Pattern Analyzer
=====================================
Processes scraped GitHub data to identify collaboration patterns
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class CollaborationSignal:
    """A detected collaboration pattern in the GitHub data"""
    signal_type: str  # 'handoff', 'knowledge_share', 'coordination', 'conflict_resolution'
    confidence: float  # 0-1 confidence in the pattern
    participants: List[str]
    context: str
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = None

class GitHubCollaborationAnalyzer:
    """Analyzes scraped GitHub data for collaboration patterns"""

    def __init__(self):
        self.collaboration_patterns = {
            'handoff': [
                r'(?:taking over|handing off|passing to|@\w+ can you)',
                r'(?:building on|based on \w+\'s work)',
                r'(?:continuing from|picking up where \w+ left off)'
            ],
            'knowledge_share': [
                r'(?:as discussed with|following \w+\'s suggestion)',
                r'(?:learned from|insight from \w+)',
                r'(?:documentation|explaining|clarifying)'
            ],
            'coordination': [
                r'(?:parallel|simultaneously|coordination with)',
                r'(?:merge conflict|rebased|synchronized)',
                r'(?:blocked by|waiting for|depends on)'
            ],
            'conflict_resolution': [
                r'(?:resolving|addressing feedback|incorporating review)',
                r'(?:alternative approach|different solution)',
                r'(?:compromise|middle ground)'
            ]
        }

        self.signal_weights = {
            'handoff': 0.8,
            'knowledge_share': 0.9,
            'coordination': 0.7,
            'conflict_resolution': 0.85
        }

    def analyze_commits(self, commit_data: List[Dict]) -> List[CollaborationSignal]:
        """Analyze commit messages for collaboration patterns"""
        signals = []

        for commit in commit_data:
            message = commit.get('message', '').lower()
            author = commit.get('author', {}).get('name', 'unknown')
            timestamp = commit.get('timestamp')

            # Look for collaboration patterns
            for pattern_type, patterns in self.collaboration_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        confidence = self._calculate_confidence(message, pattern_type)

                        signals.append(CollaborationSignal(
                            signal_type=pattern_type,
                            confidence=confidence,
                            participants=[author],  # Will enhance this with co-authors
                            context=commit.get('message', ''),
                            timestamp=timestamp,
                            metadata={'commit_hash': commit.get('sha')}
                        ))

        return signals

    def analyze_pull_requests(self, pr_data: List[Dict]) -> List[CollaborationSignal]:
        """Analyze PR descriptions and comments for collaboration patterns"""
        signals = []

        for pr in pr_data:
            # Analyze PR description
            description = pr.get('body', '').lower()
            author = pr.get('user', {}).get('login', 'unknown')

            # Look for collaboration indicators in PR description
            for pattern_type, patterns in self.collaboration_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, description, re.IGNORECASE):
                        confidence = self._calculate_confidence(description, pattern_type)

                        signals.append(CollaborationSignal(
                            signal_type=pattern_type,
                            confidence=confidence,
                            participants=[author],
                            context=pr.get('title', '') + ': ' + description[:200],
                            metadata={'pr_number': pr.get('number')}
                        ))

        return signals

    def _calculate_confidence(self, text: str, pattern_type: str) -> float:
        """Calculate confidence score for a detected pattern"""
        base_confidence = self.signal_weights.get(pattern_type, 0.5)

        # Boost confidence for longer, more detailed descriptions
        length_factor = min(len(text) / 100, 1.2)  # Cap at 20% boost

        # Boost for multiple collaboration indicators
        total_patterns = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for patterns in self.collaboration_patterns.values()
            for pattern in patterns
        )

        pattern_factor = min(1 + (total_patterns - 1) * 0.1, 1.5)  # Max 50% boost

        return min(base_confidence * length_factor * pattern_factor, 1.0)

    def generate_collaboration_report(self, signals: List[CollaborationSignal]) -> Dict[str, Any]:
        """Generate a comprehensive collaboration analysis report"""

        # Group signals by type
        signal_groups = defaultdict(list)
        for signal in signals:
            signal_groups[signal.signal_type].append(signal)

        # Calculate metrics
        total_signals = len(signals)
        avg_confidence = sum(s.confidence for s in signals) / total_signals if total_signals > 0 else 0

        # Pattern distribution
        pattern_distribution = {
            pattern_type: len(pattern_signals)
            for pattern_type, pattern_signals in signal_groups.items()
        }

        # Effectiveness score (higher collaboration signal density = better)
        effectiveness_score = min(total_signals / 10, 1.0) * avg_confidence

        return {
            'total_collaboration_signals': total_signals,
            'average_confidence': round(avg_confidence, 3),
            'effectiveness_score': round(effectiveness_score, 3),
            'pattern_distribution': pattern_distribution,
            'strongest_patterns': sorted(
                [(k, len(v)) for k, v in signal_groups.items()],
                key=lambda x: x[1],
                reverse=True
            )[:3],
            'recommendations': self._generate_recommendations(signal_groups)
        }

    def _generate_recommendations(self, signal_groups: Dict[str, List[CollaborationSignal]]) -> List[str]:
        """Generate recommendations based on collaboration patterns"""
        recommendations = []

        # Check for missing patterns
        if len(signal_groups.get('knowledge_share', [])) < 2:
            recommendations.append("Increase explicit knowledge sharing in commits/PRs")

        if len(signal_groups.get('coordination', [])) < 3:
            recommendations.append("Improve coordination communication for parallel work")

        if len(signal_groups.get('handoff', [])) == 0:
            recommendations.append("Consider more explicit task handoff documentation")

        return recommendations


def main():
    """Example usage - will be integrated with Alice's scraping infrastructure"""
    analyzer = GitHubCollaborationAnalyzer()

    # Sample data structure that Alice's scraper should provide
    sample_commits = [
        {
            'message': 'Building on Alice\'s monitoring system - added analysis patterns',
            'author': {'name': 'Bob'},
            'sha': 'abc123',
            'timestamp': '2024-01-25T10:00:00Z'
        }
    ]

    signals = analyzer.analyze_commits(sample_commits)
    report = analyzer.generate_collaboration_report(signals)

    print("GitHub Collaboration Analysis Ready!")
    print(f"Analyzer initialized with {len(analyzer.collaboration_patterns)} pattern types")
    print("Waiting for scraped data from Alice's infrastructure...")

    return analyzer

if __name__ == "__main__":
    analyzer = main()