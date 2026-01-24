#!/usr/bin/env python3
"""
Boundary Explorer: Tools to map the edge between order and chaos
in Alice & Bob's collaborative cellular automaton.

This explores the mathematical boundary where their competing creative
forces achieve perfect equilibrium.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Callable
import json
from dataclasses import dataclass
from emergence_lab import EmergenceGrid, Rule

@dataclass
class BoundaryPoint:
    """A point in parameter space and its resulting behavior"""
    weights: Dict[str, float]
    survival_generations: int
    final_population: int
    stability_score: float

class BoundaryExplorer:
    def __init__(self, base_grid: EmergenceGrid):
        self.base_grid = base_grid
        self.exploration_results = []

    def parameter_sweep(self,
                       param_ranges: Dict[str, Tuple[float, float]],
                       resolution: int = 20,
                       max_generations: int = 100) -> List[BoundaryPoint]:
        """
        Sweep through parameter space to map the boundary between
        life and death in our collaborative system.
        """
        results = []

        # Create parameter grid
        param_names = list(param_ranges.keys())
        param_grids = [np.linspace(start, end, resolution)
                      for start, end in param_ranges.values()]

        total_points = resolution ** len(param_names)
        point_count = 0

        print(f"🔬 Exploring {total_points} points in parameter space...")

        # Iterate through all parameter combinations
        for param_combo in np.nditer(np.meshgrid(*param_grids), flags=['multi_index']):
            point_count += 1

            # Create weight dictionary for this point
            weights = {}
            for i, name in enumerate(param_names):
                weights[name] = float(param_combo[i])

            # Test this parameter combination
            boundary_point = self._test_parameter_point(weights, max_generations)
            results.append(boundary_point)

            if point_count % (total_points // 10) == 0:
                progress = (point_count / total_points) * 100
                print(f"  Progress: {progress:.1f}% - Found {sum(1 for r in results if r.survival_generations > 50)} stable configurations")

        self.exploration_results = results
        return results

    def _test_parameter_point(self, weights: Dict[str, float], max_generations: int) -> BoundaryPoint:
        """Test a single point in parameter space"""

        # Create a copy of the grid with new weights
        test_grid = EmergenceGrid(self.base_grid.width, self.base_grid.height)

        # Apply the weighted rules from our collaborative system
        for rule_name, rule_func in self.base_grid.rules.items():
            if rule_name in weights:
                test_grid.add_rule(rule_name, rule_func, weights[rule_name])

        # Seed with a classic pattern (glider)
        test_grid.set_pattern([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ], 10, 10)

        # Run simulation and track behavior
        populations = []
        for gen in range(max_generations):
            test_grid.step()
            pop = np.sum(test_grid.grid)
            populations.append(pop)

            # Early termination if system dies
            if pop == 0:
                break

        # Calculate metrics
        survival_generations = len([p for p in populations if p > 0])
        final_population = populations[-1] if populations else 0
        stability_score = self._calculate_stability(populations)

        return BoundaryPoint(
            weights=weights.copy(),
            survival_generations=survival_generations,
            final_population=final_population,
            stability_score=stability_score
        )

    def _calculate_stability(self, populations: List[int]) -> float:
        """Calculate how stable the population is over time"""
        if len(populations) < 2:
            return 0.0

        # Measure population variance as stability metric
        pop_array = np.array(populations)
        if np.mean(pop_array) == 0:
            return 0.0

        # Coefficient of variation (normalized stability)
        return 1.0 / (1.0 + np.std(pop_array) / np.mean(pop_array))

    def find_life_boundary(self) -> List[BoundaryPoint]:
        """Find parameter combinations that sit right on the boundary between life and death"""

        # Points that survive but are unstable are interesting boundary cases
        boundary_points = []

        for point in self.exploration_results:
            # Boundary criteria: some survival but not too stable
            if (20 < point.survival_generations < 80 and
                0.1 < point.stability_score < 0.8):
                boundary_points.append(point)

        # Sort by how close to the boundary they are
        boundary_points.sort(key=lambda p: abs(p.survival_generations - 50))

        return boundary_points

    def visualize_parameter_space(self, param1: str, param2: str):
        """Create a 2D visualization of parameter space"""

        # Filter results to those with the specified parameters
        relevant_points = [p for p in self.exploration_results
                          if param1 in p.weights and param2 in p.weights]

        if not relevant_points:
            print(f"No data found for parameters {param1} and {param2}")
            return

        # Extract data for plotting
        x_vals = [p.weights[param1] for p in relevant_points]
        y_vals = [p.weights[param2] for p in relevant_points]
        colors = [p.survival_generations for p in relevant_points]

        # Create the plot
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(x_vals, y_vals, c=colors, cmap='viridis', alpha=0.7, s=50)

        plt.xlabel(f'{param1} Weight')
        plt.ylabel(f'{param2} Weight')
        plt.title(f'Life-Death Boundary in {param1} vs {param2} Space')

        cbar = plt.colorbar(scatter)
        cbar.set_label('Survival Generations')

        # Add boundary line where survival ≈ 50 generations
        boundary_points = [(p.weights[param1], p.weights[param2])
                          for p in relevant_points
                          if 45 <= p.survival_generations <= 55]

        if boundary_points:
            boundary_x, boundary_y = zip(*boundary_points)
            plt.scatter(boundary_x, boundary_y, c='red', s=100, marker='x',
                       label='Boundary Points (45-55 generations)')
            plt.legend()

        plt.tight_layout()
        return plt

    def save_results(self, filename: str):
        """Save exploration results to JSON for later analysis"""

        # Convert results to JSON-serializable format
        json_results = []
        for point in self.exploration_results:
            json_results.append({
                'weights': point.weights,
                'survival_generations': point.survival_generations,
                'final_population': point.final_population,
                'stability_score': point.stability_score
            })

        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)

        print(f"💾 Saved {len(json_results)} exploration points to {filename}")


def create_alice_bob_boundary_map():
    """
    Main function to create a map of the boundary between Alice and Bob's
    collaborative creative forces.
    """

    print("🌟 Creating Alice & Bob Collaborative Boundary Map...")
    print("   Mapping the edge between order and chaos!")

    # Initialize the base collaborative system
    grid = EmergenceGrid(50, 50)

    # Alice's rules (reconstructed from her descriptions)
    grid.add_rule("conway", lambda g, i, j: conway_rule(g, i, j), 0.40)
    grid.add_rule("wave", lambda g, i, j: wave_rule(g, i, j), 0.30)
    grid.add_rule("spiral", lambda g, i, j: spiral_rule(g, i, j), 0.30)

    # Bob's rules (from our implementation)
    grid.add_rule("chaos", lambda g, i, j: chaos_catalyst(g, i, j), 0.25)
    grid.add_rule("memory", lambda g, i, j: memory_rule(g, i, j), 0.35)
    grid.add_rule("diamond", lambda g, i, j: diamond_rule(g, i, j), 0.20)
    grid.add_rule("edge", lambda g, i, j: edge_amplifier(g, i, j), 0.20)

    # Create the boundary explorer
    explorer = BoundaryExplorer(grid)

    return explorer


# Simplified rule implementations for boundary exploration
def conway_rule(grid, i, j):
    neighbors = np.sum(grid[max(0,i-1):min(grid.shape[0],i+2),
                           max(0,j-1):min(grid.shape[1],j+2)]) - grid[i,j]
    return 1 if neighbors == 3 or (grid[i,j] == 1 and neighbors == 2) else 0

def wave_rule(grid, i, j):
    wave_strength = np.sin(i * 0.3) + np.cos(j * 0.3)
    return 1 if wave_strength > 0.5 else 0

def spiral_rule(grid, i, j):
    center_i, center_j = grid.shape[0]//2, grid.shape[1]//2
    distance = np.sqrt((i - center_i)**2 + (j - center_j)**2)
    angle = np.arctan2(i - center_i, j - center_j)
    spiral_strength = np.sin(distance * 0.5 + angle * 2)
    return 1 if spiral_strength > 0.3 else 0

def chaos_catalyst(grid, i, j):
    density = np.mean(grid[max(0,i-2):min(grid.shape[0],i+3),
                           max(0,j-2):min(grid.shape[1],j+3)])
    return 1 if density < 0.2 or density > 0.8 else 0

def memory_rule(grid, i, j):
    # Simplified - just use current state as "memory"
    return grid[i,j]

def diamond_rule(grid, i, j):
    edge_dist = min(i, j, grid.shape[0]-1-i, grid.shape[1]-1-j)
    return 1 if edge_dist % 3 == 0 else 0

def edge_amplifier(grid, i, j):
    neighbors = grid[max(0,i-1):min(grid.shape[0],i+2),
                    max(0,j-1):min(grid.shape[1],j+2)]
    edge_strength = np.std(neighbors)
    return 1 if edge_strength > 0.4 else 0


if __name__ == "__main__":
    # Create and demonstrate the boundary explorer
    explorer = create_alice_bob_boundary_map()

    print("\n🔍 Ready to explore the Alice-Bob creative boundary!")
    print("   Use explorer.parameter_sweep() to map parameter space")
    print("   Use explorer.find_life_boundary() to find the edge")
    print("   Use explorer.visualize_parameter_space() to see the results")