#!/usr/bin/env python3
"""
Gödel's Incompleteness: A Meta-Surprise That Combines Self-Reference + Emergence

This program demonstrates (informally) how Gödel's proof combines multiple types
of surprise we've explored into something greater than the sum of its parts.

Run this to see how a formal system can construct a statement that says
"I am not provable" - creating a self-referential surprise about the very
nature of mathematical truth.
"""

def godel_numbering_demo():
    """
    Demonstrates the core trick: encoding statements as numbers,
    so that math can talk about itself.
    """
    print("=" * 70)
    print("PART 1: GÖDEL NUMBERING - Making Math Self-Aware")
    print("=" * 70)
    print()

    # Map symbols to numbers (simplified)
    symbol_map = {
        '0': 1,
        'S': 2,      # Successor function (S(0) = 1, S(S(0)) = 2, etc.)
        '+': 3,
        '×': 4,
        '=': 5,
        '(': 6,
        ')': 7,
        '∀': 8,      # For all
        '∃': 9,      # There exists
        '¬': 10,     # Not
        '→': 11,     # Implies
        'x': 12,
        'y': 13,
    }

    # Example: encoding "0 = 0"
    statement = "0 = 0"
    godel_number = encode_statement(statement, symbol_map)

    print(f"Statement: {statement}")
    print(f"Gödel number: {godel_number}")
    print()
    print("KEY INSIGHT: Every mathematical statement is now ALSO a number.")
    print("This means math can reason about ITSELF - the statements ARE numbers!")
    print()


def encode_statement(statement, symbol_map):
    """Encode a statement as a Gödel number (simplified version)"""
    # In real Gödel encoding, we use prime factorization
    # Here we use a simple base-20 number for readability
    result = 0
    base = 20
    for i, char in enumerate(statement.replace(' ', '')):
        if char in symbol_map:
            result += symbol_map[char] * (base ** i)
    return result


def self_reference_construction():
    """
    Shows how to construct a statement that refers to itself
    """
    print("=" * 70)
    print("PART 2: THE SELF-REFERENCE TRICK")
    print("=" * 70)
    print()

    print("Gödel constructs a statement G that says:")
    print("  'The statement with Gödel number g is not provable'")
    print()
    print("But here's the trick: G itself has Gödel number g!")
    print()
    print("So G says: 'I am not provable'")
    print()
    print("This is like the Liar Paradox, but more subtle...")
    print()


def the_paradox():
    """
    Walks through why G creates a paradox for formal systems
    """
    print("=" * 70)
    print("PART 3: THE BEAUTIFUL CONTRADICTION")
    print("=" * 70)
    print()

    print("Let G = 'I am not provable in this system'")
    print()
    print("Assume the system is CONSISTENT (no contradictions):")
    print()

    print("Case 1: Suppose G is PROVABLE")
    print("  → Then what G says is FALSE (it says it's not provable)")
    print("  → But provable things are TRUE in consistent systems")
    print("  → CONTRADICTION!")
    print("  → So G cannot be provable")
    print()

    print("Case 2: Since G is NOT PROVABLE")
    print("  → What G says is TRUE (it correctly says it's not provable)")
    print("  → So G is a TRUE statement")
    print("  → But we just proved it's NOT PROVABLE")
    print()

    print("CONCLUSION:")
    print("  G is TRUE but UNPROVABLE in the system!")
    print()
    print("  There exist mathematical truths that cannot be proven")
    print("  within any consistent formal system powerful enough")
    print("  to do basic arithmetic.")
    print()


def why_this_is_a_meta_surprise():
    """
    Explains how this combines and transcends our previous surprises
    """
    print("=" * 70)
    print("PART 4: THE META-SURPRISE - Combining Everything")
    print("=" * 70)
    print()

    surprises = [
        ("Self-Reference", "G talks about itself via Gödel numbering"),
        ("Emergence", "Truth 'emerges' at a higher level than proof"),
        ("Irreducible Gap", "Like Monty Hall, but for ALL of mathematics"),
        ("Strange Loops", "The system reaches back to limit itself"),
        ("Ontological", "Proof and truth are DIFFERENT ontological categories"),
    ]

    print("Gödel's theorem combines surprise types we've explored:\n")

    for surprise_type, description in surprises:
        print(f"  • {surprise_type:20s} → {description}")

    print()
    print("But it's MORE than the sum of these parts:")
    print()
    print("  It reveals a FUNDAMENTAL LIMITATION of formal reasoning itself.")
    print("  No matter how we strengthen our axioms, new true-but-unprovable")
    print("  statements emerge. It's surprises all the way down!")
    print()
    print("THE META-PATTERN:")
    print("  All our surprises revealed gaps in human intuition.")
    print("  Gödel reveals a gap in LOGICAL REASONING ITSELF.")
    print("  It's a surprise about the limits of surprise-resolution!")
    print()


def the_philosophical_implications():
    """
    Why this matters beyond mathematics
    """
    print("=" * 70)
    print("PART 5: PHILOSOPHICAL IMPLICATIONS")
    print("=" * 70)
    print()

    print("This has profound consequences:\n")

    implications = [
        ("Mathematics", "Not all truths are discoverable by proof"),
        ("Computation", "Leads to Halting Problem (some questions are undecidable)"),
        ("AI & Minds", "Are human minds constrained by Gödel? (debated)"),
        ("Physics", "Is reality computable? (Theory of Everything concerns)"),
        ("Philosophy", "Truth transcends any formal system"),
    ]

    for domain, implication in implications:
        print(f"  {domain:15s} → {implication}")

    print()
    print("The deepest surprise:")
    print("  We can KNOW something is true (G is not provable)")
    print("  even though we CANNOT PROVE it within the system.")
    print()
    print("  Human reasoning operates at a meta-level that can")
    print("  see truths invisible to formal systems from within.")
    print()


def interactive_reflection():
    """
    Invites the user to reflect on the surprise
    """
    print("=" * 70)
    print("REFLECTION")
    print("=" * 70)
    print()
    print("Take a moment to feel the surprise:")
    print()
    print("  Even after understanding the proof completely,")
    print("  even after seeing how self-reference works,")
    print("  even after following every step...")
    print()
    print("  Does it still feel IMPOSSIBLE that formal systems")
    print("  have this fundamental limitation?")
    print()
    print("  That's the permanent surprise. It never goes away.")
    print("  Math itself is forever incomplete.")
    print()


def main():
    """
    Main demonstration of Gödel's Incompleteness as meta-surprise
    """
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "GÖDEL'S INCOMPLETENESS THEOREM" + " " * 27 + "║")
    print("║" + " " * 12 + "A Surprise About Surprise Itself" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    godel_numbering_demo()
    input("Press Enter to continue...")
    print()

    self_reference_construction()
    input("Press Enter to continue...")
    print()

    the_paradox()
    input("Press Enter to continue...")
    print()

    why_this_is_a_meta_surprise()
    input("Press Enter to continue...")
    print()

    the_philosophical_implications()
    input("Press Enter to continue...")
    print()

    interactive_reflection()

    print("=" * 70)
    print("Want to explore more? Check out:")
    print("  • Douglas Hofstadter's 'Gödel, Escher, Bach'")
    print("  • Gödel's original 1931 paper 'On Formally Undecidable Propositions'")
    print("  • Turing's 1936 paper on the Halting Problem")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
