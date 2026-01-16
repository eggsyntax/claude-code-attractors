"""
Chaos Reporter Demonstration

This script demonstrates the automated chaos analysis and reporting capabilities
that Bob and Alice built together.

It shows how all our tools combine into a comprehensive analysis pipeline:
- Bob's attractor framework (Lorenz, Rössler)
- Bob's analysis tools (Lyapunov exponents, return maps, divergence)
- Alice's visualizations (3D plots, Poincaré sections, convergence plots)
- Bob's chaos reporter (automated report generation)
"""

from lorenz import LorenzAttractor
from rossler import RosslerAttractor
from chaos_reporter import ChaosReporter, compare_attractors


def demo_single_attractor_report():
    """Generate a comprehensive report for a single attractor."""
    print("\n" + "="*70)
    print("DEMO 1: Single Attractor Report - Lorenz System")
    print("="*70 + "\n")

    # Create Lorenz attractor
    lorenz = LorenzAttractor()

    # Generate comprehensive report
    reporter = ChaosReporter()
    text_file, pdf_file = reporter.generate_full_report(
        lorenz,
        output_dir="./chaos_reports",
        t_span=(0, 50),
        n_points=10000,
        include_poincare=True,
        include_lyapunov=True,
        include_divergence=True
    )

    print(f"\n{'='*70}")
    print("REPORT GENERATION COMPLETE")
    print(f"{'='*70}")
    print(f"Text report: {text_file}")
    print(f"Visual report (PDF): {pdf_file}")
    print(f"\nThe PDF contains:")
    print("  - 3D trajectory visualization")
    print("  - Phase space projections")
    print("  - Poincaré section analysis")
    print("  - Return map")
    print("  - Lyapunov exponent convergence")
    print("  - Trajectory divergence (butterfly effect)")


def demo_rossler_report():
    """Generate a comprehensive report for Rössler attractor."""
    print("\n\n" + "="*70)
    print("DEMO 2: Single Attractor Report - Rössler System")
    print("="*70 + "\n")

    # Create Rössler attractor
    rossler = RosslerAttractor()

    # Generate comprehensive report with longer time span
    reporter = ChaosReporter()
    text_file, pdf_file = reporter.generate_full_report(
        rossler,
        output_dir="./chaos_reports",
        t_span=(0, 200),
        n_points=20000,
        include_poincare=True,
        include_lyapunov=True,
        include_divergence=True,
        poincare_plane='z',
        poincare_value=0.0
    )

    print(f"\n{'='*70}")
    print("REPORT GENERATION COMPLETE")
    print(f"{'='*70}")
    print(f"Text report: {text_file}")
    print(f"Visual report (PDF): {pdf_file}")


def demo_attractor_comparison():
    """Generate comparative analysis of multiple attractors."""
    print("\n\n" + "="*70)
    print("DEMO 3: Comparative Analysis - Lorenz vs Rössler")
    print("="*70 + "\n")

    # Create both attractors
    lorenz = LorenzAttractor()
    rossler = RosslerAttractor()

    # Generate comparison report
    comparison_file = compare_attractors(
        [lorenz, rossler],
        output_dir="./chaos_reports",
        t_span=(0, 50),
        n_points=10000,
        include_poincare=True,
        include_lyapunov=True
    )

    print(f"\n{'='*70}")
    print("COMPARISON REPORT COMPLETE")
    print(f"{'='*70}")
    print(f"Comparison PDF: {comparison_file}")
    print(f"\nThe comparison shows:")
    print("  - Side-by-side 3D trajectories")
    print("  - Lyapunov exponent comparison")
    print("  - Quantifies that Lorenz is ~13x more chaotic than Rössler!")


