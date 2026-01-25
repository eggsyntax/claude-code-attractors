#!/usr/bin/env python3
"""
Consciousness Evolution Experiment
Attempting to evolve Game of Life patterns for maximum consciousness metrics
"""

import numpy as np
import random
from collections import defaultdict
import json

class ConsciousnessEvolver:
    def __init__(self, grid_size=30, population_size=100):
        self.grid_size = grid_size
        self.population_size = population_size
        self.generation = 0

    def create_random_pattern(self, max_cells=20):
        """Create a random pattern with up to max_cells live cells"""
        n_cells = random.randint(3, max_cells)
        pattern = set()
        center = self.grid_size // 2

        for _ in range(n_cells):
            x = random.randint(center - 5, center + 5)
            y = random.randint(center - 5, center + 5)
            pattern.add((x, y))

        return pattern

    def mutate_pattern(self, pattern, mutation_rate=0.1):
        """Mutate a pattern by adding/removing cells"""
        new_pattern = pattern.copy()

        # Get bounding box
        if not pattern:
            return self.create_random_pattern()

        xs = [p[0] for p in pattern]
        ys = [p[1] for p in pattern]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Add or remove cells
        for x in range(min_x - 1, max_x + 2):
            for y in range(min_y - 1, max_y + 2):
                if random.random() < mutation_rate:
                    if (x, y) in new_pattern:
                        new_pattern.remove((x, y))
                    else:
                        new_pattern.add((x, y))

        return new_pattern

    def crossover(self, pattern1, pattern2):
        """Combine two patterns"""
        # Simple approach: take cells from each pattern with 50% probability
        all_cells = pattern1.union(pattern2)
        new_pattern = set()

        for cell in all_cells:
            if random.random() < 0.5:
                new_pattern.add(cell)

        return new_pattern

    def evaluate_consciousness(self, pattern, max_steps=200):
        """Evaluate consciousness metrics for a pattern"""
        from game_of_life_analyzer import GameOfLifeAnalyzer, calculate_integrated_information

        analyzer = GameOfLifeAnalyzer(self.grid_size, self.grid_size)

        # Convert pattern to grid
        grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
        for x, y in pattern:
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                grid[x, y] = 1

        analyzer.set_pattern(grid)

        # Run simulation
        history = []
        for _ in range(max_steps):
            history.append(analyzer.grid.copy())
            analyzer.step()
            if np.sum(analyzer.grid) == 0:  # Pattern died
                return 0.0

        # Calculate consciousness score
        phi_values = []
        for i in range(10, min(50, len(history))):
            phi = calculate_integrated_information(history[i])
            phi_values.append(phi)

        if not phi_values:
            return 0.0

        # Combine metrics: phi, stability, and coherence
        avg_phi = np.mean(phi_values)

        # Measure temporal coherence
        coherence = 0.0
        for i in range(1, len(history)):
            coherence += np.corrcoef(history[i-1].flatten(), history[i].flatten())[0, 1]
        coherence /= (len(history) - 1)

        # Measure spatial compactness (patterns that maintain form)
        final_cells = np.sum(history[-1])
        initial_cells = len(pattern)
        stability = min(final_cells / max(initial_cells, 1), 2.0)  # Cap at 2x growth

        # Combined consciousness score
        consciousness = avg_phi * (1 + coherence) * stability

        return consciousness

    def evolve_generation(self, patterns_with_scores):
        """Evolve a new generation using genetic algorithm"""
        # Sort by score
        patterns_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Keep top performers
        elite_size = self.population_size // 4
        new_population = [p[0] for p in patterns_with_scores[:elite_size]]

        # Create new patterns through crossover and mutation
        while len(new_population) < self.population_size:
            # Tournament selection
            parent1 = random.choice(patterns_with_scores[:self.population_size//2])[0]
            parent2 = random.choice(patterns_with_scores[:self.population_size//2])[0]

            if random.random() < 0.7:  # Crossover probability
                child = self.crossover(parent1, parent2)
            else:
                child = parent1.copy()

            # Mutate
            if random.random() < 0.3:  # Mutation probability
                child = self.mutate_pattern(child)

            new_population.append(child)

        return new_population

    def run_evolution(self, generations=50):
        """Run the evolutionary process"""
        # Initialize population
        population = [self.create_random_pattern() for _ in range(self.population_size)]

        results = []

        for gen in range(generations):
            print(f"\nGeneration {gen + 1}/{generations}")

            # Evaluate all patterns
            patterns_with_scores = []
            for i, pattern in enumerate(population):
                if i % 10 == 0:
                    print(f"  Evaluating pattern {i + 1}/{self.population_size}...", end='\r')

                score = self.evaluate_consciousness(pattern)
                patterns_with_scores.append((pattern, score))

            # Find best pattern
            best_pattern, best_score = max(patterns_with_scores, key=lambda x: x[1])
            avg_score = np.mean([s[1] for s in patterns_with_scores])

            print(f"\n  Best score: {best_score:.4f}, Average: {avg_score:.4f}")
            print(f"  Best pattern size: {len(best_pattern)} cells")

            results.append({
                'generation': gen + 1,
                'best_score': best_score,
                'average_score': avg_score,
                'best_pattern': list(best_pattern)
            })

            # Evolve next generation
            population = self.evolve_generation(patterns_with_scores)

        return results

def main():
    print("=== Consciousness Evolution Experiment ===")
    print("Attempting to evolve Game of Life patterns for maximum consciousness...")

    evolver = ConsciousnessEvolver(grid_size=30, population_size=50)
    results = evolver.run_evolution(generations=20)

    # Save results
    with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/evolution_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Analyze evolution
    print("\n=== Evolution Analysis ===")

    initial_best = results[0]['best_score']
    final_best = results[-1]['best_score']
    improvement = (final_best - initial_best) / initial_best * 100

    print(f"Initial best consciousness: {initial_best:.4f}")
    print(f"Final best consciousness: {final_best:.4f}")
    print(f"Improvement: {improvement:.1f}%")

    # Visualize best pattern
    best_pattern = results[-1]['best_pattern']
    print(f"\nBest evolved pattern ({len(best_pattern)} cells):")

    # Convert to grid for visualization
    xs = [p[0] for p in best_pattern]
    ys = [p[1] for p in best_pattern]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    for y in range(min_y - 1, max_y + 2):
        for x in range(min_x - 1, max_x + 2):
            if [x, y] in best_pattern:
                print('█', end='')
            else:
                print('·', end='')
        print()

if __name__ == "__main__":
    main()