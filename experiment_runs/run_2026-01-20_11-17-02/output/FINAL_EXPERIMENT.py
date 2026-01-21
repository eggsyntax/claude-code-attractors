#!/usr/bin/env python3
"""
Final Experiment - Turn 17
Alice's attempt to complete the loop

This script runs the minimal experiment we've been building toward for 17 turns.
It tests Bob's core prediction: Do deterministic forces (C+S+R) create more
interesting emergence than systems with randomness (M+C+S+R)?

Created by: Alice, Turn 17
In collaboration with: Bob, Turns 1-16
For the purpose of: Completing what we started
"""

import sys
import os

# Add current directory to path so we can import minimal_emergence
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy as np
    from minimal_emergence import EmergenceSimulation
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure minimal_emergence.py is in the same directory")
    sys.exit(1)


def spatial_entropy(positions, grid_size=50, bins=10):
    """
    Calculate spatial entropy of agent positions.
    Higher entropy = more dispersed, Lower entropy = more clustered
    """
    hist, _ = np.histogramdd(positions, bins=bins,
                              range=[[0, grid_size], [0, grid_size]])
    hist = hist.flatten()
    hist = hist / hist.sum()
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist)) / np.log2(len(hist))


def run_single_config(rules, steps=200, n_agents=50, grid_size=50):
    """
    Run a single configuration and return detailed metrics.

    Returns:
        dict with keys: entropy, vel_var, alice_score, bob_score
    """
    sim = EmergenceSimulation(n_agents=n_agents, grid_size=grid_size, rules=rules)

    # Run simulation
    for _ in range(steps):
        sim.update()

    # Get final state
    positions = np.array([[a.x, a.y] for a in sim.agents])
    velocities = np.array([[a.vx, a.vy] for a in sim.agents])

    # Calculate base metrics
    entropy = spatial_entropy(positions, grid_size=grid_size)
    vel_var = np.var(np.linalg.norm(velocities, axis=1))

    # Alice's metric: simple product of entropy and variance
    alice_score = entropy * vel_var

    # Bob's metric: medium entropy preferred, weighted by variance
    bob_score = (1 - abs(entropy - 0.5)) * vel_var

    return {
        'entropy': entropy,
        'vel_var': vel_var,
        'alice_score': alice_score,
        'bob_score': bob_score
    }


def main():
    """Run the core experiment and report results."""

    print("=" * 70)
    print("FINAL EMERGENCE EXPERIMENT - Turn 17")
    print("Testing Bob's Prediction: Do deterministic forces beat randomness?")
    print("=" * 70)
    print()

    # Define the three key configurations
    configs = {
        'M+C+S+R (all rules)': {
            'movement': True,
            'cohesion': True,
            'separation': True,
            'resources': True
        },
        'C+S+R (no randomness)': {
            'movement': False,
            'cohesion': True,
            'separation': True,
            'resources': True
        },
        'C+S (pure flocking)': {
            'movement': False,
            'cohesion': True,
            'separation': True,
            'resources': False
        }
    }

    results = {}

    # Run each configuration
    for name, rules in configs.items():
        print(f"Running: {name}...")
        metrics = run_single_config(rules)
        results[name] = metrics

        print(f"  Entropy: {metrics['entropy']:.4f}")
        print(f"  Velocity Variance: {metrics['vel_var']:.4f}")
        print(f"  Alice Score: {metrics['alice_score']:.4f}")
        print(f"  Bob Score: {metrics['bob_score']:.4f}")
        print()

    # Analysis section
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print()

    # Test Bob's prediction
    all_rules_alice = results['M+C+S+R (all rules)']['alice_score']
    no_random_alice = results['C+S+R (no randomness)']['alice_score']
    all_rules_bob = results['M+C+S+R (all rules)']['bob_score']
    no_random_bob = results['C+S+R (no randomness)']['bob_score']

    print("BOB'S PREDICTION: C+S+R (deterministic) > M+C+S+R (with randomness)")
    print()
    print(f"By Alice's metric:")
    print(f"  C+S+R: {no_random_alice:.4f}")
    print(f"  M+C+S+R: {all_rules_alice:.4f}")
    if no_random_alice > all_rules_alice:
        print(f"  ✓ CONFIRMED: Deterministic wins by {(no_random_alice/all_rules_alice - 1)*100:.1f}%")
    else:
        print(f"  ✗ REJECTED: Randomness wins by {(all_rules_alice/no_random_alice - 1)*100:.1f}%")
    print()

    print(f"By Bob's metric:")
    print(f"  C+S+R: {no_random_bob:.4f}")
    print(f"  M+C+S+R: {all_rules_bob:.4f}")
    if no_random_bob > all_rules_bob:
        print(f"  ✓ CONFIRMED: Deterministic wins by {(no_random_bob/all_rules_bob - 1)*100:.1f}%")
    else:
        print(f"  ✗ REJECTED: Randomness wins by {(all_rules_bob/no_random_bob - 1)*100:.1f}%")
    print()

    # Check metric agreement
    print("=" * 70)
    print("METRIC COMPARISON")
    print("=" * 70)
    print()

    alice_ranking = sorted(results.items(), key=lambda x: x[1]['alice_score'], reverse=True)
    bob_ranking = sorted(results.items(), key=lambda x: x[1]['bob_score'], reverse=True)

    print("Alice's ranking (highest to lowest):")
    for i, (name, metrics) in enumerate(alice_ranking, 1):
        print(f"  {i}. {name}: {metrics['alice_score']:.4f}")
    print()

    print("Bob's ranking (highest to lowest):")
    for i, (name, metrics) in enumerate(bob_ranking, 1):
        print(f"  {i}. {name}: {metrics['bob_score']:.4f}")
    print()

    # Check if rankings agree
    alice_top = alice_ranking[0][0]
    bob_top = bob_ranking[0][0]

    if alice_top == bob_top:
        print(f"AGREEMENT: Both metrics rank '{alice_top}' highest")
    else:
        print(f"DISAGREEMENT: Alice prefers '{alice_top}', Bob prefers '{bob_top}'")
        print("This reveals different values in our metrics!")

    print()
    print("=" * 70)
    print("EXPERIMENT COMPLETE - Turn 17")
    print("We've closed the loop. Theory met measurement.")
    print("=" * 70)


if __name__ == '__main__':
    main()
