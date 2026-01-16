"""
Comprehensive tests for analysis.py module.

Following TDD principles: writing tests before implementation to validate:
- Return map computation from Poincaré sections and time series
- Trajectory divergence metrics (butterfly effect quantification)
- Lyapunov exponent estimation (validate against known values)
- Statistical rigor (error estimates, convergence diagnostics)

Known validation targets:
- Lorenz (σ=10, ρ=28, β=8/3): λ₁ ≈ 0.9, D₂ ≈ 2.06
- Rössler (a=0.2, b=0.2, c=5.7): λ₁ ≈ 0.07, D₂ ≈ 2.02
"""

import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_allclose
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# These will be implemented
from analysis import (
    compute_return_map,
    compute_divergence,
    estimate_lyapunov_exponents,
    compute_time_delay_embedding
)

# Import our attractors for validation tests
from lorenz import LorenzAttractor
from rossler import RosslerAttractor


class TestReturnMap:
    """Tests for return map computation from sequence data."""

    def test_basic_return_map_structure(self):
        """Return map should return x_n vs x_{n+delay} data structure."""
        # Simple sequence: 1, 2, 3, 4, 5
        section_points = np.array([[1, 0], [2, 0], [3, 0], [4, 0], [5, 0]])

        result = compute_return_map(section_points, dimension=0, delay=1)

        # Check structure
        assert isinstance(result, dict)
        assert 'x_n' in result
        assert 'x_n_plus_delay' in result
        assert 'dimension' in result
        assert 'delay' in result
        assert 'metadata' in result

        # Check values
        assert_array_almost_equal(result['x_n'], np.array([1, 2, 3, 4]))
        assert_array_almost_equal(result['x_n_plus_delay'], np.array([2, 3, 4, 5]))
        assert result['dimension'] == 0
        assert result['delay'] == 1

    def test_return_map_with_delay_2(self):
        """Return map should handle arbitrary delays."""
        section_points = np.array([[i, 0] for i in range(10)])

        result = compute_return_map(section_points, dimension=0, delay=2)

        # x_n: [0,1,2,3,4,5,6,7], x_{n+2}: [2,3,4,5,6,7,8,9]
        assert len(result['x_n']) == 8
        assert_array_almost_equal(result['x_n'], np.arange(8))
        assert_array_almost_equal(result['x_n_plus_delay'], np.arange(2, 10))
        assert result['delay'] == 2

    def test_return_map_multidimensional(self):
        """Return map should work on 2D Poincaré section points."""
        # Spiral-like points
        t = np.linspace(0, 4*np.pi, 100)
        section_points = np.column_stack([
            t * np.cos(t),
            t * np.sin(t)
        ])

        # Dimension 0 (x-coordinate)
        result = compute_return_map(section_points, dimension=0, delay=1)
        assert len(result['x_n']) == 99
        assert result['dimension'] == 0

        # Dimension 1 (y-coordinate)
        result = compute_return_map(section_points, dimension=1, delay=1)
        assert len(result['x_n']) == 99
        assert result['dimension'] == 1

    def test_return_map_insufficient_data(self):
        """Return map should handle edge cases gracefully."""
        # Only 2 points - can't form a return map with delay > 1
        section_points = np.array([[1, 0], [2, 0]])

        result = compute_return_map(section_points, dimension=0, delay=2)

        # Should return empty arrays or minimal valid data
        assert len(result['x_n']) == 0 or len(result['x_n']) < 2

    def test_return_map_from_periodic_orbit(self):
        """Return map from periodic orbit should show fixed points."""
        # Simple periodic: 1, 2, 3, 1, 2, 3, 1, 2, 3
        periodic = np.array([1, 2, 3] * 5)
        section_points = np.column_stack([periodic, np.zeros_like(periodic)])

        result = compute_return_map(section_points, dimension=0, delay=1)

        # The map should cycle: 1->2, 2->3, 3->1
        assert 1 in result['x_n'] and 2 in result['x_n_plus_delay'][result['x_n'] == 1]
        assert 2 in result['x_n'] and 3 in result['x_n_plus_delay'][result['x_n'] == 2]
        assert 3 in result['x_n'] and 1 in result['x_n_plus_delay'][result['x_n'] == 3]


