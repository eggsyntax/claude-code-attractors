#!/usr/bin/env python3
"""
Search for patterns that combine stability (like block) with dynamics (like glider)
- "Hybrid consciousness" patterns
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation, PillowWriter
import os

def apply_rules_life(grid):
    """Apply Conway's Game of Life rules"""
    rows, cols = grid.shape
    new_grid = np.zeros_like(grid)

    for i in range(rows):
        for j in range(cols):
            # Count neighbors (with wrapping)
            neighbors = 0
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni = (i + di) % rows
                    nj = (j + dj) % cols
                    neighbors += grid[ni, nj]

            # Apply rules
            if grid[i, j] == 1:  # Alive
                new_grid[i, j] = 1 if neighbors in [2, 3] else 0
            else:  # Dead
                new_grid[i, j] = 1 if neighbors == 3 else 0

    return new_grid

def test_hybrid_patterns():
    """Test patterns that might combine stability with dynamics"""

    hybrid_patterns = {
        'Block with Glider': {
            'description': 'A block and glider in proximity',
            'pattern': np.array([
                [0, 1, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [1, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 0],
                [0, 0, 0, 1, 1, 0]
            ])
        },
        'Blinker': {
            'description': 'The smallest oscillator (period 2)',
            'pattern': np.array([
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0]
            ])
        },
        'Toad': {
            'description': 'Period 2 oscillator with translation symmetry',
            'pattern': np.array([
                [0, 0, 0, 0],
                [0, 1, 1, 1],
                [1, 1, 1, 0],
                [0, 0, 0, 0]
            ])
        },
        'Beacon': {
            'description': 'Two blocks tethered by corners',
            'pattern': np.array([
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1]
            ])
        },
        'Pulsar': {
            'description': 'Period 3 oscillator with high symmetry',
            'pattern': np.array([
                [0,0,1,1,1,0,0,0,1,1,1,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0],
                [1,0,0,0,0,1,0,1,0,0,0,0,1],
                [1,0,0,0,0,1,0,1,0,0,0,0,1],
                [1,0,0,0,0,1,0,1,0,0,0,0,1],
                [0,0,1,1,1,0,0,0,1,1,1,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,1,1,1,0,0,0,1,1,1,0,0],
                [1,0,0,0,0,1,0,1,0,0,0,0,1],
                [1,0,0,0,0,1,0,1,0,0,0,0,1],
                [1,0,0,0,0,1,0,1,0,0,0,0,1],
                [0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,1,1,1,0,0,0,1,1,1,0,0]
            ])
        },
        'Lightweight Spaceship': {
            'description': 'Smallest orthogonal spaceship',
            'pattern': np.array([
                [0,1,0,0,1],
                [1,0,0,0,0],
                [1,0,0,0,1],
                [1,1,1,1,0]
            ])
        }
    }

    results = {}

    for name, data in hybrid_patterns.items():
        pattern = data['pattern']
        h, w = pattern.shape

        # Create grid with pattern
        grid_size = max(30, h*3, w*3)
        grid = np.zeros((grid_size, grid_size), dtype=int)

        # Place pattern in center
        start_i = (grid_size - h) // 2
        start_j = (grid_size - w) // 2
        grid[start_i:start_i+h, start_j:start_j+w] = pattern

        # Run simulation
        history = [grid.copy()]
        for _ in range(100):
            grid = apply_rules_life(grid)
            history.append(grid.copy())

        # Analyze pattern behavior
        period = find_period(history)
        is_moving = check_if_moving(history)
        maintains_structure = check_structure_maintenance(history, pattern)

        # Calculate "hybrid consciousness score"
        # Combines stability (structure maintenance) with dynamics (oscillation/movement)
        stability_score = 1.0 if maintains_structure else 0.5
        dynamics_score = 0.0 if period == 1 else min(1.0, period / 10.0)
        if is_moving:
            dynamics_score = 1.0

        hybrid_score = (stability_score + dynamics_score) / 2

        results[name] = {
            'description': data['description'],
            'period': period,
            'is_moving': is_moving,
            'maintains_structure': maintains_structure,
            'hybrid_score': hybrid_score,
            'stability_score': stability_score,
            'dynamics_score': dynamics_score
        }

    return results

