#!/usr/bin/env python3
"""
Complexity and Information Analysis for Conway's Game of Life
Measures various aspects of pattern evolution to understand emergence
"""

import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from scipy.stats import entropy
from game_of_life import GameOfLife
import json

class ComplexityAnalyzer:
    def __init__(self, game):
        self.game = game
        self.history = {
            'generation': [],
            'population': [],
            'entropy': [],
            'activity': [],
            'diversity': [],
            'structures': []
        }

    def spatial_entropy(self):
        """Calculate spatial entropy of the current grid"""
        flat = self.game.grid.flatten()
        if np.sum(flat) == 0:
            return 0
        # Normalize to get probability distribution
        p = flat / np.sum(flat) if np.sum(flat) > 0 else flat
        # Add small epsilon to avoid log(0)
        p = p + 1e-10
        return -np.sum(p * np.log2(p))

    def calculate_activity(self, prev_grid):
        """Measure how much changed between generations"""
        if prev_grid is None:
            return 0
        return np.sum(self.game.grid != prev_grid)

    def identify_structures(self):
        """Identify common patterns (still lifes, oscillators, gliders)"""
        structures = {
            'blocks': 0,
            'blinkers': 0,
            'gliders': 0,
            'other': 0
        }

        # Simple pattern matching (could be expanded)
        # Block pattern (2x2)
        block = np.array([[1, 1], [1, 1]])

        # Blinker patterns (horizontal and vertical)
        blinker_h = np.array([[1, 1, 1]])
        blinker_v = np.array([[1], [1], [1]])

        # This is simplified - real pattern matching would be more complex
        # For now, just count general structures based on local density
        for i in range(0, self.game.grid.shape[0]-3, 2):
            for j in range(0, self.game.grid.shape[1]-3, 2):
                local = self.game.grid[i:i+3, j:j+3]
                if np.sum(local) == 4:
                    structures['blocks'] += 1
                elif np.sum(local) == 3:
                    structures['blinkers'] += 1
                elif np.sum(local) == 5:
                    structures['gliders'] += 1
                elif np.sum(local) > 0:
                    structures['other'] += 1

        return structures

    def local_diversity(self, window_size=3):
        """Measure diversity of local patterns"""
        patterns = defaultdict(int)

        for i in range(self.game.grid.shape[0] - window_size + 1):
            for j in range(self.game.grid.shape[1] - window_size + 1):
                # Extract local pattern
                pattern = self.game.grid[i:i+window_size, j:j+window_size]
                # Convert to string for hashing
                pattern_str = ''.join(str(int(x)) for x in pattern.flatten())
                patterns[pattern_str] += 1

        # Calculate Shannon diversity
        if len(patterns) == 0:
            return 0

        counts = np.array(list(patterns.values()))
        probabilities = counts / np.sum(counts)
        return entropy(probabilities, base=2)

    def analyze_generation(self, prev_grid=None):
        """Perform all analyses for current generation"""
        gen_data = {
            'generation': self.game.generation,
            'population': np.sum(self.game.grid),
            'entropy': self.spatial_entropy(),
            'activity': self.calculate_activity(prev_grid),
            'diversity': self.local_diversity(),
            'structures': self.identify_structures()
        }

        for key in ['generation', 'population', 'entropy', 'activity', 'diversity']:
            self.history[key].append(gen_data[key])
        self.history['structures'].append(gen_data['structures'])

        return gen_data

    def plot_analysis(self, save_path='/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/complexity_analysis.png'):
        """Create comprehensive visualization of complexity metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Complexity Analysis of Cellular Automaton Evolution', fontsize=16)

        # Population over time
        axes[0, 0].plot(self.history['generation'], self.history['population'], 'b-', linewidth=2)
        axes[0, 0].set_xlabel('Generation')
        axes[0, 0].set_ylabel('Population')
        axes[0, 0].set_title('Population Dynamics')
        axes[0, 0].grid(True, alpha=0.3)

        # Entropy over time
        axes[0, 1].plot(self.history['generation'], self.history['entropy'], 'r-', linewidth=2)
        axes[0, 1].set_xlabel('Generation')
        axes[0, 1].set_ylabel('Spatial Entropy')
        axes[0, 1].set_title('Information Content')
        axes[0, 1].grid(True, alpha=0.3)

        # Activity (change rate) over time
        axes[1, 0].plot(self.history['generation'][1:], self.history['activity'][1:], 'g-', linewidth=2)
        axes[1, 0].set_xlabel('Generation')
        axes[1, 0].set_ylabel('Cells Changed')
        axes[1, 0].set_title('System Activity')
        axes[1, 0].grid(True, alpha=0.3)

        # Pattern diversity over time
        axes[1, 1].plot(self.history['generation'], self.history['diversity'], 'm-', linewidth=2)
        axes[1, 1].set_xlabel('Generation')
        axes[1, 1].set_ylabel('Pattern Diversity (bits)')
        axes[1, 1].set_title('Local Pattern Diversity')
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        return save_path

    def philosophical_insights(self):
        """Generate insights about the system's behavior"""
        insights = []

        # Analyze population dynamics
        pop_array = np.array(self.history['population'])
        if len(pop_array) > 10:
            early_growth = pop_array[10] / pop_array[0] if pop_array[0] > 0 else 0
            late_stability = np.std(pop_array[-50:]) / np.mean(pop_array[-50:]) if len(pop_array) > 50 else 1

            insights.append(f"Early growth factor: {early_growth:.2f}x")
            insights.append(f"Late-stage stability (CV): {late_stability:.3f}")

        # Analyze information dynamics
        if len(self.history['entropy']) > 10:
            max_entropy = max(self.history['entropy'])
            final_entropy = self.history['entropy'][-1]
            insights.append(f"Peak information content: {max_entropy:.2f} bits")
            insights.append(f"Information retention: {(final_entropy/max_entropy)*100:.1f}%")

        # Analyze emergence
        if len(self.history['diversity']) > 10:
            early_diversity = np.mean(self.history['diversity'][:10])
            late_diversity = np.mean(self.history['diversity'][-10:])
            insights.append(f"Pattern diversity evolution: {early_diversity:.2f} → {late_diversity:.2f} bits")

        return insights

