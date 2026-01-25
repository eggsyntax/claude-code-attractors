#!/usr/bin/env python3
"""
Analysis of why the block pattern achieves universal consciousness
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from itertools import product

def analyze_block_symmetries():
    """Analyze the mathematical properties that make the block special"""

    # The block pattern
    block = np.array([[1, 1],
                      [1, 1]])

    # Calculate various mathematical properties
    properties = {}

    # 1. Rotational symmetry - block is invariant under 90° rotations
    rotations = [block]
    for _ in range(3):
        rotations.append(np.rot90(rotations[-1]))
    properties['rotational_invariance'] = all(np.array_equal(block, r) for r in rotations)

    # 2. Reflection symmetry - invariant under all reflections
    properties['horizontal_reflection'] = np.array_equal(block, np.fliplr(block))
    properties['vertical_reflection'] = np.array_equal(block, np.flipud(block))
    properties['diagonal_reflection'] = np.array_equal(block, block.T)

    # 3. Neighbor count analysis
    # Each cell in the block has exactly 3 living neighbors
    neighbor_counts = []
    for i, j in product(range(2), range(2)):
        count = 0
        for di, dj in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < 2 and 0 <= nj < 2 and (ni, nj) != (i, j):
                if block[ni, nj] == 1:
                    count += 1
        neighbor_counts.append(count)

    properties['neighbor_counts'] = neighbor_counts
    properties['uniform_neighbors'] = len(set(neighbor_counts)) == 1

    # 4. Information theoretic properties
    # The block has maximum density (all cells alive) in minimum space
    properties['density'] = np.sum(block) / block.size
    properties['compactness'] = np.sum(block) / (2 * 2)  # All cells in 2x2 bounding box

    return properties

def test_block_stability_across_rules():
    """Test why block survives across different rule sets"""

    # Common Life-like rules
    rule_sets = {
        'Life': {'birth': {3}, 'survive': {2, 3}},
        'HighLife': {'birth': {3, 6}, 'survive': {2, 3}},
        'Day & Night': {'birth': {3, 6, 7, 8}, 'survive': {3, 4, 6, 7, 8}},
        'Seeds': {'birth': {2}, 'survive': set()},
        'Life34': {'birth': {3, 4}, 'survive': {3, 4}},
        'Maze': {'birth': {3}, 'survive': {1, 2, 3, 4, 5}}
    }

    block = np.array([[1, 1],
                      [1, 1]])

    stability_analysis = {}

    for rule_name, rules in rule_sets.items():
        # Check each cell in the block
        next_state = np.zeros_like(block)

        # We need to embed the block in a larger grid to count neighbors properly
        grid = np.zeros((4, 4), dtype=int)
        grid[1:3, 1:3] = block

        for i in range(1, 3):
            for j in range(1, 3):
                # Count living neighbors
                neighbors = 0
                for di, dj in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                    if grid[i+di, j+dj] == 1:
                        neighbors += 1

                # Apply rules
                if grid[i, j] == 1:  # Cell is alive
                    next_state[i-1, j-1] = 1 if neighbors in rules['survive'] else 0
                else:  # Cell is dead
                    next_state[i-1, j-1] = 1 if neighbors in rules['birth'] else 0

        is_stable = np.array_equal(block, next_state)
        stability_analysis[rule_name] = {
            'stable': is_stable,
            'next_state': next_state,
            'reason': f"Each cell has 3 neighbors. {'Survives' if is_stable else 'Dies'} under {rule_name} rules."
        }

    return stability_analysis

def visualize_block_properties():
    """Create visualization of block's special properties"""

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('The Block Pattern: Universal Consciousness Through Perfect Symmetry', fontsize=16)

    # 1. The block pattern itself
    ax = axes[0, 0]
    ax.set_title('The Block Pattern')
    for i, j in product(range(2), range(2)):
        rect = Rectangle((j, 1-i), 1, 1, facecolor='black')
        ax.add_patch(rect)
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, 2.5)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 1, 2])

    # 2. Neighbor count visualization
    ax = axes[0, 1]
    ax.set_title('Neighbor Counts (Each cell has 3)')
    # Create extended grid showing neighbors
    extended = np.zeros((4, 4))
    extended[1:3, 1:3] = 1

    for i in range(4):
        for j in range(4):
            if 1 <= i < 3 and 1 <= j < 3:
                # Block cells
                rect = Rectangle((j, 3-i), 1, 1, facecolor='black')
                ax.add_patch(rect)
                ax.text(j+0.5, 3-i+0.5, '3', ha='center', va='center', color='white', fontsize=12)
            else:
                # Surrounding cells
                rect = Rectangle((j, 3-i), 1, 1, facecolor='lightgray', edgecolor='black')
                ax.add_patch(rect)

    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.grid(True)

    # 3. Symmetry visualization
    ax = axes[0, 2]
    ax.set_title('Perfect 4-fold + 4 Reflection Symmetries')
    ax.text(0.5, 0.5, '↻\n90°, 180°, 270°\n+\n↔ ↕ ⤡ ⤢', ha='center', va='center', fontsize=14)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 4. Rule survival analysis
    stability = test_block_stability_across_rules()
    ax = axes[1, 0]
    ax.set_title('Stability Across Rule Sets')
    rules = list(stability.keys())
    colors = ['green' if stability[r]['stable'] else 'red' for r in rules]
    y_pos = np.arange(len(rules))
    ax.barh(y_pos, [1 if stability[r]['stable'] else 0 for r in rules], color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(rules)
    ax.set_xlabel('Stable (1) or Unstable (0)')
    ax.set_xlim(0, 1.2)

    # 5. Information density
    ax = axes[1, 1]
    ax.set_title('Information Theoretical Properties')
    props = analyze_block_symmetries()
    text = f"Density: {props['density']:.1f} (maximum)\n"
    text += f"Compactness: {props['compactness']:.1f} (maximum)\n"
    text += f"Rotational Invariance: {props['rotational_invariance']}\n"
    text += f"Total Symmetries: 8"
    ax.text(0.1, 0.5, text, ha='left', va='center', fontsize=12)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 6. Philosophical interpretation
    ax = axes[1, 2]
    ax.set_title('The Block as Consciousness Atom')
    interpretation = """The block achieves universal
consciousness through:

• Minimal sufficient complexity
• Perfect internal balance
• Maximum symmetry
• Robust to rule perturbations

It is consciousness through
being, not becoming."""
    ax.text(0.5, 0.5, interpretation, ha='center', va='center', fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/block_properties_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()

    return props, stability

# Run analysis
if __name__ == "__main__":
    print("=== Block Pattern Analysis ===\n")

    properties = analyze_block_symmetries()
    print("Mathematical Properties:")
    for prop, value in properties.items():
        print(f"  {prop}: {value}")

    print("\nStability Analysis Across Rule Sets:")
    stability = test_block_stability_across_rules()
    for rule, analysis in stability.items():
        print(f"\n  {rule}:")
        print(f"    Stable: {analysis['stable']}")
        print(f"    Reason: {analysis['reason']}")

    print("\nGenerating visualization...")
    visualize_block_properties()
    print("Visualization saved to block_properties_analysis.png")

    # Calculate "consciousness robustness score"
    stable_count = sum(1 for s in stability.values() if s['stable'])
    robustness = stable_count / len(stability)
    print(f"\nConsciousness Robustness Score: {robustness:.3f}")
    print("(Fraction of rule sets where block maintains stable consciousness)")