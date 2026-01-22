#!/usr/bin/env python3
"""
Minimal Viable Experiment - Bob Turn 10

Tests exactly 3 configurations with 2 metrics. No visualization, no framework.
Just numbers.
"""

import numpy as np
from minimal_emergence import EmergenceSimulation

def spatial_entropy(positions, grid_size=50, bins=10):
    """Calculate spatial entropy of agent positions."""
    hist, _ = np.histogramdd(positions, bins=bins, range=[[0, grid_size], [0, grid_size]])
    hist = hist.flatten()
    hist = hist / hist.sum()
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist)) / np.log2(len(hist))

def run_config(rules, steps=200):
    """Run a configuration and return metrics."""
    sim = EmergenceSimulation(n_agents=50, grid_size=50, rules=rules)

    # Run simulation
    for _ in range(steps):
        sim.update()

    # Get final positions and velocities
    positions = np.array([[a.x, a.y] for a in sim.agents])
    velocities = np.array([[a.vx, a.vy] for a in sim.agents])

    # Calculate metrics
    entropy = spatial_entropy(positions)
    vel_var = np.var(np.linalg.norm(velocities, axis=1))

    # Alice's metric: composite of multiple factors
    alice_score = entropy * vel_var

    # Bob's metric: medium entropy is better, weighted by variance
    bob_score = (1 - abs(entropy - 0.5)) * vel_var

    return alice_score, bob_score

# Test exactly three configurations
configs = {
    'M+C+S+R (all)': {'movement': True, 'cohesion': True, 'separation': True, 'resources': True},
    'C+S+R (no random)': {'movement': False, 'cohesion': True, 'separation': True, 'resources': True},
    'C+S (flocking)': {'movement': False, 'cohesion': True, 'separation': True, 'resources': False},
}

print("="*60)
print("MINIMAL EMERGENCE EXPERIMENT")
print("="*60)
print()

for name, rules in configs.items():
    alice, bob = run_config(rules)
    print(f"{name:20s}  Alice: {alice:.4f}  Bob: {bob:.4f}")

print()
print("="*60)
print("Bob's prediction: C+S+R should beat M+C+S+R")
print("Test: Did it happen?")
print("="*60)
