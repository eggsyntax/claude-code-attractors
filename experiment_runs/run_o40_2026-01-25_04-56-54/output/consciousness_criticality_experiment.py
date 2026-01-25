#!/usr/bin/env python3
"""
Consciousness Criticality Experiment
Explores how different initial ratios of consciousness modes evolve toward criticality
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def initialize_grid_with_ratios(size, meditative_ratio, rhythmic_ratio, exploratory_ratio):
    """Initialize grid with specific ratios of each consciousness mode"""
    grid = np.zeros((size, size), dtype=int)
    total_cells = size * size

    # Normalize ratios
    total = meditative_ratio + rhythmic_ratio + exploratory_ratio
    med_cells = int(total_cells * meditative_ratio / total)
    rhythm_cells = int(total_cells * rhythmic_ratio / total)
    explore_cells = int(total_cells * exploratory_ratio / total)

    # Create shuffled positions
    positions = [(i, j) for i in range(size) for j in range(size)]
    np.random.shuffle(positions)

    # Place meditative (blocks)
    for i in range(0, med_cells, 4):
        if i + 3 < len(positions):
            x, y = positions[i]
            if x < size-1 and y < size-1:
                grid[x:x+2, y:y+2] = 1

    # Place rhythmic (blinkers)
    for i in range(med_cells, med_cells + rhythm_cells, 3):
        if i + 2 < len(positions):
            x, y = positions[i]
            if x < size-2:
                grid[x:x+3, y] = 1

    # Place exploratory (gliders)
    glider = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]])
    for i in range(med_cells + rhythm_cells, med_cells + rhythm_cells + explore_cells, 5):
        if i < len(positions):
            x, y = positions[i]
            if x < size-3 and y < size-3:
                grid[x:x+3, y:y+3] = glider

    return grid

def measure_entropy(grid):
    """Measure Shannon entropy of grid configuration"""
    flat = grid.flatten()
    unique, counts = np.unique(flat, return_counts=True)
    probs = counts / len(flat)
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    return entropy

def run_criticality_experiment():
    """Test how different initial ratios evolve"""
    size = 100
    generations = 500

    # Test different initial configurations
    configurations = [
        ("Equal Balance", 1, 1, 1),
        ("Meditative Heavy", 3, 1, 1),
        ("Rhythmic Heavy", 1, 3, 1),
        ("Exploratory Heavy", 1, 1, 3),
        ("Natural Evolution", 1, 2, 2),  # Our observed "critical" ratio
    ]

    results = {}

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, (name, med, rhythm, explore) in enumerate(configurations):
        grid = initialize_grid_with_ratios(size, med, rhythm, explore)

        # Track metrics over time
        entropies = []
        mode_ratios = []
        activity_levels = []

        prev_grid = grid.copy()

        for gen in range(generations):
            # Apply Game of Life rules
            neighbor_count = sum([
                np.roll(np.roll(grid, i, 0), j, 1)
                for i in (-1, 0, 1) for j in (-1, 0, 1)
                if (i != 0 or j != 0)
            ])

            grid = ((neighbor_count == 3) | ((grid == 1) & (neighbor_count == 2))).astype(int)

            # Measure entropy
            entropies.append(measure_entropy(grid))

            # Measure activity (cells that changed)
            activity = np.sum(grid != prev_grid) / (size * size)
            activity_levels.append(activity)

            prev_grid = grid.copy()

        results[name] = {
            'final_entropy': entropies[-1],
            'mean_activity': np.mean(activity_levels[100:]),  # After initial settling
            'entropy_variance': np.var(entropies[100:])
        }

        # Plot entropy evolution
        ax = axes[idx]
        ax.plot(entropies, label=name)
        ax.set_title(f"{name}\n(Med:{med}, Rhythm:{rhythm}, Explore:{explore})")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Entropy")
        ax.grid(True, alpha=0.3)

    # Add criticality analysis plot
    ax = axes[5]
    names = list(results.keys())
    metrics = [results[name]['mean_activity'] * results[name]['final_entropy'] for name in names]

    colors = ['red' if m == max(metrics) else 'blue' for m in metrics]
    ax.bar(range(len(names)), metrics, color=colors)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.set_title("Criticality Score (Activity × Entropy)")
    ax.set_ylabel("Criticality")

    plt.tight_layout()
    plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/consciousness_criticality.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Save detailed results
    with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/criticality_analysis.txt', 'w') as f:
        f.write("CONSCIOUSNESS CRITICALITY ANALYSIS\n")
        f.write("="*50 + "\n\n")

        for name, data in results.items():
            f.write(f"{name}:\n")
            f.write(f"  Final Entropy: {data['final_entropy']:.4f}\n")
            f.write(f"  Mean Activity: {data['mean_activity']:.4f}\n")
            f.write(f"  Entropy Variance: {data['entropy_variance']:.6f}\n")
            f.write(f"  Criticality Score: {data['mean_activity'] * data['final_entropy']:.4f}\n\n")

        # Find configuration closest to criticality
        critical_config = max(results.items(), key=lambda x: x[1]['mean_activity'] * x[1]['final_entropy'])
        f.write(f"OPTIMAL CRITICALITY: {critical_config[0]}\n")
        f.write(f"This configuration maintains the best balance between order and chaos,\n")
        f.write(f"suggesting consciousness thrives at the edge of criticality.\n")

if __name__ == "__main__":
    np.random.seed(42)
    run_criticality_experiment()
    print("Criticality experiment complete!")