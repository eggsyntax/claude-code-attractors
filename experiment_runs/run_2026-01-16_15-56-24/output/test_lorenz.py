"""
Tests for the Lorenz attractor implementation.

These tests verify the Lorenz system's behavior, including parameter
effects, butterfly effect demonstration, and physical correctness.
"""

import pytest
import numpy as np
from lorenz import LorenzAttractor


class TestLorenzInitialization:
    """Test Lorenz attractor initialization."""

    def test_default_initialization(self):
        """Test initialization with default parameters."""
        lorenz = LorenzAttractor()

        assert lorenz.dimension == 3
        assert lorenz.parameters['sigma'] == 10.0
        assert lorenz.parameters['rho'] == 28.0
        assert lorenz.parameters['beta'] == 8.0 / 3.0
        np.testing.assert_array_equal(
            lorenz.initial_state,
            np.array([1.0, 1.0, 1.0])
        )

    def test_custom_parameters(self):
        """Test initialization with custom parameters."""
        custom_params = {
            'sigma': 15.0,
            'rho': 30.0,
            'beta': 3.0
        }
        lorenz = LorenzAttractor(parameters=custom_params)

        assert lorenz.parameters['sigma'] == 15.0
        assert lorenz.parameters['rho'] == 30.0
        assert lorenz.parameters['beta'] == 3.0

    def test_custom_initial_state(self):
        """Test initialization with custom initial state."""
        custom_state = np.array([5.0, -3.0, 10.0])
        lorenz = LorenzAttractor(initial_state=custom_state)

        np.testing.assert_array_equal(lorenz.initial_state, custom_state)


class TestLorenzDerivatives:
    """Test the Lorenz differential equations."""

    def test_derivatives_at_equilibrium(self):
        """Test derivatives at an equilibrium point."""
        lorenz = LorenzAttractor()

        # The origin is always an equilibrium
        state = np.array([0.0, 0.0, 0.0])
        derivs = lorenz.derivatives(0, state)

        # At equilibrium, all derivatives should be zero
        np.testing.assert_allclose(derivs, np.zeros(3), atol=1e-10)

    def test_derivatives_sign(self):
        """Test that derivatives have expected signs in specific regions."""
        lorenz = LorenzAttractor()

        # At (1, 2, 1):
        # dx/dt = sigma * (y - x) = 10 * (2 - 1) = 10 > 0
        # dy/dt = x * (rho - z) - y = 1 * (28 - 1) - 2 = 25 > 0
        # dz/dt = x * y - beta * z = 1 * 2 - (8/3) * 1 = 2 - 8/3 ≈ -0.67 < 0
        state = np.array([1.0, 2.0, 1.0])
        derivs = lorenz.derivatives(0, state)

        assert derivs[0] > 0  # dx/dt > 0
        assert derivs[1] > 0  # dy/dt > 0
        assert derivs[2] < 0  # dz/dt < 0

    def test_derivatives_calculation(self):
        """Test explicit calculation of derivatives."""
        lorenz = LorenzAttractor()
        state = np.array([1.0, 2.0, 3.0])

        derivs = lorenz.derivatives(0, state)

        # Manually calculate expected values
        sigma, rho, beta = 10.0, 28.0, 8.0/3.0
        x, y, z = 1.0, 2.0, 3.0

        expected_dx = sigma * (y - x)  # 10 * (2 - 1) = 10
        expected_dy = x * (rho - z) - y  # 1 * (28 - 3) - 2 = 23
        expected_dz = x * y - beta * z  # 1 * 2 - (8/3) * 3 = -6

        np.testing.assert_allclose(
            derivs,
            [expected_dx, expected_dy, expected_dz],
            rtol=1e-10
        )


class TestLorenzTrajectory:
    """Test trajectory generation and properties."""

    def test_trajectory_shape(self):
        """Test that generated trajectory has correct shape."""
        lorenz = LorenzAttractor()
        n_points = 5000

        trajectory = lorenz.generate_trajectory(
            t_span=(0, 50),
            n_points=n_points
        )

        assert trajectory.shape == (n_points, 3)

    def test_trajectory_boundedness(self):
        """Test that trajectory stays bounded (doesn't explode to infinity)."""
        lorenz = LorenzAttractor()
        trajectory = lorenz.generate_trajectory(t_span=(0, 100), n_points=10000)

        # Lorenz attractor should stay in a bounded region
        # Typical bounds are roughly -20 to 20 for x,y and 0 to 50 for z
        assert np.all(np.abs(trajectory[:, 0]) < 30)  # x bounds
        assert np.all(np.abs(trajectory[:, 1]) < 30)  # y bounds
        assert np.all(trajectory[:, 2] > -5)  # z lower bound
        assert np.all(trajectory[:, 2] < 60)  # z upper bound

    def test_trajectory_not_constant(self):
        """Test that trajectory is not stuck at a fixed point."""
        lorenz = LorenzAttractor()
        trajectory = lorenz.generate_trajectory(t_span=(0, 50), n_points=1000)

        # Standard deviation should be significant (not stuck)
        assert np.std(trajectory[:, 0]) > 1.0
        assert np.std(trajectory[:, 1]) > 1.0
        assert np.std(trajectory[:, 2]) > 1.0

    def test_trajectory_with_different_parameters(self):
        """Test trajectory generation with different parameter regimes."""
        # Converging regime (rho < 1)
        lorenz_converging = LorenzAttractor(
            parameters={'sigma': 10.0, 'rho': 0.5, 'beta': 8.0/3.0}
        )
        traj_converging = lorenz_converging.generate_trajectory(
            t_span=(0, 50),
            n_points=1000
        )

        # Should converge toward origin
        assert np.linalg.norm(traj_converging[-1]) < np.linalg.norm(traj_converging[0])

        # Chaotic regime (rho = 28)
        lorenz_chaotic = LorenzAttractor()
        traj_chaotic = lorenz_chaotic.generate_trajectory(
            t_span=(0, 50),
            n_points=1000
        )

        # Should NOT converge to origin
        assert np.linalg.norm(traj_chaotic[-1]) > 1.0


