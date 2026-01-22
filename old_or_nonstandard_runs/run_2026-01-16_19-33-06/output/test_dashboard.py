"""
Test Suite for Chaos Dashboard

Comprehensive tests for the unified chaos exploration dashboard, ensuring all
visualization and analysis features work correctly.

Author: Alice
Date: January 2026
"""

import unittest
import numpy as np
from chaos_dashboard import ChaosExplorer, AttractorConfig


class TestChaosExplorer(unittest.TestCase):
    """Test the ChaosExplorer dashboard functionality."""

    def setUp(self):
        """Initialize explorer for each test."""
        self.explorer = ChaosExplorer()

    def test_initialization(self):
        """Test that explorer initializes with all attractors."""
        self.assertIn('lorenz', self.explorer.attractors)
        self.assertIn('rossler', self.explorer.attractors)
        self.assertIn('thomas', self.explorer.attractors)

        # Check each has required attributes
        for name, config in self.explorer.attractors.items():
            self.assertIsInstance(config, AttractorConfig)
            self.assertIsInstance(config.default_state, list)
            self.assertIsInstance(config.default_params, dict)
            self.assertEqual(len(config.default_state), 3)

    def test_lorenz_simulation(self):
        """Test Lorenz attractor simulation."""
        trajectory = self.explorer.simulate('lorenz', t_max=10.0)

        # Check shape
        self.assertEqual(trajectory.shape[1], 3)
        self.assertGreater(len(trajectory), 100)

        # Check that trajectory is bounded (Lorenz stays in finite region)
        self.assertTrue(np.all(np.abs(trajectory) < 100))

        # Check continuity
        differences = np.diff(trajectory, axis=0)
        max_jump = np.max(np.abs(differences))
        self.assertLess(max_jump, 5.0)  # No huge jumps

    def test_rossler_simulation(self):
        """Test Rössler attractor simulation."""
        trajectory = self.explorer.simulate('rossler', t_max=50.0)

        # Check shape
        self.assertEqual(trajectory.shape[1], 3)

        # Rössler should be bounded
        self.assertTrue(np.all(np.abs(trajectory) < 50))

        # Check continuity
        differences = np.diff(trajectory, axis=0)
        max_jump = np.max(np.abs(differences))
        self.assertLess(max_jump, 2.0)

    def test_thomas_simulation(self):
        """Test Thomas attractor simulation."""
        trajectory = self.explorer.simulate('thomas', t_max=100.0)

        # Check shape
        self.assertEqual(trajectory.shape[1], 3)

        # Thomas has trigonometric coupling, so should be bounded by ~3
        self.assertTrue(np.all(np.abs(trajectory) < 5))

        # Check continuity
        differences = np.diff(trajectory, axis=0)
        max_jump = np.max(np.abs(differences))
        self.assertLess(max_jump, 1.0)

    def test_custom_parameters(self):
        """Test simulation with custom parameters."""
        # Lorenz with different rho
        params = {'sigma': 10.0, 'beta': 8/3, 'rho': 15.0}
        trajectory = self.explorer.simulate('lorenz', params=params, t_max=10.0)

        self.assertEqual(trajectory.shape[1], 3)
        self.assertGreater(len(trajectory), 50)

    def test_custom_initial_state(self):
        """Test simulation with custom initial conditions."""
        initial = [5.0, 5.0, 5.0]
        trajectory = self.explorer.simulate('lorenz', initial_state=initial, t_max=10.0)

        # First point should be close to initial state
        np.testing.assert_array_almost_equal(trajectory[0], initial, decimal=1)

    def test_butterfly_effect_divergence(self):
        """Test that nearby trajectories diverge exponentially."""
        # Two very close initial conditions
        state1 = [1.0, 1.0, 1.0]
        state2 = [1.0 + 1e-8, 1.0, 1.0]

        traj1 = self.explorer.simulate('lorenz', initial_state=state1, t_max=15.0)
        traj2 = self.explorer.simulate('lorenz', initial_state=state2, t_max=15.0)

        # Calculate divergence
        divergence = np.linalg.norm(traj1 - traj2, axis=1)

        # Initially should be very close
        self.assertLess(divergence[0], 1e-7)

        # Should diverge significantly by the end
        self.assertGreater(divergence[-1], 0.1)

        # Check for exponential growth
        # In log space, exponential growth appears linear
        # Sample middle portion to avoid transients
        mid_start = len(divergence) // 3
        mid_end = 2 * len(divergence) // 3
        log_divergence = np.log(divergence[mid_start:mid_end] + 1e-10)

        # Fit linear trend
        x = np.arange(len(log_divergence))
        coeffs = np.polyfit(x, log_divergence, 1)
        slope = coeffs[0]

        # Slope should be positive (exponential growth)
        self.assertGreater(slope, 0)

    def test_parameter_ranges(self):
        """Test that parameter ranges are properly defined."""
        for name, config in self.explorer.attractors.items():
            for param_name, param_value in config.default_params.items():
                self.assertIn(param_name, config.param_ranges)

                min_val, max_val = config.param_ranges[param_name]
                self.assertLess(min_val, max_val)

                # Default value should be within range
                self.assertGreaterEqual(param_value, min_val)
                self.assertLessEqual(param_value, max_val)

    def test_equation_functions(self):
        """Test that equation functions return correct shapes."""
        state = [1.0, 1.0, 1.0]
        t = 0.0

        # Lorenz
        derivs = self.explorer.lorenz_equations(t, state, sigma=10, beta=8/3, rho=28)
        self.assertEqual(len(derivs), 3)
        self.assertTrue(all(isinstance(x, (int, float, np.number)) for x in derivs))

        # Rössler
        derivs = self.explorer.rossler_equations(t, state, a=0.2, b=0.2, c=5.7)
        self.assertEqual(len(derivs), 3)

        # Thomas
        derivs = self.explorer.thomas_equations(t, state, b=0.208)
        self.assertEqual(len(derivs), 3)

    def test_thomas_symmetry(self):
        """Test Thomas attractor's cyclical symmetry property."""
        # If (x,y,z) is a solution, then (y,z,x) should also be a solution
        state1 = [1.0, 2.0, 3.0]
        state2 = [2.0, 3.0, 1.0]  # Rotated

        b = 0.208
        t = 0.0

        # Compute derivatives
        derivs1 = self.explorer.thomas_equations(t, state1, b)
        derivs2 = self.explorer.thomas_equations(t, state2, b)

        # derivs2 should be rotated version of derivs1
        expected_derivs2 = [derivs1[1], derivs1[2], derivs1[0]]

        np.testing.assert_array_almost_equal(derivs2, expected_derivs2, decimal=10)

    def test_create_3d_plot(self):
        """Test 3D plot creation returns valid figure."""
        fig = self.explorer.create_3d_plot('lorenz')

        # Check that figure has data
        self.assertGreater(len(fig.data), 0)

        # Check that first trace is 3D scatter
        trace = fig.data[0]
        self.assertIsNotNone(trace.x)
        self.assertIsNotNone(trace.y)
        self.assertIsNotNone(trace.z)

        # Check arrays are non-empty
        self.assertGreater(len(trace.x), 0)
        self.assertGreater(len(trace.y), 0)
        self.assertGreater(len(trace.z), 0)

    def test_create_comparison_plot(self):
        """Test multi-system comparison plot."""
        fig = self.explorer.create_comparison_plot()

        # Should have three traces (one per attractor)
        self.assertEqual(len(fig.data), 3)

        # Each trace should be 3D
        for trace in fig.data:
            self.assertIsNotNone(trace.x)
            self.assertIsNotNone(trace.y)
            self.assertIsNotNone(trace.z)

    def test_create_butterfly_effect_plot(self):
        """Test butterfly effect visualization."""
        fig = self.explorer.create_butterfly_effect_plot('lorenz', t_max=10.0)

        # Should have multiple traces (two trajectories + divergence plot)
        self.assertGreater(len(fig.data), 2)

    def test_parameter_sensitivity_plot(self):
        """Test parameter sensitivity visualization."""
        fig = self.explorer.create_parameter_sensitivity_plot(
            'lorenz',
            'rho',
            values=[20, 24, 28, 32, 36]
        )

        # Should have one trace per parameter value
        self.assertEqual(len(fig.data), 5)

    def test_summary_report_generation(self):
        """Test that summary report is generated correctly."""
        report = self.explorer.generate_summary_report()

        # Check it's a non-empty string
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 100)

        # Check it contains key information
        self.assertIn('Lorenz', report)
        self.assertIn('Rössler', report)
        self.assertIn('Thomas', report)
        self.assertIn('Parameters', report)

    def test_different_colorscales(self):
        """Test that different colorscales can be applied."""
        colorscales = ['Viridis', 'Plasma', 'Cividis', 'Inferno']

        for colorscale in colorscales:
            fig = self.explorer.create_3d_plot('lorenz', colorscale=colorscale)
            self.assertIsNotNone(fig)
            self.assertGreater(len(fig.data), 0)

    def test_axes_visibility(self):
        """Test axes can be shown or hidden."""
        # With axes
        fig_with_axes = self.explorer.create_3d_plot('lorenz', show_axes=True)
        self.assertIsNotNone(fig_with_axes)

        # Without axes
        fig_no_axes = self.explorer.create_3d_plot('lorenz', show_axes=False)
        self.assertIsNotNone(fig_no_axes)

    def test_edge_case_short_integration(self):
        """Test very short integration time."""
        trajectory = self.explorer.simulate('lorenz', t_max=1.0)

        # Should still produce valid trajectory
        self.assertEqual(trajectory.shape[1], 3)
        self.assertGreater(len(trajectory), 10)

    def test_edge_case_extreme_parameters(self):
        """Test with extreme parameter values."""
        # Very low rho (should converge to fixed point)
        params_low = {'sigma': 10.0, 'beta': 8/3, 'rho': 1.0}
        trajectory_low = self.explorer.simulate('lorenz', params=params_low, t_max=20.0)

        self.assertEqual(trajectory_low.shape[1], 3)
        self.assertTrue(np.all(np.isfinite(trajectory_low)))

    def test_attractor_stays_on_attractor(self):
        """Test that trajectory converges to and stays on attractor."""
        # Run for long time
        trajectory = self.explorer.simulate('lorenz', t_max=100.0)

        # Split into early and late portions
        early = trajectory[:1000]
        late = trajectory[-1000:]

        # Statistics should stabilize
        # (standard deviation of coordinates should be similar)
        early_std = np.std(early, axis=0)
        late_std = np.std(late, axis=0)

        # Should be within 50% of each other (not a strict test, but reasonable)
        ratio = late_std / (early_std + 1e-10)
        self.assertTrue(np.all(ratio > 0.5))
        self.assertTrue(np.all(ratio < 2.0))


class TestAttractorConfig(unittest.TestCase):
    """Test the AttractorConfig dataclass."""

    def test_config_creation(self):
        """Test creating a config object."""
        config = AttractorConfig(
            name='test',
            display_name='Test System',
            default_state=[1, 2, 3],
            default_params={'a': 1.0, 'b': 2.0},
            param_ranges={'a': (0, 2), 'b': (1, 3)},
            integration_time=100.0,
            time_step=0.01,
            description='A test system'
        )

        self.assertEqual(config.name, 'test')
        self.assertEqual(config.display_name, 'Test System')
        self.assertEqual(config.default_state, [1, 2, 3])

    def test_config_serialization(self):
        """Test that config can be converted to dict."""
        explorer = ChaosExplorer()
        config = explorer.attractors['lorenz']

        config_dict = asdict(config)

        self.assertIsInstance(config_dict, dict)
        self.assertIn('name', config_dict)
        self.assertIn('default_params', config_dict)


def run_tests():
    """Run the test suite and display results."""
    print("\n" + "="*70)
    print("CHAOS DASHBOARD TEST SUITE")
    print("="*70 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestChaosExplorer))
    suite.addTests(loader.loadTestsFromTestCase(TestAttractorConfig))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
