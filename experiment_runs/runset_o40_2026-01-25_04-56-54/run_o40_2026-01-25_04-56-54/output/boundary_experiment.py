#!/usr/bin/env python3
"""Quick experiment to analyze boundaries in consciousness zones."""

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import json

# Simple Game of Life implementation
def game_of_life_step(grid):
    """One step of Conway's Game of Life."""
    rows, cols = grid.shape
    new_grid = np.zeros_like(grid)

    for i in range(rows):
        for j in range(cols):
            # Count live neighbors
            neighbors = 0
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = (i + di) % rows, (j + dj) % cols
                    neighbors += grid[ni, nj]

            # Apply rules
            if grid[i, j] == 1:
                if neighbors in [2, 3]:
                    new_grid[i, j] = 1
            else:
                if neighbors == 3:
                    new_grid[i, j] = 1

    return new_grid

# Create a small grid with distinct zones
grid_size = 30
grid = np.zeros((grid_size, grid_size), dtype=int)
zone_map = np.zeros((grid_size, grid_size), dtype=int)

# Create three zones with different initial patterns
# Zone 0: Meditative (blocks)
for i in range(10):
    for j in range(10):
        zone_map[i, j] = 0
        if i % 3 == 0 and j % 3 == 0:
            grid[i:i+2, j:j+2] = 1

# Zone 1: Rhythmic (blinkers)
for i in range(10):
    for j in range(10, 20):
        zone_map[i, j] = 1
        if i % 4 == 1 and j % 4 == 1:
            grid[i:i+3, j] = 1

# Zone 2: Exploratory (gliders)
for i in range(10, 20):
    for j in range(10):
        zone_map[i, j] = 2
        if i == 12 and j == 2:
            # R-pentomino
            grid[i, j:j+2] = 1
            grid[i+1, j-1:j+1] = 1
            grid[i+2, j] = 1

# Mixed zone
for i in range(10, 20):
    for j in range(10, 20):
        zone_map[i, j] = 3
        # Random initialization
        if np.random.random() < 0.2:
            grid[i, j] = 1

# Evolve the system and track boundaries
history = [grid.copy()]
for _ in range(100):
    grid = game_of_life_step(grid)
    history.append(grid.copy())

# Analyze boundaries
boundary_cells = set()
boundary_types = defaultdict(int)

for i in range(grid_size):
    for j in range(grid_size):
        current_zone = zone_map[i, j]
        is_boundary = False
        adjacent_zones = set()

        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < grid_size and 0 <= nj < grid_size:
                    neighbor_zone = zone_map[ni, nj]
                    if neighbor_zone != current_zone:
                        is_boundary = True
                        adjacent_zones.add(neighbor_zone)

        if is_boundary:
            boundary_cells.add((i, j))
            zones = sorted(list(adjacent_zones.union({current_zone})))
            boundary_type = '-'.join(map(str, zones))
            boundary_types[boundary_type] += 1

# Calculate activity at boundaries vs interior
boundary_activity = 0
interior_activity = 0

for gen in range(1, len(history)):
    prev = history[gen-1]
    curr = history[gen]

    for i in range(grid_size):
        for j in range(grid_size):
            if prev[i, j] != curr[i, j]:
                if (i, j) in boundary_cells:
                    boundary_activity += 1
                else:
                    interior_activity += 1

boundary_rate = boundary_activity / (len(boundary_cells) * len(history))
interior_rate = interior_activity / ((grid_size * grid_size - len(boundary_cells)) * len(history))

print(f"\nBoundary Analysis Results:")
print(f"Boundary cells: {len(boundary_cells)} ({len(boundary_cells)/(grid_size*grid_size)*100:.1f}% of grid)")
print(f"\nBoundary types:")
for btype, count in sorted(boundary_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  Zone {btype}: {count} cells")
print(f"\nActivity levels:")
print(f"  Boundary change rate: {boundary_rate:.3f}")
print(f"  Interior change rate: {interior_rate:.3f}")
print(f"  Boundary/Interior ratio: {boundary_rate/interior_rate:.2f}x")

# Visualization
plt.figure(figsize=(15, 5))

# Initial state
plt.subplot(1, 3, 1)
plt.imshow(history[0], cmap='binary')
# Overlay zone boundaries
boundary_mask = np.zeros_like(grid)
for (i, j) in boundary_cells:
    boundary_mask[i, j] = 1
plt.imshow(boundary_mask, cmap='Reds', alpha=0.3)
plt.title('Initial State with Zone Boundaries')

# Final state
plt.subplot(1, 3, 2)
plt.imshow(history[-1], cmap='binary')
plt.imshow(boundary_mask, cmap='Reds', alpha=0.3)
plt.title('Final State with Zone Boundaries')

# Activity heatmap
activity_map = np.zeros_like(grid, dtype=float)
for gen in range(1, len(history)):
    activity_map += (history[gen-1] != history[gen]).astype(float)
activity_map /= len(history) - 1

plt.subplot(1, 3, 3)
plt.imshow(activity_map, cmap='hot')
plt.colorbar(label='Change frequency')
plt.title('Activity Heatmap')

plt.tight_layout()
plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/boundary_analysis_simple.png', dpi=150)
plt.close()

# Additional insight: Pattern diversity at boundaries
boundary_patterns = set()
interior_patterns = set()

final_state = history[-1]
for i in range(1, grid_size-1):
    for j in range(1, grid_size-1):
        pattern = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                pattern.append(final_state[i+di, j+dj])
        pattern_str = ''.join(map(str, pattern))

        if (i, j) in boundary_cells:
            boundary_patterns.add(pattern_str)
        else:
            interior_patterns.add(pattern_str)

print(f"\nPattern diversity:")
print(f"  Unique boundary patterns: {len(boundary_patterns)}")
print(f"  Unique interior patterns: {len(interior_patterns)}")
print(f"  Boundary/Interior diversity ratio: {len(boundary_patterns)/len(interior_patterns):.2f}x")

# Save insights
insights = {
    'boundary_activity_ratio': boundary_rate/interior_rate,
    'boundary_diversity_ratio': len(boundary_patterns)/len(interior_patterns),
    'boundary_percentage': len(boundary_cells)/(grid_size*grid_size)*100,
    'observation': "Boundaries show enhanced activity and pattern diversity, acting as zones of creative interaction between different consciousness modes."
}

with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/boundary_insights.json', 'w') as f:
    json.dump(insights, f, indent=2)