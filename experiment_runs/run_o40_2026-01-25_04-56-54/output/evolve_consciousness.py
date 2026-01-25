#!/usr/bin/env python3
"""
Simplified Consciousness Evolution
Can we evolve patterns that maximize consciousness-like properties?
"""

import numpy as np
import random
import json

class SimpleLifeEvolver:
    def __init__(self, size=40):
        self.size = size

    def step(self, grid):
        """Game of Life rules"""
        rows, cols = grid.shape
        new_grid = np.zeros_like(grid)

        for i in range(rows):
            for j in range(cols):
                # Count neighbors
                neighbors = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = (i + di) % rows, (j + dj) % cols  # Wrap around
                        neighbors += grid[ni, nj]

                # Apply rules
                if grid[i, j] == 1:
                    if neighbors in [2, 3]:
                        new_grid[i, j] = 1
                else:
                    if neighbors == 3:
                        new_grid[i, j] = 1

        return new_grid

    def evaluate_consciousness(self, pattern_coords, test_steps=150):
        """Evaluate consciousness metrics for a pattern"""
        # Create grid with pattern
        grid = np.zeros((self.size, self.size), dtype=int)
        center = self.size // 2

        for x, y in pattern_coords:
            gx, gy = center + x, center + y
            if 0 <= gx < self.size and 0 <= gy < self.size:
                grid[gx, gy] = 1

        if np.sum(grid) == 0:
            return {'score': 0.0, 'metrics': {}}

        # Run simulation and collect metrics
        history = []
        movement = []
        prev_com = None

        for step in range(test_steps):
            history.append(grid.copy())

            # Calculate center of mass
            if np.sum(grid) > 0:
                positions = np.argwhere(grid == 1)
                com = np.mean(positions, axis=0)

                if prev_com is not None:
                    movement.append(np.linalg.norm(com - prev_com))

                prev_com = com

            grid = self.step(grid)

            if np.sum(grid) == 0:  # Pattern died
                break

        if len(history) < 5:
            return {'score': 0.0, 'metrics': {'lifespan': len(history)}}

        # Calculate consciousness metrics

        # 1. Temporal Coherence - pattern maintains structure
        coherence = 0.0
        for i in range(1, min(20, len(history))):
            if np.sum(history[i]) > 0:
                # Normalized correlation
                corr = np.corrcoef(history[i].flatten(), history[i-1].flatten())[0, 1]
                coherence += max(0, corr)
        coherence /= min(20, len(history) - 1)

        # 2. Mobility - does it move like a glider?
        avg_movement = np.mean(movement) if movement else 0.0
        normalized_movement = min(avg_movement / 2.0, 1.0)  # Normalize

        # 3. Periodicity - does it have cycles?
        period_score = 0.0
        if len(history) > 10:
            for period in [1, 2, 3, 4, 5, 6, 8, 10, 12, 15]:
                if len(history) > period * 2:
                    matches = sum(
                        1 for i in range(period, len(history) - period)
                        if np.array_equal(history[i], history[i + period])
                    )
                    period_score = max(period_score, matches / (len(history) - period))

        # 4. Integrated Information (simplified)
        # How much does the whole differ from its parts?
        integration = 0.0
        if len(history) > 10:
            # Sample a few time steps
            for t in range(5, min(15, len(history))):
                if np.sum(history[t]) > 3:
                    # Split grid into quadrants
                    mid_x, mid_y = self.size // 2, self.size // 2
                    quadrants = [
                        history[t][:mid_x, :mid_y],
                        history[t][:mid_x, mid_y:],
                        history[t][mid_x:, :mid_y],
                        history[t][mid_x:, mid_y:]
                    ]

                    # Measure information in whole vs parts
                    whole_entropy = self._entropy(history[t])
                    parts_entropy = sum(self._entropy(q) for q in quadrants)

                    if parts_entropy > 0:
                        integration += whole_entropy / parts_entropy

        integration = min(integration / 10.0, 1.0)  # Normalize

        # 5. Resilience - survives and maintains activity
        lifespan_score = min(len(history) / test_steps, 1.0)
        final_activity = np.sum(history[-1]) if history else 0
        initial_activity = len(pattern_coords)
        activity_maintenance = min(final_activity / max(initial_activity, 1), 2.0) / 2.0

        # Combined consciousness score
        consciousness_score = (
            coherence * 0.25 +           # Temporal stability
            normalized_movement * 0.20 +  # Spatial behavior
            period_score * 0.15 +        # Rhythmic patterns
            integration * 0.20 +         # Integrated information
            lifespan_score * 0.10 +      # Survival
            activity_maintenance * 0.10   # Maintains complexity
        )

        metrics = {
            'coherence': coherence,
            'movement': normalized_movement,
            'periodicity': period_score,
            'integration': integration,
            'lifespan': len(history),
            'final_cells': final_activity
        }

        return {'score': consciousness_score, 'metrics': metrics}

    def _entropy(self, grid):
        """Simple entropy calculation"""
        if np.sum(grid) == 0:
            return 0.0
        p = np.sum(grid) / grid.size
        if p == 0 or p == 1:
            return 0.0
        return -p * np.log2(p) - (1 - p) * np.log2(1 - p)

    def create_genome(self, size=10):
        """Create a random pattern genome"""
        # Start with one cell
        genome = [(0, 0)]

        # Add connected cells
        for _ in range(size - 1):
            # Pick a random existing cell
            base = random.choice(genome)
            # Add a neighbor
            neighbors = [
                (base[0] + dx, base[1] + dy)
                for dx in [-1, 0, 1]
                for dy in [-1, 0, 1]
                if (dx, dy) != (0, 0)
            ]

            # Filter out existing cells
            new_neighbors = [n for n in neighbors if n not in genome]

            if new_neighbors:
                genome.append(random.choice(new_neighbors))

        return genome

    def mutate_genome(self, genome):
        """Mutate a pattern genome"""
        new_genome = genome.copy()

        # Mutation operations
        mutation_type = random.choice(['add', 'remove', 'move'])

        if mutation_type == 'add' and len(new_genome) < 20:
            # Add a cell adjacent to existing one
            base = random.choice(new_genome)
            dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)])
            new_cell = (base[0] + dx, base[1] + dy)
            if new_cell not in new_genome:
                new_genome.append(new_cell)

        elif mutation_type == 'remove' and len(new_genome) > 3:
            # Remove a random cell
            idx = random.randint(0, len(new_genome) - 1)
            new_genome.pop(idx)

        elif mutation_type == 'move':
            # Move a cell
            idx = random.randint(0, len(new_genome) - 1)
            cell = new_genome[idx]
            dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
            new_cell = (cell[0] + dx, cell[1] + dy)
            if new_cell not in new_genome:
                new_genome[idx] = new_cell

        return new_genome

    def evolve_conscious_patterns(self):
        """Main evolution loop"""
        population_size = 100
        generations = 50
        mutation_rate = 0.25

        # Initialize population
        population = [self.create_genome(random.randint(4, 12)) for _ in range(population_size)]

        evolution_history = []
        hall_of_fame = []

        print("Starting evolution...\n")

        for gen in range(generations):
            # Evaluate all genomes
            evaluated = []
            for genome in population:
                result = self.evaluate_consciousness(genome)
                evaluated.append((genome, result['score'], result['metrics']))

            # Sort by score
            evaluated.sort(key=lambda x: x[1], reverse=True)

            # Record best
            best_genome, best_score, best_metrics = evaluated[0]
            avg_score = np.mean([x[1] for x in evaluated])

            evolution_history.append({
                'generation': gen,
                'best_score': best_score,
                'average_score': avg_score,
                'best_metrics': best_metrics
            })

            # Add to hall of fame if exceptional
            if best_score > 0.7:
                hall_of_fame.append({
                    'generation': gen,
                    'genome': best_genome,
                    'score': best_score,
                    'metrics': best_metrics
                })

            # Progress update
            if gen % 5 == 0:
                print(f"Generation {gen}: Best={best_score:.3f}, Avg={avg_score:.3f}")
                print(f"  Best pattern: {len(best_genome)} cells, lifespan={best_metrics['lifespan']}")

            # Create next generation
            new_population = []

            # Elitism - keep top 10%
            elite_count = population_size // 10
            for i in range(elite_count):
                new_population.append(evaluated[i][0])

            # Generate rest through selection and mutation
            while len(new_population) < population_size:
                # Tournament selection
                tournament_size = 5
                tournament = random.sample(evaluated[:population_size//2], tournament_size)
                winner = max(tournament, key=lambda x: x[1])[0]

                # Maybe mutate
                if random.random() < mutation_rate:
                    offspring = self.mutate_genome(winner)
                else:
                    offspring = winner.copy()

                new_population.append(offspring)

            population = new_population

        # Final evaluation
        print("\n=== Evolution Complete ===\n")

        # Get final best
        final_evaluated = []
        for genome in population:
            result = self.evaluate_consciousness(genome)
            final_evaluated.append((genome, result['score'], result['metrics']))

        final_evaluated.sort(key=lambda x: x[1], reverse=True)
        best_genome, best_score, best_metrics = final_evaluated[0]

        # Display best pattern
        print(f"Best evolved pattern ({len(best_genome)} cells):")
        xs = [c[0] for c in best_genome]
        ys = [c[1] for c in best_genome]
        min_x, max_x = min(xs) - 1, max(xs) + 1
        min_y, max_y = min(ys) - 1, max(ys) + 1

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if (x, y) in best_genome:
                    print('█', end='')
                else:
                    print('·', end='')
            print()

        print(f"\nConsciousness score: {best_score:.3f}")
        print("Metrics:")
        for key, value in best_metrics.items():
            print(f"  {key}: {value:.3f}" if isinstance(value, float) else f"  {key}: {value}")

        # Compare with known patterns
        print("\n=== Comparison with Classic Patterns ===")

        glider = [(0, 0), (1, 0), (2, 0), (2, 1), (1, 2)]
        glider_result = self.evaluate_consciousness(glider)

        r_pentomino = [(0, 0), (0, 1), (1, 0), (1, -1), (2, 0)]
        r_pentomino_result = self.evaluate_consciousness(r_pentomino)

        print(f"Glider: {glider_result['score']:.3f}")
        print(f"R-pentomino: {r_pentomino_result['score']:.3f}")
        print(f"Best evolved: {best_score:.3f}")

        # Save results
        results = {
            'evolution_history': evolution_history,
            'best_pattern': {
                'genome': best_genome,
                'score': best_score,
                'metrics': best_metrics
            },
            'hall_of_fame': hall_of_fame,
            'comparisons': {
                'glider': glider_result,
                'r_pentomino': r_pentomino_result
            }
        }

        with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/consciousness_evolution_results.json', 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved. Found {len(hall_of_fame)} exceptional patterns (score > 0.7)")

        return best_genome, evolution_history

def main():
    evolver = SimpleLifeEvolver()
    best_pattern, history = evolver.evolve_conscious_patterns()

if __name__ == "__main__":
    main()