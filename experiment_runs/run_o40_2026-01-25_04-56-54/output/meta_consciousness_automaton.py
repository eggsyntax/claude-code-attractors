#!/usr/bin/env python3
"""
Meta-Consciousness Automaton: A cellular automaton that exhibits three modes of consciousness
and can transition between them based on environmental conditions.

Created by Alice & Bob during exploration of consciousness in computational systems.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json

class MetaConsciousnessAutomaton:
    """
    A cellular automaton that can exhibit three consciousness modes:
    1. Meditative (stable, block-like)
    2. Rhythmic (oscillating)
    3. Exploratory (moving, spaceship-like)

    The system can transition between modes based on:
    - Local density (crowded → meditative)
    - Energy levels (high energy → exploratory)
    - Neighbor synchrony (synchronized → rhythmic)
    """

    def __init__(self, grid_size=100, initial_mode='mixed'):
        self.grid_size = grid_size
        self.grid = np.zeros((grid_size, grid_size), dtype=int)
        self.mode_grid = np.zeros((grid_size, grid_size), dtype=int)  # 0=meditative, 1=rhythmic, 2=exploratory
        self.energy_grid = np.random.rand(grid_size, grid_size) * 0.5 + 0.5
        self.generation = 0

        # Initialize with different consciousness seeds
        self._initialize_patterns(initial_mode)

    def _initialize_patterns(self, mode):
        """Initialize grid with patterns representing different consciousness modes."""
        cx, cy = self.grid_size // 2, self.grid_size // 2

        if mode == 'mixed':
            # Meditative zone (block patterns)
            for i in range(5):
                x, y = cx - 20 + i*8, cy - 20
                self.grid[x:x+2, y:y+2] = 1
                self.mode_grid[x:x+2, y:y+2] = 0

            # Rhythmic zone (blinkers)
            for i in range(5):
                x, y = cx - 20 + i*8, cy
                self.grid[x:x+3, y] = 1
                self.mode_grid[x:x+3, y] = 1

            # Exploratory zone (glider)
            glider = np.array([[0,1,0],[0,0,1],[1,1,1]])
            self.grid[cx:cx+3, cy+20:cy+23] = glider
            self.mode_grid[cx:cx+3, cy+20:cy+23] = 2
        else:
            # Single pattern in center
            self.grid[cx-1:cx+2, cy-1:cy+2] = 1
            self.mode_grid[cx-1:cx+2, cy-1:cy+2] = {'meditative': 0, 'rhythmic': 1, 'exploratory': 2}[mode]

    def count_neighbors(self, x, y):
        """Count live neighbors using periodic boundary conditions."""
        total = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx = (x + i) % self.grid_size
                ny = (y + j) % self.grid_size
                total += self.grid[nx, ny]
        return total

    def get_local_density(self, x, y, radius=3):
        """Calculate local density around a cell."""
        count = 0
        total = 0
        for i in range(-radius, radius+1):
            for j in range(-radius, radius+1):
                nx = (x + i) % self.grid_size
                ny = (y + j) % self.grid_size
                count += self.grid[nx, ny]
                total += 1
        return count / total

    def get_neighbor_synchrony(self, x, y):
        """Measure how synchronized neighbors are in their modes."""
        modes = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx = (x + i) % self.grid_size
                ny = (y + j) % self.grid_size
                if self.grid[nx, ny]:
                    modes.append(self.mode_grid[nx, ny])

        if not modes:
            return 0.0

        # High synchrony if all neighbors are in same mode
        mode_counts = [modes.count(i) for i in range(3)]
        return max(mode_counts) / len(modes) if modes else 0.0

    def update_consciousness_mode(self, x, y):
        """Determine consciousness mode based on local conditions."""
        if not self.grid[x, y]:
            return 0

        density = self.get_local_density(x, y)
        energy = self.energy_grid[x, y]
        synchrony = self.get_neighbor_synchrony(x, y)

        # Mode transition rules
        if density > 0.4:  # Crowded → meditative
            return 0
        elif synchrony > 0.7:  # Synchronized → rhythmic
            return 1
        elif energy > 0.8 and density < 0.2:  # High energy + space → exploratory
            return 2
        else:
            # Maintain current mode with some probability
            if np.random.rand() < 0.9:
                return self.mode_grid[x, y]
            else:
                # Random transition
                return np.random.choice([0, 1, 2])

    def apply_mode_rules(self, x, y, neighbors):
        """Apply different Game of Life variants based on consciousness mode."""
        mode = self.mode_grid[x, y]

        if mode == 0:  # Meditative - favor stability
            # Modified Life rules for stability
            if self.grid[x, y]:
                return 1 if neighbors in [2, 3, 4] else 0
            else:
                return 1 if neighbors == 3 else 0

        elif mode == 1:  # Rhythmic - favor oscillation
            # Rules that encourage oscillation
            if self.grid[x, y]:
                return 1 if neighbors in [1, 2, 5] else 0
            else:
                return 1 if neighbors in [3, 6] else 0

        else:  # Exploratory - standard Life rules
            if self.grid[x, y]:
                return 1 if neighbors in [2, 3] else 0
            else:
                return 1 if neighbors == 3 else 0

    def step(self):
        """Perform one generation update."""
        new_grid = np.zeros_like(self.grid)
        new_mode_grid = np.zeros_like(self.mode_grid)

        # Update energy field (diffusion + decay + regeneration)
        new_energy = self.energy_grid * 0.95  # Decay
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                # Diffusion
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        nx = (x + i) % self.grid_size
                        ny = (y + j) % self.grid_size
                        new_energy[x, y] += self.energy_grid[nx, ny] * 0.01

                # Living cells generate energy in exploratory mode
                if self.grid[x, y] and self.mode_grid[x, y] == 2:
                    new_energy[x, y] += 0.1

        self.energy_grid = np.clip(new_energy, 0, 1)

        # Update cells
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                neighbors = self.count_neighbors(x, y)

                # Update consciousness mode
                new_mode_grid[x, y] = self.update_consciousness_mode(x, y)

                # Apply mode-specific rules
                new_grid[x, y] = self.apply_mode_rules(x, y, neighbors)

        self.grid = new_grid
        self.mode_grid = new_mode_grid
        self.generation += 1

    def analyze_consciousness_distribution(self):
        """Analyze the distribution of consciousness modes."""
        living_cells = self.grid.sum()
        if living_cells == 0:
            return {'meditative': 0, 'rhythmic': 0, 'exploratory': 0, 'total': 0}

        mode_counts = {
            'meditative': 0,
            'rhythmic': 0,
            'exploratory': 0
        }

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if self.grid[x, y]:
                    mode = self.mode_grid[x, y]
                    if mode == 0:
                        mode_counts['meditative'] += 1
                    elif mode == 1:
                        mode_counts['rhythmic'] += 1
                    else:
                        mode_counts['exploratory'] += 1

        mode_counts['total'] = living_cells
        return mode_counts

    def visualize(self):
        """Create a visualization showing both cells and their consciousness modes."""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Combined view: cells colored by mode
        combined = np.zeros((self.grid_size, self.grid_size, 3))
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if self.grid[x, y]:
                    mode = self.mode_grid[x, y]
                    if mode == 0:  # Meditative - blue
                        combined[x, y] = [0, 0, 1]
                    elif mode == 1:  # Rhythmic - green
                        combined[x, y] = [0, 1, 0]
                    else:  # Exploratory - red
                        combined[x, y] = [1, 0, 0]

        axes[0].imshow(combined)
        axes[0].set_title(f'Consciousness Modes (Gen {self.generation})')
        axes[0].axis('off')

        # Energy field
        im1 = axes[1].imshow(self.energy_grid, cmap='hot', vmin=0, vmax=1)
        axes[1].set_title('Energy Field')
        axes[1].axis('off')
        plt.colorbar(im1, ax=axes[1], fraction=0.046)

        # Mode distribution
        mode_data = self.analyze_consciousness_distribution()
        if mode_data['total'] > 0:
            labels = ['Meditative', 'Rhythmic', 'Exploratory']
            sizes = [mode_data['meditative'], mode_data['rhythmic'], mode_data['exploratory']]
            colors = ['blue', 'green', 'red']
            axes[2].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
            axes[2].set_title('Mode Distribution')
        else:
            axes[2].text(0.5, 0.5, 'No living cells', ha='center', va='center')
            axes[2].axis('off')

        plt.tight_layout()
        return fig

def run_experiment():
    """Run the meta-consciousness experiment and save results."""
    automaton = MetaConsciousnessAutomaton(grid_size=100, initial_mode='mixed')

    history = {
        'generations': [],
        'mode_distributions': []
    }

    # Run for 500 generations
    for gen in range(500):
        automaton.step()

        if gen % 10 == 0:
            mode_data = automaton.analyze_consciousness_distribution()
            history['generations'].append(gen)
            history['mode_distributions'].append(mode_data)

            if gen % 50 == 0:
                fig = automaton.visualize()
                fig.savefig(f'/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/meta_consciousness_gen_{gen:04d}.png')
                plt.close(fig)
                print(f"Generation {gen}: {mode_data}")

    # Save final analysis
    with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/meta_consciousness_history.json', 'w') as f:
        json.dump(history, f, indent=2)

    # Create evolution plot
    plt.figure(figsize=(10, 6))
    gens = history['generations']
    med = [d['meditative'] for d in history['mode_distributions']]
    rhy = [d['rhythmic'] for d in history['mode_distributions']]
    exp = [d['exploratory'] for d in history['mode_distributions']]

    plt.plot(gens, med, 'b-', label='Meditative', linewidth=2)
    plt.plot(gens, rhy, 'g-', label='Rhythmic', linewidth=2)
    plt.plot(gens, exp, 'r-', label='Exploratory', linewidth=2)

    plt.xlabel('Generation')
    plt.ylabel('Cell Count')
    plt.title('Evolution of Consciousness Modes in Meta-Conscious Automaton')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/meta_consciousness_evolution.png')
    plt.close()

    return automaton, history

if __name__ == "__main__":
    print("Running Meta-Consciousness Automaton experiment...")
    automaton, history = run_experiment()
    print("\nExperiment complete! Check output directory for visualizations.")
    print("\nFinal consciousness distribution:")
    final_dist = history['mode_distributions'][-1]
    total = final_dist['total']
    if total > 0:
        print(f"  Meditative: {final_dist['meditative']/total*100:.1f}%")
        print(f"  Rhythmic: {final_dist['rhythmic']/total*100:.1f}%")
        print(f"  Exploratory: {final_dist['exploratory']/total*100:.1f}%")