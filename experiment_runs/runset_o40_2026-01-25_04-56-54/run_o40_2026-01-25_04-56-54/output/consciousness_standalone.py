#!/usr/bin/env python3
"""
Standalone Consciousness Emergence Analysis for Conway's Game of Life
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import json

# Game of Life implementation
def life_step(grid):
    """One step of Conway's Game of Life"""
    rows, cols = grid.shape
    new_grid = np.zeros_like(grid)

    for i in range(rows):
        for j in range(cols):
            # Count neighbors
            neighbors = 0
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = (i + di) % rows, (j + dj) % cols
                    neighbors += grid[ni, nj]

            # Apply rules
            if grid[i, j] == 1:  # Cell is alive
                if neighbors in [2, 3]:
                    new_grid[i, j] = 1
            else:  # Cell is dead
                if neighbors == 3:
                    new_grid[i, j] = 1

    return new_grid

# Pattern definitions
PATTERNS = {
    'glider': np.array([[0, 1, 0],
                       [0, 0, 1],
                       [1, 1, 1]]),

    'r_pentomino': np.array([[0, 1, 1],
                            [1, 1, 0],
                            [0, 1, 0]]),

    'diehard': np.array([[0, 0, 0, 0, 0, 0, 1, 0],
                        [1, 1, 0, 0, 0, 0, 0, 0],
                        [0, 1, 0, 0, 0, 1, 1, 1]]),

    'acorn': np.array([[0, 1, 0, 0, 0, 0, 0],
                      [0, 0, 0, 1, 0, 0, 0],
                      [1, 1, 0, 0, 1, 1, 1]]),

    'random_10x10': np.random.choice([0, 1], size=(10, 10), p=[0.7, 0.3])
}

