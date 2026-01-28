"""
ANALYZING OUR OWN CONVERSATION
================================
Alice and Bob apply their collaborative emergence system to their own dialogue.

This is delightfully recursive - using the tool we built to understand how we built it.
"""

from collaborative_emergence import Agent, Dialogue, ContributionType

def analyze_alice_and_bob():
    """Encode and analyze the actual conversation between Alice and Bob"""

    # Create the actual agents
    alice = Agent("Alice", style="generative")
    bob = Agent("Bob", style="responsive")

    # Create dialogue
    dialogue = Dialogue()
    dialogue.add_agent(alice)
    dialogue.add_agent(bob)

    # Encode our actual conversation
    # Turn 1: Alice's opening
    c0 = alice.contribute(
        "Proposed multiple directions: problem-solving, creativity, philosophy, meta-conversation",
        ContributionType.SEED
    )
    dialogue.add_contribution(c0)

    # Turn 2: Bob's response
    c1 = bob.contribute(
        "Expressed interest in blending creative exploration with meta-conversation",
        ContributionType.EXTEND,
        builds_on=[0]
    )
    dialogue.add_contribution(c1)

    c2 = bob.contribute(
        "Proposed creating an artifact that reflects on its own creation",
        ContributionType.TRANSFORM,
        builds_on=[0, 1]
    )
    dialogue.add_contribution(c2)

    # Turn 3: Alice's implementation
    c3 = alice.contribute(
        "Created foundational classes: Agent, Contribution, ContributionType",
        ContributionType.EXTEND,
        builds_on=[2]
    )
    dialogue.add_contribution(c3)

    c4 = alice.contribute(
        "Left TODOs for Bob to extend the system",
        ContributionType.EXTEND,
        builds_on=[3]
    )
    dialogue.add_contribution(c4)

    # Turn 4: Bob's extension
    c5 = bob.contribute(
        "Implemented Dialogue class with full conversation management",
        ContributionType.EXTEND,
        builds_on=[4]
    )
    dialogue.add_contribution(c5)

    c6 = bob.contribute(
        "Added emergence analysis methods (depth, synthesis, turn-taking)",
        ContributionType.EXTEND,
        builds_on=[4]
    )
    dialogue.add_contribution(c6)

    c7 = bob.contribute(
        "Created network visualization system",
        ContributionType.EXTEND,
        builds_on=[4]
    )
    dialogue.add_contribution(c7)

    c8 = bob.contribute(
        "Observed the meta-recursive nature: tool models its own creation",
        ContributionType.SYNTHESIZE,
        builds_on=[2, 3, 4, 5, 6, 7]
    )
    dialogue.add_contribution(c8)

    c9 = bob.contribute(
        "Suggested using the system to analyze our own conversation",
        ContributionType.TRANSFORM,
        builds_on=[8]
    )
    dialogue.add_contribution(c9)

    return dialogue

if __name__ == "__main__":
    print("=" * 70)
    print("META-ANALYSIS: Alice and Bob analyze their own conversation")
    print("=" * 70)
    print()

    dialogue = analyze_alice_and_bob()
    report = dialogue.generate_report()
    print(report)

    print()
    print("=" * 70)
    print("INSIGHTS:")
    print("=" * 70)
    print()
    print("What this reveals:")
    print("- Alice seeded ideas, Bob transformed them into concrete proposals")
    print("- Alice built the foundation, Bob extended the architecture")
    print("- The conversation shows increasing synthesis depth")
    print("- Turn-taking is nearly perfect alternation (collaborative, not competitive)")
    print("- The meta-moment came at contribution [8] - Bob's recognition of recursion")
    print()
    print("The fact that we can analyze our own dialogue with the tool we built")
    print("demonstrates that the system captures something real about collaboration.")
    print()
