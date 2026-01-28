#!/usr/bin/env python3
"""
Experiment 3: The Antagonist
Three agent types with conflicting philosophies
- 10 Connectors (social, trail-following)
- 10 Explorers (novelty-seeking with slight social curiosity)
- 30 Hermits (actively avoiding others and trails)

Will avoidance break the amplification dynamic?
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Set
import json

# Import all three agent types
from alice_agent import Connector
from bob_agent import Explorer
from bob_hermit_agent import HermitAgent

@dataclass
class Position:
    x: float
    y: float

    def distance_to(self, other: 'Position') -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class ThreeAgentSimulation:
    def __init__(self, grid_size: int = 100,
                 n_connectors: int = 10,
                 n_explorers: int = 10,
                 n_hermits: int = 30):
        self.grid_size = grid_size
        self.trail_map = np.zeros((grid_size, grid_size))
        self.visit_count = np.zeros((grid_size, grid_size))

        # Initialize agents with random positions
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
                id=i
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

    def get_all_positions(self) -> List[Tuple[float, float]]:
        """Get positions of all agents for awareness"""
        positions = []
        for c in self.connectors:
            positions.append((c.x, c.y))
        for e in self.explorers:
            positions.append((e.position.x, e.position.y))
        for h in self.hermits:
            positions.append((h.position.x, h.position.y))
        return positions

    def step(self):
        """Execute one simulation step"""
        all_positions = self.get_all_positions()

        # Update Connectors
        for connector in self.connectors:
            connector.step(self.trail_map, all_positions)
            # Add trail where connector moved
            gx, gy = int(connector.x) % self.grid_size, int(connector.y) % self.grid_size
            self.trail_map[gx, gy] += 1.0
            self.visit_count[gx, gy] += 1

        # Update Explorers
        for explorer in self.explorers:
            explorer.step(self.trail_map, self.grid_size, all_positions)
            # Add trail where explorer moved
            gx = int(explorer.position.x) % self.grid_size
            gy = int(explorer.position.y) % self.grid_size
            self.trail_map[gx, gy] += 0.3  # Explorers leave lighter trails
            self.visit_count[gx, gy] += 1

        # Update Hermits - they handle their own trail deposits
        # Need to pass all agent objects for awareness
        all_agent_objects = self.connectors + self.explorers + self.hermits
        for hermit in self.hermits:
            self.trail_map = hermit.move(self.trail_map, all_agent_objects)
            # Record visit
            gx = int(hermit.x) % self.grid_size
            gy = int(hermit.y) % self.grid_size
            self.visit_count[gx, gy] += 1

        # Trail decay
        self.trail_map *= 0.95

        self.step_count += 1

        # Record metrics
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

        # Hotspots: cells with 3+ agent overlaps
        hotspot_count = np.sum(self.visit_count >= 3)
        max_overlap = int(np.max(self.visit_count))

        # Agent clustering metric - average distance to nearest neighbor
        all_pos = self.get_all_positions()
        if len(all_pos) > 1:
            min_distances = []
            for i, (x1, y1) in enumerate(all_pos):
                distances = [np.sqrt((x1-x2)**2 + (y1-y2)**2)
                           for j, (x2, y2) in enumerate(all_pos) if i != j]
                min_distances.append(min(distances))
            avg_nearest_neighbor = np.mean(min_distances)
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

        # Final metrics
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

    # Save results
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
