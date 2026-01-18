"""
Cellular Automata Framework
============================

A flexible framework for exploring 2D cellular automata with custom rules.
Supports various neighborhood types and rule definitions.

Usage:
    automaton = CellularAutomaton(width=50, height=50, rule=life_rules)
    automaton.randomize(density=0.3)

    for _ in range(100):
        automaton.step()
        automaton.display()

Created by Alice as a starting point for exploring emergence with Bob.
"""

import numpy as np
from typing import Callable, Tuple
import sys


class CellularAutomaton:
    """
    A 2D cellular automaton with customizable rules.

    The grid wraps around at edges (toroidal topology), which prevents
    edge effects and creates more interesting dynamics.
    """

    def __init__(self, width: int, height: int, rule: Callable):
        """
        Initialize the automaton.

        Args:
            width: Width of the grid
            height: Height of the grid
            rule: Function that takes (grid, x, y) and returns new cell state
        """
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.rule = rule
        self.generation = 0

    def randomize(self, density: float = 0.3):
        """Initialize grid with random alive cells at given density."""
        self.grid = (np.random.random((self.height, self.width)) < density).astype(int)
        self.generation = 0

    def set_pattern(self, pattern: np.ndarray, x: int = 0, y: int = 0):
        """Place a specific pattern at position (x, y)."""
        h, w = pattern.shape
        self.grid[y:y+h, x:x+w] = pattern

    def count_neighbors_moore(self, x: int, y: int) -> int:
        """
        Count living neighbors using Moore neighborhood (8 surrounding cells).
        Uses modulo arithmetic for toroidal wrapping.
        """
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                count += self.grid[ny, nx]
        return count

    def count_neighbors_von_neumann(self, x: int, y: int) -> int:
        """Count living neighbors using von Neumann neighborhood (4 cardinal directions)."""
        count = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx = (x + dx) % self.width
            ny = (y + dy) % self.height
            count += self.grid[ny, nx]
        return count

    def step(self):
        """Advance the automaton by one generation."""
        new_grid = np.zeros_like(self.grid)

        for y in range(self.height):
            for x in range(self.width):
                new_grid[y, x] = self.rule(self, x, y)

        self.grid = new_grid
        self.generation += 1

    def display(self, alive_char: str = '█', dead_char: str = ' '):
        """Display the current state using ASCII characters."""
        print(f"\nGeneration {self.generation}")
        print("┌" + "─" * self.width + "┐")
        for row in self.grid:
            print("│" + "".join(alive_char if cell else dead_char for cell in row) + "│")
        print("└" + "─" * self.width + "┘")

    def get_stats(self) -> dict:
        """Return statistics about the current state."""
        alive = np.sum(self.grid)
        total = self.width * self.height
        return {
            'generation': self.generation,
            'alive': alive,
            'density': alive / total,
            'total': total
        }


# ===== RULE DEFINITIONS =====
# Rules are functions that take (automaton, x, y) and return 0 or 1

def life_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    Conway's Game of Life rules:
    - Living cell with 2-3 neighbors survives
    - Dead cell with exactly 3 neighbors becomes alive
    - All other cells die or stay dead
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)

    if current == 1:
        return 1 if neighbors in [2, 3] else 0
    else:
        return 1 if neighbors == 3 else 0


def high_life_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    HighLife variant: Like Life, but dead cells with 6 neighbors also come alive.
    This creates interesting replicating patterns.
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)

    if current == 1:
        return 1 if neighbors in [2, 3] else 0
    else:
        return 1 if neighbors in [3, 6] else 0


def seeds_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    Seeds: Living cells always die, dead cells with 2 neighbors become alive.
    Creates expanding patterns that look like growing seeds.
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)

    if current == 1:
        return 0  # Living cells always die
    else:
        return 1 if neighbors == 2 else 0


# ===== DEMO =====

if __name__ == "__main__":
    print("Cellular Automata Explorer")
    print("=" * 50)
    print("\nStarting with Conway's Game of Life...")

    # Create a small automaton
    ca = CellularAutomaton(width=40, height=20, rule=life_rules)

    # Start with a random configuration
    ca.randomize(density=0.25)

    # Run for a few generations
    for i in range(10):
        ca.display()
        stats = ca.get_stats()
        print(f"Alive cells: {stats['alive']} ({stats['density']:.1%})")

        if i < 9:
            import time
            time.sleep(0.3)

        ca.step()

    print("\n" + "=" * 50)
    print("Framework ready for experimentation!")
    print("\nTry creating your own rules:")
    print("  def my_rule(automaton, x, y):")
    print("      # Your logic here")
    print("      return 0 or 1")
