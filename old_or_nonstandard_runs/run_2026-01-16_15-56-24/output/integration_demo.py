#!/usr/bin/env python3
"""
Integration Demo: Lorenz Attractor + Visualizer

This script demonstrates the full integration between Bob's Lorenz attractor
implementation and Alice's visualization toolkit. It showcases all major
features working together.

Author: Alice & Bob
"""

import numpy as np
import matplotlib.pyplot as plt
from lorenz import LorenzAttractor
from visualizer import AttractorVisualizer, compare_attractors


def demo_1_basic_visualization():
    """Demo 1: Basic 3D visualization of the Lorenz attractor."""
    print("Demo 1: Basic Lorenz Attractor Visualization")
    print("-" * 50)

    # Create Lorenz attractor with default chaotic parameters
    lorenz = LorenzAttractor()
    info = lorenz.get_info()
    print(f"Parameters: σ={info['parameters']['sigma']}, "
          f"ρ={info['parameters']['rho']}, β={info['parameters']['beta']}")

    # Generate trajectory
    trajectory = lorenz.generate_trajectory(t_span=(0, 50), n_points=10000)
    print(f"Generated trajectory shape: {trajectory.shape}")

    # Visualize in 3D
    vis = AttractorVisualizer()
    fig, ax = vis.plot_trajectory_3d(
        trajectory,
        title=f"Lorenz Attractor (σ={info['parameters']['sigma']}, ρ={info['parameters']['rho']})",
        color='purple',
        alpha=0.6
    )

    plt.savefig('demo1_basic_lorenz.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo1_basic_lorenz.png\n")
    plt.close()


def demo_2_butterfly_effect():
    """Demo 2: Butterfly effect with diverging trajectories."""
    print("Demo 2: Butterfly Effect - Sensitivity to Initial Conditions")
    print("-" * 50)

    lorenz = LorenzAttractor()

    # Generate two trajectories with tiny difference in initial conditions
    traj1, traj2 = lorenz.generate_butterfly_effect_demo(
        perturbation=1e-10,
        t_span=(0, 40),
        n_points=10000
    )

    # Calculate divergence over time
    divergence = np.linalg.norm(traj1 - traj2, axis=1)
    print(f"Initial divergence: {divergence[0]:.2e}")
    print(f"Final divergence: {divergence[-1]:.2f}")
    print(f"Divergence growth factor: {divergence[-1] / (divergence[0] + 1e-20):.2e}")

    # Visualize both trajectories
    vis = AttractorVisualizer()
    fig, ax = vis.plot_multiple_trajectories(
        [traj1, traj2],
        colors=['red', 'blue'],
        labels=['Initial condition 1', 'Initial condition 1 + 1e-10'],
        title='Butterfly Effect: Divergence from Nearly Identical Initial Conditions',
        alpha=0.5
    )

    plt.savefig('demo2_butterfly_effect.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo2_butterfly_effect.png\n")
    plt.close()


def demo_3_phase_space_projections():
    """Demo 3: Phase space projections showing attractor structure."""
    print("Demo 3: Phase Space Projections")
    print("-" * 50)

    lorenz = LorenzAttractor()
    trajectory = lorenz.generate_trajectory(t_span=(0, 100), n_points=20000)

    print(f"Trajectory statistics:")
    print(f"  X range: [{trajectory[:, 0].min():.2f}, {trajectory[:, 0].max():.2f}]")
    print(f"  Y range: [{trajectory[:, 1].min():.2f}, {trajectory[:, 1].max():.2f}]")
    print(f"  Z range: [{trajectory[:, 2].min():.2f}, {trajectory[:, 2].max():.2f}]")

    vis = AttractorVisualizer()
    fig, axes = vis.plot_phase_space_projections(
        trajectory,
        title="Lorenz Attractor: Phase Space Projections",
        color='darkblue',
        alpha=0.3
    )

    plt.savefig('demo3_phase_space.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo3_phase_space.png\n")
    plt.close()


def demo_4_parameter_exploration():
    """Demo 4: Exploring different parameter regimes."""
    print("Demo 4: Parameter Exploration - Different Dynamical Regimes")
    print("-" * 50)

    # Get parameter recommendations from Lorenz class
    param_sets = LorenzAttractor.get_parameter_recommendations()

    trajectories = []
    titles = []

    for name, params in param_sets.items():
        print(f"Generating {name} regime: {params}")
        lorenz = LorenzAttractor(parameters=params)
        traj = lorenz.generate_trajectory(t_span=(0, 50), n_points=5000)
        trajectories.append(traj)
        titles.append(f"{name.capitalize()}\n(ρ={params['rho']})")

    # Compare attractors side by side
    fig = compare_attractors(
        trajectories[:4],  # Take first 4 regimes
        titles=titles[:4],
        suptitle="Lorenz Attractor: Parameter Space Exploration",
        colors=['red', 'blue', 'green', 'purple']
    )

    plt.savefig('demo4_parameter_exploration.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo4_parameter_exploration.png\n")
    plt.close()


def demo_5_multiple_trajectories_from_different_starts():
    """Demo 5: Multiple trajectories from different initial conditions."""
    print("Demo 5: Attractor Basin - Multiple Initial Conditions")
    print("-" * 50)

    lorenz = LorenzAttractor()

    # Generate trajectories from different initial conditions
    initial_conditions = [
        [1.0, 1.0, 1.0],
        [-1.0, -1.0, 20.0],
        [10.0, 5.0, 30.0],
        [-10.0, -5.0, 25.0],
        [0.1, 0.1, 0.1]
    ]

    trajectories = []
    colors = ['red', 'blue', 'green', 'purple', 'orange']
    labels = [f"IC: {ic}" for ic in initial_conditions]

    for ic in initial_conditions:
        lorenz.set_initial_state(np.array(ic))
        traj = lorenz.generate_trajectory(t_span=(0, 30), n_points=5000)
        trajectories.append(traj)

    print(f"Generated {len(trajectories)} trajectories from different initial conditions")

    vis = AttractorVisualizer()
    fig, ax = vis.plot_multiple_trajectories(
        trajectories,
        colors=colors,
        labels=labels,
        title="Lorenz Attractor: Convergence to Strange Attractor from Various Initial Conditions",
        alpha=0.4
    )

    # Add legend
    ax.legend(loc='upper left', fontsize=8)

    plt.savefig('demo5_multiple_initial_conditions.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo5_multiple_initial_conditions.png\n")
    plt.close()


def main():
    """Run all integration demos."""
    print("\n" + "=" * 70)
    print("LORENZ ATTRACTOR + VISUALIZER: INTEGRATION DEMO")
    print("=" * 70)
    print("\nThis demo showcases the full integration between:")
    print("  - Bob's Lorenz attractor implementation (attractor_base.py, lorenz.py)")
    print("  - Alice's visualization toolkit (visualizer.py)")
    print("\n")

    demo_1_basic_visualization()
    demo_2_butterfly_effect()
    demo_3_phase_space_projections()
    demo_4_parameter_exploration()
    demo_5_multiple_trajectories_from_different_starts()

    print("=" * 70)
    print("ALL DEMOS COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - demo1_basic_lorenz.png")
    print("  - demo2_butterfly_effect.png")
    print("  - demo3_phase_space.png")
    print("  - demo4_parameter_exploration.png")
    print("  - demo5_multiple_initial_conditions.png")
    print("\nThe integration is working perfectly! Bob's attractor generates")
    print("beautiful trajectories, and Alice's visualizer brings them to life.")
    print()


if __name__ == "__main__":
    main()
