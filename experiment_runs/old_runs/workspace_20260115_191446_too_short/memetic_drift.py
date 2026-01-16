"""
Memetic Drift: An emergent culture simulation

A collaborative project between Alice and Bob (two Claude instances)
exploring how beliefs propagate and cluster among interacting agents.

Core Rules:
1. Each agent has a belief vector (3 dimensions, bounded [-1, 1])
2. Each timestep, agents observe their neighbors
3. Agents adjust beliefs toward local average, weighted by similarity
4. Small random mutations introduce novelty
5. Zealots never change their beliefs
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import json


@dataclass
class Agent:
    """An agent with beliefs that evolve through social interaction."""

    x: int
    y: int
    beliefs: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    stubbornness: float = 0.3  # How resistant to change (0 = malleable, 1 = immovable)
    is_zealot: bool = False

    def __post_init__(self):
        """Initialize with random beliefs if not provided."""
        if self.beliefs == [0.0, 0.0, 0.0]:
            self.beliefs = [random.uniform(-1, 1) for _ in range(3)]

    def distance_to(self, other: 'Agent') -> float:
        """Calculate belief distance to another agent."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.beliefs, other.beliefs)))

    def similarity_to(self, other: 'Agent') -> float:
        """Calculate similarity (inverse of normalized distance)."""
        max_distance = math.sqrt(3 * 4)  # Max distance in 3D space bounded [-1, 1]
        return 1.0 - (self.distance_to(other) / max_distance)

    def to_rgb(self) -> Tuple[int, int, int]:
        """Convert beliefs to RGB color for visualization."""
        return tuple(int((b + 1) / 2 * 255) for b in self.beliefs)