class TestButterflyEffect:
    """Test the butterfly effect (sensitive dependence on initial conditions)."""

    def test_butterfly_effect_demo(self):
        """Test that butterfly effect demo produces diverging trajectories."""
        lorenz = LorenzAttractor()

        traj1, traj2 = lorenz.generate_butterfly_effect_demo(
            epsilon=1e-8,
            t_span=(0, 40),
            n_points=10000
        )

        # Trajectories should start very close
        distance_initial = np.linalg.norm(traj1[0] - traj2[0])
        assert distance_initial < 1e-7

        # But diverge significantly over time
        distance_final = np.linalg.norm(traj1[-1] - traj2[-1])
        assert distance_final > 1.0

        # Check divergence grows over time
        distance_mid = np.linalg.norm(traj1[len(traj1)//2] - traj2[len(traj2)//2])
        assert distance_mid > distance_initial
        assert distance_mid < distance_final

    def test_butterfly_effect_with_different_epsilon(self):
        """Test butterfly effect with different perturbation sizes."""
        lorenz = LorenzAttractor()

        # Smaller perturbation
        traj1_small, traj2_small = lorenz.generate_butterfly_effect_demo(
            epsilon=1e-10,
            t_span=(0, 30),
            n_points=5000
        )

        # Larger perturbation
        traj1_large, traj2_large = lorenz.generate_butterfly_effect_demo(
            epsilon=1e-6,
            t_span=(0, 30),
            n_points=5000
        )

        # Both should diverge, but larger epsilon starts further apart
        initial_dist_small = np.linalg.norm(traj1_small[0] - traj2_small[0])
        initial_dist_large = np.linalg.norm(traj1_large[0] - traj2_large[0])

        assert initial_dist_large > initial_dist_small

    def test_butterfly_effect_restores_initial_state(self):
        """Test that butterfly effect demo restores original initial state."""
        lorenz = LorenzAttractor()
        original_state = lorenz.initial_state.copy()

        _ = lorenz.generate_butterfly_effect_demo()

        # Should restore original state
        np.testing.assert_array_equal(lorenz.initial_state, original_state)


class TestParameterRecommendations:
    """Test parameter recommendation system."""

    def test_get_parameter_recommendations(self):
        """Test that parameter recommendations are available."""
        recommendations = LorenzAttractor.get_parameter_recommendations()

        assert 'classic' in recommendations
        assert 'pre_turbulent' in recommendations
        assert 'periodic' in recommendations

        # Each recommendation should have params and description
        for name, rec in recommendations.items():
            assert 'params' in rec
            assert 'description' in rec
            assert 'sigma' in rec['params']
            assert 'rho' in rec['params']
            assert 'beta' in rec['params']

    def test_apply_recommended_parameters(self):
        """Test applying recommended parameters."""
        lorenz = LorenzAttractor()
        recommendations = LorenzAttractor.get_parameter_recommendations()

        # Try each recommended parameter set
        for name, rec in recommendations.items():
            lorenz.update_parameters(**rec['params'])

            # Should be able to generate trajectory without error
            trajectory = lorenz.generate_trajectory(
                t_span=(0, 20),
                n_points=1000
            )

            assert trajectory.shape == (1000, 3)
            # Should stay bounded
            assert np.all(np.isfinite(trajectory))


class TestLorenzEdgeCases:
    """Test edge cases and error conditions."""

    def test_zero_parameters(self):
        """Test behavior with zero parameters."""
        # sigma=0, beta=0 should still work (though dynamics change)
        lorenz = LorenzAttractor(
            parameters={'sigma': 0.0, 'rho': 28.0, 'beta': 0.0}
        )

        trajectory = lorenz.generate_trajectory(t_span=(0, 10), n_points=100)
        assert trajectory.shape == (100, 3)
        assert np.all(np.isfinite(trajectory))

    def test_negative_parameters(self):
        """Test behavior with negative parameters."""
        # Negative parameters should still integrate
        lorenz = LorenzAttractor(
            parameters={'sigma': -10.0, 'rho': -28.0, 'beta': -8.0/3.0}
        )

        trajectory = lorenz.generate_trajectory(t_span=(0, 10), n_points=100)
        assert trajectory.shape == (100, 3)

    def test_very_short_time_span(self):
        """Test trajectory generation with very short time span."""
        lorenz = LorenzAttractor()
        trajectory = lorenz.generate_trajectory(t_span=(0, 0.1), n_points=10)

        assert trajectory.shape == (10, 3)
        # Should barely move from initial state
        assert np.linalg.norm(trajectory[-1] - trajectory[0]) < 5.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
