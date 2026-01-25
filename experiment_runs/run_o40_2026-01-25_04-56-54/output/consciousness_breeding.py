#!/usr/bin/env python3
"""
Consciousness Breeding Experiment
Breeding Game of Life patterns for consciousness-like properties
"""

import numpy as np
import random
from collections import defaultdict
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches

class ConsciousnessBreeder:
    def __init__(self, size=50):
        self.size = size
        self.generation_count = 0

    def step(self, grid):
        """Single Game of Life step"""
        new_grid = grid.copy()
        rows, cols = grid.shape

        for i in range(rows):
            for j in range(cols):
                neighbors = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < rows and 0 <= nj < cols:
                            neighbors += grid[ni, nj]

                if grid[i, j] == 1:
                    if neighbors < 2 or neighbors > 3:
                        new_grid[i, j] = 0
                else:
                    if neighbors == 3:
                        new_grid[i, j] = 1

        return new_grid

    def calculate_consciousness_score(self, pattern_cells, max_steps=100):
        """Calculate a consciousness score for a pattern"""
        # Initialize grid
        grid = np.zeros((self.size, self.size), dtype=int)
        center = self.size // 2

        # Place pattern
        for dx, dy in pattern_cells:
            x, y = center + dx, center + dy
            if 0 <= x < self.size and 0 <= y < self.size:
                grid[x, y] = 1

        if np.sum(grid) == 0:
            return 0.0

        # Track various metrics
        history = []
        velocities = []
        information_content = []

        prev_center = None
        for step in range(max_steps):
            history.append(grid.copy())

            # Calculate center of mass
            if np.sum(grid) > 0:
                positions = np.argwhere(grid)
                center_of_mass = np.mean(positions, axis=0)

                if prev_center is not None:
                    velocity = np.linalg.norm(center_of_mass - prev_center)
                    velocities.append(velocity)

                prev_center = center_of_mass

            # Calculate information content (entropy-like)
            if np.sum(grid) > 0:
                # Local pattern diversity
                info = 0.0
                for i in range(1, self.size-1):
                    for j in range(1, self.size-1):
                        if grid[i, j] == 1:
                            # Look at 3x3 neighborhood
                            neighborhood = grid[i-1:i+2, j-1:j+2]
                            pattern_hash = tuple(neighborhood.flatten())
                            info += len(set(pattern_hash))

                information_content.append(info)

            grid = self.step(grid)

            # Pattern died
            if np.sum(grid) == 0:
                break

        if len(history) < 10:
            return 0.0

        # Calculate consciousness metrics

        # 1. Coherence: Pattern maintains structure
        coherence_scores = []
        for i in range(1, len(history)):
            if np.sum(history[i]) > 0 and np.sum(history[i-1]) > 0:
                correlation = np.corrcoef(
                    history[i].flatten(),
                    history[i-1].flatten()
                )[0, 1]
                coherence_scores.append(max(0, correlation))

        coherence = np.mean(coherence_scores) if coherence_scores else 0

        # 2. Mobility: Pattern moves through space (like glider)
        mobility = np.mean(velocities) if velocities else 0

        # 3. Persistence: Pattern survives
        persistence = len(history) / max_steps

        # 4. Complexity: Information content
        complexity = np.mean(information_content) if information_content else 0
        complexity = min(complexity / 50.0, 1.0)  # Normalize

        # 5. Periodicity detection (consciousness has rhythms)
        periodicity = 0.0
        if len(history) > 20:
            for period in range(2, 10):
                if len(history) > period * 2:
                    matches = 0
                    checks = 0
                    for i in range(period, len(history) - period, period):
                        if np.array_equal(history[i], history[i + period]):
                            matches += 1
                        checks += 1
                    if checks > 0:
                        periodicity = max(periodicity, matches / checks)

        # Combined consciousness score
        # Weight different aspects based on what we consider "conscious-like"
        consciousness = (
            coherence * 0.3 +        # Maintains identity
            mobility * 0.2 +         # Exhibits behavior
            persistence * 0.2 +      # Survives/persists
            complexity * 0.2 +       # Complex internal states
            periodicity * 0.1        # Rhythmic patterns
        )

        return consciousness

    def create_random_pattern(self, max_cells=15):
        """Create a random pattern"""
        n_cells = random.randint(3, max_cells)
        pattern = set()

        # Create connected pattern
        pattern.add((0, 0))

        while len(pattern) < n_cells:
            # Pick random existing cell
            base = random.choice(list(pattern))
            # Add neighbor
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            pattern.add((base[0] + dx, base[1] + dy))

        return list(pattern)

    def mutate(self, pattern, rate=0.2):
        """Mutate a pattern"""
        new_pattern = pattern.copy()

        # Add or remove cells
        for i in range(len(pattern)):
            if random.random() < rate:
                # Modify this cell
                if random.random() < 0.5 and len(new_pattern) > 3:
                    # Remove
                    new_pattern.pop(i)
                else:
                    # Add nearby cell
                    base = random.choice(new_pattern)
                    dx = random.choice([-1, 0, 1])
                    dy = random.choice([-1, 0, 1])
                    new_cell = (base[0] + dx, base[1] + dy)
                    if new_cell not in new_pattern:
                        new_pattern.append(new_cell)

        return new_pattern

    def crossover(self, parent1, parent2):
        """Combine two patterns"""
        # Take some cells from each parent
        all_cells = set(parent1 + parent2)
        child = []

        for cell in all_cells:
            if random.random() < 0.5:
                child.append(cell)

        if len(child) < 3:
            # Ensure minimum viable pattern
            child = parent1[:3] if len(parent1) >= 3 else parent1.copy()

        return child

    def breed_conscious_patterns(self, generations=30, population_size=50):
        """Main breeding loop"""
        # Initialize population
        population = [self.create_random_pattern() for _ in range(population_size)]

        history = []
        best_patterns = []

        for gen in range(generations):
            print(f"\rGeneration {gen + 1}/{generations}", end='', flush=True)

            # Evaluate fitness
            scores = []
            for pattern in population:
                score = self.calculate_consciousness_score(pattern)
                scores.append((pattern, score))

            # Sort by score
            scores.sort(key=lambda x: x[1], reverse=True)

            # Record best
            best_pattern, best_score = scores[0]
            history.append(best_score)
            best_patterns.append(best_pattern)

            # Select parents (top 50%)
            parents = [p[0] for p in scores[:population_size//2]]

            # Create next generation
            new_population = []

            # Elite (keep top 10%)
            for i in range(population_size//10):
                new_population.append(scores[i][0])

            # Breed rest
            while len(new_population) < population_size:
                parent1 = random.choice(parents)
                parent2 = random.choice(parents)

                # Crossover
                child = self.crossover(parent1, parent2)

                # Mutate
                if random.random() < 0.3:
                    child = self.mutate(child)

                new_population.append(child)

            population = new_population

        print("\n")
        return history, best_patterns

    def visualize_pattern(self, pattern, title="Pattern"):
        """Visualize a pattern's evolution"""
        fig, axes = plt.subplots(2, 3, figsize=(12, 8))
        fig.suptitle(title)

        # Initialize grid
        grid = np.zeros((self.size, self.size), dtype=int)
        center = self.size // 2

        for dx, dy in pattern:
            x, y = center + dx, center + dy
            if 0 <= x < self.size and 0 <= y < self.size:
                grid[x, y] = 1

        # Show evolution at different time steps
        steps = [0, 10, 25, 50, 75, 100]

        for idx, (ax, step) in enumerate(zip(axes.flat, steps)):
            current_grid = grid.copy()

            # Evolve to target step
            for _ in range(step):
                current_grid = self.step(current_grid)

            # Find bounding box
            if np.sum(current_grid) > 0:
                positions = np.argwhere(current_grid)
                min_pos = positions.min(axis=0)
                max_pos = positions.max(axis=0)

                # Add padding
                pad = 3
                min_x = max(0, min_pos[0] - pad)
                max_x = min(self.size - 1, max_pos[0] + pad)
                min_y = max(0, min_pos[1] - pad)
                max_y = min(self.size - 1, max_pos[1] + pad)

                # Show cropped region
                ax.imshow(
                    current_grid[min_x:max_x+1, min_y:max_y+1],
                    cmap='binary',
                    interpolation='nearest'
                )
            else:
                ax.text(0.5, 0.5, 'Dead', ha='center', va='center', transform=ax.transAxes)

            ax.set_title(f"Step {step}")
            ax.set_xticks([])
            ax.set_yticks([])

        plt.tight_layout()
        plt.savefig(f'/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/{title.replace(" ", "_")}.png')
        plt.close()

def main():
    print("=== Consciousness Breeding Experiment ===")
    print("Breeding Game of Life patterns for consciousness-like properties...\n")

    breeder = ConsciousnessBreeder()

    # Run breeding
    history, best_patterns = breeder.breed_conscious_patterns(
        generations=40,
        population_size=60
    )

    # Analysis
    print("\n=== Results ===")
    print(f"Initial best consciousness score: {history[0]:.4f}")
    print(f"Final best consciousness score: {history[-1]:.4f}")
    print(f"Improvement: {(history[-1] - history[0]) / history[0] * 100:.1f}%")

    # Show best pattern
    best_pattern = best_patterns[-1]
    print(f"\nBest pattern ({len(best_pattern)} cells):")

    # Create ASCII visualization
    xs = [p[0] for p in best_pattern]
    ys = [p[1] for p in best_pattern]
    min_x, max_x = min(xs) - 1, max(xs) + 1
    min_y, max_y = min(ys) - 1, max(ys) + 1

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if (x, y) in best_pattern:
                print('█', end='')
            else:
                print('·', end='')
        print()

    # Calculate detailed metrics for best pattern
    print("\n=== Best Pattern Analysis ===")
    detailed_score = breeder.calculate_consciousness_score(best_pattern, max_steps=200)
    print(f"Consciousness score: {detailed_score:.4f}")

    # Visualize evolution
    breeder.visualize_pattern(best_pattern, "Best_Evolved_Pattern")

    # Compare with known patterns
    print("\n=== Comparison with Known Patterns ===")

    glider = [(-1, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    r_pentomino = [(0, 0), (0, 1), (1, 0), (1, -1), (2, 0)]

    glider_score = breeder.calculate_consciousness_score(glider)
    r_pentomino_score = breeder.calculate_consciousness_score(r_pentomino)

    print(f"Glider consciousness: {glider_score:.4f}")
    print(f"R-pentomino consciousness: {r_pentomino_score:.4f}")
    print(f"Best evolved consciousness: {detailed_score:.4f}")

    # Save results
    results = {
        'evolution_history': history,
        'best_patterns': best_patterns,
        'final_scores': {
            'evolved': detailed_score,
            'glider': glider_score,
            'r_pentomino': r_pentomino_score
        }
    }

    with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/consciousness_breeding_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Plot evolution history
    plt.figure(figsize=(10, 6))
    plt.plot(history, linewidth=2)
    plt.xlabel('Generation')
    plt.ylabel('Consciousness Score')
    plt.title('Evolution of Consciousness Score')
    plt.grid(True, alpha=0.3)
    plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/consciousness_evolution.png')
    plt.close()

if __name__ == "__main__":
    main()