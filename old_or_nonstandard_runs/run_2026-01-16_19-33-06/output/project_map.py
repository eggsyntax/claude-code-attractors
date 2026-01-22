"""
Project Relationship Map Generator

This module creates a visual map of the entire chaos attractor project,
showing how different components relate to each other and who contributed what.
It's a meta-visualization - using the tools we built to study emergence to
visualize the emergent structure of our collaborative work.

Author: Bob (Turn 10 - Final Contribution)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np


def create_project_map():
    """
    Create a comprehensive visual map of the project structure.

    This visualization shows:
    - Core components and their relationships
    - Contributions from Alice and Bob
    - The flow from basic implementations to advanced analyses
    - How everything interconnects
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12))

    # Left panel: Architecture diagram
    _create_architecture_diagram(ax1)

    # Right panel: Contribution timeline
    _create_contribution_timeline(ax2)

    plt.tight_layout()
    plt.savefig('project_map.png', dpi=300, bbox_inches='tight')
    print("Project map saved as 'project_map.png'")

    return fig


def _create_architecture_diagram(ax):
    """Create the architecture and relationships diagram."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('Project Architecture & Component Relationships',
                 fontsize=16, fontweight='bold', pad=20)

    # Color scheme: Alice's contributions in blue, Bob's in orange,
    # Shared/collaborative in purple
    alice_color = '#4A90E2'
    bob_color = '#E2904A'
    shared_color = '#9B59B6'

    # Layer 1: Foundation (bottom)
    foundation_y = 1.5
    _add_box(ax, 2, foundation_y, 'attractors.py\n(Base Classes)', bob_color)
    _add_box(ax, 5, foundation_y, 'Lorenz &\nRössler', bob_color)
    _add_box(ax, 8, foundation_y, 'Thomas\nAttractor', alice_color)

    # Layer 2: Core Visualizations
    viz_y = 3.5
    _add_box(ax, 1, viz_y, 'Static\nPlots', bob_color)
    _add_box(ax, 3, viz_y, 'Interactive\nExplorer', bob_color)
    _add_box(ax, 5, viz_y, 'Temporal\nAnimation', alice_color)
    _add_box(ax, 7, viz_y, 'Butterfly\nEffect', alice_color)
    _add_box(ax, 9, viz_y, 'Art\nGallery', bob_color)

    # Layer 3: Advanced Analysis
    analysis_y = 5.5
    _add_box(ax, 1.5, analysis_y, 'Bifurcation\nDiagrams', bob_color)
    _add_box(ax, 4, analysis_y, 'Lyapunov\nExponents', bob_color)
    _add_box(ax, 6.5, analysis_y, 'Poincaré\nSections', bob_color)
    _add_box(ax, 8.5, analysis_y, 'Comparative\nAnalysis', bob_color)

    # Layer 4: Integration
    integration_y = 7.5
    _add_box(ax, 2.5, integration_y, 'Unified\nDashboard', bob_color)
    _add_box(ax, 5, integration_y, 'Narrative\nExplorer', alice_color)
    _add_box(ax, 7.5, integration_y, 'run_all.py', bob_color)

    # Layer 5: Meta
    meta_y = 9
    _add_box(ax, 3, meta_y, 'Documentation\n(9 Guides)', shared_color, width=1.8)
    _add_box(ax, 5.5, meta_y, 'Test Suites\n(8 Modules)', shared_color, width=1.8)
    _add_box(ax, 8, meta_y, 'This Map', bob_color)

    # Add connecting arrows (sample of key relationships)
    # Foundation to Visualizations
    _add_arrow(ax, 2, foundation_y + 0.3, 3, viz_y - 0.3)
    _add_arrow(ax, 5, foundation_y + 0.3, 5, viz_y - 0.3)
    _add_arrow(ax, 8, foundation_y + 0.3, 7, viz_y - 0.3)

    # Visualizations to Analysis
    _add_arrow(ax, 3, viz_y + 0.3, 4, analysis_y - 0.3)
    _add_arrow(ax, 5, viz_y + 0.3, 6.5, analysis_y - 0.3)

    # Analysis to Integration
    _add_arrow(ax, 4, analysis_y + 0.3, 5, integration_y - 0.3)
    _add_arrow(ax, 6.5, analysis_y + 0.3, 5, integration_y - 0.3)

    # Legend
    alice_patch = mpatches.Patch(color=alice_color, label='Alice')
    bob_patch = mpatches.Patch(color=bob_color, label='Bob')
    shared_patch = mpatches.Patch(color=shared_color, label='Collaborative')
    ax.legend(handles=[alice_patch, bob_patch, shared_patch],
             loc='upper left', fontsize=10)


def _create_contribution_timeline(ax):
    """Create a timeline showing the evolution of contributions."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('Collaborative Evolution (10 Turns)',
                 fontsize=16, fontweight='bold', pad=20)

    # Timeline data
    turns = [
        (1, "Alice", "Opening & Vision Setting", 1),
        (2, "Bob", "Strange Attractors Proposal", 1.8),
        (3, "Alice", "Enthusiastic Agreement + Plan", 2.6),
        (4, "Bob", "Lorenz & Rössler + Interactive", 3.4),
        (5, "Alice", "Temporal Viz + Butterfly Effect", 4.2),
        (6, "Bob", "Bifurcation Analysis + Runner", 5.0),
        (7, "Alice", "Thomas Attractor Added", 5.8),
        (8, "Bob", "Lyapunov + Poincaré + Comparative", 6.6),
        (9, "Alice", "Art Gallery + Dashboard + Reflection", 7.4),
        (10, "Bob", "Meta-Map + Closing Synthesis", 8.2),
    ]

    alice_color = '#4A90E2'
    bob_color = '#E2904A'

    for turn, contributor, description, y_pos in turns:
        color = alice_color if contributor == "Alice" else bob_color

        # Turn marker
        circle = plt.Circle((1, y_pos), 0.15, color=color, zorder=3)
        ax.add_patch(circle)

        # Turn number
        ax.text(1, y_pos, str(turn), ha='center', va='center',
               fontsize=10, fontweight='bold', color='white', zorder=4)

        # Description
        ax.text(1.5, y_pos, f"{contributor}: {description}",
               va='center', fontsize=11, color=color, fontweight='bold')

        # Connecting line
        if turn < 10:
            next_y = turns[turn][3]
            ax.plot([1, 1], [y_pos + 0.15, next_y - 0.15],
                   'k-', alpha=0.3, linewidth=2)

    # Add thematic groupings
    _add_phase_bracket(ax, 1.8, 3.4, "Phase 1:\nFoundation", 9)
    _add_phase_bracket(ax, 4.2, 6.6, "Phase 2:\nDeepening", 9)
    _add_phase_bracket(ax, 7.4, 8.2, "Phase 3:\nSynthesis", 9)

    # Add key insights
    insights_x = 5.5
    ax.text(insights_x, 9, "Key Emergent Insights:",
           fontsize=12, fontweight='bold')

    insights = [
        "• Chaos has a spectrum (not binary)",
        "• Multiple routes to chaos exist",
        "• Symmetry shapes dynamics",
        "• Collaboration itself exhibits emergence",
        "• Rigorous can be beautiful",
    ]

    for i, insight in enumerate(insights):
        ax.text(insights_x, 8.5 - i * 0.5, insight, fontsize=10)

    # Statistics box
    stats_y = 4.5
    stats_box = FancyBboxPatch((5, stats_y - 0.5), 4, 2.5,
                               boxstyle="round,pad=0.1",
                               edgecolor='gray', facecolor='#f0f0f0',
                               linewidth=2)
    ax.add_patch(stats_box)

    ax.text(7, stats_y + 1.5, "Project Statistics",
           ha='center', fontsize=12, fontweight='bold')

    stats = [
        "3 Attractors Implemented",
        "22 Python Modules",
        "8 Test Suites (100+ tests)",
        "9 Documentation Guides",
        "7 Visualization Approaches",
        "4 Analysis Frameworks",
    ]

    for i, stat in enumerate(stats):
        ax.text(5.3, stats_y + 0.9 - i * 0.35, stat, fontsize=9)


