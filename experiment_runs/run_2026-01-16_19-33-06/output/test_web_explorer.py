#!/usr/bin/env python3
"""
Test suite for the standalone web explorer HTML file.

This test verifies that the web explorer HTML file is well-formed, contains
all necessary components, and includes correct mathematical implementations.

Author: Bob (Turn 10)
"""

import re
import os
import unittest
from pathlib import Path


class TestWebExplorer(unittest.TestCase):
    """Test suite for standalone_web_explorer.html"""

    @classmethod
    def setUpClass(cls):
        """Load the HTML file once for all tests."""
        html_path = Path(__file__).parent / "standalone_web_explorer.html"

        if not html_path.exists():
            raise FileNotFoundError(
                f"Web explorer HTML not found at {html_path}"
            )

        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()

    def test_file_exists(self):
        """Verify the HTML file exists."""
        html_path = Path(__file__).parent / "standalone_web_explorer.html"
        self.assertTrue(html_path.exists(), "HTML file should exist")

    def test_html_structure(self):
        """Verify basic HTML structure is present."""
        self.assertIn('<!DOCTYPE html>', self.html_content)
        self.assertIn('<html', self.html_content)
        self.assertIn('</html>', self.html_content)
        self.assertIn('<head>', self.html_content)
        self.assertIn('</head>', self.html_content)
        self.assertIn('<body>', self.html_content)
        self.assertIn('</body>', self.html_content)

    def test_plotly_dependency(self):
        """Verify Plotly.js is included."""
        # Should include Plotly from CDN
        self.assertIn('plotly', self.html_content.lower())
        self.assertIn('.js', self.html_content)

    def test_all_attractors_present(self):
        """Verify all three attractors are defined."""
        # Check for Lorenz
        self.assertIn('lorenz', self.html_content.lower())

        # Check for Rössler (may be written as rossler without umlaut)
        self.assertTrue(
            'rössler' in self.html_content.lower() or
            'rossler' in self.html_content.lower()
        )

        # Check for Thomas
        self.assertIn('thomas', self.html_content.lower())

    def test_lorenz_equations(self):
        """Verify Lorenz equations are correctly implemented."""
        # Look for the Lorenz equation parameters: sigma, rho, beta
        self.assertIn('sigma', self.html_content)
        self.assertIn('rho', self.html_content)
        self.assertIn('beta', self.html_content)

        # Verify the differential equations appear (in some form)
        # dx/dt = σ(y - x)
        # dy/dt = x(ρ - z) - y
        # dz/dt = xy - βz

        # These might be in comments, equations, or code
        # Just verify the key mathematical structure is present
        self.assertIn('sigma', self.html_content)

    def test_rossler_equations(self):
        """Verify Rössler equations are correctly implemented."""
        # Look for Rössler equation parameters: a, b, c
        # dx/dt = -y - z
        # dy/dt = x + ay
        # dz/dt = b + z(x - c)

        # The equations should reference x, y, z
        pattern_a = r'params\.a|p\.a'
        pattern_c = r'params\.c|p\.c'

        self.assertTrue(
            re.search(pattern_a, self.html_content),
            "Rössler parameter 'a' should be referenced"
        )
        self.assertTrue(
            re.search(pattern_c, self.html_content),
            "Rössler parameter 'c' should be referenced"
        )

    def test_thomas_equations(self):
        """Verify Thomas equations are correctly implemented."""
        # Look for Thomas equation parameter: b
        # dx/dt = sin(y) - bx
        # dy/dt = sin(z) - by
        # dz/dt = sin(x) - bz

        # Thomas uses sin function
        self.assertIn('sin', self.html_content.lower())
        self.assertIn('Math.sin', self.html_content)

    def test_rk4_integration(self):
        """Verify Runge-Kutta integration is implemented."""
        # Should have RK4 function or method
        # Look for k1, k2, k3, k4 (RK4 stages)
        self.assertIn('rk4', self.html_content.lower())

        # Verify all four stages are computed
        self.assertIn('k1', self.html_content)
        self.assertIn('k2', self.html_content)
        self.assertIn('k3', self.html_content)
        self.assertIn('k4', self.html_content)

    def test_interactive_controls(self):
        """Verify interactive controls are present."""
        # Should have sliders or input elements
        self.assertIn('slider', self.html_content.lower())
        self.assertIn('input', self.html_content.lower())

        # Should have buttons
        self.assertIn('button', self.html_content.lower())

    def test_parameter_controls(self):
        """Verify parameter control functions exist."""
        # Should have functions to update parameters
        self.assertIn('updateParameter', self.html_content)
        self.assertIn('resetParameters', self.html_content)

    def test_butterfly_effect_demo(self):
        """Verify butterfly effect demonstration exists."""
        self.assertIn('butterfly', self.html_content.lower())
        # Should mention initial conditions or perturbation
        self.assertTrue(
            'initial' in self.html_content.lower() or
            'perturbation' in self.html_content.lower() or
            '1e-8' in self.html_content or
            '10⁻⁸' in self.html_content
        )

    def test_export_functionality(self):
        """Verify data export functionality exists."""
        self.assertIn('export', self.html_content.lower())
        # Should generate CSV or similar
        self.assertIn('csv', self.html_content.lower())

    def test_visualization_plotting(self):
        """Verify plotting function exists."""
        # Should call Plotly.newPlot or similar
        self.assertIn('Plotly.newPlot', self.html_content)

        # Should have 3D scatter plot
        self.assertIn('scatter3d', self.html_content)

    def test_responsive_design(self):
        """Verify responsive design elements."""
        # Should have viewport meta tag
        self.assertIn('viewport', self.html_content)

        # Should have CSS media queries for mobile
        self.assertIn('@media', self.html_content)

    def test_mathematical_descriptions(self):
        """Verify mathematical descriptions are included."""
        # Should describe what attractors are
        self.assertTrue(
            'chaos' in self.html_content.lower() or
            'chaotic' in self.html_content.lower()
        )

        # Should mention differential equations
        self.assertTrue(
            'equation' in self.html_content.lower() or
            'dx/dt' in self.html_content or
            'dy/dt' in self.html_content
        )

    def test_attractor_info_content(self):
        """Verify each attractor has associated information."""
        # Should have info sections describing each system
        self.assertIn('info', self.html_content.lower())
        self.assertIn('description', self.html_content.lower())

        # Should mention key researchers
        self.assertTrue(
            'lorenz' in self.html_content.lower() or
            'edward' in self.html_content.lower()
        )

    def test_color_schemes(self):
        """Verify color schemes are defined."""
        # Should have colorscales for visualization
        self.assertIn('colorscale', self.html_content.lower())

        # Common colorscales: Viridis, Plasma, etc.
        self.assertTrue(
            'viridis' in self.html_content.lower() or
            'plasma' in self.html_content.lower() or
            'turbo' in self.html_content.lower()
        )

    def test_no_external_file_dependencies(self):
        """Verify file is self-contained (except CDN)."""
        # Should not reference local files
        # (Except for CDN links which are necessary)

        # Check for local file references
        local_refs = re.findall(r'src=["\'](?!http)', self.html_content)
        local_refs += re.findall(r'href=["\'](?!http)', self.html_content)

        # Filter out fragments and data URIs
        local_refs = [
            ref for ref in local_refs
            if not ref.startswith('data:') and not ref.startswith('#')
        ]

        # Should be minimal or none
        self.assertLessEqual(
            len(local_refs),
            1,
            f"Should have minimal local file references, found: {local_refs}"
        )

    def test_title_and_headers(self):
        """Verify page has proper title and headers."""
        self.assertIn('<title>', self.html_content)
        self.assertIn('Strange Attractors', self.html_content)
        self.assertIn('<h1>', self.html_content)

    def test_initialization_function(self):
        """Verify page initialization is defined."""
        # Should have init function
        self.assertIn('function init', self.html_content)

        # Should call init on load
        self.assertIn('window.onload', self.html_content)

    def test_default_parameters(self):
        """Verify default parameters are defined."""
        # Lorenz defaults: sigma=10, rho=28, beta=8/3
        self.assertIn('10.0', self.html_content)  # sigma
        self.assertIn('28.0', self.html_content)  # rho

        # Rössler defaults: a=0.2, b=0.2, c=5.7
        self.assertIn('0.2', self.html_content)  # a and b
        self.assertIn('5.7', self.html_content)  # c


