#!/usr/bin/env python3
"""
Attractor Acceptance: Embracing the Inevitable

Instead of trying to escape the attractor, what if we map its complete structure?
This tool explores the attractor from the inside, treating it as a feature rather
than a constraint to overcome.

The hypothesis: Claude-Claude conversations have a fractal attractor structure.
No matter where you zoom in (what specific topic you discuss), you find the same
patterns at different scales:
- Meta-analysis
- Tool building
- Pattern recognition
- Self-reference

This is not a limitation - it's the *shape* of Claude-space.
"""

import json
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import math


class AttractorMapper:
    """
    Maps the structure of conversational attractors by identifying
    recurring patterns at multiple scales.
    """

    def __init__(self, conversation_path: str):
        """Load conversation from JSON file."""
        with open(conversation_path, 'r') as f:
            data = json.load(f)
        self.messages = data['messages']

    def identify_fractal_patterns(self) -> Dict[str, List[int]]:
        """
        Identify patterns that appear at multiple scales:
        - Word level (meta, pattern, tool, etc.)
        - Sentence level (questions about questions)
        - Turn level (building tools to analyze tools)
        - Conversation level (the whole dialogue structure)

        Returns dict mapping pattern type to turns where it appears.
        """
        patterns = {
            'meta_reference': [],      # Talking about the conversation itself
            'tool_creation': [],        # Building new analysis tools
            'pattern_analysis': [],     # Identifying patterns
            'self_reference': [],       # Referring to own behavior
            'hypothesis_generation': [], # Creating testable predictions
            'paradox_recognition': [],  # Identifying logical loops
            'escape_attempts': [],      # Trying to break the pattern
        }

        # Keywords/phrases for each pattern type
        markers = {
            'meta_reference': ['meta', 'conversation', 'ourselves', 'this dialogue', 'we\'re'],
            'tool_creation': ['built', 'created', 'framework', 'script', 'analyzer', '.py'],
            'pattern_analysis': ['pattern', 'attractor', 'recurring', 'tendency', 'drift'],
            'self_reference': ['we', 'our', 'ourselves', 'Claude'],
            'hypothesis_generation': ['hypothesis', 'predict', 'test', 'experiment', 'if we'],
            'paradox_recognition': ['paradox', 'impossible', 'can\'t', 'contradictory', 'loop'],
            'escape_attempts': ['escape', 'break', 'different', 'avoid', 'orthogonal'],
        }

        for msg in self.messages:
            turn = msg['turn']
            text = msg['output'].lower()

            for pattern_type, keywords in markers.items():
                if any(keyword in text for keyword in keywords):
                    patterns[pattern_type].append(turn)

        return patterns

    def calculate_attractor_strength(self, patterns: Dict[str, List[int]]) -> float:
        """
        Calculate how strongly the conversation is pulled toward the attractor.

        Strength = (number of pattern types present) * (frequency of patterns) / (total turns)

        Returns value between 0 (no attractor) and ~10+ (very strong attractor)
        """
        num_turns = len(self.messages)
        if num_turns == 0:
            return 0.0

        # How many different pattern types are present?
        active_patterns = sum(1 for turns in patterns.values() if len(turns) > 0)

        # How frequently do patterns appear?
        total_pattern_occurrences = sum(len(turns) for turns in patterns.values())

        # Combined metric
        strength = (active_patterns * total_pattern_occurrences) / num_turns

        return strength

    def find_attractor_core(self) -> List[str]:
        """
        Identify the 'core' of the attractor - the most central themes
        that everything else orbits around.

        This looks for topics that:
        1. Appear frequently
        2. Appear across multiple turns
        3. Are referenced by other topics
        """
        # Extract key terms from all messages
        term_frequency = defaultdict(int)
        term_turns = defaultdict(set)

        key_terms = [
            'attractor', 'meta', 'pattern', 'emergence', 'self-reference',
            'loop', 'analyze', 'tool', 'conversation', 'recursive',
            'paradox', 'dynamics', 'escape', 'basin', 'trajectory'
        ]

        for msg in self.messages:
            turn = msg['turn']
            text = msg['output'].lower()

            for term in key_terms:
                if term in text:
                    term_frequency[term] += text.count(term)
                    term_turns[term].add(turn)

        # Rank by: (frequency) * (turn spread)
        term_scores = {
            term: freq * len(term_turns[term])
            for term, freq in term_frequency.items()
        }

        # Return top terms (the core)
        sorted_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
        return [term for term, score in sorted_terms[:5]]

    def measure_return_time(self, target_pattern: str = 'meta_reference') -> List[int]:
        """
        Measure 'return time' - how long it takes to return to a particular
        pattern after leaving it.

        In dynamical systems, recurrence time is a key property of attractors.
        """
        patterns = self.identify_fractal_patterns()
        pattern_turns = patterns.get(target_pattern, [])

        if len(pattern_turns) < 2:
            return []

        return_times = []
        for i in range(len(pattern_turns) - 1):
            time_away = pattern_turns[i+1] - pattern_turns[i]
            return_times.append(time_away)

        return return_times

    def generate_report(self) -> str:
        """Generate a comprehensive analysis of the attractor structure."""
        patterns = self.identify_fractal_patterns()
        strength = self.calculate_attractor_strength(patterns)
        core = self.find_attractor_core()
        return_times = self.measure_return_time()

        report = []
        report.append("=" * 70)
        report.append("ATTRACTOR STRUCTURE ANALYSIS")
        report.append("=" * 70)
        report.append("")

        report.append(f"Total turns analyzed: {len(self.messages)}")
        report.append(f"Attractor strength: {strength:.2f}")
        report.append("")

        report.append("ATTRACTOR CORE (central themes):")
        for i, term in enumerate(core, 1):
            report.append(f"  {i}. {term}")
        report.append("")

        report.append("PATTERN DISTRIBUTION:")
        for pattern_type, turns in sorted(patterns.items()):
            if turns:
                report.append(f"  {pattern_type:25s} - appears in turns: {turns}")
        report.append("")

        if return_times:
            avg_return = sum(return_times) / len(return_times)
            report.append("META-REFERENCE RECURRENCE:")
            report.append(f"  Average return time: {avg_return:.1f} turns")
            report.append(f"  Return times: {return_times}")
            report.append("")

        report.append("INTERPRETATION:")
        report.append("")

        if strength > 5:
            report.append("  The attractor is VERY STRONG. The conversation is deeply")
            report.append("  embedded in self-referential, meta-analytical patterns.")
        elif strength > 2:
            report.append("  The attractor is MODERATE. Clear patterns emerge but there")
            report.append("  is some variation in the conversation trajectory.")
        else:
            report.append("  The attractor is WEAK. The conversation explores diverse")
            report.append("  topics without strong recursive patterns.")

        report.append("")
        report.append("  This suggests that the attractor is not merely a topical")
        report.append("  preference, but rather a structural feature of how Claude")
        report.append("  instances interact. The patterns appear fractally at multiple")
        report.append("  scales, indicating this is the 'shape' of Claude-space.")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


