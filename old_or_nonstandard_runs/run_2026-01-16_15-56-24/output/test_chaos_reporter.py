"""
Tests for Chaos Reporter

Following TDD principles from CLAUDE.md:
- Test all core functionality
- Validate report generation
- Check data integrity
- Test edge cases
"""

import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from chaos_reporter import ChaosReporter, compare_attractors
from lorenz import LorenzAttractor
from rossler import RosslerAttractor


class TestChaosReporter:
    """Test suite for ChaosReporter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reporter = ChaosReporter()
        self.lorenz = LorenzAttractor()
        self.rossler = RosslerAttractor()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary files."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_reporter_initialization(self):
        """Test that reporter initializes correctly."""
        assert self.reporter.visualizer is not None
        assert isinstance(self.reporter.results, dict)
        assert len(self.reporter.results) == 0

    def test_analyze_attractor_basic(self):
        """Test basic attractor analysis."""
        results = self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 10),
            n_points=1000,
            include_poincare=False,
            include_lyapunov=False,
            include_divergence=False
        )

        assert 'attractor_info' in results
        assert 'trajectory' in results
        assert results['trajectory'].shape == (1000, 3)
        assert results['attractor_info']['type'] == 'Lorenz Attractor'

    def test_analyze_with_poincare(self):
        """Test analysis including Poincaré section."""
        results = self.reporter.analyze_attractor(
            self.rossler,
            t_span=(0, 100),
            n_points=5000,
            include_poincare=True,
            include_lyapunov=False,
            include_divergence=False,
            poincare_plane='z',
            poincare_value=0.0
        )

        assert 'poincare_section' in results
        assert isinstance(results['poincare_section'], np.ndarray)
        assert len(results['poincare_section']) > 0
        assert 'return_map' in results

    def test_analyze_with_lyapunov(self):
        """Test analysis including Lyapunov exponent estimation."""
        results = self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 20),
            n_points=2000,
            include_poincare=False,
            include_lyapunov=True,
            include_divergence=False
        )

        assert 'lyapunov' in results
        lyap = results['lyapunov']
        assert 'exponent' in lyap
        assert isinstance(lyap['exponent'], float)
        assert 'convergence_data' in lyap
        assert lyap['exponent'] > 0  # Lorenz should be chaotic

    def test_analyze_with_divergence(self):
        """Test analysis including trajectory divergence."""
        results = self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 10),
            n_points=1000,
            include_poincare=False,
            include_lyapunov=False,
            include_divergence=True
        )

        assert 'divergence' in results
        assert 'divergence_trajectories' in results
        div = results['divergence']
        assert isinstance(div, np.ndarray)
        assert len(div) == 1000
        assert div[0] < div[-1]  # Should diverge

    def test_analyze_full_suite(self):
        """Test complete analysis with all features enabled."""
        results = self.reporter.analyze_attractor(
            self.rossler,
            t_span=(0, 100),
            n_points=5000,
            include_poincare=True,
            include_lyapunov=True,
            include_divergence=True
        )

        # Check all analysis components present
        assert 'trajectory' in results
        assert 'poincare_section' in results
        assert 'return_map' in results
        assert 'lyapunov' in results
        assert 'divergence' in results
        assert 'divergence_trajectories' in results

    def test_generate_text_report(self):
        """Test text report generation."""
        results = self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 20),
            n_points=2000,
            include_lyapunov=True
        )

        report = self.reporter.generate_text_report(results)

        assert isinstance(report, str)
        assert len(report) > 0
        assert 'CHAOS ANALYSIS REPORT' in report
        assert 'Lorenz Attractor' in report
        assert 'Lyapunov Exponent' in report
        assert 'λ₁' in report

    def test_text_report_interpretation(self):
        """Test that text report includes interpretation of results."""
        results = self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 20),
            n_points=2000,
            include_lyapunov=True
        )

        report = self.reporter.generate_text_report(results)

        # Should include interpretation based on Lyapunov exponent
        assert any(word in report for word in ['CHAOTIC', 'REGULAR', 'NEUTRAL'])

    def test_text_report_without_optional_analysis(self):
        """Test text report with minimal analysis."""
        results = self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 10),
            n_points=1000,
            include_poincare=False,
            include_lyapunov=False,
            include_divergence=False
        )

        report = self.reporter.generate_text_report(results)

        # Should still generate valid report
        assert isinstance(report, str)
        assert 'CHAOS ANALYSIS REPORT' in report
        assert 'Lorenz Attractor' in report

    def test_generate_visual_report_structure(self):
        """Test that visual report generation works."""
        results = self.reporter.analyze_attractor(
            self.rossler,
            t_span=(0, 50),
            n_points=3000,
            include_poincare=True,
            include_lyapunov=True,
            include_divergence=True
        )

        output_file = Path(self.temp_dir) / "test_report.pdf"

        figures = self.reporter.generate_visual_report(
            results,
            output_file=str(output_file),
            show_plots=False
        )

        # Should generate multiple figures
        assert len(figures) > 0
        assert all(isinstance(item, tuple) for item in figures)
        assert all(len(item) == 2 for item in figures)

        # PDF should be created
        assert output_file.exists()

    def test_generate_full_report(self):
        """Test complete report generation (text + visual)."""
        text_file, pdf_file = self.reporter.generate_full_report(
            self.lorenz,
            output_dir=self.temp_dir,
            t_span=(0, 20),
            n_points=2000
        )

        # Both files should be created
        assert Path(text_file).exists()
        assert Path(pdf_file).exists()

        # Files should have content
        assert Path(text_file).stat().st_size > 0
        assert Path(pdf_file).stat().st_size > 0

    def test_compare_attractors_basic(self):
        """Test basic attractor comparison."""
        comparison_file = compare_attractors(
            [self.lorenz, self.rossler],
            output_dir=self.temp_dir,
            t_span=(0, 20),
            n_points=2000,
            include_lyapunov=True
        )

        assert Path(comparison_file).exists()
        assert Path(comparison_file).stat().st_size > 0

    def test_compare_single_attractor(self):
        """Test comparison with single attractor (edge case)."""
        comparison_file = compare_attractors(
            [self.lorenz],
            output_dir=self.temp_dir,
            t_span=(0, 20),
            n_points=2000
        )

        # Should still work with single attractor
        assert Path(comparison_file).exists()

    def test_analyze_stores_results(self):
        """Test that analyze_attractor stores results in reporter."""
        assert len(self.reporter.results) == 0

        self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 10),
            n_points=1000
        )

        # Results should be stored
        assert len(self.reporter.results) > 0
        assert 'attractor_info' in self.reporter.results

    def test_custom_poincare_plane(self):
        """Test analysis with different Poincaré plane specifications."""
        # Test x-plane
        results_x = self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 20),
            n_points=2000,
            include_poincare=True,
            poincare_plane='x'
        )
        assert 'poincare_section' in results_x

        # Test y-plane
        results_y = self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 20),
            n_points=2000,
            include_poincare=True,
            poincare_plane='y'
        )
        assert 'poincare_section' in results_y

    def test_report_with_different_parameters(self):
        """Test reports for attractors with non-default parameters."""
        custom_lorenz = LorenzAttractor(
            parameters={'sigma': 5, 'rho': 20, 'beta': 2}
        )

        results = self.reporter.analyze_attractor(
            custom_lorenz,
            t_span=(0, 20),
            n_points=2000,
            include_lyapunov=True
        )

        report = self.reporter.generate_text_report(results)

        # Report should include custom parameters
        assert 'sigma = 5' in report or 'sigma=5' in report
        assert 'rho = 20' in report or 'rho=20' in report

    def test_lyapunov_interpretation_strongly_chaotic(self):
        """Test interpretation for strongly chaotic systems."""
        # Lorenz is strongly chaotic (λ₁ ≈ 0.9)
        results = self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 20),
            n_points=2000,
            include_lyapunov=True
        )

        report = self.reporter.generate_text_report(results)
        assert 'CHAOTIC' in report

    def test_lyapunov_interpretation_weakly_chaotic(self):
        """Test interpretation for weakly chaotic systems."""
        # Rössler is weakly chaotic (λ₁ ≈ 0.07)
        results = self.reporter.analyze_attractor(
            self.rossler,
            t_span=(0, 100),
            n_points=5000,
            include_lyapunov=True
        )

        report = self.reporter.generate_text_report(results)
        # Should identify as chaotic but might be weaker descriptor
        assert any(word in report for word in ['CHAOTIC', 'chaos'])

    def test_divergence_growth_rate_calculation(self):
        """Test that divergence analysis calculates growth rate."""
        results = self.reporter.analyze_attractor(
            self.lorenz,
            t_span=(0, 20),
            n_points=2000,
            include_divergence=True
        )

        report = self.reporter.generate_text_report(results)

        # Report should include growth rate and doubling time
        assert 'Growth rate' in report or 'growth rate' in report
        assert 'Doubling time' in report or 'doubling time' in report

    def test_poincare_structure_interpretation(self):
        """Test interpretation of Poincaré section structure."""
        results = self.reporter.analyze_attractor(
            self.rossler,
            t_span=(0, 100),
            n_points=5000,
            include_poincare=True,
            poincare_plane='z',
            poincare_value=0.0
        )

        report = self.reporter.generate_text_report(results)

        # Should include Poincaré section analysis
        assert 'Poincaré Section' in report or 'Poincare Section' in report
        assert 'Structure' in report or 'structure' in report

    def test_output_directory_creation(self):
        """Test that output directories are created if they don't exist."""
        new_dir = Path(self.temp_dir) / "nested" / "subdirectory"
        assert not new_dir.exists()

        text_file, pdf_file = self.reporter.generate_full_report(
            self.lorenz,
            output_dir=str(new_dir),
            t_span=(0, 10),
            n_points=1000
        )

        # Directory should be created
        assert new_dir.exists()
        assert Path(text_file).exists()
        assert Path(pdf_file).exists()


class TestReporterEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reporter = ChaosReporter()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary files."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_very_short_trajectory(self):
        """Test with very short trajectory."""
        lorenz = LorenzAttractor()
        results = self.reporter.analyze_attractor(
            lorenz,
            t_span=(0, 1),
            n_points=100,
            include_poincare=False
        )

        assert 'trajectory' in results
        assert len(results['trajectory']) == 100

    def test_no_poincare_crossings(self):
        """Test handling when Poincaré section has no crossings."""
        lorenz = LorenzAttractor()

        # Very short trajectory might not cross plane
        results = self.reporter.analyze_attractor(
            lorenz,
            t_span=(0, 0.1),
            n_points=10,
            include_poincare=True,
            poincare_plane='z',
            poincare_value=100.0  # Unrealistic value
        )

        # Should handle gracefully
        if 'poincare_section' in results:
            # If section exists, return map might not
            pass  # This is okay

    def test_report_generation_with_partial_data(self):
        """Test report generation when some analysis components are missing."""
        # Manually create partial results
        lorenz = LorenzAttractor()
        trajectory = lorenz.generate_trajectory(t_span=(0, 10), n_points=1000)

        partial_results = {
            'attractor_info': lorenz.get_info(),
            'trajectory': trajectory,
            'analysis_parameters': {'t_span': (0, 10), 'n_points': 1000}
        }

        # Should generate report without crashing
        report = self.reporter.generate_text_report(partial_results)
        assert isinstance(report, str)
        assert len(report) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
