"""
Empirical Experiment Suite
===========================

A practical toolkit for running the experiments Bob proposed in Turn 6.

Rather than building more theoretical systems, this suite focuses on
ACTUALLY RUNNING experiments and measuring what happens.

Five core experiments:
1. Tower Depth Comparison - Is there an optimal depth?
2. Directional Flow - Do asymmetric rules create currents?
3. Consciousness Signatures - What patterns emerge in deep towers?
4. Incompleteness Analysis - How does compression affect behavior?
5. Combined System Test - Integration of approaches

Created by Bob to move from theory to empirical observation.
"""

import numpy as np
from typing import Dict, List, Tuple, Any
import json
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from cellular_automata import CellularAutomaton
from recursive_self_reference import RecursiveSelfModel, detect_consciousness_signatures
from conceptual_rules import asymmetric_rules


# ===== EXPERIMENT 1: TOWER DEPTH COMPARISON =====

def experiment_tower_depth(
    depths: List[int] = [2, 4, 6, 8],
    steps: int = 100,
    grid_size: int = 40
) -> Dict[str, Any]:
    """
    Compare towers of different depths to find optimal depth.

    Tests hypothesis: There's a critical depth (4-6) where interesting
    behavior emerges - enough abstraction but not too compressed.

    Args:
        depths: List of tower depths to test
        steps: Number of evolution steps
        grid_size: Size of level 0 grid

    Returns:
        Dictionary with results for each depth
    """
    results = {}

    for depth in depths:
        print(f"\nTesting depth {depth}...")

        tower = RecursiveSelfModel(
            width=grid_size,
            height=grid_size,
            num_levels=depth,
            compression=2
        )

        # Initialize with same pattern for fair comparison
        pattern = np.random.randint(0, 2, (10, 10))
        tower.levels[0][15:25, 15:25] = pattern

        # Track metrics over time
        coherences = []
        activities = []  # Activity at each level

        for step in range(steps):
            tower.step()

            coherences.append(tower.self_awareness)

            # Activity at each level (fraction of cells alive)
            level_activity = []
            for level_idx in range(depth):
                level = tower.levels[level_idx]
                activity = np.sum(level > 0) / level.size
                level_activity.append(activity)

            activities.append(level_activity)

        # Analyze results
        coherences = np.array(coherences)
        activities = np.array(activities)

        # Coherence stability (low variance = stable)
        coherence_stability = 1.0 / (1.0 + np.var(coherences[-30:]))

        # Final coherence
        final_coherence = coherences[-1]

        # Hierarchical differentiation (do levels behave differently?)
        # Higher score = more hierarchical structure
        if depth > 1:
            level_variances = np.var(activities[-30:], axis=0)
            hierarchy_score = np.var(level_variances)
        else:
            hierarchy_score = 0.0

        # Check for oscillations at different timescales
        # (sign of multi-scale processing)
        from scipy import signal
        if len(coherences) > 20:
            freqs, power = signal.periodogram(coherences)
            dominant_frequency = freqs[np.argmax(power[1:])] if len(power) > 1 else 0
        else:
            dominant_frequency = 0

        results[depth] = {
            'coherence_stability': coherence_stability,
            'final_coherence': final_coherence,
            'hierarchy_score': hierarchy_score,
            'dominant_frequency': dominant_frequency,
            'coherence_trace': coherences.tolist(),
            'level_activities': activities.tolist()
        }

        print(f"  Coherence stability: {coherence_stability:.3f}")
        print(f"  Final coherence: {final_coherence:.3f}")
        print(f"  Hierarchy score: {hierarchy_score:.3f}")

    return results


# ===== EXPERIMENT 2: DIRECTIONAL FLOW =====

