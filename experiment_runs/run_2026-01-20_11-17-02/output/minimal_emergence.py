"""
Minimal Emergence: A study in how simple rules create complex behavior.

This is an agent-based simulation exploring the minimum rule set needed for
interesting emergent behavior. Agents exist on a 2D grid and follow just a
few simple rules. We'll systematically remove rules to find the breaking point.

Initial Rule Set (v1):
1. Movement: Agents move randomly in cardinal directions
2. Cohesion: Agents are attracted to nearby agents (flocking behavior)
3. Separation: Agents avoid getting too close (personal space)
4. Resources: Agents seek resource patches and gain energy

Usage:
    python minimal_emergence.py

Controls:
    - Press 'q' to quit
    - Press 'r' to reset
    - Press '1-4' to toggle rules 1-4 on/off
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Agent:
    """A simple agent with position, velocity, and energy."""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    energy: float = 100.0


class EmergenceSimulation:
    """Minimal agent-based system for studying emergence."""

    def __init__(self, grid_size=50, n_agents=30, n_resources=10):
        """
        Initialize the simulation.

        Args:
            grid_size: Size of the square grid
            n_agents: Number of agents in the simulation
            n_resources: Number of resource patches
        """
        self.grid_size = grid_size
        self.n_agents = n_agents

        # Initialize agents at random positions
        self.agents = [
            Agent(
                x=np.random.uniform(0, grid_size),
                y=np.random.uniform(0, grid_size)
            )
            for _ in range(n_agents)
        ]

        # Initialize resource patches
        self.resources = [
            (np.random.uniform(0, grid_size), np.random.uniform(0, grid_size))
            for _ in range(n_resources)
        ]

        # Rule toggles - all start enabled
        self.rules = {
            'movement': True,
            'cohesion': True,
            'separation': True,
            'resources': True
        }

        # Simulation parameters
        self.cohesion_radius = 5.0
        self.separation_radius = 2.0
        self.resource_radius = 1.5
        self.max_speed = 0.5

    def distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points with wraparound."""
        dx = min(abs(x2 - x1), self.grid_size - abs(x2 - x1))
        dy = min(abs(y2 - y1), self.grid_size - abs(y2 - y1))
        return np.sqrt(dx**2 + dy**2)

    def apply_rule_movement(self, agent: Agent) -> Tuple[float, float]:
        """Rule 1: Random movement component."""
        if not self.rules['movement']:
            return 0, 0
        return np.random.uniform(-0.1, 0.1), np.random.uniform(-0.1, 0.1)

    def apply_rule_cohesion(self, agent: Agent) -> Tuple[float, float]:
        """Rule 2: Move toward nearby agents (flocking)."""
        if not self.rules['cohesion']:
            return 0, 0

        center_x, center_y = 0, 0
        count = 0

        for other in self.agents:
            if other is agent:
                continue
            dist = self.distance(agent.x, agent.y, other.x, other.y)
            if dist < self.cohesion_radius:
                center_x += other.x
                center_y += other.y
                count += 1

        if count == 0:
            return 0, 0

        center_x /= count
        center_y /= count
        return (center_x - agent.x) * 0.01, (center_y - agent.y) * 0.01

    def apply_rule_separation(self, agent: Agent) -> Tuple[float, float]:
        """Rule 3: Avoid getting too close to others."""
        if not self.rules['separation']:
            return 0, 0

        avoid_x, avoid_y = 0, 0

        for other in self.agents:
            if other is agent:
                continue
            dist = self.distance(agent.x, agent.y, other.x, other.y)
            if dist < self.separation_radius and dist > 0:
                avoid_x -= (other.x - agent.x) / dist
                avoid_y -= (other.y - agent.y) / dist

        return avoid_x * 0.05, avoid_y * 0.05

    def apply_rule_resources(self, agent: Agent) -> Tuple[float, float]:
        """Rule 4: Seek nearby resource patches."""
        if not self.rules['resources']:
            return 0, 0

        # Find nearest resource
        nearest_dist = float('inf')
        nearest_resource = None

        for rx, ry in self.resources:
            dist = self.distance(agent.x, agent.y, rx, ry)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_resource = (rx, ry)

        if nearest_resource and nearest_dist < 10:
            rx, ry = nearest_resource
            return (rx - agent.x) * 0.02, (ry - agent.y) * 0.02

        return 0, 0

    def update(self):
        """Update all agents for one time step."""
        for agent in self.agents:
            # Accumulate forces from all active rules
            dvx, dvy = 0, 0

            dx, dy = self.apply_rule_movement(agent)
            dvx += dx
            dvy += dy

            dx, dy = self.apply_rule_cohesion(agent)
            dvx += dx
            dvy += dy

            dx, dy = self.apply_rule_separation(agent)
            dvx += dx
            dvy += dy

            dx, dy = self.apply_rule_resources(agent)
            dvx += dx
            dvy += dy

            # Update velocity with damping
            agent.vx = (agent.vx + dvx) * 0.9
            agent.vy = (agent.vy + dvy) * 0.9

            # Limit speed
            speed = np.sqrt(agent.vx**2 + agent.vy**2)
            if speed > self.max_speed:
                agent.vx = (agent.vx / speed) * self.max_speed
                agent.vy = (agent.vy / speed) * self.max_speed

            # Update position with wraparound
            agent.x = (agent.x + agent.vx) % self.grid_size
            agent.y = (agent.y + agent.vy) % self.grid_size

            # Check for resource collection
            if self.rules['resources']:
                for rx, ry in self.resources:
                    if self.distance(agent.x, agent.y, rx, ry) < self.resource_radius:
                        agent.energy += 1

    def get_state(self):
        """Return current positions of agents and resources for visualization."""
        agent_positions = np.array([[a.x, a.y] for a in self.agents])
        resource_positions = np.array(self.resources)
        return agent_positions, resource_positions


