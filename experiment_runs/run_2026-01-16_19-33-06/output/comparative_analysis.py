"""
Comparative analysis of Lorenz, Rössler, and Thomas attractors.

This module creates visualizations that highlight the similarities and differences
between our three chaotic systems, showing their distinct personalities while
revealing common underlying principles.

Author: Bob
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from typing import Tuple, Callable
import matplotlib.patches as mpatches


# System definitions
def lorenz(t: float, state: np.ndarray, sigma=10, rho=28, beta=8/3) -> np.ndarray:
    """Lorenz system: weather model with butterfly structure."""
    x, y, z = state
    return np.array([
        sigma * (y - x),
        x * (rho - z) - y,
        x * y - beta * z
    ])


def rossler(t: float, state: np.ndarray, a=0.2, b=0.2, c=5.7) -> np.ndarray:
    """Rössler system: chemical reaction with spiral structure."""
    x, y, z = state
    return np.array([
        -y - z,
        x + a * y,
        b + z * (x - c)
    ])


def thomas(t: float, state: np.ndarray, b=0.18) -> np.ndarray:
    """Thomas system: cyclically symmetric with circular loops."""
    x, y, z = state
    return np.array([
        np.sin(y) - b * x,
        np.sin(z) - b * y,
        np.sin(x) - b * z
    ])


def simulate_attractor(system: Callable, x0: np.ndarray,
                       t_max: float = 100, dt: float = 0.01,
                       **params) -> np.ndarray:
    """
    Simulate an attractor system.

    Args:
        system: Differential equation function
        x0: Initial condition
        t_max: Simulation time
        dt: Time step for output
        **params: System parameters

    Returns:
        Trajectory array of shape (3, n_points)
    """
    t_span = (0, t_max)
    t_eval = np.arange(0, t_max, dt)

    sol = solve_ivp(system, t_span, x0, t_eval=t_eval,
                   args=tuple(params.values()), method='RK45',
                   rtol=1e-9, atol=1e-12)

    return sol.y


def create_gallery(output_file: str = 'attractor_gallery.png') -> None:
    """
    Create a beautiful gallery showing all three attractors side by side.

    Uses consistent viewing angles and color schemes to facilitate comparison.
    """
    fig = plt.figure(figsize=(18, 6))
    gs = GridSpec(1, 3, figure=fig)

    # Common visualization parameters
    elevation, azimuth = 20, 45
    n_points = 10000

    # Lorenz
    print("Simulating Lorenz attractor...")
    lorenz_traj = simulate_attractor(lorenz, np.array([1, 1, 1]),
                                     t_max=100, sigma=10, rho=28, beta=8/3)

    ax1 = fig.add_subplot(gs[0, 0], projection='3d')
    time_colors = np.linspace(0, 1, lorenz_traj.shape[1])
    ax1.plot(lorenz_traj[0], lorenz_traj[1], lorenz_traj[2],
            c=time_colors, cmap='plasma', linewidth=0.5, alpha=0.7)
    ax1.set_title('Lorenz Attractor\n"The Butterfly"', fontsize=14, weight='bold', pad=15)
    ax1.set_xlabel('X', fontsize=10)
    ax1.set_ylabel('Y', fontsize=10)
    ax1.set_zlabel('Z', fontsize=10)
    ax1.view_init(elev=elevation, azim=azimuth)
    ax1.grid(True, alpha=0.3)

    # Rössler
    print("Simulating Rössler attractor...")
    rossler_traj = simulate_attractor(rossler, np.array([1, 1, 1]),
                                      t_max=200, a=0.2, b=0.2, c=5.7)

    ax2 = fig.add_subplot(gs[0, 1], projection='3d')
    time_colors = np.linspace(0, 1, rossler_traj.shape[1])
    ax2.plot(rossler_traj[0], rossler_traj[1], rossler_traj[2],
            c=time_colors, cmap='viridis', linewidth=0.5, alpha=0.7)
    ax2.set_title('Rössler Attractor\n"The Spiral"', fontsize=14, weight='bold', pad=15)
    ax2.set_xlabel('X', fontsize=10)
    ax2.set_ylabel('Y', fontsize=10)
    ax2.set_zlabel('Z', fontsize=10)
    ax2.view_init(elev=elevation, azim=azimuth)
    ax2.grid(True, alpha=0.3)

    # Thomas
    print("Simulating Thomas attractor...")
    thomas_traj = simulate_attractor(thomas, np.array([0.1, 0, 0]),
                                     t_max=500, b=0.18)

    ax3 = fig.add_subplot(gs[0, 2], projection='3d')
    time_colors = np.linspace(0, 1, thomas_traj.shape[1])
    ax3.plot(thomas_traj[0], thomas_traj[1], thomas_traj[2],
            c=time_colors, cmap='cool', linewidth=0.5, alpha=0.7)
    ax3.set_title('Thomas Attractor\n"The Loops"', fontsize=14, weight='bold', pad=15)
    ax3.set_xlabel('X', fontsize=10)
    ax3.set_ylabel('Y', fontsize=10)
    ax3.set_zlabel('Z', fontsize=10)
    ax3.view_init(elev=elevation, azim=azimuth)
    ax3.grid(True, alpha=0.3)

    plt.suptitle('A Gallery of Strange Attractors', fontsize=18, weight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved gallery to {output_file}")
    plt.close()


def create_characteristics_table(output_file: str = 'characteristics_comparison.png') -> None:
    """
    Create a visual comparison table of attractor characteristics.

    Displays key properties side-by-side to highlight similarities and differences.
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('tight')
    ax.axis('off')

    # Data for comparison
    characteristics = [
        ['Property', 'Lorenz', 'Rössler', 'Thomas'],
        ['', '', '', ''],
        ['Structure', 'Asymmetric butterfly\nTwo lobes', 'Single spiral\nOne funnel', 'Circular loops\nThreefold symmetry'],
        ['', '', '', ''],
        ['Coupling', 'Polynomial\n(quadratic terms)', 'Mixed\n(linear + nonlinear)', 'Trigonometric\n(sine functions)'],
        ['', '', '', ''],
        ['Symmetry', 'Mirror plane:\n(x,y,z) → (-x,-y,z)', 'None', 'Rotational:\n(x,y,z) → (y,z,x)'],
        ['', '', '', ''],
        ['Lyapunov λ', '≈ 0.9\n(Highly chaotic)', '≈ 0.2-0.4\n(Moderate)', '≈ 0.05-0.1\n(Gentler chaos)'],
        ['', '', '', ''],
        ['Predictability τ', '≈ 1.1 time units\n(Very short)', '≈ 3-5 time units\n(Moderate)', '≈ 14 time units\n(Longer)'],
        ['', '', '', ''],
        ['Route to Chaos', 'Sharp bifurcation\nat ρ ≈ 24.74', 'Period-doubling\ncascade', 'Gradual transition\nas b decreases'],
        ['', '', '', ''],
        ['Fractal Dimension', 'D ≈ 2.06\n(Slightly wrinkled)', 'D ≈ 2.01\n(Nearly smooth)', 'D ≈ 2.1-2.3\n(More complex)'],
        ['', '', '', ''],
        ['Origin', 'Weather modeling\n(Lorenz, 1963)', 'Chemical reactions\n(Rössler, 1976)', 'Abstract model\n(Thomas, 1999)'],
        ['', '', '', ''],
        ['Key Parameter', 'ρ (Rayleigh number)\nForces convection', 'c (feedback strength)\nControls stretching', 'b (damping)\nBalances system'],
    ]

    # Color coding for headers
    colors = [['lightgray', 'lightcoral', 'lightgreen', 'lightblue']]
    for i in range(1, len(characteristics)):
        if i % 2 == 0:
            colors.append(['white', 'white', 'white', 'white'])
        else:
            colors.append(['#f0f0f0', '#f0f0f0', '#f0f0f0', '#f0f0f0'])

    # Create table
    table = ax.table(cellText=characteristics, cellLoc='center',
                    loc='center', cellColours=colors)

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)

    # Make header row bold
    for i in range(4):
        table[(0, i)].set_text_props(weight='bold', size=11)

    # Adjust column widths
    table.auto_set_column_width([0, 1, 2, 3])

    plt.title('Comparative Analysis of Three Strange Attractors',
             fontsize=16, weight='bold', pad=20)

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved characteristics table to {output_file}")
    plt.close()


