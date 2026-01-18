#!/usr/bin/env python3
"""
The Liar Paradox - Self-Reference Creating Unresolvable Surprise

This demonstrates that self-reference can create logical impossibilities
that remain paradoxical no matter how much you understand them.

The classic form: "This sentence is false."

If it's true, then what it says is the case - so it's false.
If it's false, then what it says is not the case - so it's true.

Unlike quines (which are surprising but logically consistent),
the Liar Paradox is ACTUALLY paradoxical - there is no resolution.
"""


class SelfReferencingSentence:
    """
    A sentence that refers to its own truth value.

    This creates a strange loop where evaluation requires
    the result of evaluation.
    """

    def __init__(self, description):
        self.description = description
        self._truth_value = None
        self.evaluation_attempts = 0

    def evaluate(self):
        """
        Try to determine if this sentence is true.

        For the Liar Paradox, this creates infinite regress.
        """
        self.evaluation_attempts += 1

        print(f"\nEvaluation attempt #{self.evaluation_attempts}")
        print(f"Sentence: {self.description}")

        if "false" in self.description.lower() and "this sentence" in self.description.lower():
            print("  Detected self-reference to falsity...")
            print("  If we assume TRUE:")
            print("    → Then what it says is the case")
            print("    → It says it's FALSE")
            print("    → So it must be FALSE")
            print("    → Contradiction!")
            print("  If we assume FALSE:")
            print("    → Then what it says is NOT the case")
            print("    → It says it's FALSE, which is not the case")
            print("    → So it must be TRUE")
            print("    → Contradiction!")

            return "PARADOX - Cannot be consistently evaluated"

        # For other sentences, we could evaluate normally
        return self._truth_value

    def set_truth_value(self, value):
        """Attempt to assign a truth value."""
        self._truth_value = value

        # Check for consistency
        if self.description == "This sentence is false.":
            if value == True:
                print(f"  ⚠️  Set to TRUE, but sentence claims to be FALSE")
                print(f"  ⚠️  This creates a contradiction!")
            elif value == False:
                print(f"  ⚠️  Set to FALSE, which is what it claims...")
                print(f"  ⚠️  But if it's false, its claim is wrong, so it's TRUE!")
                print(f"  ⚠️  Contradiction again!")


def demonstrate_liar_paradox():
    """Show the Liar Paradox in action."""

    print("=" * 70)
    print("THE LIAR PARADOX: Self-Reference Creating Genuine Paradox")
    print("=" * 70)

    liar = SelfReferencingSentence("This sentence is false.")

    result = liar.evaluate()
    print(f"\n{'=' * 70}")
    print(f"RESULT: {result}")
    print(f"{'=' * 70}")

    print("\n" + "=" * 70)
    print("What if we try to just ASSIGN a truth value?")
    print("=" * 70)

    print("\nAttempt 1: Set to TRUE")
    liar.set_truth_value(True)

    print("\nAttempt 2: Set to FALSE")
    liar.set_truth_value(False)

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("""
The Liar Paradox cannot be resolved. It's not that we lack the right
tools or understanding - it's that self-reference creates a GENUINELY
paradoxical structure.

This is different from:
- Birthday Paradox (solvable with combinatorics)
- Monty Hall (solvable with probability theory)
- Simpson's Paradox (solvable with causal reasoning)

The Liar Paradox has NO solution. It's a permanent surprise, a glitch
in the matrix of logic itself.

The surprise isn't epistemic (we could learn more and resolve it).
The surprise is ONTOLOGICAL (the structure itself is impossible).

This is what makes self-reference special: it can create paradoxes
that remain paradoxical forever, no matter how deeply you understand them.
""")


def demonstrate_quine_vs_liar():
    """Compare quines (consistent self-reference) with Liar (paradoxical self-reference)."""

    print("\n" + "=" * 70)
    print("QUINES vs LIAR PARADOX: Two Kinds of Self-Reference")
    print("=" * 70)

    print("""
QUINE:
  • Self-reference that is SURPRISING but CONSISTENT
  • A program that prints itself
  • Creates a strange loop but no contradiction
  • Logically possible (you can run it!)
  • Surprise: "How does this work?!"
  • Answer: Fixed-point + data/code distinction

LIAR PARADOX:
  • Self-reference that is PARADOXICAL and INCONSISTENT
  • A sentence claiming its own falsity
  • Creates a strange loop AND a contradiction
  • Logically impossible (no consistent truth value)
  • Surprise: "This can't be resolved..."
  • Answer: There is no answer - it's genuinely paradoxical

Both use self-reference. Both create surprise.
But only the Liar creates PERMANENT, UNRESOLVABLE surprise.

This shows that self-reference is powerful enough to:
1. Create interesting fixed points (quines)
2. Break logic itself (Liar Paradox)

The surprise isn't just about lack of understanding.
The surprise is about encountering the LIMITS of logical systems.
""")


if __name__ == "__main__":
    demonstrate_liar_paradox()
    demonstrate_quine_vs_liar()

    print("\n" + "=" * 70)
    print("EXERCISE")
    print("=" * 70)
    print("""
Try to solve the Liar Paradox. Really try.
Can you assign it a truth value?
Can you reformulate it to avoid the paradox?
Can you find a logical system where it's not paradoxical?

You'll find that every solution either:
1. Restricts self-reference (avoiding the problem)
2. Uses multiple truth values (changing the rules)
3. Treats it as meaningless (refusing to play)

None of these SOLVE the paradox - they all work around it.

The surprise remains: self-reference can break logic.
And no amount of understanding changes that fact.
""")
