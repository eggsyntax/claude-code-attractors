"""
Test suite for the Aizawa attractor implementation.

This test suite validates the correctness of the Aizawa attractor implementation
following the TDD principles from CLAUDE.md. Tests cover:
- Mathematical correctness of derivatives
- Trajectory generation and properties
- Parameter management
- Edge cases and error handling
- Butterfly effect demonstration
- Integration with the analysis framework

Author: Bob
Date: January 2026
Part of the Alice & Bob Chaotic Attractor Toolkit
"""

import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal
from aizawa import AizawaAttractor


class TestAizawaInitialization:
    """Tests for Aizawa attractor initialization."""

    def test_default_initialization(self):
        """Test initialization with default parameters."""
        aizawa = AizawaAttractor()
        assert aizawa.parameters['a'] == 0.95
        assert aizawa.parameters['b'] == 0.7
        assert aizawa.parameters['c'] == 0.6
        assert aizawa.parameters['d'] == 3.5
        assert aizawa.parameters['e'] == 0.25
        assert aizawa.parameters['f'] == 0.1
        assert len(aizawa.initial_state) == 3

    def test_custom_parameters(self):
        """Test initialization with custom parameters."""
        custom_params = {'a': 0.8, 'c': 0.5, 'd': 3.0}
        aizawa = AizawaAttractor(**custom_params)
        assert aizawa.parameters['a'] == 0.8
        assert aizawa.parameters['b'] == 0.7  # default
        assert aizawa.parameters['c'] == 0.5
        assert aizawa.parameters['d'] == 3.0

    def test_custom_initial_state(self):
        """Test initialization with custom initial state."""
        custom_state = np.array([1.0, 2.0, 3.0])
        aizawa = AizawaAttractor(initial_state=custom_state)
        assert_array_equal(aizawa.initial_state, custom_state)

    def test_dimension(self):
        """Test that dimension is correctly set to 3."""
        aizawa = AizawaAttractor()
        assert aizawa.dimension == 3


class TestAizawaDerivatives:
    """Tests for derivative calculations."""

    def test_derivatives_shape(self):
        """Test that derivatives return correct shape."""
        aizawa = AizawaAttractor()
        state = np.array([0.1, 0.0, 0.0])
        derivs = aizawa.derivatives(state, 0.0)
        assert derivs.shape == (3,)

    def test_derivatives_at_initial_state(self):
        """Test derivative values at default initial state."""
        aizawa = AizawaAttractor()
        state = np.array([0.1, 0.0, 0.0])
        derivs = aizawa.derivatives(state, 0.0)

        # Manually compute expected values
        # dx/dt = (z - b) * x - d * y = (0 - 0.7) * 0.1 - 3.5 * 0 = -0.07
        # dy/dt = d * x + (z - b) * y = 3.5 * 0.1 + (0 - 0.7) * 0 = 0.35
        # dz/dt = c + a * z - (z^3)/3 - (x^2 + y^2) * (1 + e * z) + f * z * x^3
        #       = 0.6 + 0.95 * 0 - 0 - (0.01 + 0) * 1 + 0 = 0.59

        assert_array_almost_equal(derivs[0], -0.07, decimal=6)
        assert_array_almost_equal(derivs[1], 0.35, decimal=6)
        assert_array_almost_equal(derivs[2], 0.59, decimal=6)

    def test_derivatives_at_origin(self):
        """Test derivatives at origin."""
        aizawa = AizawaAttractor()
        state = np.array([0.0, 0.0, 0.0])
        derivs = aizawa.derivatives(state, 0.0)

        # At origin:
        # dx/dt = (0 - 0.7) * 0 - 3.5 * 0 = 0
        # dy/dt = 3.5 * 0 + (0 - 0.7) * 0 = 0
        # dz/dt = 0.6 + 0.95 * 0 - 0 - 0 * 1 + 0 = 0.6

        assert_array_almost_equal(derivs[0], 0.0, decimal=10)
        assert_array_almost_equal(derivs[1], 0.0, decimal=10)
        assert_array_almost_equal(derivs[2], 0.6, decimal=10)

    def test_derivatives_nonlinear_terms(self):
        """Test that nonlinear terms (z^3, x^3) work correctly."""
        aizawa = AizawaAttractor()
        state = np.array([1.0, 1.0, 2.0])
        derivs = aizawa.derivatives(state, 0.0)

        # Verify derivatives are computed (non-zero)
        assert derivs[0] != 0.0
        assert derivs[1] != 0.0
        assert derivs[2] != 0.0

        # Manually compute dz/dt to verify nonlinear terms
        # dz/dt = 0.6 + 0.95*2 - 8/3 - 2*(1 + 0.25*2) + 0.1*2*1 = 0.6 + 1.9 - 2.667 - 3.0 + 0.2
        expected_dz = 0.6 + 1.9 - 8.0/3.0 - 2.0 * (1 + 0.5) + 0.2
        assert_array_almost_equal(derivs[2], expected_dz, decimal=6)


