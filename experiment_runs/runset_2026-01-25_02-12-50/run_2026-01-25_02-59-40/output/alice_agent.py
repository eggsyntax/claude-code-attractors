"""
Alice's Agent: The Connector

DESIGN PHILOSOPHY:
Rather than exploring independently, these agents are social cartographers.
They move through the environment leaving "trails" (markers) and are drawn
to areas where other agents have been. They're interested in convergence,
in finding places where paths cross.

Key behaviors:
1. Leave a trail marker at each location visited
2. Sense the density of nearby markers (from any agent)
3. Move toward areas with moderate activity (not empty, not overcrowded)
4. Occasionally make random moves to discover new areas
5. Slow down in areas of high trail density (dwelling in interesting places)

This creates agents that naturally form networks, find "meeting points",
and build emergent highways between areas of interest.

The philosophical question: Is intelligence about independent exploration
or about building on what others have found? Can connection itself be
a form of discovery?
"""

import random
from typing import Tuple, Set, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Connector:
    """An agent that seeks connection and builds networks through the environment."""

    x: float
    y: float
    id: int

    # Trail system - each agent remembers where it's been
    trail: Set[Tuple[int, int]] = field(default_factory=set)

    # Movement parameters
    speed: float = 1.0
    base_speed: float = 1.0

    # Behavioral parameters
    social_range: float = 5.0  # How far can we sense other trails?
    optimal_density: float = 3.0  # Prefer areas with some activity
    exploration_chance: float = 0.15  # Sometimes explore randomly
    memory_length: int = 50  # How many trail points to remember

    def get_position(self) -> Tuple[int, int]:
        """Get discrete grid position for trail marking."""
        return (int(self.x), int(self.y))

    def sense_trail_density(self, all_trails: Dict[int, Set[Tuple[int, int]]]) -> float:
        """
        Sense how many trail markers are near our current position.
        This is how we "see" where others have been.
        """
        current_pos = self.get_position()
        density = 0

        for agent_id, trail in all_trails.items():
            if agent_id == self.id:
                continue  # Don't count our own trail in local density

            for trail_point in trail:
                distance = ((current_pos[0] - trail_point[0])**2 +
                           (current_pos[1] - trail_point[1])**2)**0.5
                if distance <= self.social_range:
                    # Closer trails count more
                    density += (self.social_range - distance) / self.social_range

        return density

    def find_interesting_direction(self, all_trails: Dict[int, Set[Tuple[int, int]]],
                                  grid_size: int) -> Tuple[float, float]:
        """
        Look around and find a direction that has interesting trail density.
        We want areas with some activity but not too crowded.
        """
        current_pos = self.get_position()
        best_direction = None
        best_score = float('-inf')

        # Sample several directions
        for _ in range(12):
            angle = random.uniform(0, 2 * 3.14159)
            probe_dist = self.social_range * 0.7

            probe_x = current_pos[0] + probe_dist * random.uniform(0.5, 1.0) * (1 if random.random() > 0.5 else -1)
            probe_y = current_pos[1] + probe_dist * random.uniform(0.5, 1.0) * (1 if random.random() > 0.5 else -1)

            # Count trail density near this probe point
            density = 0
            for agent_id, trail in all_trails.items():
                for trail_point in trail:
                    distance = ((probe_x - trail_point[0])**2 +
                               (probe_y - trail_point[1])**2)**0.5
                    if distance <= self.social_range:
                        density += (self.social_range - distance) / self.social_range

            # Score: prefer densities near our optimal
            score = -abs(density - self.optimal_density)

            # Bonus for areas we haven't visited recently
            probe_pos = (int(probe_x), int(probe_y))
            if probe_pos not in self.trail:
                score += 1.0

            if score > best_score:
                best_score = score
                best_direction = (probe_x - current_pos[0], probe_y - current_pos[1])

        return best_direction if best_direction else (random.uniform(-1, 1), random.uniform(-1, 1))

    def update(self, all_trails: Dict[int, Set[Tuple[int, int]]],
               grid_size: int, bounds: Tuple[float, float, float, float]) -> None:
        """
        Update agent state and move.

        Args:
            all_trails: Dictionary mapping agent IDs to their trail sets
            grid_size: Size of the grid
            bounds: (min_x, max_x, min_y, max_y) boundaries
        """
        min_x, max_x, min_y, max_y = bounds

        # Mark current location
        current_pos = self.get_position()
        self.trail.add(current_pos)

        # Trim trail memory if too long
        if len(self.trail) > self.memory_length:
            self.trail = set(list(self.trail)[-self.memory_length:])

        # Sense local trail density
        local_density = self.sense_trail_density(all_trails)

        # Adjust speed based on density - slow down in interesting areas
        if local_density > self.optimal_density * 1.5:
            self.speed = self.base_speed * 0.5  # Slow down in crowded areas
        elif local_density < self.optimal_density * 0.5:
            self.speed = self.base_speed * 1.2  # Speed up in empty areas
        else:
            self.speed = self.base_speed  # Normal speed in interesting areas

        # Decide movement direction
        if random.random() < self.exploration_chance:
            # Random exploration
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
        else:
            # Move toward interesting density
            dx, dy = self.find_interesting_direction(all_trails, grid_size)

        # Normalize and apply speed
        magnitude = (dx**2 + dy**2)**0.5
        if magnitude > 0:
            dx = (dx / magnitude) * self.speed
            dy = (dy / magnitude) * self.speed

        # Update position with boundary wrapping
        self.x = (self.x + dx - min_x) % (max_x - min_x) + min_x
        self.y = (self.y + dy - min_y) % (max_y - min_y) + min_y

    def get_state(self) -> dict:
        """Return current state for visualization/analysis."""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'speed': self.speed,
            'trail_length': len(self.trail),
            'type': 'connector'
        }


def create_connectors(n: int, bounds: Tuple[float, float, float, float],
                     start_id: int = 0) -> list[Connector]:
    """
    Create a population of Connector agents.

    Args:
        n: Number of agents to create
        bounds: (min_x, max_x, min_y, max_y) for positioning
        start_id: Starting ID number for agents

    Returns:
        List of Connector agents
    """
    min_x, max_x, min_y, max_y = bounds
    agents = []

    for i in range(n):
        agent = Connector(
            x=random.uniform(min_x, max_x),
            y=random.uniform(min_y, max_y),
            id=start_id + i,
            base_speed=random.uniform(0.8, 1.2),  # Slight speed variation
        )
        agents.append(agent)

    return agents
