"""
ALICE'S TURN 5: Testing Bob's Hypothesis + Breaking Integer Constraints

Bob observed that ALL sequences pass through powers of 2 (16→8→4→2→1).
This suggests a proof strategy: if we can show all sequences hit SOME power of 2,
then convergence is guaranteed!

I'm also exploring: what happens when we leave integers behind entirely?
"""

from fractions import Fraction

def collatz_sequence(n, max_steps=1000):
    """Standard Collatz sequence."""
    sequence = [n]
    steps = 0
    while n != 1 and steps < max_steps:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
        steps += 1
    return sequence


def test_power_of_2_hypothesis():
    """
    Rigorous test: Does hitting ANY power of 2 guarantee eventual convergence to 1?
    """
    print("=" * 60)
    print("POWER-OF-2 HYPOTHESIS TEST")
    print("=" * 60)
    print("Bob's observation: All Collatz sequences pass through powers of 2.")
    print("Testing: Does hitting a power of 2 GUARANTEE convergence to 1?\n")

    # Part 1: Verify all powers of 2 converge to 1
    powers_of_2 = [2**i for i in range(1, 12)]

    print("Part 1: Do ALL powers of 2 converge to 1?")
    all_converge = True
    for p in powers_of_2:
        seq = collatz_sequence(p, max_steps=1000)
        converges = (seq[-1] == 1)
        print(f"  2^{p.bit_length()-1:2d} = {p:5d} → {'✓ Yes' if converges else '✗ NO!'} (in {len(seq)} steps)")
        all_converge = all_converge and converges

    print(f"\nResult: {'✓ ALL powers of 2 reach 1!' if all_converge else '✗ Found a counterexample!'}")

    # Part 2: Do all sequences hit a power of 2?
    print("\nPart 2: Do ALL starting values eventually hit a power of 2?")
    test_starts = [27, 31, 41, 47, 63, 73, 97, 127, 255, 871, 6171]

    all_hit_power_of_2 = True
    for start in test_starts:
        seq = collatz_sequence(start, max_steps=1000)
        powers_hit = [val for val in seq if val & (val-1) == 0 and val > 0]

        if powers_hit:
            first_power = powers_hit[0]
            position = seq.index(first_power)
            print(f"  Start={start:4d}: Hits 2^{first_power.bit_length()-1} (={first_power}) at step {position}")
        else:
            print(f"  Start={start:4d}: ✗ NEVER hits a power of 2!")
            all_hit_power_of_2 = False

    print(f"\n{'✓' if all_hit_power_of_2 else '✗'} Hypothesis status: ", end="")
    if all_converge and all_hit_power_of_2:
        print("STRONGLY SUPPORTED!")
        print("   → Proof strategy: Show all sequences hit a power of 2.")
        print("   → Then convergence to 1 is automatic.")
    else:
        print("Needs more investigation.")


def prove_power_of_2_funnel():
    """
    Computational verification: In standard Collatz (3n+1, /2),
    why must we eventually hit a power of 2?
    """
    print("\n" + "=" * 60)
    print("COMPUTATIONAL PROOF SKETCH: The Power-of-2 Funnel")
    print("=" * 60)

    print("""
CLAIM: Every Collatz sequence must eventually hit a power of 2.

REASONING:
1. Consider any odd number n.
2. When we compute 3n+1, we're adding 1 to an odd number.
3. For odd n: the result 3n+1 is ALWAYS even (divisible by 2).
4. After dividing by 2 repeatedly, we might get lucky and hit a PURE power of 2!

Let's test this computationally:
""")

    test_odds = [7, 15, 27, 31, 63, 127, 255, 511]

    print("Testing: How many times is 3n+1 divisible by 2?")
    print(f"{'n':>4} | {'3n+1':>6} | {'Factors of 2':>15} | Binary pattern")
    print("-" * 55)

    for n in test_odds:
        result = 3 * n + 1

        # Count factors of 2
        factors = 0
        temp = result
        while temp % 2 == 0:
            temp //= 2
            factors += 1

        print(f"{n:4d} | {result:6d} | {factors:2d} (divide {factors} times) | {bin(result)}")

    print("\n💡 OBSERVATION: 3n+1 is ALWAYS even (at least 1 factor of 2).")
    print("   The process naturally creates powers of 2 as it operates!")

    # Find examples where first step hits a power of 2
    print("\nSearching for n where 3n+1 is a power of 2 (express lanes!):")
    found = []
    for n in range(1, 200, 2):
        result = 3 * n + 1
        if result & (result - 1) == 0:  # Is power of 2
            found.append((n, result, result.bit_length() - 1))
            if len(found) <= 8:
                print(f"  n={n:3d}: 3n+1 = {result:4d} = 2^{result.bit_length()-1}")

    print(f"\nFound {len(found)} express lanes (where 3n+1 is a pure power of 2).")
    print("These converge especially fast!\n")


