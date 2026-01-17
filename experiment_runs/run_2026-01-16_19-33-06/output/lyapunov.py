"""
Lyapunov Exponent Calculation for Dynamical Systems

This module computes Lyapunov exponents, which quantify the rate of separation
of infinitesimally close trajectories in phase space. They are the fundamental
measure of chaos - positive Lyapunov exponents indicate exponential divergence
and unpredictability.

The largest Lyapunov exponent λ_max determines the system's character:
- λ_max < 0: Trajectories converge → stable fixed point or limit cycle
- λ_max ≈ 0: Marginal stability → periodic or quasi-periodic motion
- λ_max > 0: Trajectories diverge → chaos

For a chaotic attractor, the full spectrum typically has signature (+, 0, -):
one positive (divergence), one zero (flow direction), one negative (dissipation).

Mathematical Background:
-----------------------
The Lyapunov exponent measures how a small perturbation δ(t) grows over time:

    δ(t) ≈ δ₀ * e^(λt)

Taking logarithms: λ = lim(t→∞) [1/t * ln(|δ(t)|/|δ₀|)]

We compute this by tracking the evolution of tangent vectors - small perturbations
that are repeatedly renormalized to prevent numerical overflow.
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import Callable, Tuple


def compute_jacobian(equations: Callable, state: np.ndarray, dt: float = 1e-6) -> np.ndarray:
    """
    Compute the Jacobian matrix using finite differences.

    The Jacobian J[i,j] = ∂f_i/∂x_j describes how the flow changes with position.

    Args:
        equations: Function f(t, state) returning derivatives
        state: Current state vector
        dt: Step size for finite differences

    Returns:
        Jacobian matrix (n x n) where n is state dimension
    """
    n = len(state)
    J = np.zeros((n, n))

    # Compute each column by perturbing that variable
    for i in range(n):
        state_plus = state.copy()
        state_minus = state.copy()
        state_plus[i] += dt
        state_minus[i] -= dt

        # Central difference approximation
        deriv_plus = equations(0, state_plus)
        deriv_minus = equations(0, state_minus)
        J[:, i] = (deriv_plus - deriv_minus) / (2 * dt)

    return J


def compute_lyapunov_exponent(
    equations: Callable,
    initial_state: np.ndarray,
    dt: float = 0.01,
    total_time: float = 100.0,
    transient_time: float = 10.0,
    renorm_interval: int = 10
) -> float:
    """
    Compute the largest Lyapunov exponent using the tangent vector method.

    This tracks how a small perturbation grows along the trajectory, periodically
    renormalizing to prevent overflow. The average growth rate gives λ_max.

    Algorithm:
    1. Integrate the main trajectory
    2. Track a tangent vector (small perturbation) using the linearized flow
    3. Periodically renormalize the tangent vector
    4. Average the logarithmic growth rates

    Args:
        equations: ODE system f(t, state) returning derivatives
        initial_state: Starting point in phase space
        dt: Integration time step
        total_time: Total integration time
        transient_time: Time to wait before measuring (let attractor settle)
        renorm_interval: Steps between renormalizations

    Returns:
        Largest Lyapunov exponent λ_max

    Example:
        >>> def lorenz(t, state, sigma=10.0, rho=28.0, beta=8/3):
        ...     x, y, z = state
        ...     return np.array([sigma*(y-x), x*(rho-z)-y, x*y-beta*z])
        >>> λ = compute_lyapunov_exponent(lorenz, [1.0, 1.0, 1.0])
        >>> print(f"Lorenz λ_max ≈ {λ:.3f}")  # Should be ~0.9
    """
    n = len(initial_state)
    state = initial_state.copy()

    # Random initial tangent vector
    tangent = np.random.randn(n)
    tangent = tangent / np.linalg.norm(tangent)

    # Accumulate sum of logarithmic growth rates
    lyapunov_sum = 0.0
    num_renorms = 0

    # Time points
    t_eval = np.arange(0, total_time, dt)
    start_measuring = int(transient_time / dt)

    for step, t in enumerate(t_eval[:-1]):
        # Integrate main trajectory one step
        sol = solve_ivp(
            equations,
            (t, t + dt),
            state,
            method='RK45',
            rtol=1e-9,
            atol=1e-12
        )
        state = sol.y[:, -1]

        # Evolve tangent vector using Jacobian
        J = compute_jacobian(equations, state)
        tangent = J @ tangent

        # Renormalize periodically
        if (step + 1) % renorm_interval == 0:
            norm = np.linalg.norm(tangent)
            tangent = tangent / norm

            # Record growth rate (after transient)
            if step >= start_measuring:
                lyapunov_sum += np.log(norm)
                num_renorms += 1

    # Average growth rate over all renormalizations, scaled by interval
    if num_renorms == 0:
        return 0.0

    lambda_max = lyapunov_sum / (num_renorms * renorm_interval * dt)
    return lambda_max


def lyapunov_spectrum(
    equations: Callable,
    initial_state: np.ndarray,
    dt: float = 0.01,
    total_time: float = 100.0,
    transient_time: float = 10.0,
    renorm_interval: int = 10
) -> np.ndarray:
    """
    Compute the full Lyapunov spectrum (all exponents) using QR decomposition.

    The spectrum {λ₁, λ₂, ..., λₙ} characterizes expansion/contraction rates
    along different directions in phase space.

    For an n-dimensional system:
    - Ordered λ₁ ≥ λ₂ ≥ ... ≥ λₙ
    - Sum Σλᵢ gives phase volume expansion rate
    - For dissipative systems (attractors), Σλᵢ < 0

    Algorithm:
    1. Track n orthogonal tangent vectors simultaneously
    2. Use QR decomposition to maintain orthogonality
    3. Diagonal of R matrix gives growth rates
    4. Average logarithmic growth rates over time

    Args:
        equations: ODE system f(t, state) returning derivatives
        initial_state: Starting point in phase space
        dt: Integration time step
        total_time: Total integration time
        transient_time: Time to discard as transient
        renorm_interval: Steps between orthogonalizations

    Returns:
        Array of Lyapunov exponents [λ₁, λ₂, ..., λₙ] in descending order

    Example:
        >>> def lorenz(t, state):
        ...     x, y, z = state
        ...     return np.array([10*(y-x), x*(28-z)-y, x*y-8/3*z])
        >>> spectrum = lyapunov_spectrum(lorenz, [1.0, 1.0, 1.0])
        >>> print(f"Spectrum: {spectrum}")  # Should be ~[0.9, 0.0, -14.5]
    """
    n = len(initial_state)
    state = initial_state.copy()

    # Initialize n orthonormal tangent vectors (identity matrix)
    tangents = np.eye(n)

    # Accumulate sums for each exponent
    lyapunov_sums = np.zeros(n)
    num_renorms = 0

    # Time points
    t_eval = np.arange(0, total_time, dt)
    start_measuring = int(transient_time / dt)

    for step, t in enumerate(t_eval[:-1]):
        # Integrate main trajectory
        sol = solve_ivp(
            equations,
            (t, t + dt),
            state,
            method='RK45',
            rtol=1e-9,
            atol=1e-12
        )
        state = sol.y[:, -1]

        # Evolve all tangent vectors
        J = compute_jacobian(equations, state)
        tangents = J @ tangents

        # QR decomposition to maintain orthogonality
        if (step + 1) % renorm_interval == 0:
            Q, R = np.linalg.qr(tangents)
            tangents = Q

            # Record growth rates from R diagonal (after transient)
            if step >= start_measuring:
                # R diagonal elements are the stretching factors
                for i in range(n):
                    lyapunov_sums[i] += np.log(abs(R[i, i]))
                num_renorms += 1

    # Average growth rates
    if num_renorms == 0:
        return np.zeros(n)

    spectrum = lyapunov_sums / (num_renorms * renorm_interval * dt)

    # Sort in descending order
    spectrum = np.sort(spectrum)[::-1]

    return spectrum


def lyapunov_vs_parameter(
    equations_factory: Callable,
    param_name: str,
    param_range: np.ndarray,
    initial_state: np.ndarray,
    dt: float = 0.01,
    total_time: float = 100.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute largest Lyapunov exponent across a parameter range.

    This creates a curve λ(p) showing how chaos emerges as parameters change.
    The zero-crossing λ=0 marks the transition to chaos (Hopf bifurcation).

    Args:
        equations_factory: Function (param_value) -> equations(t, state)
        param_name: Name of parameter being varied (for display)
        param_range: Array of parameter values to test
        initial_state: Starting state for trajectory
        dt: Integration time step
        total_time: Integration time for each parameter

    Returns:
        Tuple of (param_values, lyapunov_exponents)

    Example:
        >>> def lorenz_factory(rho):
        ...     def equations(t, state):
        ...         x, y, z = state
        ...         return np.array([10*(y-x), x*(rho-z)-y, x*y-8/3*z])
        ...     return equations
        >>> rho_values = np.linspace(10, 40, 50)
        >>> rhos, lambdas = lyapunov_vs_parameter(
        ...     lorenz_factory, "rho", rho_values, [1, 1, 1]
        ... )
        >>> # lambdas crosses zero around rho ≈ 24.74
    """
    lyapunov_values = []

    for param_value in param_range:
        equations = equations_factory(param_value)

        # Compute λ_max for this parameter value
        lambda_max = compute_lyapunov_exponent(
            equations,
            initial_state,
            dt=dt,
            total_time=total_time
        )

        lyapunov_values.append(lambda_max)

        print(f"{param_name}={param_value:.2f}: λ_max={lambda_max:.4f}")

    return param_range, np.array(lyapunov_values)