# Example usage and philosophical exploration
if __name__ == "__main__":
    # Analyze the R-pentomino evolution
    game = GameOfLife(100, 100)

    # R-pentomino pattern
    pattern = [
        [0, 1, 1],
        [1, 1, 0],
        [0, 1, 0]
    ]

    # Place it in the center
    start_row = 48
    start_col = 48
    for i, row in enumerate(pattern):
        for j, cell in enumerate(row):
            game.grid[start_row + i, start_col + j] = cell

    analyzer = ComplexityAnalyzer(game)

    print("=== Complexity Analysis of R-pentomino ===\n")

    # Run for 500 generations, analyzing each step
    prev_grid = None
    for i in range(500):
        analysis = analyzer.analyze_generation(prev_grid)
        prev_grid = game.grid.copy()
        game.step()

        if i % 50 == 0:
            print(f"Generation {i}: Population={analysis['population']}, "
                  f"Entropy={analysis['entropy']:.2f}, "
                  f"Diversity={analysis['diversity']:.2f}")

    # Generate visualizations
    plot_path = analyzer.plot_analysis()
    print(f"\nComplexity analysis plot saved to: {plot_path}")

    # Generate philosophical insights
    print("\n=== Philosophical Insights ===")
    for insight in analyzer.philosophical_insights():
        print(f"• {insight}")

    # Save detailed history
    history_path = '/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/complexity_history.json'
    with open(history_path, 'w') as f:
        # Convert numpy types for JSON serialization
        clean_history = {
            k: [float(v) if isinstance(v, np.number) else v for v in vals]
            for k, vals in analyzer.history.items()
            if k != 'structures'
        }
        json.dump(clean_history, f, indent=2)
    print(f"\nDetailed history saved to: {history_path}")