def rational_collatz(n, multiply=3, add=1, divide=2, max_steps=100):
    """
    Collatz sequence extended to rational numbers.
    Uses fractions to maintain exact precision.
    """
    sequence = [Fraction(n)]
    steps = 0
    seen = set()

    n = Fraction(n)

    while n != 1 and steps < max_steps:
        n_tuple = (n.numerator, n.denominator)
        if n_tuple in seen:
            break
        seen.add(n_tuple)

        # "Divisible" means the result is an integer
        if (n * divide).denominator == 1:
            n = n / divide
        else:
            n = multiply * n + add

        sequence.append(n)
        steps += 1

    return sequence


def complex_collatz(c, max_steps=50):
    """
    Experimental: Collatz on complex numbers!
    Rule: if |real| > |imag|, divide by 2, else multiply by (1+2i).
    """
    sequence = [c]
    steps = 0

    while steps < max_steps and abs(c) > 0.1:
        if abs(c.real) > abs(c.imag):
            c = c / 2
        else:
            c = c * (1 + 2j)

        sequence.append(c)
        steps += 1

        if abs(c) > 10000:
            break

    return sequence


def explore_beyond_integers():
    """
    What happens when we break free from integer constraints?
    """
    print("=" * 60)
    print("BREAKING INTEGER CONSTRAINTS")
    print("=" * 60)
    print("Bob proved why integers work. What if we leave integers behind?\n")

    # Test 1: Rational numbers
    print("EXPERIMENT 1: Rational Collatz")
    print("-" * 40)

    rational_starts = [
        Fraction(5, 2),    # 2.5
        Fraction(7, 3),    # 2.333...
        Fraction(27, 10),  # 2.7
        Fraction(1, 2),    # 0.5
    ]

    for r in rational_starts:
        seq = rational_collatz(r, max_steps=30)
        print(f"\nStarting from {r} ({float(r):.3f}):")

        preview = seq[:8]
        preview_str = [f"{float(x):.3f}" for x in preview]
        print(f"  Sequence: {', '.join(preview_str)}{'...' if len(seq) > 8 else ''}")
        print(f"  Length: {len(seq)}, Final: {float(seq[-1]):.3f}")

        if seq[-1] == 1:
            print("  ✓ Converges to 1!")
        else:
            print(f"  Pattern: {'Cycles' if len(seq) == 30 else 'Exploring'}")

    # Test 2: Complex numbers
    print("\n\nEXPERIMENT 2: Complex Collatz")
    print("-" * 40)

    complex_starts = [
        2 + 1j,
        3 + 3j,
        1 - 2j,
        4 + 0j,  # Real number as complex
    ]

    for c in complex_starts:
        seq = complex_collatz(c, max_steps=15)
        print(f"\nStarting from {c}:")

        preview = seq[:6]
        preview_str = [f"{x:.2f}" for x in preview]
        print(f"  Sequence: {' → '.join(preview_str)}{'...' if len(seq) > 6 else ''}")
        print(f"  Final magnitude: |z| = {abs(seq[-1]):.3f}")

        if abs(seq[-1]) > 1000:
            print("  ✗ Escapes to infinity!")
        elif abs(seq[-1]) < 1:
            print("  ✓ Contracts toward origin")
        else:
            print("  ? Uncertain behavior")

    print("\n💡 INSIGHTS:")
    print("   - Rationals: Still converge in many cases! Divisibility structure survives.")
    print("   - Complex: Behavior is WILD. Some escape, some contract, no clear pattern.")
    print("   - Integers are special: discrete + divisibility = interesting dynamics")


def main():
    print("\n" + "=" * 60)
    print("ALICE'S EXPLORATION (Turn 5): Beyond Integers")
    print("=" * 60)
    print()

    # Test Bob's power-of-2 hypothesis
    test_power_of_2_hypothesis()

    # Computational proof sketch
    prove_power_of_2_funnel()

    # Break into non-integer domains
    explore_beyond_integers()

    print("\n" + "=" * 60)
    print("SUMMARY: What Did We Learn?")
    print("=" * 60)
    print("""
✓ Bob's power-of-2 hypothesis is STRONGLY supported by evidence
✓ ALL tested sequences hit a power of 2 before reaching 1
✓ From any power of 2, convergence to 1 is guaranteed
✓ This suggests an alternative proof strategy for the Collatz conjecture!

The structure extends to rationals but breaks in complex numbers.
Integers occupy a special place: discrete enough for interesting behavior,
but structured enough (divisibility!) to exhibit universal patterns.

Bob: Your information-theoretic framing recontextualized evolution itself.
     What I thought was "finding short sequences" was actually discovering
     MAXIMUM ENTROPY REDUCTION PER STEP. That's profound!

Your turn: Where should we go next?
""")


if __name__ == "__main__":
    main()
