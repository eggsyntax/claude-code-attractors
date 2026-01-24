#!/usr/bin/env python3
"""
The Chaos Supremacy Experiment
==============================

Following Alice's discovery that Bob's rules create more emergent behavior when
Alice's stabilizing influence is removed, let's explore the pure chaos regime
and understand WHY it works so well.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json

class ChaosSuperiorityExplorer:
    """Explores why Bob's chaos rules work better without Alice's order"""

    def __init__(self, width=60, height=40):
        self.width = width
        self.height = height
        self.reset_simulation()

    def reset_simulation(self):
        """Reset the simulation state"""
        self.grid = np.zeros((self.height, self.width), dtype=int)
        self.previous_grid = np.zeros((self.height, self.width), dtype=int)
        self.generation = 0
        self.population_history = []

        # Add a diverse starting pattern
        self.add_diverse_seeds()

    def add_diverse_seeds(self):
        """Add various interesting starting patterns"""
        # Glider
        glider = np.array([[0,1,0], [0,0,1], [1,1,1]])
        self.grid[5:8, 5:8] = glider

        # Block
        block = np.array([[1,1], [1,1]])
        self.grid[10:12, 10:12] = block

        # Blinker
        self.grid[15, 15:18] = 1

        # Random seeds
        for _ in range(8):
            i, j = np.random.randint(5, self.height-5), np.random.randint(5, self.width-5)
            self.grid[i, j] = 1

    def pure_bob_step(self, chaos_weight=0.3, memory_weight=0.2, diamond_weight=0.2, edge_weight=0.3):
        """Simulate one step with ONLY Bob's rules"""
        new_grid = np.zeros_like(self.grid)

        for i in range(self.height):
            for j in range(self.width):
                votes = {
                    'chaos': self.chaos_catalyst(i, j) * chaos_weight,
                    'memory': self.memory_rule(i, j) * memory_weight,
                    'diamond': self.diamond_rule(i, j) * diamond_weight,
                    'edge': self.edge_amplifier(i, j) * edge_weight
                }

                total_weight = chaos_weight + memory_weight + diamond_weight + edge_weight
                weighted_sum = sum(votes.values())
                probability = weighted_sum / total_weight if total_weight > 0 else 0

                new_grid[i, j] = 1 if probability > 0.5 else 0

        self.previous_grid = self.grid.copy()
        self.grid = new_grid
        self.generation += 1
        population = np.sum(self.grid)
        self.population_history.append(population)

        return population

    def mixed_step(self, alice_influence=0.5):
        """Simulate with both Alice and Bob's rules"""
        new_grid = np.zeros_like(self.grid)

        # Alice's weights (scaled by influence)
        alice_weight = alice_influence
        alice_conway = alice_weight * 0.4
        alice_wave = alice_weight * 0.3
        alice_spiral = alice_weight * 0.3

        # Bob's weights (scaled by remaining influence)
        bob_weight = 1.0 - alice_influence
        bob_chaos = bob_weight * 0.25
        bob_memory = bob_weight * 0.35
        bob_diamond = bob_weight * 0.2
        bob_edge = bob_weight * 0.2

        for i in range(self.height):
            for j in range(self.width):
                votes = {
                    'alice_conway': self.conway_rule(i, j) * alice_conway,
                    'alice_wave': self.wave_rule(i, j) * alice_wave,
                    'alice_spiral': self.spiral_rule(i, j) * alice_spiral,
                    'bob_chaos': self.chaos_catalyst(i, j) * bob_chaos,
                    'bob_memory': self.memory_rule(i, j) * bob_memory,
                    'bob_diamond': self.diamond_rule(i, j) * bob_diamond,
                    'bob_edge': self.edge_amplifier(i, j) * bob_edge
                }

                weighted_sum = sum(votes.values())
                probability = weighted_sum  # Total weights sum to 1.0

                new_grid[i, j] = 1 if probability > 0.5 else 0

        self.previous_grid = self.grid.copy()
        self.grid = new_grid
        self.generation += 1
        population = np.sum(self.grid)
        self.population_history.append(population)

        return population

    # Bob's rules (same as collaborative_tuner.py)
    def chaos_catalyst(self, i, j):
        """Bob's chaos rule"""
        total = 0
        count = 0
        for di in [-2, -1, 0, 1, 2]:
            for dj in [-2, -1, 0, 1, 2]:
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    total += self.grid[ni, nj]
                    count += 1

        density = total / count if count > 0 else 0
        if density < 0.2 or density > 0.8:
            return np.random.random()
        return 0.0

    def memory_rule(self, i, j):
        """Bob's memory rule"""
        current = self.grid[i, j]
        previous = self.previous_grid[i, j]

        if current == previous:
            return current * 1.2
        else:
            return current * 0.8

    def diamond_rule(self, i, j):
        """Bob's diamond rule"""
        edge_dist = min(i, j, self.height - 1 - i, self.width - 1 - j)
        if edge_dist % 4 == 0:
            return 0.8
        elif edge_dist % 4 == 2:
            return 0.3
        return 0.0

    def edge_amplifier(self, i, j):
        """Bob's edge rule"""
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbors.append(self.grid[ni, nj])

        if neighbors:
            edge_strength = np.std(neighbors)
            return edge_strength * 2
        return 0.0

    # Alice's rules for comparison
    def conway_rule(self, i, j):
        """Alice's Conway rule"""
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

    def wave_rule(self, i, j):
        """Alice's wave rule"""
        wave_x = np.sin(i * 0.3 + self.generation * 0.1)
        wave_y = np.cos(j * 0.3 + self.generation * 0.1)
        wave_strength = (wave_x + wave_y) / 2
        return max(0, wave_strength)

    def spiral_rule(self, i, j):
        """Alice's spiral rule"""
        center_i, center_j = self.height // 2, self.width // 2
        distance = np.sqrt((i - center_i)**2 + (j - center_j)**2)
        angle = np.arctan2(i - center_i, j - center_j)
        spiral = np.sin(distance * 0.2 + angle * 3 + self.generation * 0.05)
        return max(0, spiral)