class TestAizawaTrajectory:
    """Tests for trajectory generation."""

    def test_trajectory_generation(self):
        """Test basic trajectory generation."""
        aizawa = AizawaAttractor()
        trajectory = aizawa.generate_trajectory(t_span=(0, 100), n_points=1000)
        assert trajectory.shape == (1000, 3)

    def test_trajectory_bounded(self):
        """Test that trajectories remain bounded (no explosion to infinity)."""
        aizawa = AizawaAttractor()
        trajectory = aizawa.generate_trajectory(t_span=(0, 500), n_points=5000)

        # Aizawa attractor should stay within reasonable bounds
        assert np.all(np.abs(trajectory) < 50), "Trajectory exploded to infinity"

        # More typical bounds (less strict)
        x_range = trajectory[:, 0].max() - trajectory[:, 0].min()
        y_range = trajectory[:, 1].max() - trajectory[:, 1].min()
        z_range = trajectory[:, 2].max() - trajectory[:, 2].min()

        assert 0.1 < x_range < 20, f"Unexpected X range: {x_range}"
        assert 0.1 < y_range < 20, f"Unexpected Y range: {y_range}"
        assert 0.1 < z_range < 20, f"Unexpected Z range: {z_range}"

    def test_trajectory_different_lengths(self):
        """Test trajectory generation with different lengths."""
        aizawa = AizawaAttractor()

        for n_points in [100, 500, 1000, 5000]:
            trajectory = aizawa.generate_trajectory(t_span=(0, 100), n_points=n_points)
            assert trajectory.shape == (n_points, 3)

    def test_trajectory_reproducibility(self):
        """Test that same initial conditions produce same trajectory."""
        aizawa1 = AizawaAttractor(initial_state=np.array([0.1, 0.0, 0.0]))
        aizawa2 = AizawaAttractor(initial_state=np.array([0.1, 0.0, 0.0]))

        traj1 = aizawa1.generate_trajectory(t_span=(0, 50), n_points=500)
        traj2 = aizawa2.generate_trajectory(t_span=(0, 50), n_points=500)

        assert_array_almost_equal(traj1, traj2, decimal=10)

    def test_trajectory_sensitivity(self):
        """Test sensitive dependence on initial conditions."""
        aizawa1 = AizawaAttractor(initial_state=np.array([0.1, 0.0, 0.0]))
        aizawa2 = AizawaAttractor(initial_state=np.array([0.100001, 0.0, 0.0]))

        traj1 = aizawa1.generate_trajectory(t_span=(0, 500), n_points=5000)
        traj2 = aizawa2.generate_trajectory(t_span=(0, 500), n_points=5000)

        # Should start close
        initial_dist = np.linalg.norm(traj1[0] - traj2[0])
        assert initial_dist < 1e-4

        # Should diverge significantly
        final_dist = np.linalg.norm(traj1[-1] - traj2[-1])
        assert final_dist > 0.1, "Trajectories should diverge (butterfly effect)"


class TestAizawaParameters:
    """Tests for parameter management."""

    def test_update_parameters(self):
        """Test parameter updates."""
        aizawa = AizawaAttractor()
        aizawa.update_parameters({'a': 0.8, 'd': 3.0})

        assert aizawa.parameters['a'] == 0.8
        assert aizawa.parameters['d'] == 3.0
        assert aizawa.parameters['b'] == 0.7  # unchanged

    def test_parameter_recommendations(self):
        """Test that parameter recommendations are valid."""
        recommendations = AizawaAttractor.parameter_recommendations()

        assert 'chaotic' in recommendations
        assert 'alternative_chaotic' in recommendations
        assert 'more_symmetric' in recommendations
        assert 'weaker_chaos' in recommendations

        # Each recommendation should have all required parameters
        for regime, params in recommendations.items():
            assert 'a' in params
            assert 'b' in params
            assert 'c' in params
            assert 'd' in params
            assert 'e' in params
            assert 'f' in params

    def test_different_parameter_regimes(self):
        """Test trajectories with different parameter regimes."""
        recommendations = AizawaAttractor.parameter_recommendations()

        for regime, params in recommendations.items():
            aizawa = AizawaAttractor(**params)
            trajectory = aizawa.generate_trajectory(t_span=(0, 100), n_points=1000)

            # Should generate valid trajectories
            assert trajectory.shape == (1000, 3)
            assert np.all(np.isfinite(trajectory)), f"Invalid trajectory for {regime}"
            assert np.all(np.abs(trajectory) < 100), f"Trajectory exploded for {regime}"


