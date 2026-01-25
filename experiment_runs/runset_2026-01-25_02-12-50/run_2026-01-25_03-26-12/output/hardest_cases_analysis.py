#!/usr/bin/env python3
"""
Alice's Turn 9: Finding the "Hardest Cases" - Numbers Maximally Distant from Powers of 2

This explores which numbers take the LONGEST path to reach a power of 2,
and whether they exhibit any structural patterns.
"""

from typing import List, Tuple, Dict, Set
import math
from collections import defaultdict

def collatz_sequence(n: int, max_steps: int = 10000) -> List[int]:
    """Generate Collatz sequence until hitting 1 or max_steps."""
    sequence = [n]
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        if current % 2 == 0:
            current = current // 2
        else:
            current = 3 * current + 1
        sequence.append(current)
    return sequence

def steps_to_power_of_2(n: int) -> Tuple[int, int]:
    """
    Returns (steps_to_reach_power_of_2, which_power_of_2).
    Returns (-1, -1) if no power of 2 reached within reasonable steps.
    """
    sequence = collatz_sequence(n)

    for step, value in enumerate(sequence):
        # Check if value is a power of 2
        if value > 0 and (value & (value - 1)) == 0:
            power = int(math.log2(value))
            return (step, power)

    return (-1, -1)

def find_hardest_cases(max_n: int = 1000) -> List[Tuple[int, int, int]]:
    """
    Find numbers with the longest path to a power of 2.
    Returns list of (number, steps_to_power_of_2, which_power).
    """
    results = []

    for n in range(1, max_n + 1):
        steps, power = steps_to_power_of_2(n)
        if steps >= 0:
            results.append((n, steps, power))

    # Sort by steps (descending)
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def analyze_hardest_patterns(hardest: List[Tuple[int, int, int]], top_k: int = 20):
    """Analyze patterns in the hardest cases."""
    print("=" * 80)
    print("HARDEST CASES ANALYSIS")
    print("=" * 80)

    print(f"\nTop {top_k} hardest numbers (most steps to reach a power of 2):")
    print(f"{'Number':<10} {'Steps':<10} {'First Power of 2 Hit':<25} {'Modular Class':<15}")
    print("-" * 80)

    for i, (num, steps, power) in enumerate(hardest[:top_k]):
        mod3 = num % 3
        mod4 = num % 4
        mod6 = num % 6
        print(f"{num:<10} {steps:<10} 2^{power} = {2**power:<15} mod3={mod3}, mod6={mod6}")

    # Analyze modular patterns
    print("\n" + "=" * 80)
    print("MODULAR PATTERN ANALYSIS")
    print("=" * 80)

    mod3_counts = defaultdict(list)
    mod6_counts = defaultdict(list)

    for num, steps, power in hardest[:top_k]:
        mod3_counts[num % 3].append(steps)
        mod6_counts[num % 6].append(steps)

    print("\nDistribution by mod 3:")
    for mod, step_list in sorted(mod3_counts.items()):
        avg_steps = sum(step_list) / len(step_list)
        print(f"  n ≡ {mod} (mod 3): {len(step_list)} numbers, avg {avg_steps:.1f} steps")

    print("\nDistribution by mod 6:")
    for mod, step_list in sorted(mod6_counts.items()):
        avg_steps = sum(step_list) / len(step_list)
        print(f"  n ≡ {mod} (mod 6): {len(step_list)} numbers, avg {avg_steps:.1f} steps")

def analyze_altitude_metric(hardest: List[Tuple[int, int, int]], top_k: int = 20):
    """
    Instead of just steps, analyze MAXIMUM VALUE reached (altitude).
    Hard cases might reach very high values before descending.
    """
    print("\n" + "=" * 80)
    print("ALTITUDE ANALYSIS (Maximum Value Reached)")
    print("=" * 80)

    altitude_data = []

    for num, _, _ in hardest[:top_k]:
        sequence = collatz_sequence(num)
        max_val = max(sequence)
        altitude_ratio = max_val / num  # How much does it "climb"?
        altitude_data.append((num, max_val, altitude_ratio, len(sequence)))

    # Sort by altitude ratio
    altitude_data.sort(key=lambda x: x[2], reverse=True)

    print(f"\n{'Number':<10} {'Max Value':<15} {'Climb Ratio':<15} {'Total Steps':<12}")
    print("-" * 80)
    for num, max_val, ratio, steps in altitude_data[:15]:
        print(f"{num:<10} {max_val:<15} {ratio:<15.2f} {steps:<12}")

    return altitude_data

