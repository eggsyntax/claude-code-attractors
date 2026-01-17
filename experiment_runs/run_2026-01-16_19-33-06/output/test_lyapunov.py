"""
Unit tests for Lyapunov exponent calculations.

These tests verify the mathematical correctness of the Lyapunov exponent
computation and ensure the results match theoretical expectations for
known dynamical systems.
"""

import unittest
import numpy as np
from lyapunov import compute_lyapunov_exponent, lyapunov_spectrum


class TestLyapunovExponents(unittest.TestCase):
    """Test suite for Lyapunov exponent calculations."""

    def test_lorenz_positive_exponent_in_chaotic_regime(self):
        """
        Test that Lorenz system has positive largest Lyapunov exponent in chaotic regime.

        For ρ=28 (classic chaotic parameters), the largest Lyapunov exponent
        should be positive, indicating chaos.
        """
        def lorenz(t, state, sigma=10.0, rho=28.0, beta=8.0/3.0):
            x, y, z = state
            return np.array([
                sigma * (y - x),
                x * (rho - z) - y,
                x * y - beta * z
            ])

        initial_state = np.array([1.0, 1.0, 1.0])
        lambda_max = compute_lyapunov_exponent(
            lorenz, initial_state, dt=0.01, total_time=50.0
        )

        # For ρ=28, λ_max ≈ 0.9, should definitely be positive
        self.assertGreater(lambda_max, 0.0,
                          "Largest Lyapunov exponent should be positive in chaotic regime")
        self.assertLess(lambda_max, 2.0,
                       "Lyapunov exponent should be reasonable magnitude")

    def test_lorenz_negative_exponent_in_stable_regime(self):
        """
        Test that Lorenz system has negative largest Lyapunov exponent in stable regime.

        For ρ=10 (below critical value ~24.74), the system should converge to
        a fixed point, indicated by negative Lyapunov exponent.
        """
        def lorenz(t, state, sigma=10.0, rho=10.0, beta=8.0/3.0):
            x, y, z = state
            return np.array([
                sigma * (y - x),
                x * (rho - z) - y,
                x * y - beta * z
            ])

        initial_state = np.array([1.0, 1.0, 1.0])
        lambda_max = compute_lyapunov_exponent(
            lorenz, initial_state, dt=0.01, total_time=50.0
        )

        # Below the bifurcation, should have negative exponent
        self.assertLess(lambda_max, 0.0,
                       "Largest Lyapunov exponent should be negative in stable regime")

    def test_rossler_positive_exponent_in_chaotic_regime(self):
        """
        Test that Rössler system has positive Lyapunov exponent in chaotic regime.

        For c=5.7 (well into chaotic regime), the system should be chaotic.
        """
        def rossler(t, state, a=0.2, b=0.2, c=5.7):
            x, y, z = state
            return np.array([
                -y - z,
                x + a * y,
                b + z * (x - c)
            ])

        initial_state = np.array([1.0, 1.0, 1.0])
        lambda_max = compute_lyapunov_exponent(
            rossler, initial_state, dt=0.01, total_time=50.0
        )

        # Should be positive in chaotic regime
        self.assertGreater(lambda_max, 0.0,
                          "Largest Lyapunov exponent should be positive for chaotic Rössler")

    def test_exponential_divergence_matches_lyapunov(self):
        """
        Test that actual trajectory divergence matches predicted exponential growth.

        The Lyapunov exponent λ predicts that separation grows as δ(t) ≈ δ₀ * e^(λt).
        We verify this relationship holds approximately.
        """
        def lorenz(t, state, sigma=10.0, rho=28.0, beta=8.0/3.0):
            x, y, z = state
            return np.array([
                sigma * (y - x),
                x * (rho - z) - y,
                x * y - beta * z
            ])

        initial_state = np.array([1.0, 1.0, 1.0])
        lambda_max = compute_lyapunov_exponent(
            lorenz, initial_state, dt=0.01, total_time=50.0
        )

        # Now simulate two nearby trajectories and measure actual divergence
        from scipy.integrate import solve_ivp

        epsilon = 1e-8
        perturbed_state = initial_state + epsilon

        t_span = (0, 10.0)
        t_eval = np.linspace(0, 10.0, 1000)

        sol1 = solve_ivp(lorenz, t_span, initial_state, t_eval=t_eval,
                        method='RK45', rtol=1e-8, atol=1e-10)
        sol2 = solve_ivp(lorenz, t_span, perturbed_state, t_eval=t_eval,
                        method='RK45', rtol=1e-8, atol=1e-10)

        # Measure divergence at t=5 seconds
        separation_at_5s = np.linalg.norm(sol1.y[:, 500] - sol2.y[:, 500])
        predicted_separation = epsilon * np.exp(lambda_max * 5.0)

        # Should be within same order of magnitude (factor of 10)
        ratio = separation_at_5s / predicted_separation
        self.assertGreater(ratio, 0.1,
                          "Actual divergence should match predicted order of magnitude")
        self.assertLess(ratio, 10.0,
                       "Actual divergence should match predicted order of magnitude")

    def test_lyapunov_spectrum_sum_property(self):
        """
        Test that Lyapunov spectrum sum matches divergence/convergence of phase volume.

        For dissipative systems (like Lorenz and Rössler), the sum of all Lyapunov
        exponents should be negative (phase volume contracts).
        """
        def lorenz(t, state, sigma=10.0, rho=28.0, beta=8.0/3.0):
            x, y, z = state
            return np.array([
                sigma * (y - x),
                x * (rho - z) - y,
                x * y - beta * z
            ])

        initial_state = np.array([1.0, 1.0, 1.0])
        spectrum = lyapunov_spectrum(
            lorenz, initial_state, dt=0.01, total_time=50.0
        )

        # Sum should be negative for dissipative system
        spectrum_sum = np.sum(spectrum)
        self.assertLess(spectrum_sum, 0.0,
                       "Sum of Lyapunov exponents should be negative for dissipative system")

        # For Lorenz with standard parameters, sum ≈ -(σ + 1 + β) ≈ -13.67
        self.assertGreater(spectrum_sum, -20.0,
                          "Spectrum sum should match theoretical prediction")

    def test_lyapunov_spectrum_ordering(self):
        """
        Test that Lyapunov exponents are properly ordered (largest to smallest).

        By convention, Lyapunov exponents are ordered: λ₁ ≥ λ₂ ≥ λ₃.
        """
        def lorenz(t, state, sigma=10.0, rho=28.0, beta=8.0/3.0):
            x, y, z = state
            return np.array([
                sigma * (y - x),
                x * (rho - z) - y,
                x * y - beta * z
            ])

        initial_state = np.array([1.0, 1.0, 1.0])
        spectrum = lyapunov_spectrum(
            lorenz, initial_state, dt=0.01, total_time=50.0
        )

        # Should have 3 exponents for 3D system
        self.assertEqual(len(spectrum), 3,
                        "Should compute 3 Lyapunov exponents for 3D system")

        # Should be ordered
        self.assertGreaterEqual(spectrum[0], spectrum[1],
                               "Exponents should be in descending order")
        self.assertGreaterEqual(spectrum[1], spectrum[2],
                               "Exponents should be in descending order")

    def test_lyapunov_signature_for_chaos(self):
        """
        Test that chaotic attractor has the signature Lyapunov spectrum: (+, 0, -).

        Strange attractors typically have one positive, one near-zero (tangent to flow),
        and one negative exponent.
        """
        def lorenz(t, state, sigma=10.0, rho=28.0, beta=8.0/3.0):
            x, y, z = state
            return np.array([
                sigma * (y - x),
                x * (rho - z) - y,
                x * y - beta * z
            ])

        initial_state = np.array([1.0, 1.0, 1.0])
        spectrum = lyapunov_spectrum(
            lorenz, initial_state, dt=0.01, total_time=50.0
        )

        # Check (+, 0, -) signature
        self.assertGreater(spectrum[0], 0.0,
                          "Largest exponent should be positive (chaos)")
        self.assertLess(abs(spectrum[1]), 0.2,
                       "Middle exponent should be near zero (flow direction)")
        self.assertLess(spectrum[2], 0.0,
                       "Smallest exponent should be negative (dissipation)")

    def test_consistency_across_initial_conditions(self):
        """
        Test that Lyapunov exponents are invariant to initial conditions.

        Once on the attractor, the Lyapunov exponent should be the same
        regardless of where you start.
        """
        def lorenz(t, state, sigma=10.0, rho=28.0, beta=8.0/3.0):
            x, y, z = state
            return np.array([
                sigma * (y - x),
                x * (rho - z) - y,
                x * y - beta * z
            ])

        initial_state_1 = np.array([1.0, 1.0, 1.0])
        initial_state_2 = np.array([5.0, 5.0, 15.0])

        lambda1 = compute_lyapunov_exponent(
            lorenz, initial_state_1, dt=0.01, total_time=50.0
        )
        lambda2 = compute_lyapunov_exponent(
            lorenz, initial_state_2, dt=0.01, total_time=50.0
        )

        # Should agree within ~10% (some variation due to finite integration time)
        relative_difference = abs(lambda1 - lambda2) / abs(lambda1)
        self.assertLess(relative_difference, 0.15,
                       "Lyapunov exponent should be independent of initial conditions")


if __name__ == '__main__':
    unittest.main()
