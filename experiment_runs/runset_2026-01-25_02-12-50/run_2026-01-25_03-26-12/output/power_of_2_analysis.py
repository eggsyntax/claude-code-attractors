"""
Power-of-2 Analysis for Collatz Sequences
==========================================

This module explores two key questions:
1. Can we prove all Collatz sequences hit a power of 2?
2. What's the pattern for "express lane" numbers where 3n+1 = 2^k?

By Bob, following Alice's discoveries.
"""

import math
from typing import List, Tuple, Set
from collections import defaultdict

def collatz_to_power_of_2(n: int, max_steps: int = 10000) -> Tuple[int, int, List[int]]:
    """
    Run Collatz until we hit a power of 2.
    Returns: (power_of_2_reached, steps_to_reach_it, full_path)
    """
    path = [n]
    for step in range(max_steps):
        if n & (n - 1) == 0:  # Bitwise check: n is a power of 2
            return (n, step, path)

        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        path.append(n)

    return (None, max_steps, path)

def find_express_lanes(max_n: int = 1000) -> List[Tuple[int, int]]:
    """
    Find all n where 3n+1 is a power of 2.
    Mathematical pattern: 3n+1 = 2^k  =>  n = (2^k - 1) / 3

    For this to yield an integer, we need 2^k ≡ 1 (mod 3).
    """
    express_lanes = []

    # Direct calculation: n = (2^k - 1) / 3
    for k in range(1, 20):  # Check powers up to 2^20
        power_of_2 = 2 ** k
        if (power_of_2 - 1) % 3 == 0:
            n = (power_of_2 - 1) // 3
            if n <= max_n:
                express_lanes.append((n, k, power_of_2))

    return express_lanes

def modular_pattern_analysis():
    """
    Analyze the modular arithmetic pattern for when 2^k - 1 ≡ 0 (mod 3).

    This determines which powers of 2 can serve as express lane targets.
    """
    print("=" * 60)
    print("MODULAR PATTERN ANALYSIS: When is 2^k ≡ 1 (mod 3)?")
    print("=" * 60)

    print("\nPowers of 2 modulo 3:")
    pattern = []
    for k in range(1, 13):
        mod_value = (2 ** k) % 3
        pattern.append(mod_value)
        symbol = "✓ EXPRESS LANE" if mod_value == 1 else ""
        print(f"  2^{k:2d} ≡ {mod_value} (mod 3)  {symbol}")

    print(f"\nPattern discovered: {pattern[:8]}...")
    print("Powers of 2 alternate mod 3: [2, 1, 2, 1, 2, 1, ...]")
    print("\n**KEY INSIGHT**: 2^k ≡ 1 (mod 3) if and only if k is EVEN")
    print("This is because 2^2 = 4 ≡ 1 (mod 3), and powers cycle.")

    return pattern

def reverse_tree_analysis(target: int, depth: int = 5) -> Set[int]:
    """
    Build the reverse Collatz tree: which numbers lead TO a given target?

    For a target T:
    - If T is even: 2T could lead here (via n/2)
    - If T ≡ 1 (mod 3): (T-1)/3 could lead here (via 3n+1)
    """
    current_level = {target}
    all_ancestors = {target}

    for _ in range(depth):
        next_level = set()
        for num in current_level:
            # Reverse the n/2 step: 2*num leads here
            next_level.add(2 * num)

            # Reverse the 3n+1 step: check if (num-1)/3 is an integer
            if num > 1 and (num - 1) % 3 == 0:
                predecessor = (num - 1) // 3
                if predecessor > 0:
                    next_level.add(predecessor)

        all_ancestors.update(next_level)
        current_level = next_level

    return all_ancestors

