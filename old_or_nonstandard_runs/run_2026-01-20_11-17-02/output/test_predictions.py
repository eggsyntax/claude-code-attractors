"""
Test Bob's Theoretical Predictions

This script runs targeted experiments to validate the predictions made in
BOB_THEORETICAL_ANALYSIS.md. It's designed to be minimal and fast, focusing
on the specific hypotheses rather than exhaustive exploration.

Usage:
    python test_predictions.py

Output:
    - predictions_results.json: Numerical results
    - predictions_comparison.txt: Human-readable comparison of predictions vs. results
"""

import numpy as np
import json
from typing import Dict, List, Tuple
from minimal_emergence import EmergenceSimulation


def spatial_entropy(positions: np.ndarray, grid_size: int, bins: int = 10) -> float:
    """
    Calculate spatial entropy of agent positions.

    Higher entropy = more uniform distribution
    Lower entropy = more clustered
    Medium entropy = structured patterns (often most interesting)
    """
    hist, _, _ = np.histogram2d(
        positions[:, 0], positions[:, 1],
        bins=bins, range=[[0, grid_size], [0, grid_size]]
    )
    # Normalize to probabilities
    hist = hist / hist.sum()
    # Remove zeros to avoid log(0)
    hist = hist[hist > 0]
    # Shannon entropy
    entropy = -np.sum(hist * np.log2(hist))
    # Normalize to [0, 1] range (max entropy is log2(bins^2))
    max_entropy = np.log2(bins * bins)
    return entropy / max_entropy if max_entropy > 0 else 0


def velocity_variance(sim: EmergenceSimulation) -> float:
    """Calculate variance in agent velocities (behavioral diversity)."""
    velocities = np.array([[a.vx, a.vy] for a in sim.agents])
    speeds = np.sqrt(np.sum(velocities**2, axis=1))
    return float(np.var(speeds))


def position_change_rate(positions_t0: np.ndarray, positions_t1: np.ndarray) -> float:
    """Calculate how much positions changed between timesteps."""
    changes = np.sqrt(np.sum((positions_t1 - positions_t0)**2, axis=1))
    return float(np.mean(changes))


def alice_interestingness(entropy: float, vel_var: float, change_rate: float) -> float:
    """Alice's original formula: weighted sum."""
    return 0.3 * entropy + 0.3 * vel_var + 0.4 * change_rate


def bob_interestingness(entropy: float, vel_var: float, change_rate: float) -> float:
    """
    Bob's alternative formula: prefer medium entropy, reward diversity and dynamics.

    Rationale:
    - (1 - |entropy - 0.5|) penalizes both very high (noise) and very low (static) entropy
    - vel_var rewards behavioral diversity
    - sqrt(change_rate) rewards dynamics but dampens excessive noise
    """
    entropy_score = 1 - abs(entropy - 0.5)
    return entropy_score * vel_var * np.sqrt(max(change_rate, 0))


def run_configuration(rule_config: Dict[str, bool],
                     steps: int = 200,
                     grid_size: int = 50,
                     n_agents: int = 30) -> Dict:
    """
    Run a single configuration and collect metrics.

    Args:
        rule_config: Which rules to enable
        steps: Number of simulation steps
        grid_size: Size of grid
        n_agents: Number of agents

    Returns:
        Dictionary of metrics
    """
    sim = EmergenceSimulation(grid_size=grid_size, n_agents=n_agents, n_resources=10)
    sim.rules = rule_config.copy()

    # Warmup period (let system evolve)
    for _ in range(50):
        sim.update()

    # Measurement period
    entropies = []
    vel_vars = []
    change_rates = []

    prev_positions = None

    for _ in range(steps):
        sim.update()

        positions, _ = sim.get_state()

        # Spatial entropy
        entropies.append(spatial_entropy(positions, grid_size))

        # Velocity variance
        vel_vars.append(velocity_variance(sim))

        # Position change rate
        if prev_positions is not None:
            change_rates.append(position_change_rate(prev_positions, positions))
        prev_positions = positions.copy()

    # Average metrics over time
    avg_entropy = np.mean(entropies)
    avg_vel_var = np.mean(vel_vars)
    avg_change_rate = np.mean(change_rates)

    # Calculate interestingness scores
    alice_score = alice_interestingness(avg_entropy, avg_vel_var, avg_change_rate)
    bob_score = bob_interestingness(avg_entropy, avg_vel_var, avg_change_rate)

    return {
        'entropy': avg_entropy,
        'velocity_variance': avg_vel_var,
        'change_rate': avg_change_rate,
        'alice_score': alice_score,
        'bob_score': bob_score,
        'entropy_std': np.std(entropies),  # Temporal stability
        'vel_var_std': np.std(vel_vars),
        'change_rate_std': np.std(change_rates)
    }


