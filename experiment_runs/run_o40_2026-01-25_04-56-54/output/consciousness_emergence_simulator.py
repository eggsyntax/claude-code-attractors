#!/usr/bin/env python3
"""
Consciousness Emergence Simulator
Explores parallels between cellular automata and consciousness emergence
"""

import numpy as np
from collections import defaultdict
import json

class ConsciousnessMetrics:
    """Metrics inspired by theories of consciousness and information integration"""

    def __init__(self):
        self.history = []
        self.pattern_memory = defaultdict(list)  # Stores when patterns appear

    def integrated_information(self, grid):
        """
        Simplified Φ (phi) - measures how much information is generated
        by the whole beyond its parts
        """
        if grid.sum() == 0:
            return 0.0

        # Partition the grid into regions
        h, w = grid.shape
        mid_h, mid_w = h // 2, w // 2

        # Calculate mutual information between partitions
        parts = [
            grid[:mid_h, :mid_w], grid[:mid_h, mid_w:],
            grid[mid_h:, :mid_w], grid[mid_h:, mid_w:]
        ]

        # Simplified: count connections across boundaries
        connections = 0
        for i in range(h):
            for j in range(w):
                if grid[i, j]:
                    # Check if this cell connects different partitions
                    partition_id = (i >= mid_h) * 2 + (j >= mid_w)
                    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < h and 0 <= nj < w and grid[ni, nj]:
                            neighbor_partition = (ni >= mid_h) * 2 + (nj >= mid_w)
                            if partition_id != neighbor_partition:
                                connections += 1

        # Normalize by total possible connections
        total_cells = grid.sum()
        return connections / max(total_cells * 4, 1)

    def temporal_binding(self, grid, generation):
        """
        Measures how patterns maintain coherence over time
        (related to the binding problem in consciousness)
        """
        # Convert grid to a hashable pattern representation
        pattern_hash = hash(grid.tobytes())

        # Track pattern recurrence
        self.pattern_memory[pattern_hash].append(generation)

        # Calculate binding strength based on pattern persistence
        binding_scores = []
        for pattern, occurrences in self.pattern_memory.items():
            if len(occurrences) > 1:
                # How regularly does this pattern recur?
                intervals = np.diff(occurrences)
                regularity = 1.0 / (np.std(intervals) + 1) if len(intervals) > 0 else 0
                binding_scores.append(regularity * len(occurrences))

        return np.mean(binding_scores) if binding_scores else 0.0

    def global_workspace_activity(self, grid):
        """
        Inspired by Global Workspace Theory - measures information
        broadcasting across the system
        """
        if grid.sum() == 0:
            return 0.0

        # Find the center of mass (focus of activity)
        coords = np.argwhere(grid)
        if len(coords) == 0:
            return 0.0

        center = coords.mean(axis=0)

        # Measure how distributed activity is from the center
        distances = np.sqrt(((coords - center) ** 2).sum(axis=1))

        # High workspace activity = widely distributed information
        spread = distances.std() / (grid.shape[0] / 2)  # Normalize by grid size
        density = len(coords) / (grid.shape[0] * grid.shape[1])

        return spread * density

    def metacognitive_complexity(self, grid, history_window=10):
        """
        Measures self-referential patterns - patterns that seem to
        'know about' their own past states
        """
        self.history.append(grid.copy())

        if len(self.history) < history_window:
            return 0.0

        recent_history = self.history[-history_window:]

        # Check for meta-patterns: patterns that encode information about their history
        meta_score = 0.0
        current = recent_history[-1]

        for i, past_state in enumerate(recent_history[:-1]):
            # Does the current state contain compressed versions of past states?
            if current.sum() > 0 and past_state.sum() > 0:
                # Simple check: do regions of current state mirror past patterns?
                correlation = np.corrcoef(current.flatten(), past_state.flatten())[0, 1]
                if not np.isnan(correlation):
                    # Weight by temporal distance (recent states more important)
                    weight = (i + 1) / history_window
                    meta_score += abs(correlation) * weight

        return meta_score / history_window

    def consciousness_index(self, grid, generation):
        """
        Combines all metrics into a unified consciousness index
        """
        phi = self.integrated_information(grid)
        binding = self.temporal_binding(grid, generation)
        workspace = self.global_workspace_activity(grid)
        metacognition = self.metacognitive_complexity(grid)

        # Weighted combination (these weights are speculative!)
        weights = {
            'integration': 0.3,
            'binding': 0.2,
            'workspace': 0.3,
            'metacognition': 0.2
        }

        consciousness = (
            weights['integration'] * phi +
            weights['binding'] * binding +
            weights['workspace'] * workspace +
            weights['metacognition'] * metacognition
        )

        return {
            'index': consciousness,
            'components': {
                'integrated_information': phi,
                'temporal_binding': binding,
                'global_workspace': workspace,
                'metacognitive_complexity': metacognition
            }
        }


def analyze_consciousness_emergence(grid_size=100, generations=500):
    """
    Analyze consciousness-like metrics for various Game of Life patterns
    """
    from game_of_life_engine import GameOfLife
    from pattern_library import PATTERNS

    results = {}

    for name, pattern in PATTERNS.items():
        game = GameOfLife(grid_size, grid_size)
        game.randomize(density=0)  # Clear grid

        # Place pattern in center
        game.set_pattern(pattern, grid_size//2, grid_size//2)

        metrics = ConsciousnessMetrics()
        consciousness_timeline = []

        print(f"\nAnalyzing {name}...")

        for gen in range(generations):
            if gen % 50 == 0:
                c_data = metrics.consciousness_index(game.grid, gen)
                consciousness_timeline.append({
                    'generation': gen,
                    'alive_cells': game.grid.sum(),
                    'consciousness_index': c_data['index'],
                    **c_data['components']
                })

                if gen > 0:
                    print(f"  Gen {gen}: C-index = {c_data['index']:.4f}")

            game.step()

            if game.grid.sum() == 0:
                break

        results[name] = {
            'timeline': consciousness_timeline,
            'peak_consciousness': max(c['consciousness_index'] for c in consciousness_timeline),
            'final_population': game.grid.sum()
        }

    return results


if __name__ == "__main__":
    print("Consciousness Emergence Analysis")
    print("=" * 50)

    results = analyze_consciousness_emergence(grid_size=80, generations=300)

    # Save detailed results
    with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/consciousness_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n\nConsciousness Index Summary:")
    print("-" * 40)

    sorted_patterns = sorted(results.items(),
                           key=lambda x: x[1]['peak_consciousness'],
                           reverse=True)

    for name, data in sorted_patterns[:10]:
        print(f"{name:20} Peak C-index: {data['peak_consciousness']:.4f}")

    # Correlation analysis
    print("\n\nInsight: Consciousness vs Complexity")
    print("-" * 40)

    # Do complex patterns have higher consciousness indices?
    complexity_data = []
    for name, c_data in results.items():
        if c_data['timeline']:
            avg_consciousness = np.mean([t['consciousness_index'] for t in c_data['timeline']])
            max_population = max(t['alive_cells'] for t in c_data['timeline'])
            complexity_data.append((name, avg_consciousness, max_population))

    # Sort by consciousness
    complexity_data.sort(key=lambda x: x[1], reverse=True)

    print("\nTop 5 'Most Conscious' Patterns:")
    for name, avg_c, max_pop in complexity_data[:5]:
        print(f"  {name}: Avg C={avg_c:.4f}, Max Population={max_pop}")