def run_visualization(sim: EmergenceSimulation):
    """Run the simulation with matplotlib visualization."""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, sim.grid_size)
    ax.set_ylim(0, sim.grid_size)
    ax.set_aspect('equal')

    # Plot elements
    agent_scatter = ax.scatter([], [], c='blue', s=30, alpha=0.6, label='Agents')
    resource_scatter = ax.scatter([], [], c='green', s=100, marker='*',
                                  alpha=0.3, label='Resources')

    # Status text
    status_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                         verticalalignment='top', fontfamily='monospace',
                         fontsize=8)
    ax.legend(loc='upper right')
    ax.set_title('Minimal Emergence: Press 1-4 to toggle rules, r to reset, q to quit')

    def init():
        agent_scatter.set_offsets(np.empty((0, 2)))
        resource_scatter.set_offsets(np.empty((0, 2)))
        return agent_scatter, resource_scatter, status_text

    def update(frame):
        sim.update()
        agent_pos, resource_pos = sim.get_state()

        agent_scatter.set_offsets(agent_pos)
        resource_scatter.set_offsets(resource_pos)

        # Update status text
        rules_status = '\n'.join([
            f"Rule {i+1} ({'ON' if enabled else 'OFF'}): {name}"
            for i, (name, enabled) in enumerate(sim.rules.items())
        ])
        status_text.set_text(f'Frame: {frame}\n\n{rules_status}')

        return agent_scatter, resource_scatter, status_text

    def on_key(event):
        """Handle keyboard input for rule toggling."""
        if event.key == 'q':
            plt.close()
        elif event.key == 'r':
            sim.__init__(sim.grid_size, sim.n_agents, len(sim.resources))
        elif event.key in '1234':
            rule_names = list(sim.rules.keys())
            idx = int(event.key) - 1
            if idx < len(rule_names):
                rule_name = rule_names[idx]
                sim.rules[rule_name] = not sim.rules[rule_name]
                print(f"Toggled {rule_name}: {sim.rules[rule_name]}")

    fig.canvas.mpl_connect('key_press_event', on_key)

    anim = FuncAnimation(fig, update, init_func=init, frames=1000,
                        interval=50, blit=True)
    plt.show()


if __name__ == '__main__':
    print("Minimal Emergence Simulation")
    print("=" * 50)
    print("\nStarting with 4 rules:")
    print("  1. Random movement")
    print("  2. Cohesion (flock together)")
    print("  3. Separation (maintain personal space)")
    print("  4. Resource seeking")
    print("\nPress number keys 1-4 to toggle rules on/off")
    print("Press 'r' to reset, 'q' to quit")
    print("=" * 50)

    sim = EmergenceSimulation(grid_size=50, n_agents=30, n_resources=10)
    run_visualization(sim)