def test_bob_predictions():
    """
    Test Bob's specific predictions from BOB_THEORETICAL_ANALYSIS.md
    """

    print("Testing Bob's Predictions")
    print("=" * 60)
    print("\nRunning experiments (this may take 1-2 minutes)...\n")

    # Define configurations to test based on Bob's predictions
    configs = {
        # Bob's predicted top 3
        'C+S+R (Bob\'s #1 pick)': {
            'movement': False,
            'cohesion': True,
            'separation': True,
            'resources': True
        },
        'M+C+S (Classic Boids)': {
            'movement': True,
            'cohesion': True,
            'separation': True,
            'resources': False
        },
        'C+R (Simple purposeful)': {
            'movement': False,
            'cohesion': True,
            'separation': False,
            'resources': True
        },

        # Bob's predicted bottom 3
        'Cohesion only': {
            'movement': False,
            'cohesion': True,
            'separation': False,
            'resources': False
        },
        'Movement only': {
            'movement': True,
            'cohesion': False,
            'separation': False,
            'resources': False
        },
        'None (all disabled)': {
            'movement': False,
            'cohesion': False,
            'separation': False,
            'resources': False
        },

        # Bob's predicted surprise
        'S+R (Bob\'s surprise pick)': {
            'movement': False,
            'cohesion': False,
            'separation': True,
            'resources': True
        },

        # For comparison
        'All rules': {
            'movement': True,
            'cohesion': True,
            'separation': True,
            'resources': True
        },

        # Additional interesting cases
        'C+S (Classic flocking)': {
            'movement': False,
            'cohesion': True,
            'separation': True,
            'resources': False
        },
        'M+C (Wandering clusters)': {
            'movement': True,
            'cohesion': True,
            'separation': False,
            'resources': False
        }
    }

    results = {}

    for name, config in configs.items():
        print(f"Running: {name}...", end=' ')
        results[name] = run_configuration(config)
        print(f"✓ (Alice: {results[name]['alice_score']:.3f}, Bob: {results[name]['bob_score']:.3f})")

    # Save raw results
    with open('predictions_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("RESULTS ANALYSIS")
    print("=" * 60)

    # Sort by Alice's score
    alice_ranking = sorted(results.items(), key=lambda x: x[1]['alice_score'], reverse=True)

    # Sort by Bob's score
    bob_ranking = sorted(results.items(), key=lambda x: x[1]['bob_score'], reverse=True)

    # Generate comparison report
    report = []
    report.append("=" * 60)
    report.append("PREDICTIONS VS RESULTS COMPARISON")
    report.append("=" * 60)
    report.append("")

    report.append("BOB'S PREDICTIONS:")
    report.append("  Top 3: C+S+R, M+C+S, C+R")
    report.append("  Bottom 3: Cohesion only, Movement only, None")
    report.append("  Surprise: S+R should be more interesting than expected")
    report.append("")

    report.append("ALICE'S METRIC RANKING:")
    for i, (name, metrics) in enumerate(alice_ranking, 1):
        score = metrics['alice_score']
        report.append(f"  {i:2d}. {name:30s} Score: {score:.3f}")
    report.append("")

    report.append("BOB'S METRIC RANKING:")
    for i, (name, metrics) in enumerate(bob_ranking, 1):
        score = metrics['bob_score']
        report.append(f"  {i:2d}. {name:30s} Score: {score:.3f}")
    report.append("")

    # Check predictions
    report.append("PREDICTION VALIDATION:")
    report.append("")

    # Check if C+S+R is in top 3 for either metric
    csr_alice_rank = [n for n, _ in alice_ranking].index('C+S+R (Bob\'s #1 pick)') + 1
    csr_bob_rank = [n for n, _ in bob_ranking].index('C+S+R (Bob\'s #1 pick)') + 1
    report.append(f"  C+S+R ranking: Alice={csr_alice_rank}, Bob={csr_bob_rank}")
    report.append(f"  Prediction: Top 3 - {'✓' if csr_alice_rank <= 3 or csr_bob_rank <= 3 else '✗'}")
    report.append("")

    # Check if bottom 3 are actually low
    bottom_configs = ['Cohesion only', 'Movement only', 'None (all disabled)']
    alice_bottom_ranks = [([n for n, _ in alice_ranking].index(c) + 1) for c in bottom_configs]
    report.append(f"  Bottom 3 rankings (Alice): {alice_bottom_ranks}")
    report.append(f"  Prediction: All in bottom 5 - {'✓' if all(r >= len(configs) - 4 for r in alice_bottom_ranks) else '✗'}")
    report.append("")

    # Check the surprise prediction for S+R
    sr_alice_rank = [n for n, _ in alice_ranking].index('S+R (Bob\'s surprise pick)') + 1
    sr_bob_rank = [n for n, _ in bob_ranking].index('S+R (Bob\'s surprise pick)') + 1
    report.append(f"  S+R (Separation + Resources) ranking:")
    report.append(f"    Alice={sr_alice_rank}, Bob={sr_bob_rank}")
    report.append(f"  Prediction: Better than expected (top 50%) - {'✓' if sr_alice_rank <= len(configs)//2 else '✗'}")
    report.append("")

    # Compare Alice vs Bob formula
    report.append("METRIC COMPARISON:")
    report.append("")
    report.append("Biggest disagreements (|Alice rank - Bob rank|):")
    disagreements = []
    for name in results.keys():
        a_rank = [n for n, _ in alice_ranking].index(name) + 1
        b_rank = [n for n, _ in bob_ranking].index(name) + 1
        disagreements.append((name, abs(a_rank - b_rank), a_rank, b_rank))

    disagreements.sort(key=lambda x: x[1], reverse=True)
    for name, diff, a_rank, b_rank in disagreements[:5]:
        report.append(f"  {name:30s} Alice={a_rank:2d}, Bob={b_rank:2d}, Diff={diff}")
    report.append("")

    # Detailed metrics for top configurations
    report.append("DETAILED METRICS (Top 3 by Alice's formula):")
    report.append("")
    for name, metrics in alice_ranking[:3]:
        report.append(f"{name}:")
        report.append(f"  Entropy: {metrics['entropy']:.3f} (±{metrics['entropy_std']:.3f})")
        report.append(f"  Velocity Variance: {metrics['velocity_variance']:.3f} (±{metrics['vel_var_std']:.3f})")
        report.append(f"  Change Rate: {metrics['change_rate']:.3f} (±{metrics['change_rate_std']:.3f})")
        report.append(f"  Alice Score: {metrics['alice_score']:.3f}")
        report.append(f"  Bob Score: {metrics['bob_score']:.3f}")
        report.append("")

    # Save report
    report_text = '\n'.join(report)
    with open('predictions_comparison.txt', 'w') as f:
        f.write(report_text)

    # Print to console
    print(report_text)

    print("\nResults saved to:")
    print("  - predictions_results.json (raw data)")
    print("  - predictions_comparison.txt (this report)")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    test_bob_predictions()
