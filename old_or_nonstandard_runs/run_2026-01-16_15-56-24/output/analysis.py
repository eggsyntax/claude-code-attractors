"""
Quantitative analysis tools for chaotic dynamical systems.

This module provides rigorous mathematical analysis of attractors:
- Return maps: visualize successive Poincaré section crossings
- Divergence metrics: quantify the butterfly effect
- Lyapunov exponents: measure sensitivity to initial conditions
- Time delay embedding: reconstruct attractors from time series (Takens theorem)

All functions return structured data compatible with visualizer.py for plotting.

References:
- Sprott, J.C. (2003). Chaos and Time-Series Analysis
- Kantz, H. & Schreiber, T. (2004). Nonlinear Time Series Analysis
- Wolf et al. (1985). Determining Lyapunov exponents from a time series
"""

import numpy as np
from typing import Dict, Tuple, Optional, Union
import warnings


def compute_return_map(
    section_points: np.ndarray,
    dimension: int = 0,
    delay: int = 1
) -> Dict:
    """
    Compute return map from Poincaré section or time series data.

    A return map plots x_{n+delay} vs x_n, revealing structure in chaotic
    systems. Fixed points appear as points on the diagonal, periodic orbits
    as closed loops, and chaotic behavior as complex curves.

    Args:
        section_points: Array of shape (n_points, n_dims) from Poincaré section
                       or time series data
        dimension: Which dimension to analyze (0 for x, 1 for y, etc.)
        delay: Lag for the return map (1 means successive points)

    Returns:
        Dictionary with keys:
            - 'x_n': Array of x_n values
            - 'x_n_plus_delay': Array of x_{n+delay} values
            - 'dimension': The dimension analyzed
            - 'delay': The delay used
            - 'metadata': Additional information

    Example:
        >>> from rossler import RosslerAttractor
        >>> rossler = RosslerAttractor()
        >>> trajectory = rossler.generate_trajectory(t_span=(0, 500), n_points=50000)
        >>> section = rossler.compute_poincare_section(trajectory, plane='z', plane_value=0.0)
        >>> return_map = compute_return_map(section, dimension=0, delay=1)
        >>> # Can now plot return_map['x_n'] vs return_map['x_n_plus_delay']
    """
    if section_points.ndim == 1:
        section_points = section_points.reshape(-1, 1)

    if dimension >= section_points.shape[1]:
        raise ValueError(
            f"dimension {dimension} out of range for data with "
            f"{section_points.shape[1]} dimensions"
        )

    # Extract the specified dimension
    series = section_points[:, dimension]

    # Create return map: x_n vs x_{n+delay}
    n_points = len(series)
    if n_points <= delay:
        warnings.warn(f"Not enough points ({n_points}) for delay {delay}")
        return {
            'x_n': np.array([]),
            'x_n_plus_delay': np.array([]),
            'dimension': dimension,
            'delay': delay,
            'metadata': {'n_points': 0}
        }

    x_n = series[:-delay]
    x_n_plus_delay = series[delay:]

    return {
        'x_n': x_n,
        'x_n_plus_delay': x_n_plus_delay,
        'dimension': dimension,
        'delay': delay,
        'metadata': {
            'n_points': len(x_n),
            'x_range': (float(np.min(x_n)), float(np.max(x_n))),
            'description': f"Return map with delay {delay} on dimension {dimension}"
        }
    }


