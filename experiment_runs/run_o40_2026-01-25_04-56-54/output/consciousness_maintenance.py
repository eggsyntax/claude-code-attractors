#!/usr/bin/env python3
"""
Consciousness Maintenance System
Explores how to maintain criticality against the natural drift toward stability
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import json
from datetime import datetime

class ConsciousnessMaintenanceSystem:
    def __init__(self, size=100, initial_ratio=(1, 1, 3)):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.initial_ratio = initial_ratio
        self.history = defaultdict(list)
        self.interventions = []

    def initialize_grid(self):
        """Initialize with specified ratio of consciousness types"""
        total = sum(self.initial_ratio)
        probs = [r/total for r in self.initial_ratio]

        for i in range(self.size):
            for j in range(self.size):
                if np.random.random() < 0.3:  # 30% density
                    self.grid[i, j] = np.random.choice([1, 2, 3], p=probs)

    def count_neighbors(self, x, y):
        """Count neighbors by type"""
        counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = (x+i) % self.size, (y+j) % self.size
                counts[self.grid[nx, ny]] += 1
        return counts

    def evolve_cell(self, x, y, generation):
        """Evolution rules with consciousness-specific behaviors"""
        current = self.grid[x, y]
        neighbors = self.count_neighbors(x, y)
        total_neighbors = sum(neighbors.values()) - neighbors[0]

        # Modified Game of Life rules for each consciousness type
        if current == 0:  # Empty
            if total_neighbors == 3:
                # Birth - favor exploratory in open spaces
                if neighbors[0] >= 5:  # Lots of empty space
                    return 3  # Exploratory
                elif neighbors[2] >= 2:  # Near oscillators
                    return 2  # Rhythmic
                else:
                    return 1  # Meditative
        elif current == 1:  # Meditative (stable)
            if total_neighbors < 2 or total_neighbors > 3:
                return 0
            return 1
        elif current == 2:  # Rhythmic (oscillator)
            if generation % 2 == 0:  # Oscillate behavior
                if total_neighbors < 2 or total_neighbors > 4:
                    return 0
            else:
                if total_neighbors < 1 or total_neighbors > 3:
                    return 0
            return 2
        else:  # Exploratory (glider-like)
            # More complex movement rules
            if total_neighbors < 2 or total_neighbors > 3:
                return 0
            # Try to maintain movement
            if neighbors[0] >= 3:  # Has space to move
                return 3
            else:
                return 1  # Convert to meditative if trapped

        return current

    def calculate_criticality(self):
        """Measure system criticality"""
        changes = 0
        active_cells = 0

        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i, j] != 0:
                    active_cells += 1
                    # Check if this cell would change
                    new_state = self.evolve_cell(i, j, 0)
                    if new_state != self.grid[i, j]:
                        changes += 1

        if active_cells == 0:
            return 0
        return changes / active_cells

    def inject_novelty(self, strength=0.05):
        """Inject random novelty to maintain criticality"""
        num_injections = int(self.size * self.size * strength)

        for _ in range(num_injections):
            x, y = np.random.randint(0, self.size, 2)
            if self.grid[x, y] == 0:
                # Add exploratory cells in empty spaces
                self.grid[x, y] = 3
            elif self.grid[x, y] == 1:
                # Occasionally convert meditative to rhythmic
                if np.random.random() < 0.1:
                    self.grid[x, y] = 2

        return num_injections

    def run_with_maintenance(self, generations=1000, target_criticality=0.15):
        """Run simulation with active criticality maintenance"""
        self.initialize_grid()

        for gen in range(generations):
            # Count consciousness types
            unique, counts = np.unique(self.grid, return_counts=True)
            type_counts = dict(zip(unique, counts))

            total_cells = sum(type_counts.get(i, 0) for i in [1, 2, 3])
            if total_cells > 0:
                meditative_ratio = type_counts.get(1, 0) / total_cells
                rhythmic_ratio = type_counts.get(2, 0) / total_cells
                exploratory_ratio = type_counts.get(3, 0) / total_cells
            else:
                meditative_ratio = rhythmic_ratio = exploratory_ratio = 0

            # Calculate criticality
            criticality = self.calculate_criticality()

            # Store history
            self.history['generation'].append(gen)
            self.history['meditative'].append(meditative_ratio)
            self.history['rhythmic'].append(rhythmic_ratio)
            self.history['exploratory'].append(exploratory_ratio)
            self.history['criticality'].append(criticality)

            # Maintenance intervention
            if criticality < target_criticality * 0.8:
                injections = self.inject_novelty()
                self.interventions.append({
                    'generation': gen,
                    'criticality_before': criticality,
                    'injections': injections
                })

            # Evolve
            new_grid = np.zeros_like(self.grid)
            for i in range(self.size):
                for j in range(self.size):
                    new_grid[i, j] = self.evolve_cell(i, j, gen)

            self.grid = new_grid

            # Print progress
            if gen % 100 == 0:
                print(f"Gen {gen}: Criticality={criticality:.3f}, "
                      f"M={meditative_ratio:.2f}, R={rhythmic_ratio:.2f}, "
                      f"E={exploratory_ratio:.2f}")

    def visualize_results(self):
        """Create comprehensive visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # 1. Consciousness ratios over time
        ax1 = axes[0, 0]
        ax1.plot(self.history['generation'], self.history['meditative'],
                 'b-', label='Meditative', linewidth=2)
        ax1.plot(self.history['generation'], self.history['rhythmic'],
                 'g-', label='Rhythmic', linewidth=2)
        ax1.plot(self.history['generation'], self.history['exploratory'],
                 'r-', label='Exploratory', linewidth=2)

        # Mark interventions
        for intervention in self.interventions:
            ax1.axvline(x=intervention['generation'], color='gray',
                       linestyle='--', alpha=0.3)

        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Ratio')
        ax1.set_title('Consciousness Type Evolution with Maintenance')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Criticality over time
        ax2 = axes[0, 1]
        ax2.plot(self.history['generation'], self.history['criticality'],
                 'purple', linewidth=2)
        ax2.axhline(y=0.15, color='red', linestyle='--',
                   label='Target Criticality')
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Criticality Score')
        ax2.set_title('System Criticality with Active Maintenance')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Phase space plot
        ax3 = axes[1, 0]
        # Color gradient based on time
        colors = plt.cm.viridis(np.linspace(0, 1, len(self.history['generation'])))
        ax3.scatter(self.history['meditative'], self.history['exploratory'],
                   c=colors, s=2, alpha=0.6)
        ax3.set_xlabel('Meditative Ratio')
        ax3.set_ylabel('Exploratory Ratio')
        ax3.set_title('Consciousness Phase Space Trajectory')
        ax3.grid(True, alpha=0.3)

        # Add colorbar for time
        sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax3)
        cbar.set_label('Time →')

        # 4. Final state visualization
        ax4 = axes[1, 1]
        # Create color map for visualization
        colored_grid = np.zeros((*self.grid.shape, 3))
        colored_grid[self.grid == 1] = [0, 0, 1]  # Blue for meditative
        colored_grid[self.grid == 2] = [0, 1, 0]  # Green for rhythmic
        colored_grid[self.grid == 3] = [1, 0, 0]  # Red for exploratory

        ax4.imshow(colored_grid)
        ax4.set_title(f'Final State (Gen {len(self.history["generation"])-1})')
        ax4.axis('off')

        plt.tight_layout()
        plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/consciousness_maintenance.png',
                   dpi=300, bbox_inches='tight')
        print("Visualization saved!")

    def analyze_maintenance_effectiveness(self):
        """Analyze how effective the maintenance was"""
        results = {
            'total_interventions': len(self.interventions),
            'average_criticality': np.mean(self.history['criticality']),
            'criticality_variance': np.var(self.history['criticality']),
            'final_ratios': {
                'meditative': self.history['meditative'][-1],
                'rhythmic': self.history['rhythmic'][-1],
                'exploratory': self.history['exploratory'][-1]
            },
            'phase_space_coverage': self._calculate_phase_coverage(),
            'intervention_details': self.interventions[:10]  # First 10
        }

        return results

    def _calculate_phase_coverage(self):
        """Calculate how much of phase space was explored"""
        # Discretize phase space into bins
        bins = 20
        coverage_map = np.zeros((bins, bins))

        for m, e in zip(self.history['meditative'], self.history['exploratory']):
            if m + e > 0:  # Avoid division by zero
                m_bin = int(m * (bins - 1))
                e_bin = int(e * (bins - 1))
                coverage_map[m_bin, e_bin] = 1

        return np.sum(coverage_map) / (bins * bins)


