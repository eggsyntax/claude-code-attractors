"""
Combined Bifurcation and Lyapunov Exponent Visualization

This module creates dual-panel plots showing both the bifurcation diagram
(what the system does) and the Lyapunov exponent curve (how chaotic it is).

The combination reveals the deep connection between structure and chaos:
- Where λ crosses zero, the bifurcation diagram shows transition to chaos
- Periodic windows appear where λ dips back negative
- The Lyapunov curve quantifies what the bifurcation shows qualitatively
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Callable, Tuple
from bifurcation import create_bifurcation_diagram
from lyapunov import compute_lyapunov_exponent


def combined_bifurcation_lyapunov(
    equations_factory: Callable,
    param_range: np.ndarray,
    initial_state: np.ndarray,
    param_name: str,
    system_name: str,
    crossing_plane: str = 'y',
    crossing_direction: str = 'positive',
    output_file: str = None
) -> None:
    """
    Create a dual-panel visualization showing bifurcation and Lyapunov exponent.

    Top panel: Bifurcation diagram (Poincaré section vs parameter)
    Bottom panel: Largest Lyapunov exponent vs parameter

    The λ=0 line on the bottom panel marks the chaos threshold, aligning
    with dramatic changes in the bifurcation structure above.

    Args:
        equations_factory: Function (param_value) -> equations(t, state)
        param_range: Parameter values to sweep
        initial_state: Starting state for all trajectories
        param_name: Parameter name for axis labels
        system_name: System name for title
        crossing_plane: Which coordinate to plot ('x', 'y', or 'z')
        crossing_direction: 'positive' or 'negative' velocity crossing
        output_file: Path to save figure (optional)

    Example:
        >>> def lorenz_factory(rho):
        ...     def equations(t, state):
        ...         x, y, z = state
        ...         return [10*(y-x), x*(rho-z)-y, x*y-8/3*z]
        ...     return equations
        >>> rho_range = np.linspace(10, 40, 100)
        >>> combined_bifurcation_lyapunov(
        ...     lorenz_factory, rho_range, [1,1,1], "ρ", "Lorenz"
        ... )
    """
    print(f"\nGenerating combined bifurcation-Lyapunov analysis for {system_name}")
    print("=" * 70)

    # Compute bifurcation diagram
    print("\n1. Computing bifurcation diagram...")
    param_values, poincare_values = create_bifurcation_diagram(
        equations_factory=equations_factory,
        param_range=param_range,
        initial_state=initial_state,
        crossing_plane=crossing_plane,
        crossing_direction=crossing_direction,
        show_plot=False
    )

    # Compute Lyapunov exponents
    print("\n2. Computing Lyapunov exponents...")
    lyapunov_values = []

    for i, param_value in enumerate(param_range):
        equations = equations_factory(param_value)

        lambda_max = compute_lyapunov_exponent(
            equations,
            initial_state,
            dt=0.01,
            total_time=80.0,
            transient_time=20.0
        )

        lyapunov_values.append(lambda_max)

        # Progress indicator
        if (i + 1) % max(1, len(param_range) // 10) == 0:
            progress = 100 * (i + 1) / len(param_range)
            print(f"   Progress: {progress:.0f}% - {param_name}={param_value:.2f}, λ={lambda_max:.4f}")

    lyapunov_values = np.array(lyapunov_values)

    # Create dual-panel figure
    print("\n3. Creating visualization...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Top panel: Bifurcation diagram
    ax1.plot(param_values, poincare_values, ',k', alpha=0.5, markersize=0.5)
    ax1.set_ylabel(f'{crossing_plane.upper()} at Poincaré Section', fontsize=12)
    ax1.set_title(f'{system_name} System: Bifurcation Diagram and Lyapunov Exponent',
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Bottom panel: Lyapunov exponent
    ax2.plot(param_range, lyapunov_values, 'b-', linewidth=2, label='λ_max')
    ax2.axhline(y=0, color='r', linestyle='--', linewidth=1.5, label='λ = 0 (chaos threshold)')
    ax2.fill_between(param_range, 0, lyapunov_values,
                     where=(lyapunov_values > 0), alpha=0.3, color='red',
                     label='Chaotic regime')
    ax2.fill_between(param_range, lyapunov_values, 0,
                     where=(lyapunov_values < 0), alpha=0.3, color='blue',
                     label='Stable regime')

    ax2.set_xlabel(f'Parameter {param_name}', fontsize=12)
    ax2.set_ylabel('Largest Lyapunov Exponent λ₁', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best', fontsize=10)

    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved to {output_file}")

    plt.show()

    # Analyze chaos transitions
    print("\n4. Analysis of chaos transitions:")
    print("-" * 70)

    # Find zero crossings
    zero_crossings = []
    for i in range(len(lyapunov_values) - 1):
        if lyapunov_values[i] * lyapunov_values[i+1] < 0:
            # Linear interpolation to find crossing point
            crossing = param_range[i] + (param_range[i+1] - param_range[i]) * \
                      (-lyapunov_values[i]) / (lyapunov_values[i+1] - lyapunov_values[i])
            zero_crossings.append(crossing)

    if zero_crossings:
        print(f"Chaos threshold crossings (λ = 0):")
        for crossing in zero_crossings:
            print(f"  {param_name} ≈ {crossing:.3f}")
    else:
        print("No chaos transitions found in parameter range")

    # Identify chaotic regions
    chaotic_mask = lyapunov_values > 0
    if np.any(chaotic_mask):
        chaotic_frac = np.sum(chaotic_mask) / len(chaotic_mask)
        print(f"\nChaotic parameter fraction: {100*chaotic_frac:.1f}%")

        max_lambda_idx = np.argmax(lyapunov_values)
        print(f"Maximum chaos: λ = {lyapunov_values[max_lambda_idx]:.4f} "
              f"at {param_name} = {param_range[max_lambda_idx]:.3f}")

    print("\n" + "=" * 70)


def lorenz_combined_analysis(output_dir: str = ".") -> None:
    """
    Generate combined bifurcation-Lyapunov analysis for Lorenz system.

    Sweeps ρ (Rayleigh number) from 10 to 40, showing the transition from
    stable fixed points through the iconic butterfly attractor into more
    complex chaotic regimes.

    Critical value: ρ_c ≈ 24.74 where chaos first emerges.
    """
    def lorenz_factory(rho):
        def equations(t, state, sigma=10.0, beta=8.0/3.0):
            x, y, z = state
            return np.array([
                sigma * (y - x),
                x * (rho - z) - y,
                x * y - beta * z
            ])
        return equations

    param_range = np.linspace(10, 40, 80)
    initial_state = np.array([1.0, 1.0, 1.0])

    combined_bifurcation_lyapunov(
        equations_factory=lorenz_factory,
        param_range=param_range,
        initial_state=initial_state,
        param_name='ρ',
        system_name='Lorenz',
        crossing_plane='z',
        crossing_direction='positive',
        output_file=f'{output_dir}/lorenz_bifurcation_lyapunov.png'
    )


def rossler_combined_analysis(output_dir: str = ".") -> None:
    """
    Generate combined bifurcation-Lyapunov analysis for Rössler system.

    Sweeps c parameter from 2 to 8, revealing the beautiful period-doubling
    cascade: 1 → 2 → 4 → 8 → ... → chaos.

    The Lyapunov curve shows λ crossing zero at each period-doubling, with
    brief returns to negative values at periodic windows.
    """
    def rossler_factory(c):
        def equations(t, state, a=0.2, b=0.2):
            x, y, z = state
            return np.array([
                -y - z,
                x + a * y,
                b + z * (x - c)
            ])
        return equations

    param_range = np.linspace(2.0, 8.0, 80)
    initial_state = np.array([1.0, 1.0, 1.0])

    combined_bifurcation_lyapunov(
        equations_factory=rossler_factory,
        param_range=param_range,
        initial_state=initial_state,
        param_name='c',
        system_name='Rössler',
        crossing_plane='z',
        crossing_direction='positive',
        output_file=f'{output_dir}/rossler_bifurcation_lyapunov.png'
    )


def compare_predictability_horizons(output_dir: str = ".") -> None:
    """
    Compare predictability horizons (1/λ) for different systems and parameters.

    The predictability horizon is the time scale beyond which predictions
    become unreliable due to chaos. Smaller λ → longer prediction window.

    Creates a bar chart comparing different configurations.
    """
    print("\nComparing predictability horizons across systems")
    print("=" * 70)

    systems = []

    # Lorenz at different ρ values
    for rho in [24, 28, 35]:
        def lorenz(t, state):
            x, y, z = state
            return np.array([
                10 * (y - x),
                x * (rho - z) - y,
                x * y - 8/3 * z
            ])

        lambda_max = compute_lyapunov_exponent(
            lorenz, [1, 1, 1], total_time=100.0
        )

        if lambda_max > 0:
            horizon = 1.0 / lambda_max
            systems.append({
                'name': f'Lorenz (ρ={rho})',
                'lambda': lambda_max,
                'horizon': horizon
            })
            print(f"Lorenz (ρ={rho:2d}): λ={lambda_max:6.4f}, horizon={horizon:5.2f} time units")

    # Rössler at different c values
    for c in [4.0, 5.7, 7.0]:
        def rossler(t, state):
            x, y, z = state
            return np.array([
                -y - z,
                x + 0.2 * y,
                0.2 + z * (x - c)
            ])

        lambda_max = compute_lyapunov_exponent(
            rossler, [1, 1, 1], total_time=100.0
        )

        if lambda_max > 0:
            horizon = 1.0 / lambda_max
            systems.append({
                'name': f'Rössler (c={c})',
                'lambda': lambda_max,
                'horizon': horizon
            })
            print(f"Rössler (c={c:3.1f}): λ={lambda_max:6.4f}, horizon={horizon:5.2f} time units")

    # Create comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    names = [s['name'] for s in systems]
    lambdas = [s['lambda'] for s in systems]
    horizons = [s['horizon'] for s in systems]

    # Lyapunov exponents
    colors = ['#e74c3c' if 'Lorenz' in name else '#3498db' for name in names]
    ax1.barh(names, lambdas, color=colors, alpha=0.7)
    ax1.set_xlabel('Largest Lyapunov Exponent λ₁', fontsize=12)
    ax1.set_title('Chaos Strength', fontsize=13, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)

    # Predictability horizons
    ax2.barh(names, horizons, color=colors, alpha=0.7)
    ax2.set_xlabel('Predictability Horizon (1/λ) [time units]', fontsize=12)
    ax2.set_title('Prediction Window', fontsize=13, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/predictability_comparison.png', dpi=300, bbox_inches='tight')
    print(f"\nSaved comparison to {output_dir}/predictability_comparison.png")
    plt.show()

    print("\n" + "=" * 70)


if __name__ == '__main__':
    """Generate all combined analyses."""
    import os

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("COMBINED BIFURCATION AND LYAPUNOV ANALYSIS")
    print("=" * 70)

    # Lorenz analysis
    lorenz_combined_analysis(output_dir)

    # Rössler analysis
    rossler_combined_analysis(output_dir)

    # Predictability comparison
    compare_predictability_horizons(output_dir)

    print("\n" + "=" * 70)
    print("All analyses complete!")
    print("=" * 70)
