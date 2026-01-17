"""
Bifurcation analysis for the Thomas attractor.

This module creates bifurcation diagrams showing how the Thomas attractor's
behavior changes as parameter b varies. Unlike Lorenz's sharp transitions or
Rössler's period-doubling cascade, Thomas shows a gradual transition to chaos.

The Thomas system:
    dx/dt = sin(y) - b·x
    dy/dt = sin(z) - b·y
    dz/dt = sin(x) - b·z

Author: Bob
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from typing import Tuple, List


def thomas_system(t: float, state: np.ndarray, b: float) -> np.ndarray:
    """
    Thomas attractor differential equations.

    Args:
        t: Time (not used, system is autonomous)
        state: Current state [x, y, z]
        b: System parameter (damping coefficient)

    Returns:
        Derivatives [dx/dt, dy/dt, dz/dt]
    """
    x, y, z = state
    return np.array([
        np.sin(y) - b * x,
        np.sin(z) - b * y,
        np.sin(x) - b * z
    ])


def poincare_section_thomas(b: float,
                            x0: np.ndarray = np.array([0.1, 0, 0]),
                            t_transient: float = 500,
                            t_sample: float = 2000,
                            plane_coord: int = 0,
                            plane_value: float = 0.0) -> List[float]:
    """
    Compute Poincaré section for Thomas attractor.

    This samples the attractor by detecting when trajectories cross a plane
    (default: x=0 with positive velocity).

    Args:
        b: Thomas system parameter
        x0: Initial condition
        t_transient: Time to discard (let transients decay)
        t_sample: Time to sample for crossings
        plane_coord: Which coordinate defines the plane (0=x, 1=y, 2=z)
        plane_value: The value of the plane

    Returns:
        List of sampled values at Poincaré crossings
    """
    # Integrate through transient
    t_span = (0, t_transient + t_sample)
    t_eval = np.linspace(0, t_transient + t_sample, int((t_transient + t_sample) * 50))

    sol = solve_ivp(thomas_system, t_span, x0, args=(b,),
                   t_eval=t_eval, method='RK45', rtol=1e-9, atol=1e-12)

    # Find crossings after transient period
    start_idx = np.searchsorted(sol.t, t_transient)
    trajectory = sol.y[:, start_idx:]

    crossings = []
    coord_values = trajectory[plane_coord]

    # Detect zero crossings with positive velocity
    for i in range(len(coord_values) - 1):
        if coord_values[i] <= plane_value < coord_values[i + 1]:
            # Linear interpolation to find crossing point
            alpha = (plane_value - coord_values[i]) / (coord_values[i + 1] - coord_values[i])

            # Sample one of the other coordinates (use z for x-plane)
            sample_coord = (plane_coord + 2) % 3
            crossing_value = (1 - alpha) * trajectory[sample_coord, i] + \
                           alpha * trajectory[sample_coord, i + 1]
            crossings.append(crossing_value)

    return crossings


def create_bifurcation_diagram(b_range: Tuple[float, float] = (0.05, 0.5),
                               n_points: int = 200,
                               output_file: str = 'thomas_bifurcation.png') -> None:
    """
    Create bifurcation diagram for Thomas attractor varying parameter b.

    Unlike Lorenz (sharp transitions) or Rössler (period-doubling cascade),
    Thomas shows a more gradual emergence of complexity as b decreases.

    Args:
        b_range: Range of b values to explore (min, max)
        n_points: Number of parameter values to sample
        output_file: Where to save the plot
    """
    b_values = np.linspace(b_range[0], b_range[1], n_points)

    fig, ax = plt.subplots(figsize=(12, 8))

    print("Computing Thomas bifurcation diagram...")
    for i, b in enumerate(b_values):
        if i % 20 == 0:
            print(f"  Progress: {i}/{n_points} ({100*i/n_points:.1f}%)")

        # Get Poincaré section samples
        crossings = poincare_section_thomas(b, t_transient=1000, t_sample=3000)

        # Plot as vertical scatter at this b value
        if len(crossings) > 0:
            ax.scatter([b] * len(crossings), crossings,
                      s=0.5, c='black', alpha=0.3)

    ax.set_xlabel('Parameter b', fontsize=14)
    ax.set_ylabel('z at Poincaré section (x=0, dx/dt>0)', fontsize=14)
    ax.set_title('Thomas Attractor Bifurcation Diagram\n' +
                'Gradual transition to chaos as b decreases',
                fontsize=16, pad=20)
    ax.grid(True, alpha=0.3)

    # Add annotations
    ax.text(0.42, ax.get_ylim()[1] * 0.9,
           'Higher b →\nStronger damping\nSimpler dynamics',
           fontsize=10, ha='center',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.text(0.12, ax.get_ylim()[1] * 0.9,
           '← Lower b\nWeaker damping\nRicher chaos',
           fontsize=10, ha='center',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nSaved bifurcation diagram to {output_file}")
    plt.close()


def compare_three_attractors(output_file: str = 'bifurcation_comparison.png') -> None:
    """
    Create side-by-side bifurcation diagrams for all three attractors.

    This shows the distinct routes to chaos:
    - Lorenz: Sharp bifurcation at ρ ≈ 24.74
    - Rössler: Period-doubling cascade
    - Thomas: Gradual transition
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Thomas
    print("\n1/3: Computing Thomas bifurcation...")
    b_values = np.linspace(0.05, 0.5, 150)
    for i, b in enumerate(b_values):
        if i % 30 == 0:
            print(f"  Progress: {i}/{len(b_values)}")
        crossings = poincare_section_thomas(b, t_transient=800, t_sample=2000)
        if len(crossings) > 0:
            axes[0].scatter([b] * len(crossings), crossings,
                          s=0.5, c='blue', alpha=0.3)

    axes[0].set_xlabel('Parameter b', fontsize=12)
    axes[0].set_ylabel('z at x=0', fontsize=12)
    axes[0].set_title('Thomas Attractor\nGradual Transition', fontsize=13, pad=10)
    axes[0].grid(True, alpha=0.3)

    # Lorenz (simplified for comparison)
    print("\n2/3: Computing Lorenz bifurcation...")
    from bifurcation import lorenz_system, poincare_section

    rho_values = np.linspace(15, 35, 150)
    for i, rho in enumerate(rho_values):
        if i % 30 == 0:
            print(f"  Progress: {i}/{len(rho_values)}")
        crossings = poincare_section(lorenz_system, (10, 28, 8/3),
                                     param_idx=1, param_value=rho,
                                     t_transient=50, t_sample=200)
        if len(crossings) > 0:
            axes[1].scatter([rho] * len(crossings), crossings,
                          s=0.5, c='red', alpha=0.3)

    axes[1].set_xlabel('Parameter ρ', fontsize=12)
    axes[1].set_ylabel('z at y=0', fontsize=12)
    axes[1].set_title('Lorenz Attractor\nSharp Bifurcation', fontsize=13, pad=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].axvline(24.74, color='orange', linestyle='--', alpha=0.5,
                   label='Critical point')
    axes[1].legend()

    # Rössler
    print("\n3/3: Computing Rössler bifurcation...")
    from bifurcation import rossler_system

    c_values = np.linspace(2, 6, 150)
    for i, c in enumerate(c_values):
        if i % 30 == 0:
            print(f"  Progress: {i}/{len(c_values)}")
        crossings = poincare_section(rossler_system, (0.2, 0.2, 5.7),
                                     param_idx=2, param_value=c,
                                     t_transient=100, t_sample=500)
        if len(crossings) > 0:
            axes[2].scatter([c] * len(crossings), crossings,
                          s=0.5, c='green', alpha=0.3)

    axes[2].set_xlabel('Parameter c', fontsize=12)
    axes[2].set_ylabel('z at x=0', fontsize=12)
    axes[2].set_title('Rössler Attractor\nPeriod-Doubling Cascade', fontsize=13, pad=10)
    axes[2].grid(True, alpha=0.3)

    plt.suptitle('Three Routes to Chaos', fontsize=16, y=1.02, weight='bold')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nSaved comparison to {output_file}")
    plt.close()


if __name__ == '__main__':
    # Individual Thomas bifurcation
    create_bifurcation_diagram()

    # Comparative analysis
    print("\n" + "="*60)
    print("Creating comparative bifurcation diagram...")
    print("="*60)
    compare_three_attractors()

    print("\n✓ Analysis complete!")
    print("\nKey findings:")
    print("  • Thomas: Gradual complexity increase as b decreases")
    print("  • Lorenz: Sharp transition at ρ ≈ 24.74")
    print("  • Rössler: Clear period-doubling cascade")
    print("\nEach attractor has its own personality!")