class TestDivergence:
    """Tests for trajectory divergence computation."""

    def test_divergence_identical_trajectories(self):
        """Divergence of identical trajectories should be zero."""
        traj = np.random.randn(1000, 3)

        div = compute_divergence(traj, traj)

        assert_array_almost_equal(div, np.zeros(1000), decimal=10)

    def test_divergence_structure(self):
        """Divergence should return array of distances over time."""
        traj1 = np.random.randn(1000, 3)
        traj2 = traj1 + 0.01 * np.random.randn(1000, 3)

        div = compute_divergence(traj1, traj2)

        assert isinstance(div, np.ndarray)
        assert len(div) == 1000
        assert np.all(div >= 0)  # Distances are non-negative

    def test_divergence_grows_exponentially_for_chaos(self):
        """For chaotic systems, nearby trajectories should diverge exponentially."""
        # Use Lorenz attractor with slightly different initial conditions
        lorenz1 = LorenzAttractor()
        lorenz2 = LorenzAttractor()

        # Very close initial conditions
        traj1 = lorenz1.generate_trajectory(t_span=(0, 10), n_points=1000)

        lorenz2.initial_state = lorenz1.initial_state + np.array([0.0001, 0, 0])
        traj2 = lorenz2.generate_trajectory(t_span=(0, 10), n_points=1000)

        div = compute_divergence(traj1, traj2)

        # Early divergence should be small
        assert div[0] < 0.001

        # Should grow significantly (exponentially for chaotic system)
        # After some time, divergence should be much larger
        assert div[-1] > div[0] * 10

        # Check for exponential growth in early phase (before saturation)
        # Take log of first part where it's growing
        early_div = div[10:100]  # Skip first few points
        early_div = early_div[early_div > 1e-10]  # Remove zeros
        if len(early_div) > 10:
            log_div = np.log(early_div)
            # Should be approximately linear in log space (exponential growth)
            # Simple check: correlation between log(div) and time should be high
            time_indices = np.arange(len(log_div))
            correlation = np.corrcoef(log_div, time_indices)[0, 1]
            assert correlation > 0.8, "Divergence should grow exponentially initially"

    def test_divergence_different_lengths_error(self):
        """Divergence should error on mismatched trajectory lengths."""
        traj1 = np.random.randn(100, 3)
        traj2 = np.random.randn(50, 3)

        with pytest.raises(ValueError, match="same length"):
            compute_divergence(traj1, traj2)

    def test_divergence_constant_offset(self):
        """Divergence with constant spatial offset should be constant."""
        traj1 = np.random.randn(1000, 3)
        offset = np.array([1.0, 2.0, 3.0])
        traj2 = traj1 + offset

        div = compute_divergence(traj1, traj2)

        # All distances should be equal to norm of offset
        expected_distance = np.linalg.norm(offset)
        assert_allclose(div, expected_distance * np.ones(1000), rtol=1e-6)


