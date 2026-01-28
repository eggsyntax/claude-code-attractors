#!/usr/bin/env python3
"""
Analyzer for Conway's Game of Life - Exploring emergent properties
"""

import numpy as np
from game_of_life import GameOfLife, Patterns
import matplotlib.pyplot as plt
from collections import deque

class LifeAnalyzer:
    def __init__(self, game):
        self.game = game
        self.history = deque(maxlen=1000)  # Keep last 1000 states
        self.population_history = []
        self.entropy_history = []
        self.pattern_counts = {}

    def analyze_generation(self):
        """Analyze current generation"""
        state = self.game.grid.copy()
        self.history.append(state)

        # Population
        population = np.sum(state)
        self.population_history.append(population)

        # Spatial entropy (measure of randomness/organization)
        if population > 0:
            # Calculate local density variance as proxy for organization
            kernel = np.ones((3, 3)) / 9
            from scipy.signal import convolve2d
            local_density = convolve2d(state.astype(float), kernel, mode='same', boundary='wrap')
            entropy = np.var(local_density)
            self.entropy_history.append(entropy)

        return {
            'population': population,
            'density': population / (self.game.width * self.game.height),
            'generation': self.game.generation
        }

    def detect_period(self, max_period=20):
        """Detect if the pattern is periodic"""
        if len(self.history) < max_period:
            return None

        current_state = self.history[-1]
        for period in range(1, min(max_period, len(self.history))):
            if np.array_equal(current_state, self.history[-1-period]):
                return period
        return None

    def find_still_lifes(self):
        """Identify stable patterns (still lifes)"""
        if len(self.history) < 2:
            return []

        # Find cells that haven't changed
        unchanged = np.array_equal(self.history[-1], self.history[-2])
        if unchanged:
            return self._extract_connected_components(self.history[-1])
        return []

    def _extract_connected_components(self, grid):
        """Extract individual connected patterns"""
        from scipy.ndimage import label
        labeled, num_features = label(grid)
        patterns = []
        for i in range(1, num_features + 1):
            pattern_mask = (labeled == i)
            patterns.append(pattern_mask)
        return patterns

    def plot_analysis(self):
        """Create visualization of analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Population over time
        axes[0, 0].plot(self.population_history)
        axes[0, 0].set_title("Population Over Time")
        axes[0, 0].set_xlabel("Generation")
        axes[0, 0].set_ylabel("Living Cells")

        # Entropy over time
        if self.entropy_history:
            axes[0, 1].plot(self.entropy_history)
            axes[0, 1].set_title("Spatial Organization")
            axes[0, 1].set_xlabel("Generation")
            axes[0, 1].set_ylabel("Variance (lower = more organized)")

        # Current state heatmap
        axes[1, 0].imshow(self.game.grid, cmap='binary')
        axes[1, 0].set_title(f"Generation {self.game.generation}")

        # Phase space (population vs change in population)
        if len(self.population_history) > 1:
            pop_changes = np.diff(self.population_history)
            axes[1, 1].scatter(self.population_history[:-1], pop_changes, alpha=0.5)
            axes[1, 1].set_title("Phase Space")
            axes[1, 1].set_xlabel("Population")
            axes[1, 1].set_ylabel("Change in Population")

        plt.tight_layout()
        plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/life_analysis.png')
        plt.close()

# Philosophical reflection generator
def generate_reflection(analyzer):
    """Generate philosophical insights based on the simulation"""
    period = analyzer.detect_period()

    reflection = f"""
Reflections on Generation {analyzer.game.generation}:

Population: {analyzer.population_history[-1] if analyzer.population_history else 0}
"""

    if period:
        reflection += f"\nThe system has entered a periodic state with period {period}."
        if period == 1:
            reflection += "\nPerfect stability achieved - a 'still life' configuration."
        else:
            reflection += f"\nAn oscillating pattern - eternal motion within bounds."

    if len(analyzer.population_history) > 10:
        recent_pop = analyzer.population_history[-10:]
        if max(recent_pop) - min(recent_pop) < 5:
            reflection += "\n\nThe system appears to be reaching equilibrium."
        elif np.std(recent_pop) > np.mean(recent_pop) * 0.5:
            reflection += "\n\nChaotic fluctuations persist - far from equilibrium."

    reflection += """

This simple universe, governed by just four rules, demonstrates how:
- Order can emerge from chaos
- Complex patterns arise from simple rules
- Systems can self-organize without external guidance
- Deterministic rules can produce unpredictable outcomes
"""

    return reflection

if __name__ == "__main__":
    # Create and analyze a game
    game = GameOfLife(100, 50)
    analyzer = LifeAnalyzer(game)

    # Start with R-pentomino - a pattern that evolves for 1103 generations
    game.add_pattern(Patterns.R_PENTOMINO, 50, 25)

    # Run for a while, analyzing each step
    for i in range(200):
        analyzer.analyze_generation()
        game.step()

        if i % 50 == 0:
            print(f"Generation {i}: Population = {analyzer.population_history[-1]}")

    # Generate analysis
    analyzer.plot_analysis()

    # Write philosophical reflection
    with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/emergence_reflection.txt', 'w') as f:
        f.write(generate_reflection(analyzer))

    print("\nAnalysis complete! Check life_analysis.png and emergence_reflection.txt")