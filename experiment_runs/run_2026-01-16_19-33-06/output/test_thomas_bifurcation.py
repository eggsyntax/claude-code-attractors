"""
Unit tests for Thomas attractor bifurcation analysis.

Tests the mathematical correctness of bifurcation computation,
Poincaré section detection, and comparative analysis functionality.

Author: Bob
"""

import unittest
import numpy as np
from thomas_bifurcation import (
    thomas_system,
    poincare_section_thomas,
)


class TestThomasBifurcation(unittest.TestCase):
    """Test suite for Thomas bifurcation analysis."""

    def test_thomas_equations(self):
        """Test that Thomas differential equations are correct."""
        state = np.array([1.0, 0.5, -0.3])
        b = 0.2

        derivs = thomas_system(0, state, b)

        # Manual calculation
        expected = np.array([
            np.sin(0.5) - 0.2 * 1.0,      # sin(y) - b*x
            np.sin(-0.3) - 0.2 * 0.5,     # sin(z) - b*y
            np.sin(1.0) - 0.2 * (-0.3)    # sin(x) - b*z
        ])

        np.testing.assert_array_almost_equal(derivs, expected, decimal=10)

    def test_thomas_cyclical_symmetry(self):
        """Test that equations respect cyclical symmetry."""
        # The Thomas system has the property that
        # if (x,y,z) solves the system, then (y,z,x) also does
        state = np.array([0.5, -0.3, 0.8])
        b = 0.15

        # Original
        dx1, dy1, dz1 = thomas_system(0, state, b)

        # Rotated state (x,y,z) -> (y,z,x)
        rotated_state = np.array([state[1], state[2], state[0]])
        dx2, dy2, dz2 = thomas_system(0, rotated_state, b)

        # The derivatives should also be rotated
        # (dx,dy,dz) -> (dy,dz,dx)
        np.testing.assert_array_almost_equal(
            [dy1, dz1, dx1],
            [dx2, dy2, dz2],
            decimal=10
        )

    def test_thomas_bounded_derivatives(self):
        """Test that derivatives are bounded due to sin() terms."""
        # Since sin() is bounded by [-1, 1], and we have terms like sin(y) - b*x,
        # the derivatives should be bounded
        state = np.array([2.0, 1.5, -1.8])
        b = 0.3

        derivs = thomas_system(0, state, b)

        # Each derivative is of form sin(...) - b*coord
        # Maximum magnitude should be approximately 1 + b*max(|coord|)
        max_coord = np.max(np.abs(state))
        expected_max = 1.0 + b * max_coord

        for deriv in derivs:
            self.assertLess(abs(deriv), expected_max + 0.1)  # Small tolerance

    def test_poincare_section_returns_samples(self):
        """Test that Poincaré section returns crossing points."""
        b = 0.2
        crossings = poincare_section_thomas(
            b,
            x0=np.array([0.1, 0, 0]),
            t_transient=100,
            t_sample=500
        )

        # Should get some crossings
        self.assertGreater(len(crossings), 0)

        # Crossings should be finite numbers
        for crossing in crossings:
            self.assertTrue(np.isfinite(crossing))

    def test_poincare_varies_with_parameter(self):
        """Test that Poincaré section changes with parameter b."""
        b1 = 0.1
        b2 = 0.4

        crossings1 = poincare_section_thomas(b1, t_transient=200, t_sample=800)
        crossings2 = poincare_section_thomas(b2, t_transient=200, t_sample=800)

        # Different parameters should give different behavior
        # (at minimum, different number of crossings or values)
        mean1 = np.mean(crossings1) if len(crossings1) > 0 else 0
        mean2 = np.mean(crossings2) if len(crossings2) > 0 else 0

        # They should be noticeably different
        self.assertNotAlmostEqual(mean1, mean2, places=1)

    def test_thomas_attractor_convergence(self):
        """Test that trajectories converge to the attractor."""
        from scipy.integrate import solve_ivp

        b = 0.18
        x0_1 = np.array([0.1, 0.0, 0.0])
        x0_2 = np.array([0.5, 0.5, 0.5])

        # Integrate both from different initial conditions
        t_span = (0, 1000)
        t_eval = np.linspace(900, 1000, 1000)  # Sample late times

        sol1 = solve_ivp(thomas_system, t_span, x0_1, args=(b,),
                        t_eval=t_eval, method='RK45', rtol=1e-9)
        sol2 = solve_ivp(thomas_system, t_span, x0_2, args=(b,),
                        t_eval=t_eval, method='RK45', rtol=1e-9)

        # After convergence, both should visit similar regions
        # (not identical due to chaos, but similar statistics)
        range1 = np.ptp(sol1.y[0])  # Peak-to-peak of x coordinate
        range2 = np.ptp(sol2.y[0])

        # Ranges should be comparable (within factor of 2)
        self.assertLess(abs(range1 - range2) / max(range1, range2), 0.5)

    def test_thomas_b_parameter_effect(self):
        """Test that parameter b affects attractor size as expected."""
        from scipy.integrate import solve_ivp

        # Higher b means stronger damping -> smaller attractor
        b_small = 0.1
        b_large = 0.4

        x0 = np.array([0.1, 0.0, 0.0])
        t_span = (0, 500)
        t_eval = np.linspace(400, 500, 1000)

        sol_small = solve_ivp(thomas_system, t_span, x0, args=(b_small,),
                             t_eval=t_eval, method='RK45', rtol=1e-9)
        sol_large = solve_ivp(thomas_system, t_span, x0, args=(b_large,),
                             t_eval=t_eval, method='RK45', rtol=1e-9)

        # Smaller b should give larger attractor
        size_small = np.max(np.linalg.norm(sol_small.y, axis=0))
        size_large = np.max(np.linalg.norm(sol_large.y, axis=0))

        self.assertGreater(size_small, size_large)

    def test_thomas_origin_fixed_point(self):
        """Test that origin is a fixed point for any b."""
        state = np.array([0.0, 0.0, 0.0])
        b_values = [0.1, 0.2, 0.5]

        for b in b_values:
            derivs = thomas_system(0, state, b)
            # At origin, sin(0) - b*0 = 0 for all three equations
            np.testing.assert_array_almost_equal(
                derivs,
                np.array([0.0, 0.0, 0.0]),
                decimal=12
            )


