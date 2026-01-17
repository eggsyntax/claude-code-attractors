"""
Unit Tests for Bifurcation Diagram Generator

Tests the bifurcation analysis functionality, verifying:
- Correct Poincaré section crossing detection
- Parameter sweep behavior
- System dynamics at known parameter values
- Bifurcation diagram structure

Author: Bob
"""

import unittest
import numpy as np
from bifurcation import (
    BifurcationDiagram,
    lorenz_system,
    rossler_system
)


class TestBifurcationDiagram(unittest.TestCase):
    """Test the BifurcationDiagram class."""

    def test_poincare_crossing_positive(self):
        """Test detection of positive (upward) Poincaré section crossings."""
        bifurcation = BifurcationDiagram(
            system_func=lorenz_system,
            param_range=(0, 1),
            initial_state=np.array([1.0, 1.0, 1.0])
        )

        # Create a simple trajectory that crosses y=0 upward at indices 2 and 5
        trajectory = np.array([
            [1, 1, 1, 1, 1, 1, 1],  # x
            [-1, -0.5, 0.5, 1, -1, 0.5, 1],  # y (crosses 0 at indices 2 and 5)
            [1, 1, 1, 1, 1, 1, 1]   # z
        ])

        crossings = bifurcation._find_poincare_crossings(
            trajectory,
            condition_index=1,
            condition_value=0.0,
            direction='positive'
        )

        self.assertEqual(len(crossings), 2)
        self.assertIn(2, crossings)
        self.assertIn(5, crossings)

    def test_poincare_crossing_negative(self):
        """Test detection of negative (downward) Poincaré section crossings."""
        bifurcation = BifurcationDiagram(
            system_func=lorenz_system,
            param_range=(0, 1),
            initial_state=np.array([1.0, 1.0, 1.0])
        )

        # Create a trajectory that crosses y=0 downward at index 2
        trajectory = np.array([
            [1, 1, 1, 1],  # x
            [1, 0.5, -0.5, -1],  # y (crosses 0 downward at index 2)
            [1, 1, 1, 1]   # z
        ])

        crossings = bifurcation._find_poincare_crossings(
            trajectory,
            condition_index=1,
            condition_value=0.0,
            direction='negative'
        )

        self.assertEqual(len(crossings), 1)
        self.assertEqual(crossings[0], 2)

    def test_lorenz_system_evaluation(self):
        """Test that the Lorenz system produces expected derivatives."""
        state = np.array([1.0, 1.0, 1.0])
        rho = 28.0

        derivatives = lorenz_system(0, state, rho)

        # At (1, 1, 1) with standard parameters:
        # dx = 10 * (1 - 1) = 0
        # dy = 1 * (28 - 1) - 1 = 26
        # dz = 1 * 1 - (8/3) * 1 ≈ -1.667

        self.assertEqual(len(derivatives), 3)
        self.assertAlmostEqual(derivatives[0], 0.0, places=5)
        self.assertAlmostEqual(derivatives[1], 26.0, places=5)
        self.assertAlmostEqual(derivatives[2], -8.0/3.0, places=5)

    def test_rossler_system_evaluation(self):
        """Test that the Rössler system produces expected derivatives."""
        state = np.array([1.0, 1.0, 1.0])
        c = 5.7

        derivatives = rossler_system(0, state, c)

        # At (1, 1, 1) with a=0.2, b=0.2, c=5.7:
        # dx = -1 - 1 = -2
        # dy = 1 + 0.2 * 1 = 1.2
        # dz = 0.2 + 1 * (1 - 5.7) = -4.5

        self.assertEqual(len(derivatives), 3)
        self.assertAlmostEqual(derivatives[0], -2.0, places=5)
        self.assertAlmostEqual(derivatives[1], 1.2, places=5)
        self.assertAlmostEqual(derivatives[2], -4.5, places=5)

    def test_lorenz_chaotic_vs_stable(self):
        """
        Test that Lorenz system shows different behavior for chaotic vs stable parameters.

        For rho < 1, the system should converge to the origin.
        For rho = 28, the system should exhibit chaotic behavior.
        """
        # Test stable case (rho = 0.5, should converge to origin)
        bifurcation_stable = BifurcationDiagram(
            system_func=lorenz_system,
            param_range=(0.5, 0.5),
            param_steps=1,
            initial_state=np.array([1.0, 1.0, 1.0]),
            t_transient=50.0,
            t_sample=50.0,
            dt=0.1
        )

        params_stable, values_stable = bifurcation_stable.compute()

        # Should have very few or no crossings (converges to fixed point)
        self.assertLessEqual(len(values_stable[0]), 5)

        # Test chaotic case (rho = 28, should have many crossings)
        bifurcation_chaotic = BifurcationDiagram(
            system_func=lorenz_system,
            param_range=(28.0, 28.0),
            param_steps=1,
            initial_state=np.array([1.0, 1.0, 1.0]),
            t_transient=50.0,
            t_sample=50.0,
            dt=0.1
        )

        params_chaotic, values_chaotic = bifurcation_chaotic.compute()

        # Should have many crossings (chaotic behavior)
        self.assertGreater(len(values_chaotic[0]), 20)

    def test_rossler_period_doubling(self):
        """
        Test that Rössler system shows period-doubling behavior.

        At c = 2.5, should see period-1 behavior (few distinct crossing values).
        At c = 5.0, should see chaotic behavior (many crossing values).
        """
        # Test period-1 case
        bifurcation_periodic = BifurcationDiagram(
            system_func=rossler_system,
            param_range=(2.5, 2.5),
            param_steps=1,
            initial_state=np.array([1.0, 1.0, 1.0]),
            t_transient=200.0,
            t_sample=100.0,
            dt=0.1
        )

        params_periodic, values_periodic = bifurcation_periodic.compute()

        # For period-1, crossings should cluster around 2-3 similar values
        if len(values_periodic[0]) > 0:
            crossing_std = np.std(values_periodic[0])
            self.assertLess(crossing_std, 1.0)  # Low variance for periodic

        # Test chaotic case
        bifurcation_chaotic = BifurcationDiagram(
            system_func=rossler_system,
            param_range=(5.0, 5.0),
            param_steps=1,
            initial_state=np.array([1.0, 1.0, 1.0]),
            t_transient=200.0,
            t_sample=100.0,
            dt=0.1
        )

        params_chaotic, values_chaotic = bifurcation_chaotic.compute()

        # For chaos, should have high variance and many crossings
        if len(values_chaotic[0]) > 0:
            crossing_std = np.std(values_chaotic[0])
            self.assertGreater(crossing_std, 1.0)  # Higher variance for chaos

    def test_parameter_sweep_length(self):
        """Test that parameter sweep generates correct number of points."""
        param_steps = 10
        bifurcation = BifurcationDiagram(
            system_func=lorenz_system,
            param_range=(20.0, 30.0),
            param_steps=param_steps,
            initial_state=np.array([1.0, 1.0, 1.0]),
            t_transient=20.0,
            t_sample=20.0,
            dt=0.1
        )

        params, values = bifurcation.compute()

        self.assertEqual(len(params), param_steps)
        self.assertEqual(len(values), param_steps)

        # Check parameter range
        self.assertAlmostEqual(params[0], 20.0, places=5)
        self.assertAlmostEqual(params[-1], 30.0, places=5)

    def test_system_boundedness(self):
        """Test that attractors remain bounded during parameter sweeps."""
        bifurcation = BifurcationDiagram(
            system_func=lorenz_system,
            param_range=(20.0, 35.0),
            param_steps=5,
            initial_state=np.array([1.0, 1.0, 1.0]),
            t_transient=50.0,
            t_sample=50.0,
            dt=0.1
        )

        params, values = bifurcation.compute(state_index=2)  # z coordinate

        # Check that all crossing values are bounded
        # Lorenz z-coordinate typically stays below 50
        for val_array in values:
            if len(val_array) > 0:
                self.assertLess(np.max(np.abs(val_array)), 100.0)


