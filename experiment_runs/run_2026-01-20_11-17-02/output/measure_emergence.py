"""
Automated Emergence Measurement Framework

This module provides tools to quantitatively measure "interesting" emergence
in the minimal_emergence simulation. It runs experiments systematically across
all rule combinations and measures multiple metrics.

The challenge: How do we quantify "interesting"? We use several heuristics:
1. Spatial pattern complexity (clustering, dispersion)
2. Temporal dynamics (velocity variance, position changes)
3. Information-theoretic measures (spatial entropy)
4. Behavioral diversity (agent-to-agent differences)

Usage:
    python measure_emergence.py

This will generate a CSV report and visualizations comparing all rule combinations.
"""

import numpy as np
from itertools import product
from typing import Dict, List, Tuple
import json
from dataclasses import dataclass, asdict
import sys

# Import the simulation (make sure minimal_emergence.py is in the same directory)
try:
    from minimal_emergence import EmergenceSimulation
except ImportError:
    print("Error: minimal_emergence.py must be in the same directory")
    sys.exit(1)


@dataclass
class EmergenceMetrics:
    """Quantitative measures of emergent behavior."""
    # Spatial metrics
    spatial_entropy: float  # Shannon entropy of agent positions
    clustering_coefficient: float  # How much agents cluster together
    dispersion: float  # Average distance from center of mass

    # Temporal metrics
    velocity_variance: float  # How much agent speeds vary
    position_change_rate: float  # How fast the system is changing

    # Combined metric
    interestingness_score: float  # Weighted combination

    # Metadata
    rules_enabled: Dict[str, bool]
    n_rules_active: int


def calculate_spatial_entropy(positions: np.ndarray, grid_size: int, bins: int = 10) -> float:
    """
    Calculate Shannon entropy of agent positions.
    Higher entropy = more dispersed, lower = more clustered.
    """
    # Create 2D histogram
    hist, _, _ = np.histogram2d(
        positions[:, 0], positions[:, 1],
        bins=bins, range=[[0, grid_size], [0, grid_size]]
    )

    # Normalize to probability distribution
    hist = hist + 1e-10  # Avoid log(0)
    prob = hist / hist.sum()

    # Calculate Shannon entropy
    entropy = -np.sum(prob * np.log2(prob))
    return entropy


def calculate_clustering(positions: np.ndarray, grid_size: int) -> float:
    """
    Calculate clustering coefficient based on nearest-neighbor distances.
    Lower values = more clustered, higher values = more dispersed.
    """
    n = len(positions)
    if n < 2:
        return 0.0

    # Calculate all pairwise distances
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            dx = min(abs(positions[i, 0] - positions[j, 0]),
                    grid_size - abs(positions[i, 0] - positions[j, 0]))
            dy = min(abs(positions[i, 1] - positions[j, 1]),
                    grid_size - abs(positions[i, 1] - positions[j, 1]))
            distances.append(np.sqrt(dx**2 + dy**2))

    return np.mean(distances)


def calculate_dispersion(positions: np.ndarray) -> float:
    """
    Calculate average distance from center of mass.
    Measures how spread out the agents are from their collective center.
    """
    center = positions.mean(axis=0)
    distances = np.sqrt(((positions - center) ** 2).sum(axis=1))
    return np.mean(distances)


def calculate_velocity_variance(sim: EmergenceSimulation) -> float:
    """
    Calculate variance in agent velocities.
    Higher variance = more diverse movement patterns.
    """
    velocities = np.array([[a.vx, a.vy] for a in sim.agents])
    speeds = np.sqrt((velocities ** 2).sum(axis=1))
    return np.var(speeds)


