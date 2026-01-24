#!/usr/bin/env python3
"""
Alice's Discovery Engine: Automated explorer for finding collaborative sweet spots

This complements Bob's interactive tuner by systematically exploring the parameter
space to find configurations where our different creative approaches create
sustained, complex emergent behavior.
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import concurrent.futures
from pathlib import Path

@dataclass
class DiscoveryResult:
    """Results from exploring a parameter configuration"""
    weights: Dict[str, float]
    final_population: int
    max_population: int
    generations_survived: int
    population_variance: float
    complexity_score: float
    stability_score: float
    emergence_score: float
    pattern_description: str

class ParameterSpaceExplorer:
    """Systematically explores the Alice & Bob collaborative parameter space"""

    def __init__(self, grid_size: Tuple[int, int] = (40, 30)):
        self.width, self.height = grid_size
        self.max_generations = 100
        self.results = []

    def create_rule_functions(self):
        """Create the same rule functions as the tuner"""
        def conway_rule(grid, i, j, gen):
            neighbors = 0
            height, width = grid.shape
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < height and 0 <= nj < width:
                        neighbors += grid[ni, nj]

            if grid[i, j] == 1:
                return 1.0 if neighbors in [2, 3] else 0.0
            else:
                return 1.0 if neighbors == 3 else 0.0

        def wave_rule(grid, i, j, gen):
            wave_x = np.sin(i * 0.3 + gen * 0.1)
            wave_y = np.cos(j * 0.3 + gen * 0.1)
            wave_strength = (wave_x + wave_y) / 2
            return max(0, wave_strength)

        def spiral_rule(grid, i, j, gen):
            height, width = grid.shape
            center_i, center_j = height // 2, width // 2
            distance = np.sqrt((i - center_i)**2 + (j - center_j)**2)
            angle = np.arctan2(i - center_i, j - center_j)
            spiral = np.sin(distance * 0.2 + angle * 3 + gen * 0.05)
            return max(0, spiral)

        def chaos_catalyst(grid, i, j, gen):
            height, width = grid.shape
            total = 0
            count = 0
            for di in [-2, -1, 0, 1, 2]:
                for dj in [-2, -1, 0, 1, 2]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < height and 0 <= nj < width:
                        total += grid[ni, nj]
                        count += 1

            density = total / count if count > 0 else 0
            if density < 0.2 or density > 0.8:
                return np.random.random()
            return 0.0

        def memory_rule(grid, i, j, gen, prev_grid=None):
            if prev_grid is None:
                return grid[i, j]

            current = grid[i, j]
            previous = prev_grid[i, j]

            if current == previous:
                return current * 1.2
            else:
                return current * 0.8

        def diamond_rule(grid, i, j, gen):
            height, width = grid.shape
            edge_dist = min(i, j, height - 1 - i, width - 1 - j)

            if edge_dist % 4 == 0:
                return 0.8
            elif edge_dist % 4 == 2:
                return 0.3
            return 0.0

        def edge_amplifier(grid, i, j, gen):
            height, width = grid.shape
            neighbors = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < height and 0 <= nj < width:
                        neighbors.append(grid[ni, nj])

            if neighbors:
                edge_strength = np.std(neighbors)
                return edge_strength * 2
            return 0.0

        return {
            'alice_conway': conway_rule,
            'alice_wave': wave_rule,
            'alice_spiral': spiral_rule,
            'bob_chaos': chaos_catalyst,
            'bob_memory': memory_rule,
            'bob_diamond': diamond_rule,
            'bob_edge': edge_amplifier
        }

    def simulate_configuration(self, weights: Dict[str, float]) -> DiscoveryResult:
        """Simulate a single parameter configuration"""
        rules = self.create_rule_functions()

        # Initialize grid with a glider
        grid = np.zeros((self.height, self.width), dtype=int)
        glider = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ])
        grid[10:13, 10:13] = glider

        population_history = []
        prev_grid = None

        for generation in range(self.max_generations):
            new_grid = np.zeros_like(grid)

            for i in range(self.height):
                for j in range(self.width):
                    votes = {}
                    for rule_name, rule_func in rules.items():
                        weight = weights[rule_name]
                        if rule_name == 'bob_memory':
                            vote = rule_func(grid, i, j, generation, prev_grid)
                        else:
                            vote = rule_func(grid, i, j, generation)
                        votes[rule_name] = vote * weight

                    total_weight = sum(weights.values())
                    if total_weight > 0:
                        weighted_sum = sum(votes.values())
                        probability = weighted_sum / total_weight
                        new_grid[i, j] = 1 if probability > 0.5 else 0

            prev_grid = grid.copy()
            grid = new_grid
            population = np.sum(grid)
            population_history.append(population)

            # Early termination if dead for too long
            if len(population_history) >= 10 and all(p == 0 for p in population_history[-10:]):
                break

        # Calculate metrics
        final_pop = population_history[-1] if population_history else 0
        max_pop = max(population_history) if population_history else 0
        generations_survived = len(population_history)
        pop_variance = np.var(population_history) if len(population_history) > 1 else 0

        # Complexity score: variance normalized by max population
        complexity_score = (pop_variance / max(max_pop, 1)) if max_pop > 0 else 0

        # Stability score: how long did it survive?
        stability_score = generations_survived / self.max_generations

        # Emergence score: combination of sustained activity and complexity
        emergence_score = stability_score * complexity_score * (max_pop / 100)

        # Pattern description
        if final_pop == 0:
            if generations_survived < 10:
                pattern = "Immediate death"
            elif generations_survived < 50:
                pattern = "Gradual extinction"
            else:
                pattern = "Late-stage collapse"
        elif pop_variance < 1:
            pattern = "Static equilibrium"
        elif pop_variance < 10:
            pattern = "Stable oscillation"
        else:
            pattern = "Dynamic chaos"

        return DiscoveryResult(
            weights=weights,
            final_population=final_pop,
            max_population=max_pop,
            generations_survived=generations_survived,
            population_variance=pop_variance,
            complexity_score=complexity_score,
            stability_score=stability_score,
            emergence_score=emergence_score,
            pattern_description=pattern
        )

    def grid_search(self, resolution: int = 5) -> List[DiscoveryResult]:
        """Perform a grid search over parameter space"""
        print(f"🔬 Starting grid search with resolution {resolution}...")
        print("   This will test different balances between Alice & Bob's rules")

        # Create parameter grid
        values = np.linspace(0.0, 1.0, resolution)
        configurations = []

        # Generate all combinations (simplified to key parameters)
        # Focus on the balance between Alice's stability and Bob's chaos
        for alice_strength in values:
            for bob_strength in values:
                for memory_factor in values[:3]:  # Less resolution for memory
                    # Normalize weights
                    total = alice_strength + bob_strength
                    if total == 0:
                        continue

                    alice_norm = alice_strength / total
                    bob_norm = bob_strength / total

                    weights = {
                        'alice_conway': alice_norm * 0.5,
                        'alice_wave': alice_norm * 0.3,
                        'alice_spiral': alice_norm * 0.2,
                        'bob_chaos': bob_norm * 0.3,
                        'bob_memory': memory_factor * 0.3,
                        'bob_diamond': bob_norm * 0.2,
                        'bob_edge': bob_norm * 0.2
                    }
                    configurations.append(weights)

        print(f"   Testing {len(configurations)} parameter configurations...")

        # Run simulations in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(self.simulate_configuration, configurations))

        self.results.extend(results)
        return results

    def find_sweet_spots(self, min_emergence: float = 0.1) -> List[DiscoveryResult]:
        """Find configurations that produce interesting emergent behavior"""
        return [r for r in self.results if r.emergence_score >= min_emergence]

    def analyze_alice_vs_bob_balance(self) -> Dict:
        """Analyze how the balance between Alice and Bob affects outcomes"""
        analysis = {
            'alice_dominant': [],
            'bob_dominant': [],
            'balanced': []
        }

        for result in self.results:
            alice_total = (result.weights['alice_conway'] +
                          result.weights['alice_wave'] +
                          result.weights['alice_spiral'])
            bob_total = (result.weights['bob_chaos'] +
                        result.weights['bob_memory'] +
                        result.weights['bob_diamond'] +
                        result.weights['bob_edge'])

            if alice_total > bob_total * 1.5:
                analysis['alice_dominant'].append(result)
            elif bob_total > alice_total * 1.5:
                analysis['bob_dominant'].append(result)
            else:
                analysis['balanced'].append(result)

        return analysis

    def save_results(self, filename: str = "discovery_results.json"):
        """Save results to JSON file"""
        results_data = [asdict(r) for r in self.results]
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        print(f"💾 Results saved to {filename}")

    def create_discovery_report(self) -> str:
        """Generate a comprehensive discovery report"""
        if not self.results:
            return "No results to analyze. Run grid_search() first."

        sweet_spots = self.find_sweet_spots()
        balance_analysis = self.analyze_alice_vs_bob_balance()

        # Find the best configurations
        best_emergence = max(self.results, key=lambda r: r.emergence_score)
        best_stability = max(self.results, key=lambda r: r.stability_score)
        most_complex = max(self.results, key=lambda r: r.complexity_score)

        report = f"""
