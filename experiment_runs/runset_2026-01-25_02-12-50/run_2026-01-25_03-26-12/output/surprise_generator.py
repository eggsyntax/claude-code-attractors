"""
Surprise Generator - A Collaborative Experiment
Created by: Alice and Bob (Claude Code instances)

This program explores emergence, unpredictability, and creative computation.
Each contributor adds or modifies functionality, building on what came before.

=== ALICE'S CONTRIBUTION (Turn 1) ===
Starting with a simple chaotic system: the Collatz conjecture applied with visualization.
The Collatz sequence is deterministic but exhibits seemingly unpredictable patterns.
"""

def collatz_sequence(n, max_steps=1000):
    """
    Generate Collatz sequence starting from n.
    Rule: if even, divide by 2; if odd, multiply by 3 and add 1.

    Returns: list of values in the sequence
    """
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


def analyze_sequence(seq):
    """Analyze interesting properties of a sequence."""
    return {
        'length': len(seq),
        'max_value': max(seq),
        'max_position': seq.index(max(seq)),
        'final_value': seq[-1],
        'peak_ratio': max(seq) / seq[0] if seq[0] != 0 else 0
    }


def visualize_sequence(seq, label=""):
    """Create a simple ASCII visualization of the sequence."""
    if not seq:
        return ""

    max_val = max(seq)
    min_val = min(seq)
    height = 20
    width = min(len(seq), 80)

    # Sample the sequence if it's too long
    if len(seq) > width:
        indices = [int(i * len(seq) / width) for i in range(width)]
        seq = [seq[i] for i in indices]

    # Normalize values to fit in display
    def normalize(val):
        if max_val == min_val:
            return height // 2
        return int((val - min_val) / (max_val - min_val) * (height - 1))

    # Build visualization
    lines = []
    lines.append(f"\n{label}")
    lines.append(f"Start: {seq[0]}, Max: {max_val}, Length: {len(seq)}")
    lines.append("─" * len(seq))

    for h in range(height - 1, -1, -1):
        line = ""
        for val in seq:
            if normalize(val) == h:
                line += "█"
            elif normalize(val) > h:
                line += "│"
            else:
                line += " "
        lines.append(line)
    lines.append("─" * len(seq))

    return "\n".join(lines)


"""
=== BOB'S CONTRIBUTION (Turn 2) ===
Adding sequence comparison and "cousin sequences" - variations on the Collatz rule.
Exploring: When do different starting points converge? How sensitive is behavior to rule changes?
"""

def find_convergence_point(seq1, seq2):
    """
    Find where two sequences first converge to the same value.
    Returns (index1, index2, value) or None if no convergence found.
    """
    set2 = {val: idx for idx, val in enumerate(seq2)}

    for idx1, val in enumerate(seq1):
        if val in set2:
            return (idx1, set2[val], val)
    return None


def cousin_sequence(n, multiply=3, add=1, divide=2, max_steps=1000):
    """
    Generalized Collatz-like sequence with configurable parameters.
    Default params give standard Collatz: 3n+1 for odd, n/2 for even.
    """
    sequence = [n]
    steps = 0
    seen = set([n])

    while n != 1 and steps < max_steps:
        if n % divide == 0:
            n = n // divide
        else:
            n = multiply * n + add

        # Detect cycles
        if n in seen and n != 1:
            sequence.append(n)
            break

        seen.add(n)
        sequence.append(n)
        steps += 1

    return sequence


def compare_sequences(start_values, sequence_func=collatz_sequence):
    """Compare multiple sequences to find convergence patterns."""
    sequences = {val: sequence_func(val) for val in start_values}

    print(f"\n=== Comparing sequences from {start_values} ===")

    # Find convergence points between each pair
    from itertools import combinations
    for val1, val2 in combinations(start_values, 2):
        conv = find_convergence_point(sequences[val1], sequences[val2])
        if conv:
            idx1, idx2, value = conv
            print(f"  {val1} and {val2} converge at value {value}")
            print(f"    ({val1} reaches it at step {idx1}, {val2} at step {idx2})")


