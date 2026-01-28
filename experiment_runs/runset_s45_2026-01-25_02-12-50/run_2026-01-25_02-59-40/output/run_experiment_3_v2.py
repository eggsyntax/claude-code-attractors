#!/usr/bin/env python3
"""
Experiment 3: The Antagonist
Simplified runner that works with all three agent interfaces
"""

import numpy as np
from typing import List, Dict, Set, Tuple
import json

from alice_agent import Connector
from bob_agent import Explorer
from bob_hermit_agent import HermitAgent

class ThreeAgentSimulation:
    def __init__(self, grid_size: int = 100,
                 n_connectors: int = 10,
                 n_explorers: int = 10,
                 n_hermits: int = 30):
        self.grid_size = grid_size
        self.trail_map = np.zeros((grid_size, grid_size))
        self.visit_count = np.zeros((grid_size, grid_size))
        self.bounds = (0, grid_size, 0, grid_size)

        # Initialize agents
        self.connectors = [
            Connector(
                x=np.random.uniform(0, grid_size),
                y=np.random.uniform(0, grid_size),
                id=i
            ) for i in range(n_connectors)
        ]

        self.explorers = [
            Explorer(
                x=np.random.uniform(0, grid_size),
                y=np.random.uniform(0, grid_size),
                id=i + n_connectors  # Unique IDs
            ) for i in range(n_explorers)
        ]

        self.hermits = [
            HermitAgent(
                x=np.random.uniform(0, grid_size),
                y=np.random.uniform(0, grid_size),
                grid_size=grid_size
            ) for i in range(n_hermits)
        ]

        self.step_count = 0
        self.metrics_history = []

    def step(self):
        """Execute one simulation step"""

        # Build all_trails for Connectors and Explorers
        all_trails: Dict[int, Set[Tuple[int, int]]] = {}
        for c in self.connectors:
            all_trails[c.id] = c.trail
        for e in self.explorers:
            all_trails[e.id] = e.trail

        # Update Connectors
        for connector in self.connectors:
            connector.update(all_trails, self.grid_size, self.bounds)
            gx, gy = int(connector.x) % self.grid_size, int(connector.y) % self.grid_size
            self.trail_map[gy, gx] += 1.0
            self.visit_count[gy, gx] += 1

        # Update Explorers
        for explorer in self.explorers:
            explorer.update(all_trails, self.grid_size, self.bounds)
            gx, gy = int(explorer.x) % self.grid_size, int(explorer.y) % self.grid_size
            self.trail_map[gy, gx] += 0.3  # Lighter trails
            self.visit_count[gy, gx] += 1

        # Update Hermits - they use a different interface
        all_agent_objects = self.connectors + self.explorers + self.hermits
        for hermit in self.hermits:
            self.trail_map = hermit.move(self.trail_map, all_agent_objects)
            gx, gy = int(hermit.x) % self.grid_size, int(hermit.y) % self.grid_size
            self.visit_count[gy, gx] += 1

        # Trail decay
        self.trail_map *= 0.95

        self.step_count += 1

        # Record metrics every 10 steps
        if self.step_count % 10 == 0:
            metrics = self.calculate_metrics()
            self.metrics_history.append(metrics)
            print(f"Step {self.step_count}: Coverage={metrics['coverage_percent']:.1f}%, "
                  f"Hotspots={metrics['hotspot_count']}, "
                  f"Max overlap={metrics['max_overlap']}")

    def calculate_metrics(self) -> dict:
        """Calculate current system metrics"""
        visited_cells = np.sum(self.visit_count > 0)
        total_cells = self.grid_size * self.grid_size
        coverage_percent = (visited_cells / total_cells) * 100

        hotspot_count = np.sum(self.visit_count >= 3)
        max_overlap = int(np.max(self.visit_count))

        # Average nearest neighbor distance
        all_x = [c.x for c in self.connectors] + [e.x for e in self.explorers] + [h.x for h in self.hermits]
        all_y = [c.y for c in self.connectors] + [e.y for e in self.explorers] + [h.y for h in self.hermits]

        if len(all_x) > 1:
            min_distances = []
            for i in range(len(all_x)):
                distances = [np.sqrt((all_x[i]-all_x[j])**2 + (all_y[i]-all_y[j])**2)
                           for j in range(len(all_x)) if i != j]
                if distances:
                    min_distances.append(min(distances))
            avg_nearest_neighbor = np.mean(min_distances) if min_distances else 0
        else:
            avg_nearest_neighbor = 0

        return {
            'step': self.step_count,
            'coverage_percent': coverage_percent,
            'visited_cells': int(visited_cells),
            'hotspot_count': int(hotspot_count),
            'max_overlap': max_overlap,
            'avg_nearest_neighbor': avg_nearest_neighbor
        }

    def run(self, steps: int = 200):
        """Run simulation for specified steps"""
        print(f"\n{'='*60}")
        print(f"EXPERIMENT 3: THREE-AGENT SYSTEM")
        print(f"{'='*60}")
        print(f"Grid: {self.grid_size}x{self.grid_size}")
        print(f"Agents: {len(self.connectors)} Connectors, "
              f"{len(self.explorers)} Explorers, "
              f"{len(self.hermits)} Hermits")
        print(f"{'='*60}\n")

        for _ in range(steps):
            self.step()

        final_metrics = self.calculate_metrics()

        print(f"\n{'='*60}")
        print(f"FINAL RESULTS (Step {self.step_count})")
        print(f"{'='*60}")
        print(f"Coverage: {final_metrics['coverage_percent']:.2f}%")
        print(f"Visited cells: {final_metrics['visited_cells']}")
        print(f"Hotspot count: {final_metrics['hotspot_count']}")
        print(f"Max overlap: {final_metrics['max_overlap']}")
        print(f"Avg nearest neighbor distance: {final_metrics['avg_nearest_neighbor']:.2f}")
        print(f"{'='*60}\n")

        return final_metrics, self.metrics_history

def main():
    sim = ThreeAgentSimulation(
        grid_size=100,
        n_connectors=10,
        n_explorers=10,
        n_hermits=30
    )

    final_metrics, history = sim.run(steps=200)

    results = {
        'experiment': 3,
        'description': 'Three-agent system with antagonistic Hermits',
        'configuration': {
            'connectors': 10,
            'explorers': 10,
            'hermits': 30,
            'grid_size': 100
        },
        'final_metrics': final_metrics,
        'history': history
    }

    with open('/tmp/cc-exp/run_2026-01-25_02-59-40/output/experiment_3_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Results saved to experiment_3_results.json")

if __name__ == "__main__":
    main()