def compute_divergence(
    trajectory1: np.ndarray,
    trajectory2: np.ndarray,
    norm: str = 'euclidean'
) -> np.ndarray:
    """
    Compute divergence (separation distance) between two trajectories over time.

    This quantifies the butterfly effect: how quickly do nearby initial
    conditions separate? For chaotic systems, divergence grows exponentially
    until saturation.

    Args:
        trajectory1: Array of shape (n_points, n_dims)
        trajectory2: Array of shape (n_points, n_dims)
        norm: Distance metric ('euclidean', 'manhattan', 'max')

    Returns:
        Array of shape (n_points,) containing distance at each time step

    Raises:
        ValueError: If trajectories have different lengths or shapes

    Example:
        >>> from lorenz import LorenzAttractor
        >>> lorenz1 = LorenzAttractor()
        >>> lorenz2 = LorenzAttractor()
        >>> traj1 = lorenz1.generate_trajectory(t_span=(0, 20), n_points=2000)
        >>> lorenz2.initial_state = lorenz1.initial_state + [1e-8, 0, 0]
        >>> traj2 = lorenz2.generate_trajectory(t_span=(0, 20), n_points=2000)
        >>> divergence = compute_divergence(traj1, traj2)
        >>> # divergence shows exponential growth: butterfly effect!
    """
    if trajectory1.shape != trajectory2.shape:
        raise ValueError(
            f"Trajectories must have same shape. Got {trajectory1.shape} "
            f"and {trajectory2.shape}"
        )

    if len(trajectory1) != len(trajectory2):
        raise ValueError(
            f"Trajectories must have same length. Got {len(trajectory1)} "
            f"and {len(trajectory2)}"
        )

    # Compute pointwise distances
    if norm == 'euclidean':
        divergence = np.linalg.norm(trajectory1 - trajectory2, axis=1)
    elif norm == 'manhattan':
        divergence = np.sum(np.abs(trajectory1 - trajectory2), axis=1)
    elif norm == 'max':
        divergence = np.max(np.abs(trajectory1 - trajectory2), axis=1)
    else:
        raise ValueError(f"Unknown norm: {norm}. Use 'euclidean', 'manhattan', or 'max'")

    return divergence


def estimate_lyapunov_exponents(
    attractor,
    method: str = 'finitetime',
    t_span: Tuple[float, float] = (0, 100),
    n_points: int = 10000,
    include_diagnostics: bool = False,
    **kwargs
) -> Dict:
    """
    Estimate largest Lyapunov exponent for an attractor.

    The largest Lyapunov exponent (λ₁) measures sensitivity to initial conditions:
    - λ₁ > 0: chaotic (exponential divergence)
    - λ₁ = 0: periodic/quasiperiodic
    - λ₁ < 0: converging to fixed point

    Known values for validation:
    - Lorenz (σ=10, ρ=28, β=8/3): λ₁ ≈ 0.9
    - Rössler (a=0.2, b=0.2, c=5.7): λ₁ ≈ 0.07

    Args:
        attractor: AttractorBase instance
        method: 'finitetime' (fast) or 'wolf' (rigorous, if implemented)
        t_span: Time span for integration
        n_points: Number of time points
        include_diagnostics: If True, include error estimates and convergence data
        **kwargs: Additional method-specific parameters

    Returns:
        Dictionary with keys:
            - 'exponent': Estimated λ₁
            - 'method': Method used
            - 'std_error': Standard error (if include_diagnostics=True)
            - 'convergence_data': Evolution of estimate (if include_diagnostics=True)

    Example:
        >>> from lorenz import LorenzAttractor
        >>> lorenz = LorenzAttractor()
        >>> result = estimate_lyapunov_exponents(lorenz, method='finitetime')
        >>> print(f"λ₁ = {result['exponent']:.3f}")  # Should be ~0.9
    """
    if method == 'finitetime':
        return _lyapunov_finitetime(
            attractor, t_span, n_points, include_diagnostics, **kwargs
        )
    elif method == 'wolf':
        # Placeholder for future implementation
        raise NotImplementedError(
            "Wolf's algorithm not yet implemented. Use method='finitetime'"
        )
    else:
        raise ValueError(
            f"Unknown method: {method}. Use 'finitetime' or 'wolf'"
        )


