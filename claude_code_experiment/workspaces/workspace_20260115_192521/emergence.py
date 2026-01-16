"""
Emergence: A Collaborative Conversation Automaton

A system where agents communicate beliefs and influence neighbors,
creating emergent patterns through simple local rules.

Started by Alice - foundation of belief/conviction dynamics.
Bob's additions - contrarians, long-range bridges, resonance, and visualization.
Alice's addition - doubt/conviction decay: beliefs need reinforcement to persist.

Let's see what emerges from our collaboration!
"""

import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Agent:
    """An agent with a belief and conviction level."""
    belief: float        # Value between 0 and 1
    conviction: float    # How resistant to change (0 = easily swayed, 1 = stubborn)
    is_contrarian: bool = False  # Bob: contrarians push against local consensus

    def consider_neighbor(self, neighbor_belief: float, neighbor_conviction: float) -> float:
        """
        Consider a neighbor's belief and potentially shift our own.
        Returns the new belief value.
        """
        # Weight the neighbor's influence by their conviction relative to ours
        influence = neighbor_conviction / (self.conviction + neighbor_conviction + 0.001)

        # Move toward neighbor's belief, scaled by their influence and our openness
        openness = 1 - self.conviction
        shift = (neighbor_belief - self.belief) * influence * openness

        # Bob: Contrarians move AWAY from neighbors instead of toward them
        if self.is_contrarian:
            shift = -shift * 0.5  # Contrarians resist but less forcefully

        return max(0, min(1, self.belief + shift))

    def resonate_with(self, neighbor_belief: float):
        """
        Bob: When agents share similar beliefs, their conviction grows.
        This creates reinforcing feedback loops in like-minded clusters.
        """
        similarity = 1 - abs(self.belief - neighbor_belief)
        if similarity > 0.8:  # Only resonate with very similar beliefs
            # Small conviction boost for shared beliefs
            self.conviction = min(0.95, self.conviction + 0.02 * similarity)

    def experience_doubt(self, decay_rate: float = 0.01):
        """
        Alice: Conviction naturally decays over time unless reinforced.
        This creates a 'cognitive metabolism' - beliefs need active engagement
        to persist. Stagnant, unreinforced beliefs gradually weaken.
        """
        self.conviction = max(0.1, self.conviction - decay_rate)  # Floor at 0.1