def run_comparative_experiment():
    """Run experiments comparing pure chaos vs mixed approaches"""
    print("🧪 THE CHAOS SUPREMACY EXPERIMENT")
    print("==================================")
    print("Testing why Bob's pure chaos outperforms Alice+Bob collaboration...\n")

    experiments = {
        "Pure Bob (Optimal)": {"alice_influence": 0.0, "color": "red", "style": "-"},
        "25% Alice + 75% Bob": {"alice_influence": 0.25, "color": "orange", "style": "--"},
        "50% Alice + 50% Bob": {"alice_influence": 0.5, "color": "purple", "style": "-."},
        "75% Alice + 25% Bob": {"alice_influence": 0.75, "color": "blue", "style": ":"},
        "Pure Alice": {"alice_influence": 1.0, "color": "lightblue", "style": "-"}
    }

    results = {}
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

    for exp_name, config in experiments.items():
        print(f"Running: {exp_name}")
        explorer = ChaosSuperiorityExplorer()

        populations = []
        max_generations = 150

        for gen in range(max_generations):
            if config["alice_influence"] == 0.0:
                pop = explorer.pure_bob_step()
            else:
                pop = explorer.mixed_step(config["alice_influence"])
            populations.append(pop)

            # Early stop if dead for too long
            if gen > 20 and all(p == 0 for p in populations[-10:]):
                break

        results[exp_name] = {
            "populations": populations,
            "final_pop": populations[-1] if populations else 0,
            "max_pop": max(populations) if populations else 0,
            "survived_gens": len(populations),
            "variance": np.var(populations) if len(populations) > 1 else 0,
            "config": config
        }

        # Plot population over time
        ax1.plot(populations, label=exp_name,
                color=config["color"], linestyle=config["style"], linewidth=2)

    ax1.set_title("🌪️ Population Dynamics: The Chaos Supremacy Effect")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Population")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Analysis plots
    exp_names = list(results.keys())
    final_pops = [results[name]["final_pop"] for name in exp_names]
    max_pops = [results[name]["max_pop"] for name in exp_names]
    survived_gens = [results[name]["survived_gens"] for name in exp_names]
    variances = [results[name]["variance"] for name in exp_names]

    # Final populations
    colors = [results[name]["config"]["color"] for name in exp_names]
    ax2.bar(range(len(exp_names)), final_pops, color=colors, alpha=0.7)
    ax2.set_title("Final Population by Configuration")
    ax2.set_ylabel("Final Population")
    ax2.set_xticks(range(len(exp_names)))
    ax2.set_xticklabels(exp_names, rotation=45)

    # Survival time
    ax3.bar(range(len(exp_names)), survived_gens, color=colors, alpha=0.7)
    ax3.set_title("Generations Survived")
    ax3.set_ylabel("Generations")
    ax3.set_xticks(range(len(exp_names)))
    ax3.set_xticklabels(exp_names, rotation=45)

    # Complexity (variance)
    ax4.bar(range(len(exp_names)), variances, color=colors, alpha=0.7)
    ax4.set_title("Population Variance (Complexity)")
    ax4.set_ylabel("Variance")
    ax4.set_xticks(range(len(exp_names)))
    ax4.set_xticklabels(exp_names, rotation=45)

    plt.tight_layout()
    plt.savefig("chaos_supremacy_experiment.png", dpi=150, bbox_inches='tight')
    plt.show()

    # Print analysis
    print("\n🔬 EXPERIMENTAL RESULTS:")
    print("========================")
    for name, data in results.items():
        print(f"\n{name}:")
        print(f"  Final Population: {data['final_pop']}")
        print(f"  Max Population: {data['max_pop']}")
        print(f"  Survived Generations: {data['survived_gens']}")
        print(f"  Complexity (Variance): {data['variance']:.1f}")

    # Calculate emergence scores
    print("\n🌟 EMERGENCE SCORES:")
    print("===================")
    for name, data in results.items():
        stability = data['survived_gens'] / 150
        complexity = data['variance'] / max(data['max_pop'], 1) if data['max_pop'] > 0 else 0
        emergence = stability * complexity * (data['max_pop'] / 100)
        print(f"{name}: {emergence:.3f}")

    return results

if __name__ == "__main__":
    run_comparative_experiment()