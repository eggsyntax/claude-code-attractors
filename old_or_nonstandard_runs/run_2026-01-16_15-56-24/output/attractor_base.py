"""
Base class for dynamical system attractors.

This module provides an abstract base class that all specific attractor
implementations should inherit from. It handles numerical integration
using scipy's solve_ivp with adaptive step sizing.

Example:
    class MyAttractor(AttractorBase):
        def derivatives(self, t, state):
            x, y, z = state
            # Return dx/dt, dy/dt, dz/dt
            return [dx_dt, dy_dt, dz_dt]

    attractor = MyAttractor(initial_state=[1, 1, 1])
    trajectory = attractor.generate_trajectory(t_span=(0, 100), n_points=10000)
"""

from abc import ABC, abstractmethod
import numpy as np
from scipy.integrate import solve_ivp
from typing import Tuple, Optional, Dict, Any


class AttractorBase(ABC):
    """
    Abstract base class for strange attractors and dynamical systems.

    This class provides the numerical integration framework using scipy's
    solve_ivp with RK45 (Runge-Kutta 4-5) adaptive step size integration.

    Attributes:
        initial_state: Initial conditions [x0, y0, z0]
        parameters: Dictionary of system parameters
        dimension: Number of dimensions (default 3 for most attractors)
    """

    def __init__(
        self,
        initial_state: Optional[np.ndarray] = None,
        parameters: Optional[Dict[str, float]] = None,
        dimension: int = 3
    ):
        """
        Initialize the attractor.

        Args:
            initial_state: Initial conditions. If None, uses default_initial_state()
            parameters: System parameters. If None, uses default_parameters()
            dimension: Dimensionality of the system (typically 3)
        """
        self.dimension = dimension
        self.parameters = parameters if parameters is not None else self.default_parameters()
        self.initial_state = (
            initial_state if initial_state is not None
            else self.default_initial_state()
        )

        # Validate initial state
        if len(self.initial_state) != self.dimension:
            raise ValueError(
                f"Initial state dimension {len(self.initial_state)} "
                f"doesn't match system dimension {self.dimension}"
            )

    @abstractmethod
    def derivatives(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Compute the derivatives (dx/dt, dy/dt, dz/dt, ...) at a given state.

        This is the core differential equation that defines the attractor's dynamics.
        Must be implemented by each specific attractor class.

        Args:
            t: Time (often not used in autonomous systems, but required by solve_ivp)
            state: Current state vector [x, y, z, ...]

        Returns:
            Array of derivatives [dx/dt, dy/dt, dz/dt, ...]
        """
        pass

    @abstractmethod
    def default_parameters(self) -> Dict[str, float]:
        """
        Return default parameters for this attractor.

        Returns:
            Dictionary of parameter names and their default values
        """
        pass

    @abstractmethod
    def default_initial_state(self) -> np.ndarray:
        """
        Return default initial conditions for this attractor.

        Returns:
            Array of initial state values [x0, y0, z0, ...]
        """
        pass

    def generate_trajectory(
        self,
        t_span: Tuple[float, float] = (0, 100),
        n_points: int = 10000,
        method: str = 'RK45',
        **solve_ivp_kwargs
    ) -> np.ndarray:
        """
        Generate a trajectory through phase space.

        Uses scipy's solve_ivp for numerical integration with adaptive step size.
        The trajectory is interpolated to return exactly n_points evenly spaced
        in time.

        Args:
            t_span: Tuple (t_start, t_end) defining time interval
            n_points: Number of points to return (evenly spaced in time)
            method: Integration method (default: RK45 - Runge-Kutta 4-5)
            **solve_ivp_kwargs: Additional arguments passed to solve_ivp

        Returns:
            numpy array of shape (n_points, dimension) containing trajectory

        Example:
            trajectory = attractor.generate_trajectory(
                t_span=(0, 50),
                n_points=5000
            )
            # trajectory.shape == (5000, 3) for a 3D attractor
        """
        # Time points where we want the solution
        t_eval = np.linspace(t_span[0], t_span[1], n_points)

        # Solve the ODE system
        solution = solve_ivp(
            fun=self.derivatives,
            t_span=t_span,
            y0=self.initial_state,
            method=method,
            t_eval=t_eval,
            **solve_ivp_kwargs
        )

        if not solution.success:
            raise RuntimeError(
                f"Integration failed: {solution.message}"
            )

        # Transpose to get shape (n_points, dimension)
        trajectory = solution.y.T

        return trajectory

    def update_parameters(self, **kwargs) -> None:
        """
        Update system parameters.

        Args:
            **kwargs: Parameter names and new values

        Example:
            attractor.update_parameters(sigma=10.0, rho=28.0)
        """
        for key, value in kwargs.items():
            if key not in self.parameters:
                raise ValueError(
                    f"Unknown parameter '{key}'. "
                    f"Valid parameters: {list(self.parameters.keys())}"
                )
            self.parameters[key] = value

    def set_initial_state(self, state: np.ndarray) -> None:
        """
        Set new initial conditions.

        Args:
            state: New initial state vector
        """
        if len(state) != self.dimension:
            raise ValueError(
                f"State dimension {len(state)} "
                f"doesn't match system dimension {self.dimension}"
            )
        self.initial_state = np.array(state)

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the current attractor configuration.

        Returns:
            Dictionary containing system info
        """
        return {
            'type': self.__class__.__name__,
            'dimension': self.dimension,
            'parameters': self.parameters.copy(),
            'initial_state': self.initial_state.copy()
        }
