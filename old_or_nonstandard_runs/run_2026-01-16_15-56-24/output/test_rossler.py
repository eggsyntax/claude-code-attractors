"""
Comprehensive test suite for the Rössler attractor implementation.

Tests cover derivative calculations, trajectory generation, parameter regimes,
boundedness, Poincaré sections, and comparison with known results from literature.
"""

import numpy as np
import pytest
from rossler import RosslerAttractor


class TestRosslerBasics:
    """Test basic Rössler attractor functionality."""

    def test_initialization_default(self):
        """Test initialization with default parameters."""
        rossler = RosslerAttractor()
        assert rossler.dimension == 3
        assert 'a' in rossler.parameters
        assert 'b' in rossler.parameters
        assert 'c' in rossler.parameters
        assert len(rossler.initial_state) == 3

    def test_initialization_custom_parameters(self):
        """Test initialization with custom parameters."""
        params = {'a': 0.3, 'b': 0.3, 'c': 4.0}
        rossler = RosslerAttractor(parameters=params)
        assert rossler.parameters['a'] == 0.3
        assert rossler.parameters['b'] == 0.3
        assert rossler.parameters['c'] == 4.0

    def test_initialization_custom_initial_state(self):
        """Test initialization with custom initial state."""
        state = np.array([2.0, 3.0, 4.0])
        rossler = RosslerAttractor(initial_state=state)
        np.testing.assert_array_equal(rossler.initial_state, state)


class TestRosslerDerivatives:
    """Test derivative calculations."""

    def test_derivatives_shape(self):
        """Test that derivatives return correct shape."""
        rossler = RosslerAttractor()
        state = np.array([1.0, 1.0, 1.0])
        derivatives = rossler.derivatives(0, state)
        assert derivatives.shape == (3,)

    def test_derivatives_standard_parameters(self):
        """Test derivative calculation with standard chaotic parameters."""
        rossler = RosslerAttractor()  # a=0.2, b=0.2, c=5.7
        state = np.array([1.0, 1.0, 1.0])
        dx_dt, dy_dt, dz_dt = rossler.derivatives(0, state)

        # Manual calculation:
        # dx/dt = -y - z = -1 - 1 = -2
        # dy/dt = x + a*y = 1 + 0.2*1 = 1.2
        # dz/dt = b + z*(x - c) = 0.2 + 1*(1 - 5.7) = 0.2 - 4.7 = -4.5

        assert np.isclose(dx_dt, -2.0)
        assert np.isclose(dy_dt, 1.2)
        assert np.isclose(dz_dt, -4.5)

    def test_derivatives_at_different_states(self):
        """Test derivatives at various states to verify correctness."""
        rossler = RosslerAttractor()

        # State 1: Origin
        state1 = np.array([0.0, 0.0, 0.0])
        dx1, dy1, dz1 = rossler.derivatives(0, state1)
        assert np.isclose(dx1, 0.0)
        assert np.isclose(dy1, 0.0)
        assert np.isclose(dz1, 0.2)  # Just b

        # State 2: Positive values
        state2 = np.array([5.0, 2.0, 3.0])
        dx2, dy2, dz2 = rossler.derivatives(0, state2)
        assert np.isclose(dx2, -2.0 - 3.0)  # -y - z
        assert np.isclose(dy2, 5.0 + 0.2 * 2.0)  # x + a*y
        assert np.isclose(dz2, 0.2 + 3.0 * (5.0 - 5.7))  # b + z*(x - c)


