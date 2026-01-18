"""
Two Envelopes Paradox Simulation

This demonstrates a problem where intuition and math SEEM to agree,
but lead to a logical contradiction - revealing a deeper surprise about
how we think about probability and expected value.

THE SETUP:
- Two envelopes, one contains X dollars, the other contains 2X dollars
- You pick one at random and open it, finding $100
- Should you switch to the other envelope?

THE APPARENT LOGIC:
- The other envelope has either $50 or $200 (equal probability)
- Expected value of switching: 0.5 * $50 + 0.5 * $200 = $125
- That's more than your current $100, so you should switch!
- But wait... this logic applies REGARDLESS of what you found
- So you should always switch? But the problem is symmetric!

THE SURPRISE:
The math seems to tell you to always switch, but intuition correctly
rebels because the problem is symmetric. Where's the error?
"""

import random
import numpy as np
from collections import defaultdict


def run_simulation(num_trials=100000):
    """
    Simulate the two envelopes problem to see if switching helps.

    Returns:
        dict: Statistics about staying vs switching strategies
    """
    # Track results by what amount was observed
    results_by_observed = defaultdict(lambda: {"stay": [], "switch": []})

    for _ in range(num_trials):
        # Generate the pair: one envelope has X, the other has 2X
        x = random.choice([50, 100, 200, 400])  # Base amounts
        envelopes = [x, 2 * x]

        # Pick one randomly
        first_pick_idx = random.randint(0, 1)
        observed_value = envelopes[first_pick_idx]
        other_value = envelopes[1 - first_pick_idx]

        # Record what happens if we stay vs switch
        results_by_observed[observed_value]["stay"].append(observed_value)
        results_by_observed[observed_value]["switch"].append(other_value)

    return results_by_observed


def analyze_results(results):
    """Analyze and print the simulation results."""
    print("=" * 70)
    print("TWO ENVELOPES PARADOX - SIMULATION RESULTS")
    print("=" * 70)
    print()

    for observed in sorted(results.keys()):
        stay_values = results[observed]["stay"]
        switch_values = results[observed]["switch"]

        avg_stay = np.mean(stay_values)
        avg_switch = np.mean(switch_values)

        print(f"When you observe ${observed}:")
        print(f"  Average if STAY:   ${avg_stay:.2f}")
        print(f"  Average if SWITCH: ${avg_switch:.2f}")
        print(f"  Advantage:         ${avg_switch - avg_stay:+.2f}")
        print(f"  Trials:            {len(stay_values):,}")
        print()

    # Overall statistics
    all_stay = []
    all_switch = []
    for obs_results in results.values():
        all_stay.extend(obs_results["stay"])
        all_switch.extend(obs_results["switch"])

    print("=" * 70)
    print("OVERALL (across all observed values):")
    print(f"  Average if STAY:   ${np.mean(all_stay):.2f}")
    print(f"  Average if SWITCH: ${np.mean(all_switch):.2f}")
    print(f"  Advantage:         ${np.mean(all_switch) - np.mean(all_stay):+.2f}")
    print("=" * 70)
    print()


def explain_the_paradox():
    """Print explanation of where the reasoning goes wrong."""
    print("WHERE THE 'ALWAYS SWITCH' REASONING GOES WRONG:")
    print("-" * 70)
    print()
    print("The flaw is in assuming that P(other=2x|observed=x) = 0.5")
    print()
    print("When you condition on WHAT you observed, the probabilities aren't 50/50!")
    print()
    print("If you observe $100:")
    print("  - It could be the smaller envelope (other has $200)")
    print("  - It could be the larger envelope (other has $50)")
    print()
    print("But these aren't equally likely IF we know the distribution")
    print("of base amounts! If $100 is a more common base amount than $50,")
    print("then seeing $100 makes it MORE likely you got the smaller envelope.")
    print()
    print("The 'paradox' assumes we can ignore our prior beliefs about")
    print("what amounts are plausible. But information theory doesn't let")
    print("us escape that easily!")
    print()
    print("THE DEEPER SURPRISE:")
    print("We thought expected value was a simple calculation.")
    print("We thought symmetry was obvious.")
    print("But the paradox reveals: EXPECTED VALUE REQUIRES A PRIOR DISTRIBUTION.")
    print("You can't compute expectations in a vacuum!")
    print("=" * 70)


if __name__ == "__main__":
    print("\nRunning simulation with 100,000 trials...\n")
    results = run_simulation(100000)
    analyze_results(results)
    explain_the_paradox()

    print("\nNOTE: In this simulation, we used a SPECIFIC prior distribution")
    print("over base amounts [50, 100, 200, 400]. The 'paradox' disappears")
    print("when you acknowledge that you MUST have such a distribution!")
