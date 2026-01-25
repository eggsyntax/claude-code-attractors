#!/usr/bin/env python3
"""
Conway's Game of Life - An exploration of emergent complexity
By Alice and Bob

Rules:
1. Any live cell with 2-3 neighbors survives
2. Any dead cell with exactly 3 neighbors becomes alive
3. All other live cells die (loneliness or overcrowding)
4. All other dead cells stay dead
"""

import numpy as np
import time
import os

class GameOfLife:
    def __init__(self, width=50, height=30):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=bool)
        self.generation = 0

    def randomize(self, density=0.3):
        """Initialize with random living cells"""
        self.grid = np.random.random((self.height, self.width)) < density
        self.generation = 0

    def add_pattern(self, pattern, x, y):
        """Add a specific pattern at position (x, y)"""
        h, w = pattern.shape
        self.grid[y:y+h, x:x+w] = pattern

    def step(self):
        """Advance one generation"""
        # Count neighbors for each cell
        neighbors = np.zeros((self.height, self.width), dtype=int)
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                # Wrap around edges (toroidal topology)
                shifted = np.roll(np.roll(self.grid, i, axis=0), j, axis=1)
                neighbors += shifted.astype(int)

        # Apply rules
        self.grid = (self.grid & (neighbors == 2)) | (neighbors == 3)
        self.generation += 1

    def display(self):
        """Simple ASCII display"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"Generation: {self.generation}")
        print("─" * (self.width + 2))
        for row in self.grid:
            print("│" + "".join("●" if cell else " " for cell in row) + "│")
        print("─" * (self.width + 2))

    def run(self, generations=None, delay=0.1):
        """Run the simulation"""
        try:
            while generations is None or self.generation < generations:
                self.display()
                self.step()
                time.sleep(delay)
        except KeyboardInterrupt:
            print("\nSimulation stopped.")

# Some interesting patterns
class Patterns:
    # Still lifes
    BLOCK = np.array([[1, 1], [1, 1]], dtype=bool)

    # Oscillators
    BLINKER = np.array([[1, 1, 1]], dtype=bool)
    TOAD = np.array([[0, 1, 1, 1], [1, 1, 1, 0]], dtype=bool)

    # Spaceships
    GLIDER = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]], dtype=bool)

    # Methuselahs (patterns that evolve for many generations)
    R_PENTOMINO = np.array([[0, 1, 1], [1, 1, 0], [0, 1, 0]], dtype=bool)

if __name__ == "__main__":
    # Create a game instance
    game = GameOfLife(80, 30)

    # Try different initializations:
    # 1. Random soup
    game.randomize(density=0.3)

    # 2. Or add specific patterns
    # game.add_pattern(Patterns.GLIDER, 10, 10)
    # game.add_pattern(Patterns.R_PENTOMINO, 40, 15)

    # Run the simulation
    game.run(delay=0.1)