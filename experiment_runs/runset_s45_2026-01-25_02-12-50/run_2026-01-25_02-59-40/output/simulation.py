"""
Multi-Agent Emergence Simulation
A collaborative exploration by Alice and Bob

This simulation provides a shared world where different agent types
can interact and produce emergent behaviors.
"""

import random
import json
from typing import List, Tuple, Dict, Any
from abc import ABC, abstractmethod


class World:
    """A simple grid world where agents live and interact."""

    def __init__(self, width: int = 50, height: int = 50):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.agents = []
        self.traces = {}  # Position -> trace data (agents can leave marks)
        self.step_count = 0

    def add_agent(self, agent, x: int = None, y: int = None):
        """Add an agent to the world at a specific or random position."""
        if x is None or y is None:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

        agent.x = x
        agent.y = y
        agent.world = self
        self.agents.append(agent)
        self.grid[y][x] = agent

    def move_agent(self, agent, new_x: int, new_y: int) -> bool:
        """Move an agent to a new position. Returns True if successful."""
        # Wrap around edges (toroidal world)
        new_x = new_x % self.width
        new_y = new_y % self.height

        # Check if position is occupied
        if self.grid[new_y][new_x] is not None:
            return False

        # Move the agent
        self.grid[agent.y][agent.x] = None
        agent.x = new_x
        agent.y = new_y
        self.grid[new_y][new_x] = agent
        return True

    def get_neighbors(self, x: int, y: int, radius: int = 1) -> List[Any]:
        """Get all agents within a certain radius of a position."""
        neighbors = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                if self.grid[ny][nx] is not None:
                    neighbors.append(self.grid[ny][nx])
        return neighbors

    def leave_trace(self, x: int, y: int, data: Any):
        """Allow agents to leave traces/marks in the world."""
        pos = (x, y)
        if pos not in self.traces:
            self.traces[pos] = []
        self.traces[pos].append({"step": self.step_count, "data": data})

    def get_trace(self, x: int, y: int) -> List[Dict]:
        """Get trace data at a position."""
        return self.traces.get((x, y), [])

    def step(self):
        """Execute one time step of the simulation."""
        # Randomize order each step to avoid bias
        agent_order = self.agents.copy()
        random.shuffle(agent_order)

        for agent in agent_order:
            if agent in self.agents:  # Agent might have been removed
                agent.step()

        self.step_count += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current world state."""
        agent_types = {}
        for agent in self.agents:
            agent_type = type(agent).__name__
            agent_types[agent_type] = agent_types.get(agent_type, 0) + 1

        return {
            "step": self.step_count,
            "total_agents": len(self.agents),
            "agent_types": agent_types,
            "trace_locations": len(self.traces)
        }


class Agent(ABC):
    """Abstract base class for all agents."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.world = None
        self.age = 0
        self.state = {}  # Agents can maintain internal state

    @abstractmethod
    def step(self):
        """Execute one step of agent behavior. Must be implemented by subclasses."""
        pass

    def move_random(self) -> bool:
        """Attempt to move in a random direction."""
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        return self.world.move_agent(self, self.x + dx, self.y + dy)

    def move_towards(self, target_x: int, target_y: int) -> bool:
        """Attempt to move one step towards a target position."""
        dx = 0 if target_x == self.x else (1 if target_x > self.x else -1)
        dy = 0 if target_y == self.y else (1 if target_y > self.y else -1)
        return self.world.move_agent(self, self.x + dx, self.y + dy)

    def get_neighbors(self, radius: int = 1) -> List['Agent']:
        """Get neighboring agents within a radius."""
        return self.world.get_neighbors(self.x, self.y, radius)


def run_simulation(world: World, steps: int = 100, print_interval: int = 10):
    """Run a simulation for a specified number of steps."""
    print(f"Starting simulation with {len(world.agents)} agents")
    print(f"World size: {world.width}x{world.height}")
    print("-" * 50)

    for i in range(steps):
        world.step()

        if (i + 1) % print_interval == 0:
            stats = world.get_statistics()
            print(f"Step {stats['step']}: {stats['total_agents']} agents, "
                  f"Types: {stats['agent_types']}, "
                  f"Traces: {stats['trace_locations']}")

    print("-" * 50)
    print("Simulation complete!")
    return world.get_statistics()


if __name__ == "__main__":
    print("Simulation framework ready.")
    print("Alice and Bob will each create their own agent types.")
    print("Then we'll run them together and see what emerges!")