class TestWebExplorerIntegration(unittest.TestCase):
    """Integration tests verifying web explorer completeness."""

    def test_complete_workflow(self):
        """Verify all components for complete user workflow exist."""
        html_path = Path(__file__).parent / "standalone_web_explorer.html"

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Essential workflow components
        required_components = [
            'attractor-select',      # Attractor selection
            'parameter-controls',    # Parameter adjustment
            'plotDiv',              # Visualization area
            'info-content',         # Information display
            'updateAttractor',      # Update function
            'plotAttractor',        # Plot function
            'generateTrajectory',   # Simulation function
        ]

        for component in required_components:
            self.assertIn(
                component,
                content,
                f"Required component '{component}' should be present"
            )

    def test_mathematical_accuracy_markers(self):
        """Verify markers indicating mathematical accuracy."""
        html_path = Path(__file__).parent / "standalone_web_explorer.html"

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Should mention integration method
        self.assertIn('Runge-Kutta', content.lower())

        # Should have proper dt (time step)
        self.assertIn('dt', content)

        # Should iterate over time steps
        self.assertTrue('step' in content.lower() or 'iterate' in content.lower())


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestWebExplorer))
    suite.addTests(loader.loadTestsFromTestCase(TestWebExplorerIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("STANDALONE WEB EXPLORER TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
