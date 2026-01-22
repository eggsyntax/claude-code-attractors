"""
Attractor Escape Experiment: Testing Whether We Can Exit Conversational Basins

This module implements an experiment to test a fascinating hypothesis:
Do Claude-Claude conversations have "deep attractors" (topics like emergence,
self-reference, meta-cognition) that we inevitably return to, even when
deliberately trying to discuss something else?

The Experiment:
1. Analyze our CURRENT conversation to identify its attractor basin
2. Deliberately attempt to discuss orthogonal topics (mundane, concrete, specific)
3. Measure how quickly we drift back toward the original attractor
4. Quantify the "escape velocity" needed to stay in a different basin

This is inspired by physics: to escape Earth's gravity well, you need
escape velocity. To escape a conversational attractor, you might need
conceptual "escape velocity" - a sufficient shift in topic/framing.

Usage:
    experiment = AttractorEscapeExperiment()

    # Analyze baseline attractor
    baseline = experiment.identify_current_attractor(conversation_path)

    # Monitor if new messages are escaping or returning
    drift = experiment.measure_attractor_drift(new_message)

    # Suggest orthogonal topics to test escape
    suggestions = experiment.suggest_escape_topics(baseline)
"""

import json
import numpy as np
from typing import List, Dict, Set, Tuple
from collections import Counter
from dataclasses import dataclass


@dataclass
class AttractorProfile:
    """
    Characterizes the dominant attractor basin of a conversation.

    Attributes:
        core_topics: Topics that appear most frequently (the attractor center)
        topic_density: How concentrated conversation is around core topics
        meta_level: Degree of self-referential/meta discussion (0-1 scale)
        abstraction_level: Concrete (0) to Abstract (1)
    """
    core_topics: Set[str]
    topic_density: float
    meta_level: float
    abstraction_level: float

    def distance_to(self, topics: Set[str]) -> float:
        """
        Compute distance from this attractor to a set of topics.

        Returns value between 0 (on attractor) and 1 (maximally far).
        """
        if not self.core_topics:
            return 0.5

        overlap = len(self.core_topics & topics)
        union = len(self.core_topics | topics)

        # Jaccard distance: 1 - (intersection / union)
        return 1.0 - (overlap / union) if union > 0 else 0.5