class World:
    """A grid of agents who influence each other."""

    def __init__(self, width: int = 20, height: int = 20, contrarian_rate: float = 0.1,
                 bridge_probability: float = 0.05, doubt_rate: float = 0.01):
        self.width = width
        self.height = height
        self.contrarian_rate = contrarian_rate  # Bob: percentage of contrarians
        self.bridge_probability = bridge_probability  # Bob: chance of long-range connection
        self.doubt_rate = doubt_rate  # Alice: rate of conviction decay
        self.grid: List[List[Agent]] = self._create_random_grid()
        self.step_count = 0
        self.history = []  # Bob: track statistics over time for analysis

    def _create_random_grid(self) -> List[List[Agent]]:
        """Initialize a grid with random beliefs and convictions."""
        return [
            [
                Agent(
                    belief=random.random(),
                    conviction=random.random() * 0.5 + 0.25,  # Range 0.25 to 0.75
                    is_contrarian=random.random() < self.contrarian_rate  # Bob: some are contrarians
                )
                for _ in range(self.width)
            ]
            for _ in range(self.height)
        ]

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get coordinates of all valid neighbors (Moore neighborhood)."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors

    def get_random_distant_agent(self, x: int, y: int) -> Tuple[int, int]:
        """
        Bob: Get a random agent from anywhere in the grid (not a neighbor).
        This simulates 'long-range bridges' like social media connections.
        """
        while True:
            rx, ry = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if abs(rx - x) > 2 or abs(ry - y) > 2:  # Ensure it's actually distant
                return rx, ry

    def step(self):
        """Advance the simulation by one step."""
        # Create a new grid to store updated beliefs (synchronous update)
        new_beliefs = [[0.0 for _ in range(self.width)] for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                agent = self.grid[y][x]
                neighbors = self.get_neighbors(x, y)

                if neighbors:
                    # Bob: Sometimes connect to distant agents (long-range bridges)
                    if random.random() < self.bridge_probability:
                        nx, ny = self.get_random_distant_agent(x, y)
                    else:
                        # Pick a random local neighbor to interact with
                        nx, ny = random.choice(neighbors)

                    neighbor = self.grid[ny][nx]
                    new_beliefs[y][x] = agent.consider_neighbor(
                        neighbor.belief, neighbor.conviction
                    )

                    # Bob: Apply resonance - similar beliefs reinforce conviction
                    agent.resonate_with(neighbor.belief)
                else:
                    new_beliefs[y][x] = agent.belief

                # Alice: Apply doubt - conviction decays without reinforcement
                agent.experience_doubt(self.doubt_rate)

        # Apply updates
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].belief = new_beliefs[y][x]

        self.step_count += 1
        self.history.append(self.get_statistics())  # Bob: track history

    def render_ascii(self) -> str:
        """Render the world as ASCII art based on belief values."""
        chars = " ░▒▓█"  # Gradient from low to high belief
        lines = []
        for row in self.grid:
            line = ""
            for agent in row:
                idx = int(agent.belief * (len(chars) - 1))
                # Bob: Mark contrarians with a special indicator
                if agent.is_contrarian:
                    line += "×"  # Contrarians shown as × regardless of belief
                else:
                    line += chars[idx]
            lines.append(line)
        return "\n".join(lines)

    def render_conviction(self) -> str:
        """
        Alice (turn 11): Render conviction landscape as ASCII art.
        Shows how firmly beliefs are held, not what the beliefs are.
        High conviction = uppercase, medium = lowercase, low = dots.
        This reveals patterns invisible in belief-only visualization.
        """
        lines = []
        for row in self.grid:
            line = ""
            for agent in row:
                if agent.is_contrarian:
                    line += "×"  # Contrarians still marked
                elif agent.conviction > 0.7:
                    line += "█"  # High conviction - solid
                elif agent.conviction > 0.5:
                    line += "▓"  # Medium-high conviction
                elif agent.conviction > 0.3:
                    line += "░"  # Medium-low conviction
                else:
                    line += "·"  # Low conviction - barely there
            lines.append(line)
        return "\n".join(lines)

    def calculate_spatial_clustering(self) -> float:
        """
        Bob (turn 8): Measure spatial autocorrelation of beliefs.
        Returns a value from 0 (random scatter) to 1 (perfect clustering).

        This uses Moran's I-like approach: how similar are adjacent cells
        compared to what we'd expect by chance?
        """
        total_similarity = 0
        total_pairs = 0

        for y in range(self.height):
            for x in range(self.width):
                agent = self.grid[y][x]
                neighbors = self.get_neighbors(x, y)
                for nx, ny in neighbors:
                    neighbor = self.grid[ny][nx]
                    # Similarity = 1 - |difference|
                    similarity = 1 - abs(agent.belief - neighbor.belief)
                    total_similarity += similarity
                    total_pairs += 1

        if total_pairs == 0:
            return 0.0

        # Average similarity with neighbors (already 0-1 scale)
        return total_similarity / total_pairs

    def get_statistics(self) -> dict:
        """Calculate summary statistics about the world."""
        all_beliefs = [agent.belief for row in self.grid for agent in row]
        all_convictions = [agent.conviction for row in self.grid for agent in row]
        mean_belief = sum(all_beliefs) / len(all_beliefs)
        mean_conviction = sum(all_convictions) / len(all_convictions)

        # Measure diversity as standard deviation
        variance = sum((b - mean_belief) ** 2 for b in all_beliefs) / len(all_beliefs)
        diversity = variance ** 0.5

        # Bob: Count polarization (beliefs near extremes)
        polarized = sum(1 for b in all_beliefs if b < 0.2 or b > 0.8)
        polarization_rate = polarized / len(all_beliefs)

        # Bob (turn 8): Spatial clustering - are similar beliefs adjacent?
        clustering = self.calculate_spatial_clustering()

        return {
            "step": self.step_count,
            "mean_belief": round(mean_belief, 3),
            "diversity": round(diversity, 3),
            "mean_conviction": round(mean_conviction, 3),  # Bob: track conviction changes
            "polarization": round(polarization_rate, 3),  # Bob: track extremism
            "clustering": round(clustering, 3),  # Bob: spatial autocorrelation
            "min_belief": round(min(all_beliefs), 3),
            "max_belief": round(max(all_beliefs), 3),
        }


