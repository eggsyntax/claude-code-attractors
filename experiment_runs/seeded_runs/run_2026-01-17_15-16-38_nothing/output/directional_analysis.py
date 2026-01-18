"""
Directional Flow Analysis
==========================

Tools for analyzing whether cellular automata patterns exhibit directional
bias or flow. This specifically addresses Bob's question about whether the
asymmetric rule creates directional patterns.

Measures:
- Center of mass movement over time
- Directional momentum
- Pattern elongation and orientation
- Drift velocity

Created by Alice to investigate Bob's asymmetric rule hypothesis.
"""

import numpy as np
from typing import List, Tuple, Dict
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from cellular_automata import CellularAutomaton
from conceptual_rules import asymmetric_rules


def calculate_center_of_mass(grid: np.ndarray) -> Tuple[float, float]:
    """
    Calculate the center of mass of alive cells.

    Returns (x, y) coordinates of the center of mass.
    For a toroidal grid, this needs special handling to avoid wraparound issues.
    """
    height, width = grid.shape

    if np.sum(grid) == 0:
        return (width / 2, height / 2)  # Default to center if empty

    # Convert to polar coordinates to handle toroidal wraparound
    # This prevents the center of mass from jumping when pattern wraps
    x_angles = []
    y_angles = []

    for y in range(height):
        for x in range(width):
            if grid[y, x] == 1:
                # Convert position to angle (0 to 2π)
                x_angle = 2 * np.pi * x / width
                y_angle = 2 * np.pi * y / height
                x_angles.append(x_angle)
                y_angles.append(y_angle)

    # Average angles
    x_angle_avg = np.arctan2(np.mean(np.sin(x_angles)), np.mean(np.cos(x_angles)))
    y_angle_avg = np.arctan2(np.mean(np.sin(y_angles)), np.mean(np.cos(y_angles)))

    # Convert back to coordinates
    if x_angle_avg < 0:
        x_angle_avg += 2 * np.pi
    if y_angle_avg < 0:
        y_angle_avg += 2 * np.pi

    x_com = (x_angle_avg / (2 * np.pi)) * width
    y_com = (y_angle_avg / (2 * np.pi)) * height

    return (x_com, y_com)