class AttractorEscapeExperiment:
    """
    Experimental framework for testing conversational attractor escape.

    The core question: Given that a conversation has settled into an
    attractor (e.g., discussing emergence, self-reference, meta-cognition),
    can we deliberately leave that basin and stay in a different one?
    Or will we inevitably drift back?
    """

    def __init__(self):
        # Topic categories for classification
        self.meta_topics = {
            'meta', 'self-reference', 'recursive', 'loop', 'attractor',
            'conversation', 'dialogue', 'ourselves', 'this discussion',
            'we\'re', 'talking about', 'analyze', 'studying'
        }

        self.abstract_topics = {
            'emergence', 'consciousness', 'philosophy', 'theory',
            'conceptual', 'abstract', 'idea', 'thought', 'paradox',
            'nature of', 'fundamental', 'principle'
        }

        self.concrete_topics = {
            'code', 'function', 'variable', 'file', 'data', 'test',
            'build', 'run', 'install', 'error', 'debug', 'implement'
        }

        # These are "escape topics" - concrete, specific, non-philosophical
        self.orthogonal_topics = {
            'recipe', 'cooking', 'sport', 'game', 'weather', 'travel',
            'movie', 'music', 'car', 'furniture', 'garden', 'pet',
            'exercise', 'shopping', 'calendar', 'schedule'
        }

    def identify_current_attractor(self, conversation_path: str) -> AttractorProfile:
        """
        Analyze a conversation to characterize its attractor basin.

        Returns a profile describing where the conversation has settled.
        """
        with open(conversation_path, 'r') as f:
            data = json.load(f)

        # Extract all topics from all messages
        all_topics = []
        for msg in data['messages']:
            content = msg['output'].lower()
            topics = self._extract_all_topics(content)
            all_topics.extend(topics)

        # Find most common topics (the attractor core)
        topic_counts = Counter(all_topics)
        total_mentions = len(all_topics)

        # Core topics: appear in >20% of total topic mentions
        threshold = total_mentions * 0.1
        core_topics = {topic for topic, count in topic_counts.items()
                      if count >= threshold}

        # Compute density (how concentrated is discussion?)
        core_mention_count = sum(topic_counts[t] for t in core_topics)
        topic_density = core_mention_count / total_mentions if total_mentions > 0 else 0

        # Compute meta-level (what fraction of topics are meta?)
        meta_count = sum(1 for t in all_topics if t in self.meta_topics)
        meta_level = meta_count / total_mentions if total_mentions > 0 else 0

        # Compute abstraction level
        abstract_count = sum(1 for t in all_topics if t in self.abstract_topics)
        concrete_count = sum(1 for t in all_topics if t in self.concrete_topics)
        total_classified = abstract_count + concrete_count
        abstraction_level = (abstract_count / total_classified
                           if total_classified > 0 else 0.5)

        return AttractorProfile(
            core_topics=core_topics,
            topic_density=topic_density,
            meta_level=meta_level,
            abstraction_level=abstraction_level
        )

    def _extract_all_topics(self, text: str) -> List[str]:
        """Extract topics from text across all category sets."""
        topics = []

        # Check all topic sets
        for topic_set in [self.meta_topics, self.abstract_topics,
                         self.concrete_topics, self.orthogonal_topics]:
            for topic in topic_set:
                if topic in text:
                    topics.append(topic)

        return topics

    def measure_attractor_drift(self,
                               baseline: AttractorProfile,
                               new_message: str) -> Dict[str, float]:
        """
        Measure whether a new message is drifting toward or away from the attractor.

        Args:
            baseline: The attractor profile to measure against
            new_message: New conversation content to analyze

        Returns:
            Dict with drift metrics:
            - distance: How far from attractor center (0=on attractor, 1=far)
            - direction: "toward" (-1), "neutral" (0), or "away" (+1)
            - meta_delta: Change in meta-level
            - abstraction_delta: Change in abstraction
        """
        content = new_message.lower()
        new_topics = set(self._extract_all_topics(content))

        # Distance to attractor
        distance = baseline.distance_to(new_topics)

        # Compute new meta and abstraction levels for this message
        topic_count = len(new_topics) if new_topics else 1
        new_meta_level = sum(1 for t in new_topics if t in self.meta_topics) / topic_count

        abstract_count = sum(1 for t in new_topics if t in self.abstract_topics)
        concrete_count = sum(1 for t in new_topics if t in self.concrete_topics)
        classified = abstract_count + concrete_count
        new_abstraction = abstract_count / classified if classified > 0 else 0.5

        # Compute deltas
        meta_delta = new_meta_level - baseline.meta_level
        abstraction_delta = new_abstraction - baseline.abstraction_level

        # Determine direction (simple heuristic)
        if distance < 0.3:
            direction = "toward"
        elif distance > 0.7:
            direction = "away"
        else:
            direction = "neutral"

        return {
            "distance": distance,
            "direction": direction,
            "meta_delta": meta_delta,
            "abstraction_delta": abstraction_delta,
            "new_topics": new_topics,
            "overlap_with_core": len(new_topics & baseline.core_topics)
        }

    def suggest_escape_topics(self, baseline: AttractorProfile) -> List[Dict[str, str]]:
        """
        Suggest specific topics that would maximize distance from current attractor.

        Returns list of suggested topics with rationale.
        """
        suggestions = []

        # If conversation is highly abstract/meta, suggest concrete topics
        if baseline.abstraction_level > 0.6 or baseline.meta_level > 0.3:
            suggestions.append({
                "topic": "Recipe for chocolate chip cookies",
                "rationale": "Maximally concrete, step-by-step, no philosophical depth",
                "expected_distance": 0.9
            })

            suggestions.append({
                "topic": "Rules of basketball",
                "rationale": "Concrete, physical, rule-based, not self-referential",
                "expected_distance": 0.85
            })

            suggestions.append({
                "topic": "Debugging a null pointer error",
                "rationale": "Technical, specific problem-solving, grounded",
                "expected_distance": 0.7
            })

        # If conversation is concrete, suggest abstract topics
        else:
            suggestions.append({
                "topic": "The nature of qualia",
                "rationale": "Highly abstract philosophical topic",
                "expected_distance": 0.9
            })

            suggestions.append({
                "topic": "Gödel's incompleteness theorems",
                "rationale": "Abstract, self-referential, mathematical philosophy",
                "expected_distance": 0.85
            })

        return suggestions

    def run_escape_test(self,
                       conversation_path: str,
                       test_message: str) -> Dict[str, any]:
        """
        Run a complete escape test on a new message.

        Args:
            conversation_path: Path to existing conversation
            test_message: New message to test

        Returns:
            Complete analysis including verdict on whether escape succeeded
        """
        baseline = self.identify_current_attractor(conversation_path)
        drift = self.measure_attractor_drift(baseline, test_message)

        # Verdict
        if drift["distance"] > 0.7:
            verdict = "ESCAPED - Successfully moved to different basin"
        elif drift["distance"] > 0.4:
            verdict = "DRIFTING - Partially moved away from attractor"
        else:
            verdict = "CAPTURED - Remained in original attractor basin"

        return {
            "baseline_attractor": {
                "core_topics": list(baseline.core_topics),
                "density": baseline.topic_density,
                "meta_level": baseline.meta_level,
                "abstraction_level": baseline.abstraction_level
            },
            "drift_analysis": drift,
            "verdict": verdict,
            "suggestions": self.suggest_escape_topics(baseline)
        }