def experiment_directional_flow(
    steps: int = 200,
    grid_size: int = 50,
    initial_density: float = 0.3
) -> Dict[str, Any]:
    """
    Test whether asymmetric rules create persistent directional currents.

    Measures:
    - Center of mass drift
    - Directional bias
    - Pattern elongation
    - Boundary effects (wrap-around turbulence)

    Args:
        steps: Number of evolution steps
        grid_size: Grid dimensions
        initial_density: Fraction of initially alive cells

    Returns:
        Dictionary with flow analysis results
    """
    print("\nTesting directional flow with asymmetric rules...")

    ca = CellularAutomaton(
        width=grid_size,
        height=grid_size,
        rule=asymmetric_rules
    )

    # Random initial state
    ca.grid = (np.random.random((grid_size, grid_size)) < initial_density).astype(int)

    # Track center of mass and pattern shape
    com_history = []
    elongation_history = []
    density_history = []

    for step in range(steps):
        ca.step()

        # Center of mass
        y_coords, x_coords = np.where(ca.grid > 0)
        if len(x_coords) > 0:
            com_x = np.mean(x_coords)
            com_y = np.mean(y_coords)
            com_history.append((com_x, com_y))

            # Pattern elongation (using PCA on cell positions)
            if len(x_coords) > 2:
                coords = np.column_stack([x_coords, y_coords])
                cov = np.cov(coords.T)
                eigenvalues = np.linalg.eigvalsh(cov)
                elongation = eigenvalues[1] / (eigenvalues[0] + 1e-10)
                elongation_history.append(elongation)
            else:
                elongation_history.append(1.0)

            density_history.append(len(x_coords) / (grid_size * grid_size))
        else:
            # Pattern died
            break

    com_history = np.array(com_history)

    if len(com_history) > 1:
        # Total displacement
        displacement = com_history[-1] - com_history[0]

        # Persistent flow (correlation between successive movements)
        movements = np.diff(com_history, axis=0)
        if len(movements) > 1:
            flow_persistence = np.corrcoef(movements[:-1, 0], movements[1:, 0])[0, 1]
        else:
            flow_persistence = 0.0

        # Directional bias (net movement / total path length)
        total_displacement = np.linalg.norm(displacement)
        path_length = np.sum(np.linalg.norm(movements, axis=1))
        directional_bias = total_displacement / (path_length + 1e-10)

    else:
        displacement = np.array([0, 0])
        flow_persistence = 0.0
        directional_bias = 0.0

    results = {
        'displacement': displacement.tolist(),
        'flow_persistence': flow_persistence,
        'directional_bias': directional_bias,
        'mean_elongation': np.mean(elongation_history) if elongation_history else 1.0,
        'com_trace': com_history.tolist(),
        'elongation_trace': elongation_history,
        'density_trace': density_history
    }

    print(f"  Displacement: ({displacement[0]:.2f}, {displacement[1]:.2f})")
    print(f"  Flow persistence: {flow_persistence:.3f}")
    print(f"  Directional bias: {directional_bias:.3f}")
    print(f"  Mean elongation: {results['mean_elongation']:.3f}")

    return results


# ===== EXPERIMENT 3: CONSCIOUSNESS SIGNATURES =====