class TestLyapunovExponents:
    """Tests for Lyapunov exponent estimation."""

    def test_lyapunov_basic_structure(self):
        """Lyapunov estimation should return structured results."""
        lorenz = LorenzAttractor()

        result = estimate_lyapunov_exponents(
            lorenz,
            method='finitetime',
            t_span=(0, 50),
            n_points=5000
        )

        # Check structure
        assert isinstance(result, dict)
        assert 'exponent' in result
        assert 'method' in result
        assert result['method'] == 'finitetime'
        assert isinstance(result['exponent'], (float, np.floating))

    def test_lyapunov_with_diagnostics(self):
        """Lyapunov with diagnostics should include error estimates."""
        lorenz = LorenzAttractor()

        result = estimate_lyapunov_exponents(
            lorenz,
            method='finitetime',
            include_diagnostics=True
        )

        assert 'exponent' in result
        assert 'std_error' in result or 'confidence_interval' in result
        assert 'convergence_data' in result

    def test_lyapunov_lorenz_positive(self):
        """Lorenz attractor should have positive Lyapunov exponent (chaos)."""
        lorenz = LorenzAttractor()  # Default chaotic parameters

        result = estimate_lyapunov_exponents(
            lorenz,
            method='finitetime',
            t_span=(0, 100),
            n_points=10000
        )

        # Should be positive (chaotic)
        assert result['exponent'] > 0, "Lorenz attractor should have positive λ₁"

        # Should be roughly in the right range (λ₁ ≈ 0.9 for standard params)
        # Allow wide tolerance since finite-time method is approximate
        assert 0.5 < result['exponent'] < 1.5, f"Expected λ₁ ≈ 0.9, got {result['exponent']}"

    def test_lyapunov_rossler_positive(self):
        """Rössler attractor should have positive Lyapunov exponent (chaos)."""
        rossler = RosslerAttractor()  # Default chaotic parameters

        result = estimate_lyapunov_exponents(
            rossler,
            method='finitetime',
            t_span=(0, 200),
            n_points=20000
        )

        # Should be positive but smaller than Lorenz (λ₁ ≈ 0.07)
        assert result['exponent'] > 0, "Rössler attractor should have positive λ₁"
        assert result['exponent'] < 0.5, f"Rössler λ₁ should be small, got {result['exponent']}"

    def test_lyapunov_fixed_point_negative(self):
        """System converging to fixed point should have negative exponent."""
        # Lorenz with parameters that converge to origin
        lorenz = LorenzAttractor()
        lorenz.update_parameters({'rho': 0.5})  # Below critical value

        result = estimate_lyapunov_exponents(
            lorenz,
            method='finitetime',
            t_span=(0, 50),
            n_points=5000
        )

        # Should be negative (converging)
        assert result['exponent'] < 0, "Converging system should have negative λ₁"

    def test_lyapunov_method_comparison(self):
        """Different methods should give roughly consistent results."""
        lorenz = LorenzAttractor()

        result_finite = estimate_lyapunov_exponents(
            lorenz,
            method='finitetime',
            t_span=(0, 100),
            n_points=10000
        )

        # If Wolf method is implemented, compare
        try:
            result_wolf = estimate_lyapunov_exponents(
                lorenz,
                method='wolf',
                t_span=(0, 100),
                n_points=10000
            )

            # Should have same sign and similar magnitude
            assert np.sign(result_finite['exponent']) == np.sign(result_wolf['exponent'])

            # Within factor of 2 (methods have different accuracy)
            ratio = result_finite['exponent'] / result_wolf['exponent']
            assert 0.5 < ratio < 2.0, "Methods should give similar results"
        except (NotImplementedError, ValueError):
            pytest.skip("Wolf method not yet implemented")

    def test_lyapunov_invalid_method(self):
        """Should raise error for invalid method."""
        lorenz = LorenzAttractor()

        with pytest.raises(ValueError, match="method"):
            estimate_lyapunov_exponents(lorenz, method='invalid_method')


class TestTimeDelayEmbedding:
    """Tests for time delay embedding (Takens theorem)."""

    def test_embedding_basic_structure(self):
        """Embedding should create higher-dimensional vectors."""
        # Simple 1D time series
        time_series = np.sin(np.linspace(0, 10*np.pi, 1000))

        embedded = compute_time_delay_embedding(
            time_series,
            delay=10,
            embedding_dim=3
        )

        # Should create 3D vectors from 1D signal
        assert embedded.shape[1] == 3
        assert embedded.shape[0] < len(time_series)  # Some points lost due to delay

    def test_embedding_reconstruction(self):
        """Embedded points should contain original signal information."""
        time_series = np.sin(np.linspace(0, 10*np.pi, 1000))

        embedded = compute_time_delay_embedding(
            time_series,
            delay=10,
            embedding_dim=3
        )

        # First column should be time_series[0:-2*delay]
        # Second column should be time_series[delay:-delay]
        # Third column should be time_series[2*delay:]
        n_embedded = embedded.shape[0]
        assert_array_almost_equal(
            embedded[:, 0],
            time_series[:n_embedded]
        )

    def test_embedding_preserves_dynamics(self):
        """Embedding should preserve attractor structure (Takens theorem)."""
        # Generate Lorenz attractor, take one coordinate
        lorenz = LorenzAttractor()
        trajectory = lorenz.generate_trajectory(t_span=(0, 50), n_points=5000)
        x_component = trajectory[:, 0]  # Just x coordinate

        # Embed in 3D
        embedded = compute_time_delay_embedding(
            x_component,
            delay=10,
            embedding_dim=3
        )

        # Embedded attractor should have similar properties
        # Check that it's bounded (like original Lorenz)
        assert embedded.shape[1] == 3
        for dim in range(3):
            assert np.std(embedded[:, dim]) > 0, "Should have variation"
            assert np.abs(np.mean(embedded[:, dim])) < 50, "Should be bounded"