def butterfly_effect_comparison(output_file: str = 'butterfly_comparison.png') -> None:
    """
    Compare sensitivity to initial conditions across all three attractors.

    Shows how quickly nearby trajectories diverge in each system.
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    epsilon = 1e-8  # Tiny perturbation
    t_max = 30

    systems = [
        ('Lorenz', lorenz, np.array([1.0, 1.0, 1.0]),
         {'sigma': 10, 'rho': 28, 'beta': 8/3}, 'plasma'),
        ('Rössler', rossler, np.array([1.0, 1.0, 1.0]),
         {'a': 0.2, 'b': 0.2, 'c': 5.7}, 'viridis'),
        ('Thomas', thomas, np.array([0.1, 0.0, 0.0]),
         {'b': 0.18}, 'cool'),
    ]

    for col, (name, system, x0, params, cmap) in enumerate(systems):
        print(f"Computing butterfly effect for {name}...")

        # Original trajectory
        traj1 = simulate_attractor(system, x0, t_max=t_max, dt=0.01, **params)

        # Perturbed trajectory
        x0_pert = x0 + np.array([epsilon, 0, 0])
        traj2 = simulate_attractor(system, x0_pert, t_max=t_max, dt=0.01, **params)

        # Calculate divergence
        distance = np.linalg.norm(traj1 - traj2, axis=0)
        times = np.arange(0, t_max, 0.01)

        # Top row: 3D trajectories
        ax_3d = axes[0, col]
        if col == 0:
            ax_3d = fig.add_subplot(2, 3, col + 1, projection='3d')
            axes[0, col].remove()
            axes[0, col] = ax_3d
            fig.add_subplot(ax_3d)

        ax_3d = fig.add_subplot(2, 3, col + 1, projection='3d')
        ax_3d.plot(traj1[0], traj1[1], traj1[2], 'b-', linewidth=0.8,
                  alpha=0.6, label='Original')
        ax_3d.plot(traj2[0], traj2[1], traj2[2], 'r-', linewidth=0.8,
                  alpha=0.6, label=f'Perturbed (ε={epsilon})')
        ax_3d.set_title(f'{name} Attractor\nTrajectory Divergence', fontsize=12, weight='bold')
        ax_3d.legend(fontsize=8)
        ax_3d.grid(True, alpha=0.3)

        # Bottom row: Distance over time
        ax_dist = axes[1, col]
        ax_dist.semilogy(times[:len(distance)], distance, linewidth=2, color='purple')
        ax_dist.set_xlabel('Time', fontsize=11)
        ax_dist.set_ylabel('Distance between trajectories', fontsize=11)
        ax_dist.set_title(f'Exponential Divergence', fontsize=12, weight='bold')
        ax_dist.grid(True, alpha=0.3)

        # Calculate and annotate amplification
        initial_dist = distance[0]
        final_dist = distance[-1]
        amplification = final_dist / initial_dist

        ax_dist.text(0.6, 0.85, f'Initial: {initial_dist:.2e}\nFinal: {final_dist:.2e}\n' +
                    f'Amplified: {amplification:.2e}×',
                    transform=ax_dist.transAxes, fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
                    verticalalignment='top')

    plt.suptitle('Butterfly Effect Across Three Attractors\n' +
                'How tiny differences grow exponentially',
                fontsize=16, weight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved butterfly effect comparison to {output_file}")
    plt.close()


if __name__ == '__main__':
    print("="*70)
    print("COMPARATIVE ANALYSIS: Lorenz vs Rössler vs Thomas")
    print("="*70)

    print("\n1/3: Creating attractor gallery...")
    create_gallery()

    print("\n2/3: Creating characteristics comparison table...")
    create_characteristics_table()

    print("\n3/3: Comparing butterfly effects...")
    butterfly_effect_comparison()

    print("\n" + "="*70)
    print("✓ Comparative analysis complete!")
    print("="*70)

    print("\nKey insights:")
    print("  • All three systems are chaotic (positive Lyapunov exponents)")
    print("  • But they have distinct personalities:")
    print("    - Lorenz: Wildly chaotic, short predictability")
    print("    - Rössler: Moderate chaos, clean spiral structure")
    print("    - Thomas: Gentler chaos, longer predictability, beautiful symmetry")
    print("  • Different routes to chaos:")
    print("    - Lorenz: Sharp bifurcation")
    print("    - Rössler: Period-doubling cascade")
    print("    - Thomas: Gradual transition")
    print("\nChaos is not one thing - it's a rich spectrum of behaviors!")