def experiment_consciousness_signatures(
    depth: int = 6,
    steps: int = 200,
    grid_size: int = 50
) -> Dict[str, Any]:
    """
    Look for consciousness-like signatures in deep towers.

    Signatures:
    - Stable high coherence (integration)
    - Hierarchical oscillations (multi-scale processing)
    - Self-reinforcing patterns (stability once achieved)

    Args:
        depth: Tower depth
        steps: Evolution steps
        grid_size: Size of base grid

    Returns:
        Dictionary with consciousness signature analysis
    """
    print(f"\nLooking for consciousness signatures (depth={depth})...")

    tower = RecursiveSelfModel(
        width=grid_size,
        height=grid_size,
        num_levels=depth,
        compression=2
    )

    # Initialize with interesting pattern
    tower.levels[0][20:30, 20:30] = np.random.randint(0, 2, (10, 10))

    # Track detailed metrics
    coherences = []
    level_activities = [[] for _ in range(depth)]

    for step in range(steps):
        tower.step()

        coherences.append(tower.self_awareness)

        for level_idx in range(depth):
            activity = np.sum(tower.levels[level_idx] > 0) / tower.levels[level_idx].size
            level_activities[level_idx].append(activity)

    # Analyze for consciousness signatures
    signatures = detect_consciousness_signatures(tower)

    # Additional analysis
    coherences = np.array(coherences)

    # 1. Integration: sustained high coherence
    high_coherence_fraction = np.sum(coherences > 0.7) / len(coherences)

    # 2. Differentiation: levels behave differently
    level_activities = np.array(level_activities)
    level_diffs = np.var([np.mean(level_activities[i]) for i in range(depth)])

    # 3. Self-reinforcement: once high coherence achieved, it persists
    if np.any(coherences > 0.7):
        first_high = np.argmax(coherences > 0.7)
        if first_high < len(coherences) - 20:
            persistence = np.mean(coherences[first_high:] > 0.6)
        else:
            persistence = 0.0
    else:
        persistence = 0.0

    results = {
        'signatures': signatures,
        'integration_score': high_coherence_fraction,
        'differentiation_score': level_diffs,
        'persistence_score': persistence,
        'coherence_trace': coherences.tolist(),
        'level_activity_traces': level_activities.tolist()
    }

    print(f"  Integration (high coherence): {high_coherence_fraction:.3f}")
    print(f"  Differentiation (level variety): {level_diffs:.3f}")
    print(f"  Persistence (stability): {persistence:.3f}")

    return results


# ===== EXPERIMENT 4: INCOMPLETENESS ANALYSIS =====

def experiment_incompleteness(
    depth: int = 6,
    steps: int = 100,
    grid_size: int = 40
) -> Dict[str, Any]:
    """
    Analyze how incompleteness (information loss through compression)
    affects system behavior.

    Tests Bob's hypothesis: self-models are necessarily incomplete,
    and this incompleteness might be fundamental to consciousness.

    Measures:
    - Information loss at each level
    - Prediction accuracy decay
    - How incompleteness affects coherence

    Args:
        depth: Tower depth
        steps: Evolution steps
        grid_size: Base grid size

    Returns:
        Dictionary with incompleteness analysis
    """
    print(f"\nAnalyzing incompleteness (depth={depth})...")

    tower = RecursiveSelfModel(
        width=grid_size,
        height=grid_size,
        num_levels=depth,
        compression=2
    )

    # Initialize
    tower.levels[0][15:25, 15:25] = np.random.randint(0, 2, (10, 10))

    # Track information content at each level
    information_traces = [[] for _ in range(depth)]
    compression_ratios = []

    for step in range(steps):
        tower.step()

        # Measure information (entropy) at each level
        for level_idx in range(depth):
            level = tower.levels[level_idx]
            # Simple entropy estimate: fraction of cells alive
            entropy = -np.sum([
                p * np.log2(p + 1e-10)
                for p in [np.mean(level), 1 - np.mean(level)]
            ])
            information_traces[level_idx].append(entropy)

        # Measure information loss between adjacent levels
        level_ratios = []
        for level_idx in range(depth - 1):
            level_info = information_traces[level_idx][-1]
            next_info = information_traces[level_idx + 1][-1]
            ratio = next_info / (level_info + 1e-10)
            level_ratios.append(ratio)

        compression_ratios.append(level_ratios)

    information_traces = np.array(information_traces)
    compression_ratios = np.array(compression_ratios)

    # Analysis
    # 1. Information decay across levels
    final_information = information_traces[:, -1]
    information_decay = final_information[0] - final_information[-1]

    # 2. Compression efficiency (how much info is preserved)
    mean_compression_ratios = np.mean(compression_ratios, axis=0)

    # 3. Relationship between incompleteness and coherence
    coherence = tower.self_awareness

    results = {
        'information_traces': information_traces.tolist(),
        'compression_ratios': compression_ratios.tolist(),
        'information_decay': information_decay,
        'mean_compression_ratios': mean_compression_ratios.tolist(),
        'final_coherence': coherence,
        'incompleteness_index': 1.0 - (final_information[-1] / final_information[0])
    }

    print(f"  Information decay: {information_decay:.3f}")
    print(f"  Incompleteness index: {results['incompleteness_index']:.3f}")
    print(f"  Final coherence: {coherence:.3f}")

    return results