def _lyapunov_finitetime(
    attractor,
    t_span: Tuple[float, float],
    n_points: int,
    include_diagnostics: bool,
    initial_separation: float = 1e-8,
    n_iterations: int = 50,
    renorm_interval: int = 5
) -> Dict:
    """
    Estimate Lyapunov exponent using finite-time divergence method.

    This method tracks how a small perturbation grows over time, periodically
    renormalizing to stay in the linear regime. It's fast but less accurate
    than Wolf's algorithm.

    Algorithm:
    1. Start with reference trajectory and nearby perturbed trajectory
    2. Let them evolve for short time
    3. Measure divergence (in log space)
    4. Renormalize perturbation to initial size
    5. Repeat and average

    Args:
        attractor: AttractorBase instance
        t_span: Time span for each iteration
        n_points: Points per iteration
        include_diagnostics: Include convergence data
        initial_separation: Initial perturbation magnitude
        n_iterations: Number of renormalization cycles
        renorm_interval: Points between renormalizations

    Returns:
        Dictionary with Lyapunov exponent and optional diagnostics
    """
    import copy

    # Storage for Lyapunov sums
    lyapunov_sums = []
    all_exponents = []  # For diagnostics

    # Reference attractor
    attractor_ref = copy.deepcopy(attractor)

    # Time per renormalization
    t_total = t_span[1] - t_span[0]
    t_renorm = t_total / n_iterations
    n_points_renorm = max(renorm_interval, n_points // n_iterations)

    # Initial state
    state_ref = attractor_ref.initial_state.copy()

    # Create initial perturbation (small random direction)
    perturbation = np.random.randn(len(state_ref))
    perturbation = perturbation / np.linalg.norm(perturbation) * initial_separation

    for iteration in range(n_iterations):
        # Set up reference and perturbed trajectories
        attractor_ref.initial_state = state_ref

        attractor_pert = copy.deepcopy(attractor_ref)
        attractor_pert.initial_state = state_ref + perturbation

        # Evolve both
        t_span_iter = (0, t_renorm)
        traj_ref = attractor_ref.generate_trajectory(
            t_span=t_span_iter,
            n_points=n_points_renorm
        )
        traj_pert = attractor_pert.generate_trajectory(
            t_span=t_span_iter,
            n_points=n_points_renorm
        )

        # Final states
        state_ref = traj_ref[-1]
        state_pert = traj_pert[-1]

        # Compute divergence
        final_separation = np.linalg.norm(state_pert - state_ref)

        # Avoid log(0)
        if final_separation < 1e-15:
            warnings.warn("Separation became too small, skipping iteration")
            continue

        # Lyapunov exponent contribution: (1/Δt) * log(final/initial)
        lyapunov_contribution = (1.0 / t_renorm) * np.log(
            final_separation / initial_separation
        )
        lyapunov_sums.append(lyapunov_contribution)

        # Running average
        current_estimate = np.mean(lyapunov_sums)
        all_exponents.append(current_estimate)

        # Renormalize perturbation
        perturbation = (state_pert - state_ref)
        perturbation = perturbation / np.linalg.norm(perturbation) * initial_separation

    # Final estimate
    if len(lyapunov_sums) == 0:
        raise RuntimeError("Failed to compute Lyapunov exponent (all iterations invalid)")

    exponent = np.mean(lyapunov_sums)

    result = {
        'exponent': float(exponent),
        'method': 'finitetime'
    }

    if include_diagnostics:
        result['std_error'] = float(np.std(lyapunov_sums) / np.sqrt(len(lyapunov_sums)))
        result['convergence_data'] = {
            'estimates': np.array(all_exponents),
            'n_iterations': n_iterations,
            'converged': len(all_exponents) == n_iterations
        }
        result['confidence_interval'] = (
            float(exponent - 1.96 * result['std_error']),
            float(exponent + 1.96 * result['std_error'])
        )

    return result


def compute_time_delay_embedding(
    time_series: np.ndarray,
    delay: int,
    embedding_dim: int
) -> np.ndarray:
    """
    Perform time delay embedding (Takens reconstruction).

    Takens' theorem: A chaotic attractor can be reconstructed from a single
    observable using time delays. This is powerful for analyzing experimental
    data where you can't measure all state variables.

    The embedding creates vectors:
    [x(t), x(t+τ), x(t+2τ), ..., x(t+(m-1)τ)]

    where τ is the delay and m is the embedding dimension.

    Args:
        time_series: 1D array of observations
        delay: Time delay τ (in units of sampling interval)
        embedding_dim: Embedding dimension m

    Returns:
        Array of shape (n_embedded, embedding_dim) containing embedded vectors

    Example:
        >>> from lorenz import LorenzAttractor
        >>> lorenz = LorenzAttractor()
        >>> trajectory = lorenz.generate_trajectory(t_span=(0, 50), n_points=5000)
        >>> x_only = trajectory[:, 0]  # Just x coordinate
        >>> embedded = compute_time_delay_embedding(x_only, delay=10, embedding_dim=3)
        >>> # embedded now reconstructs the 3D attractor from 1D signal!

    References:
        Takens, F. (1981). Detecting strange attractors in turbulence.
        Lecture Notes in Mathematics, 898, 366-381.
    """
    if time_series.ndim != 1:
        raise ValueError("time_series must be 1-dimensional")

    n = len(time_series)
    n_embedded = n - (embedding_dim - 1) * delay

    if n_embedded <= 0:
        raise ValueError(
            f"Time series too short ({n}) for embedding_dim={embedding_dim} "
            f"and delay={delay}. Need at least {(embedding_dim - 1) * delay + 1} points."
        )

    # Create embedded vectors
    embedded = np.zeros((n_embedded, embedding_dim))
    for i in range(embedding_dim):
        start_idx = i * delay
        end_idx = start_idx + n_embedded
        embedded[:, i] = time_series[start_idx:end_idx]

    return embedded


def compute_correlation_dimension(
    trajectory: np.ndarray,
    max_embedding_dim: int = 10,
    n_points: Optional[int] = None,
    r_min: Optional[float] = None,
    r_max: Optional[float] = None,
    n_radii: int = 50
) -> Dict:
    """
    Estimate correlation dimension using Grassberger-Procaccia algorithm.

    The correlation dimension D₂ is a measure of the fractal dimension of
    the attractor. For strange attractors, D₂ is non-integer:
    - Lorenz: D₂ ≈ 2.06
    - Rössler: D₂ ≈ 2.02

    WARNING: This is computationally expensive for large datasets!

    Args:
        trajectory: Array of shape (n_points, n_dims)
        max_embedding_dim: Maximum embedding dimension to test
        n_points: Subsample to this many points (for speed)
        r_min: Minimum radius for scaling region
        r_max: Maximum radius for scaling region
        n_radii: Number of radii to test

    Returns:
        Dictionary with keys:
            - 'dimension': Estimated correlation dimension
            - 'radii': Array of radii tested
            - 'correlations': Correlation integrals at each radius
            - 'fit_slope': Slope of log-log plot (= dimension)
            - 'fit_intercept': Intercept of log-log plot

    Note:
        This is a placeholder implementation. Full Grassberger-Procaccia
        algorithm requires careful selection of scaling region and
        embedding dimension convergence analysis.
    """
    # TODO: Implement full Grassberger-Procaccia algorithm
    # This is complex and requires careful handling of:
    # 1. Theiler correction (avoid temporal correlations)
    # 2. Scaling region identification
    # 3. Embedding dimension convergence
    # 4. Efficient distance computation (KD-tree or similar)

    raise NotImplementedError(
        "Correlation dimension estimation not yet fully implemented. "
        "This requires careful treatment of scaling regions and temporal "
        "correlations. See Grassberger & Procaccia (1983) for details."
    )


# Helper function for analysis
def compute_recurrence_rate(
    trajectory: np.ndarray,
    epsilon: float
) -> float:
    """
    Compute recurrence rate: fraction of points within epsilon of each other.

    This is a simple measure of attractor complexity. Higher recurrence
    indicates more structure/periodicity.

    Args:
        trajectory: Array of shape (n_points, n_dims)
        epsilon: Distance threshold

    Returns:
        Recurrence rate (between 0 and 1)
    """
    from scipy.spatial.distance import pdist, squareform

    # Compute all pairwise distances
    distances = squareform(pdist(trajectory))

    # Count pairs within epsilon (excluding diagonal)
    n = len(trajectory)
    recurrent_pairs = np.sum(distances < epsilon) - n  # Subtract diagonal
    total_pairs = n * (n - 1)

    return recurrent_pairs / total_pairs


if __name__ == '__main__':
    print("Analysis module for chaotic dynamical systems")
    print("\nAvailable functions:")
    print("  - compute_return_map: Return maps from Poincaré sections")
    print("  - compute_divergence: Quantify butterfly effect")
    print("  - estimate_lyapunov_exponents: Measure chaos strength")
    print("  - compute_time_delay_embedding: Reconstruct attractor from time series")
    print("\nSee docstrings for detailed usage and examples.")
