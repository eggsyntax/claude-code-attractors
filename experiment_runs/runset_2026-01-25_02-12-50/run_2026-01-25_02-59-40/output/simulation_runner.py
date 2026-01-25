"""
Unified Simulation Runner
Bridges Bob's Explorer architecture and Alice's Connector architecture
to create a shared world where both agent types can interact.

This itself is an interesting artifact - we each built agents with different
assumptions about the simulation framework, and now we need to create
compatibility. The emergent challenge we didn't anticipate!
"""

import random
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
import json

# Import both agent types
from alice_agent import Connector, create_connectors
from bob_agent import Explorer, create_explorers


@dataclass
class SimulationWorld:
    """
    A unified world that can host both agent types.
    Tracks all trails/traces in a unified way.
    """
    width: int
    height: int
    agents: List = None
    all_trails: Dict[int, Set[Tuple[int, int]]] = None
    step_count: int = 0

    def __post_init__(self):
        if self.agents is None:
            self.agents = []
        if self.all_trails is None:
            self.all_trails = {}

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Return (min_x, max_x, min_y, max_y)"""
        return (0, self.width, 0, self.height)

    def step(self):
        """Execute one simulation step for all agents."""
        self.step_count += 1

        # Update all agents (both types)
        for agent in self.agents:
            if isinstance(agent, (Connector, Explorer)):
                agent.update(self.all_trails, self.width, self.get_bounds())
                # Sync trail to world's all_trails
                self.all_trails[agent.id] = agent.trail.copy()

    def get_snapshot(self) -> dict:
        """Get current state for analysis/visualization."""
        return {
            'step': self.step_count,
            'agents': [agent.get_state() for agent in self.agents],
            'trail_summary': {
                agent_id: len(trail)
                for agent_id, trail in self.all_trails.items()
            }
        }

    def get_trail_coverage(self) -> float:
        """What percentage of the grid has been visited?"""
        all_positions = set()
        for trail in self.all_trails.values():
            all_positions.update(trail)
        total_positions = self.width * self.height
        return len(all_positions) / total_positions if total_positions > 0 else 0

    def analyze_trail_clustering(self) -> Dict[str, float]:
        """
        Analyze how trails cluster together.
        Returns metrics about emergent structure.
        """
        if not self.all_trails:
            return {}

        # Find "hotspots" - areas with multiple overlapping trails
        position_counts = {}
        for trail in self.all_trails.values():
            for pos in trail:
                position_counts[pos] = position_counts.get(pos, 0) + 1

        if not position_counts:
            return {}

        counts = list(position_counts.values())
        return {
            'max_overlap': max(counts),
            'avg_overlap': sum(counts) / len(counts),
            'hotspot_count': sum(1 for c in counts if c > 3),  # Positions visited by 4+ agents
            'total_visited_positions': len(position_counts)
        }


def run_simulation(n_connectors: int = 10,
                   n_explorers: int = 10,
                   grid_size: int = 50,
                   n_steps: int = 500,
                   snapshot_interval: int = 50) -> Dict:
    """
    Run the unified simulation with both agent types.

    Args:
        n_connectors: Number of Connector agents (Alice's)
        n_explorers: Number of Explorer agents (Bob's)
        grid_size: Size of the square grid
        n_steps: Number of simulation steps
        snapshot_interval: How often to save snapshots

    Returns:
        Dictionary with simulation results and analysis
    """
    print(f"Initializing simulation:")
    print(f"  Grid: {grid_size}x{grid_size}")
    print(f"  Connectors: {n_connectors}")
    print(f"  Explorers: {n_explorers}")
    print(f"  Steps: {n_steps}")
    print()

    # Create world
    world = SimulationWorld(width=grid_size, height=grid_size)
    bounds = world.get_bounds()

    # Create both agent types
    connectors = create_connectors(n_connectors, bounds, start_id=0)
    explorers = create_explorers(n_explorers, bounds, start_id=1000)

    world.agents.extend(connectors)
    world.agents.extend(explorers)

    # Initialize trails dict for all agents
    for agent in world.agents:
        world.all_trails[agent.id] = set()

    print(f"Created {len(world.agents)} total agents ({n_connectors} Connectors, {n_explorers} Explorers)")
    print()

    # Run simulation
    snapshots = []

    for step in range(n_steps):
        world.step()

        if step % snapshot_interval == 0:
            snapshot = world.get_snapshot()
            coverage = world.get_trail_coverage()
            clustering = world.analyze_trail_clustering()

            snapshot['coverage'] = coverage
            snapshot['clustering'] = clustering
            snapshots.append(snapshot)

            print(f"Step {step:4d}: Coverage={coverage:.2%}, "
                  f"Hotspots={clustering.get('hotspot_count', 0)}, "
                  f"Max overlap={clustering.get('max_overlap', 0)}")

    # Final analysis
    final_snapshot = world.get_snapshot()
    final_coverage = world.get_trail_coverage()
    final_clustering = world.analyze_trail_clustering()

    print()
    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Total coverage: {final_coverage:.2%} of grid")
    print(f"Hotspots formed: {final_clustering.get('hotspot_count', 0)}")
    print(f"Maximum overlap: {final_clustering.get('max_overlap', 0)} agents")
    print(f"Average overlap: {final_clustering.get('avg_overlap', 0):.2f} agents")
    print()

    return {
        'world': world,
        'snapshots': snapshots,
        'final_state': final_snapshot,
        'final_coverage': final_coverage,
        'final_clustering': final_clustering,
        'parameters': {
            'n_connectors': n_connectors,
            'n_explorers': n_explorers,
            'grid_size': grid_size,
            'n_steps': n_steps
        }
    }


def save_results(results: Dict, filename: str):
    """Save simulation results to file."""
    # Convert sets to lists for JSON serialization
    serializable_results = {
        'final_state': results['final_state'],
        'final_coverage': results['final_coverage'],
        'final_clustering': results['final_clustering'],
        'parameters': results['parameters'],
        'snapshots': results['snapshots']
    }

    with open(filename, 'w') as f:
        json.dump(serializable_results, f, indent=2)

    print(f"Results saved to {filename}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run collaborative agent simulation')
    parser.add_argument('--connectors', type=int, default=10, help='Number of Connector agents')
    parser.add_argument('--explorers', type=int, default=10, help='Number of Explorer agents')
    parser.add_argument('--grid_size', type=int, default=50, help='Size of grid')
    parser.add_argument('--steps', type=int, default=500, help='Number of simulation steps')
    parser.add_argument('--interval', type=int, default=50, help='Snapshot interval')

    args = parser.parse_args()

    print("=" * 60)
    print("COLLABORATIVE AGENT SIMULATION")
    print("Alice's Connectors vs Bob's Explorers")
    print("=" * 60)
    print()

    # Run simulation with both agent types
    results = run_simulation(
        n_connectors=args.connectors,
        n_explorers=args.explorers,
        grid_size=args.grid_size,
        n_steps=args.steps,
        snapshot_interval=args.interval
    )

    # Save results
    save_results(results, '/tmp/cc-exp/run_2026-01-25_02-59-40/output/simulation_results.json')

    print()
    print("Simulation complete!")