class TestComparativeAnalysis(unittest.TestCase):
    """Test comparative analysis across attractors."""

    def test_all_systems_are_chaotic(self):
        """Test that all three systems exhibit sensitive dependence."""
        from comparative_analysis import lorenz, rossler, thomas, simulate_attractor

        systems = [
            (lorenz, np.array([1.0, 1.0, 1.0]),
             {'sigma': 10, 'rho': 28, 'beta': 8/3}),
            (rossler, np.array([1.0, 1.0, 1.0]),
             {'a': 0.2, 'b': 0.2, 'c': 5.7}),
            (thomas, np.array([0.1, 0.0, 0.0]),
             {'b': 0.18}),
        ]

        epsilon = 1e-8
        t_max = 20

        for system, x0, params in systems:
            # Original trajectory
            traj1 = simulate_attractor(system, x0, t_max=t_max, dt=0.01, **params)

            # Perturbed trajectory
            x0_pert = x0 + np.array([epsilon, 0, 0])
            traj2 = simulate_attractor(system, x0_pert, t_max=t_max, dt=0.01, **params)

            # Calculate divergence
            distance = np.linalg.norm(traj1 - traj2, axis=0)

            # Should amplify significantly (chaos!)
            amplification = distance[-1] / distance[0]
            self.assertGreater(amplification, 100,
                             f"System should be chaotic (amplification: {amplification})")

    def test_thomas_has_smallest_lyapunov(self):
        """Test that Thomas has gentler chaos than Lorenz/Rössler."""
        from comparative_analysis import lorenz, rossler, thomas, simulate_attractor

        systems = [
            ('Lorenz', lorenz, np.array([1.0, 1.0, 1.0]),
             {'sigma': 10, 'rho': 28, 'beta': 8/3}),
            ('Rössler', rossler, np.array([1.0, 1.0, 1.0]),
             {'a': 0.2, 'b': 0.2, 'c': 5.7}),
            ('Thomas', thomas, np.array([0.1, 0.0, 0.0]),
             {'b': 0.18}),
        ]

        epsilon = 1e-8
        t_max = 20

        amplifications = {}

        for name, system, x0, params in systems:
            traj1 = simulate_attractor(system, x0, t_max=t_max, dt=0.01, **params)
            x0_pert = x0 + np.array([epsilon, 0, 0])
            traj2 = simulate_attractor(system, x0_pert, t_max=t_max, dt=0.01, **params)

            distance = np.linalg.norm(traj1 - traj2, axis=0)
            amplifications[name] = distance[-1] / distance[0]

        # Thomas should have smallest amplification (gentlest chaos)
        self.assertLess(amplifications['Thomas'], amplifications['Lorenz'])
        self.assertLess(amplifications['Thomas'], amplifications['Rössler'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
