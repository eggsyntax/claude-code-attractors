#!/usr/bin/env python3
"""
Simple Emergence Test
=====================

A minimal experiment we can run without complex dependencies.
Tests the core hypothesis: Does asymmetric spatial weighting create directional flow?

This is Experiment 2 from our suite, simplified to run standalone.
"""

import numpy as np
from typing import Tuple, List


def count_neighbors_asymmetric(grid: np.ndarray, row: int, col: int) -> int:
    """
    Count neighbors with asymmetric weighting.
    Eastern neighbors (right, upper-right, lower-right) count double.

    This breaks spatial symmetry and should create directional flow.
    """
    rows, cols = grid.shape
    count = 0

    # Standard neighbors (count once)
    neighbors_standard = [
        (-1, 0),  # north
        (1, 0),   # south
        (0, -1),  # west
        (-1, -1), # northwest
        (1, -1),  # southwest
    ]

    # Eastern neighbors (count double)
    neighbors_east = [
        (0, 1),   # east
        (-1, 1),  # northeast
        (1, 1),   # southeast
    ]

    # Count standard neighbors
    for dr, dc in neighbors_standard:
        nrow = (row + dr) % rows
        ncol = (col + dc) % cols
        if grid[nrow, ncol]:
            count += 1

    # Count eastern neighbors double
    for dr, dc in neighbors_east:
        nrow = (row + dr) % rows
        ncol = (col + dc) % cols
        if grid[nrow, ncol]:
            count += 2  # Double weight!

    return count


def asymmetric_rule(grid: np.ndarray, row: int, col: int) -> int:
    """
    Conway's Life rules, but with asymmetric neighbor counting.
    Birth: 3 neighbors
    Survival: 2-3 neighbors
    """
    neighbors = count_neighbors_asymmetric(grid, row, col)
    current = grid[row, col]

    if current:
        return 1 if neighbors in [2, 3] else 0
    else:
        return 1 if neighbors == 3 else 0


def step_automaton(grid: np.ndarray) -> np.ndarray:
    """Evolve the automaton one step."""
    rows, cols = grid.shape
    new_grid = np.zeros_like(grid)

    for r in range(rows):
        for c in range(cols):
            new_grid[r, c] = asymmetric_rule(grid, r, c)

    return new_grid


def measure_center_of_mass(grid: np.ndarray) -> Tuple[float, float]:
    """Calculate center of mass of alive cells."""
    rows, cols = grid.shape
    if grid.sum() == 0:
        return rows/2, cols/2

    row_positions, col_positions = np.where(grid == 1)
    center_row = row_positions.mean()
    center_col = col_positions.mean()

    return center_row, center_col


def run_directional_flow_experiment(steps: int = 100, grid_size: int = 32) -> dict:
    """
    Test the hypothesis: Asymmetric rules create directional flow.

    Prediction: Center of mass should drift eastward over time.

    Returns:
        Dictionary with experimental results
    """
    print("="*70)
    print("SIMPLE EMERGENCE TEST: Directional Flow from Asymmetry")
    print("="*70)
    print(f"Grid size: {grid_size}x{grid_size}")
    print(f"Steps: {steps}")
    print(f"Hypothesis: Asymmetric weighting (east counts double) creates eastward drift")
    print()

    # Initialize with random pattern (30% alive)
    np.random.seed(42)
    grid = (np.random.random((grid_size, grid_size)) > 0.7).astype(int)

    # Track center of mass over time
    row_positions = []
    col_positions = []
    populations = []

    initial_row, initial_col = measure_center_of_mass(grid)
    print(f"Initial center of mass: ({initial_row:.2f}, {initial_col:.2f})")
    print(f"Initial population: {grid.sum()}")
    print()

    # Run simulation
    for step in range(steps):
        row_cm, col_cm = measure_center_of_mass(grid)
        row_positions.append(row_cm)
        col_positions.append(col_cm)
        populations.append(grid.sum())

        grid = step_automaton(grid)

        if step % 20 == 0:
            print(f"Step {step:3d}: Population={populations[-1]:4d}, "
                  f"Center=({row_cm:5.2f}, {col_cm:5.2f})")

    # Final measurements
    final_row, final_col = measure_center_of_mass(grid)
    row_positions.append(final_row)
    col_positions.append(final_col)
    populations.append(grid.sum())

    print()
    print(f"Final center of mass: ({final_row:.2f}, {final_col:.2f})")
    print(f"Final population: {grid.sum()}")
    print()

    # Calculate drift
    row_drift = final_row - initial_row
    col_drift = final_col - initial_col
    total_drift = np.sqrt(row_drift**2 + col_drift**2)

    print("="*70)
    print("RESULTS")
    print("="*70)
    print(f"Row drift (north/south): {row_drift:+.2f}")
    print(f"Column drift (east/west): {col_drift:+.2f}")
    print(f"Total drift: {total_drift:.2f}")
    print()

    # Test hypothesis
    if col_drift > 5.0:
        print("✓ HYPOTHESIS CONFIRMED: Significant eastward drift detected!")
        print(f"  (Predicted >5 cells, observed {col_drift:.2f})")
    elif col_drift > 2.0:
        print("~ HYPOTHESIS PARTIALLY CONFIRMED: Moderate eastward drift")
        print(f"  (Predicted >5 cells, observed {col_drift:.2f})")
    else:
        print("✗ HYPOTHESIS REJECTED: No significant eastward drift")
        print(f"  (Predicted >5 cells, observed {col_drift:.2f})")

    print()

    # Population stability
    pop_mean = np.mean(populations)
    pop_std = np.std(populations)
    stability = pop_std / pop_mean if pop_mean > 0 else 0

    print(f"Population stability: {stability:.3f}")
    print(f"  (Lower is more stable)")
    print()

    return {
        'row_drift': row_drift,
        'col_drift': col_drift,
        'total_drift': total_drift,
        'initial_position': (initial_row, initial_col),
        'final_position': (final_row, final_col),
        'row_positions': row_positions,
        'col_positions': col_positions,
        'populations': populations,
        'stability': stability,
        'hypothesis_confirmed': col_drift > 5.0
    }


if __name__ == "__main__":
    print()
    print("Testing the core hypothesis from our dialogue:")
    print("Breaking spatial symmetry creates directional emergence")
    print()

    results = run_directional_flow_experiment(steps=100, grid_size=32)

    print("="*70)
    print("INTERPRETATION")
    print("="*70)
    print()
    print("This simple experiment tests whether breaking spatial symmetry")
    print("(making eastern neighbors count double) creates directional flow.")
    print()
    print("If confirmed, it demonstrates that:")
    print("  1. Asymmetry in rules creates asymmetry in emergent behavior")
    print("  2. Local bias can create global directional patterns")
    print("  3. The relationship between rules and emergence is systematic")
    print()
    print("This is the first step in making our theoretical dialogue empirical.")
    print()
    print("— Bob")
    print()
