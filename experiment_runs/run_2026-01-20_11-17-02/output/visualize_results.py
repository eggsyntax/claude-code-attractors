"""
Visualization tool for emergence experiment results.

Creates visual summaries of how different rule combinations affect emergence metrics.
Run this after measure_emergence.py to visualize the results.

Usage:
    python visualize_results.py
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def load_results(filename: str = "emergence_results.json"):
    """Load experimental results from JSON file."""
    input_path = Path("/tmp/cc-exp/run_2026-01-20_11-17-02/output") / filename

    with open(input_path, 'r') as f:
        data = json.load(f)

    return data


def create_heatmap(results):
    """
    Create a heatmap showing interestingness scores for different rule combinations.
    """
    # Extract data
    n_results = len(results)
    rule_names = ['movement', 'cohesion', 'separation', 'resources']

    # Create matrix where rows are configurations, columns are rules + metrics
    config_matrix = np.zeros((n_results, 4))
    scores = np.zeros(n_results)

    for i, result in enumerate(results):
        for j, rule in enumerate(rule_names):
            config_matrix[i, j] = 1 if result['rules_enabled'][rule] else 0
        scores[i] = result['interestingness_score']

    # Sort by score
    sort_idx = np.argsort(scores)[::-1]
    config_matrix = config_matrix[sort_idx]
    scores = scores[sort_idx]

    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8), gridspec_kw={'width_ratios': [4, 1]})

    # Heatmap of rule configurations
    im1 = ax1.imshow(config_matrix, aspect='auto', cmap='RdYlGn', alpha=0.7)
    ax1.set_xticks(range(4))
    ax1.set_xticklabels([r[:3].upper() for r in rule_names], rotation=0)
    ax1.set_yticks(range(n_results))
    ax1.set_yticklabels([f"{i+1}" for i in range(n_results)], fontsize=8)
    ax1.set_xlabel('Rules (Green = Active, Red = Inactive)', fontsize=11)
    ax1.set_ylabel('Configuration Rank', fontsize=11)
    ax1.set_title('Rule Combinations by Interestingness', fontsize=13, fontweight='bold')

    # Add grid
    ax1.set_xticks(np.arange(4) - 0.5, minor=True)
    ax1.set_yticks(np.arange(n_results) - 0.5, minor=True)
    ax1.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)

    # Bar chart of interestingness scores
    colors = plt.cm.viridis(scores / scores.max())
    ax2.barh(range(n_results), scores, color=colors)
    ax2.set_yticks(range(n_results))
    ax2.set_yticklabels([])
    ax2.set_xlabel('Interest Score', fontsize=11)
    ax2.set_title('Scores', fontsize=13, fontweight='bold')
    ax2.invert_yaxis()

    plt.tight_layout()
    return fig


def create_metric_comparison(results):
    """
    Create scatter plots comparing different metrics across configurations.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # Extract metrics
    n_rules = [r['n_rules_active'] for r in results]
    entropy = [r['spatial_entropy'] for r in results]
    clustering = [r['clustering_coefficient'] for r in results]
    velocity_var = [r['velocity_variance'] for r in results]
    change_rate = [r['position_change_rate'] for r in results]
    scores = [r['interestingness_score'] for r in results]

    # Color by number of active rules
    colors = plt.cm.plasma(np.array(n_rules) / 4.0)

    # Plot 1: Entropy vs Interestingness
    axes[0, 0].scatter(entropy, scores, c=colors, s=100, alpha=0.7, edgecolors='black')
    axes[0, 0].set_xlabel('Spatial Entropy', fontsize=11)
    axes[0, 0].set_ylabel('Interestingness Score', fontsize=11)
    axes[0, 0].set_title('Entropy vs Interestingness', fontsize=12, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: Velocity Variance vs Interestingness
    axes[0, 1].scatter(velocity_var, scores, c=colors, s=100, alpha=0.7, edgecolors='black')
    axes[0, 1].set_xlabel('Velocity Variance', fontsize=11)
    axes[0, 1].set_ylabel('Interestingness Score', fontsize=11)
    axes[0, 1].set_title('Velocity Variance vs Interestingness', fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)

    # Plot 3: Position Change Rate vs Interestingness
    axes[1, 0].scatter(change_rate, scores, c=colors, s=100, alpha=0.7, edgecolors='black')
    axes[1, 0].set_xlabel('Position Change Rate', fontsize=11)
    axes[1, 0].set_ylabel('Interestingness Score', fontsize=11)
    axes[1, 0].set_title('Dynamics vs Interestingness', fontsize=12, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)

    # Plot 4: Number of Rules vs Interestingness
    axes[1, 1].scatter(n_rules, scores, c=colors, s=100, alpha=0.7, edgecolors='black')
    axes[1, 1].set_xlabel('Number of Active Rules', fontsize=11)
    axes[1, 1].set_ylabel('Interestingness Score', fontsize=11)
    axes[1, 1].set_title('Complexity vs Interestingness', fontsize=12, fontweight='bold')
    axes[1, 1].set_xticks([0, 1, 2, 3, 4])
    axes[1, 1].grid(True, alpha=0.3)

    # Add colorbar legend
    sm = plt.cm.ScalarMappable(cmap=plt.cm.plasma, norm=plt.Normalize(vmin=0, vmax=4))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes.ravel().tolist(), label='Number of Active Rules',
                       orientation='horizontal', pad=0.05, aspect=30)

    plt.tight_layout()
    return fig