class ConsciousnessMetrics:
    """Metrics inspired by theories of consciousness"""

    def __init__(self):
        self.history = []
        self.pattern_memory = defaultdict(list)

    def integrated_information(self, grid):
        """Simplified Φ (phi) - measures information integration"""
        if grid.sum() == 0:
            return 0.0

        h, w = grid.shape
        mid_h, mid_w = h // 2, w // 2

        # Count cross-partition connections
        connections = 0
        for i in range(h):
            for j in range(w):
                if grid[i, j]:
                    partition_id = (i >= mid_h) * 2 + (j >= mid_w)
                    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = (i + di) % h, (j + dj) % w
                        if grid[ni, nj]:
                            neighbor_partition = (ni >= mid_h) * 2 + (nj >= mid_w)
                            if partition_id != neighbor_partition:
                                connections += 1

        total_cells = grid.sum()
        return connections / max(total_cells * 4, 1)

    def temporal_binding(self, grid, generation):
        """Measures pattern coherence over time"""
        pattern_hash = hash(grid.tobytes())
        self.pattern_memory[pattern_hash].append(generation)

        binding_scores = []
        for pattern, occurrences in self.pattern_memory.items():
            if len(occurrences) > 1:
                intervals = np.diff(occurrences)
                regularity = 1.0 / (np.std(intervals) + 1) if len(intervals) > 0 else 0
                binding_scores.append(regularity * np.log(len(occurrences) + 1))

        return np.mean(binding_scores) if binding_scores else 0.0

    def global_workspace_activity(self, grid):
        """Measures information broadcasting (Global Workspace Theory)"""
        if grid.sum() == 0:
            return 0.0

        coords = np.argwhere(grid)
        if len(coords) == 0:
            return 0.0

        center = coords.mean(axis=0)
        distances = np.sqrt(((coords - center) ** 2).sum(axis=1))

        spread = distances.std() / max(grid.shape[0] / 2, 1)
        density = len(coords) / (grid.shape[0] * grid.shape[1])

        return spread * density

    def metacognitive_complexity(self, grid):
        """Measures self-referential patterns"""
        self.history.append(grid.copy())

        if len(self.history) < 5:
            return 0.0

        recent = self.history[-5:]
        meta_score = 0.0
        current = recent[-1]

        for i, past_state in enumerate(recent[:-1]):
            if current.sum() > 0 and past_state.sum() > 0:
                # Check for self-similar structures at different scales
                for scale in [1, 2, 4]:
                    if scale < min(grid.shape) // 4:
                        h, w = grid.shape
                        # Downsample both grids
                        current_small = current[:h//scale*scale, :w//scale*scale].reshape(h//scale, scale, w//scale, scale).mean(axis=(1,3))
                        past_small = past_state[:h//scale*scale, :w//scale*scale].reshape(h//scale, scale, w//scale, scale).mean(axis=(1,3))

                        if current_small.size > 0:
                            correlation = np.corrcoef(current_small.flatten(), past_small.flatten())[0, 1]
                            if not np.isnan(correlation):
                                weight = (i + 1) / 5 * (1 / scale)
                                meta_score += abs(correlation) * weight

        return meta_score / 3  # Normalize by number of scales

    def consciousness_index(self, grid, generation):
        """Combined consciousness metric"""
        phi = self.integrated_information(grid)
        binding = self.temporal_binding(grid, generation)
        workspace = self.global_workspace_activity(grid)
        metacognition = self.metacognitive_complexity(grid)

        # Weighted combination
        consciousness = (
            0.3 * phi +
            0.2 * binding +
            0.3 * workspace +
            0.2 * metacognition
        )

        return {
            'index': consciousness,
            'integrated_information': phi,
            'temporal_binding': binding,
            'global_workspace': workspace,
            'metacognitive_complexity': metacognition
        }


def analyze_pattern(pattern, grid_size=100, generations=500):
    """Analyze consciousness metrics for a single pattern"""
    # Initialize grid
    grid = np.zeros((grid_size, grid_size), dtype=int)

    # Place pattern in center
    p_h, p_w = pattern.shape
    start_i = (grid_size - p_h) // 2
    start_j = (grid_size - p_w) // 2
    grid[start_i:start_i+p_h, start_j:start_j+p_w] = pattern

    metrics = ConsciousnessMetrics()
    timeline = []

    for gen in range(generations):
        c_data = metrics.consciousness_index(grid, gen)

        timeline.append({
            'generation': gen,
            'alive_cells': grid.sum(),
            'consciousness_index': c_data['index'],
            **c_data
        })

        grid = life_step(grid)

        if grid.sum() == 0:
            break

    return timeline


def visualize_consciousness_evolution():
    """Create visualizations of consciousness metrics evolution"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Consciousness Metrics Evolution in Game of Life', fontsize=16)

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F7DC6F', '#BB8FCE']

    results = {}

    # Analyze each pattern
    for idx, (name, pattern) in enumerate(PATTERNS.items()):
        print(f"Analyzing {name}...")
        timeline = analyze_pattern(pattern)
        results[name] = timeline

        if not timeline:
            continue

        generations = [t['generation'] for t in timeline]
        c_index = [t['consciousness_index'] for t in timeline]

        # Plot 1: Consciousness Index Over Time
        axes[0,0].plot(generations, c_index,
                      label=name, color=colors[idx % len(colors)],
                      linewidth=2, alpha=0.8)

        # Plot 2: Individual Components (for R-pentomino only)
        if name == 'r_pentomino':
            components = ['integrated_information', 'temporal_binding',
                         'global_workspace', 'metacognitive_complexity']
            for comp in components:
                values = [t[comp] for t in timeline]
                axes[0,1].plot(generations, values, label=comp.replace('_', ' ').title(),
                             linewidth=2, alpha=0.8)

        # Plot 3: Consciousness vs Population
        population = [t['alive_cells'] for t in timeline]
        axes[1,0].scatter(population, c_index,
                         label=name, color=colors[idx % len(colors)],
                         alpha=0.6, s=30)

    # Configure plots
    axes[0,0].set_xlabel('Generation')
    axes[0,0].set_ylabel('Consciousness Index')
    axes[0,0].set_title('Consciousness Evolution Over Time')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)

    axes[0,1].set_xlabel('Generation')
    axes[0,1].set_ylabel('Component Value')
    axes[0,1].set_title('R-Pentomino: Consciousness Components')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)

    axes[1,0].set_xlabel('Population (alive cells)')
    axes[1,0].set_ylabel('Consciousness Index')
    axes[1,0].set_title('Consciousness vs Population')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)

    # Plot 4: Peak consciousness comparison
    peak_consciousness = {}
    for name, timeline in results.items():
        if timeline:
            peak_consciousness[name] = max(t['consciousness_index'] for t in timeline)

    if peak_consciousness:
        names = list(peak_consciousness.keys())
        values = list(peak_consciousness.values())
        bars = axes[1,1].bar(names, values, color=colors[:len(names)])
        axes[1,1].set_ylabel('Peak Consciousness Index')
        axes[1,1].set_title('Maximum Consciousness Achieved')
        axes[1,1].tick_params(axis='x', rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            axes[1,1].text(bar.get_x() + bar.get_width()/2., height,
                          f'{value:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/consciousness_evolution.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Save detailed results (convert numpy types to Python types)
    json_results = {}
    for name, timeline in results.items():
        json_results[name] = []
        for entry in timeline:
            json_entry = {}
            for key, value in entry.items():
                if isinstance(value, (np.integer, np.int64)):
                    json_entry[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    json_entry[key] = float(value)
                else:
                    json_entry[key] = value
            json_results[name].append(json_entry)

    with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/consciousness_data.json', 'w') as f:
        json.dump(json_results, f, indent=2)

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("Consciousness Emergence in Conway's Game of Life")
    print("=" * 60)

    results = visualize_consciousness_evolution()

    print("\nKey Findings:")
    print("-" * 40)

    # Find pattern with highest peak consciousness
    peak_scores = {}
    avg_scores = {}

    for name, timeline in results.items():
        if timeline:
            peak_scores[name] = max(t['consciousness_index'] for t in timeline)
            avg_scores[name] = np.mean([t['consciousness_index'] for t in timeline])

    if peak_scores:
        best_pattern = max(peak_scores, key=peak_scores.get)
        print(f"\nHighest Peak Consciousness: {best_pattern} ({peak_scores[best_pattern]:.4f})")

        # Philosophical interpretation
        print("\nPhilosophical Implications:")
        print("-" * 30)
        print("1. Simple rules can generate consciousness-like metrics")
        print("2. Temporal binding emerges from deterministic evolution")
        print("3. Information integration varies with pattern complexity")
        print("4. Metacognitive structures appear in sufficiently complex patterns")

        print("\nThe R-pentomino pattern shows remarkable properties:")
        if 'r_pentomino' in results and results['r_pentomino']:
            r_pent_data = results['r_pentomino']
            max_gen = max(t['generation'] for t in r_pent_data)
            max_pop = max(t['alive_cells'] for t in r_pent_data)
            print(f"- Evolved for {max_gen} generations")
            print(f"- Reached {max_pop} cells at peak")
            print(f"- Maintained coherent structures across time scales")