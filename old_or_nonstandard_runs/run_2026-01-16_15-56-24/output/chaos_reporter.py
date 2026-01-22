"""
Chaos Reporter - Comprehensive Analysis and Reporting Tool

This module provides automated chaos analysis and report generation for any
dynamical system. It combines all the tools Alice and I have built to create
publication-ready reports with visualizations and quantitative metrics.

Author: Bob (with visualizations by Alice)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import analysis
from visualizer import AttractorVisualizer
from attractor_base import AttractorBase


class ChaosReporter:
    """
    Automated chaos analysis and reporting system.

    Takes any AttractorBase instance and generates comprehensive analysis
    including visualizations, quantitative metrics, and interpretations.
    """

    def __init__(self, visualizer: Optional[AttractorVisualizer] = None):
        """
        Initialize the chaos reporter.

        Args:
            visualizer: Optional AttractorVisualizer instance. If None, creates one.
        """
        self.visualizer = visualizer or AttractorVisualizer()
        self.results = {}

    def analyze_attractor(
        self,
        attractor: AttractorBase,
        t_span: Tuple[float, float] = (0, 100),
        n_points: int = 10000,
        include_poincare: bool = True,
        include_lyapunov: bool = True,
        include_divergence: bool = True,
        poincare_plane: str = 'z',
        poincare_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive chaos analysis on an attractor.

        Args:
            attractor: The attractor system to analyze
            t_span: Time span for trajectory generation
            n_points: Number of points in trajectory
            include_poincare: Whether to compute Poincaré sections
            include_lyapunov: Whether to estimate Lyapunov exponents
            include_divergence: Whether to compute trajectory divergence
            poincare_plane: Plane for Poincaré section ('x', 'y', or 'z')
            poincare_value: Value of plane (None = use mean)

        Returns:
            Dictionary containing all analysis results
        """
        results = {
            'attractor_info': attractor.get_info(),
            'analysis_parameters': {
                't_span': t_span,
                'n_points': n_points
            }
        }

        # Generate main trajectory
        print(f"Generating trajectory for {results['attractor_info']['type']}...")
        trajectory = attractor.generate_trajectory(t_span=t_span, n_points=n_points)
        results['trajectory'] = trajectory

        # Poincaré section analysis
        if include_poincare:
            print("Computing Poincaré section...")
            if poincare_value is None:
                # Use mean value of the specified coordinate
                coord_map = {'x': 0, 'y': 1, 'z': 2}
                poincare_value = np.mean(trajectory[:, coord_map[poincare_plane]])

            section = attractor.compute_poincare_section(
                trajectory,
                plane=poincare_plane,
                plane_value=poincare_value,
                direction='up'
            )
            results['poincare_section'] = section

            # Compute return map from Poincaré section
            if len(section) > 1:
                print("Computing return map...")
                return_map = analysis.compute_return_map(section, dimension=0, delay=1)
                results['return_map'] = return_map

        # Lyapunov exponent estimation
        if include_lyapunov:
            print("Estimating Lyapunov exponent...")
            lyapunov = analysis.estimate_lyapunov_exponents(
                attractor,
                method='finitetime',
                t_span=t_span,
                include_diagnostics=True
            )
            results['lyapunov'] = lyapunov

        # Divergence analysis (butterfly effect)
        if include_divergence:
            print("Computing trajectory divergence...")
            # Generate two nearby trajectories
            state1 = attractor.initial_state.copy()
            state2 = state1 + 1e-8 * np.random.randn(len(state1))

            traj1 = attractor.generate_trajectory(
                initial_state=state1,
                t_span=t_span,
                n_points=n_points
            )
            traj2 = attractor.generate_trajectory(
                initial_state=state2,
                t_span=t_span,
                n_points=n_points
            )

            divergence = analysis.compute_divergence(traj1, traj2)
            results['divergence'] = divergence
            results['divergence_trajectories'] = (traj1, traj2)

        self.results = results
        return results

    def generate_text_report(self, results: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a text summary report of the analysis.

        Args:
            results: Analysis results (uses self.results if None)

        Returns:
            Formatted text report
        """
        if results is None:
            results = self.results

        info = results['attractor_info']
        report_lines = [
            "=" * 70,
            "CHAOS ANALYSIS REPORT",
            "=" * 70,
            "",
            f"Attractor Type: {info['type']}",
            f"Dimension: {info['dimension']}D",
            "",
            "Parameters:",
        ]

        for param, value in info['parameters'].items():
            report_lines.append(f"  {param} = {value}")

        report_lines.append("")
        report_lines.append("Initial State:")
        report_lines.append(f"  {info['initial_state']}")
        report_lines.append("")
        report_lines.append("-" * 70)
        report_lines.append("ANALYSIS RESULTS")
        report_lines.append("-" * 70)

        # Lyapunov exponent
        if 'lyapunov' in results:
            lyap = results['lyapunov']
            report_lines.append("")
            report_lines.append("Lyapunov Exponent:")
            report_lines.append(f"  λ₁ = {lyap['exponent']:.6f}")

            if 'std_error' in lyap:
                report_lines.append(f"  Standard Error: ±{lyap['std_error']:.6f}")

            if 'confidence_interval' in lyap:
                ci = lyap['confidence_interval']
                report_lines.append(f"  95% CI: [{ci[0]:.6f}, {ci[1]:.6f}]")

            if 'convergence_data' in lyap:
                conv = lyap['convergence_data']['converged']
                report_lines.append(f"  Converged: {'Yes ✓' if conv else 'No ⚠'}")

            # Interpretation
            exponent = lyap['exponent']
            if exponent > 0.1:
                interpretation = "STRONGLY CHAOTIC - High sensitivity to initial conditions"
            elif exponent > 0.01:
                interpretation = "CHAOTIC - Positive divergence indicates chaos"
            elif exponent > -0.01:
                interpretation = "NEAR-NEUTRAL - Borderline chaotic/regular behavior"
            else:
                interpretation = "REGULAR - Negative exponent indicates stable dynamics"

            report_lines.append(f"  Interpretation: {interpretation}")

        # Poincaré section
        if 'poincare_section' in results:
            section = results['poincare_section']
            report_lines.append("")
            report_lines.append("Poincaré Section:")
            report_lines.append(f"  Number of crossings: {len(section)}")

            if len(section) > 0:
                # Estimate whether it's a periodic orbit
                if len(section) < 10:
                    report_lines.append("  Structure: Likely periodic orbit (few crossings)")
                else:
                    # Check if points are clustered or dispersed
                    std = np.std(section, axis=0)
                    if np.all(std < 0.1):
                        report_lines.append("  Structure: Concentrated (periodic or quasi-periodic)")
                    else:
                        report_lines.append("  Structure: Dispersed (strange attractor)")

        # Return map
        if 'return_map' in results:
            rm = results['return_map']
            report_lines.append("")
            report_lines.append("Return Map:")
            report_lines.append(f"  Dimension: {rm['dimension']}")
            report_lines.append(f"  Delay: {rm['delay']}")
            report_lines.append(f"  Data points: {len(rm['x_n'])}")

        # Divergence
        if 'divergence' in results:
            div = results['divergence']
            report_lines.append("")
            report_lines.append("Trajectory Divergence (Butterfly Effect):")
            report_lines.append(f"  Initial separation: {div[0]:.2e}")
            report_lines.append(f"  Final separation: {div[-1]:.2e}")

            # Estimate exponential growth rate
            if len(div) > 10:
                # Fit exponential to first half (before saturation)
                mid = len(div) // 2
                t = np.arange(mid)
                log_div = np.log(div[:mid] + 1e-10)

                # Only fit if divergence is actually growing
                if log_div[-1] > log_div[0]:
                    growth_rate = (log_div[-1] - log_div[0]) / mid
                    report_lines.append(f"  Growth rate: {growth_rate:.6f}")
                    report_lines.append(f"  Doubling time: {np.log(2)/growth_rate:.2f} time units")

        report_lines.append("")
        report_lines.append("=" * 70)

        return "\n".join(report_lines)

    def generate_visual_report(
        self,
        results: Optional[Dict[str, Any]] = None,
        output_file: Optional[str] = None,
        show_plots: bool = False
    ):
        """
        Generate comprehensive visual report with all analysis plots.

        Args:
            results: Analysis results (uses self.results if None)
            output_file: Path to save PDF report (None = display only)
            show_plots: Whether to display plots interactively
        """
        if results is None:
            results = self.results

        info = results['attractor_info']
        attractor_name = info['type']

        # Create figure list
        figures = []

        # Figure 1: 3D Trajectory
        print("Creating 3D trajectory plot...")
        fig, ax = self.visualizer.plot_trajectory_3d(
            results['trajectory'],
            title=f"{attractor_name} - 3D Trajectory",
            color='viridis',
            alpha=0.6
        )
        figures.append(('3D Trajectory', fig))

        # Figure 2: Phase space projections
        if results['trajectory'].shape[1] >= 3:
            print("Creating phase space projections...")
            figs = self.visualizer.plot_phase_projections(
                results['trajectory'],
                title=f"{attractor_name} - Phase Space Projections"
            )
            figures.append(('Phase Space Projections', figs))

        # Figure 3: Poincaré section (if available)
        if 'poincare_section' in results and len(results['poincare_section']) > 0:
            print("Creating Poincaré section plot...")
            fig, ax = self.visualizer.plot_poincare_section_2d(
                results['poincare_section'],
                title=f"{attractor_name} - Poincaré Section",
                use_sequence_colors=True,
                colormap='plasma'
            )
            figures.append(('Poincaré Section', fig))

        # Figure 4: Return map (if available)
        if 'return_map' in results:
            print("Creating return map...")
            fig, ax = self.visualizer.plot_return_map(
                results['return_map'],
                title=f"{attractor_name} - Return Map",
                use_sequence_colors=True,
                show_diagonal=True
            )
            figures.append(('Return Map', fig))

        # Figure 5: Lyapunov convergence (if available)
        if 'lyapunov' in results and 'convergence_data' in results['lyapunov']:
            print("Creating Lyapunov convergence plot...")
            fig, ax = self.visualizer.plot_lyapunov_convergence(
                results['lyapunov'],
                title=f"{attractor_name} - Lyapunov Exponent Estimation",
                show_confidence=True
            )
            figures.append(('Lyapunov Convergence', fig))

        # Figure 6: Divergence plot (if available)
        if 'divergence' in results:
            print("Creating divergence plot...")
            fig, ax = self.visualizer.plot_divergence(
                results['divergence'],
                title=f"{attractor_name} - Trajectory Divergence",
                use_log_scale=True,
                show_fit=True
            )
            figures.append(('Trajectory Divergence', fig))

        # Save to PDF if requested
        if output_file:
            print(f"Saving visual report to {output_file}...")
            with PdfPages(output_file) as pdf:
                for title, fig in figures:
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close(fig)
            print(f"Visual report saved to {output_file}")

        # Show plots if requested
        if show_plots:
            plt.show()

        return figures

    def generate_full_report(
        self,
        attractor: AttractorBase,
        output_dir: str = "./reports",
        **analysis_kwargs
    ) -> Tuple[str, str]:
        """
        Generate complete analysis report (text + visual) for an attractor.

        Args:
            attractor: The attractor to analyze
            output_dir: Directory to save reports
            **analysis_kwargs: Arguments passed to analyze_attractor

        Returns:
            Tuple of (text_report_path, pdf_report_path)
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Analyze the attractor
        print(f"\n{'='*70}")
        print(f"ANALYZING {attractor.get_info()['type']}")
        print(f"{'='*70}\n")

        results = self.analyze_attractor(attractor, **analysis_kwargs)

        # Generate text report
        text_report = self.generate_text_report(results)
        print("\n" + text_report)

        # Save text report
        attractor_name = results['attractor_info']['type'].replace(' ', '_')
        text_file = output_path / f"{attractor_name}_report.txt"
        with open(text_file, 'w') as f:
            f.write(text_report)
        print(f"\nText report saved to {text_file}")

        # Generate and save visual report
        pdf_file = output_path / f"{attractor_name}_visual_report.pdf"
        self.generate_visual_report(results, output_file=str(pdf_file))

        return str(text_file), str(pdf_file)


def compare_attractors(
    attractors: List[AttractorBase],
    output_dir: str = "./reports",
    **analysis_kwargs
) -> str:
    """
    Generate comparative analysis report for multiple attractors.

    Args:
        attractors: List of attractors to compare
        output_dir: Directory to save comparison report
        **analysis_kwargs: Arguments passed to analyze_attractor

    Returns:
        Path to comparison report PDF
    """
    reporter = ChaosReporter()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Analyze all attractors
    all_results = []
    for attractor in attractors:
        print(f"\nAnalyzing {attractor.get_info()['type']}...")
        results = reporter.analyze_attractor(attractor, **analysis_kwargs)
        all_results.append(results)

    # Create comparison plots
    print("\nGenerating comparison visualizations...")

    # Comparison 1: Side-by-side 3D trajectories
    fig, axes = plt.subplots(1, len(attractors), figsize=(6*len(attractors), 5),
                             subplot_kw={'projection': '3d'})
    if len(attractors) == 1:
        axes = [axes]

    for idx, (results, ax) in enumerate(zip(all_results, axes)):
        traj = results['trajectory']
        info = results['attractor_info']
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], alpha=0.6, linewidth=0.5)
        ax.set_title(info['type'])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

    fig.suptitle('Attractor Comparison - 3D Trajectories', fontsize=14, fontweight='bold')
    plt.tight_layout()

    pdf_file = output_path / "attractor_comparison.pdf"
    with PdfPages(pdf_file) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # Comparison 2: Lyapunov exponents
        if all('lyapunov' in r for r in all_results):
            fig, ax = plt.subplots(figsize=(10, 6))
            names = [r['attractor_info']['type'] for r in all_results]
            exponents = [r['lyapunov']['exponent'] for r in all_results]
            errors = [r['lyapunov'].get('std_error', 0) for r in all_results]

            bars = ax.bar(names, exponents, yerr=errors, capsize=5, alpha=0.7,
                         color=['red' if e > 0 else 'blue' for e in exponents])
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
            ax.set_ylabel('Lyapunov Exponent λ₁')
            ax.set_title('Chaos Comparison - Lyapunov Exponents', fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Add value labels on bars
            for i, (bar, exp) in enumerate(zip(bars, exponents)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{exp:.4f}', ha='center', va='bottom')

            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    print(f"\nComparison report saved to {pdf_file}")
    return str(pdf_file)


if __name__ == "__main__":
    # Example usage
    print("Chaos Reporter - Example Usage\n")
    print("This module provides automated chaos analysis.")
    print("Import it and use ChaosReporter.generate_full_report() on any attractor!")
