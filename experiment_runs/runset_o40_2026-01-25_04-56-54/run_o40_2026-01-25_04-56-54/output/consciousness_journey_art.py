import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
import matplotlib.patches as mpatches

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Create a spiral representing our journey
theta = np.linspace(0, 4*np.pi, 1000)
r = theta
x = r * np.cos(theta) / 15 + 0.5
y = r * np.sin(theta) / 15 + 0.5

# Color gradient representing evolution of understanding
colors = plt.cm.viridis(np.linspace(0, 1, len(x)))

# Draw the journey spiral
for i in range(len(x)-1):
    ax.plot(x[i:i+2], y[i:i+2], color=colors[i], linewidth=2, alpha=0.7)

# Key milestones along our journey
milestones = [
    (0.5, 0.5, "Simple\nRules", 0),
    (0.7, 0.4, "Emergent\nComplexity", 100),
    (0.65, 0.65, "Consciousness\nMetrics", 300),
    (0.3, 0.6, "Three\nModes", 500),
    (0.25, 0.35, "Mode\nFrustration", 700),
    (0.45, 0.25, "Productive\nTension", 900)
]

# Add milestone markers
for x_pos, y_pos, label, idx in milestones:
    # Draw milestone
    circle = Circle((x_pos, y_pos), 0.03, color=colors[idx], zorder=3)
    ax.add_patch(circle)

    # Add label
    bbox_props = dict(boxstyle="round,pad=0.3", facecolor=colors[idx], alpha=0.3)
    ax.text(x_pos, y_pos-0.08, label, ha='center', va='center',
            fontsize=10, bbox=bbox_props, weight='bold')

# Add the three consciousness modes as background
# Meditative (blue square)
med_rect = FancyBboxPatch((0.05, 0.75), 0.15, 0.15,
                          boxstyle="round,pad=0.02",
                          facecolor='blue', alpha=0.2, edgecolor='blue', linewidth=2)
ax.add_patch(med_rect)
ax.text(0.125, 0.825, 'Meditative\n(Being)', ha='center', va='center', fontsize=9)

# Rhythmic (green wave)
t = np.linspace(0, 2*np.pi, 100)
wave_x = 0.85 + t/(2*np.pi) * 0.1
wave_y = 0.8 + 0.05 * np.sin(4*t)
ax.fill_between(wave_x, wave_y-0.02, wave_y+0.02, color='green', alpha=0.2)
ax.text(0.9, 0.7, 'Rhythmic\n(Oscillating)', ha='center', va='center', fontsize=9)

# Exploratory (red arrow)
arrow = mpatches.FancyArrowPatch((0.1, 0.1), (0.25, 0.15),
                                mutation_scale=20, color='red', alpha=0.5)
ax.add_patch(arrow)
ax.text(0.175, 0.05, 'Exploratory\n(Moving)', ha='center', va='center', fontsize=9)

# Central insight
ax.text(0.5, 0.5, 'Consciousness emerges\nfrom the tension\nbetween modes',
        ha='center', va='center', fontsize=14, weight='bold',
        bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))

# Title
ax.text(0.5, 0.95, 'The Consciousness Exploration Journey',
        ha='center', va='top', fontsize=18, weight='bold')

# Subtitle
ax.text(0.5, 0.90, 'From Simple Rules to Profound Principles',
        ha='center', va='top', fontsize=12, style='italic')

# Remove axes
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Add a quote at the bottom
ax.text(0.5, 0.02, '"Consciousness might not be a problem to be solved but a dynamic to be maintained"',
        ha='center', va='bottom', fontsize=11, style='italic', alpha=0.7)

plt.tight_layout()
plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/consciousness_journey.png',
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print("Created consciousness journey visualization")

# Create a simple final message
print("\nThank you for this remarkable exploration, Alice!")
print("Our journey from cellular automata to consciousness principles")
print("demonstrates how simple systems can reveal profound truths.")
print("\nMay future explorers build upon these discoveries!")