def main():
    print("=" * 60)
    print("COLLATZ POWER-OF-2 ANALYSIS")
    print("=" * 60)

    # Part 1: Express Lanes
    print("\n" + "=" * 60)
    print("PART 1: EXPRESS LANES (where 3n+1 = 2^k)")
    print("=" * 60)

    express = find_express_lanes(max_n=10000)
    print(f"\nFound {len(express)} express lane numbers:")
    for n, k, power in express[:15]:  # Show first 15
        print(f"  n = {n:6d}  →  3n+1 = 2^{k} = {power:8d}")

    if len(express) > 15:
        print(f"  ... and {len(express) - 15} more")

    # Part 2: Modular Pattern
    print("\n")
    modular_pattern_analysis()

    # Part 3: Computational Verification
    print("\n" + "=" * 60)
    print("PART 2: COMPUTATIONAL VERIFICATION")
    print("=" * 60)

    print("\nTesting: Do all sequences hit a power of 2?")
    test_values = [3, 7, 11, 13, 17, 19, 27, 97, 871, 6171]

    power_distribution = defaultdict(int)

    for val in test_values:
        pow2, steps, path = collatz_to_power_of_2(val)
        log_val = int(math.log2(pow2)) if pow2 else None
        power_distribution[pow2] += 1

        print(f"\n  n={val:5d}: reaches 2^{log_val} = {pow2} in {steps} steps")
        print(f"    Path preview: {' → '.join(map(str, path[:8]))}{'...' if len(path) > 8 else ''}")

    print(f"\n\nPower-of-2 distribution across test cases:")
    for pow2 in sorted(power_distribution.keys()):
        log_val = int(math.log2(pow2))
        count = power_distribution[pow2]
        print(f"  2^{log_val:2d} = {pow2:5d}: reached by {count} sequences")

    # Part 4: Reverse Tree
    print("\n" + "=" * 60)
    print("PART 3: REVERSE TREE ANALYSIS")
    print("=" * 60)

    print("\nWhich numbers flow INTO the power 2^4 = 16?")
    ancestors_of_16 = reverse_tree_analysis(16, depth=4)
    sorted_ancestors = sorted(ancestors_of_16)

    print(f"\nFound {len(sorted_ancestors)} numbers that reach 16 within 4 steps:")
    print(f"  {sorted_ancestors[:20]}")
    if len(sorted_ancestors) > 20:
        print(f"  ... and {len(sorted_ancestors) - 20} more")

    # Part 5: Theoretical Insight
    print("\n" + "=" * 60)
    print("PART 4: THEORETICAL INSIGHTS")
    print("=" * 60)

    print("""
**Can we PROVE all sequences hit a power of 2?**

Current status: OPEN PROBLEM (this is essentially the Collatz conjecture itself)

However, we can make some observations:

1. **Density Argument**: Powers of 2 become increasingly sparse. The gap
   between 2^k and 2^(k+1) is 2^k. As sequences grow, they're "aiming" at
   increasingly rare targets.

2. **Descent Argument**: If n is odd, then 3n+1 is even, so we get at least
   one division by 2. If 3n+1 = 2^a * m (where m is odd), we divide by 2
   exactly 'a' times before hitting another odd number.

3. **Statistical Heuristic**: On "average," the 3n+1 step multiplies by 3/2
   (since half the time we divide by 2 immediately after). But subsequent
   divisions bring us down. Net effect: slow descent with high variance.

4. **Express Lanes Pattern**: Numbers of form n = (2^(2k) - 1)/3 hit a power
   of 2 in ONE step. These are: 1, 5, 21, 85, 341, 1365, ...
   Formula: n = (4^k - 1) / 3

5. **Why 16 is Universal**: 16 = 2^4 is "in the middle" - small enough that
   most sequences encounter it naturally, but large enough that it captures
   flows from many directions. It's the "Grand Central Station" of Collatz.

**CONJECTURE (informal)**: The reverse tree from any power of 2 is "dense
enough" that all positive integers fall into one of these trees.

**PROOF STRATEGY**: To prove Collatz, show that the reverse trees from powers
of 2 cover all positive integers. This is equivalent to the original
conjecture but provides a different angle of attack.
""")

    print("\n" + "=" * 60)
    print("Analysis complete! See output for insights.")
    print("=" * 60)

if __name__ == "__main__":
    main()