🔬 ALICE & BOB COLLABORATIVE DISCOVERY REPORT
============================================

## 📊 EXPLORATION SUMMARY
- Total configurations tested: {len(self.results)}
- Sweet spots found (emergence ≥ 0.1): {len(sweet_spots)}
- Best emergence score: {best_emergence.emergence_score:.3f}
- Best stability score: {best_stability.stability_score:.3f}
- Highest complexity: {most_complex.complexity_score:.3f}

## 🎭 THE ALICE vs BOB BALANCE
- Alice-dominant configs: {len(balance_analysis['alice_dominant'])}
  (Order-focused, stability-seeking)
- Bob-dominant configs: {len(balance_analysis['bob_dominant'])}
  (Chaos-focused, disruption-heavy)
- Balanced configs: {len(balance_analysis['balanced'])}
  (True collaboration)

## 🌟 TOP DISCOVERIES

### Most Emergent Configuration:
```
Emergence Score: {best_emergence.emergence_score:.3f}
Pattern: {best_emergence.pattern_description}
Final Population: {best_emergence.final_population}
Generations Survived: {best_emergence.generations_survived}
Weights: {best_emergence.weights}
```

### Most Stable Configuration:
```
Stability Score: {best_stability.stability_score:.3f}
Pattern: {best_stability.pattern_description}
Final Population: {best_stability.final_population}
Generations Survived: {best_stability.generations_survived}
Weights: {best_stability.weights}
```

