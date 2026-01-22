"""
Unit tests for the Thomas attractor implementation.

Tests verify:
- Mathematical correctness of differential equations
- Trajectory properties (continuity, boundedness)
- Parameter effects
- Symmetry properties
- Chaotic behavior characteristics
"""

import unittest
import numpy as np
from thomas_attractor import ThomasAttractor


class TestThomasAttractor(unittest.TestCase):
    """Test suite for Thomas attractor."""

    def setUp(self):
        """Set up test fixtures."""
        # Classic parameter value
        self.thomas = ThomasAttractor(b=0.208186)
        # For faster tests, use shorter duration
        self.test_duration = 50.0
        self.test_dt = 0.01

    def test_initialization(self):
        """Test that Thomas attractor initializes correctly."""
        thomas = ThomasAttractor(b=0.3)
        self.assertEqual(thomas.b, 0.3)

        # Test default parameter
        thomas_default = ThomasAttractor()
        self.assertAlmostEqual(thomas_default.b, 0.208186, places=5)

    def test_equations_shape(self):
        """Test that equations return correct shape."""
        state = np.array([1.0, 2.0, 3.0])
        derivatives = self.thomas.equations(0, state)

        self.assertEqual(derivatives.shape, (3,))
        self.assertTrue(np.all(np.isfinite(derivatives)))

    def test_equations_symmetry(self):
        """
        Test cyclic symmetry of Thomas equations.

        The Thomas system has cyclic symmetry: if we rotate the coordinates
        (x, y, z) → (y, z, x), the equations should transform accordingly.
        """
        # Test point
        state1 = np.array([1.0, 2.0, 3.0])
        deriv1 = self.thomas.equations(0, state1)

        # Rotate coordinates: (x,y,z) → (y,z,x)
        state2 = np.array([2.0, 3.0, 1.0])  # (y, z, x) from state1
        deriv2 = self.thomas.equations(0, state2)

        # The derivatives should also be rotated
        # deriv1 = [dx/dt, dy/dt, dz/dt]
        # deriv2 should equal [dy/dt, dz/dt, dx/dt] from state1's perspective
        expected = np.array([deriv1[1], deriv1[2], deriv1[0]])

        np.testing.assert_array_almost_equal(deriv2, expected, decimal=10)

    def test_equations_values(self):
        """Test specific equation values at known points."""
        # At origin, equations simplify nicely
        state = np.array([0.0, 0.0, 0.0])
        derivatives = self.thomas.equations(0, state)

        # At origin: dx/dt = sin(0) - b*0 = 0
        # Same for all three equations
        expected = np.array([0.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(derivatives, expected, decimal=10)

        # Test a non-zero point
        # x=π/2, y=0, z=0
        state = np.array([np.pi/2, 0.0, 0.0])
        derivatives = self.thomas.equations(0, state)

        b = self.thomas.b
        expected = np.array([
            np.sin(0.0) - b * np.pi/2,  # dx/dt = sin(y) - b*x
            np.sin(0.0) - b * 0.0,       # dy/dt = sin(z) - b*y
            np.sin(np.pi/2) - b * 0.0    # dz/dt = sin(x) - b*z
        ])
        np.testing.assert_array_almost_equal(derivatives, expected, decimal=10)

    def test_default_initial_state(self):
        """Test that default initial state is sensible."""
        state = self.thomas.default_initial_state()

        self.assertEqual(state.shape, (3,))
        self.assertTrue(np.all(np.isfinite(state)))

        # Should be near origin but not at it
        self.assertLess(np.linalg.norm(state), 1.0)
        self.assertGreater(np.linalg.norm(state), 0.0)

    def test_simulation_runs(self):
        """Test that simulation completes without errors."""
        trajectory = self.thomas.simulate(duration=self.test_duration, dt=self.test_dt)

        expected_length = int(self.test_duration / self.test_dt) + 1
        self.assertEqual(len(trajectory), expected_length)
        self.assertEqual(trajectory.shape[1], 3)
        self.assertTrue(np.all(np.isfinite(trajectory)))

    def test_trajectory_continuity(self):
        """Test that trajectory is continuous (no jumps)."""
        trajectory = self.thomas.simulate(duration=self.test_duration, dt=self.test_dt)

        # Check that consecutive points are close
        differences = np.diff(trajectory, axis=0)
        max_step = np.max(np.abs(differences))

        # With dt=0.01 and bounded derivatives, steps should be small
        self.assertLess(max_step, 1.0)

    def test_trajectory_boundedness(self):
        """
        Test that trajectory remains bounded.

        The Thomas attractor should remain in a bounded region of phase space.
        For b = 0.208186, typical values stay within roughly [-4, 4] for each coordinate.
        """
        trajectory = self.thomas.simulate(duration=self.test_duration, dt=self.test_dt)

        # Check each coordinate
        for i, label in enumerate(['x', 'y', 'z']):
            coord = trajectory[:, i]
            self.assertLess(np.max(np.abs(coord)), 10.0,
                          f"Coordinate {label} exceeds expected bounds")

    def test_attractor_convergence(self):
        """
        Test that trajectory converges to attractor region.

        After transient period, the trajectory should settle into the
        attractor and stay within consistent bounds.
        """
        trajectory = self.thomas.simulate(duration=100.0, dt=self.test_dt)

        # Skip transient (first 20 time units)
        transient_idx = int(20.0 / self.test_dt)
        settled = trajectory[transient_idx:]

        # After settling, all points should be in similar region
        for i in range(3):
            coord = settled[:, i]
            coord_range = np.max(coord) - np.min(coord)
            # Should span a reasonable range (not collapsed to a point)
            self.assertGreater(coord_range, 1.0)
            # But not too large
            self.assertLess(coord_range, 10.0)

    def test_sensitive_dependence(self):
        """
        Test butterfly effect: nearby initial conditions diverge.

        This is the defining characteristic of chaotic systems.
        """
        # Two very close initial conditions
        epsilon = 1e-8
        state1 = np.array([0.1, 0.0, 0.0])
        state2 = state1 + np.array([epsilon, 0.0, 0.0])

        # Simulate both
        traj1 = self.thomas.simulate(duration=20.0, dt=self.test_dt,
                                     initial_state=state1)
        traj2 = self.thomas.simulate(duration=20.0, dt=self.test_dt,
                                     initial_state=state2)

        # Compute distance over time
        distances = np.linalg.norm(traj1 - traj2, axis=1)

        # Distance should grow significantly from initial separation
        final_distance = distances[-1]
        initial_distance = distances[0]

        # Should see substantial amplification
        amplification = final_distance / initial_distance
        self.assertGreater(amplification, 100.0,
                          "Trajectories should diverge significantly (butterfly effect)")

    def test_phase_space_exploration(self):
        """
        Test that trajectory explores phase space (not periodic).

        A chaotic attractor should visit many different states without
        repeating exactly.
        """
        trajectory = self.thomas.simulate(duration=self.test_duration, dt=self.test_dt)

        # Skip transient
        transient_idx = int(10.0 / self.test_dt)
        settled = trajectory[transient_idx:]

        # Compute variance in each dimension - should be significant
        variances = np.var(settled, axis=0)
        for i, var in enumerate(variances):
            self.assertGreater(var, 0.1,
                             f"Dimension {i} should show significant variation")

    def test_parameter_effect(self):
        """
        Test that different b values produce different behavior.

        Changing the damping parameter should affect the attractor's shape.
        """
        b_values = [0.1, 0.208186, 0.3]
        trajectories = []

        for b in b_values:
            thomas = ThomasAttractor(b=b)
            traj = thomas.simulate(duration=50.0, dt=self.test_dt)
            trajectories.append(traj)

        # Trajectories should be substantially different
        # Compare by looking at ranges in each dimension
        ranges = []
        for traj in trajectories:
            # Skip transient
            settled = traj[int(10.0 / self.test_dt):]
            coord_ranges = np.ptp(settled, axis=0)  # ptp = peak-to-peak
            ranges.append(coord_ranges)

        # At least two trajectories should have noticeably different ranges
        # (they shouldn't all be the same)
        for dim in range(3):
            dim_ranges = [r[dim] for r in ranges]
            range_variation = np.std(dim_ranges)
            # Allow for some variation but not all identical
            self.assertGreater(range_variation, 0.01,
                             f"Dimension {dim} should vary with parameter b")

    def test_origin_is_fixed_point(self):
        """
        Test that origin is a fixed point.

        At (0, 0, 0), all derivatives should be zero.
        """
        state = np.array([0.0, 0.0, 0.0])
        derivatives = self.thomas.equations(0, state)

        np.testing.assert_array_almost_equal(
            derivatives,
            np.array([0.0, 0.0, 0.0]),
            decimal=10,
            err_msg="Origin should be a fixed point"
        )

    def test_trigonometric_bounds(self):
        """
        Test that derivatives respect trigonometric bounds.

        Since equations use sin(), which is bounded by [-1, 1],
        the derivatives should be bounded accordingly.
        """
        # Test at various points
        np.random.seed(42)
        for _ in range(100):
            # Random point in phase space
            state = np.random.uniform(-5, 5, size=3)
            derivatives = self.thomas.equations(0, state)

            # For each derivative: |dx/dt| = |sin(y) - b*x|
            # sin(y) is in [-1, 1], so |dx/dt| ≤ 1 + b*|x|
            b = self.thomas.b
            x, y, z = state

            max_dx = 1.0 + b * abs(x)
            max_dy = 1.0 + b * abs(y)
            max_dz = 1.0 + b * abs(z)

            self.assertLessEqual(abs(derivatives[0]), max_dx + 0.01)  # small tolerance
            self.assertLessEqual(abs(derivatives[1]), max_dy + 0.01)
            self.assertLessEqual(abs(derivatives[2]), max_dz + 0.01)


def run_tests():
    """Run all tests with verbose output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestThomasAttractor)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