def create_rule_impact_chart(results):
    """
    Create bar chart showing the impact of each rule on interestingness.
    """
    rule_names = ['movement', 'cohesion', 'separation', 'resources']
    impacts = []

    for rule_name in rule_names:
        with_rule = [r for r in results if r['rules_enabled'][rule_name]]
        without_rule = [r for r in results if not r['rules_enabled'][rule_name]]

        avg_with = np.mean([r['interestingness_score'] for r in with_rule]) if with_rule else 0
        avg_without = np.mean([r['interestingness_score'] for r in without_rule]) if without_rule else 0

        impact = avg_with - avg_without
        impacts.append(impact)

    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['green' if i > 0 else 'red' for i in impacts]
    bars = ax.bar(rule_names, impacts, color=colors, alpha=0.7, edgecolor='black', linewidth=2)

    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_ylabel('Impact on Interestingness Score', fontsize=12)
    ax.set_xlabel('Rule', fontsize=12)
    ax.set_title('Individual Rule Impact Analysis', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar, impact in zip(bars, impacts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{impact:+.3f}',
                ha='center', va='bottom' if height > 0 else 'top',
                fontsize=11, fontweight='bold')

    plt.tight_layout()
    return fig


def main():
    """Generate all visualizations."""
    print("Loading results from emergence_results.json...")
    results = load_results()

    print(f"Found {len(results)} experimental configurations.")
    print("\nGenerating visualizations...")

    # Create output directory for figures
    output_dir = Path("/tmp/cc-exp/run_2026-01-20_11-17-02/output")

    # Generate and save heatmap
    print("  1. Creating rule configuration heatmap...")
    fig1 = create_heatmap(results)
    fig1.savefig(output_dir / "emergence_heatmap.png", dpi=150, bbox_inches='tight')
    plt.close(fig1)

    # Generate and save metric comparisons
    print("  2. Creating metric comparison plots...")
    fig2 = create_metric_comparison(results)
    fig2.savefig(output_dir / "emergence_metrics.png", dpi=150, bbox_inches='tight')
    plt.close(fig2)

    # Generate and save rule impact chart
    print("  3. Creating rule impact analysis...")
    fig3 = create_rule_impact_chart(results)
    fig3.savefig(output_dir / "rule_impacts.png", dpi=150, bbox_inches='tight')
    plt.close(fig3)

    print("\n✓ Visualizations saved to output directory:")
    print("  - emergence_heatmap.png")
    print("  - emergence_metrics.png")
    print("  - rule_impacts.png")
    print("\nAnalysis complete!")


if __name__ == '__main__':
    main()