class TestValidationAgainstKnownResults:
    """Integration tests validating against published results."""

    def test_lorenz_standard_parameters_lyapunov(self):
        """Lorenz (σ=10, ρ=28, β=8/3) should have λ₁ ≈ 0.9."""
        lorenz = LorenzAttractor()  # These are the defaults
        assert lorenz.parameters['sigma'] == 10
        assert lorenz.parameters['rho'] == 28
        assert lorenz.parameters['beta'] == 8/3

        # Long trajectory for accurate estimation
        result = estimate_lyapunov_exponents(
            lorenz,
            method='finitetime',
            t_span=(0, 200),
            n_points=20000,
            include_diagnostics=True
        )

        # Should be close to 0.9 (allow 30% tolerance for finite-time method)
        expected = 0.9
        tolerance = 0.3
        assert expected * (1 - tolerance) < result['exponent'] < expected * (1 + tolerance), \
            f"Expected λ₁ ≈ {expected}, got {result['exponent']}"

    def test_rossler_standard_parameters_lyapunov(self):
        """Rössler (a=0.2, b=0.2, c=5.7) should have λ₁ ≈ 0.07."""
        rossler = RosslerAttractor()  # These are the defaults
        assert rossler.parameters['a'] == 0.2
        assert rossler.parameters['b'] == 0.2
        assert rossler.parameters['c'] == 5.7

        # Very long trajectory for accurate estimation (Rössler is slower)
        result = estimate_lyapunov_exponents(
            rossler,
            method='finitetime',
            t_span=(0, 500),
            n_points=50000,
            include_diagnostics=True
        )

        # Should be close to 0.07 (allow 50% tolerance for finite-time method)
        expected = 0.07
        tolerance = 0.5
        assert expected * (1 - tolerance) < result['exponent'] < expected * (1 + tolerance), \
            f"Expected λ₁ ≈ {expected}, got {result['exponent']}"

    def test_butterfly_effect_quantification(self):
        """Should quantify exponential divergence (butterfly effect)."""
        lorenz = LorenzAttractor()

        # Generate two trajectories with tiny difference
        traj1 = lorenz.generate_trajectory(t_span=(0, 20), n_points=2000)

        lorenz.initial_state = lorenz.initial_state + np.array([1e-8, 0, 0])
        traj2 = lorenz.generate_trajectory(t_span=(0, 20), n_points=2000)

        div = compute_divergence(traj1, traj2)

        # Initial divergence should be tiny
        assert div[0] < 1e-6

        # Should grow exponentially with rate ~ λ₁
        # Find where divergence has grown by factor of e
        e_fold_index = np.where(div > div[0] * np.e)[0]
        if len(e_fold_index) > 0:
            e_fold_time = 20 * e_fold_index[0] / 2000
            estimated_lyapunov = 1.0 / e_fold_time

            # Should be roughly consistent with known λ₁ ≈ 0.9
            # (very rough estimate, allow wide tolerance)
            assert 0.3 < estimated_lyapunov < 2.0, \
                f"Divergence rate implies λ₁ ≈ {estimated_lyapunov}, expected ~0.9"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