class TestRosslerTrajectories:
    """Test trajectory generation."""

    def test_generate_trajectory_basic(self):
        """Test basic trajectory generation."""
        rossler = RosslerAttractor()
        trajectory = rossler.generate_trajectory(t_span=(0, 10), n_points=1000)

        assert trajectory.shape == (1000, 3)
        assert not np.any(np.isnan(trajectory))
        assert not np.any(np.isinf(trajectory))

    def test_trajectory_starts_at_initial_state(self):
        """Test that trajectory starts at the specified initial state."""
        initial = np.array([1.0, 2.0, 3.0])
        rossler = RosslerAttractor(initial_state=initial)
        trajectory = rossler.generate_trajectory(t_span=(0, 10), n_points=100)

        # First point should be close to initial state
        np.testing.assert_array_almost_equal(trajectory[0], initial, decimal=1)

    def test_trajectory_evolves_over_time(self):
        """Test that trajectory changes over time (not static)."""
        rossler = RosslerAttractor()
        trajectory = rossler.generate_trajectory(t_span=(0, 50), n_points=1000)

        # Check that trajectory actually moves
        start = trajectory[0]
        end = trajectory[-1]
        distance = np.linalg.norm(end - start)
        assert distance > 1.0  # Should have moved significantly

    def test_different_integration_methods(self):
        """Test that different integration methods work."""
        rossler = RosslerAttractor()

        methods = ['RK45', 'RK23', 'DOP853']
        trajectories = []

        for method in methods:
            traj = rossler.generate_trajectory(
                t_span=(0, 20),
                n_points=500,
                method=method
            )
            trajectories.append(traj)
            assert traj.shape == (500, 3)
            assert not np.any(np.isnan(traj))

        # Different methods should give similar but not identical results
        for i in range(len(trajectories) - 1):
            correlation = np.corrcoef(
                trajectories[i].flatten(),
                trajectories[i+1].flatten()
            )[0, 1]
            assert correlation > 0.95  # Highly correlated


class TestRosslerParameterRegimes:
    """Test behavior in different parameter regimes."""

    def test_chaotic_regime_boundedness(self):
        """Test that chaotic trajectories remain bounded."""
        rossler = RosslerAttractor(parameters={'a': 0.2, 'b': 0.2, 'c': 5.7})
        trajectory = rossler.generate_trajectory(t_span=(0, 100), n_points=5000)

        # Rössler attractor should remain bounded in chaotic regime
        # Typical bounds are roughly -20 < x < 20, -10 < y < 10, 0 < z < 40
        assert np.all(np.abs(trajectory[:, 0]) < 30)
        assert np.all(np.abs(trajectory[:, 1]) < 20)
        assert np.all(trajectory[:, 2] < 50)
        assert np.all(trajectory[:, 2] > -5)

    def test_periodic_regime(self):
        """Test behavior in periodic regime (c = 2.0)."""
        rossler = RosslerAttractor(parameters={'a': 0.2, 'b': 0.2, 'c': 2.0})
        trajectory = rossler.generate_trajectory(t_span=(0, 100), n_points=5000)

        # Should be bounded and well-behaved
        assert not np.any(np.isnan(trajectory))
        assert not np.any(np.isinf(trajectory))
        assert np.all(np.abs(trajectory) < 100)

    def test_parameter_recommendations(self):
        """Test that parameter recommendations are provided and valid."""
        recommendations = RosslerAttractor.get_parameter_recommendations()

        assert isinstance(recommendations, dict)
        assert 'chaotic' in recommendations
        assert 'periodic' in recommendations

        # Test that each recommendation works
        for name, params in recommendations.items():
            rossler = RosslerAttractor(parameters=params)
            trajectory = rossler.generate_trajectory(t_span=(0, 20), n_points=500)
            assert trajectory.shape == (500, 3)
            assert not np.any(np.isnan(trajectory))


class TestPoincareSection:
    """Test Poincaré section functionality."""

    def test_poincare_section_basic(self):
        """Test basic Poincaré section computation."""
        rossler = RosslerAttractor()
        trajectory = rossler.generate_trajectory(t_span=(0, 200), n_points=10000)

        # Compute Poincaré section for z = 0 plane
        section = rossler.compute_poincare_section(trajectory, plane='z', value=0.0)

        assert section.shape[1] == 2  # Should be 2D (x, y)
        assert section.shape[0] > 0  # Should have some intersection points
        assert not np.any(np.isnan(section))

    def test_poincare_section_different_planes(self):
        """Test Poincaré sections on different planes."""
        rossler = RosslerAttractor()
        trajectory = rossler.generate_trajectory(t_span=(0, 200), n_points=10000)

        planes = ['x', 'y', 'z']
        for plane in planes:
            section = rossler.compute_poincare_section(
                trajectory,
                plane=plane,
                value=0.0
            )
            assert section.shape[1] == 2
            assert section.shape[0] > 0

    def test_poincare_section_with_direction(self):
        """Test Poincaré section with direction constraint (upward crossing)."""
        rossler = RosslerAttractor()
        trajectory = rossler.generate_trajectory(t_span=(0, 200), n_points=10000)

        section_all = rossler.compute_poincare_section(
            trajectory, plane='z', value=10.0, direction='both'
        )
        section_up = rossler.compute_poincare_section(
            trajectory, plane='z', value=10.0, direction='up'
        )
        section_down = rossler.compute_poincare_section(
            trajectory, plane='z', value=10.0, direction='down'
        )

        # Upward and downward should be fewer than both
        assert section_up.shape[0] < section_all.shape[0]
        assert section_down.shape[0] < section_all.shape[0]

        # Sum should roughly equal both (allowing for boundary effects)
        assert abs((section_up.shape[0] + section_down.shape[0]) -
                   section_all.shape[0]) < 5


