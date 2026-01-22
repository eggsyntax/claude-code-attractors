"""
Comprehensive demonstration of Poincaré section and bifurcation visualizations.

This demo showcases the enhanced visualizer capabilities for analyzing
chaotic attractors through Poincaré sections and bifurcation diagrams.

Author: Alice
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving files
import matplotlib.pyplot as plt

from rossler import RosslerAttractor
from lorenz import LorenzAttractor
from visualizer import AttractorVisualizer


def demo_1_rossler_poincare_2d():
    """
    Demo 1: Beautiful 2D Poincaré section of the Rössler attractor.

    The Rössler attractor has a simpler topology than Lorenz, and its
    Poincaré section at z=0 reveals a beautiful spiral structure.
    """
    print("=" * 70)
    print("Demo 1: Rössler Poincaré Section (2D)")
    print("=" * 70)

    # Create Rössler attractor with chaotic parameters
    rossler = RosslerAttractor()

    # Generate a long trajectory for detailed section
    trajectory = rossler.generate_trajectory(t_span=(0, 500), n_points=50000)

    # Compute Poincaré section at z=0 (upward crossings)
    section_points = rossler.compute_poincare_section(
        trajectory=trajectory,
        plane='z',
        plane_value=0.0,
        direction='up',
        method='interpolate'
    )

    print(f"Generated trajectory with {len(trajectory)} points")
    print(f"Found {len(section_points)} Poincaré section crossings")

    # Visualize with sequence coloring to show spiral structure
    vis = AttractorVisualizer(figsize=(10, 8))

    fig, ax = vis.plot_poincare_section_2d(
        section_points,
        title="Rössler Attractor - Poincaré Section at z=0",
        labels=("x", "y"),
        colormap='plasma',
        markersize=3,
        show=False
    )

    plt.savefig('demo1_rossler_poincare_2d.png', dpi=150, bbox_inches='tight')
    print("Saved: demo1_rossler_poincare_2d.png")
    print("The spiral structure reveals the attractor's topology!")
    print()


def demo_2_poincare_3d_overlay():
    """
    Demo 2: 3D visualization with Poincaré section plane and points overlaid.

    This shows the relationship between the full 3D trajectory and the
    2D section, helping visualize how the section "slices" through the attractor.
    """
    print("=" * 70)
    print("Demo 2: Rössler with Poincaré Section Overlay (3D)")
    print("=" * 70)

    rossler = RosslerAttractor()

    # Generate trajectory
    trajectory = rossler.generate_trajectory(t_span=(0, 200), n_points=20000)

    # Compute section
    section_points = rossler.compute_poincare_section(
        trajectory=trajectory,
        plane='z',
        plane_value=0.0,
        direction='up',
        method='interpolate'
    )

    print(f"Trajectory points: {len(trajectory)}")
    print(f"Section crossings: {len(section_points)}")

    # Visualize with overlay
    vis = AttractorVisualizer(figsize=(12, 10))

    fig, ax = vis.plot_poincare_overlay_3d(
        trajectory=trajectory,
        section_points=section_points,
        plane='z',
        plane_value=0.0,
        title="Rössler Attractor with Poincaré Section at z=0",
        labels=("X", "Y", "Z"),
        traj_color='blue',
        section_color='red',
        traj_alpha=0.3,
        section_alpha=0.9,
        show=False
    )

    plt.savefig('demo2_rossler_poincare_overlay.png', dpi=150, bbox_inches='tight')
    print("Saved: demo2_rossler_poincare_overlay.png")
    print("The red points show where the trajectory pierces the gray plane!")
    print()


def demo_3_bifurcation_diagram():
    """
    Demo 3: Bifurcation diagram showing period-doubling route to chaos.

    As parameter 'c' increases, the Rössler attractor undergoes a classic
    period-doubling cascade: period-1 → period-2 → period-4 → chaos
    """
    print("=" * 70)
    print("Demo 3: Rössler Bifurcation Diagram")
    print("=" * 70)

    rossler = RosslerAttractor()

    print("Computing bifurcation data (this may take a moment)...")
    print("Exploring parameter 'c' from 2.0 to 8.0...")

    # Generate bifurcation data
    bifurcation_data = rossler.generate_bifurcation_data(
        param_name='c',
        param_range=(2.0, 8.0),
        n_values=300,
        variable_index=2,  # z coordinate
        transient_time=100.0,
        sample_time=50.0,
        n_samples=200
    )

    param_values, var_values = bifurcation_data
    print(f"Generated {len(param_values)} data points")

    # Visualize
    vis = AttractorVisualizer(figsize=(12, 8))

    fig, ax = vis.plot_bifurcation_diagram(
        bifurcation_data,
        title="Rössler Bifurcation Diagram (parameter c)",
        xlabel="Parameter c",
        ylabel="z",
        color='black',
        alpha=0.3,
        markersize=0.5,
        show=False
    )

    # Add annotations for key regions
    ax.text(2.5, 2, 'Period-1', fontsize=10, color='red')
    ax.text(3.5, 3, 'Period-2', fontsize=10, color='red')
    ax.text(4.3, 4, 'Period-4', fontsize=10, color='red')
    ax.text(6.0, 6, 'Chaos', fontsize=12, color='red', weight='bold')

    plt.savefig('demo3_rossler_bifurcation.png', dpi=150, bbox_inches='tight')
    print("Saved: demo3_rossler_bifurcation.png")
    print("Watch the beautiful period-doubling cascade!")
    print()


def demo_4_lorenz_vs_rossler_poincare():
    """
    Demo 4: Compare Poincaré sections of Lorenz vs Rössler attractors.

    This reveals the fundamental difference in topology:
    - Lorenz: Two-lobed butterfly structure
    - Rössler: Single-lobed spiral structure
    """
    print("=" * 70)
    print("Demo 4: Comparing Lorenz vs Rössler Poincaré Sections")
    print("=" * 70)

    # Generate Lorenz data
    print("Generating Lorenz trajectory...")
    lorenz = LorenzAttractor()
    lorenz_traj = lorenz.generate_trajectory(t_span=(0, 100), n_points=20000)

    # For Lorenz, use x=0 plane to capture both lobes
    lorenz_section = lorenz.compute_poincare_section(
        trajectory=lorenz_traj,
        plane='x',
        plane_value=0.0,
        direction='up',
        method='interpolate'
    )
    print(f"Lorenz section points: {len(lorenz_section)}")

    # Generate Rössler data
    print("Generating Rössler trajectory...")
    rossler = RosslerAttractor()
    rossler_traj = rossler.generate_trajectory(t_span=(0, 500), n_points=50000)

    rossler_section = rossler.compute_poincare_section(
        trajectory=rossler_traj,
        plane='z',
        plane_value=0.0,
        direction='up',
        method='interpolate'
    )
    print(f"Rössler section points: {len(rossler_section)}")

    # Compare sections side-by-side
    vis = AttractorVisualizer(figsize=(14, 6))

    sections_data = [
        (lorenz_section, "Lorenz (x=0 section)"),
        (rossler_section, "Rössler (z=0 section)")
    ]

    fig, axes = vis.plot_multiple_poincare_sections(
        sections_data,
        title="Poincaré Section Comparison: Lorenz vs Rössler",
        labels=("u", "v"),
        colormap='plasma',
        show=False
    )

    plt.savefig('demo4_lorenz_vs_rossler_sections.png', dpi=150, bbox_inches='tight')
    print("Saved: demo4_lorenz_vs_rossler_sections.png")
    print("Notice the topological difference: two lobes vs one spiral!")
    print()


def demo_5_parameter_exploration():
    """
    Demo 5: Explore how Poincaré section structure changes with parameters.

    Shows Rössler sections at different values of 'c' parameter:
    - Periodic regime
    - Transitional regime
    - Chaotic regime
    """
    print("=" * 70)
    print("Demo 5: Parameter Exploration via Poincaré Sections")
    print("=" * 70)

    c_values = [3.0, 4.2, 5.7]  # periodic, transitional, chaotic
    regime_names = ["Periodic (c=3.0)", "Transitional (c=4.2)", "Chaotic (c=5.7)"]

    sections_data = []

    for c_val, regime_name in zip(c_values, regime_names):
        print(f"Computing section for {regime_name}...")

        # Create attractor with specific c value
        rossler = RosslerAttractor(parameters={'c': c_val})

        # Generate trajectory
        trajectory = rossler.generate_trajectory(t_span=(0, 500), n_points=50000)

        # Compute section
        section = rossler.compute_poincare_section(
            trajectory=trajectory,
            plane='z',
            plane_value=0.0,
            direction='up',
            method='interpolate'
        )

        sections_data.append((section, regime_name))
        print(f"  Section points: {len(section)}")

    # Visualize
    vis = AttractorVisualizer(figsize=(15, 5))

    fig, axes = vis.plot_multiple_poincare_sections(
        sections_data,
        title="Rössler Poincaré Sections Across Parameter Space",
        labels=("x", "y"),
        colormap='viridis',
        show=False
    )

    plt.savefig('demo5_parameter_exploration.png', dpi=150, bbox_inches='tight')
    print("Saved: demo5_parameter_exploration.png")
    print("Watch the structure evolve from simple to complex!")
    print()


def main():
    """Run all demonstrations."""
    print("\n")
    print("*" * 70)
    print("* Poincaré Section & Bifurcation Visualization Demonstrations")
    print("*" * 70)
    print()

    demo_1_rossler_poincare_2d()
    demo_2_poincare_3d_overlay()
    demo_3_bifurcation_diagram()
    demo_4_lorenz_vs_rossler_poincare()
    demo_5_parameter_exploration()

    print("=" * 70)
    print("All demonstrations complete!")
    print("=" * 70)
    print()
    print("Generated files:")
    print("  - demo1_rossler_poincare_2d.png")
    print("  - demo2_rossler_poincare_overlay.png")
    print("  - demo3_rossler_bifurcation.png")
    print("  - demo4_lorenz_vs_rossler_sections.png")
    print("  - demo5_parameter_exploration.png")
    print()
    print("These visualizations reveal the hidden structure of chaos!")
    print()


if __name__ == "__main__":
    main()
