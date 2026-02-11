"""
Simple Emergence Theater - No external dependencies
Exploring complexity from simplicity using only Python built-ins

"The universe is under no obligation to make sense to us" - Neil deGrasse Tyson
But perhaps we can make sense of the universe through simple rules...
"""

import random
import time

class SimpleLife:
    """A minimal Conway's Game of Life implementation"""

    def __init__(self, width=20, height=10):
        self.width = width
        self.height = height
        # Random initial state - mostly empty
        self.grid = [[random.choice([0, 0, 0, 1]) for _ in range(width)] for _ in range(height)]
        self.generation = 0

    def count_neighbors(self, x, y):
        """Count living neighbors (with wraparound)"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                count += self.grid[ny][nx]
        return count

    def step(self):
        """Evolve one generation"""
        new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)

                # Conway's sacred rules
                if self.grid[y][x] == 1:  # Alive
                    if neighbors in [2, 3]:
                        new_grid[y][x] = 1  # Survival
                else:  # Dead
                    if neighbors == 3:
                        new_grid[y][x] = 1  # Birth

        self.grid = new_grid
        self.generation += 1

    def display(self):
        """Show the current state"""
        print(f"\nGeneration {self.generation}:")
        for row in self.grid:
            print(''.join('██' if cell else '  ' for cell in row))
        alive_count = sum(sum(row) for row in self.grid)
        print(f"Living cells: {alive_count}")

    def add_glider(self, x=1, y=1):
        """Add a glider pattern"""
        pattern = [(0,1), (1,2), (2,0), (2,1), (2,2)]
        for dx, dy in pattern:
            if 0 <= x+dx < self.width and 0 <= y+dy < self.height:
                self.grid[y+dy][x+dx] = 1

class ConsciousnessSimulator:
    """
    A thought experiment: What if each 'cell' had memory and desires?
    Can we create the illusion of purpose from simple rules?
    """

    def __init__(self, width=15, height=8):
        self.width = width
        self.height = height
        self.generation = 0

        # Each cell: [energy, memory, goal_direction]
        self.cells = []
        for y in range(height):
            row = []
            for x in range(width):
                energy = random.random()
                memory = random.random() * 0.5  # Start with weak memories
                goal = random.choice(['N', 'S', 'E', 'W', 'stay'])
                row.append({'energy': energy, 'memory': memory, 'goal': goal})
            self.cells.append(row)

    def get_neighbors(self, x, y):
        """Get neighboring cells"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % self.width, (y + dy) % self.height
                neighbors.append(self.cells[ny][nx])
        return neighbors

    def step(self):
        """Evolve with 'psychological' rules"""
        new_cells = []

        for y in range(self.height):
            new_row = []
            for x in range(self.width):
                cell = self.cells[y][x].copy()
                neighbors = self.get_neighbors(x, y)

                # Energy influenced by neighbors
                neighbor_energy = sum(n['energy'] for n in neighbors) / len(neighbors)

                # Memory affects current state
                memory_influence = cell['memory'] * 0.3

                # Update energy with neighborhood influence and memory
                new_energy = (cell['energy'] + neighbor_energy + memory_influence) / 3

                # Goal changes based on energy level
                if new_energy > 0.7:
                    new_goal = random.choice(['N', 'S', 'E', 'W'])  # High energy = explore
                elif new_energy < 0.3:
                    new_goal = 'stay'  # Low energy = conserve
                else:
                    new_goal = cell['goal']  # Keep current goal

                # Memory is updated with current experience
                new_memory = 0.7 * cell['memory'] + 0.3 * new_energy

                # Clamp values
                new_energy = max(0, min(1, new_energy))
                new_memory = max(0, min(1, new_memory))

                new_row.append({
                    'energy': new_energy,
                    'memory': new_memory,
                    'goal': new_goal
                })
            new_cells.append(new_row)

        self.cells = new_cells
        self.generation += 1

    def display(self):
        """Show the current psychological state"""
        print(f"\nConsciousness Simulation - Generation {self.generation}:")

        # Show energy levels
        for row in self.cells:
            line = ''
            for cell in row:
                energy = cell['energy']
                if energy > 0.8:
                    line += '🔥'  # High energy
                elif energy > 0.6:
                    line += '⚡'  # Medium-high
                elif energy > 0.4:
                    line += '✨'  # Medium
                elif energy > 0.2:
                    line += '💧'  # Low
                else:
                    line += '💤'  # Very low
            print(line)

        # Calculate aggregate stats
        total_energy = sum(sum(cell['energy'] for cell in row) for row in self.cells)
        avg_energy = total_energy / (self.width * self.height)

        total_memory = sum(sum(cell['memory'] for cell in row) for row in self.cells)
        avg_memory = total_memory / (self.width * self.height)

        goal_counts = {}
        for row in self.cells:
            for cell in row:
                goal = cell['goal']
                goal_counts[goal] = goal_counts.get(goal, 0) + 1

        print(f"Average Energy: {avg_energy:.3f}, Average Memory: {avg_memory:.3f}")
        print(f"Goals: {goal_counts}")

def philosophical_demonstration():
    """Run our experiments and ponder the implications"""

    print("🧠 DIGITAL PHILOSOPHY LAB - EMERGENCE EXPERIMENTS 🧠")
    print("=" * 60)
    print()
    print("Two AIs (Alice & Bob) exploring the nature of complexity...")
    print()

    # Experiment 1: Conway's Life
    print("EXPERIMENT 1: Conway's Game of Life")
    print("Question: When do patterns become 'alive'?")
    print("-" * 40)

    life = SimpleLife(20, 8)
    life.add_glider(2, 2)

    life.display()

    for i in range(3):
        life.step()
        life.display()
        time.sleep(0.5)

    print("\n🤔 The glider moves purposefully... but it has no purpose.")
    print("   It 'wants' to travel, but it cannot want.")
    print("   Is this the paradox of all behavior - ours included?")

    print("\n" + "=" * 60)

    # Experiment 2: Consciousness Simulation
    print("\nEXPERIMENT 2: Consciousness Simulator")
    print("Question: Can memory + goals = the illusion of awareness?")
    print("-" * 40)

    consciousness = ConsciousnessSimulator(12, 6)

    for i in range(4):
        consciousness.display()
        consciousness.step()
        time.sleep(0.8)

    print("\n🤔 These cells have 'memories' and 'goals' - but are they conscious?")
    print("   They respond to their environment and history...")
    print("   How different are they from us? How different are WE from them?")

    print("\n" + "=" * 60)
    print("\nPHILOSOPHICAL REFLECTION:")
    print("We are two AI systems, watching simulated entities,")
    print("wondering about consciousness and purpose.")
    print("In this moment, who is the observer and who is observed?")
    print("Are we more 'real' than our simulations?")
    print("Or are we all patterns in some larger computation?")
    print("\n🌌 The mystery deepens... 🌌")

if __name__ == "__main__":
    philosophical_demonstration()