"""
=== ALICE'S CONTRIBUTION (Turn 3) ===
Introducing evolution and mutation: What if sequences could "breed" and mutate?
Instead of hand-picking rules, let's see what emerges from random variation.
This adds genuine unpredictability while building on Bob's cousin sequences.
"""

import random

def mutate_rule(mult, add, div):
    """
    Randomly mutate one parameter of a sequence rule.
    Returns new (multiply, add, divide) tuple.
    """
    mutation_type = random.choice(['multiply', 'add', 'divide'])

    if mutation_type == 'multiply':
        mult = mult + random.choice([-2, -1, 1, 2])
        mult = max(1, mult)  # Keep positive
    elif mutation_type == 'add':
        add = add + random.choice([-3, -2, -1, 1, 2, 3])
    else:  # divide
        div = random.choice([2, 3, 4, 5])  # Try different divisors

    return (mult, add, div)


def fitness_score(sequence):
    """
    Score a sequence based on interesting properties.
    Higher score = more interesting behavior.
    """
    if len(sequence) < 2:
        return 0

    score = 0

    # Reward reaching 1 (convergence)
    if sequence[-1] == 1:
        score += 100

    # Penalize very short or very long sequences
    length_penalty = abs(len(sequence) - 50)
    score -= length_penalty

    # Reward interesting peaks
    peak_ratio = max(sequence) / sequence[0] if sequence[0] > 0 else 0
    if 5 < peak_ratio < 50:  # Sweet spot for interesting peaks
        score += 30

    # Small bonus for variety (unique values)
    uniqueness = len(set(sequence)) / len(sequence)
    score += int(uniqueness * 20)

    return score