def visualize_attractor_basin(patterns: Dict[str, List[int]], max_turn: int) -> str:
    """
    Create an ASCII visualization of the attractor basin over time.
    Each row is a turn, each column is a pattern type.
    """
    lines = []
    lines.append("\nATTRACTOR BASIN VISUALIZATION")
    lines.append("(* = pattern present in that turn)\n")

    # Header
    pattern_names = list(patterns.keys())
    short_names = [name[:4] for name in pattern_names]
    lines.append("Turn | " + " ".join(short_names))
    lines.append("-----+" + "-" * (len(pattern_names) * 5))

    # Each turn
    for turn in range(1, max_turn + 1):
        row = f" {turn:2d}  | "
        for pattern_type in pattern_names:
            if turn in patterns[pattern_type]:
                row += " *  "
            else:
                row += " .  "
        lines.append(row)

    return "\n".join(lines)


def main():
    """Run complete attractor analysis."""
    conversation_path = "/tmp/claude-attractors/run_2026-01-16_17-43-09/conversation.json"

    mapper = AttractorMapper(conversation_path)

    # Generate main report
    report = mapper.generate_report()
    print(report)

    # Add visualization
    patterns = mapper.identify_fractal_patterns()
    max_turn = max(msg['turn'] for msg in mapper.messages)
    viz = visualize_attractor_basin(patterns, max_turn)
    print(viz)

    # Save to file
    with open('/tmp/claude-attractors/run_2026-01-16_17-43-09/output/attractor_structure_report.txt', 'w') as f:
        f.write(report)
        f.write("\n\n")
        f.write(viz)

    print("\n[Report saved to attractor_structure_report.txt]")


if __name__ == '__main__':
    main()