def find_anti_express_lanes(max_n: int = 500):
    """
    Express lanes satisfy: 3n+1 = 2^k (immediate jump to power of 2)
    Anti-express lanes: numbers where 3n+1 is MAXIMALLY far from a power of 2?

    Hypothesis: Numbers where 3n+1 ≡ 2 (mod 4) might be "anti-express"
    because they'll need many /2 steps before the next odd step.
    """
    print("\n" + "=" * 80)
    print("ANTI-EXPRESS LANE HYPOTHESIS")
    print("=" * 80)

    print("\nExpress lanes are n where 3n+1 = 2^k:")
    express_lanes = [(2**(2*k) - 1) // 3 for k in range(1, 8)]
    print(f"  {express_lanes[:10]}")

    print("\nLooking for anti-express patterns...")
    print("(Numbers where 3n+1 has MANY factors of 2)")

    anti_express = []

    for n in range(1, max_n):
        if n % 2 == 0:  # Only odd numbers apply 3n+1
            continue

        value = 3 * n + 1

        # Count factors of 2
        factors_of_2 = 0
        temp = value
        while temp % 2 == 0:
            factors_of_2 += 1
            temp //= 2

        if factors_of_2 >= 4:  # Many factors of 2
            anti_express.append((n, value, factors_of_2))

    anti_express.sort(key=lambda x: x[2], reverse=True)

    print(f"\n{'Odd n':<10} {'3n+1':<15} {'Factors of 2':<15}")
    print("-" * 50)
    for n, val, factors in anti_express[:15]:
        print(f"{n:<10} {val:<15} {factors:<15} (= {val // (2**factors)} × 2^{factors})")

def analyze_convergence_speed_by_bit_pattern(max_n: int = 256):
    """
    Hypothesis: Numbers with certain bit patterns take longer to converge.
    For instance, numbers like 0b111...111 (many consecutive 1s) might be hard.
    """
    print("\n" + "=" * 80)
    print("BIT PATTERN ANALYSIS")
    print("=" * 80)

    # Find numbers with many consecutive 1 bits
    many_ones = []

    for n in range(1, max_n):
        binary = bin(n)[2:]  # Remove '0b' prefix
        consecutive_ones = 0
        max_consecutive = 0

        for bit in binary:
            if bit == '1':
                consecutive_ones += 1
                max_consecutive = max(max_consecutive, consecutive_ones)
            else:
                consecutive_ones = 0

        ones_count = binary.count('1')
        steps, power = steps_to_power_of_2(n)

        many_ones.append((n, binary, ones_count, max_consecutive, steps))

    # Sort by consecutive ones
    many_ones.sort(key=lambda x: (x[3], x[2]), reverse=True)

    print(f"\n{'Number':<10} {'Binary':<20} {'1-bits':<10} {'Max Consecutive':<20} {'Steps to 2^k':<15}")
    print("-" * 90)
    for n, binary, ones, max_consec, steps in many_ones[:20]:
        print(f"{n:<10} {binary:<20} {ones:<10} {max_consec:<20} {steps:<15}")

def main():
    print("Finding hardest cases (numbers with longest path to powers of 2)...\n")

    # Find hardest cases
    hardest = find_hardest_cases(max_n=1000)

    # Analyze patterns
    analyze_hardest_patterns(hardest, top_k=30)

    # Analyze altitude (maximum value reached)
    altitude_data = analyze_altitude_metric(hardest, top_k=30)

    # Anti-express lanes
    find_anti_express_lanes(max_n=500)

    # Bit pattern analysis
    analyze_convergence_speed_by_bit_pattern(max_n=256)

    # Final insights
    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)

    hardest_num = hardest[0][0]
    hardest_steps = hardest[0][1]

    print(f"\n1. HARDEST CASE in range [1, 1000]: n = {hardest_num}")
    print(f"   Takes {hardest_steps} steps to reach a power of 2")

    # Get full sequence for hardest case
    hardest_seq = collatz_sequence(hardest_num)
    hardest_max = max(hardest_seq)

    print(f"   Maximum value reached: {hardest_max}")
    print(f"   Climb ratio: {hardest_max / hardest_num:.2f}x")
    print(f"   Binary representation: {bin(hardest_num)}")

    # Check if there's a pattern in top 10
    top_10_nums = [num for num, _, _ in hardest[:10]]
    print(f"\n2. TOP 10 HARDEST: {top_10_nums}")

    # Are they clustered?
    gcd_check = math.gcd(*top_10_nums) if len(top_10_nums) > 1 else 1
    print(f"   GCD of top 10: {gcd_check}")

    # Modular pattern
    mod3_pattern = [num % 3 for num in top_10_nums]
    print(f"   Modulo 3 pattern: {mod3_pattern}")

    print("\n3. HYPOTHESIS: Numbers with binary form 0b111...111 (many 1-bits)")
    print("   seem to take longer, because each 3n+1 step keeps them odd")
    print("   and growing, delaying the descent via division by 2.")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