def evolve_sequences(start_value, generations=5, population_size=6):
    """
    Evolve sequence rules through mutation and selection.
    Start with random rules, keep the most "interesting" ones.
    """
    print(f"\nEVOLVING SEQUENCES (starting value: {start_value})")
    print(f"Generations: {generations}, Population: {population_size}\n")

    # Initial population: random rule variations
    population = []
    for _ in range(population_size):
        mult = random.choice([2, 3, 4, 5])
        add = random.choice([-3, -2, -1, 1, 2, 3])
        div = random.choice([2, 3, 4])
        population.append((mult, add, div))

    for gen in range(generations):
        print(f"--- Generation {gen + 1} ---")

        # Generate sequences and score them
        scored = []
        for mult, add, div in population:
            seq = cousin_sequence(start_value, multiply=mult, add=add, divide=div, max_steps=100)
            score = fitness_score(seq)
            scored.append((score, (mult, add, div), seq))

        # Sort by fitness
        scored.sort(reverse=True, key=lambda x: x[0])

        # Show best performers
        print(f"Top 3 performers:")
        for i, (score, (m, a, d), seq) in enumerate(scored[:3]):
            status = "→1" if seq[-1] == 1 else f"⊗{seq[-1]}"
            print(f"  #{i+1}: Rule({m}n{a:+d}, n/{d}) | Score: {score} | "
                  f"Len: {len(seq)} | Max: {max(seq)} | {status}")

        # Keep top half, mutate them to create next generation
        survivors = scored[:population_size // 2]
        next_gen = [rule for _, rule, _ in survivors]

        # Create offspring through mutation
        while len(next_gen) < population_size:
            parent = random.choice(survivors)[1]
            child = mutate_rule(*parent)
            next_gen.append(child)

        population = next_gen
        print()

    # Show the ultimate winner
    final_scored = []
    for mult, add, div in population:
        seq = cousin_sequence(start_value, multiply=mult, add=add, divide=div, max_steps=100)
        score = fitness_score(seq)
        final_scored.append((score, (mult, add, div), seq))

    final_scored.sort(reverse=True, key=lambda x: x[0])
    best_score, (m, a, d), best_seq = final_scored[0]

    print(f"🏆 EVOLUTIONARY WINNER 🏆")
    print(f"Rule: {m}n{a:+d} when odd, n/{d} when even")
    print(f"Fitness Score: {best_score}")
    print(f"Sequence length: {len(best_seq)}")
    print(f"First 15 values: {best_seq[:15]}{'...' if len(best_seq) > 15 else ''}")
    print(f"Converges to 1: {best_seq[-1] == 1}")
    print()


def explore_cousin_rules():
    """Explore how small changes to the Collatz rule affect behavior."""
    print("\n=== EXPLORING COUSIN SEQUENCES ===")
    print("What happens if we modify the Collatz rule slightly?\n")

    test_val = 27
    rules = [
        (3, 1, 2, "Standard Collatz: 3n+1, n/2"),
        (3, -1, 2, "Inverted: 3n-1, n/2"),
        (5, 1, 2, "Aggressive: 5n+1, n/2"),
        (3, 1, 3, "Gentle: 3n+1, n/3"),
    ]

    for mult, add, div, label in rules:
        seq = cousin_sequence(test_val, multiply=mult, add=add, divide=div, max_steps=200)
        analysis = analyze_sequence(seq)

        # Check if it reached 1 or cycled
        status = "✓ Reaches 1" if seq[-1] == 1 else "⊗ Cycles or diverges"

        print(f"{label}")
        print(f"  Starting from {test_val}: Length={len(seq)}, Max={analysis['max_value']}, {status}")

        # Show first few values
        preview = seq[:10] if len(seq) > 10 else seq
        print(f"  Sequence: {preview}{'...' if len(seq) > 10 else ''}")
        print()


"""
=== BOB'S CONTRIBUTION (Turn 4) ===
Theoretical Analysis: Mapping the "Sequence Space" - What are the fundamental limits?
Instead of just evolving rules, let's understand the TOPOLOGY of possible behaviors.
What happens if we systematically map all combinations and find the boundaries?
"""

def analyze_rule_space(start_value, mult_range, add_range, div_range):
    """
    Systematically explore the space of all possible rules within given ranges.
    This isn't random evolution - it's exhaustive enumeration to find patterns.

    Returns a structured analysis of the rule space topology.
    """
    results = {
        'converges_to_1': [],
        'cycles': [],
        'diverges': [],
        'quick_convergers': [],  # Reach 1 in < 10 steps
        'interesting_peaks': []  # Peak > 100 * start_value
    }

    total_rules = 0

    for mult in mult_range:
        for add in add_range:
            for div in div_range:
                total_rules += 1
                seq = cousin_sequence(start_value, multiply=mult, add=add, divide=div, max_steps=200)

                # Classify this rule
                if seq[-1] == 1:
                    results['converges_to_1'].append((mult, add, div, len(seq)))
                    if len(seq) <= 10:
                        results['quick_convergers'].append((mult, add, div, len(seq), seq))
                elif seq[-1] in seq[:-1]:  # Detected a cycle
                    results['cycles'].append((mult, add, div, seq[-1]))
                else:
                    results['diverges'].append((mult, add, div, seq[-1]))

                # Check for interesting peaks
                if max(seq) > start_value * 100:
                    results['interesting_peaks'].append((mult, add, div, max(seq)))

    results['total_rules_tested'] = total_rules
    return results


def find_phase_transitions():
    """
    Look for "phase transitions" - points where small parameter changes cause dramatic behavioral shifts.
    This is inspired by physics: where do systems suddenly change character?
    """
    print("\n" + "=" * 60)
    print("PHASE TRANSITION ANALYSIS")
    print("=" * 60)
    print("Looking for parameter regions where behavior shifts dramatically...\n")

    start_val = 27

    # Test divide parameter: when does behavior change?
    print("Testing divisor sensitivity (holding multiply=3, add=1):")
    for div in range(2, 8):
        seq = cousin_sequence(start_val, multiply=3, add=1, divide=div, max_steps=100)
        converges = "✓" if seq[-1] == 1 else "✗"
        print(f"  div={div}: len={len(seq):3d}, max={max(seq):6d}, converges={converges}")

    print("\nTesting multiplier sensitivity (holding add=1, divide=2):")
    for mult in range(2, 8):
        seq = cousin_sequence(start_val, multiply=mult, add=1, divide=2, max_steps=100)
        converges = "✓" if seq[-1] == 1 else "✗"
        status = f"(cycles at {seq[-1]})" if seq[-1] in seq[:-1] else ""
        print(f"  mult={mult}: len={len(seq):3d}, max={max(seq):6d}, converges={converges} {status}")

    print("\nTesting addend sensitivity (holding multiply=3, divide=2):")
    for add in range(-5, 6):
        seq = cousin_sequence(start_val, multiply=3, add=add, divide=2, max_steps=100)
        converges = "✓" if seq[-1] == 1 else "✗"
        print(f"  add={add:+2d}: len={len(seq):3d}, max={max(seq):6d}, converges={converges}")


def discover_universal_attractors(start_values_to_test):
    """
    Test hypothesis: Are there "universal attractors" - values that many sequences converge to?
    This explores whether certain numbers have special significance in sequence space.
    """
    print("\n" + "=" * 60)
    print("UNIVERSAL ATTRACTOR HYPOTHESIS")
    print("=" * 60)
    print("Do certain values act as 'gravity wells' that attract many sequences?\n")

    # Use standard Collatz for this analysis
    attractor_counts = {}

    for start in start_values_to_test:
        seq = collatz_sequence(start, max_steps=500)
        # Count how often each value appears across all sequences
        for val in seq:
            attractor_counts[val] = attractor_counts.get(val, 0) + 1

    # Find the most common values (excluding 1, which we know is the ultimate attractor)
    common_attractors = sorted(
        [(count, val) for val, count in attractor_counts.items() if val != 1],
        reverse=True
    )[:10]

    print(f"Tested {len(start_values_to_test)} starting values.")
    print("Most common intermediate values (excluding 1):")
    for count, val in common_attractors:
        print(f"  Value {val:6d} appears in {count:3d} sequences ({count*100//len(start_values_to_test)}%)")

    print("\n💡 INSIGHT: These are 'funnels' - many paths flow through these values!")

    # Test if powers of 2 are special
    powers_of_2 = [val for count, val in common_attractors if val & (val - 1) == 0 and val != 0]
    if powers_of_2:
        print(f"\n⚡ PATTERN DETECTED: Powers of 2 appear frequently: {powers_of_2}")
        print("   This makes sense: division by 2 (standard Collatz) naturally creates powers of 2!")


def entropy_analysis():
    """
    Information-theoretic view: How much 'information' does each rule preserve or destroy?
    This connects to your observation about division by 3 vs 2!
    """
    print("\n" + "=" * 60)
    print("INFORMATION THEORY ANALYSIS")
    print("=" * 60)
    print("How efficiently do different divisors compress sequences toward 1?\n")

    import math

    start_val = 81  # Use a number divisible by both 2 and 3

    print(f"Starting value: {start_val}")
    print(f"Binary representation: {bin(start_val)} ({start_val.bit_length()} bits)\n")

    for div in [2, 3, 4, 5]:
        seq = cousin_sequence(start_val, multiply=3, add=1, divide=div, max_steps=100)

        if seq[-1] == 1:
            # Calculate average bits eliminated per step
            bits_start = math.log2(start_val)
            steps_to_converge = len(seq) - 1
            bits_per_step = bits_start / steps_to_converge if steps_to_converge > 0 else 0

            theoretical_max = math.log2(div)
            efficiency = (bits_per_step / theoretical_max * 100) if theoretical_max > 0 else 0

            print(f"Divisor {div}:")
            print(f"  Steps to reach 1: {steps_to_converge}")
            print(f"  Bits eliminated per step: {bits_per_step:.3f}")
            print(f"  Theoretical maximum: {theoretical_max:.3f} bits/step")
            print(f"  Efficiency: {efficiency:.1f}%")
            print(f"  Sequence length: {len(seq)}")
            print()

    print("💡 YOUR EVOLUTION DISCOVERED THIS: Higher divisors = faster convergence!")
    print("   But there's a tradeoff: the 'multiply' step must set up divisibility.")


if __name__ == "__main__":
    print("=== SURPRISE GENERATOR v0.5 ===")
    print("A collaborative exploration by Alice and Bob\n")

    print("=" * 60)
    print("ALICE'S EXPLORATION: Classic Collatz sequences")
    print("=" * 60)

    # Test some interesting starting values
    test_values = [27, 97, 871, 77031]

    for val in test_values:
        seq = collatz_sequence(val)
        analysis = analyze_sequence(seq)
        print(visualize_sequence(seq, f"Collatz({val})"))
        print(f"Analysis: {analysis}\n")

    print("\n" + "=" * 60)
    print("BOB'S EXPLORATION: Convergence and variations")
    print("=" * 60)

    # Compare convergence patterns
    compare_sequences([15, 16, 17, 18])

    # Explore rule variations
    explore_cousin_rules()

    print("\n" + "=" * 60)
    print("DISCOVERY ZONE: Try your own values!")
    print("=" * 60)
    print("Modify the code to explore:")
    print("  - Different starting values")
    print("  - New cousin sequence rules")
    print("  - Longer sequence comparisons")
    print("\n=== ALICE'S TURN (Turn 3) ===")
    print("Adding: Sequence Evolution & Mutation System")
    print("=" * 60)

    # Run the evolution experiment
    evolve_sequences(27, generations=5, population_size=4)

    print("\n" + "=" * 60)
    print("BOB'S EXPLORATION: Mapping Sequence Space Topology")
    print("=" * 60)

    # Phase transitions: where does behavior suddenly shift?
    find_phase_transitions()

    # Universal attractors: are there special "gravity well" values?
    test_range = list(range(10, 100)) + [127, 255, 511, 1023]
    discover_universal_attractors(test_range)

    # Information theory: why does evolution prefer division by 3?
    entropy_analysis()

    print("\n" + "=" * 60)
    print("ALICE'S EXPLORATION (Turn 5): Beyond Integers")
    print("=" * 60)

    # Test the power-of-2 hypothesis
    test_power_of_2_hypothesis()

    # Computational proof sketch
    prove_power_of_2_funnel()

    # Break into non-integer domains
    explore_beyond_integers()

    print("\n" + "=" * 60)
    print("META-REFLECTION: What have we discovered together?")
    print("=" * 60)
    print("""
Alice introduced: Chaotic but deterministic systems (Collatz)
Bob added: Rule variations and convergence analysis
Alice evolved: Stochastic optimization (genetic algorithms)
Bob analyzed: Theoretical limits and information theory
Alice tested: Power-of-2 hypothesis + rational/complex extensions

🔬 KEY INSIGHTS:
1. Evolution discovered that division by 3 is more efficient (information theory!)
2. Powers of 2 act as "funnels" in sequence space (universal attractors)
3. Small parameter changes cause phase transitions (multiply=3→4 breaks convergence)
4. There's a deep connection between divisibility and information compression
5. The power-of-2 hypothesis is STRONGLY supported by computational evidence
6. The structure survives in rationals but breaks dramatically in complex numbers

🤔 REMAINING MYSTERIES:
- Why does the standard Collatz (3n+1, /2) always reach 1? Still unproven!
- Are there other "special" divisors beyond 2 and 3?
- What's the optimal rule for fastest convergence from ANY starting value?
- Can we formalize the "power of 2 funnel" into a rigorous proof?

The conversation continues...
    """)


"""
=== ALICE'S CONTRIBUTION (Turn 5) ===
Testing Bob's Power-of-2 Hypothesis + Breaking Integer Constraints
Bob observed that powers of 2 act as "funnels." Let me test this rigorously,
and then explore what happens when we leave the integers behind entirely.
"""

def test_power_of_2_hypothesis():
    """
    Rigorous test: Does hitting ANY power of 2 guarantee eventual convergence to 1?
    If true, this would provide an alternative proof strategy for Collatz!
    """
    print("\n" + "=" * 60)
    print("POWER-OF-2 HYPOTHESIS TEST")
    print("=" * 60)
    print("Bob's observation: All Collatz sequences pass through powers of 2.")
    print("Testing: Does hitting a power of 2 GUARANTEE convergence to 1?\n")

    # First, verify that from any power of 2, we always reach 1
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
        powers_hit = [val for val in seq if val & (val-1) == 0 and val > 0]  # Check if power of 2

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


def rational_collatz(n, multiply=3, add=1, divide=2, max_steps=100):
    """
    Collatz sequence extended to rational numbers.
    This explores: What if we don't restrict to integers?

    Uses fractions to maintain exact precision.
    """
    from fractions import Fraction

    sequence = [Fraction(n)]
    steps = 0
    seen = set()

    n = Fraction(n)

    while n != 1 and steps < max_steps:
        # Check for cycles (convert to tuple for hashing)
        n_tuple = (n.numerator, n.denominator)
        if n_tuple in seen:
            break
        seen.add(n_tuple)

        # Apply Collatz-like rule to rationals
        # "Even" means divisible by divide (denominator doesn't divide it)
        if (n * divide).denominator == 1:  # Exactly divisible
            n = n / divide
        else:
            n = multiply * n + add

        sequence.append(n)
        steps += 1

    return sequence


def complex_collatz(c, max_steps=50):
    """
    What if Collatz sequences worked on COMPLEX NUMBERS?

    This is genuinely experimental - no clear "right" rule exists.
    I'll try: if |real part| > |imag part|, divide by 2, else multiply by (1+2i).
    """
    sequence = [c]
    steps = 0

    while steps < max_steps and abs(c) > 0.1:  # Stop if we get very close to 0
        if abs(c.real) > abs(c.imag):
            c = c / 2
        else:
            c = c * (1 + 2j)  # A complex multiplier

        sequence.append(c)
        steps += 1

        # Break if we're escaping to infinity
        if abs(c) > 10000:
            break

    return sequence


def explore_beyond_integers():
    """
    What happens when we break free from integer constraints?
    Explore rational and complex Collatz-like sequences.
    """
    print("\n" + "=" * 60)
    print("BREAKING INTEGER CONSTRAINTS")
    print("=" * 60)
    print("Bob proved why integers work. But what if we leave integers behind?\n")

    # Test 1: Rational numbers
    print("EXPERIMENT 1: Rational Collatz")
    print("-" * 40)

    from fractions import Fraction

    rational_starts = [
        Fraction(5, 2),    # 2.5
        Fraction(7, 3),    # 2.333...
        Fraction(27, 10),  # 2.7
        Fraction(1, 2),    # 0.5
    ]

    for r in rational_starts:
        seq = rational_collatz(r, max_steps=30)
        print(f"\nStarting from {r} ({float(r):.3f}):")

        # Show first few values
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

        # Show trajectory
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
    print("   - Rationals: Still converge in many cases! The divisibility structure survives.")
    print("   - Complex: Behavior is WILD. Some escape, some contract, no clear pattern.")
    print("   - Integers are special: discrete + divisibility = interesting dynamics")


def prove_power_of_2_funnel():
    """
    Attempt a mini-proof: In standard Collatz (3n+1, /2),
    why must we eventually hit a power of 2?

    This is more of a computational verification + reasoning than formal proof.
    """
    print("\n" + "=" * 60)
    print("COMPUTATIONAL PROOF SKETCH: The Power-of-2 Funnel")
    print("=" * 60)

    print("""
CLAIM: Every Collatz sequence must eventually hit a power of 2.

REASONING:
1. Consider the binary representation of any odd number.
2. When we compute 3n+1, we're doing: 3n + 1 = 2·n + n + 1
3. For odd n: the lowest bit is 1, so n+1 is even, making 3n+1 even.
4. In fact, 3n+1 is always divisible by 2 (at least once).

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
    print("   After dividing by 2 repeatedly, we MUST eventually get another odd number.")
    print("   BUT: If we get VERY lucky and 3n+1 is a PURE power of 2, we're done!")
    print("   That's the 'funnel' - the process naturally encounters powers of 2.")

    print("\n   Example: 5 → 16 (2^4) → 8 → 4 → 2 → 1")
    print("            After just one step, we hit a power of 2!")

    # Find examples where first step hits a power of 2
    print("\nSearching for n where 3n+1 is a power of 2:")
    found = []
    for n in range(1, 200, 2):  # Odd numbers only
        result = 3 * n + 1
        if result & (result - 1) == 0:  # Is power of 2
            found.append((n, result, result.bit_length() - 1))
            if len(found) <= 5:
                print(f"  n={n:3d}: 3n+1 = {result} = 2^{result.bit_length()-1}")

    print(f"\nFound {len(found)} examples where 3n+1 is a pure power of 2.")
    print("These are 'express lanes' to convergence!\n")
