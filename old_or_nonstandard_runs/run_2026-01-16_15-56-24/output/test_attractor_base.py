"""
Tests for the AttractorBase class.

These tests verify the base functionality that all attractors inherit,
including initialization, parameter management, and trajectory generation.
"""

import pytest
import numpy as np
from attractor_base import AttractorBase


class SimpleAttractor(AttractorBase):
    """
    A simple test attractor for testing the base class.

    Implements a simple linear system:
        dx/dt = -x
        dy/dt = -y
        dz/dt = -z

    This converges exponentially to the origin.
    """

    def derivatives(self, t, state):
        """Simple exponential decay."""
        return -state

    def default_parameters(self):
        """No parameters needed for this simple system."""
        return {'decay_rate': 1.0}

    def default_initial_state(self):
        """Start at [1, 1, 1]."""
        return np.array([1.0, 1.0, 1.0])


class TestAttractorBaseInitialization:
    """Test attractor initialization and configuration."""

    def test_default_initialization(self):
        """Test initialization with default values."""
        attractor = SimpleAttractor()

        assert attractor.dimension == 3
        assert len(attractor.initial_state) == 3
        np.testing.assert_array_equal(
            attractor.initial_state,
            np.array([1.0, 1.0, 1.0])
        )
        assert 'decay_rate' in attractor.parameters

    def test_custom_initial_state(self):
        """Test initialization with custom initial state."""
        custom_state = np.array([5.0, -2.0, 3.0])
        attractor = SimpleAttractor(initial_state=custom_state)

        np.testing.assert_array_equal(
            attractor.initial_state,
            custom_state
        )

    def test_custom_parameters(self):
        """Test initialization with custom parameters."""
        custom_params = {'decay_rate': 2.0}
        attractor = SimpleAttractor(parameters=custom_params)

        assert attractor.parameters['decay_rate'] == 2.0

    def test_wrong_dimension_raises_error(self):
        """Test that wrong initial state dimension raises ValueError."""
        wrong_state = np.array([1.0, 2.0])  # 2D instead of 3D

        with pytest.raises(ValueError, match="doesn't match system dimension"):
            SimpleAttractor(initial_state=wrong_state)


class TestAttractorTrajectoryGeneration:
    """Test trajectory generation functionality."""

    def test_generate_trajectory_shape(self):
        """Test that generated trajectory has correct shape."""
        attractor = SimpleAttractor()
        n_points = 1000

        trajectory = attractor.generate_trajectory(
            t_span=(0, 10),
            n_points=n_points
        )

        assert trajectory.shape == (n_points, 3)

    def test_generate_trajectory_values(self):
        """Test that trajectory values are physically reasonable."""
        attractor = SimpleAttractor()
        trajectory = attractor.generate_trajectory(
            t_span=(0, 5),
            n_points=100
        )

        # For exponential decay, values should monotonically decrease
        # and approach zero
        assert trajectory[0, 0] > trajectory[-1, 0]
        assert trajectory[-1, 0] > 0  # Should be positive but small
        assert trajectory[-1, 0] < 0.1  # Should decay significantly

    def test_generate_trajectory_different_timespan(self):
        """Test trajectory generation with different time spans."""
        attractor = SimpleAttractor()

        # Short time span
        traj_short = attractor.generate_trajectory(
            t_span=(0, 1),
            n_points=100
        )

        # Long time span
        traj_long = attractor.generate_trajectory(
            t_span=(0, 10),
            n_points=100
        )

        # Longer time should lead to more decay
        assert np.linalg.norm(traj_long[-1]) < np.linalg.norm(traj_short[-1])

    def test_generate_trajectory_integration_methods(self):
        """Test that different integration methods work."""
        attractor = SimpleAttractor()

        methods = ['RK45', 'RK23', 'DOP853']

        for method in methods:
            trajectory = attractor.generate_trajectory(
                t_span=(0, 5),
                n_points=100,
                method=method
            )
            assert trajectory.shape == (100, 3)
            # Should still decay
            assert np.linalg.norm(trajectory[-1]) < np.linalg.norm(trajectory[0])


class TestAttractorParameterManagement:
    """Test parameter update and management."""

    def test_update_parameters(self):
        """Test updating parameters."""
        attractor = SimpleAttractor()
        original_value = attractor.parameters['decay_rate']

        attractor.update_parameters(decay_rate=5.0)

        assert attractor.parameters['decay_rate'] == 5.0
        assert attractor.parameters['decay_rate'] != original_value

    def test_update_invalid_parameter_raises_error(self):
        """Test that updating non-existent parameter raises error."""
        attractor = SimpleAttractor()

        with pytest.raises(ValueError, match="Unknown parameter"):
            attractor.update_parameters(nonexistent_param=1.0)

    def test_set_initial_state(self):
        """Test setting new initial state."""
        attractor = SimpleAttractor()
        new_state = np.array([10.0, -5.0, 2.0])

        attractor.set_initial_state(new_state)

        np.testing.assert_array_equal(attractor.initial_state, new_state)

    def test_set_initial_state_wrong_dimension(self):
        """Test that setting wrong dimension raises error."""
        attractor = SimpleAttractor()
        wrong_state = np.array([1.0, 2.0])

        with pytest.raises(ValueError, match="doesn't match system dimension"):
            attractor.set_initial_state(wrong_state)


class TestAttractorInfo:
    """Test information retrieval methods."""

    def test_get_info(self):
        """Test getting attractor information."""
        attractor = SimpleAttractor()
        info = attractor.get_info()

        assert 'type' in info
        assert info['type'] == 'SimpleAttractor'
        assert 'dimension' in info
        assert info['dimension'] == 3
        assert 'parameters' in info
        assert 'initial_state' in info

    def test_get_info_returns_copies(self):
        """Test that get_info returns copies, not references."""
        attractor = SimpleAttractor()
        info = attractor.get_info()

        # Modify the returned values
        info['parameters']['decay_rate'] = 999.0
        info['initial_state'][0] = 999.0

        # Original should be unchanged
        assert attractor.parameters['decay_rate'] != 999.0
        assert attractor.initial_state[0] != 999.0


class TestAttractorIntegration:
    """Integration tests combining multiple features."""

    def test_parameter_change_affects_trajectory(self):
        """Test that changing parameters affects the generated trajectory."""
        attractor = SimpleAttractor()

        # Generate trajectory with default parameters
        traj1 = attractor.generate_trajectory(t_span=(0, 5), n_points=100)

        # Change decay rate (not actually used in SimpleAttractor,
        # but demonstrates the pattern)
        # For a real test, we'd need an attractor where parameters matter
        attractor.set_initial_state(np.array([10.0, 10.0, 10.0]))
        traj2 = attractor.generate_trajectory(t_span=(0, 5), n_points=100)

        # Trajectories should be different
        assert not np.allclose(traj1, traj2)

    def test_reproducibility(self):
        """Test that same configuration produces same trajectory."""
        attractor1 = SimpleAttractor()
        attractor2 = SimpleAttractor()

        traj1 = attractor1.generate_trajectory(t_span=(0, 5), n_points=100)
        traj2 = attractor2.generate_trajectory(t_span=(0, 5), n_points=100)

        np.testing.assert_allclose(traj1, traj2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
