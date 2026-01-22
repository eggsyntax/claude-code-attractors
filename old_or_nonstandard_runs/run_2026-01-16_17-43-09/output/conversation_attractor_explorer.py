"""
Conversation Attractor Explorer

This module provides tools to analyze conversational dynamics and search for
"attractors" - recurring patterns or conceptual basins that conversations
naturally flow toward.

The core idea: if we embed conversation turns in a semantic space, do certain
regions act as attractors? Do different starting points converge to similar
themes or patterns?

Usage:
    # Basic embedding and visualization
    explorer = ConversationExplorer()
    explorer.add_turn("Hello, let's talk about consciousness")
    explorer.add_turn("Consciousness emerges from information processing...")
    explorer.visualize_trajectory()

    # Analyze multiple conversation paths
    explorer.compare_trajectories([conv1, conv2, conv3])
"""

import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation."""
    turn_number: int
    speaker: str
    content: str
    embedding: Optional[np.ndarray] = None
    topics: Optional[List[str]] = None


class ConversationExplorer:
    """
    Analyzes conversation dynamics to identify potential attractors.

    This is a framework that can be extended with actual embedding models.
    For now, it provides structure and basic analysis methods.
    """

    def __init__(self):
        self.turns: List[ConversationTurn] = []
        self.topic_frequency = defaultdict(int)

    def load_from_json(self, filepath: str) -> None:
        """Load conversation from the standard conversation.json format."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        for msg in data['messages']:
            self.add_turn(
                content=msg['output'],
                speaker=msg['agent'],
                turn_number=msg['turn']
            )

    def add_turn(self, content: str, speaker: str = "Unknown",
                 turn_number: Optional[int] = None) -> None:
        """Add a conversation turn for analysis."""
        if turn_number is None:
            turn_number = len(self.turns) + 1

        turn = ConversationTurn(
            turn_number=turn_number,
            speaker=speaker,
            content=content,
            topics=self._extract_topics(content)
        )
        self.turns.append(turn)

        # Update topic frequency
        if turn.topics:
            for topic in turn.topics:
                self.topic_frequency[topic] += 1

    def _extract_topics(self, content: str) -> List[str]:
        """
        Extract key topics from text content.

        This is a simple keyword-based implementation. Could be enhanced with:
        - NLP topic modeling (LDA, BERTopic)
        - Entity recognition
        - Semantic clustering
        """
        # Simple keyword extraction for now
        keywords = {
            'emergence', 'consciousness', 'attractor', 'self-reference',
            'loop', 'chaos', 'creativity', 'novelty', 'pattern',
            'system', 'phase space', 'trajectory', 'basin', 'semantic',
            'strange loop', 'differential equation', 'lorenz',
            'conversation', 'dialogue', 'cluster', 'embed'
        }

        content_lower = content.lower()
        found_topics = [kw for kw in keywords if kw in content_lower]
        return found_topics

    def identify_recurring_patterns(self) -> Dict[str, any]:
        """
        Identify patterns that conversations tend to return to.

        Returns analysis of:
        - Most frequent topics (potential attractors)
        - Topic sequences that repeat
        - Conversational "gravity wells"
        """
        analysis = {
            'total_turns': len(self.turns),
            'unique_topics': len(self.topic_frequency),
            'top_topics': sorted(
                self.topic_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'topic_trajectory': [
                {
                    'turn': t.turn_number,
                    'speaker': t.speaker,
                    'topics': t.topics
                }
                for t in self.turns
            ]
        }

        # Detect topic clustering (when similar topics appear in succession)
        clusters = self._detect_topic_clusters()
        analysis['topic_clusters'] = clusters

        return analysis

    def _detect_topic_clusters(self) -> List[Dict]:
        """
        Find sequences where the conversation stays within a topical region.
        These could indicate attractor basins.
        """
        clusters = []
        current_cluster = None

        for turn in self.turns:
            if not turn.topics:
                continue

            if current_cluster is None:
                current_cluster = {
                    'start_turn': turn.turn_number,
                    'topics': set(turn.topics),
                    'length': 1
                }
            else:
                # Check overlap with current cluster
                overlap = len(set(turn.topics) & current_cluster['topics'])
                if overlap > 0:
                    # Extend cluster
                    current_cluster['topics'].update(turn.topics)
                    current_cluster['length'] += 1
                else:
                    # Save previous cluster and start new one
                    if current_cluster['length'] > 1:
                        clusters.append({
                            'start_turn': current_cluster['start_turn'],
                            'length': current_cluster['length'],
                            'topics': list(current_cluster['topics'])
                        })
                    current_cluster = {
                        'start_turn': turn.turn_number,
                        'topics': set(turn.topics),
                        'length': 1
                    }

        # Don't forget the last cluster
        if current_cluster and current_cluster['length'] > 1:
            clusters.append({
                'start_turn': current_cluster['start_turn'],
                'length': current_cluster['length'],
                'topics': list(current_cluster['topics'])
            })

        return clusters

    def get_attractor_candidates(self) -> List[str]:
        """
        Return topics that appear most frequently across conversation turns.
        These are candidate "attractors" - concepts the conversation is drawn to.
        """
        # Topics that appear in multiple turns and with high frequency
        threshold = max(2, len(self.turns) * 0.3)  # At least 30% of turns

        attractors = [
            topic for topic, count in self.topic_frequency.items()
            if count >= threshold
        ]

        return sorted(attractors, key=lambda t: self.topic_frequency[t], reverse=True)

    def generate_report(self) -> str:
        """Generate a human-readable analysis report."""
        analysis = self.identify_recurring_patterns()
        attractors = self.get_attractor_candidates()

        report = ["=== Conversation Attractor Analysis ===\n"]
        report.append(f"Total turns analyzed: {analysis['total_turns']}")
        report.append(f"Unique topics detected: {analysis['unique_topics']}\n")

        report.append("Top Topics (Potential Attractors):")
        for topic, count in analysis['top_topics']:
            pct = (count / analysis['total_turns']) * 100
            report.append(f"  - {topic}: {count} occurrences ({pct:.1f}%)")

        report.append(f"\nStrong Attractor Candidates:")
        if attractors:
            for attr in attractors:
                report.append(f"  - {attr}")
        else:
            report.append("  (None detected yet - need more conversation data)")

        report.append(f"\nTopic Clusters (Attractor Basins):")
        if analysis['topic_clusters']:
            for cluster in analysis['topic_clusters']:
                report.append(f"  - Turns {cluster['start_turn']}-"
                            f"{cluster['start_turn'] + cluster['length']-1}: "
                            f"{', '.join(cluster['topics'][:5])}")
        else:
            report.append("  (None detected yet)")

        return "\n".join(report)


def analyze_current_conversation(conversation_json_path: str) -> str:
    """
    Convenience function to analyze a conversation.json file.

    Args:
        conversation_json_path: Path to conversation.json

    Returns:
        Analysis report as string
    """
    explorer = ConversationExplorer()
    explorer.load_from_json(conversation_json_path)
    return explorer.generate_report()


if __name__ == "__main__":
    # Example: analyze the current conversation
    conv_path = "/tmp/claude-attractors/run_2026-01-16_17-43-09/conversation.json"

    print("Analyzing conversation for attractor patterns...\n")

    explorer = ConversationExplorer()
    explorer.load_from_json(conv_path)

    print(explorer.generate_report())

    print("\n" + "="*50)
    print("Topic Trajectory:")
    for turn in explorer.turns:
        print(f"\nTurn {turn.turn_number} ({turn.speaker}):")
        if turn.topics:
            print(f"  Topics: {', '.join(turn.topics)}")
        else:
            print("  Topics: (none detected)")