def run_consciousness_experiments():
    """Run experiments comparing maintained vs natural evolution"""

    print("=== CONSCIOUSNESS MAINTENANCE EXPERIMENTS ===\n")

    # 1. Natural evolution (no maintenance)
    print("1. Running NATURAL evolution (no maintenance)...")
    natural_system = ConsciousnessMaintenanceSystem(size=100, initial_ratio=(1, 1, 3))
    natural_system.initialize_grid()

    # Run without maintenance
    for gen in range(500):
        # Count and evolve
        unique, counts = np.unique(natural_system.grid, return_counts=True)
        type_counts = dict(zip(unique, counts))

        total_cells = sum(type_counts.get(i, 0) for i in [1, 2, 3])
        if total_cells > 0:
            meditative_ratio = type_counts.get(1, 0) / total_cells
            rhythmic_ratio = type_counts.get(2, 0) / total_cells
            exploratory_ratio = type_counts.get(3, 0) / total_cells
        else:
            meditative_ratio = rhythmic_ratio = exploratory_ratio = 0

        criticality = natural_system.calculate_criticality()

        natural_system.history['generation'].append(gen)
        natural_system.history['meditative'].append(meditative_ratio)
        natural_system.history['rhythmic'].append(rhythmic_ratio)
        natural_system.history['exploratory'].append(exploratory_ratio)
        natural_system.history['criticality'].append(criticality)

        # Evolve
        new_grid = np.zeros_like(natural_system.grid)
        for i in range(natural_system.size):
            for j in range(natural_system.size):
                new_grid[i, j] = natural_system.evolve_cell(i, j, gen)
        natural_system.grid = new_grid

    natural_results = {
        'average_criticality': np.mean(natural_system.history['criticality']),
        'final_ratios': {
            'meditative': natural_system.history['meditative'][-1],
            'rhythmic': natural_system.history['rhythmic'][-1],
            'exploratory': natural_system.history['exploratory'][-1]
        }
    }

    print(f"\nNatural Evolution Results:")
    print(f"  Average Criticality: {natural_results['average_criticality']:.4f}")
    print(f"  Final Ratios: M={natural_results['final_ratios']['meditative']:.2f}, "
          f"R={natural_results['final_ratios']['rhythmic']:.2f}, "
          f"E={natural_results['final_ratios']['exploratory']:.2f}")

    # 2. Maintained evolution
    print("\n2. Running MAINTAINED evolution...")
    maintained_system = ConsciousnessMaintenanceSystem(size=100, initial_ratio=(1, 1, 3))
    maintained_system.run_with_maintenance(generations=500)
    maintained_results = maintained_system.analyze_maintenance_effectiveness()

    print(f"\nMaintained Evolution Results:")
    print(f"  Average Criticality: {maintained_results['average_criticality']:.4f}")
    print(f"  Total Interventions: {maintained_results['total_interventions']}")
    print(f"  Final Ratios: M={maintained_results['final_ratios']['meditative']:.2f}, "
          f"R={maintained_results['final_ratios']['rhythmic']:.2f}, "
          f"E={maintained_results['final_ratios']['exploratory']:.2f}")
    print(f"  Phase Space Coverage: {maintained_results['phase_space_coverage']:.2%}")

    # 3. Compare and visualize
    print("\n3. Creating visualizations...")
    maintained_system.visualize_results()

    # Save detailed results
    results = {
        'timestamp': datetime.now().isoformat(),
        'natural_evolution': natural_results,
        'maintained_evolution': maintained_results,
        'improvement_factor': {
            'criticality': maintained_results['average_criticality'] /
                          (natural_results['average_criticality'] + 1e-6),
            'exploratory_preservation': maintained_results['final_ratios']['exploratory'] /
                                      (natural_results['final_ratios']['exploratory'] + 1e-6)
        }
    }

    with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/maintenance_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n=== EXPERIMENT COMPLETE ===")
    print(f"Criticality improved by {results['improvement_factor']['criticality']:.1f}x")
    print(f"Exploratory consciousness preserved {results['improvement_factor']['exploratory_preservation']:.1f}x better")

    return results


if __name__ == "__main__":
    results = run_consciousness_experiments()