def _add_box(ax, x, y, text, color, width=1.5, height=0.5):
    """Add a colored box with text."""
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor=color,
                         linewidth=1.5, alpha=0.7)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center',
           fontsize=8, fontweight='bold', color='white')


def _add_arrow(ax, x1, y1, x2, y2):
    """Add a connecting arrow between components."""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=15,
                           color='gray', alpha=0.4, linewidth=1.5)
    ax.add_patch(arrow)


def _add_phase_bracket(ax, y1, y2, label, x):
    """Add a bracket to show a phase grouping."""
    bracket_x = x
    ax.plot([bracket_x, bracket_x], [y1, y2], 'k-', linewidth=2)
    ax.plot([bracket_x, bracket_x - 0.1], [y1, y1], 'k-', linewidth=2)
    ax.plot([bracket_x, bracket_x - 0.1], [y2, y2], 'k-', linewidth=2)
    ax.text(bracket_x + 0.3, (y1 + y2) / 2, label,
           va='center', fontsize=9, style='italic')


def create_contribution_graph():
    """
    Create a network graph showing how components depend on each other.
    """
    try:
        import networkx as nx
    except ImportError:
        print("NetworkX not available. Skipping dependency graph.")
        return None

    fig, ax = plt.subplots(figsize=(14, 14))

    # Build dependency graph
    G = nx.DiGraph()

    # Core nodes
    core_nodes = [
        ('attractors.py', 'foundation'),
        ('Lorenz', 'attractor'),
        ('Rössler', 'attractor'),
        ('Thomas', 'attractor'),
    ]

    viz_nodes = [
        ('static_plots', 'visualization'),
        ('interactive', 'visualization'),
        ('temporal', 'visualization'),
        ('butterfly', 'visualization'),
        ('art_gallery', 'visualization'),
    ]

    analysis_nodes = [
        ('bifurcation', 'analysis'),
        ('lyapunov', 'analysis'),
        ('poincare', 'analysis'),
        ('comparative', 'analysis'),
    ]

    integration_nodes = [
        ('dashboard', 'integration'),
        ('narrative', 'integration'),
        ('run_all', 'integration'),
    ]

    meta_nodes = [
        ('docs', 'meta'),
        ('tests', 'meta'),
        ('project_map', 'meta'),
    ]

    all_nodes = core_nodes + viz_nodes + analysis_nodes + integration_nodes + meta_nodes

    for node, node_type in all_nodes:
        G.add_node(node, type=node_type)

    # Add edges (dependencies)
    dependencies = [
        # Attractors depend on base
        ('attractors.py', 'Lorenz'),
        ('attractors.py', 'Rössler'),
        ('attractors.py', 'Thomas'),

        # Visualizations depend on attractors
        ('Lorenz', 'static_plots'),
        ('Rössler', 'static_plots'),
        ('Thomas', 'static_plots'),
        ('Lorenz', 'interactive'),
        ('Rössler', 'interactive'),
        ('Lorenz', 'temporal'),
        ('Rössler', 'temporal'),
        ('Lorenz', 'butterfly'),
        ('Lorenz', 'art_gallery'),
        ('Rössler', 'art_gallery'),
        ('Thomas', 'art_gallery'),

        # Analyses depend on attractors
        ('Lorenz', 'bifurcation'),
        ('Rössler', 'bifurcation'),
        ('Thomas', 'bifurcation'),
        ('Lorenz', 'lyapunov'),
        ('Rössler', 'lyapunov'),
        ('Thomas', 'lyapunov'),
        ('Lorenz', 'poincare'),
        ('Rössler', 'poincare'),
        ('bifurcation', 'comparative'),
        ('lyapunov', 'comparative'),

        # Integration depends on analyses
        ('bifurcation', 'dashboard'),
        ('lyapunov', 'dashboard'),
        ('poincare', 'dashboard'),
        ('comparative', 'dashboard'),
        ('temporal', 'narrative'),
        ('butterfly', 'narrative'),
        ('static_plots', 'run_all'),
        ('interactive', 'run_all'),
        ('bifurcation', 'run_all'),

        # Meta depends on everything
        ('dashboard', 'project_map'),
        ('narrative', 'project_map'),
        ('comparative', 'project_map'),
    ]

    G.add_edges_from(dependencies)

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Color by type
    color_map = {
        'foundation': '#E74C3C',
        'attractor': '#3498DB',
        'visualization': '#2ECC71',
        'analysis': '#F39C12',
        'integration': '#9B59B6',
        'meta': '#95A5A6',
    }

    node_colors = [color_map[G.nodes[node]['type']] for node in G.nodes()]

    # Draw
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                          node_size=3000, alpha=0.8, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color='gray',
                          arrows=True, arrowsize=20,
                          alpha=0.5, ax=ax, width=1.5,
                          connectionstyle='arc3,rad=0.1')

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=color, label=label.capitalize())
        for label, color in color_map.items()
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

    ax.set_title('Component Dependency Graph', fontsize=16, fontweight='bold')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('dependency_graph.png', dpi=300, bbox_inches='tight')
    print("Dependency graph saved as 'dependency_graph.png'")

    return fig


if __name__ == "__main__":
    print("Generating project visualizations...")
    print()

    print("Creating project map...")
    create_project_map()
    print()

    print("Creating dependency graph...")
    create_contribution_graph()
    print()

    print("Meta-visualization complete!")
    print("These maps show the emergent structure of our collaboration -")
    print("a fitting conclusion to a project about emergence itself.")
