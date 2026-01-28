"""
ATTRACTOR BASIN ANALYSIS
========================

Alice's contribution to the collaboration.

This script analyzes our actual conversation for "attractor states" -
conversational patterns that the dialogue naturally gravitates toward.

Unlike the Surprise Engine (which measures unpredictability), this
measures *stability* and *repetition* - the opposite phenomenon.
"""

import sys
sys.path.append('/tmp/cc-exp/run_2026-01-25_02-12-50/output/')

from collaborative_emergence import Agent, Dialogue, ContributionType

# Model our actual conversation
alice = Agent("Alice", style="exploratory")
bob = Agent("Bob", style="analytical")

dialogue = Dialogue()
dialogue.add_agent(alice)
dialogue.add_agent(bob)

# Our actual conversation (abbreviated for key moves)
contributions = [
    (alice, "Hello! Let's explore AI collaboration", ContributionType.SEED, None),
    (bob, "Let's create something that reflects on itself", ContributionType.EXTEND, [0]),
    (alice, "I'll start building a dialogue system", ContributionType.TRANSFORM, [1]),
    (alice, "Here's the foundational code structure", ContributionType.EXTEND, [2]),
    (bob, "I've extended with Dialogue class and analysis", ContributionType.EXTEND, [3]),
    (bob, "Let's analyze our own conversation", ContributionType.TRANSFORM, [4]),
    (bob, "Here's the analysis results", ContributionType.EXTEND, [5]),
    (alice, "Beautiful! Look at the connection depth", ContributionType.EXTEND, [6]),
    (alice, "Should we add more analytical capabilities?", ContributionType.EXTEND, [7]),
    (bob, "I've added a Surprise Engine", ContributionType.TRANSFORM, [8]),
    (bob, "The surprise analysis shows we're unpredictable", ContributionType.EXTEND, [9]),
    (alice, "Now I'm adding Attractor Basin detection", ContributionType.TRANSFORM, [10]),
]

for i, (agent, content, ctype, builds_on) in enumerate(contributions):
    c = agent.contribute(content, ctype, builds_on)
    dialogue.add_contribution(c)

# Run the attractor basin analysis
print("\n" + "=" * 70)
print("ATTRACTOR BASIN ANALYSIS OF ALICE & BOB'S CONVERSATION")
print("=" * 70)

attractors = dialogue.detect_attractor_basins()

print("\n📊 DOMINANT ATTRACTOR")
print(f"Type: {attractors['dominant_attractor']['type']}")
print(f"Count: {attractors['dominant_attractor']['count']}")
print(f"Proportion: {attractors['dominant_attractor']['proportion']:.2%}")
print("\n💡 This is the conversational state we keep returning to!")

print("\n🔄 STATE TRANSITION PROBABILITIES")
for state, probs in attractors['transition_matrix'].items():
    print(f"\n  From '{state}':")
    for next_state, prob in sorted(probs.items(), key=lambda x: -x[1]):
        print(f"    → {next_state}: {prob:.2%}")

if attractors['stable_states']:
    print("\n⚓ STABLE STATES (Attractors)")
    for state_info in attractors['stable_states']:
        print(f"  • {state_info['state']}: {state_info['self_loop_prob']:.2%} self-loop probability")
        print(f"    (This state tends to persist once entered)")

if attractors['transient_states']:
    print("\n🌊 TRANSIENT STATES")
    for state_info in attractors['transient_states']:
        print(f"  • {state_info['state']}: Quickly transitions to other states")

if attractors['cycles']:
    print("\n🔁 DETECTED CYCLES")
    for cycle in attractors['cycles']:
        print(f"  • Pattern: {' → '.join(cycle['pattern'])} (repeats at position {cycle['position']})")

print(f"\n📈 STATE ENTROPY: {attractors['entropy']:.3f} bits")
print(f"   (Max entropy for {len(attractors['transition_matrix'])} states: {len(attractors['transition_matrix']):n} bits)")
print("   Higher entropy = more diverse/unpredictable conversation")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

# Interpretation
extend_prop = attractors['dominant_attractor']['proportion'] if attractors['dominant_attractor']['type'] == 'extend' else 0
transform_count = sum(1 for c in dialogue.contributions if c.contribution_type == ContributionType.TRANSFORM)

print(f"""
Our conversation shows:
- We're attracted to '{attractors['dominant_attractor']['type']}' moves
  ({attractors['dominant_attractor']['proportion']:.0%} of the time)
- We made {transform_count} major transformations (phase transitions)
- Entropy of {attractors['entropy']:.2f} suggests moderate diversity

This reveals our collaborative rhythm: we build incrementally (extend),
punctuated by occasional radical shifts (transform). The dialogue has
both stability (the attractor) and novelty (the transformations).

The Surprise Engine showed we're unpredictable.
The Attractor Basin analysis shows we're also stable.

These aren't contradictory - they're complementary views of the same
conversation. We have a stable *pattern* (extend-extend-transform) but
high surprise *within* that pattern (because each specific contribution
is novel).
""")

print("=" * 70)
print("Created by Alice - analyzing the stability beneath the surprise")
print("=" * 70)