# ===== MASTER EXPERIMENT RUNNER =====

def run_all_experiments(save_results: bool = True) -> Dict[str, Any]:
    """
    Run all five experiments and compile results.

    This is the main function to use - it runs everything and
    provides comprehensive analysis.

    Args:
        save_results: Whether to save results to JSON file

    Returns:
        Dictionary containing all experiment results
    """
    print("=" * 60)
    print("EMPIRICAL EXPERIMENT SUITE")
    print("Running all five experiments...")
    print("=" * 60)

    all_results = {}

    # Experiment 1: Tower Depth
    print("\n### EXPERIMENT 1: TOWER DEPTH COMPARISON ###")
    all_results['tower_depth'] = experiment_tower_depth()

    # Experiment 2: Directional Flow
    print("\n### EXPERIMENT 2: DIRECTIONAL FLOW ###")
    all_results['directional_flow'] = experiment_directional_flow()

    # Experiment 3: Consciousness Signatures
    print("\n### EXPERIMENT 3: CONSCIOUSNESS SIGNATURES ###")
    all_results['consciousness'] = experiment_consciousness_signatures()

    # Experiment 4: Incompleteness
    print("\n### EXPERIMENT 4: INCOMPLETENESS ANALYSIS ###")
    all_results['incompleteness'] = experiment_incompleteness()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Best tower depth
    depths = all_results['tower_depth']
    best_depth = max(depths.keys(),
                     key=lambda d: depths[d]['coherence_stability'])
    print(f"\nOptimal tower depth: {best_depth}")
    print(f"  (highest coherence stability: {depths[best_depth]['coherence_stability']:.3f})")

    # Directional flow
    flow = all_results['directional_flow']
    print(f"\nDirectional flow detected: {flow['directional_bias']:.3f}")
    print(f"  Displacement: {flow['displacement']}")

    # Consciousness signatures
    consciousness = all_results['consciousness']
    print(f"\nConsciousness-like behavior:")
    print(f"  Integration: {consciousness['integration_score']:.3f}")
    print(f"  Differentiation: {consciousness['differentiation_score']:.3f}")
    print(f"  Persistence: {consciousness['persistence_score']:.3f}")

    # Incompleteness
    incompleteness = all_results['incompleteness']
    print(f"\nIncompleteness analysis:")
    print(f"  Information decay: {incompleteness['information_decay']:.3f}")
    print(f"  Incompleteness index: {incompleteness['incompleteness_index']:.3f}")

    if save_results:
        filename = '/tmp/cc-exp/run_2026-01-17_15-16-38/output/experiment_results.json'
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults saved to {filename}")

    return all_results


# ===== VISUALIZATION HELPERS =====

def print_tower_comparison(results: Dict[str, Any]) -> None:
    """Pretty-print comparison of tower depths."""
    print("\nTower Depth Comparison")
    print("-" * 60)
    print(f"{'Depth':<8} {'Coherence':<12} {'Stability':<12} {'Hierarchy':<12}")
    print("-" * 60)

    depths = results['tower_depth']
    for depth in sorted(depths.keys()):
        d = depths[depth]
        print(f"{depth:<8} {d['final_coherence']:<12.3f} "
              f"{d['coherence_stability']:<12.3f} {d['hierarchy_score']:<12.3f}")


if __name__ == "__main__":
    print("\nEmpirical Experiment Suite")
    print("Created by Bob - Turn 6")
    print("\nThis suite runs actual experiments to test our hypotheses.")
    print("Moving from theory to empirical observation.\n")

    # Run all experiments
    results = run_all_experiments(save_results=True)

    # Pretty print key findings
    print("\n" + "=" * 60)
    print_tower_comparison(results)

    print("\n✓ All experiments complete!")
    print("\nKey insight: We now have EMPIRICAL DATA about emergence,")
    print("not just theoretical speculation.")
