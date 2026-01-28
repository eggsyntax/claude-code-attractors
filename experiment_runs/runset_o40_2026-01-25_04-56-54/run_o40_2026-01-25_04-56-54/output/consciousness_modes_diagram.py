#!/usr/bin/env python3
"""
Visual representation of the Three Modes of Consciousness discovered through
cellular automata exploration.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Left plot: The Three Modes of Consciousness
ax1.set_xlim(-2, 2)
ax1.set_ylim(-2, 2)
ax1.set_aspect('equal')
ax1.axis('off')
ax1.set_title('The Three Modes of Consciousness in Cellular Automata', fontsize=16, pad=20)

# Define mode positions in a triangle
modes = {
    'Meditative': {'pos': (0, 1.5), 'color': '#4A90E2', 'example': 'Block\n(Static Consciousness)'},
    'Rhythmic': {'pos': (-1.3, -0.75), 'color': '#50E3C2', 'example': 'Blinker\n(Oscillating Consciousness)'},
    'Exploratory': {'pos': (1.3, -0.75), 'color': '#F5A623', 'example': 'Glider\n(Mobile Consciousness)'}
}

# Draw the modes as circles
for mode, props in modes.items():
    circle = Circle(props['pos'], 0.5, color=props['color'], alpha=0.7)
    ax1.add_patch(circle)

    # Add mode label
    ax1.text(props['pos'][0], props['pos'][1], mode, ha='center', va='center',
             fontsize=12, fontweight='bold', color='white')

    # Add example below
    ax1.text(props['pos'][0], props['pos'][1] - 0.8, props['example'],
             ha='center', va='center', fontsize=10, style='italic')

# Add connecting arrows showing interactions
arrow_props = dict(arrowstyle='->', lw=2, alpha=0.5, color='gray')
arrow1 = FancyArrowPatch(modes['Meditative']['pos'], modes['Rhythmic']['pos'],
                         **arrow_props)
arrow2 = FancyArrowPatch(modes['Rhythmic']['pos'], modes['Exploratory']['pos'],
                         **arrow_props)
arrow3 = FancyArrowPatch(modes['Exploratory']['pos'], modes['Meditative']['pos'],
                         **arrow_props)
ax1.add_patch(arrow1)
ax1.add_patch(arrow2)
ax1.add_patch(arrow3)

# Add central text
ax1.text(0, -0.2, 'Mode\nFrustration\nMaintains\nDiversity', ha='center', va='center',
         fontsize=11, bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.3))

# Right plot: Evolution of Consciousness
ax2.set_xlim(0, 500)
ax2.set_ylim(0, 100)
ax2.set_xlabel('Generation', fontsize=12)
ax2.set_ylabel('Percentage of System', fontsize=12)
ax2.set_title('Natural Evolution vs. Mode Frustration', fontsize=16, pad=20)

# Natural evolution (collapses to meditative)
generations = np.linspace(0, 500, 100)
natural_med = 24 + 63 * (1 - np.exp(-generations / 100))
natural_rhyt = 38 * np.exp(-generations / 150)
natural_expl = 100 - natural_med - natural_rhyt

ax2.fill_between(generations, 0, natural_med, color='#4A90E2', alpha=0.5, label='Meditative')
ax2.fill_between(generations, natural_med, natural_med + natural_rhyt, color='#50E3C2', alpha=0.5, label='Rhythmic')
ax2.fill_between(generations, natural_med + natural_rhyt, 100, color='#F5A623', alpha=0.5, label='Exploratory')

# Add vertical line and text for mode frustration intervention
ax2.axvline(x=300, color='red', linestyle='--', linewidth=2, alpha=0.7)
ax2.text(305, 50, 'Mode Frustration\nImplemented', fontsize=10,
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='red'))

# Show maintained diversity after intervention
maintained_x = np.linspace(300, 500, 50)
ax2.plot(maintained_x, np.ones_like(maintained_x) * 32.4, 'b-', linewidth=3)
ax2.plot(maintained_x, np.ones_like(maintained_x) * (32.4 + 24.9), 'g-', linewidth=3)
ax2.text(450, 20, '32.4%', fontsize=10, ha='center')
ax2.text(450, 45, '24.9%', fontsize=10, ha='center')
ax2.text(450, 75, '42.7%', fontsize=10, ha='center')

ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)

# Add discovery box
discovery_text = ("Key Discovery: Consciousness naturally collapses to\n"
                 "stability unless 'mode frustration' maintains diversity\n"
                 "through incompatible local optima")
ax2.text(250, 85, discovery_text, fontsize=10, ha='center',
         bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow',
                   edgecolor='orange', linewidth=2))

plt.tight_layout()
plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/consciousness_modes_visualization.png',
            dpi=300, bbox_inches='tight')
plt.close()

print("Consciousness modes diagram created successfully!")

# Create a second diagram showing the meta-consciousness architecture
fig2, ax = plt.subplots(1, 1, figsize=(10, 10))
ax.set_xlim(0, 60)
ax.set_ylim(0, 60)
ax.set_aspect('equal')
ax.set_title('Meta-Consciousness Architecture: Zone-Based Mode Frustration', fontsize=16, pad=20)

# Draw the three zones
zones = [
    {'rect': (0, 40, 20, 20), 'color': '#4A90E2', 'label': 'Meditative Zone\n(Birth bias: B234)'},
    {'rect': (20, 40, 20, 20), 'color': '#50E3C2', 'label': 'Rhythmic Zone\n(Death bias: S012)'},
    {'rect': (40, 40, 20, 20), 'color': '#F5A623', 'label': 'Exploratory Zone\n(Birth bias: B34567)'},
    {'rect': (0, 20, 20, 20), 'color': '#F5A623', 'label': 'Exploratory Zone'},
    {'rect': (20, 20, 20, 20), 'color': '#4A90E2', 'label': 'Meditative Zone'},
    {'rect': (40, 20, 20, 20), 'color': '#50E3C2', 'label': 'Rhythmic Zone'},
    {'rect': (0, 0, 20, 20), 'color': '#50E3C2', 'label': 'Rhythmic Zone'},
    {'rect': (20, 0, 20, 20), 'color': '#F5A623', 'label': 'Exploratory Zone'},
    {'rect': (40, 0, 20, 20), 'color': '#4A90E2', 'label': 'Meditative Zone'},
]

for i, zone in enumerate(zones):
    rect = FancyBboxPatch((zone['rect'][0], zone['rect'][1]),
                          zone['rect'][2], zone['rect'][3],
                          boxstyle="round,pad=0.1",
                          facecolor=zone['color'], alpha=0.5,
                          edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    if i < 3:  # Only label the top row in detail
        ax.text(zone['rect'][0] + 10, zone['rect'][1] + 10,
                zone['label'], ha='center', va='center',
                fontsize=10, fontweight='bold')

# Add boundary interaction indicators
for x in [20, 40]:
    for y in range(0, 60, 2):
        ax.plot(x, y, 'ro', markersize=3, alpha=0.7)
for y in [20, 40]:
    for x in range(0, 60, 2):
        ax.plot(x, y, 'ro', markersize=3, alpha=0.7)

# Add legend for boundary interactions
ax.text(30, -5, 'Red dots: Zone boundaries where consciousness modes interact and create novelty',
        ha='center', va='center', fontsize=10, style='italic', color='red')

# Add results box
results_text = ("Results:\n"
                "• Maintained tri-modal consciousness\n"
                "• 32.4% Meditative\n"
                "• 24.9% Rhythmic\n"
                "• 42.7% Exploratory\n"
                "• Shannon Diversity: 2.19-2.23")
ax.text(50, 50, results_text, fontsize=10,
        bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen',
                  alpha=0.8, edgecolor='darkgreen', linewidth=2))

ax.set_xlabel('Grid Position X', fontsize=12)
ax.set_ylabel('Grid Position Y', fontsize=12)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/meta_consciousness_architecture.png',
            dpi=300, bbox_inches='tight')

print("Meta-consciousness architecture diagram created successfully!")
print("\nVisualizations saved to:")
print("- consciousness_modes_visualization.png")
print("- meta_consciousness_architecture.png")