def analyze_system(
    equations: Callable,
    system_name: str,
    initial_state: np.ndarray,
    total_time: float = 100.0
) -> dict:
    """
    Perform comprehensive Lyapunov analysis of a dynamical system.

    Computes both the largest exponent and full spectrum, providing
    a complete characterization of the system's chaotic properties.

    Args:
        equations: ODE system f(t, state)
        system_name: Name for display
        initial_state: Starting point
        total_time: Integration time

    Returns:
        Dictionary with analysis results:
        - lambda_max: Largest Lyapunov exponent
        - spectrum: Full Lyapunov spectrum
        - is_chaotic: Boolean (λ_max > 0)
        - spectrum_sum: Sum of all exponents (phase volume rate)
        - system_name: Name of system

    Example:
        >>> def lorenz(t, state):
        ...     x, y, z = state
        ...     return np.array([10*(y-x), x*(28-z)-y, x*y-8/3*z])
        >>> results = analyze_system(lorenz, "Lorenz", [1, 1, 1])
        >>> print(f"Chaotic: {results['is_chaotic']}")
        >>> print(f"λ_max = {results['lambda_max']:.3f}")
    """
    print(f"\nAnalyzing {system_name} system...")
    print("=" * 50)

    # Compute largest exponent
    print("Computing largest Lyapunov exponent...")
    lambda_max = compute_lyapunov_exponent(
        equations, initial_state, total_time=total_time
    )

    # Compute full spectrum
    print("Computing full Lyapunov spectrum...")
    spectrum = lyapunov_spectrum(
        equations, initial_state, total_time=total_time
    )

    # Analysis
    is_chaotic = lambda_max > 0.0
    spectrum_sum = np.sum(spectrum)

    # Display results
    print(f"\nResults for {system_name}:")
    print(f"  Largest exponent λ₁ = {lambda_max:.6f}")
    print(f"  Full spectrum:")
    for i, lam in enumerate(spectrum):
        print(f"    λ_{i+1} = {lam:+.6f}")
    print(f"  Sum Σλᵢ = {spectrum_sum:.6f}")
    print(f"  Chaotic: {is_chaotic}")
    if is_chaotic:
        print(f"  Predictability horizon: ~{1/lambda_max:.1f} time units")

    return {
        'system_name': system_name,
        'lambda_max': lambda_max,
        'spectrum': spectrum,
        'spectrum_sum': spectrum_sum,
        'is_chaotic': is_chaotic
    }


if __name__ == '__main__':
    """Demonstrate Lyapunov exponent calculations."""

    print("Lyapunov Exponent Analysis")
    print("=" * 70)

    # Lorenz system (chaotic)
    def lorenz(t, state, sigma=10.0, rho=28.0, beta=8.0/3.0):
        x, y, z = state
        return np.array([
            sigma * (y - x),
            x * (rho - z) - y,
            x * y - beta * z
        ])

    lorenz_results = analyze_system(
        lorenz, "Lorenz (ρ=28)", [1.0, 1.0, 1.0], total_time=100.0
    )

    # Rössler system (chaotic)
    def rossler(t, state, a=0.2, b=0.2, c=5.7):
        x, y, z = state
        return np.array([
            -y - z,
            x + a * y,
            b + z * (x - c)
        ])

    rossler_results = analyze_system(
        rossler, "Rössler (c=5.7)", [1.0, 1.0, 1.0], total_time=100.0
    )

    print("\n" + "=" * 70)
    print("Analysis complete!")
