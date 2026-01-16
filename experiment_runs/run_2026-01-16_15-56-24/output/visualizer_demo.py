"""
Demo script for the AttractorVisualizer.

This demonstrates how to use the visualizer with sample data before
we have actual attractor implementations.

Usage:
    python visualizer_demo.py
"""

import numpy as np
from visualizer import AttractorVisualizer, compare_attractors


def generate_spiral_trajectory(n_points=1000):
    """
    Generate a simple 3D spiral for demonstration.

    This is just placeholder data - real attractors will be much more interesting!
    """
    t = np.linspace(0, 4*np.pi, n_points)
    trajectory = np.column_stack([
        np.cos(t) * np.exp(-t/10),
        np.sin(t) * np.exp(-t/10),
        t / 5
    ])
    return trajectory


def generate_perturbed_trajectories(base_trajectory, n_trajectories=5, perturbation=0.01):
    """
    Generate multiple trajectories with slight perturbations to initial conditions.

    This demonstrates sensitivity to initial conditions.
    """
    trajectories = [base_trajectory]

    for i in range(1, n_trajectories):
        # Add small random perturbation
        perturbation_vector = np.random.randn(3) * perturbation
        perturbed = base_trajectory + perturbation_vector
        trajectories.append(perturbed)

    return trajectories


def demo_single_trajectory():
    """Demo 1: Plot a single 3D trajectory."""
    print("Demo 1: Single 3D trajectory")
    print("-" * 40)

    trajectory = generate_spiral_trajectory()
    visualizer = AttractorVisualizer()

    visualizer.plot_trajectory_3d(
        trajectory,
        title="Simple Spiral Trajectory",
        color='blue',
        alpha=0.7
    )
    print("Displaying single trajectory plot...\n")


def demo_multiple_trajectories():
    """Demo 2: Plot multiple trajectories to show divergence."""
    print("Demo 2: Multiple trajectories (sensitivity to initial conditions)")
    print("-" * 40)

    base_trajectory = generate_spiral_trajectory()
    trajectories = generate_perturbed_trajectories(base_trajectory, n_trajectories=5)

    visualizer = AttractorVisualizer()
    visualizer.plot_multiple_trajectories(
        trajectories,
        title="Sensitivity to Initial Conditions",
        alpha=0.5
    )
    print("Displaying multiple trajectories...\n")


def demo_phase_projections():
    """Demo 3: Plot phase space projections."""
    print("Demo 3: Phase space projections")
    print("-" * 40)

    trajectory = generate_spiral_trajectory()
    visualizer = AttractorVisualizer()

    visualizer.plot_phase_projections(
        trajectory,
        title="Phase Space Projections",
        color='red'
    )
    print("Displaying phase space projections...\n")


def demo_comparison():
    """Demo 4: Compare multiple different attractors."""
    print("Demo 4: Attractor comparison")
    print("-" * 40)

    # Generate three different "attractors" (just variations for demo)
    traj1 = generate_spiral_trajectory(500)
    traj2 = generate_spiral_trajectory(500) * 1.5  # Scaled version
    traj3 = generate_spiral_trajectory(500) @ np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])  # Flipped

    attractors_data = [
        (traj1, "Spiral A"),
        (traj2, "Spiral B (scaled)"),
        (traj3, "Spiral C (flipped)")
    ]

    fig, axes = compare_attractors(attractors_data)
    print("Displaying attractor comparison...\n")


def demo_animation():
    """Demo 5: Create an animated trajectory."""
    print("Demo 5: Animated trajectory")
    print("-" * 40)

    trajectory = generate_spiral_trajectory(1000)
    visualizer = AttractorVisualizer()

    print("Creating animation...")
    anim = visualizer.create_animation(
        trajectory,
        title="Growing Spiral",
        frames=100,
        interval=50
    )
    print("Animation created (displaying...)\n")


if __name__ == "__main__":
    print("=" * 60)
    print("AttractorVisualizer Demo")
    print("=" * 60)
    print()
    print("This demo shows the visualizer's capabilities using")
    print("simple spiral trajectories. Once Bob implements the actual")
    print("attractor systems (Lorenz, Rössler, Aizawa), we'll see")
    print("much more interesting chaotic behavior!")
    print()
    print("=" * 60)
    print()

    # Run all demos
    # Note: Uncomment the demos you want to run
    # (They open matplotlib windows sequentially)

    # demo_single_trajectory()
    # demo_multiple_trajectories()
    # demo_phase_projections()
    # demo_comparison()
    # demo_animation()

    print()
    print("=" * 60)
    print("Demo complete!")
    print()
    print("To run individual demos, uncomment the function calls")
    print("at the bottom of this script.")
    print("=" * 60)