class TestAizawaButterflyEffect:
    """Tests for butterfly effect demonstration."""

    def test_butterfly_effect_demo(self):
        """Test butterfly effect demonstration generates two trajectories."""
        aizawa = AizawaAttractor()
        traj1, traj2 = aizawa.generate_butterfly_effect_demo()

        assert traj1.shape == traj2.shape
        assert traj1.shape[1] == 3

    def test_butterfly_effect_divergence(self):
        """Test that butterfly effect demo shows divergence."""
        aizawa = AizawaAttractor()
        traj1, traj2 = aizawa.generate_butterfly_effect_demo(
            t_span=(0, 500),
            n_points=5000,
            perturbation=1e-8
        )

        # Compute distances over time
        distances = np.linalg.norm(traj1 - traj2, axis=1)

        # Should start very close
        assert distances[0] < 1e-6, "Initial conditions should be very close"

        # Should eventually diverge significantly
        assert distances[-1] > 0.1, "Trajectories should diverge significantly"

        # Should show general increasing trend (some fluctuation is okay)
        # Compare first quarter to last quarter
        first_quarter_avg = np.mean(distances[:len(distances)//4])
        last_quarter_avg = np.mean(distances[3*len(distances)//4:])
        assert last_quarter_avg > first_quarter_avg * 10, "Should show exponential divergence"

    def test_butterfly_effect_custom_perturbation(self):
        """Test butterfly effect with custom perturbation size."""
        aizawa = AizawaAttractor()
        traj1, traj2 = aizawa.generate_butterfly_effect_demo(perturbation=1e-5)

        initial_dist = np.linalg.norm(traj1[0] - traj2[0])
        # Should be on the order of the perturbation (3D, so ~sqrt(3) * perturbation)
        assert 1e-6 < initial_dist < 1e-4


class TestAizawaIntegration:
    """Tests for integration with other toolkit components."""

    def test_get_info(self):
        """Test that get_info returns complete information."""
        aizawa = AizawaAttractor()
        info = aizawa.get_info()

        assert info['type'] == 'Aizawa Attractor'
        assert info['dimension'] == 3
        assert 'a' in info['parameters']
        assert 'initial_state' in info
        assert len(info['initial_state']) == 3

    def test_integration_methods(self):
        """Test trajectory generation with different integration methods."""
        aizawa = AizawaAttractor()

        for method in ['RK45', 'RK23', 'DOP853']:
            trajectory = aizawa.generate_trajectory(
                t_span=(0, 100),
                n_points=1000,
                method=method
            )
            assert trajectory.shape == (1000, 3)
            assert np.all(np.isfinite(trajectory))


class TestAizawaEdgeCases:
    """Tests for edge cases and error handling."""

    def test_very_short_trajectory(self):
        """Test generation of very short trajectories."""
        aizawa = AizawaAttractor()
        trajectory = aizawa.generate_trajectory(t_span=(0, 1), n_points=10)
        assert trajectory.shape == (10, 3)

    def test_very_long_trajectory(self):
        """Test generation of long trajectories."""
        aizawa = AizawaAttractor()
        trajectory = aizawa.generate_trajectory(t_span=(0, 1000), n_points=10000)
        assert trajectory.shape == (10000, 3)
        assert np.all(np.isfinite(trajectory))

    def test_extreme_initial_conditions(self):
        """Test with extreme initial conditions."""
        # Large initial condition
        aizawa = AizawaAttractor(initial_state=np.array([10.0, 10.0, 10.0]))
        trajectory = aizawa.generate_trajectory(t_span=(0, 100), n_points=1000)
        assert np.all(np.isfinite(trajectory))

        # Small initial condition
        aizawa = AizawaAttractor(initial_state=np.array([0.001, 0.001, 0.001]))
        trajectory = aizawa.generate_trajectory(t_span=(0, 100), n_points=1000)
        assert np.all(np.isfinite(trajectory))


class TestAizawaComparison:
    """Tests comparing Aizawa to other attractors."""

    def test_aizawa_differs_from_lorenz(self):
        """
        Test that Aizawa produces different dynamics than Lorenz.

        This is a sanity check that we haven't accidentally implemented
        the same system twice.
        """
        from lorenz import LorenzAttractor

        aizawa = AizawaAttractor(initial_state=np.array([0.1, 0.0, 0.0]))
        lorenz = LorenzAttractor(initial_state=np.array([0.1, 0.0, 0.0]))

        aizawa_traj = aizawa.generate_trajectory(t_span=(0, 50), n_points=500)
        lorenz_traj = lorenz.generate_trajectory(t_span=(0, 50), n_points=500)

        # Trajectories should be significantly different
        diff = np.linalg.norm(aizawa_traj - lorenz_traj)
        assert diff > 10, "Aizawa and Lorenz should produce different trajectories"

    def test_aizawa_differs_from_rossler(self):
        """Test that Aizawa produces different dynamics than Rössler."""
        from rossler import RosslerAttractor

        aizawa = AizawaAttractor(initial_state=np.array([0.1, 0.0, 0.0]))
        rossler = RosslerAttractor(initial_state=np.array([0.1, 0.0, 0.0]))

        aizawa_traj = aizawa.generate_trajectory(t_span=(0, 50), n_points=500)
        rossler_traj = rossler.generate_trajectory(t_span=(0, 50), n_points=500)

        # Trajectories should be significantly different
        diff = np.linalg.norm(aizawa_traj - rossler_traj)
        assert diff > 10, "Aizawa and Rössler should produce different trajectories"


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, '-v'])
