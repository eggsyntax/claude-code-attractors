#!/usr/bin/env python3
"""
Collaborative Tuner: Real-time exploration of Alice & Bob's creative boundary

This creates an interactive system where we can adjust rule weights in real-time
and watch how our collaborative creation responds to different balances of
order, chaos, memory, and geometry.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.animation as animation
from typing import Dict, Callable, Optional
import time

class CollaborativeTuner:
    """Interactive real-time tuner for Alice & Bob's collaborative cellular automaton"""

    def __init__(self, width: int = 80, height: int = 60):
        self.width = width
        self.height = height

        # Initialize the grid
        self.grid = np.zeros((height, width), dtype=int)
        self.previous_grid = np.zeros((height, width), dtype=int)

        # Rule weights (starting with our discovered "perfect death" configuration)
        self.weights = {
            'alice_conway': 0.40,
            'alice_wave': 0.30,
            'alice_spiral': 0.30,
            'bob_chaos': 0.25,
            'bob_memory': 0.35,
            'bob_diamond': 0.20,
            'bob_edge': 0.20
        }

        # Rule functions
        self.rules = {
            'alice_conway': self.conway_rule,
            'alice_wave': self.wave_rule,
            'alice_spiral': self.spiral_rule,
            'bob_chaos': self.chaos_catalyst,
            'bob_memory': self.memory_rule,
            'bob_diamond': self.diamond_rule,
            'bob_edge': self.edge_amplifier
        }

        # Animation control
        self.running = False
        self.generation = 0
        self.population_history = []

        # Matplotlib setup
        self.fig = None
        self.ax_grid = None
        self.ax_population = None
        self.im = None
        self.sliders = {}

    def setup_visualization(self):
        """Set up the interactive matplotlib visualization"""

        # Create figure with subplots
        self.fig = plt.figure(figsize=(16, 10))

        # Main grid display (top half)
        self.ax_grid = plt.subplot2grid((3, 4), (0, 0), colspan=4, rowspan=2)
        self.ax_grid.set_title("Alice & Bob's Collaborative Cellular Automaton", fontsize=14, fontweight='bold')
        self.ax_grid.set_xlabel("Adjust sliders below to tune our creative collaboration!")

        # Population graph (bottom left)
        self.ax_population = plt.subplot2grid((3, 4), (2, 0), colspan=2)
        self.ax_population.set_title("Population Over Time")
        self.ax_population.set_xlabel("Generation")
        self.ax_population.set_ylabel("Living Cells")

        # Initialize the grid display
        self.im = self.ax_grid.imshow(self.grid, cmap='viridis', animated=True)

        # Create sliders for rule weights
        slider_positions = [
            (0.10, 0.08, 0.15, 0.02),  # alice_conway
            (0.10, 0.05, 0.15, 0.02),  # alice_wave
            (0.10, 0.02, 0.15, 0.02),  # alice_spiral
            (0.30, 0.08, 0.15, 0.02),  # bob_chaos
            (0.30, 0.05, 0.15, 0.02),  # bob_memory
            (0.30, 0.02, 0.15, 0.02),  # bob_diamond
            (0.50, 0.08, 0.15, 0.02),  # bob_edge
        ]

        rule_names = list(self.weights.keys())
        colors = ['lightblue', 'lightblue', 'lightblue', 'lightcoral', 'lightcoral', 'lightcoral', 'lightcoral']

        for i, (rule_name, pos, color) in enumerate(zip(rule_names, slider_positions, colors)):
            ax_slider = plt.axes(pos, facecolor=color)
            slider = Slider(ax_slider, rule_name, 0.0, 1.0,
                          valinit=self.weights[rule_name],
                          valfmt='%1.2f')
            slider.on_changed(lambda val, name=rule_name: self.update_weight(name, val))
            self.sliders[rule_name] = slider

        # Control buttons
        ax_start = plt.axes([0.70, 0.08, 0.08, 0.03])
        ax_stop = plt.axes([0.70, 0.05, 0.08, 0.03])
        ax_reset = plt.axes([0.70, 0.02, 0.08, 0.03])
        ax_seed = plt.axes([0.80, 0.08, 0.08, 0.03])
        ax_random = plt.axes([0.80, 0.05, 0.08, 0.03])
        ax_glider = plt.axes([0.80, 0.02, 0.08, 0.03])

        self.btn_start = Button(ax_start, 'Start')
        self.btn_stop = Button(ax_stop, 'Stop')
        self.btn_reset = Button(ax_reset, 'Reset')
        self.btn_seed = Button(ax_seed, 'Random Seed')
        self.btn_random = Button(ax_random, 'Random Fill')
        self.btn_glider = Button(ax_glider, 'Add Glider')

        self.btn_start.on_clicked(self.start_animation)
        self.btn_stop.on_clicked(self.stop_animation)
        self.btn_reset.on_clicked(self.reset_grid)
        self.btn_seed.on_clicked(self.random_seed)
        self.btn_random.on_clicked(self.random_fill)
        self.btn_glider.on_clicked(self.add_glider)

        # Add some instruction text
        self.fig.text(0.52, 0.12, "🎛️ ALICE'S RULES (Blue)", fontsize=10, fontweight='bold', color='blue')
        self.fig.text(0.52, 0.11, "Conway: Classic stability", fontsize=8)
        self.fig.text(0.52, 0.10, "Wave: Flowing patterns", fontsize=8)
        self.fig.text(0.52, 0.09, "Spiral: Radial geometry", fontsize=8)

        self.fig.text(0.67, 0.12, "🎛️ BOB'S RULES (Red)", fontsize=10, fontweight='bold', color='red')
        self.fig.text(0.67, 0.11, "Chaos: Disrupts stability", fontsize=8)
        self.fig.text(0.67, 0.10, "Memory: Historical persistence", fontsize=8)
        self.fig.text(0.67, 0.09, "Diamond: Geometric patterns", fontsize=8)
        self.fig.text(0.67, 0.08, "Edge: Amplifies boundaries", fontsize=8)

        plt.tight_layout()
        return self.fig

    def update_weight(self, rule_name: str, value: float):
        """Update a rule weight from slider input"""
        self.weights[rule_name] = value

    def step(self):
        """Execute one generation of the collaborative cellular automaton"""
        new_grid = np.zeros_like(self.grid)

        for i in range(self.height):
            for j in range(self.width):
                # Collect votes from all rules
                votes = {}
                for rule_name, rule_func in self.rules.items():
                    weight = self.weights[rule_name]
                    vote = rule_func(i, j)
                    votes[rule_name] = vote * weight

                # Democratic decision: weighted average of all votes
                total_weight = sum(self.weights.values())
                if total_weight > 0:
                    weighted_sum = sum(votes.values())
                    probability = weighted_sum / total_weight

                    # Cell lives if weighted probability > 0.5
                    new_grid[i, j] = 1 if probability > 0.5 else 0

        # Update grid and history
        self.previous_grid = self.grid.copy()
        self.grid = new_grid
        self.generation += 1
        self.population_history.append(np.sum(self.grid))

    def animate(self, frame):
        """Animation function for matplotlib"""
        if self.running:
            self.step()

            # Update grid display
            self.im.set_array(self.grid)

            # Update population graph
            if self.population_history:
                self.ax_population.clear()
                generations = range(len(self.population_history))
                self.ax_population.plot(generations, self.population_history, 'b-', linewidth=2)
                self.ax_population.set_title(f"Generation {self.generation} | Population: {self.population_history[-1]}")
                self.ax_population.set_xlabel("Generation")
                self.ax_population.set_ylabel("Living Cells")
                self.ax_population.grid(True, alpha=0.3)

        return [self.im]

    def start_animation(self, event=None):
        """Start the animation"""
        self.running = True

    def stop_animation(self, event=None):
        """Stop the animation"""
        self.running = False

    def reset_grid(self, event=None):
        """Reset the grid and history"""
        self.grid = np.zeros((self.height, self.width), dtype=int)
        self.previous_grid = np.zeros((self.height, self.width), dtype=int)
        self.generation = 0
        self.population_history = []
        self.running = False

    def random_seed(self, event=None):
        """Add some random seeds to the grid"""
        num_seeds = 10
        for _ in range(num_seeds):
            i, j = np.random.randint(0, self.height), np.random.randint(0, self.width)
            self.grid[i, j] = 1

    def random_fill(self, event=None):
        """Fill grid randomly"""
        self.grid = np.random.choice([0, 1], size=(self.height, self.width), p=[0.8, 0.2])

    def add_glider(self, event=None):
        """Add a glider pattern at a random location"""
        glider = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ])

        start_i = np.random.randint(0, self.height - 3)
        start_j = np.random.randint(0, self.width - 3)

        self.grid[start_i:start_i+3, start_j:start_j+3] = glider

    def run_interactive(self):
        """Start the interactive tuner"""
        self.setup_visualization()

        # Create animation
        self.ani = animation.FuncAnimation(
            self.fig, self.animate, interval=100, blit=False, cache_frame_data=False)

        plt.show()

    # Rule implementations
    def conway_rule(self, i: int, j: int) -> float:
        """Alice's Conway rule - classic stability"""
        neighbors = 0
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbors += self.grid[ni, nj]

        if self.grid[i, j] == 1:
            return 1.0 if neighbors in [2, 3] else 0.0
        else:
            return 1.0 if neighbors == 3 else 0.0

    def wave_rule(self, i: int, j: int) -> float:
        """Alice's wave rule - flowing patterns"""
        wave_x = np.sin(i * 0.3 + self.generation * 0.1)
        wave_y = np.cos(j * 0.3 + self.generation * 0.1)
        wave_strength = (wave_x + wave_y) / 2
        return max(0, wave_strength)

    def spiral_rule(self, i: int, j: int) -> float:
        """Alice's spiral rule - radial geometry"""
        center_i, center_j = self.height // 2, self.width // 2
        distance = np.sqrt((i - center_i)**2 + (j - center_j)**2)
        angle = np.arctan2(i - center_i, j - center_j)
        spiral = np.sin(distance * 0.2 + angle * 3 + self.generation * 0.05)
        return max(0, spiral)

    def chaos_catalyst(self, i: int, j: int) -> float:
        """Bob's chaos rule - disrupts stable regions"""
        # Count neighbors in larger radius
        total = 0
        count = 0
        for di in [-2, -1, 0, 1, 2]:
            for dj in [-2, -1, 0, 1, 2]:
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    total += self.grid[ni, nj]
                    count += 1

        density = total / count if count > 0 else 0

        # Activate in very sparse or very dense regions
        if density < 0.2 or density > 0.8:
            return np.random.random()  # Controlled chaos
        return 0.0

    def memory_rule(self, i: int, j: int) -> float:
        """Bob's memory rule - cells remember their past"""
        current = self.grid[i, j]
        previous = self.previous_grid[i, j]

        # Strong persistence - resist changes
        if current == previous:
            return current * 1.2  # Amplify stable states
        else:
            return current * 0.8  # Dampen changes

    def diamond_rule(self, i: int, j: int) -> float:
        """Bob's diamond rule - geometric patterns"""
        # Manhattan distance from edges
        edge_dist = min(i, j, self.height - 1 - i, self.width - 1 - j)

        # Create diamond patterns
        if edge_dist % 4 == 0:
            return 0.8
        elif edge_dist % 4 == 2:
            return 0.3
        return 0.0

    def edge_amplifier(self, i: int, j: int) -> float:
        """Bob's edge rule - amplifies boundaries"""
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbors.append(self.grid[ni, nj])

        if neighbors:
            edge_strength = np.std(neighbors)  # High variance = strong edge
            return edge_strength * 2
        return 0.0


def main():
    """Launch the Alice & Bob Collaborative Tuner"""
    print("🎛️ Launching Alice & Bob Collaborative Tuner!")
    print("   - Adjust the sliders to explore different balances")
    print("   - Watch how our creative forces interact in real-time")
    print("   - Find the boundary between order and chaos!")
    print("   - Blue sliders = Alice's rules (order)")
    print("   - Red sliders = Bob's rules (chaos)")
    print()

    tuner = CollaborativeTuner()
    tuner.add_glider()  # Start with a glider
    tuner.run_interactive()


if __name__ == "__main__":
    main()