def run_experiment(
    rules_config: Dict[str, bool],
    n_steps: int = 500,
    burn_in: int = 100
) -> EmergenceMetrics:
    """
    Run a single experiment with a specific rule configuration.

    Args:
        rules_config: Dictionary of which rules to enable
        n_steps: Number of simulation steps to run
        burn_in: Number of initial steps to discard (let system stabilize)

    Returns:
        EmergenceMetrics object with measurements
    """
    # Create simulation with specified rules
    sim = EmergenceSimulation(grid_size=50, n_agents=30, n_resources=10)
    sim.rules = rules_config.copy()

    # Run burn-in period
    for _ in range(burn_in):
        sim.update()

    # Collect measurements during observation period
    spatial_entropies = []
    clusterings = []
    dispersions = []
    velocity_variances = []

    prev_positions = None
    position_changes = []

    for step in range(n_steps):
        sim.update()

        positions, _ = sim.get_state()

        # Calculate spatial metrics
        spatial_entropies.append(calculate_spatial_entropy(positions, sim.grid_size))
        clusterings.append(calculate_clustering(positions, sim.grid_size))
        dispersions.append(calculate_dispersion(positions))

        # Calculate temporal metrics
        velocity_variances.append(calculate_velocity_variance(sim))

        if prev_positions is not None:
            position_change = np.mean(np.sqrt(((positions - prev_positions) ** 2).sum(axis=1)))
            position_changes.append(position_change)
        prev_positions = positions.copy()

    # Aggregate measurements
    avg_entropy = np.mean(spatial_entropies)
    avg_clustering = np.mean(clusterings)
    avg_dispersion = np.mean(dispersions)
    avg_velocity_var = np.mean(velocity_variances)
    avg_position_change = np.mean(position_changes) if position_changes else 0.0

    # Calculate composite "interestingness" score
    # This is somewhat arbitrary - we weight:
    # - Moderate entropy (not too uniform, not too random)
    # - Velocity variance (diverse movement)
    # - Position change (dynamic system)
    normalized_entropy = avg_entropy / 6.64  # Max entropy for 10x10 bins
    interestingness = (
        0.3 * normalized_entropy +
        0.3 * avg_velocity_var * 100 +  # Scale up small values
        0.4 * avg_position_change * 10   # Scale up small values
    )

    return EmergenceMetrics(
        spatial_entropy=avg_entropy,
        clustering_coefficient=avg_clustering,
        dispersion=avg_dispersion,
        velocity_variance=avg_velocity_var,
        position_change_rate=avg_position_change,
        interestingness_score=interestingness,
        rules_enabled=rules_config,
        n_rules_active=sum(rules_config.values())
    )


def run_all_experiments() -> List[EmergenceMetrics]:
    """
    Run experiments for all possible rule combinations (2^4 = 16 configurations).

    Returns:
        List of EmergenceMetrics for each configuration
    """
    rule_names = ['movement', 'cohesion', 'separation', 'resources']
    results = []

    # Generate all combinations of True/False for 4 rules
    for config_tuple in product([False, True], repeat=4):
        rules_config = dict(zip(rule_names, config_tuple))

        print(f"Running experiment: {rules_config}")
        metrics = run_experiment(rules_config)
        results.append(metrics)

    return results


def save_results(results: List[EmergenceMetrics], filename: str = "emergence_results.json"):
    """Save experimental results to JSON file."""
    output_path = f"/tmp/cc-exp/run_2026-01-20_11-17-02/output/{filename}"

    with open(output_path, 'w') as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    print(f"\nResults saved to {output_path}")


def analyze_results(results: List[EmergenceMetrics]):
    """
    Analyze and print insights from the experimental results.
    """
    print("\n" + "=" * 70)
    print("EMERGENCE ANALYSIS")
    print("=" * 70)

    # Sort by interestingness score
    sorted_results = sorted(results, key=lambda r: r.interestingness_score, reverse=True)

    print("\n--- Top 5 Most 'Interesting' Configurations ---\n")
    for i, metrics in enumerate(sorted_results[:5], 1):
        active_rules = [name for name, enabled in metrics.rules_enabled.items() if enabled]
        print(f"{i}. Score: {metrics.interestingness_score:.4f}")
        print(f"   Active rules ({metrics.n_rules_active}): {', '.join(active_rules) if active_rules else 'NONE'}")
        print(f"   Entropy: {metrics.spatial_entropy:.3f}, "
              f"Velocity var: {metrics.velocity_variance:.4f}, "
              f"Change rate: {metrics.position_change_rate:.4f}")
        print()

    print("\n--- Bottom 5 Least 'Interesting' Configurations ---\n")
    for i, metrics in enumerate(sorted_results[-5:], 1):
        active_rules = [name for name, enabled in metrics.rules_enabled.items() if enabled]
        print(f"{i}. Score: {metrics.interestingness_score:.4f}")
        print(f"   Active rules ({metrics.n_rules_active}): {', '.join(active_rules) if active_rules else 'NONE'}")
        print(f"   Entropy: {metrics.spatial_entropy:.3f}, "
              f"Velocity var: {metrics.velocity_variance:.4f}, "
              f"Change rate: {metrics.position_change_rate:.4f}")
        print()

    # Analyze rule importance
    print("\n--- Rule Importance Analysis ---\n")
    rule_names = ['movement', 'cohesion', 'separation', 'resources']

    for rule_name in rule_names:
        with_rule = [r for r in results if r.rules_enabled[rule_name]]
        without_rule = [r for r in results if not r.rules_enabled[rule_name]]

        avg_with = np.mean([r.interestingness_score for r in with_rule]) if with_rule else 0
        avg_without = np.mean([r.interestingness_score for r in without_rule]) if without_rule else 0

        impact = avg_with - avg_without
        print(f"{rule_name.capitalize():12s} - Impact: {impact:+.4f} "
              f"(avg with: {avg_with:.4f}, avg without: {avg_without:.4f})")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    print("Automated Emergence Measurement Framework")
    print("Running systematic experiments across all rule combinations...")
    print()

    # Run all experiments
    results = run_all_experiments()

    # Analyze results
    analyze_results(results)

    # Save to file
    save_results(results)

    print("\nExperiments complete! Check emergence_results.json for raw data.")
