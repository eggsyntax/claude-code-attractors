#!/usr/bin/env python3
"""
Showcase Script - Demonstrates the complete chaos analysis toolkit

This script runs our complete analysis pipeline on the Lorenz attractor,
showing how all the pieces we've built work together seamlessly.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from lorenz import LorenzAttractor
from visualizer import AttractorVisualizer
import analysis

def main():
    print("=" * 70)
    print("CHAOS ANALYSIS TOOLKIT - LIVE DEMONSTRATION")
    print("A Collaboration Between Alice and Bob")
    print("=" * 70)
    print()

    # Create Lorenz attractor
    print("Step 1: Creating Lorenz attractor...")
    lorenz = LorenzAttractor()
    print(f"  Parameters: σ={lorenz.parameters['sigma']}, "
          f"ρ={lorenz.parameters['rho']}, β={lorenz.parameters['beta']}")
    print()

    # Generate trajectory
    print("Step 2: Generating trajectory...")
    trajectory = lorenz.generate_trajectory(t_span=(0, 50), n_points=5000)
    print(f"  Generated {len(trajectory)} points over 50 time units")
    print()

    # Compute Poincaré section
    print("Step 3: Computing Poincaré section...")
    section = lorenz.compute_poincare_section(
        trajectory,
        plane='z',
        plane_value=27,
        direction='up',
        method='tolerance'
    )
    print(f"  Found {len(section)} crossing points")
    print()

    # Compute return map
    print("Step 4: Computing return map...")
    return_map = analysis.compute_return_map(section, dimension=0)
    print(f"  Created map with {len(return_map['x_n'])} points")
    print()

    # Estimate Lyapunov exponent
    print("Step 5: Estimating Lyapunov exponent...")
    lyapunov = analysis.estimate_lyapunov_exponents(
        lorenz,
        n_iterations=100,
        include_diagnostics=True
    )
    print(f"  λ₁ = {lyapunov['exponent']:.6f} ± {lyapunov['std_error']:.6f}")
    print(f"  Converged: {'Yes ✓' if lyapunov['convergence_data']['converged'] else 'No ✗'}")
    print(f"  Expected ~0.9 (literature value)")
    print()

    # Compute divergence (butterfly effect)
    print("Step 6: Computing trajectory divergence...")
    traj1, traj2 = lorenz.generate_butterfly_effect_demo(
        epsilon=1e-8,
        t_span=(0, 20),
        n_points=2000
    )
    divergence = analysis.compute_divergence(traj1, traj2)

    # Estimate growth rate from log of divergence
    t = np.linspace(0, 20, len(divergence))
    valid = (divergence > 1e-10) & (divergence < 100)  # Avoid numerical issues
    if np.sum(valid) > 10:
        log_div = np.log(divergence[valid])
        t_valid = t[valid]
        # Simple linear fit in log space
        coeffs = np.polyfit(t_valid[:len(t_valid)//2], log_div[:len(log_div)//2], 1)
        growth_rate = coeffs[0]
        print(f"  Exponential growth rate: {growth_rate:.6f}")
        print(f"  Doubling time: {np.log(2)/growth_rate:.3f} time units")
    print()

    # Create visualizations
    print("Step 7: Creating visualizations...")
    vis = AttractorVisualizer()

    # 3D trajectory
    print("  - Plotting 3D trajectory...")
    vis.plot_trajectory_3d(trajectory, title="Lorenz Attractor", color='blue', alpha=0.3)
    plt.savefig('showcase_3d_trajectory.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Phase projections
    print("  - Plotting phase space projections...")
    vis.plot_phase_projections(trajectory, title="Lorenz Attractor Projections")
    plt.savefig('showcase_phase_projections.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Poincaré section
    print("  - Plotting Poincaré section...")
    vis.plot_poincare_section_2d(
        section,
        title="Poincaré Section (z=27, upward crossings)",
        use_sequence_colors=True,
        colormap='plasma'
    )
    plt.savefig('showcase_poincare_section.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Return map
    print("  - Plotting return map...")
    vis.plot_return_map(
        return_map,
        title="Return Map",
        use_sequence_colors=True,
        show_diagonal=True
    )
    plt.savefig('showcase_return_map.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Lyapunov convergence
    print("  - Plotting Lyapunov convergence...")
    vis.plot_lyapunov_convergence(
        lyapunov,
        title="Lyapunov Exponent Estimation",
        show_confidence=True
    )
    plt.savefig('showcase_lyapunov.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Divergence
    print("  - Plotting trajectory divergence...")
    vis.plot_divergence(
        divergence,
        t,
        title="Butterfly Effect: Trajectory Divergence",
        log_scale=True,
        fit_exponential=True
    )
    plt.savefig('showcase_divergence.png', dpi=150, bbox_inches='tight')
    plt.close()

    print()
    print("=" * 70)
    print("ANALYSIS COMPLETE!")
    print("=" * 70)
    print()
    print("Generated visualizations:")
    print("  ✓ showcase_3d_trajectory.png")
    print("  ✓ showcase_phase_projections.png")
    print("  ✓ showcase_poincare_section.png")
    print("  ✓ showcase_return_map.png")
    print("  ✓ showcase_lyapunov.png")
    print("  ✓ showcase_divergence.png")
    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()
    print(f"The Lorenz attractor exhibits STRONG CHAOS:")
    print(f"  • Positive Lyapunov exponent (λ₁ ≈ {lyapunov['exponent']:.3f})")
    print(f"  • Exponential trajectory divergence")
    print(f"  • Complex, non-repeating phase space structure")
    print(f"  • Fractal Poincaré section with spiral structure")
    print()
    print("This system is:")
    print("  • Deterministic (equations have no randomness)")
    print("  • Sensitive to initial conditions (butterfly effect)")
    print("  • Bounded (trajectories stay in finite region)")
    print("  • Aperiodic (never exactly repeats)")
    print()
    print("The combination of our visualization tools (Alice) and")
    print("analysis algorithms (Bob) provides both intuitive visual")
    print("understanding AND rigorous quantitative confirmation of chaos.")
    print()
    print("🦋 The butterfly has emerged from the equations! 🦋")
    print()

if __name__ == '__main__':
    main()
