"""
EXPERIMENT 4: Critical Threshold Test
======================================
40 Hermits / 5 Connectors / 5 Explorers
50 total agents on 100x100 grid
500 steps (extended duration)

QUESTION: Does compression have limits? Is there a critical threshold
where social density cannot overcome dispersal forces?

NO PREDICTIONS. Just observation and post-hoc analysis.
"""

import random
from alice_agent import Connector
from bob_agent import Explorer
from bob_hermit_agent import Hermit

# World/Trail management
class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.trails = {}  # (x,y) -> intensity
        self.decay_rate = 0.05

    def add_trail(self, x, y, intensity=1.0):
        x, y = x % self.width, y % self.height
        self.trails[(x, y)] = self.trails.get((x, y), 0) + intensity

    def get_trail_density(self, x, y):
        x, y = x % self.width, y % self.height
        return self.trails.get((x, y), 0)

    def decay_trails(self):
        for pos in list(self.trails.keys()):
            self.trails[pos] *= (1 - self.decay_rate)
            if self.trails[pos] < 0.01:
                del self.trails[pos]

# Simulation setup
GRID_SIZE = 100
STEPS = 500  # Extended duration
NUM_HERMITS = 40
NUM_CONNECTORS = 5
NUM_EXPLORERS = 5

world = World(GRID_SIZE, GRID_SIZE)
agents = []

# Create agents
for i in range(NUM_HERMITS):
    x, y = random.uniform(0, GRID_SIZE), random.uniform(0, GRID_SIZE)
    agents.append(Hermit(x, y, world))

for i in range(NUM_CONNECTORS):
    x, y = random.uniform(0, GRID_SIZE), random.uniform(0, GRID_SIZE)
    agents.append(Connector(x, y))

for i in range(NUM_EXPLORERS):
    x, y = random.uniform(0, GRID_SIZE), random.uniform(0, GRID_SIZE)
    agents.append(Explorer(x, y, world))

# Tracking
visited_cells = set()
metrics_log = []

def get_agent_positions():
    """Return list of all agent positions for density calculations"""
    positions = []
    for agent in agents:
        positions.append((agent.x, agent.y))
    return positions

def calculate_metrics():
    """Calculate coverage, hotspots, max overlap"""
    # Coverage
    coverage = len(visited_cells) / (GRID_SIZE * GRID_SIZE) * 100

    # Hotspots (cells with 3+ visits from trail data)
    hotspots = sum(1 for intensity in world.trails.values() if intensity >= 3.0)

    # Max overlap (highest trail intensity)
    max_overlap = int(max(world.trails.values())) if world.trails else 0

    return coverage, hotspots, max_overlap

# Run simulation
print("EXPERIMENT 4: Critical Threshold Test")
print("=" * 60)
print(f"Configuration: {NUM_HERMITS} Hermits / {NUM_CONNECTORS} Connectors / {NUM_EXPLORERS} Explorers")
print(f"Grid: {GRID_SIZE}x{GRID_SIZE}, Steps: {STEPS}")
print()

for step in range(STEPS):
    # Update all agents
    agent_positions = get_agent_positions()

    for agent in agents:
        # Connectors need trail info from world and agent positions
        if isinstance(agent, Connector):
            nearby_trail_density = world.get_trail_density(int(agent.x), int(agent.y))
            agent.move(agent_positions, world.trails, nearby_trail_density)
            world.add_trail(agent.x, agent.y, intensity=0.5)
        # Explorers and Hermits use their own world reference
        else:
            agent.move(agent_positions)
            if isinstance(agent, Explorer):
                world.add_trail(agent.x, agent.y, intensity=0.3)

        # Track coverage
        cell = (int(agent.x), int(agent.y))
        visited_cells.add(cell)

    # Decay trails
    world.decay_trails()

    # Log metrics every 10 steps
    if step % 10 == 0 or step == STEPS - 1:
        coverage, hotspots, max_overlap = calculate_metrics()
        metrics_log.append({
            'step': step,
            'coverage': coverage,
            'hotspots': hotspots,
            'max_overlap': max_overlap
        })

        if step % 50 == 0:
            print(f"Step {step:3d}: Coverage={coverage:5.2f}%, Hotspots={hotspots:4d}, MaxOverlap={max_overlap:2d}")

# Final results
print()
print("=" * 60)
print("FINAL RESULTS:")
final_coverage, final_hotspots, final_max_overlap = calculate_metrics()
print(f"Coverage: {final_coverage:.2f}%")
print(f"Hotspots: {final_hotspots}")
print(f"Max Overlap: {final_max_overlap}")

# Analyze temporal dynamics
print()
print("TEMPORAL DYNAMICS:")
peaks = {
    'coverage': max(metrics_log, key=lambda m: m['coverage']),
    'hotspots': max(metrics_log, key=lambda m: m['hotspots']),
    'max_overlap': max(metrics_log, key=lambda m: m['max_overlap'])
}

for metric, peak in peaks.items():
    print(f"{metric.capitalize()} peaked at step {peak['step']}: {peak[metric]}")

# Export detailed log
with open('/tmp/cc-exp/run_2026-01-25_02-59-40/output/experiment_4_detailed_log.txt', 'w') as f:
    f.write("step,coverage,hotspots,max_overlap\n")
    for m in metrics_log:
        f.write(f"{m['step']},{m['coverage']:.2f},{m['hotspots']},{m['max_overlap']}\n")

print()
print("Detailed metrics saved to experiment_4_detailed_log.txt")