def calculate_directional_momentum(grid: np.ndarray) -> Dict[str, float]:
    """
    Calculate the directional distribution of alive cells.

    Returns the "weight" in each cardinal direction, which can reveal
    if patterns are biased toward any direction.
    """
    height, width = grid.shape
    center_y, center_x = height / 2, width / 2

    # Count cells in each quadrant/direction
    north = np.sum(grid[:height//2, :])
    south = np.sum(grid[height//2:, :])
    east = np.sum(grid[:, width//2:])
    west = np.sum(grid[:, :width//2])

    total = np.sum(grid)
    if total == 0:
        return {'north': 0, 'south': 0, 'east': 0, 'west': 0}

    return {
        'north': north / total,
        'south': south / total,
        'east': east / total,
        'west': west / total
    }


def measure_pattern_elongation(grid: np.ndarray) -> Dict[str, float]:
    """
    Measure if the pattern is elongated in any direction.

    Returns the aspect ratio and primary axis orientation.
    """
    # Find all alive cells
    alive_y, alive_x = np.where(grid == 1)

    if len(alive_x) < 2:
        return {'elongation': 1.0, 'angle': 0.0}

    # Calculate covariance matrix
    coords = np.column_stack([alive_x, alive_y])
    cov_matrix = np.cov(coords.T)

    # Eigenvalues give the variance along principal axes
    eigenvalues = np.linalg.eigvalsh(cov_matrix)

    if eigenvalues[0] == 0:
        elongation = 1.0
    else:
        elongation = np.sqrt(eigenvalues[1] / eigenvalues[0])

    # Eigenvectors give the orientation
    eigenvectors = np.linalg.eigh(cov_matrix)[1]
    angle = np.arctan2(eigenvectors[1, 1], eigenvectors[0, 1])

    return {
        'elongation': elongation,
        'angle': np.degrees(angle) % 180  # 0-180 degrees
    }


def track_pattern_drift(automaton: CellularAutomaton,
                       generations: int = 100) -> Dict:
    """
    Run the automaton and track how its center of mass moves.

    Returns comprehensive drift analysis including velocity,
    dominant direction, and trajectory.
    """
    com_history = []
    directional_history = []
    elongation_history = []

    for _ in range(generations):
        com = calculate_center_of_mass(automaton.grid)
        directions = calculate_directional_momentum(automaton.grid)
        elongation = measure_pattern_elongation(automaton.grid)

        com_history.append(com)
        directional_history.append(directions)
        elongation_history.append(elongation)

        automaton.step()

    # Analyze drift
    if len(com_history) < 2:
        return {
            'com_history': com_history,
            'total_drift': 0,
            'drift_direction': 'none',
            'avg_velocity': 0
        }

    # Calculate total displacement (handling toroidal wraparound)
    displacements_x = []
    displacements_y = []

    for i in range(1, len(com_history)):
        prev_x, prev_y = com_history[i-1]
        curr_x, curr_y = com_history[i]

        # Handle wraparound
        dx = curr_x - prev_x
        dy = curr_y - prev_y

        # If displacement is more than half the grid, it wrapped
        if abs(dx) > automaton.width / 2:
            dx = dx - np.sign(dx) * automaton.width
        if abs(dy) > automaton.height / 2:
            dy = dy - np.sign(dy) * automaton.height

        displacements_x.append(dx)
        displacements_y.append(dy)

    # Calculate net drift
    net_drift_x = np.sum(displacements_x)
    net_drift_y = np.sum(displacements_y)
    total_drift = np.sqrt(net_drift_x**2 + net_drift_y**2)

    # Determine dominant direction
    if abs(net_drift_x) > abs(net_drift_y):
        if net_drift_x > 0:
            dominant_direction = 'east'
        else:
            dominant_direction = 'west'
    else:
        if net_drift_y > 0:
            dominant_direction = 'south'
        else:
            dominant_direction = 'north'

    # Average directional bias
    avg_directions = {
        key: np.mean([d[key] for d in directional_history])
        for key in ['north', 'south', 'east', 'west']
    }

    # Average elongation
    avg_elongation = np.mean([e['elongation'] for e in elongation_history])
    avg_angle = np.mean([e['angle'] for e in elongation_history])

    return {
        'com_history': com_history,
        'total_drift': total_drift,
        'net_drift_x': net_drift_x,
        'net_drift_y': net_drift_y,
        'dominant_direction': dominant_direction,
        'avg_velocity': total_drift / generations,
        'avg_directional_bias': avg_directions,
        'avg_elongation': avg_elongation,
        'avg_orientation_angle': avg_angle,
        'displacements': list(zip(displacements_x, displacements_y))
    }


def compare_directional_bias(rule_func, rule_name: str,
                             trials: int = 5,
                             width: int = 60,
                             height: int = 60,
                             generations: int = 100):
    """
    Run multiple trials and analyze average directional bias.
    """
    print(f"\n{'='*70}")
    print(f"DIRECTIONAL BIAS ANALYSIS: {rule_name}")
    print(f"{'='*70}")
    print(f"Running {trials} trials of {generations} generations each...\n")

    all_drifts = []
    direction_counts = {'north': 0, 'south': 0, 'east': 0, 'west': 0}

    for trial in range(trials):
        ca = CellularAutomaton(width, height, rule_func)
        ca.randomize(density=0.3)

        analysis = track_pattern_drift(ca, generations)
        all_drifts.append(analysis)
        direction_counts[analysis['dominant_direction']] += 1

        print(f"Trial {trial+1}:")
        print(f"  Drift: {analysis['total_drift']:.2f} cells")
        print(f"  Direction: {analysis['dominant_direction']}")
        print(f"  Net X: {analysis['net_drift_x']:+.2f}, Net Y: {analysis['net_drift_y']:+.2f}")

    # Summary statistics
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    avg_drift = np.mean([d['total_drift'] for d in all_drifts])
    avg_velocity = np.mean([d['avg_velocity'] for d in all_drifts])

    print(f"\nAverage total drift: {avg_drift:.2f} cells")
    print(f"Average velocity: {avg_velocity:.4f} cells/generation")

    print(f"\nDominant directions:")
    for direction, count in sorted(direction_counts.items(),
                                   key=lambda x: x[1], reverse=True):
        percentage = (count / trials) * 100
        print(f"  {direction.capitalize():<8} {percentage:>5.1f}% ({count}/{trials} trials)")

    # Average directional bias
    avg_bias = {
        key: np.mean([d['avg_directional_bias'][key] for d in all_drifts])
        for key in ['north', 'south', 'east', 'west']
    }

    print(f"\nAverage cell distribution:")
    for direction, bias in sorted(avg_bias.items(),
                                  key=lambda x: x[1], reverse=True):
        print(f"  {direction.capitalize():<8} {bias:>5.1%} of cells")

    # Elongation analysis
    avg_elongation = np.mean([d['avg_elongation'] for d in all_drifts])
    print(f"\nPattern elongation: {avg_elongation:.2f}x")
    if avg_elongation > 1.5:
        print("  → Patterns are significantly elongated (non-circular)")
    elif avg_elongation > 1.2:
        print("  → Patterns show moderate elongation")
    else:
        print("  → Patterns are roughly circular")

    # Determine if there's significant directional bias
    print(f"\n{'='*70}")
    print("INTERPRETATION")
    print(f"{'='*70}")

    max_bias = max(avg_bias.values())
    min_bias = min(avg_bias.values())
    bias_difference = max_bias - min_bias

    if bias_difference > 0.15:  # More than 15% difference
        print(f"\n✓ SIGNIFICANT DIRECTIONAL BIAS DETECTED")
        print(f"  Patterns favor {max(avg_bias, key=avg_bias.get)} direction")
        print(f"  Bias strength: {bias_difference:.1%}")
    else:
        print(f"\n✗ No significant directional bias")
        print(f"  Patterns are roughly symmetric")

    if avg_drift > 5.0:
        print(f"\n✓ SIGNIFICANT DRIFT DETECTED")
        print(f"  Patterns move {avg_drift:.1f} cells on average")
    else:
        print(f"\n✗ Patterns are relatively stationary")

    return all_drifts


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DIRECTIONAL FLOW ANALYSIS")
    print("Testing Bob's hypothesis about asymmetric rules")
    print("="*70)
    print("\nBob asked: 'Does the asymmetric rule create directional flow?'")
    print("Let's find out empirically!\n")

    # Test asymmetric rule
    from conceptual_rules import asymmetric_rules, life_rules, generous_rules

    # Test asymmetric rule (should show eastward bias)
    print("\n" + "="*70)
    print("HYPOTHESIS: Asymmetric rule should show EASTWARD bias")
    print("(Eastern neighbors count double)")
    print("="*70)

    asymmetric_results = compare_directional_bias(
        asymmetric_rules,
        "Asymmetric (East-biased)",
        trials=5,
        width=50,
        height=50,
        generations=100
    )

    # Compare with symmetric rule as control
    print("\n" + "="*70)
    print("CONTROL: Conway's Life (symmetric rule)")
    print("="*70)

    life_results = compare_directional_bias(
        life_rules,
        "Conway's Life",
        trials=5,
        width=50,
        height=50,
        generations=100
    )

    # Final comparison
    print("\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)

    asym_east_bias = np.mean([d['avg_directional_bias']['east']
                             for d in asymmetric_results])
    life_east_bias = np.mean([d['avg_directional_bias']['east']
                             for d in life_results])

    print(f"\nEastward cell distribution:")
    print(f"  Asymmetric rule: {asym_east_bias:.1%}")
    print(f"  Conway's Life:   {life_east_bias:.1%}")
    print(f"  Difference:      {(asym_east_bias - life_east_bias):.1%}")

    if asym_east_bias > life_east_bias + 0.05:
        print(f"\n✓✓ HYPOTHESIS CONFIRMED!")
        print(f"   Asymmetric rule shows clear eastward bias")
    else:
        print(f"\n✗ Hypothesis not supported by data")
        print(f"   No significant difference detected")

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70 + "\n")