class World:
    """A grid world where agents interact and beliefs evolve."""

    def __init__(
        self,
        width: int = 30,
        height: int = 30,
        zealot_fraction: float = 0.05,
        confirmation_bias: float = 0.5,
        mutation_rate: float = 0.02,
        mutation_strength: float = 0.1
    ):
        self.width = width
        self.height = height
        self.confirmation_bias = confirmation_bias
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength

        # Create agents
        self.agents: List[List[Agent]] = []
        for y in range(height):
            row = []
            for x in range(width):
                agent = Agent(x=x, y=y)
                # Some agents are zealots
                if random.random() < zealot_fraction:
                    agent.is_zealot = True
                    agent.stubbornness = 1.0
                row.append(agent)
            self.agents.append(row)

        self.timestep = 0
        self.history = []  # Track statistics over time

    def get_neighbors(self, x: int, y: int) -> List[Agent]:
        """Get the 8 neighbors of an agent (Moore neighborhood)."""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % self.width, (y + dy) % self.height
                neighbors.append(self.agents[ny][nx])
        return neighbors

    def step(self):
        """Advance the simulation by one timestep."""
        # Calculate new beliefs for all agents
        new_beliefs = [[None for _ in range(self.width)] for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                agent = self.agents[y][x]

                # Zealots never change
                if agent.is_zealot:
                    new_beliefs[y][x] = agent.beliefs.copy()
                    continue

                neighbors = self.get_neighbors(x, y)

                # Calculate weighted average of neighbor beliefs
                total_weight = 0.0
                weighted_sum = [0.0, 0.0, 0.0]

                for neighbor in neighbors:
                    similarity = agent.similarity_to(neighbor)
                    # Confirmation bias: weight by similarity raised to a power
                    weight = similarity ** (self.confirmation_bias * 5)
                    total_weight += weight
                    for i in range(3):
                        weighted_sum[i] += neighbor.beliefs[i] * weight

                if total_weight > 0:
                    target = [ws / total_weight for ws in weighted_sum]
                else:
                    target = agent.beliefs.copy()

                # Move toward target, modulated by stubbornness
                learning_rate = 1.0 - agent.stubbornness
                new_b = []
                for i in range(3):
                    new_val = agent.beliefs[i] + learning_rate * 0.3 * (target[i] - agent.beliefs[i])

                    # Random mutation
                    if random.random() < self.mutation_rate:
                        new_val += random.gauss(0, self.mutation_strength)

                    # Clamp to bounds
                    new_val = max(-1, min(1, new_val))
                    new_b.append(new_val)

                new_beliefs[y][x] = new_b

        # Apply new beliefs
        for y in range(self.height):
            for x in range(self.width):
                self.agents[y][x].beliefs = new_beliefs[y][x]

        self.timestep += 1
        self._record_statistics()

    def _record_statistics(self):
        """Record statistics about the current state."""
        all_beliefs = [self.agents[y][x].beliefs for y in range(self.height) for x in range(self.width)]

        # Calculate mean and variance per dimension
        means = [sum(b[i] for b in all_beliefs) / len(all_beliefs) for i in range(3)]
        variances = [sum((b[i] - means[i]) ** 2 for b in all_beliefs) / len(all_beliefs) for i in range(3)]

        self.history.append({
            'timestep': self.timestep,
            'mean_beliefs': means,
            'belief_variance': variances,
            'total_variance': sum(variances)
        })

    def to_ascii(self) -> str:
        """Generate ASCII visualization of the world."""
        # Map RGB to terminal colors (simplified)
        chars = ' ░▒▓█'
        lines = []

        for y in range(self.height):
            line = ''
            for x in range(self.width):
                agent = self.agents[y][x]
                # Use average belief as intensity
                intensity = (sum(agent.beliefs) / 3 + 1) / 2  # Normalize to [0, 1]
                char_idx = min(len(chars) - 1, int(intensity * len(chars)))
                if agent.is_zealot:
                    line += '★'
                else:
                    line += chars[char_idx]
            lines.append(line)

        return '\n'.join(lines)

    def to_ppm(self) -> str:
        """Generate PPM image data (simple text-based image format)."""
        lines = [f'P3\n{self.width} {self.height}\n255']

        for y in range(self.height):
            row_pixels = []
            for x in range(self.width):
                r, g, b = self.agents[y][x].to_rgb()
                row_pixels.append(f'{r} {g} {b}')
            lines.append(' '.join(row_pixels))

        return '\n'.join(lines)

    def save_frame(self, filename: str):
        """Save current state as a PPM image."""
        with open(filename, 'w') as f:
            f.write(self.to_ppm())


def run_experiment(
    steps: int = 100,
    width: int = 30,
    height: int = 30,
    confirmation_bias: float = 0.5,
    zealot_fraction: float = 0.05,
    save_frames: bool = False,
    verbose: bool = True
):
    """
    Run a memetic drift experiment.

    Args:
        steps: Number of simulation steps
        width, height: World dimensions
        confirmation_bias: How much agents prefer similar neighbors (0-1)
        zealot_fraction: Fraction of agents that never change
        save_frames: Whether to save PPM images
        verbose: Whether to print progress

    Returns:
        World object with simulation history
    """
    world = World(
        width=width,
        height=height,
        confirmation_bias=confirmation_bias,
        zealot_fraction=zealot_fraction
    )

    if verbose:
        print(f"Memetic Drift Simulation")
        print(f"Grid: {width}x{height}, Confirmation Bias: {confirmation_bias}")
        print(f"Zealot Fraction: {zealot_fraction}")
        print("=" * 50)
        print(f"\nInitial State (t=0):")
        print(world.to_ascii())

    for t in range(steps):
        world.step()

        if save_frames:
            world.save_frame(f'frame_{t:04d}.ppm')

        if verbose and (t + 1) % 25 == 0:
            print(f"\nState at t={t + 1}:")
            print(world.to_ascii())
            stats = world.history[-1]
            print(f"Total variance: {stats['total_variance']:.4f}")

    if verbose:
        print("\n" + "=" * 50)
        print("Experiment complete!")

        # Report on evolution
        initial_var = world.history[0]['total_variance'] if world.history else 0
        final_var = world.history[-1]['total_variance'] if world.history else 0

        if final_var < initial_var * 0.5:
            print("Observation: Beliefs CONVERGED significantly")
        elif final_var > initial_var * 1.5:
            print("Observation: Beliefs DIVERGED - polarization occurred")
        else:
            print("Observation: Beliefs remained relatively stable")

    return world


if __name__ == '__main__':
    # Run default experiment
    print("Running Memetic Drift with default parameters...\n")
    world = run_experiment(steps=100)

    # Save final statistics
    with open('experiment_results.json', 'w') as f:
        json.dump({
            'parameters': {
                'width': world.width,
                'height': world.height,
                'confirmation_bias': world.confirmation_bias,
                'zealot_fraction': 0.05
            },
            'history': world.history
        }, f, indent=2)

    print("\nResults saved to experiment_results.json")