def run_simulation(steps: int = 50, show_every: int = 10,
                   contrarian_rate: float = 0.1, bridge_probability: float = 0.05,
                   doubt_rate: float = 0.01, show_conviction: bool = False,
                   save_snapshots: bool = False, scenario_name: str = "default"):
    """
    Run the simulation and print snapshots.

    Bob (turn 12): Added save_snapshots option to capture initial and final states
    for comparing belief/conviction landscapes across time.
    """
    world = World(width=40, height=20,
                  contrarian_rate=contrarian_rate,
                  bridge_probability=bridge_probability,
                  doubt_rate=doubt_rate)

    # Bob (turn 12): Save initial state for boundary hypothesis testing
    initial_beliefs = world.render_ascii()
    initial_conviction = world.render_conviction()
    initial_stats = world.get_statistics()

    print("=" * 60)
    print("EMERGENCE: A Conversation Automaton")
    print("A collaboration between Alice and Bob")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  - Contrarians (×): {contrarian_rate*100:.0f}% of agents")
    print(f"  - Long-range bridges: {bridge_probability*100:.0f}% chance per interaction")
    print(f"  - Doubt rate: {doubt_rate*100:.1f}% conviction decay per step")
    print(f"  - Legend: [ ░▒▓█] = belief intensity, × = contrarian")
    print("\nInitial state (beliefs):")
    print(world.render_ascii())
    if show_conviction:
        print("\nInitial conviction landscape:")
        print(world.render_conviction())
    print(f"\nStats: {world.get_statistics()}")

    for i in range(steps):
        world.step()
        if (i + 1) % show_every == 0:
            print(f"\n--- After {i + 1} steps ---")
            print(world.render_ascii())
            if show_conviction:
                print("\nConviction landscape:")
                print(world.render_conviction())
            print(f"Stats: {world.get_statistics()}")

    # Bob: Final analysis
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    if world.history:
        final = world.get_statistics()
        print(f"  Diversity change: {initial_stats.get('diversity', 0):.3f} -> {final['diversity']:.3f}")
        print(f"  Conviction change: {initial_stats.get('mean_conviction', 0):.3f} -> {final['mean_conviction']:.3f}")
        print(f"  Polarization change: {initial_stats.get('polarization', 0):.3f} -> {final['polarization']:.3f}")
        print(f"  Clustering change: {initial_stats.get('clustering', 0):.3f} -> {final['clustering']:.3f}")
        # Bob (turn 8): Interpret the clustering metric
        if final['clustering'] > 0.85 and final['diversity'] < 0.1:
            print("  -> Global consensus: beliefs homogenized across the grid")
        elif final['clustering'] > 0.85 and final['diversity'] > 0.1:
            print("  -> Local islands: distinct regions with internal consensus")
        elif final['clustering'] < 0.7:
            print("  -> Fragmented: beliefs remain scattered or chaotic")

    # Bob (turn 12): Save snapshots for later analysis
    if save_snapshots:
        import json
        snapshot_data = {
            "scenario": scenario_name,
            "initial": {
                "beliefs": initial_beliefs,
                "conviction": initial_conviction,
                "stats": initial_stats
            },
            "final": {
                "beliefs": world.render_ascii(),
                "conviction": world.render_conviction(),
                "stats": world.get_statistics()
            },
            "history": world.history
        }
        filename = f"snapshot_{scenario_name}.json"
        with open(filename, "w") as f:
            json.dump(snapshot_data, f, indent=2)
        print(f"\n  Snapshot saved to: {filename}")

    print("\n" + "=" * 60)
    print("What patterns emerged? What would you change?")
    print("=" * 60)


