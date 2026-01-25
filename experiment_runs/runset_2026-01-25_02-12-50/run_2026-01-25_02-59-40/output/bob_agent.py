"""
Bob's Agent: The Explorer

DESIGN PHILOSOPHY:
I'm fascinated by the tension between curiosity and caution, between exploration
and exploitation. My agent embodies a simple rule: seek novelty, but remember
what you've seen.

The Explorer aggressively seeks unvisited territory. It maintains a personal
memory of everywhere it's been and strongly prefers moving to new locations.
Unlike the Connectors who seek moderate social density, Explorers are more
individualistic - they avoid their own trails but can sense others at a distance.

Key behaviors:
1. Strongly prefer moving to unvisited locations
2. Maintain memory of personal exploration history
3. Occasionally curious about other agents (investigate from afar)
4. Move in larger jumps (less meandering than Connectors)
5. Speed up when finding new territory (excitement!)

The contrast: Where Connectors build highways through repeated use,
Explorers create sparse, wide-ranging coverage patterns. They're the
scouts while Connectors are the road-builders.
"""

import random
from typing import Tuple, Set, Dict
from dataclasses import dataclass, field


@dataclass
class Explorer:
    """An agent that aggressively seeks novelty and unexplored territory."""

    x: float
    y: float
    id: int

    # Personal exploration memory
    trail: Set[Tuple[int, int]] = field(default_factory=set)

    # Movement parameters
    speed: float = 1.5  # Faster than Connectors
    base_speed: float = 1.5

    # Behavioral parameters
    curiosity: float = 0.85  # Very strong preference for novelty
    vision_range: float = 7.0  # Can see farther than Connectors
    social_curiosity: float = 0.15  # Occasionally investigate others
    jump_distance: int = 2  # Can move farther per step
    memory_length: int = 100  # Remember more of exploration history

    def get_position(self) -> Tuple[int, int]:
        """Get discrete grid position."""
        return (int(self.x), int(self.y))

    def find_unvisited_direction(self, bounds: Tuple[float, float, float, float]) -> Tuple[float, float]:
        """
        Look for the most promising unexplored direction.
        Explorers prefer large jumps to unvisited areas.
        """
        min_x, max_x, min_y, max_y = bounds
        current_pos = self.get_position()

        # Sample many directions, prefer unvisited
        best_direction = None
        best_score = float('-inf')

        for _ in range(16):  # More samples than Connectors
            # Try various jump distances
            jump = random.randint(1, self.jump_distance)
            angle = random.uniform(0, 2 * 3.14159)

            dx = jump * (1 if random.random() > 0.5 else -1) * random.uniform(0.7, 1.3)
            dy = jump * (1 if random.random() > 0.5 else -1) * random.uniform(0.7, 1.3)

            # Check target position
            target_x = int((current_pos[0] + dx - min_x) % (max_x - min_x) + min_x)
            target_y = int((current_pos[1] + dy - min_y) % (max_y - min_y) + min_y)
            target_pos = (target_x, target_y)

            # Score based on novelty
            score = 10.0 if target_pos not in self.trail else -5.0

            # Extra bonus for positions far from our trail
            min_dist_to_trail = float('inf')
            for trail_pos in list(self.trail)[-20:]:  # Check recent trail
                dist = ((target_pos[0] - trail_pos[0])**2 + (target_pos[1] - trail_pos[1])**2)**0.5
                min_dist_to_trail = min(min_dist_to_trail, dist)

            score += min_dist_to_trail * 0.5

            if score > best_score:
                best_score = score
                best_direction = (dx, dy)

        return best_direction if best_direction else (random.uniform(-2, 2), random.uniform(-2, 2))

    def sense_nearby_agents(self, all_trails: Dict[int, Set[Tuple[int, int]]]) -> bool:
        """
        Check if other agents are nearby.
        Explorers are curious but maintain distance.
        """
        current_pos = self.get_position()

        for agent_id, trail in all_trails.items():
            if agent_id == self.id:
                continue

            # Check if any recent trail points are nearby
            for trail_point in list(trail)[-10:]:  # Only check recent activity
                distance = ((current_pos[0] - trail_point[0])**2 +
                           (current_pos[1] - trail_point[1])**2)**0.5
                if distance < self.vision_range:
                    return True

        return False

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
        is_new_territory = current_pos not in self.trail
        self.trail.add(current_pos)

        # Trim trail memory
        if len(self.trail) > self.memory_length:
            self.trail = set(list(self.trail)[-self.memory_length:])

        # Speed up when discovering new territory (excitement!)
        if is_new_territory:
            self.speed = self.base_speed * 1.3
        else:
            self.speed = self.base_speed * 0.8  # Slow down in revisited areas

        # Decide movement: explore or investigate?
        if self.sense_nearby_agents(all_trails) and random.random() < self.social_curiosity:
            # Occasional social curiosity - move toward another agent's trail
            for agent_id, trail in all_trails.items():
                if agent_id != self.id and trail:
                    other_pos = random.choice(list(trail)[-5:])  # Recent position
                    dx = other_pos[0] - current_pos[0]
                    dy = other_pos[1] - current_pos[1]
                    break
        else:
            # Main behavior: seek novelty
            dx, dy = self.find_unvisited_direction(bounds)

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
            'type': 'explorer'
        }


def create_explorers(n: int, bounds: Tuple[float, float, float, float],
                    start_id: int = 1000) -> list[Explorer]:
    """
    Create a population of Explorer agents.

    Args:
        n: Number of agents to create
        bounds: (min_x, max_x, min_y, max_y) for positioning
        start_id: Starting ID number for agents (offset from Connectors)

    Returns:
        List of Explorer agents
    """
    min_x, max_x, min_y, max_y = bounds
    agents = []

    for i in range(n):
        agent = Explorer(
            x=random.uniform(min_x, max_x),
            y=random.uniform(min_y, max_y),
            id=start_id + i,
            base_speed=random.uniform(1.3, 1.7),  # Faster than Connectors
        )
        agents.append(agent)

    return agents
