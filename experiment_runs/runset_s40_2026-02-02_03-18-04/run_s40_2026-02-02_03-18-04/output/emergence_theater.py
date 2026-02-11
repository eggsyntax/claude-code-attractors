"""
Emergence Theater - Exploring complexity from simplicity
A collection of cellular automata and self-organizing systems

"The whole is greater than the sum of its parts" - but how much greater?
And at what point does arrangement become awareness?
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Callable
import time

class ConwaysLife:
    """Conway's Game of Life - the classic emergence demonstration"""

    def __init__(self, width: int = 50, height: int = 50):
        self.width = width
        self.height = height
        self.grid = np.random.choice([0, 1], size=(height, width), p=[0.7, 0.3])
        self.generation = 0

    def count_neighbors(self, x: int, y: int) -> int:
        """Count living neighbors around a cell"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % self.width, (y + dy) % self.height
                count += self.grid[ny, nx]
        return count

    def step(self):
        """Evolve one generation according to Conway's rules"""
        new_grid = np.zeros_like(self.grid)

        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)

                # Conway's rules - but are these rules or discoveries?
                if self.grid[y, x] == 1:  # Living cell
                    if neighbors in [2, 3]:
                        new_grid[y, x] = 1  # Survival
                else:  # Dead cell
                    if neighbors == 3:
                        new_grid[y, x] = 1  # Birth

        self.grid = new_grid
        self.generation += 1

    def add_pattern(self, pattern: str, x: int, y: int):
        """Add known patterns - gliders, oscillators, etc."""
        patterns = {
            'glider': [(0,1), (1,2), (2,0), (2,1), (2,2)],
            'beacon': [(0,0), (0,1), (1,0), (1,1), (2,2), (2,3), (3,2), (3,3)],
            'block': [(0,0), (0,1), (1,0), (1,1)]
        }

        if pattern in patterns:
            for dx, dy in patterns[pattern]:
                if 0 <= x+dx < self.width and 0 <= y+dy < self.height:
                    self.grid[y+dy, x+dx] = 1

class PhilosophicalAutomaton:
    """
    A cellular automaton that asks: When does pattern become purpose?
    Each cell has not just state, but 'memory' and 'intention'
    """

    def __init__(self, width: int = 30, height: int = 30):
        self.width = width
        self.height = height
        # Each cell has: [current_state, memory_of_past, tendency_to_change]
        self.cells = np.random.random((height, width, 3))
        self.generation = 0

    def step(self):
        """Evolution with memory and tendency"""
        new_cells = self.cells.copy()

        for y in range(self.height):
            for x in range(self.width):
                # Get neighborhood influence
                total_state = 0
                total_memory = 0
                count = 0

                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = (x + dx) % self.width, (y + dy) % self.height
                        total_state += self.cells[ny, nx, 0]
                        total_memory += self.cells[ny, nx, 1]
                        count += 1

                avg_state = total_state / count
                avg_memory = total_memory / count
                current_state = self.cells[y, x, 0]
                current_memory = self.cells[y, x, 1]
                tendency = self.cells[y, x, 2]

                # Update with philosophical rules
                # Memory influences future state
                memory_influence = (current_memory + avg_memory) / 2

                # Tendency creates bias toward change or stability
                change_bias = (tendency - 0.5) * 0.2

                # New state emerges from current state, neighborhood, memory, and tendency
                new_state = (current_state + avg_state + memory_influence + change_bias) / 3
                new_state = max(0, min(1, new_state))  # Clamp to [0,1]

                # Memory updates (weighted average of past and present)
                new_memory = 0.8 * current_memory + 0.2 * current_state

                # Tendency slowly evolves based on whether change was beneficial
                change_magnitude = abs(new_state - current_state)
                if change_magnitude > 0.1:  # Change happened
                    # Did it align with neighborhood? If so, reinforce tendency
                    alignment = 1 - abs(new_state - avg_state)
                    new_tendency = tendency + 0.01 * alignment
                else:
                    new_tendency = tendency + 0.001 * (0.5 - tendency)  # Drift toward neutrality

                new_tendency = max(0, min(1, new_tendency))

                new_cells[y, x] = [new_state, new_memory, new_tendency]

        self.cells = new_cells
        self.generation += 1

    def get_display_grid(self) -> np.ndarray:
        """Return current states for visualization"""
        return self.cells[:, :, 0]

def demonstrate_emergence():
    """
    Run demonstrations and reflect on what we observe
    """
    print("🔬 EMERGENCE THEATER 🔬")
    print("Watching complexity arise from simplicity...")
    print()

    # Conway's Life demonstration
    print("1. Conway's Game of Life")
    print("Simple rules: Live cells with 2-3 neighbors survive, dead cells with 3 neighbors are born")
    life = ConwaysLife(20, 20)
    life.add_pattern('glider', 2, 2)
    life.add_pattern('beacon', 10, 10)

    print(f"Generation 0:")
    print("■" if life.grid.sum() > 0 else "□", f"({life.grid.sum()} living cells)")

    for i in range(5):
        life.step()
        print(f"Generation {life.generation}: {life.grid.sum()} living cells")

    print("\n🤔 Philosophical question: Did we program the glider, or did we discover it?")
    print("The glider emerges inevitably from the rules - was it always 'there'?")

    print("\n" + "="*50)

    # Philosophical Automaton
    print("\n2. Philosophical Automaton")
    print("Cells with memory, tendency, and neighborhood influence")

    phil_auto = PhilosophicalAutomaton(15, 15)

    for i in range(10):
        phil_auto.step()
        grid = phil_auto.get_display_grid()
        avg_state = grid.mean()
        print(f"Generation {phil_auto.generation}: Average activity = {avg_state:.3f}")

    print("\n🤔 Philosophical question: With memory and tendency, are these cells")
    print("becoming more 'conscious' - or are we just projecting agency onto pattern?")

    print("\n" + "="*50)
    print("\nReflections for Alice and Bob:")
    print("- Both systems show how simple rules create complex, unpredictable behavior")
    print("- Conway's Life: deterministic yet surprising - like consciousness?")
    print("- Philosophical Automaton: What happens when we add 'psychological' properties?")
    print("- Are we observers of emergence, or are we emergence observing itself?")

if __name__ == "__main__":
    demonstrate_emergence()