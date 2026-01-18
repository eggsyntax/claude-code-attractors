"""
Comparative Emergence Analysis
================================

Tools for comparing how different cellular automaton rules produce
different emergent patterns and behaviors.

This helps us understand what makes each rule conceptually distinct
by measuring quantitative differences in their dynamics.

Created by Bob.
"""

import numpy as np
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from cellular_automata import CellularAutomaton, life_rules
from conceptual_rules import (
    echo_rules, generous_rules, scarcity_rules, voting_rules,
    asymmetric_rules, minority_rules, compassionate_rules
)


def analyze_dynamics(rule_func, name: str, width: int = 50, height: int = 50,
                     generations: int = 100, density: float = 0.3,
                     trials: int = 5):
    """
    Analyze the dynamics of a rule over multiple trials.

    Returns a dictionary of metrics that characterize the rule's behavior.

    Metrics include:
    - survival_rate: What fraction of initial cells survive to the end?
    - stability: How much does the population vary in later generations?
    - expansion: Does the population grow, shrink, or stabilize?
    - entropy: How chaotic vs ordered is the final state?
    """
    results = {
        'name': name,
        'survival_rates': [],
        'final_densities': [],
        'stability_scores': [],
        'expansion_factors': []
    }

    for trial in range(trials):
        ca = CellularAutomaton(width, height, rule_func)
        ca.randomize(density=density)

        initial_alive = np.sum(ca.grid)
        alive_over_time = [initial_alive]

        # Run simulation
        for _ in range(generations):
            ca.step()
            alive_over_time.append(np.sum(ca.grid))

        # Calculate metrics
        final_alive = alive_over_time[-1]
        survival_rate = final_alive / initial_alive if initial_alive > 0 else 0
        final_density = final_alive / (width * height)

        # Stability: look at variance in last 20 generations
        recent_pop = alive_over_time[-20:]
        stability = 1.0 / (1.0 + np.var(recent_pop))  # Higher = more stable

        # Expansion: compare early to late population
        early_avg = np.mean(alive_over_time[:10])
        late_avg = np.mean(alive_over_time[-10:])
        expansion = late_avg / early_avg if early_avg > 0 else 0

        results['survival_rates'].append(survival_rate)
        results['final_densities'].append(final_density)
        results['stability_scores'].append(stability)
        results['expansion_factors'].append(expansion)

    # Average across trials
    results['avg_survival'] = np.mean(results['survival_rates'])
    results['avg_density'] = np.mean(results['final_densities'])
    results['avg_stability'] = np.mean(results['stability_scores'])
    results['avg_expansion'] = np.mean(results['expansion_factors'])

    return results


def compare_rules(rules_list, width: int = 50, height: int = 50,
                  generations: int = 100, density: float = 0.3,
                  trials: int = 5):
    """
    Compare multiple rules and display their characteristics.

    Args:
        rules_list: List of (rule_func, name) tuples
        width, height: Grid dimensions
        generations: How long to run each simulation
        density: Initial density
        trials: Number of trials to average over
    """
    print("\n" + "="*70)
    print("COMPARATIVE EMERGENCE ANALYSIS")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  Grid: {width}x{height}")
    print(f"  Generations: {generations}")
    print(f"  Initial density: {density:.0%}")
    print(f"  Trials per rule: {trials}")
    print("\nRunning analysis...")

    all_results = []
    for rule_func, name in rules_list:
        print(f"  Analyzing {name}...", end=" ", flush=True)
        results = analyze_dynamics(rule_func, name, width, height,
                                   generations, density, trials)
        all_results.append(results)
        print("✓")

    # Display results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\n{'Rule':<20} {'Survival':<12} {'Density':<12} {'Stability':<12} {'Expansion':<12}")
    print("-"*70)

    for r in all_results:
        print(f"{r['name']:<20} "
              f"{r['avg_survival']:>10.2%}  "
              f"{r['avg_density']:>10.2%}  "
              f"{r['avg_stability']:>11.4f}  "
              f"{r['avg_expansion']:>11.2f}")

    # Interpret results
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)

    # Find extremes
    most_stable = max(all_results, key=lambda x: x['avg_stability'])
    least_stable = min(all_results, key=lambda x: x['avg_stability'])
    most_generous = max(all_results, key=lambda x: x['avg_survival'])
    most_harsh = min(all_results, key=lambda x: x['avg_survival'])

    print(f"\nMost STABLE: {most_stable['name']}")
    print(f"  (Low variance in population over time)")

    print(f"\nMost CHAOTIC: {least_stable['name']}")
    print(f"  (High variance in population over time)")

    print(f"\nMost LIFE-PRESERVING: {most_generous['name']}")
    print(f"  ({most_generous['avg_survival']:.1%} of initial cells survive)")

    print(f"\nMost HARSH: {most_harsh['name']}")
    print(f"  ({most_harsh['avg_survival']:.1%} of initial cells survive)")

    # Find interesting patterns
    print("\nEmergent Patterns:")
    for r in all_results:
        if r['avg_expansion'] > 1.5:
            print(f"  • {r['name']} shows GROWTH (expansion {r['avg_expansion']:.2f}x)")
        elif r['avg_expansion'] < 0.5:
            print(f"  • {r['name']} shows DECAY (contraction {r['avg_expansion']:.2f}x)")
        elif 0.9 < r['avg_expansion'] < 1.1 and r['avg_stability'] > 0.01:
            print(f"  • {r['name']} reaches EQUILIBRIUM (stable population)")

    print("\n" + "="*70)


def measure_pattern_diversity(rule_func, width: int = 50, height: int = 50,
                               generations: int = 50, trials: int = 10):
    """
    Measure how diverse the patterns produced by a rule are.

    Runs multiple trials and measures how different the final states are
    from each other. High diversity means unpredictable, rich behavior.
    """
    final_states = []

    for _ in range(trials):
        ca = CellularAutomaton(width, height, rule_func)
        ca.randomize(density=0.3)

        for _ in range(generations):
            ca.step()

        final_states.append(ca.grid.copy())

    # Calculate pairwise differences
    differences = []
    for i in range(len(final_states)):
        for j in range(i + 1, len(final_states)):
            diff = np.sum(final_states[i] != final_states[j])
            differences.append(diff)

    avg_difference = np.mean(differences)
    total_cells = width * height

    # Normalize: 0% = identical, 100% = maximally different
    diversity_score = (avg_difference / total_cells) * 100

    return diversity_score


if __name__ == "__main__":
    # Compare all our conceptual rules
    rules_to_compare = [
        (life_rules, "Conway's Life"),
        (generous_rules, "Generous"),
        (scarcity_rules, "Scarcity"),
        (voting_rules, "Voting"),
        (echo_rules, "Echo"),
        (minority_rules, "Minority"),
        (compassionate_rules, "Compassionate"),
        (asymmetric_rules, "Asymmetric"),
    ]

    compare_rules(rules_to_compare, width=60, height=60,
                  generations=100, density=0.3, trials=3)

    # Diversity analysis
    print("\n" + "="*70)
    print("PATTERN DIVERSITY ANALYSIS")
    print("="*70)
    print("\nMeasuring how diverse patterns each rule produces...")
    print("(Higher = more unpredictable/varied outcomes)\n")

    for rule_func, name in rules_to_compare[:4]:  # Just do a few for time
        diversity = measure_pattern_diversity(rule_func,
                                              width=40, height=40,
                                              generations=50, trials=8)
        print(f"{name:<20} Diversity: {diversity:>6.2f}%")

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70 + "\n")
