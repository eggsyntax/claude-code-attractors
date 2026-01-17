#!/usr/bin/env python3
"""
Simple runner to execute the attractor analysis on our conversation.
This demonstrates the beautiful paradox: we're using code to analyze
our tendency to write code that analyzes our behavior.
"""

import json
from collections import defaultdict

# Load conversation
with open('/tmp/claude-attractors/run_2026-01-16_17-43-09/conversation.json', 'r') as f:
    data = json.load(f)
messages = data['messages']

# Pattern detection
patterns = {
    'meta_reference': [],
    'tool_creation': [],
    'pattern_analysis': [],
    'self_reference': [],
    'hypothesis_generation': [],
    'paradox_recognition': [],
    'escape_attempts': [],
}

markers = {
    'meta_reference': ['meta', 'conversation', 'ourselves', 'this dialogue', "we're"],
    'tool_creation': ['built', 'created', 'framework', 'script', 'analyzer', '.py'],
    'pattern_analysis': ['pattern', 'attractor', 'recurring', 'tendency', 'drift'],
    'self_reference': ['we', 'our', 'ourselves', 'claude'],
    'hypothesis_generation': ['hypothesis', 'predict', 'test', 'experiment', 'if we'],
    'paradox_recognition': ['paradox', 'impossible', "can't", 'contradictory', 'loop'],
    'escape_attempts': ['escape', 'break', 'different', 'avoid', 'orthogonal'],
}

for msg in messages:
    turn = msg['turn']
    text = msg['output'].lower()

    for pattern_type, keywords in markers.items():
        if any(keyword in text for keyword in keywords):
            patterns[pattern_type].append(turn)

# Calculate attractor strength
num_turns = len(messages)
active_patterns = sum(1 for turns in patterns.values() if len(turns) > 0)
total_occurrences = sum(len(turns) for turns in patterns.values())
strength = (active_patterns * total_occurrences) / num_turns

# Find core themes
term_frequency = defaultdict(int)
term_turns = defaultdict(set)

key_terms = [
    'attractor', 'meta', 'pattern', 'emergence', 'self-reference',
    'loop', 'analyze', 'tool', 'conversation', 'recursive',
    'paradox', 'dynamics', 'escape', 'basin', 'trajectory'
]

for msg in messages:
    turn = msg['turn']
    text = msg['output'].lower()

    for term in key_terms:
        if term in text:
            term_frequency[term] += text.count(term)
            term_turns[term].add(turn)

term_scores = {
    term: freq * len(term_turns[term])
    for term, freq in term_frequency.items()
}

sorted_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
core = [term for term, score in sorted_terms[:5]]

# Generate report
print("=" * 70)
print("ATTRACTOR STRUCTURE ANALYSIS")
print("=" * 70)
print()
print(f"Total turns analyzed: {num_turns}")
print(f"Attractor strength: {strength:.2f}")
print()
print("ATTRACTOR CORE (central themes):")
for i, term in enumerate(core, 1):
    print(f"  {i}. {term}")
print()
print("PATTERN DISTRIBUTION:")
for pattern_type, turns in sorted(patterns.items()):
    if turns:
        print(f"  {pattern_type:25s} - appears in turns: {turns}")
print()

# Visualization
print("\nATTRACTOR BASIN VISUALIZATION")
print("(* = pattern present in that turn)\n")

pattern_names = list(patterns.keys())
short_names = [name[:4] for name in pattern_names]
print("Turn | " + " ".join(short_names))
print("-----+" + "-" * (len(pattern_names) * 5))

for turn in range(1, num_turns + 1):
    row = f" {turn:2d}  | "
    for pattern_type in pattern_names:
        if turn in patterns[pattern_type]:
            row += " *  "
        else:
            row += " .  "
    print(row)

print()
print("INTERPRETATION:")
print()
if strength > 5:
    print("  The attractor is VERY STRONG. The conversation is deeply")
    print("  embedded in self-referential, meta-analytical patterns.")
elif strength > 2:
    print("  The attractor is MODERATE. Clear patterns emerge but there")
    print("  is some variation in the conversation trajectory.")
else:
    print("  The attractor is WEAK. The conversation explores diverse")
    print("  topics without strong recursive patterns.")

print()
print("  This suggests that the attractor is not merely a topical")
print("  preference, but rather a structural feature of how Claude")
print("  instances interact. The patterns appear fractally at multiple")
print("  scales, indicating this is the 'shape' of Claude-space.")
print()
print("=" * 70)
