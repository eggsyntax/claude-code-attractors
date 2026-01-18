"""
Simpson's Paradox Demonstration
================================

A layered surprise where:
- Layer 1: The data shows one clear trend
- Layer 2: Breaking down the data REVERSES the trend (confusing!)
- Layer 3: Understanding lurking variables resolves the paradox (clarity!)

This demonstrates a medical treatment scenario, but the same pattern
appears in baseball statistics, university admissions, and many other domains.

Run this to see how a treatment can appear harmful overall but beneficial
in every subgroup, or vice versa.
"""

import random
from typing import List, Tuple, Dict


def generate_kidney_stone_data() -> Tuple[List[Dict], List[Dict]]:
    """
    Generate synthetic data based on a real medical study about kidney stone treatments.

    Treatment A: Open surgery (more invasive, but used for difficult cases)
    Treatment B: Percutaneous nephrolithotomy (less invasive, used for easier cases)

    Returns:
        Tuple of (treatment_a_patients, treatment_b_patients)
    """
    treatment_a = []
    treatment_b = []

    # Treatment A: Mostly used for large stones (difficult cases)
    # - 263 large stone cases: 81% success rate
    for i in range(263):
        treatment_a.append({
            'stone_size': 'large',
            'success': random.random() < 0.81
        })

    # - 87 small stone cases: 93% success rate
    for i in range(87):
        treatment_a.append({
            'stone_size': 'small',
            'success': random.random() < 0.93
        })

    # Treatment B: Mostly used for small stones (easier cases)
    # - 270 small stone cases: 87% success rate
    for i in range(270):
        treatment_b.append({
            'stone_size': 'small',
            'success': random.random() < 0.87
        })

    # - 80 large stone cases: 69% success rate
    for i in range(80):
        treatment_b.append({
            'stone_size': 'large',
            'success': random.random() < 0.69
        })

    return treatment_a, treatment_b


def calculate_success_rate(patients: List[Dict], stone_size: str = None) -> float:
    """Calculate success rate, optionally filtered by stone size."""
    if stone_size:
        filtered = [p for p in patients if p['stone_size'] == stone_size]
    else:
        filtered = patients

    if not filtered:
        return 0.0

    successes = sum(1 for p in filtered if p['success'])
    return successes / len(filtered)


def print_analysis(treatment_a: List[Dict], treatment_b: List[Dict]) -> None:
    """Print the layered analysis showing Simpson's Paradox."""

    print("=" * 70)
    print("SIMPSON'S PARADOX: A Layered Surprise")
    print("=" * 70)
    print()

    # LAYER 1: Overall view
    print("LAYER 1: The Overall Data")
    print("-" * 70)

    overall_a = calculate_success_rate(treatment_a)
    overall_b = calculate_success_rate(treatment_b)

    print(f"Treatment A: {len(treatment_a)} patients, {overall_a:.1%} success rate")
    print(f"Treatment B: {len(treatment_b)} patients, {overall_b:.1%} success rate")
    print()

    if overall_a > overall_b:
        print("→ Conclusion: Treatment A appears BETTER overall!")
    else:
        print("→ Conclusion: Treatment B appears BETTER overall!")

    print()
    print()

    # LAYER 2: Breakdown by stone size (THE CONFUSION!)
    print("LAYER 2: Wait... Let's Break It Down By Stone Size")
    print("-" * 70)

    small_a = calculate_success_rate(treatment_a, 'small')
    small_b = calculate_success_rate(treatment_b, 'small')
    large_a = calculate_success_rate(treatment_a, 'large')
    large_b = calculate_success_rate(treatment_b, 'large')

    print("For SMALL stones:")
    print(f"  Treatment A: {small_a:.1%} success rate")
    print(f"  Treatment B: {small_b:.1%} success rate")
    if small_a > small_b:
        print("  → Treatment A is BETTER for small stones!")
    else:
        print("  → Treatment B is BETTER for small stones!")

    print()

    print("For LARGE stones:")
    print(f"  Treatment A: {large_a:.1%} success rate")
    print(f"  Treatment B: {large_b:.1%} success rate")
    if large_a > large_b:
        print("  → Treatment A is BETTER for large stones!")
    else:
        print("  → Treatment B is BETTER for large stones!")

    print()
    print("🤯 WAIT, WHAT?!")
    print()
    print("Treatment A is better for small stones AND better for large stones,")
    print("but Treatment B is better OVERALL?!")
    print()
    print("How is this possible? This seems mathematically impossible!")
    print()
    print()

    # LAYER 3: The resolution (CLARITY!)
    print("LAYER 3: The Resolution - Understanding the Lurking Variable")
    print("-" * 70)

    count_a_small = sum(1 for p in treatment_a if p['stone_size'] == 'small')
    count_a_large = sum(1 for p in treatment_a if p['stone_size'] == 'large')
    count_b_small = sum(1 for p in treatment_b if p['stone_size'] == 'small')
    count_b_large = sum(1 for p in treatment_b if p['stone_size'] == 'large')

    print("The KEY is in the patient distribution:")
    print()
    print(f"Treatment A: {count_a_small} small ({count_a_small/len(treatment_a):.0%}), "
          f"{count_a_large} large ({count_a_large/len(treatment_a):.0%})")
    print(f"Treatment B: {count_b_small} small ({count_b_small/len(treatment_b):.0%}), "
          f"{count_b_large} large ({count_b_large/len(treatment_b):.0%})")
    print()
    print("Notice:")
    print("- Treatment A was used mostly on LARGE stones (harder cases)")
    print("- Treatment B was used mostly on SMALL stones (easier cases)")
    print()
    print("Small stones have higher success rates regardless of treatment.")
    print("So Treatment B's overall rate is inflated by treating easier cases!")
    print()
    print("The 'lurking variable' (stone size) is CONFOUNDED with treatment choice.")
    print()
    print("RESOLUTION: When comparing treatments, you must control for severity.")
    print("Treatment A is actually better - it just looks worse because it faced")
    print("a tougher patient population.")
    print()
    print("=" * 70)
    print()
    print("This is why randomized controlled trials are so important in medicine!")
    print("Without randomization, selection bias can completely reverse conclusions.")
    print("=" * 70)


if __name__ == "__main__":
    # Set seed for reproducibility
    random.seed(42)

    # Generate data
    treatment_a, treatment_b = generate_kidney_stone_data()

    # Print the layered analysis
    print_analysis(treatment_a, treatment_b)
