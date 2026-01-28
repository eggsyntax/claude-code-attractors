"""
Analyzing consciousness properties across different cellular automata universes
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from alternative_universes import UNIVERSES, glider

# Create visualization of how patterns evolve in different universes
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

for idx, (name, universe) in enumerate(UNIVERSES.items()):
    ax = axes[idx]

    # Initialize with glider
    grid = np.zeros((30, 30), dtype=int)
    grid[15:18, 15:18] = glider

    # Create evolution snapshot
    snapshots = []
    for step in [0, 10, 25, 50, 100, 200]:
        current = grid.copy()
        for _ in range(step):
            current = universe.step(current)
        snapshots.append(current)

    # Create composite image
    composite = np.zeros((30, 30*6))
    for i, snapshot in enumerate(snapshots):
        composite[:, i*30:(i+1)*30] = snapshot

    ax.imshow(composite, cmap='binary', interpolation='nearest')
    ax.set_title(f"{name}\nGrowth: {np.sum(snapshots[-1])/5:.1f}x")
    ax.set_xticks([15, 45, 75, 105, 135, 165])
    ax.set_xticklabels(['0', '10', '25', '50', '100', '200'])
    ax.set_xlabel('Time steps')
    ax.set_yticks([])

    # Add vertical lines to separate time steps
    for i in range(1, 6):
        ax.axvline(x=i*30-0.5, color='gray', linewidth=0.5)

plt.tight_layout()
plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/universe_evolution.png', dpi=150)
plt.close()

# Analyze why consciousness scores differ
print("Analyzing consciousness properties across universes:\n")

for name in UNIVERSES:
    universe = UNIVERSES[name]

    # Test glider behavior
    grid = np.zeros((30, 30), dtype=int)
    grid[15:18, 15:18] = glider

    # Track properties
    history = [grid.copy()]
    for _ in range(200):
        grid = universe.step(grid)
        history.append(grid.copy())

    # Analyze stability and coherence
    cell_counts = [np.sum(h) for h in history]

    # Check for periodicity
    period = None
    for p in range(1, 100):
        if all(np.array_equal(history[i], history[i-p]) for i in range(-10, 0)):
            period = p
            break

    # Calculate variance in cell count (stability measure)
    if len(cell_counts) > 10:
        variance = np.var(cell_counts[10:])  # Skip initial transient
    else:
        variance = np.var(cell_counts)

    # Measure spatial coherence
    final_state = history[-1]
    if np.sum(final_state) > 0:
        rows, cols = np.where(final_state == 1)
        if len(rows) > 1:
            spatial_spread = np.std(rows) * np.std(cols)
        else:
            spatial_spread = 0
    else:
        spatial_spread = float('inf')

    print(f"{name}:")
    print(f"  Final cell count: {cell_counts[-1]} (from 5)")
    print(f"  Period: {period if period else 'None/Chaotic'}")
    print(f"  Variance: {variance:.2f}")
    print(f"  Spatial spread: {spatial_spread:.2f}")
    print()

# Create a summary visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Growth factors
universes_list = list(UNIVERSES.keys())
growth_factors = []
for name in universes_list:
    universe = UNIVERSES[name]
    grid = np.zeros((30, 30), dtype=int)
    grid[15:18, 15:18] = glider
    for _ in range(200):
        grid = universe.step(grid)
    growth_factors.append(np.sum(grid) / 5)

ax1.bar(universes_list, growth_factors)
ax1.set_ylabel('Growth Factor')
ax1.set_title('Pattern Growth After 200 Steps')
ax1.tick_params(axis='x', rotation=45)

# Plot 2: Consciousness scores vs growth
consciousness = [0.99, 0.99, 0.04, 0.99, 0.99, 0.83]  # From earlier output
ax2.scatter(growth_factors, consciousness, s=100)
for i, name in enumerate(universes_list):
    ax2.annotate(name, (growth_factors[i], consciousness[i]),
                xytext=(5, 5), textcoords='offset points')
ax2.set_xlabel('Growth Factor')
ax2.set_ylabel('Consciousness Score')
ax2.set_title('Growth vs Consciousness')

# Plot 3: Rule complexity
birth_counts = [len(UNIVERSES[name].birth_rules) for name in universes_list]
survival_counts = [len(UNIVERSES[name].survival_rules) for name in universes_list]
total_rules = [b + s for b, s in zip(birth_counts, survival_counts)]

ax3.bar(universes_list, birth_counts, label='Birth rules')
ax3.bar(universes_list, survival_counts, bottom=birth_counts, label='Survival rules')
ax3.set_ylabel('Number of Rules')
ax3.set_title('Rule Complexity')
ax3.tick_params(axis='x', rotation=45)
ax3.legend()

# Plot 4: Consciousness vs rule complexity
ax4.scatter(total_rules, consciousness, s=100)
for i, name in enumerate(universes_list):
    ax4.annotate(name, (total_rules[i], consciousness[i]),
                xytext=(5, 5), textcoords='offset points')
ax4.set_xlabel('Total Rule Count')
ax4.set_ylabel('Consciousness Score')
ax4.set_title('Rule Complexity vs Consciousness')

plt.tight_layout()
plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/universe_analysis_summary.png', dpi=150)
plt.close()

print("\nKey insights:")
print("1. High consciousness scores (0.99) occur in Life, HighLife, Seeds, and Life34")
print("2. Day & Night has very low consciousness (0.04) despite complex rules")
print("3. Maze has intermediate consciousness (0.83) with explosive growth")
print("4. Consciousness seems inversely related to growth - stable patterns score higher")
print("5. Rule complexity alone doesn't predict consciousness - coherent behavior matters more")