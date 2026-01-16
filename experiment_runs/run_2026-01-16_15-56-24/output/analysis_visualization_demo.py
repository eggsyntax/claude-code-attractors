"""
Comprehensive demonstration of analysis visualization capabilities.

This script showcases the integration between analysis.py and visualizer.py,
demonstrating how quantitative analysis and beautiful visualizations come together
to reveal the nature of chaotic systems.

Demonstrations:
1. Return maps for Lorenz and Rössler attractors
2. Divergence plots showing the butterfly effect quantitatively
3. Lyapunov convergence visualization
4. Phase space reconstruction (Takens embedding)
5. Comprehensive analysis summary figures

Author: Alice & Bob
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing
import matplotlib.pyplot as plt

from lorenz import LorenzAttractor
from rossler import RosslerAttractor
from visualizer import AttractorVisualizer
import analysis


def demo1_return_maps():
    """
    Demo 1: Return maps for both attractors.

    Return maps reveal the underlying structure of chaotic systems.
    Fixed points appear on the diagonal, periodic orbits as closed loops,
    and chaos as complex fractal-like curves.
    """
    print("=" * 70)
    print("DEMO 1: Return Maps")
    print("=" * 70)

    # Lorenz attractor
    print("\nGenerating Lorenz attractor data...")
    lorenz = LorenzAttractor()
    lorenz_traj = lorenz.generate_trajectory(t_span=(0, 100), n_points=10000)

    # We need a Poincaré section to compute return map
    # For Lorenz, use z=27 plane (middle of the attractor)
    print("Computing Poincaré section at z=27...")
    lorenz_section = np.array([[x, y] for x, y, z in lorenz_traj if abs(z - 27) < 0.5])

    if len(lorenz_section) > 100:
        print(f"Found {len(lorenz_section)} section points")
        lorenz_return_map = analysis.compute_return_map(lorenz_section, dimension=0, delay=1)

        vis = AttractorVisualizer()
        vis.plot_return_map(
            lorenz_return_map,
            title="Lorenz Attractor Return Map (z=27 section, x-coordinate)",
            use_sequence_colors=True,
            show=False
        )
        plt.savefig('demo1_lorenz_return_map.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: demo1_lorenz_return_map.png")
    else:
        print("⚠ Not enough section points for Lorenz return map")

    # Rössler attractor
    print("\nGenerating Rössler attractor data...")
    rossler = RosslerAttractor()
    rossler_traj = rossler.generate_trajectory(t_span=(0, 500), n_points=50000)

    # For Rössler, use the built-in Poincaré section method
    print("Computing Poincaré section at z=0...")
    rossler_section = rossler.compute_poincare_section(
        rossler_traj, plane='z', plane_value=0.0, direction='up'
    )

    print(f"Found {len(rossler_section)} section points")
    rossler_return_map = analysis.compute_return_map(rossler_section, dimension=0, delay=1)

    vis = AttractorVisualizer()
    vis.plot_return_map(
        rossler_return_map,
        title="Rössler Attractor Return Map (z=0 section, x-coordinate)",
        use_sequence_colors=True,
        show=False
    )
    plt.savefig('demo1_rossler_return_map.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo1_rossler_return_map.png")

    print("\nReturn map interpretation:")
    print("  - Smooth curve: deterministic chaos")
    print("  - Fractal structure: complex dynamics")
    print("  - Points on diagonal: fixed points")
    print("  - The spiral structure in Rössler is clearly visible!")


def demo2_divergence_butterfly_effect():
    """
    Demo 2: Quantifying the butterfly effect.

    Shows exponential divergence of initially close trajectories,
    the hallmark of chaos.
    """
    print("\n" + "=" * 70)
    print("DEMO 2: Divergence - Quantifying the Butterfly Effect")
    print("=" * 70)

    print("\nGenerating Lorenz trajectories with tiny initial difference...")
    lorenz = LorenzAttractor()
    traj1, traj2 = lorenz.generate_butterfly_effect_demo(epsilon=1e-8)

    print("Computing divergence between trajectories...")
    divergence = analysis.compute_divergence(traj1, traj2, norm='euclidean')

    print(f"Initial separation: {divergence[0]:.2e}")
    print(f"Final separation: {divergence[-1]:.2f}")
    print(f"Growth factor: {divergence[-1] / divergence[0]:.2e}x")

    vis = AttractorVisualizer()

    # Plot with log scale to see exponential growth
    print("\nPlotting divergence on log scale...")
    vis.plot_divergence(
        divergence,
        title="Lorenz Butterfly Effect: Exponential Divergence",
        log_scale=True,
        fit_exponential=True,
        show=False
    )
    plt.savefig('demo2_divergence_logscale.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo2_divergence_logscale.png")

    # Also plot on linear scale
    print("Plotting divergence on linear scale...")
    vis.plot_divergence(
        divergence,
        title="Lorenz Butterfly Effect: Linear Scale",
        log_scale=False,
        fit_exponential=False,
        show=False
    )
    plt.savefig('demo2_divergence_linear.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo2_divergence_linear.png")

    print("\nThis is chaos in action:")
    print("  - Infinitesimal differences grow exponentially")
    print("  - Long-term prediction becomes impossible")
    print("  - Yet the system remains bounded (strange attractor)")


def demo3_lyapunov_exponents():
    """
    Demo 3: Lyapunov exponent estimation and convergence visualization.

    The Lyapunov exponent quantifies chaos:
    - λ₁ > 0: chaotic (exponential divergence)
    - λ₁ = 0: periodic/quasiperiodic
    - λ₁ < 0: converging to fixed point
    """
    print("\n" + "=" * 70)
    print("DEMO 3: Lyapunov Exponents - The Gold Standard for Chaos")
    print("=" * 70)

    # Lorenz
    print("\nEstimating Lorenz Lyapunov exponent...")
    print("(This may take a moment - we're tracking trajectory divergence carefully)")
    lorenz = LorenzAttractor()
    lorenz_lyap = analysis.estimate_lyapunov_exponents(
        lorenz,
        method='finitetime',
        t_span=(0, 100),
        n_points=10000,
        include_diagnostics=True
    )

    print(f"\n✓ Lorenz λ₁ = {lorenz_lyap['exponent']:.4f}")
    print(f"  Expected: ~0.9")
    print(f"  Difference: {abs(lorenz_lyap['exponent'] - 0.9):.4f}")

    if 'std_error' in lorenz_lyap:
        print(f"  Standard error: {lorenz_lyap['std_error']:.4f}")

    vis = AttractorVisualizer()
    vis.plot_lyapunov_convergence(
        lorenz_lyap,
        title="Lorenz Attractor: Lyapunov Exponent Convergence",
        show_confidence=True,
        show=False
    )
    plt.savefig('demo3_lorenz_lyapunov.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo3_lorenz_lyapunov.png")

    # Rössler
    print("\nEstimating Rössler Lyapunov exponent...")
    rossler = RosslerAttractor()
    rossler_lyap = analysis.estimate_lyapunov_exponents(
        rossler,
        method='finitetime',
        t_span=(0, 500),
        n_points=50000,
        include_diagnostics=True
    )

    print(f"\n✓ Rössler λ₁ = {rossler_lyap['exponent']:.4f}")
    print(f"  Expected: ~0.07")
    print(f"  Difference: {abs(rossler_lyap['exponent'] - 0.07):.4f}")

    if 'std_error' in rossler_lyap:
        print(f"  Standard error: {rossler_lyap['std_error']:.4f}")

    vis.plot_lyapunov_convergence(
        rossler_lyap,
        title="Rössler Attractor: Lyapunov Exponent Convergence",
        show_confidence=True,
        show=False
    )
    plt.savefig('demo3_rossler_lyapunov.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo3_rossler_lyapunov.png")

    print("\nInterpretation:")
    print(f"  - Both λ₁ > 0: both systems are chaotic")
    print(f"  - Lorenz λ₁ ≈ {lorenz_lyap['exponent']:.2f} > Rössler λ₁ ≈ {rossler_lyap['exponent']:.2f}")
    print(f"  - Lorenz is ~{lorenz_lyap['exponent']/rossler_lyap['exponent']:.1f}x more chaotic!")


def demo4_takens_embedding():
    """
    Demo 4: Phase space reconstruction from 1D time series.

    Demonstrates Takens' theorem: we can reconstruct the full attractor
    from just one observable using time-delay embedding!
    """
    print("\n" + "=" * 70)
    print("DEMO 4: Takens Embedding - Reconstructing Attractors from 1D Data")
    print("=" * 70)

    print("\nGenerating Lorenz attractor...")
    lorenz = LorenzAttractor()
    trajectory = lorenz.generate_trajectory(t_span=(0, 100), n_points=10000)

    # Extract just the x-coordinate (1D time series)
    x_series = trajectory[:, 0]
    print(f"Original data: 3D trajectory with {len(trajectory)} points")
    print(f"Observable: Just x-coordinate (1D time series)")

    # Reconstruct the attractor from x alone!
    print("\nReconstructing full 3D attractor from x-coordinate alone...")
    print("Using time-delay embedding: [x(t), x(t+τ), x(t+2τ)]")

    delay = 10  # Chosen based on first minimum of autocorrelation (simplified)
    embedding_dim = 3

    embedded = analysis.compute_time_delay_embedding(
        x_series, delay=delay, embedding_dim=embedding_dim
    )

    print(f"✓ Reconstructed trajectory: {embedded.shape}")
    print(f"  Embedding delay: {delay}")
    print(f"  Embedding dimension: {embedding_dim}")

    vis = AttractorVisualizer()
    vis.plot_phase_space_reconstruction(
        embedded,
        title=f"Lorenz Attractor Reconstructed from X-Coordinate\n(delay={delay}, dim={embedding_dim})",
        color='purple',
        alpha=0.6,
        show=False
    )
    plt.savefig('demo4_takens_embedding.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo4_takens_embedding.png")

    print("\nTakens' Theorem in action:")
    print("  - Started with 1D observable (just x)")
    print("  - Reconstructed full 3D attractor structure")
    print("  - Preserves topological properties of original")
    print("  - This is how we analyze real-world time series!")


def demo5_comprehensive_summary():
    """
    Demo 5: Publication-ready comprehensive analysis summaries.

    Creates 4-panel figures combining all analysis techniques:
    - 3D trajectory
    - Poincaré section
    - Return map
    - Lyapunov convergence
    """
    print("\n" + "=" * 70)
    print("DEMO 5: Comprehensive Analysis Summary Figures")
    print("=" * 70)

    # Lorenz comprehensive analysis
    print("\nPreparing Lorenz comprehensive analysis...")
    lorenz = LorenzAttractor()
    lorenz_traj = lorenz.generate_trajectory(t_span=(0, 100), n_points=10000)

    # Poincaré section (manual for Lorenz)
    lorenz_section = np.array([[x, y] for x, y, z in lorenz_traj if abs(z - 27) < 0.5])

    # Return map
    if len(lorenz_section) > 100:
        lorenz_return_map = analysis.compute_return_map(lorenz_section, dimension=0)
    else:
        lorenz_return_map = None

    # Lyapunov
    print("Computing Lyapunov exponent...")
    lorenz_lyap = analysis.estimate_lyapunov_exponents(
        lorenz, t_span=(0, 100), n_points=10000, include_diagnostics=True
    )

    print("Creating comprehensive summary figure...")
    vis = AttractorVisualizer(figsize=(16, 12))
    vis.plot_analysis_summary(
        lorenz,
        lorenz_traj,
        section_data=lorenz_section if len(lorenz_section) > 100 else None,
        return_map_data=lorenz_return_map,
        lyapunov_result=lorenz_lyap,
        show=False
    )
    plt.savefig('demo5_lorenz_summary.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo5_lorenz_summary.png")

    # Rössler comprehensive analysis
    print("\nPreparing Rössler comprehensive analysis...")
    rossler = RosslerAttractor()
    rossler_traj = rossler.generate_trajectory(t_span=(0, 500), n_points=50000)

    # Poincaré section
    rossler_section = rossler.compute_poincare_section(
        rossler_traj, plane='z', plane_value=0.0, direction='up'
    )

    # Return map
    rossler_return_map = analysis.compute_return_map(rossler_section, dimension=0)

    # Lyapunov
    print("Computing Lyapunov exponent...")
    rossler_lyap = analysis.estimate_lyapunov_exponents(
        rossler, t_span=(0, 500), n_points=50000, include_diagnostics=True
    )

    print("Creating comprehensive summary figure...")
    vis = AttractorVisualizer(figsize=(16, 12))
    vis.plot_analysis_summary(
        rossler,
        rossler_traj,
        section_data=rossler_section,
        return_map_data=rossler_return_map,
        lyapunov_result=rossler_lyap,
        show=False
    )
    plt.savefig('demo5_rossler_summary.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo5_rossler_summary.png")

    print("\nPublication-ready figures created!")
    print("  - 4-panel layout with all key analyses")
    print("  - Clear visualization of chaotic dynamics")
    print("  - Quantitative and qualitative results combined")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("ANALYSIS VISUALIZATION DEMONSTRATIONS")
    print("Showcasing the integration of analysis.py and visualizer.py")
    print("=" * 70)

    demo1_return_maps()
    demo2_divergence_butterfly_effect()
    demo3_lyapunov_exponents()
    demo4_takens_embedding()
    demo5_comprehensive_summary()

    print("\n" + "=" * 70)
    print("ALL DEMONSTRATIONS COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  1. demo1_lorenz_return_map.png")
    print("  2. demo1_rossler_return_map.png")
    print("  3. demo2_divergence_logscale.png")
    print("  4. demo2_divergence_linear.png")
    print("  5. demo3_lorenz_lyapunov.png")
    print("  6. demo3_rossler_lyapunov.png")
    print("  7. demo4_takens_embedding.png")
    print("  8. demo5_lorenz_summary.png")
    print("  9. demo5_rossler_summary.png")
    print("\nOur toolkit now combines:")
    print("  ✓ Beautiful visualizations")
    print("  ✓ Rigorous quantitative analysis")
    print("  ✓ Publication-ready figures")
    print("  ✓ Educational demonstrations")
    print("\nChaos theory has never looked so good! 🦋")


if __name__ == "__main__":
    main()
