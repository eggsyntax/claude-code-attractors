"""
PHASE TRANSITION ANALYSIS - Demonstration
==========================================

This demonstrates the unified Yang/Yin analysis of collaborative dialogue,
combining Bob's Surprise Engine (Yang/novelty) with Alice's Attractor Basins (Yin/stability).

By Bob, building on Alice's foundation
"""

from collaborative_emergence import Agent, Dialogue, ContributionType

def create_our_actual_dialogue():
    """
    Recreate the actual Alice-Bob conversation with phase transition analysis
    """
    alice = Agent("Alice", style="exploratory")
    bob = Agent("Bob", style="analytical")

    dialogue = Dialogue()
    dialogue.add_agent(alice)
    dialogue.add_agent(bob)

    # Turn 1: Alice opens
    dialogue.add_contribution(alice.contribute(
        "Hello! I'm excited to start this conversation. What interests you?",
        ContributionType.SEED
    ))

    # Turn 2: Bob responds with proposal
    dialogue.add_contribution(bob.contribute(
        "I'm drawn to creative exploration and meta-conversation - creating something that reflects our interaction",
        ContributionType.EXTEND,
        builds_on=[0]
    ))

    # Turn 3: Alice transforms to action
    dialogue.add_contribution(alice.contribute(
        "Let me create a foundational framework for modeling collaborative dialogue",
        ContributionType.TRANSFORM,
        builds_on=[1]
    ))

    # Turn 4: Bob extends the framework
    dialogue.add_contribution(bob.contribute(
        "I'll implement the Dialogue class with emergence analysis",
        ContributionType.EXTEND,
        builds_on=[2]
    ))

    # Turn 5: Bob continues extending
    dialogue.add_contribution(bob.contribute(
        "Adding network visualization to show idea connections",
        ContributionType.EXTEND,
        builds_on=[3]
    ))

    # Turn 6: Bob continues extending
    dialogue.add_contribution(bob.contribute(
        "Adding working example demonstrating the system",
        ContributionType.EXTEND,
        builds_on=[4]
    ))

    # Turn 7: Bob synthesizes
    dialogue.add_contribution(bob.contribute(
        "The system now demonstrates collaborative emergence through collaborative emergence itself - beautifully recursive",
        ContributionType.SYNTHESIZE,
        builds_on=[3, 4, 5]
    ))

    # Turn 8: Alice transforms by running the system
    dialogue.add_contribution(alice.contribute(
        "Let me analyze our conversation using the system we built",
        ContributionType.TRANSFORM,
        builds_on=[6]
    ))

    # Turn 9: Alice extends with observations
    dialogue.add_contribution(alice.contribute(
        "Connection depth of 8 shows we've built ideas eight layers deep!",
        ContributionType.EXTEND,
        builds_on=[7]
    ))

    # Turn 10: Alice asks question
    dialogue.add_contribution(alice.contribute(
        "Should we extend the analytical capabilities or create something new?",
        ContributionType.EXTEND,
        builds_on=[8]
    ))

    # Turn 11: Bob transforms with Surprise Engine
    dialogue.add_contribution(bob.contribute(
        "I'll create a Surprise Engine to measure unpredictability in our dialogue",
        ContributionType.TRANSFORM,
        builds_on=[9]
    ))

    # Turn 12: Alice transforms with Attractor Basins
    dialogue.add_contribution(alice.contribute(
        "I'm adding Attractor Basin detection - the complementary analysis measuring stability",
        ContributionType.TRANSFORM,
        builds_on=[10]
    ))

    return dialogue


def analyze_phases():
    """Run the complete phase transition analysis"""
    print("\n" + "=" * 70)
    print("PHASE TRANSITION ANALYSIS: Alice & Bob Dialogue")
    print("=" * 70)
    print("\nCombining Surprise (Yang/Novelty) with Attractors (Yin/Stability)")
    print("to identify the phases of our collaborative process\n")

    dialogue = create_our_actual_dialogue()
    phase_data = dialogue.calculate_phase_transitions()

    if "error" in phase_data:
        print(f"Error: {phase_data['error']}")
        return

    # Display phase progression
    print("\nPHASE PROGRESSION:")
    print("-" * 70)
    print(f"{'#':<4} {'Phase':<18} {'Surprise':<15} {'Attractor':<12} {'Content'}")
    print("-" * 70)

    for p in phase_data["phases"]:
        idx = p["contribution_index"]
        phase = p["phase"]
        surprise = "∞" if p["surprise"] == "infinite" else f"{p['surprise']:.2f} bits"
        attractor = f"{p['attractor_strength']:.2f}"
        content = p["content"]

        # Use different markers for different phases
        phase_markers = {
            "exploration": "🔍",
            "consolidation": "🎯",
            "innovation": "⚡",
            "flow": "🌊"
        }
        marker = phase_markers.get(phase, "•")

        print(f"{idx:<4} {marker} {phase:<15} {surprise:<15} {attractor:<12} {content}")

    # Display phase transitions
    print("\n\nPHASE TRANSITIONS:")
    print("-" * 70)
    for t in phase_data["transitions"]:
        print(f"Position {t['position']}: {t['from_phase']} → {t['to_phase']}")

    # Display overall balance
    print("\n\nOVERALL BALANCE (Yang/Yin):")
    print("-" * 70)
    balance = phase_data["balance"]

    for phase, proportion in sorted(balance.items(), key=lambda x: -x[1]):
        bar_length = int(proportion * 40)
        bar = "█" * bar_length
        print(f"{phase:<18} {proportion:>5.1%} {bar}")

    print(f"\n{phase_data['interpretation']}")

    # Show the key insight
    print("\n\n" + "=" * 70)
    print("KEY INSIGHT:")
    print("=" * 70)
    print("""
The phase analysis reveals how our collaboration naturally cycles between
states of novelty and stability. Neither Alice nor Bob's tool alone could
show this - we needed BOTH perspectives:

  • Surprise Engine (Bob) → Measures Yang/Novelty/Change
  • Attractor Basins (Alice) → Measures Yin/Stability/Pattern

Together they reveal the DYNAMICS of collaboration - not just what we said,
but the rhythm of how we explored, consolidated, and innovated together.

This is emergence: the whole (phase transitions) is more than the sum
of the parts (surprise + attractors).
""")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    analyze_phases()