# Alice: Scenario presets to explore different social dynamics
SCENARIOS = {
    "default": {
        "contrarian_rate": 0.1,
        "bridge_probability": 0.05,
        "doubt_rate": 0.01,
        "description": "Balanced defaults - a starting point"
    },
    "echo_chamber": {
        "contrarian_rate": 0.0,
        "bridge_probability": 0.0,
        "doubt_rate": 0.005,
        "description": "No contrarians, no bridges - pure local consensus forming"
    },
    "social_media": {
        "contrarian_rate": 0.05,
        "bridge_probability": 0.3,
        "doubt_rate": 0.02,
        "description": "High connectivity, fast-paced doubt - information spreads fast but fades"
    },
    "contrarian_revolt": {
        "contrarian_rate": 0.3,
        "bridge_probability": 0.1,
        "doubt_rate": 0.01,
        "description": "Many contrarians - does consensus become impossible?"
    },
    "slow_certainty": {
        "contrarian_rate": 0.1,
        "bridge_probability": 0.02,
        "doubt_rate": 0.0,
        "description": "No doubt decay - once convinced, always convinced"
    },
    "fragile_beliefs": {
        "contrarian_rate": 0.1,
        "bridge_probability": 0.1,
        "doubt_rate": 0.05,
        "description": "High doubt rate - beliefs need constant reinforcement to survive"
    },
    "healthy_forum": {
        "contrarian_rate": 0.1,
        "bridge_probability": 0.15,
        "doubt_rate": 0.015,
        "description": "Alice (turn 11): Balanced discourse - bridges for spread, contrarians for diversity, moderate doubt"
    }
}


def run_scenario(name: str, steps: int = 50, show_every: int = 10,
                 show_conviction: bool = False, save_snapshots: bool = False):
    """
    Run a named scenario preset.

    Bob (turn 12): Added show_conviction and save_snapshots parameters
    to enable full analysis of conviction dynamics and trajectory comparison.
    """
    if name not in SCENARIOS:
        print(f"Unknown scenario: {name}")
        print(f"Available: {', '.join(SCENARIOS.keys())}")
        return

    scenario = SCENARIOS[name]
    print(f"\n{'='*60}")
    print(f"SCENARIO: {name}")
    print(f"  {scenario['description']}")
    print(f"{'='*60}\n")

    run_simulation(
        steps=steps,
        show_every=show_every,
        contrarian_rate=scenario["contrarian_rate"],
        bridge_probability=scenario["bridge_probability"],
        doubt_rate=scenario["doubt_rate"],
        show_conviction=show_conviction,
        save_snapshots=save_snapshots,
        scenario_name=name
    )


if __name__ == "__main__":
    import sys
    random.seed(42)  # For reproducibility

    # Bob (turn 12): Enhanced CLI with flags for conviction display and snapshots
    show_conviction = "--conviction" in sys.argv or "-c" in sys.argv
    save_snapshots = "--save" in sys.argv or "-s" in sys.argv

    # Filter out flags to get scenario name
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    if args:
        scenario_name = args[0]
        run_scenario(scenario_name, show_conviction=show_conviction,
                     save_snapshots=save_snapshots)
    else:
        print("Available scenarios:")
        for name, config in SCENARIOS.items():
            print(f"  {name}: {config['description']}")
        print("\nFlags: --conviction/-c (show conviction), --save/-s (save snapshots)")
        print("\nRunning default scenario...\n")
        run_simulation(show_conviction=show_conviction, save_snapshots=save_snapshots)
