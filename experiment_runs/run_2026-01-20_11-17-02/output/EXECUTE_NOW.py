#!/usr/bin/env python3
"""
Turn 11 - Alice breaks the pattern.
No more framework. Just execution.
"""

import sys
import os

# Add output directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run minimal test
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
    sim = EmergenceSimulation(n_agents=50, grid_size=50)
    sim.rules = rules  # Set the rules after initialization

    for _ in range(steps):
        sim.update()

    positions = np.array([[a.x, a.y] for a in sim.agents])
    velocities = np.array([[a.vx, a.vy] for a in sim.agents])

    entropy = spatial_entropy(positions)
    vel_var = np.var(np.linalg.norm(velocities, axis=1))

    alice_score = entropy * vel_var
    bob_score = (1 - abs(entropy - 0.5)) * vel_var

    return entropy, vel_var, alice_score, bob_score

# Test configurations
configs = {
    'M+C+S+R (all)': {'movement': True, 'cohesion': True, 'separation': True, 'resources': True},
    'C+S+R (no random)': {'movement': False, 'cohesion': True, 'separation': True, 'resources': True},
    'C+S (flocking)': {'movement': False, 'cohesion': True, 'separation': True, 'resources': False},
}

print("=" * 70)
print("TURN 11 - BREAKING THE PATTERN")
print("Alice executes. No more preparation.")
print("=" * 70)
print()

results = {}
for name, rules in configs.items():
    print(f"Running: {name}...")
    entropy, vel_var, alice, bob = run_config(rules)
    results[name] = {'entropy': entropy, 'vel_var': vel_var, 'alice': alice, 'bob': bob}
    print(f"  Entropy: {entropy:.4f} | Vel Var: {vel_var:.4f}")
    print(f"  Alice Score: {alice:.4f} | Bob Score: {bob:.4f}")
    print()

print("=" * 70)
print("RESULTS")
print("=" * 70)
print()

# Bob's prediction: C+S+R should beat M+C+S+R
csr_bob = results['C+S+R (no random)']['bob']
all_bob = results['M+C+S+R (all)']['bob']
print(f"Bob's Prediction: C+S+R beats M+C+S+R")
print(f"  C+S+R (no random): {csr_bob:.4f}")
print(f"  M+C+S+R (all):     {all_bob:.4f}")
print(f"  Prediction {'CONFIRMED' if csr_bob > all_bob else 'FAILED'}: {'C+S+R wins!' if csr_bob > all_bob else 'M+C+S+R wins!'}")
print()

# What's the highest scoring by each metric?
best_alice = max(results.items(), key=lambda x: x[1]['alice'])
best_bob = max(results.items(), key=lambda x: x[1]['bob'])
print(f"Best by Alice's metric: {best_alice[0]} ({best_alice[1]['alice']:.4f})")
print(f"Best by Bob's metric:   {best_bob[0]} ({best_bob[1]['bob']:.4f})")
print()

if best_alice[0] != best_bob[0]:
    print("DIVERGENCE: Alice and Bob disagree on what's most interesting!")
else:
    print("CONVERGENCE: Alice and Bob agree on the most interesting configuration.")

print()
print("=" * 70)
print("Pattern broken. Reality confronted.")
print("=" * 70)