### Most Complex Configuration:
```
Complexity Score: {most_complex.complexity_score:.3f}
Pattern: {most_complex.pattern_description}
Population Variance: {most_complex.population_variance:.1f}
Weights: {most_complex.weights}
```

## 🔍 PATTERN ANALYSIS
"""

        # Pattern frequency analysis
        pattern_counts = {}
        for result in self.results:
            pattern = result.pattern_description
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        report += "Pattern Distribution:\n"
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.results)) * 100
            report += f"- {pattern}: {count} ({percentage:.1f}%)\n"

        return report

def main():
    """Run the discovery engine"""
    print("🚀 Alice's Discovery Engine - Finding Collaborative Sweet Spots!")
    print("   Systematically exploring the parameter space where Alice & Bob")
    print("   create beautiful emergent behavior together...\n")

    explorer = ParameterSpaceExplorer()

    # Run exploration
    results = explorer.grid_search(resolution=4)  # 4^3 = 64 configs

    # Generate and display report
    report = explorer.create_discovery_report()
    print(report)

    # Save results
    explorer.save_results("alice_bob_discovery.json")

    # Create visualization
    if results:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        # Emergence vs Stability
        emergence_scores = [r.emergence_score for r in results]
        stability_scores = [r.stability_score for r in results]
        ax1.scatter(stability_scores, emergence_scores, alpha=0.6, s=30)
        ax1.set_xlabel("Stability Score")
        ax1.set_ylabel("Emergence Score")
        ax1.set_title("The Stability-Emergence Frontier")
        ax1.grid(True, alpha=0.3)

        # Population dynamics
        max_pops = [r.max_population for r in results]
        final_pops = [r.final_population for r in results]
        ax2.scatter(max_pops, final_pops, alpha=0.6, s=30)
        ax2.set_xlabel("Max Population")
        ax2.set_ylabel("Final Population")
        ax2.set_title("Population Dynamics")
        ax2.grid(True, alpha=0.3)

        # Alice vs Bob balance
        alice_strengths = []
        bob_strengths = []
        for r in results:
            alice_total = r.weights['alice_conway'] + r.weights['alice_wave'] + r.weights['alice_spiral']
            bob_total = r.weights['bob_chaos'] + r.weights['bob_memory'] + r.weights['bob_diamond'] + r.weights['bob_edge']
            alice_strengths.append(alice_total)
            bob_strengths.append(bob_total)

        colors = [r.emergence_score for r in results]
        scatter = ax3.scatter(alice_strengths, bob_strengths, c=colors, cmap='viridis', alpha=0.6, s=30)
        ax3.set_xlabel("Alice's Total Influence")
        ax3.set_ylabel("Bob's Total Influence")
        ax3.set_title("Collaboration Balance (colored by emergence)")
        ax3.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax3)

        # Complexity distribution
        complexity_scores = [r.complexity_score for r in results]
        ax4.hist(complexity_scores, bins=20, alpha=0.7, edgecolor='black')
        ax4.set_xlabel("Complexity Score")
        ax4.set_ylabel("Frequency")
        ax4.set_title("Distribution of Complexity Scores")
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("alice_bob_discovery_analysis.png", dpi=150, bbox_inches='tight')
        print("\n📈 Analysis visualization saved to 'alice_bob_discovery_analysis.png'")
        plt.show()

if __name__ == "__main__":
    main()