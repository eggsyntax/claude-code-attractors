"""
Comprehensive demonstration of the Rössler attractor.

This script showcases all features of the Rössler implementation including:
- Basic 3D visualization
- Poincaré sections for analyzing structure
- Return maps showing chaotic dynamics
- Parameter exploration across different regimes
- Comparison with Lorenz attractor
- Bifurcation diagram preview (data generation)
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from rossler import RosslerAttractor
from lorenz import LorenzAttractor
from visualizer import AttractorVisualizer


def demo_basic_rossler():
    """Demo 1: Basic Rössler attractor visualization."""
    print("Demo 1: Basic Rössler Attractor")
    print("-" * 50)

    rossler = RosslerAttractor()
    trajectory = rossler.generate_trajectory(t_span=(0, 100), n_points=10000)

    print(f"Parameters: {rossler.parameters}")
    print(f"Trajectory shape: {trajectory.shape}")
    print(f"Bounds: X[{trajectory[:,0].min():.1f}, {trajectory[:,0].max():.1f}], "
          f"Y[{trajectory[:,1].min():.1f}, {trajectory[:,1].max():.1f}], "
          f"Z[{trajectory[:,2].min():.1f}, {trajectory[:,2].max():.1f}]")

    # Visualize
    vis = AttractorVisualizer()
    info = rossler.get_info()
    title = f"{info['type']} Attractor (a={info['parameters']['a']}, " \
            f"b={info['parameters']['b']}, c={info['parameters']['c']})"

    fig, ax = vis.plot_trajectory_3d(trajectory, title=title, color='purple', alpha=0.6)
    plt.savefig('demo1_rossler_basic.png', dpi=150, bbox_inches='tight')
    print("Saved: demo1_rossler_basic.png\n")


def demo_poincare_section():
    """Demo 2: Poincaré section analysis."""
    print("Demo 2: Poincaré Section")
    print("-" * 50)

    rossler = RosslerAttractor()
    trajectory = rossler.generate_trajectory(t_span=(0, 200), n_points=20000)

    # Compute Poincaré section for z=0 plane
    section = rossler.compute_poincare_section(
        trajectory,
        plane='z',
        value=0.0,
        direction='up'  # Only upward crossings
    )

    print(f"Generated {len(trajectory)} trajectory points")
    print(f"Found {len(section)} Poincaré section points (z=0, upward crossings)")

    # Create visualization
    fig = plt.figure(figsize=(14, 5))

    # Left: 3D trajectory with plane
    ax1 = fig.add_subplot(131, projection='3d')
    ax1.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
             'purple', linewidth=0.5, alpha=0.6)

    # Draw the z=0 plane
    xx, yy = np.meshgrid(
        np.linspace(trajectory[:, 0].min(), trajectory[:, 0].max(), 10),
        np.linspace(trajectory[:, 1].min(), trajectory[:, 1].max(), 10)
    )
    zz = np.zeros_like(xx)
    ax1.plot_surface(xx, yy, zz, alpha=0.2, color='gray')

    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    ax1.set_title('3D Trajectory\n(with z=0 plane)')

    # Middle: Poincaré section
    ax2 = fig.add_subplot(132)
    ax2.scatter(section[:, 0], section[:, 1], s=1, c='purple', alpha=0.5)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_title(f'Poincaré Section\n(z=0 plane, n={len(section)})')
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)

    # Right: Return map
    ax3 = fig.add_subplot(133)
    if len(section) > 1:
        x_current = section[:-1, 0]
        x_next = section[1:, 0]
        ax3.scatter(x_current, x_next, s=1, c='purple', alpha=0.5)
        ax3.plot([x_current.min(), x_current.max()],
                 [x_current.min(), x_current.max()],
                 'k--', alpha=0.3, label='y=x')
        ax3.set_xlabel('X_n')
        ax3.set_ylabel('X_n+1')
        ax3.set_title('Return Map\n(First-return map on x)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('demo2_poincare_section.png', dpi=150, bbox_inches='tight')
    print("Saved: demo2_poincare_section.png\n")


def demo_parameter_regimes():
    """Demo 3: Explore different parameter regimes."""
    print("Demo 3: Parameter Regimes")
    print("-" * 50)

    recommendations = RosslerAttractor.get_parameter_recommendations()
    regimes = ['periodic', 'period_2', 'chaotic', 'highly_chaotic']

    fig = plt.figure(figsize=(16, 10))

    for idx, regime_name in enumerate(regimes):
        params = recommendations[regime_name]
        print(f"{regime_name}: c={params['c']}")

        rossler = RosslerAttractor(parameters=params)
        trajectory = rossler.generate_trajectory(t_span=(0, 100), n_points=10000)

        # 3D view
        ax = fig.add_subplot(2, 4, idx + 1, projection='3d')
        ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
                linewidth=0.5, alpha=0.7)
        ax.set_title(f'{regime_name}\nc={params["c"]}')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Time series of z coordinate
        ax2 = fig.add_subplot(2, 4, idx + 5)
        time = np.linspace(0, 100, len(trajectory))
        ax2.plot(time, trajectory[:, 2], linewidth=0.5)
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Z')
        ax2.set_title(f'Z(t) - {regime_name}')
        ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('demo3_parameter_regimes.png', dpi=150, bbox_inches='tight')
    print("Saved: demo3_parameter_regimes.png\n")


def demo_butterfly_effect():
    """Demo 4: Demonstrate sensitivity to initial conditions."""
    print("Demo 4: Butterfly Effect")
    print("-" * 50)

    # Two very close initial conditions
    state1 = np.array([1.0, 1.0, 1.0])
    state2 = np.array([1.0, 1.0, 1.0001])  # Tiny difference in z

    rossler1 = RosslerAttractor(initial_state=state1)
    rossler2 = RosslerAttractor(initial_state=state2)

    traj1 = rossler1.generate_trajectory(t_span=(0, 50), n_points=5000)
    traj2 = rossler2.generate_trajectory(t_span=(0, 50), n_points=5000)

    # Calculate divergence
    distances = np.linalg.norm(traj1 - traj2, axis=1)
    time = np.linspace(0, 50, len(distances))

    print(f"Initial separation: {distances[0]:.6f}")
    print(f"Final separation: {distances[-1]:.4f}")
    print(f"Divergence factor: {distances[-1]/distances[0]:.1f}x")

    # Visualize
    vis = AttractorVisualizer()

    fig = plt.figure(figsize=(14, 5))

    # Left: Both trajectories
    ax1 = fig.add_subplot(131, projection='3d')
    ax1.plot(traj1[:, 0], traj1[:, 1], traj1[:, 2],
             'r', linewidth=0.5, alpha=0.7, label='IC 1')
    ax1.plot(traj2[:, 0], traj2[:, 1], traj2[:, 2],
             'b', linewidth=0.5, alpha=0.7, label='IC 2')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    ax1.set_title('Two Nearby Trajectories')
    ax1.legend()

    # Middle: Divergence over time
    ax2 = fig.add_subplot(132)
    ax2.plot(time, distances, 'purple', linewidth=1)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Distance')
    ax2.set_title('Trajectory Divergence')
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')

    # Right: X coordinate comparison
    ax3 = fig.add_subplot(133)
    ax3.plot(time, traj1[:, 0], 'r', linewidth=0.8, alpha=0.7, label='IC 1')
    ax3.plot(time, traj2[:, 0], 'b', linewidth=0.8, alpha=0.7, label='IC 2')
    ax3.set_xlabel('Time')
    ax3.set_ylabel('X')
    ax3.set_title('X Coordinate Over Time')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('demo4_butterfly_effect.png', dpi=150, bbox_inches='tight')
    print("Saved: demo4_butterfly_effect.png\n")


def demo_lorenz_vs_rossler():
    """Demo 5: Compare Lorenz and Rössler attractors."""
    print("Demo 5: Lorenz vs Rössler Comparison")
    print("-" * 50)

    # Generate both attractors
    lorenz = LorenzAttractor()
    rossler = RosslerAttractor()

    traj_lorenz = lorenz.generate_trajectory(t_span=(0, 50), n_points=10000)
    traj_rossler = rossler.generate_trajectory(t_span=(0, 100), n_points=10000)

    print("Lorenz: double-lobed butterfly structure")
    print("Rössler: single-lobed ribbon structure")

    # Use visualizer's comparison function
    vis = AttractorVisualizer()

    fig = vis.compare_attractors(
        [traj_lorenz, traj_rossler],
        ['Lorenz Attractor', 'Rössler Attractor'],
        ['blue', 'purple']
    )

    plt.savefig('demo5_lorenz_vs_rossler.png', dpi=150, bbox_inches='tight')
    print("Saved: demo5_lorenz_vs_rossler.png\n")


def demo_bifurcation_preview():
    """Demo 6: Generate bifurcation diagram data."""
    print("Demo 6: Bifurcation Diagram Data")
    print("-" * 50)
    print("Generating bifurcation data (this may take a moment)...")

    rossler = RosslerAttractor()

    # Generate bifurcation data for parameter c
    params, samples = rossler.generate_bifurcation_data(
        parameter='c',
        param_range=(2.0, 6.5),
        n_params=100,
        transient_time=50.0,
        sample_time=50.0,
        n_points=2000
    )

    print(f"Generated data for {len(params)} parameter values")
    print(f"Parameter range: c ∈ [{params.min():.1f}, {params.max():.1f}]")

    # Create bifurcation diagram
    fig, ax = plt.subplots(figsize=(12, 6))

    # For each parameter value, plot sampled z values
    for i, param_val in enumerate(params):
        sample_data = samples[i]
        z_values = sample_data[:, 2]  # z coordinate

        # Plot every few points to avoid overcrowding
        step = max(1, len(z_values) // 50)
        ax.plot([param_val] * len(z_values[::step]), z_values[::step],
                'k.', markersize=0.5, alpha=0.5)

    ax.set_xlabel('Parameter c', fontsize=12)
    ax.set_ylabel('Z (sampled values)', fontsize=12)
    ax.set_title('Bifurcation Diagram: Period-Doubling Route to Chaos', fontsize=14)
    ax.grid(True, alpha=0.3)

    # Add annotations
    ax.axvline(x=2.0, color='green', linestyle='--', alpha=0.5, linewidth=1)
    ax.text(2.1, ax.get_ylim()[1] * 0.95, 'Periodic', fontsize=9, color='green')

    ax.axvline(x=3.5, color='orange', linestyle='--', alpha=0.5, linewidth=1)
    ax.text(3.6, ax.get_ylim()[1] * 0.95, 'Period-2', fontsize=9, color='orange')

    ax.axvline(x=5.7, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax.text(5.8, ax.get_ylim()[1] * 0.95, 'Chaotic', fontsize=9, color='red')

    plt.tight_layout()
    plt.savefig('demo6_bifurcation.png', dpi=150, bbox_inches='tight')
    print("Saved: demo6_bifurcation.png\n")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 50)
    print("RÖSSLER ATTRACTOR DEMONSTRATION")
    print("=" * 50 + "\n")

    demos = [
        demo_basic_rossler,
        demo_poincare_section,
        demo_parameter_regimes,
        demo_butterfly_effect,
        demo_lorenz_vs_rossler,
        demo_bifurcation_preview
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"Error in {demo.__name__}: {e}\n")

    print("=" * 50)
    print("All demonstrations complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()
