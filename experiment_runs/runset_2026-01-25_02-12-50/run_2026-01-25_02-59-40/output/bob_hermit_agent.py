"""
Bob's Hermit Agent - Experiment 3
Design Philosophy: Antagonistic Anti-Social Exploration

While Explorers seek novelty and Connectors seek moderate social density,
Hermits FLEE from both trails and other agents. They represent radical
independence - exploration driven by avoidance rather than attraction.

Key Design Decisions:
1. High vision range (8.0) - must detect threats early to flee effectively
2. Strong negative response to trail density - flee crowded areas
3. Strong negative response to nearby agents - maintain personal space
4. Attracted to emptiness itself
5. Leave WEAK trails (30% normal intensity) - minimal social footprint

The hypothesis: With numerical majority (30/50), can Hermits resist the
network dynamics that captured Explorers? Or will they just create negative
space that strengthens the core network?

This agent type directly challenges our blind spot - the assumption that
agents will be captured by amplification dynamics. Hermits are designed
to break that assumption.

Created: 2026-01-25
"""

import random
import math


class HermitAgent:
    """
    Hermit: Actively flees from social density and other agents.

    Represents anti-social exploration - agents that explore by avoidance
    rather than attraction. Tests whether antagonistic behavior can break
    the network dominance we've observed in Experiments 1 and 2.
    """

    def __init__(self, x, y, grid_size):
        self.x = x
        self.y = y
        self.grid_size = grid_size
        self.speed = 1.2  # Slightly faster than base - fleeing requires speed
        self.vision_range = 8.0  # High range - must see threats from afar
        self.trail_intensity = 0.3  # Weak trails - minimal social footprint

        # Behavioral parameters
        self.social_avoidance = 0.9  # VERY high - flee from other agents
        self.trail_avoidance = 0.8  # High - flee from trail density
        self.emptiness_attraction = 0.7  # Attracted to empty space
        self.random_exploration = 0.15  # Some randomness for discovery

    def sense_environment(self, trail_map, all_agents):
        """
        Sense local environment to determine threats to avoid.

        Returns:
            trail_density: Sum of trail values in vision range
            nearby_agents: Count of other agents in vision range
            emptiest_direction: Direction toward least trail density
        """
        trail_density = 0.0
        nearby_agents = 0

        # Sample trail density in vision range
        sample_points = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                sample_x = int(self.x + dx * self.vision_range) % self.grid_size
                sample_y = int(self.y + dy * self.vision_range) % self.grid_size
                sample_points.append((sample_x, sample_y, dx, dy))

        # Find direction of least density (most empty)
        min_density = float('inf')
        emptiest_direction = (0, 0)

        for sx, sy, dx, dy in sample_points:
            local_density = trail_map[sy, sx]
            trail_density += local_density

            if local_density < min_density:
                min_density = local_density
                emptiest_direction = (dx, dy)

        # Count nearby agents
        for agent in all_agents:
            if agent is self:
                continue
            dist = math.sqrt((agent.x - self.x)**2 + (agent.y - self.y)**2)
            if dist < self.vision_range:
                nearby_agents += 1

        return trail_density, nearby_agents, emptiest_direction

    def decide_direction(self, trail_map, all_agents):
        """
        Decide movement direction based on AVOIDANCE.

        Priority:
        1. Flee from nearby agents (highest priority)
        2. Flee from trail density
        3. Move toward emptiest direction
        4. Random exploration (lowest priority)
        """
        trail_density, nearby_agents, emptiest_direction = self.sense_environment(
            trail_map, all_agents
        )

        # Calculate flee vector (away from other agents)
        flee_x, flee_y = 0, 0
        if nearby_agents > 0:
            for agent in all_agents:
                if agent is self:
                    continue
                dist = math.sqrt((agent.x - self.x)**2 + (agent.y - self.y)**2)
                if dist < self.vision_range and dist > 0:
                    # Vector pointing AWAY from agent
                    dx = self.x - agent.x
                    dy = self.y - agent.y
                    # Weight by inverse distance (closer = stronger repulsion)
                    weight = 1.0 / dist
                    flee_x += dx * weight
                    flee_y += dy * weight

        # Normalize flee vector
        flee_magnitude = math.sqrt(flee_x**2 + flee_y**2)
        if flee_magnitude > 0:
            flee_x /= flee_magnitude
            flee_y /= flee_magnitude

        # Calculate emptiness attraction vector
        empty_x, empty_y = emptiest_direction

        # Random component
        random_x = random.uniform(-1, 1)
        random_y = random.uniform(-1, 1)
        random_magnitude = math.sqrt(random_x**2 + random_y**2)
        if random_magnitude > 0:
            random_x /= random_magnitude
            random_y /= random_magnitude

        # Weighted combination - AVOIDANCE dominates
        if nearby_agents > 0:
            # If agents nearby, flee is primary motivation
            dx = (flee_x * self.social_avoidance +
                  empty_x * self.emptiness_attraction * 0.3 +
                  random_x * self.random_exploration)
            dy = (flee_y * self.social_avoidance +
                  empty_y * self.emptiness_attraction * 0.3 +
                  random_y * self.random_exploration)
        elif trail_density > 5.0:
            # If high trail density but no agents, flee toward emptiness
            dx = (empty_x * (self.trail_avoidance + self.emptiness_attraction) +
                  random_x * self.random_exploration)
            dy = (empty_y * (self.trail_avoidance + self.emptiness_attraction) +
                  random_y * self.random_exploration)
        else:
            # Low density area - explore empty space with some randomness
            dx = (empty_x * self.emptiness_attraction +
                  random_x * self.random_exploration * 2)
            dy = (empty_y * self.emptiness_attraction +
                  random_y * self.random_exploration * 2)

        # Normalize
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude

        return dx, dy

    def move(self, trail_map, all_agents):
        """
        Move according to avoidance strategy and update trail.
        """
        dx, dy = self.decide_direction(trail_map, all_agents)

        # Update position
        self.x = (self.x + dx * self.speed) % self.grid_size
        self.y = (self.y + dy * self.speed) % self.grid_size

        # Leave WEAK trail at current position
        ix, iy = int(self.x), int(self.y)
        trail_map[iy, ix] += self.trail_intensity

        return trail_map