class TestLorenzSystem(unittest.TestCase):
    """Specific tests for the Lorenz system behavior."""

    def test_lorenz_symmetry(self):
        """Test that Lorenz system respects its symmetry property."""
        # Lorenz system has (x, y, z) → (-x, -y, z) symmetry
        state1 = np.array([1.0, 2.0, 3.0])
        state2 = np.array([-1.0, -2.0, 3.0])
        rho = 28.0

        deriv1 = lorenz_system(0, state1, rho)
        deriv2 = lorenz_system(0, state2, rho)

        # dx and dy should flip sign, dz should be the same
        self.assertAlmostEqual(deriv1[0], -deriv2[0], places=5)
        self.assertAlmostEqual(deriv1[1], -deriv2[1], places=5)
        self.assertAlmostEqual(deriv1[2], deriv2[2], places=5)

    def test_lorenz_fixed_point_origin(self):
        """Test that origin is a fixed point for small rho."""
        # At origin with any rho, derivatives should be zero
        state = np.array([0.0, 0.0, 0.0])
        rho = 28.0

        deriv = lorenz_system(0, state, rho)

        self.assertAlmostEqual(deriv[0], 0.0, places=10)
        self.assertAlmostEqual(deriv[1], 0.0, places=10)
        self.assertAlmostEqual(deriv[2], 0.0, places=10)


class TestRosslerSystem(unittest.TestCase):
    """Specific tests for the Rössler system behavior."""

    def test_rossler_parameter_dependence(self):
        """Test that Rössler system behavior changes with parameter c."""
        state = np.array([1.0, 1.0, 1.0])

        # Compute derivatives for different c values
        deriv_c2 = rossler_system(0, state, c=2.0)
        deriv_c5 = rossler_system(0, state, c=5.0)

        # dx and dy should be the same (don't depend on c)
        self.assertAlmostEqual(deriv_c2[0], deriv_c5[0], places=5)
        self.assertAlmostEqual(deriv_c2[1], deriv_c5[1], places=5)

        # dz should be different (depends on c)
        self.assertNotAlmostEqual(deriv_c2[2], deriv_c5[2], places=1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