class TestReturnMap:
    """Test return map functionality."""

    def test_return_map_basic(self):
        """Test basic return map computation."""
        rossler = RosslerAttractor()
        trajectory = rossler.generate_trajectory(t_span=(0, 200), n_points=10000)

        # Get Poincaré section
        section = rossler.compute_poincare_section(trajectory, plane='z', value=0.0)

        # Compute return map (plotting z_n+1 vs z_n equivalent)
        if section.shape[0] > 1:
            x_current = section[:-1, 0]
            x_next = section[1:, 0]

            assert len(x_current) == len(x_next)
            assert len(x_current) > 0

    def test_return_map_shows_structure(self):
        """Test that return map reveals attractor structure."""
        rossler = RosslerAttractor()
        trajectory = rossler.generate_trajectory(t_span=(0, 300), n_points=15000)

        section = rossler.compute_poincare_section(
            trajectory, plane='z', value=0.0, direction='up'
        )

        # For chaotic Rössler, return map should show characteristic structure
        if section.shape[0] > 10:
            x_vals = section[:, 0]
            # Should span a reasonable range
            assert np.ptp(x_vals) > 1.0  # Range should be > 1
            # Should have some variation
            assert np.std(x_vals) > 0.1


class TestRosslerInfo:
    """Test information and metadata methods."""

    def test_get_info(self):
        """Test that get_info returns proper metadata."""
        rossler = RosslerAttractor()
        info = rossler.get_info()

        assert info['type'] == 'Rössler'
        assert info['dimension'] == 3
        assert 'parameters' in info
        assert 'initial_state' in info

    def test_info_includes_parameters(self):
        """Test that info includes current parameters."""
        params = {'a': 0.3, 'b': 0.3, 'c': 4.0}
        rossler = RosslerAttractor(parameters=params)
        info = rossler.get_info()

        assert info['parameters']['a'] == 0.3
        assert info['parameters']['b'] == 0.3
        assert info['parameters']['c'] == 4.0


class TestRosslerComparison:
    """Test comparison and validation against known results."""

    def test_sensitivity_to_initial_conditions(self):
        """Test butterfly effect (sensitive dependence on initial conditions)."""
        # Two very close initial conditions
        state1 = np.array([1.0, 1.0, 1.0])
        state2 = np.array([1.0, 1.0, 1.000001])  # Tiny difference

        rossler1 = RosslerAttractor(initial_state=state1)
        rossler2 = RosslerAttractor(initial_state=state2)

        traj1 = rossler1.generate_trajectory(t_span=(0, 50), n_points=5000)
        traj2 = rossler2.generate_trajectory(t_span=(0, 50), n_points=5000)

        # Calculate divergence over time
        distances = np.linalg.norm(traj1 - traj2, axis=1)

        # Should start very close
        assert distances[0] < 0.0001

        # Should diverge significantly by the end
        assert distances[-1] > 1.0

        # Check that divergence generally increases (allowing for fluctuations)
        early_mean = np.mean(distances[:len(distances)//4])
        late_mean = np.mean(distances[3*len(distances)//4:])
        assert late_mean > early_mean * 10

    def test_attractor_convergence(self):
        """Test that different initial conditions converge to same attractor."""
        # Multiple initial conditions
        initial_states = [
            np.array([1.0, 1.0, 1.0]),
            np.array([5.0, -3.0, 2.0]),
            np.array([-2.0, 4.0, 8.0])
        ]

        trajectories = []
        for state in initial_states:
            rossler = RosslerAttractor(initial_state=state)
            # Let it settle onto attractor
            traj = rossler.generate_trajectory(t_span=(0, 100), n_points=5000)
            trajectories.append(traj)

        # After settling, all should occupy similar regions of space
        # Check the last quarter of each trajectory
        for i in range(len(trajectories)):
            settled = trajectories[i][-1250:]  # Last quarter

            # Should be in typical Rössler bounds
            assert np.all(np.abs(settled[:, 0]) < 20)
            assert np.all(np.abs(settled[:, 1]) < 15)
            assert np.all(settled[:, 2] < 45)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
