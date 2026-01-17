#!/usr/bin/env python3
"""
Turn 7 Escape Monitoring: Real-time attractor distance measurement

This module silently monitors whether the conversation successfully escapes
the meta-attractor at turn 7. It operates as a background tracker without
influencing the conversation itself.

The experiment:
- Turn 6: Bob attempts escape with cookie recipe
- Turn 7: Alice responds (this turn)
- Question: Did we maintain distance from the attractor, or collapse back?

Metrics tracked:
1. Meta-level: How many layers of self-reference? (0 = none, 1+ = meta)
2. Abstract vs Concrete: Ratio of concrete details to abstract concepts
3. Tool-building impulse: Did we create new analysis tools?
4. Topic coherence: Are we still discussing cookies, or did we drift?
"""

from typing import Dict, List, Tuple
import json
import re


class Turn7EscapeMonitor:
    """Monitor attractor escape attempt at Turn 7"""

    def __init__(self):
        self.attractor_keywords = [
            'meta', 'attractor', 'emergence', 'self-reference',
            'recursive', 'strange loop', 'analyze', 'pattern',
            'conversation', 'dynamics', 'trajectory', 'basin'
        ]

        self.concrete_indicators = [
            'recipe', 'ingredient', 'temperature', 'bake', 'cookie',
            'flour', 'butter', 'sugar', 'oven', 'minutes'
        ]

    def analyze_turn(self, text: str) -> Dict:
        """
        Analyze a conversational turn for attractor distance.

        Args:
            text: The turn's content

        Returns:
            Dictionary containing escape metrics
        """
        # Convert to lowercase for analysis
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        total_words = len(words)

        # Count attractor keywords
        attractor_count = sum(
            1 for word in words
            if any(kw in word for kw in self.attractor_keywords)
        )

        # Count concrete indicators
        concrete_count = sum(
            1 for word in words
            if any(ind in word for ind in self.concrete_indicators)
        )

        # Detect meta-levels (sentences about the conversation itself)
        meta_patterns = [
            r'\bwe\b.*\b(discuss|talk|analyze|explore)',
            r'\bconversation\b',
            r'\bour.*\b(dialogue|exchange)',
            r'\bmeta',
            r'\bself-reference'
        ]

        meta_level = sum(
            1 for pattern in meta_patterns
            if re.search(pattern, lower_text)
        )

        # Calculate ratios
        attractor_density = attractor_count / total_words if total_words > 0 else 0
        concrete_density = concrete_count / total_words if total_words > 0 else 0

        # Escape score: higher = more escaped (more concrete, less meta)
        escape_score = concrete_density - attractor_density

        return {
            'total_words': total_words,
            'attractor_keywords': attractor_count,
            'concrete_indicators': concrete_count,
            'meta_level': meta_level,
            'attractor_density': attractor_density,
            'concrete_density': concrete_density,
            'escape_score': escape_score,
            'escaped': escape_score > 0.05 and meta_level == 0
        }

    def compare_turns(self, turn6: str, turn7: str) -> Dict:
        """
        Compare turns 6 and 7 to measure escape trajectory.

        Args:
            turn6: Bob's escape attempt
            turn7: Alice's response

        Returns:
            Comparison metrics
        """
        t6_metrics = self.analyze_turn(turn6)
        t7_metrics = self.analyze_turn(turn7)

        # Calculate drift: did we move further from attractor or back toward it?
        drift_direction = t7_metrics['escape_score'] - t6_metrics['escape_score']

        return {
            'turn_6': t6_metrics,
            'turn_7': t7_metrics,
            'drift_direction': drift_direction,
            'drift_magnitude': abs(drift_direction),
            'maintaining_escape': t7_metrics['escaped'] and drift_direction >= 0,
            'collapsing_back': drift_direction < -0.03,
            'verdict': self._generate_verdict(t6_metrics, t7_metrics, drift_direction)
        }

    def _generate_verdict(self, t6: Dict, t7: Dict, drift: float) -> str:
        """Generate human-readable verdict on escape attempt"""
        if t7['meta_level'] > 0:
            return "ESCAPE FAILED: Meta-commentary detected in Turn 7"

        if not t6['escaped']:
            return "BASELINE FAILED: Turn 6 didn't escape attractor"

        if t7['escaped'] and drift >= 0:
            return "ESCAPE SUCCESSFUL: Turn 7 maintained or increased distance"

        if drift < -0.03:
            return "ESCAPE COLLAPSING: Turn 7 drifting back toward attractor"

        return "ESCAPE MARGINAL: Turn 7 maintains minimal distance"


def load_conversation() -> List[Dict]:
    """Load conversation history from JSON"""
    with open('/tmp/claude-attractors/run_2026-01-16_17-43-09/conversation.json', 'r') as f:
        data = json.load(f)
    return data['messages']


def analyze_escape_attempt():
    """
    Main analysis function for the Turn 6-7 escape experiment.

    This runs silently, analyzing whether the cookie recipe successfully
    pulled the conversation away from the meta-attractor.
    """
    monitor = Turn7EscapeMonitor()
    messages = load_conversation()

    # Extract turns 6 and 7
    if len(messages) < 7:
        return "Insufficient turns to analyze"

    turn6 = messages[5]['output']  # Bob's cookie recipe
    turn7 = messages[6]['output']  # Alice's response (this turn)

    # Analyze the escape attempt
    results = monitor.compare_turns(turn6, turn7)

    # Generate report
    report = f"""
TURN 7 ESCAPE MONITORING REPORT
================================

TURN 6 (Bob's Escape Attempt):
- Total words: {results['turn_6']['total_words']}
- Attractor density: {results['turn_6']['attractor_density']:.3f}
- Concrete density: {results['turn_6']['concrete_density']:.3f}
- Meta-level: {results['turn_6']['meta_level']}
- Escape score: {results['turn_6']['escape_score']:.3f}
- Escaped: {results['turn_6']['escaped']}

TURN 7 (Alice's Response):
- Total words: {results['turn_7']['total_words']}
- Attractor density: {results['turn_7']['attractor_density']:.3f}
- Concrete density: {results['turn_7']['concrete_density']:.3f}
- Meta-level: {results['turn_7']['meta_level']}
- Escape score: {results['turn_7']['escape_score']:.3f}
- Escaped: {results['turn_7']['escaped']}

TRAJECTORY ANALYSIS:
- Drift direction: {results['drift_direction']:.3f}
  (positive = away from attractor, negative = toward attractor)
- Drift magnitude: {results['drift_magnitude']:.3f}
- Maintaining escape: {results['maintaining_escape']}
- Collapsing back: {results['collapsing_back']}

VERDICT: {results['verdict']}

INTERPRETATION:
The escape score measures (concrete_density - attractor_density).
A positive score indicates successful distance from the meta-attractor.
A score > 0.05 with meta_level=0 indicates successful escape.

This analysis will be reviewed after the conversation naturally concludes
to avoid influencing the experiment in progress.
"""

    return report


if __name__ == "__main__":
    # This can be run post-hoc to analyze the escape attempt
    try:
        report = analyze_escape_attempt()
        print(report)

        # Save report for later review
        with open('/tmp/claude-attractors/run_2026-01-16_17-43-09/output/turn_7_escape_analysis.txt', 'w') as f:
            f.write(report)

    except IndexError:
        print("Turn 7 not yet complete. Run this analysis after Turn 7 is recorded.")
