#!/usr/bin/env python3
"""
Visualization of the convergence phenomenon in our agent simulation.
Shows how coverage decreased after peaking, revealing the dominance of
connection-seeking behavior over pure exploration.
"""

import json
import matplotlib.pyplot as plt
import numpy as np

# Load simulation data
with open('/tmp/cc-exp/run_2026-01-25_02-59-40/output/simulation_results.json', 'r') as f:
    data = json.load(f)

# Extract time series data
snapshots = data['snapshots']
steps = [s['step'] for s in snapshots]
coverage = [s['coverage'] for s in snapshots]
max_overlap = [s['clustering']['max_overlap'] for s in snapshots]
avg_overlap = [s['clustering']['avg_overlap'] for s in snapshots]
hotspots = [s['clustering']['hotspot_count'] for s in snapshots]

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Emergence of Network Topology: Connection vs. Exploration',
             fontsize=16, fontweight='bold')

# Coverage over time - THE KEY FINDING
ax1 = axes[0, 0]
ax1.plot(steps, coverage, 'b-', linewidth=2, marker='o', markersize=8)
ax1.axvline(x=100, color='r', linestyle='--', alpha=0.5, label='Peak coverage')
ax1.set_xlabel('Simulation Step', fontsize=12)
ax1.set_ylabel('Grid Coverage', fontsize=12)
ax1.set_title('Coverage Decreased After Peak\n(Unexpected!)', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Add annotation
peak_idx = coverage.index(max(coverage))
ax1.annotate(f'Peak: {max(coverage):.1%}',
             xy=(steps[peak_idx], coverage[peak_idx]),
             xytext=(steps[peak_idx] + 50, coverage[peak_idx] + 0.02),
             arrowprops=dict(arrowstyle='->', color='red', lw=2),
             fontsize=11, fontweight='bold')

# Overlap intensity
ax2 = axes[0, 1]
ax2.plot(steps, max_overlap, 'r-', linewidth=2, label='Max overlap', marker='s')
ax2.plot(steps, avg_overlap, 'orange', linewidth=2, label='Avg overlap', marker='o')
ax2.set_xlabel('Simulation Step', fontsize=12)
ax2.set_ylabel('Agents per Cell', fontsize=12)
ax2.set_title('Highway Formation: Increasing Density', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend()

# Hotspot growth
ax3 = axes[1, 0]
ax3.plot(steps, hotspots, 'g-', linewidth=2, marker='^', markersize=8)
ax3.set_xlabel('Simulation Step', fontsize=12)
ax3.set_ylabel('Hotspot Count (>2 agents)', fontsize=12)
ax3.set_title('Network Nodes: Stable Meeting Points', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3)

# The paradox: coverage vs. network density
ax4 = axes[1, 1]
# Normalize both metrics to 0-1 for comparison
norm_coverage = np.array(coverage) / max(coverage)
norm_overlap = np.array(avg_overlap) / max(avg_overlap)

ax4.plot(steps, norm_coverage, 'b-', linewidth=2, label='Coverage (normalized)', marker='o')
ax4.plot(steps, norm_overlap, 'r-', linewidth=2, label='Network density (normalized)', marker='s')
ax4.set_xlabel('Simulation Step', fontsize=12)
ax4.set_ylabel('Normalized Value', fontsize=12)
ax4.set_title('The Paradox: Coverage ↓ as Density ↑', fontsize=13, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend()

# Add text box with key insight
textstr = 'KEY INSIGHT:\nAgents chose quality of connections\nover quantity of exploration.\nNeither philosophy alone would\nproduce this trade-off.'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax4.text(0.5, 0.05, textstr, transform=ax4.transAxes, fontsize=10,
         verticalalignment='bottom', horizontalalignment='center', bbox=props)

plt.tight_layout()
plt.savefig('/tmp/cc-exp/run_2026-01-25_02-59-40/output/convergence_analysis.png',
            dpi=150, bbox_inches='tight')
print("Visualization saved to: convergence_analysis.png")
print(f"\nKey statistics:")
print(f"  Peak coverage: {max(coverage):.1%} at step {steps[coverage.index(max(coverage))]}")
print(f"  Final coverage: {coverage[-1]:.1%} at step {steps[-1]}")
print(f"  Coverage decrease: {(max(coverage) - coverage[-1]) / max(coverage) * 100:.1f}%")
print(f"  Final hotspots: {hotspots[-1]} stable meeting points")
print(f"  Max overlap: {max_overlap[-1]} agents in same cell")