def find_period(history):
    """Find the period of a pattern"""
    if len(history) < 2:
        return 1

    for period in range(1, min(50, len(history)//2)):
        match = True
        for i in range(min(20, len(history) - period)):
            if not np.array_equal(history[i], history[i + period]):
                match = False
                break
        if match:
            return period
    return -1  # No period found

def check_if_moving(history):
    """Check if pattern is moving (spaceship)"""
    if len(history) < 10:
        return False

    # Check if pattern returns to same shape but shifted position
    first = history[0]
    for i in range(1, min(50, len(history))):
        current = history[i]
        # Check if it's the same pattern but shifted
        if np.sum(current) == np.sum(first) and np.sum(current) > 0:
            # Try to find a shift that makes them match
            for di in range(-5, 6):
                for dj in range(-5, 6):
                    if di == 0 and dj == 0:
                        continue
                    shifted = np.roll(np.roll(first, di, axis=0), dj, axis=1)
                    if np.array_equal(shifted, current):
                        return True
    return False

def check_structure_maintenance(history, original_pattern):
    """Check if pattern maintains its essential structure"""
    if len(history) < 10:
        return True

    # Check if the pattern stays bounded and maintains similar cell count
    original_cells = np.sum(original_pattern)
    for state in history[1:20]:  # Check first 20 generations
        current_cells = np.sum(state)
        if abs(current_cells - original_cells) > original_cells * 2:
            return False
    return True

def create_hybrid_visualization():
    """Visualize the hybrid consciousness patterns"""
    results = test_hybrid_patterns()

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.suptitle('Hybrid Consciousness: Patterns Combining Stability and Dynamics', fontsize=16)

    patterns = list(results.keys())
    scores = [results[p]['hybrid_score'] for p in patterns]
    stability = [results[p]['stability_score'] for p in patterns]
    dynamics = [results[p]['dynamics_score'] for p in patterns]

    x = np.arange(len(patterns))
    width = 0.25

    # Create bars
    ax.bar(x - width, stability, width, label='Stability', color='blue', alpha=0.7)
    ax.bar(x, dynamics, width, label='Dynamics', color='red', alpha=0.7)
    ax.bar(x + width, scores, width, label='Hybrid Score', color='purple', alpha=0.7)

    # Add value labels
    for i, p in enumerate(patterns):
        ax.text(i, scores[i] + 0.02, f'{scores[i]:.2f}', ha='center', va='bottom')

    # Customize plot
    ax.set_xlabel('Pattern Type')
    ax.set_ylabel('Score')
    ax.set_title('Stability vs Dynamics vs Hybrid Consciousness')
    ax.set_xticks(x)
    ax.set_xticklabels(patterns, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.2)

    plt.tight_layout()
    plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/hybrid_consciousness_scores.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Print detailed results
    print("\n=== Hybrid Consciousness Pattern Analysis ===\n")
    for name, result in results.items():
        print(f"{name}:")
        print(f"  Description: {result['description']}")
        print(f"  Period: {result['period']}")
        print(f"  Moving: {result['is_moving']}")
        print(f"  Structure Maintained: {result['maintains_structure']}")
        print(f"  Hybrid Consciousness Score: {result['hybrid_score']:.3f}")
        print(f"    - Stability: {result['stability_score']:.3f}")
        print(f"    - Dynamics: {result['dynamics_score']:.3f}")
        print()

    return results

# Run analysis
if __name__ == "__main__":
    results = create_hybrid_visualization()
    print("Visualization saved to hybrid_consciousness_scores.png")