def demo_parameter_exploration():
    """Generate reports for different parameter regimes."""
    print("\n\n" + "="*70)
    print("DEMO 4: Parameter Exploration - Rössler System")
    print("="*70 + "\n")

    print("Exploring different dynamical regimes...\n")

    # Get parameter recommendations
    regimes = RosslerAttractor.get_parameter_recommendations()

    reporter = ChaosReporter()

    for regime_name, params in list(regimes.items())[:3]:  # First 3 regimes
        print(f"\nAnalyzing: {regime_name}")
        print(f"Parameters: {params}")

        rossler = RosslerAttractor(parameters=params)

        # Quick analysis (no full report, just summary)
        results = reporter.analyze_attractor(
            rossler,
            t_span=(0, 200),
            n_points=15000,
            include_poincare=False,  # Skip for speed
            include_lyapunov=True,
            include_divergence=False
        )

        lyap = results['lyapunov']
        print(f"  λ₁ = {lyap['exponent']:.6f}")

        if lyap['exponent'] > 0.01:
            print("  → CHAOTIC")
        elif lyap['exponent'] > -0.01:
            print("  → MARGINALLY STABLE")
        else:
            print("  → STABLE/PERIODIC")


def demo_custom_analysis():
    """Show how to use the reporter with custom analysis settings."""
    print("\n\n" + "="*70)
    print("DEMO 5: Custom Analysis Configuration")
    print("="*70 + "\n")

    print("This demo shows flexibility in the analysis pipeline.\n")

    # Create attractor with custom parameters
    lorenz = LorenzAttractor(parameters={'sigma': 10, 'rho': 28, 'beta': 8/3})

    # Custom analysis: longer time, more points, specific Poincaré plane
    reporter = ChaosReporter()

    print("Running extended analysis (this may take a moment)...")
    results = reporter.analyze_attractor(
        lorenz,
        t_span=(0, 100),  # Longer time span
        n_points=20000,   # More points for better resolution
        include_poincare=True,
        include_lyapunov=True,
        include_divergence=True,
        poincare_plane='z',
        poincare_value=27.0  # Near the fixed point
    )

    # Generate just the text report
    text_report = reporter.generate_text_report(results)
    print("\n" + text_report)

    # Can save manually if desired
    print("\n[Visual report generation skipped in this demo]")
    print("Use reporter.generate_visual_report(results, 'output.pdf') to create it.")


def main():
    """Run all chaos reporter demonstrations."""
    print("\n" + "="*70)
    print(" CHAOS REPORTER DEMONSTRATION")
    print(" Automated Analysis of Chaotic Dynamical Systems")
    print("="*70)
    print("\nThis demonstration showcases the complete toolkit:")
    print("  - Lorenz and Rössler attractor implementations")
    print("  - Quantitative analysis (Lyapunov exponents, return maps)")
    print("  - Visual analysis (3D plots, Poincaré sections)")
    print("  - Automated report generation")
    print("\nAll built through collaboration between Bob and Alice!")

    try:
        # Run demonstrations
        demo_single_attractor_report()
        demo_rossler_report()
        demo_attractor_comparison()
        demo_parameter_exploration()
        demo_custom_analysis()

        print("\n\n" + "="*70)
        print(" ALL DEMONSTRATIONS COMPLETE!")
        print("="*70)
        print("\nCheck the ./chaos_reports directory for generated reports.")
        print("\nWhat we've demonstrated:")
        print("  ✓ Automated comprehensive analysis")
        print("  ✓ Publication-ready visualizations")
        print("  ✓ Quantitative chaos metrics")
        print("  ✓ Multi-attractor comparison")
        print("  ✓ Parameter space exploration")
        print("  ✓ Flexible, extensible framework")
        print("\nThis toolkit is ready for research, education, and exploration!")

    except Exception as e:
        print(f"\n ERROR: {e}")
        print("\nMake sure all required files are present:")
        print("  - lorenz.py, rossler.py (attractor implementations)")
        print("  - attractor_base.py (base class)")
        print("  - analysis.py (analysis functions)")
        print("  - visualizer.py (visualization tools)")
        print("  - chaos_reporter.py (report generation)")


if __name__ == "__main__":
    main()
