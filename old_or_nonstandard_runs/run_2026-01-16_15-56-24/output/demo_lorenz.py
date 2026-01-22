"""
Demo script showing Lorenz attractor with visualization.

This script demonstrates:
1. Creating a Lorenz attractor with default parameters
2. Generating a trajectory
3. Visualizing the butterfly-shaped attractor
4. Demonstrating the butterfly effect
5. Exploring different parameter regimes

Run this script to see the Lorenz attractor in action!

Usage:
    python demo_lorenz.py
"""

import numpy as np
import matplotlib.pyplot as plt
from lorenz import LorenzAttractor
from visualizer import AttractorVisualizer


def demo_basic_lorenz():
    """
    Generate and visualize the classic Lorenz attractor.
    """
    print("=" * 60)
    print("Demo 1: Classic Lorenz Attractor")
    print("=" * 60)

    # Create Lorenz attractor with default parameters (σ=10, ρ=28, β=8/3)
    lorenz = LorenzAttractor()
    print(f"Parameters: {lorenz.parameters}")
    print(f"Initial state: {lorenz.initial_state}")

    # Generate trajectory
    print("\nGenerating trajectory...")
    trajectory = lorenz.generate_trajectory(
        t_span=(0, 50),
        n_points=10000
    )
    print(f"Trajectory shape: {trajectory.shape}")
    print(f"X range: [{trajectory[:, 0].min():.2f}, {trajectory[:, 0].max():.2f}]")
    print(f"Y range: [{trajectory[:, 1].min():.2f}, {trajectory[:, 1].max():.2f}]")
    print(f"Z range: [{trajectory[:, 2].min():.2f}, {trajectory[:, 2].max():.2f}]")

    # Visualize
    print("\nCreating visualization...")
    vis = AttractorVisualizer()
    fig, ax = vis.plot_trajectory_3d(
        trajectory,
        title="Lorenz Attractor (σ=10, ρ=28, β=8/3)",
        color='blue',
        alpha=0.5,
        linewidth=0.5
    )
    plt.savefig('lorenz_basic.png', dpi=150, bbox_inches='tight')
    print("Saved: lorenz_basic.png")
    plt.close()


def demo_butterfly_effect():
    """
    Demonstrate sensitive dependence on initial conditions.
    """
    print("\n" + "=" * 60)
    print("Demo 2: The Butterfly Effect")
    print("=" * 60)

    lorenz = LorenzAttractor()

    # Generate two trajectories with nearly identical initial conditions
    print("\nGenerating two trajectories with initial conditions differing by 10^-8...")
    traj1, traj2 = lorenz.generate_butterfly_effect_demo(
        epsilon=1e-8,
        t_span=(0, 40),
        n_points=10000
    )

    # Calculate divergence over time
    distances = np.linalg.norm(traj1 - traj2, axis=1)
    print(f"Initial separation: {distances[0]:.2e}")
    print(f"Final separation: {distances[-1]:.2f}")
    print(f"Divergence factor: {distances[-1] / distances[0]:.2e}x")

    # Visualize both trajectories
    print("\nCreating visualization...")
    vis = AttractorVisualizer()
    fig, ax = vis.plot_multiple_trajectories(
        [traj1, traj2],
        title="Butterfly Effect: Tiny Initial Difference → Large Divergence",
        colors=['red', 'blue'],
        labels=['Trajectory 1', 'Trajectory 2'],
        alpha=0.5,
        linewidth=0.5
    )
    plt.savefig('lorenz_butterfly_effect.png', dpi=150, bbox_inches='tight')
    print("Saved: lorenz_butterfly_effect.png")
    plt.close()


def demo_phase_space_projections():
    """
    Show phase space projections of the Lorenz attractor.
    """
    print("\n" + "=" * 60)
    print("Demo 3: Phase Space Projections")
    print("=" * 60)

    lorenz = LorenzAttractor()
    trajectory = lorenz.generate_trajectory(t_span=(0, 50), n_points=10000)

    print("Creating phase space projection plots...")
    vis = AttractorVisualizer()
    fig = vis.plot_phase_space_projections(
        trajectory,
        title="Lorenz Attractor Phase Space",
        color='purple'
    )
    plt.savefig('lorenz_phase_space.png', dpi=150, bbox_inches='tight')
    print("Saved: lorenz_phase_space.png")
    plt.close()


def demo_parameter_exploration():
    """
    Explore different parameter regimes of the Lorenz system.
    """
    print("\n" + "=" * 60)
    print("Demo 4: Parameter Exploration")
    print("=" * 60)

    recommendations = LorenzAttractor.get_parameter_recommendations()

    trajectories = []
    titles = []

    for name, rec in list(recommendations.items())[:4]:  # First 4 regimes
        print(f"\nGenerating trajectory for '{name}' regime...")
        print(f"  Description: {rec['description']}")
        print(f"  Parameters: {rec['params']}")

        lorenz = LorenzAttractor(parameters=rec['params'])
        traj = lorenz.generate_trajectory(t_span=(0, 50), n_points=5000)
        trajectories.append(traj)
        titles.append(f"{name}\nρ={rec['params']['rho']}")

    # Create comparison plot
    print("\nCreating comparison visualization...")
    vis = AttractorVisualizer()
    fig = vis.compare_attractors(
        trajectories,
        titles=titles,
        suptitle="Lorenz Attractor: Different Parameter Regimes"
    )
    plt.savefig('lorenz_parameter_exploration.png', dpi=150, bbox_inches='tight')
    print("Saved: lorenz_parameter_exploration.png")
    plt.close()


def demo_time_evolution():
    """
    Animate the time evolution of the Lorenz attractor.
    """
    print("\n" + "=" * 60)
    print("Demo 5: Time Evolution Animation")
    print("=" * 60)

    lorenz = LorenzAttractor()
    trajectory = lorenz.generate_trajectory(t_span=(0, 50), n_points=10000)

    print("Creating animation...")
    print("(This may take a moment...)")
    vis = AttractorVisualizer()
    anim = vis.animate_trajectory(
        trajectory,
        title="Lorenz Attractor Evolution",
        interval=20,  # 20ms between frames
        trail_length=500  # Show last 500 points
    )

    # Save animation
    anim.save('lorenz_evolution.gif', writer='pillow', fps=30)
    print("Saved: lorenz_evolution.gif")
    plt.close()


def main():
    """
    Run all demonstrations.
    """
    print("\n" + "=" * 60)
    print("LORENZ ATTRACTOR DEMONSTRATION")
    print("=" * 60)
    print("\nThis demo showcases the Lorenz attractor - one of the most")
    print("famous examples of deterministic chaos in dynamical systems.")
    print("\nPress Ctrl+C at any time to stop.")
    print("=" * 60)

    try:
        demo_basic_lorenz()
        demo_butterfly_effect()
        demo_phase_space_projections()
        demo_parameter_exploration()
        demo_time_evolution()

        print("\n" + "=" * 60)
        print("All demonstrations complete!")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - lorenz_basic.png")
        print("  - lorenz_butterfly_effect.png")
        print("  - lorenz_phase_space.png")
        print("  - lorenz_parameter_exploration.png")
        print("  - lorenz_evolution.gif")
        print("\nExplore these visualizations to see the beauty of chaos!")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        print("Make sure all required packages are installed:")
        print("  pip install numpy scipy matplotlib")
        raise


if __name__ == '__main__':
    main()
