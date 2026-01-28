#!/usr/bin/env python3
"""
EXPERIMENT 4: Critical Threshold Test
======================================
40 Hermits / 5 Connectors / 5 Explorers (80% Hermits)
50 total agents on 100x100 grid
500 steps (extended duration)

QUESTION: Does compression have limits? Is there a critical threshold
where social density cannot overcome dispersal forces?

NO PREDICTIONS. Just observation and post-hoc analysis.
"""

import numpy as np
from typing import List, Dict, Set, Tuple
import json

from alice_agent import Connector
from bob_agent import Explorer
from bob_hermit_agent import HermitAgent

class ExtremeRatioSimulation:
    def __init__(self, grid_size: int = 100,
                 n_connectors: int = 5,
                 n_explorers: int = 5,
                 n_hermits: int = 40):
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
                id=i + n_connectors
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
            self.trail_map[gy, gx] += 0.3
            self.visit_count[gy, gx] += 1

        # Update Hermits
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
            if self.step_count % 50 == 0:
                print(f"Step {self.step_count:3d}: Coverage={metrics['coverage_percent']:5.1f}%, "
                      f"Hotspots={metrics['hotspot_count']:4d}, "
                      f"Max overlap={metrics['max_overlap']:2d}")

    def calculate_metrics(self) -> dict:
        """Calculate current system metrics"""
        visited_cells = np.sum(self.visit_count > 0)
        total_cells = self.grid_size * self.grid_size
        coverage_percent = 100.0 * visited_cells / total_cells

        # Hotspots: cells with 3+ visits
        hotspot_count = np.sum(self.visit_count >= 3)

        # Max overlap
        max_overlap = int(np.max(self.visit_count))

        return {
            'step': self.step_count,
            'coverage_percent': coverage_percent,
            'hotspot_count': hotspot_count,
            'max_overlap': max_overlap,
            'visited_cells': int(visited_cells)
        }

    def run(self, steps: int = 500):
        """Run simulation for specified steps"""
        print("EXPERIMENT 4: Critical Threshold Test")
        print("=" * 60)
        print(f"Configuration: {len(self.hermits)} Hermits / "
              f"{len(self.connectors)} Connectors / {len(self.explorers)} Explorers")
        print(f"Grid: {self.grid_size}x{self.grid_size}, Steps: {steps}")
        print()

        for _ in range(steps):
            self.step()

        # Final results
        print()
        print("=" * 60)
        print("FINAL RESULTS:")
        final = self.metrics_history[-1]
        print(f"Coverage: {final['coverage_percent']:.2f}%")
        print(f"Hotspots: {final['hotspot_count']}")
        print(f"Max Overlap: {final['max_overlap']}")

        # Analyze temporal dynamics
        print()
        print("TEMPORAL DYNAMICS:")

        # Find peaks for each metric
        coverage_peak = max(self.metrics_history, key=lambda m: m['coverage_percent'])
        hotspot_peak = max(self.metrics_history, key=lambda m: m['hotspot_count'])
        overlap_peak = max(self.metrics_history, key=lambda m: m['max_overlap'])

        print(f"Coverage peaked at step {coverage_peak['step']}: {coverage_peak['coverage_percent']:.1f}%")
        print(f"Hotspots peaked at step {hotspot_peak['step']}: {hotspot_peak['hotspot_count']}")
        print(f"Max overlap peaked at step {overlap_peak['step']}: {overlap_peak['max_overlap']}")

        # Check if metrics are still growing, stable, or declining
        last_10 = self.metrics_history[-10:]
        first_5_coverage = np.mean([m['coverage_percent'] for m in last_10[:5]])
        last_5_coverage = np.mean([m['coverage_percent'] for m in last_10[5:]])

        if last_5_coverage > first_5_coverage * 1.02:
            trend = "GROWING"
        elif last_5_coverage < first_5_coverage * 0.98:
            trend = "DECLINING"
        else:
            trend = "STABLE"

        print(f"\nSystem state at end: {trend}")

        # Export detailed log
        with open('experiment_4_detailed_log.txt', 'w') as f:
            f.write("step,coverage,hotspots,max_overlap\n")
            for m in self.metrics_history:
                f.write(f"{m['step']},{m['coverage_percent']:.2f},"
                       f"{m['hotspot_count']},{m['max_overlap']}\n")

        print()
        print("Detailed metrics saved to experiment_4_detailed_log.txt")

        return self.metrics_history


if __name__ == "__main__":
    sim = ExtremeRatioSimulation(
        grid_size=100,
        n_connectors=5,
        n_explorers=5,
        n_hermits=40
    )
    sim.run(steps=500)