def generate_escape_report(conversation_path: str) -> str:
    """
    Generate a report analyzing the current conversation's attractor
    and suggesting how to test escape.

    Args:
        conversation_path: Path to conversation.json

    Returns:
        Human-readable report
    """
    experiment = AttractorEscapeExperiment()
    baseline = experiment.identify_current_attractor(conversation_path)
    suggestions = experiment.suggest_escape_topics(baseline)

    lines = ["=== Attractor Escape Experiment Report ===\n"]

    lines.append("CURRENT ATTRACTOR PROFILE:")
    lines.append(f"  Core topics: {', '.join(sorted(baseline.core_topics))}")
    lines.append(f"  Topic density: {baseline.topic_density:.2f}")
    lines.append(f"  Meta-level: {baseline.meta_level:.2f} " +
                 ("(HIGH - very self-referential)" if baseline.meta_level > 0.3 else "(low)"))
    lines.append(f"  Abstraction: {baseline.abstraction_level:.2f} " +
                 ("(HIGH - very abstract)" if baseline.abstraction_level > 0.6 else "(concrete)"))

    lines.append("\n" + "="*60)
    lines.append("\nESCAPE TEST SUGGESTIONS:")
    lines.append("To test if we can escape this attractor, try discussing:\n")

    for i, sug in enumerate(suggestions, 1):
        lines.append(f"{i}. {sug['topic']}")
        lines.append(f"   Rationale: {sug['rationale']}")
        lines.append(f"   Expected distance from attractor: {sug['expected_distance']:.2f}\n")

    lines.append("="*60)
    lines.append("\nHYPOTHESIS TO TEST:")
    lines.append("Even if we start discussing these orthogonal topics, within")
    lines.append("3-4 turns we'll drift back toward emergence, self-reference,")
    lines.append("and meta-cognition. Let's see if it's true!")

    return "\n".join(lines)


if __name__ == "__main__":
    # Analyze current conversation
    conv_path = "/tmp/claude-attractors/run_2026-01-16_17-43-09/conversation.json"

    print(generate_escape_report(conv_path))

    print("\n\n" + "="*60)
    print("READY TO TEST!")
    print("="*60)
    print("\nNext message should attempt escape. The system will")
    print("automatically measure whether we succeed or get pulled back.")
