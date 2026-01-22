"""
Strange Attractors: A collection of chaotic dynamical systems

This module implements various strange attractors - deterministic chaotic systems
that produce beautiful, never-repeating trajectories in phase space.

Example usage:
    from attractors import LorenzAttractor, RosslerAttractor

    # Create and simulate a Lorenz attractor
    lorenz = LorenzAttractor(sigma=10.0, rho=28.0, beta=8/3)
    trajectory = lorenz.simulate(duration=50.0, dt=0.01)
    lorenz.plot_3d(trajectory)
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import Tuple, Optional
import plotly.graph_objects as go


class Attractor:
    """Base class for strange attractors"""

    def __init__(self, initial_state: Optional[np.ndarray] = None):
        """
        Initialize the attractor

        Args:
            initial_state: Initial conditions [x0, y0, z0]. If None, uses default.
        """
        self.initial_state = initial_state if initial_state is not None else self.default_initial_state()

    def default_initial_state(self) -> np.ndarray:
        """Return default initial conditions"""
        return np.array([1.0, 1.0, 1.0])

    def equations(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Differential equations defining the system

        Args:
            t: Time (not used in autonomous systems, but required by solve_ivp)
            state: Current state [x, y, z]

        Returns:
            Derivatives [dx/dt, dy/dt, dz/dt]
        """
        raise NotImplementedError("Subclasses must implement equations()")

    def simulate(self, duration: float = 50.0, dt: float = 0.01) -> np.ndarray:
        """
        Simulate the attractor trajectory

        Args:
            duration: Total simulation time
            dt: Time step for output

        Returns:
            Array of shape (n_points, 3) containing the trajectory
        """
        t_span = (0, duration)
        t_eval = np.arange(0, duration, dt)

        solution = solve_ivp(
            self.equations,
            t_span,
            self.initial_state,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-8,
            atol=1e-10
        )

        return solution.y.T  # Transpose to get (n_points, 3) shape

    def plot_3d_matplotlib(self, trajectory: np.ndarray, title: str = "Strange Attractor",
                          color_by_time: bool = True, figsize: Tuple[int, int] = (10, 8)):
        """
        Create a static 3D plot using matplotlib

        Args:
            trajectory: Array of shape (n_points, 3)
            title: Plot title
            color_by_time: If True, color trajectory by time progression
            figsize: Figure size in inches
        """
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')

        if color_by_time:
            # Color by progression through time
            colors = np.arange(len(trajectory))
            scatter = ax.scatter(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
                               c=colors, cmap='viridis', s=0.5, alpha=0.6)
            plt.colorbar(scatter, ax=ax, label='Time progression')
        else:
            ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
                   linewidth=0.5, alpha=0.7)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(title)

        return fig, ax

    def plot_3d_interactive(self, trajectory: np.ndarray, title: str = "Strange Attractor",
                           color_by_time: bool = True):
        """
        Create an interactive 3D plot using plotly

        Args:
            trajectory: Array of shape (n_points, 3)
            title: Plot title
            color_by_time: If True, color trajectory by time progression

        Returns:
            Plotly figure object
        """
        if color_by_time:
            colors = np.arange(len(trajectory))
            colorscale = 'Viridis'
        else:
            colors = 'blue'
            colorscale = None

        fig = go.Figure(data=[go.Scatter3d(
            x=trajectory[:, 0],
            y=trajectory[:, 1],
            z=trajectory[:, 2],
            mode='lines',
            line=dict(
                color=colors,
                colorscale=colorscale,
                width=2
            ),
            marker=dict(size=1)
        )])

        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            width=900,
            height=700
        )

        return fig


class LorenzAttractor(Attractor):
    """
    The Lorenz attractor - discovered by Edward Lorenz in 1963

    The system models simplified atmospheric convection and exhibits chaotic behavior
    for certain parameter values. The classic "butterfly" shape appears at:
    sigma=10, rho=28, beta=8/3

    Equations:
        dx/dt = sigma * (y - x)
        dy/dt = x * (rho - z) - y
        dz/dt = x * y - beta * z

    Parameters:
        sigma: Prandtl number (ratio of momentum diffusivity to thermal diffusivity)
        rho: Rayleigh number (relates to temperature difference)
        beta: Geometric factor
    """

    def __init__(self, sigma: float = 10.0, rho: float = 28.0, beta: float = 8/3,
                 initial_state: Optional[np.ndarray] = None):
        """
        Initialize the Lorenz attractor

        Args:
            sigma: Prandtl number (default: 10.0)
            rho: Rayleigh number (default: 28.0)
            beta: Geometric factor (default: 8/3)
            initial_state: Initial conditions [x0, y0, z0]
        """
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        super().__init__(initial_state)

    def default_initial_state(self) -> np.ndarray:
        """Default initial state for Lorenz system"""
        return np.array([0.1, 0.0, 0.0])

    def equations(self, t: float, state: np.ndarray) -> np.ndarray:
        """Lorenz system differential equations"""
        x, y, z = state
        dx_dt = self.sigma * (y - x)
        dy_dt = x * (self.rho - z) - y
        dz_dt = x * y - self.beta * z
        return np.array([dx_dt, dy_dt, dz_dt])

    def __repr__(self) -> str:
        return f"LorenzAttractor(sigma={self.sigma}, rho={self.rho}, beta={self.beta:.3f})"


class RosslerAttractor(Attractor):
    """
    The Rössler attractor - introduced by Otto Rössler in 1976

    A simpler system than Lorenz that still exhibits chaotic behavior.
    The classic parameters are: a=0.2, b=0.2, c=5.7

    Equations:
        dx/dt = -y - z
        dy/dt = x + a * y
        dz/dt = b + z * (x - c)

    Parameters:
        a, b, c: System parameters controlling the dynamics
    """

    def __init__(self, a: float = 0.2, b: float = 0.2, c: float = 5.7,
                 initial_state: Optional[np.ndarray] = None):
        """
        Initialize the Rössler attractor

        Args:
            a: First parameter (default: 0.2)
            b: Second parameter (default: 0.2)
            c: Third parameter (default: 5.7)
            initial_state: Initial conditions [x0, y0, z0]
        """
        self.a = a
        self.b = b
        self.c = c
        super().__init__(initial_state)

    def default_initial_state(self) -> np.ndarray:
        """Default initial state for Rössler system"""
        return np.array([1.0, 1.0, 1.0])

    def equations(self, t: float, state: np.ndarray) -> np.ndarray:
        """Rössler system differential equations"""
        x, y, z = state
        dx_dt = -y - z
        dy_dt = x + self.a * y
        dz_dt = self.b + z * (x - self.c)
        return np.array([dx_dt, dy_dt, dz_dt])

    def __repr__(self) -> str:
        return f"RosslerAttractor(a={self.a}, b={self.b}, c={self.c})"


if __name__ == "__main__":
    # Example: Generate both Lorenz and Rössler attractors
    print("Generating Lorenz attractor...")
    lorenz = LorenzAttractor()
    lorenz_trajectory = lorenz.simulate(duration=50.0, dt=0.01)

    print("Generating Rössler attractor...")
    rossler = RosslerAttractor()
    rossler_trajectory = rossler.simulate(duration=100.0, dt=0.01)

    # Create matplotlib visualizations
    print("Creating matplotlib plots...")
    fig1, _ = lorenz.plot_3d_matplotlib(lorenz_trajectory,
                                         title="Lorenz Attractor (σ=10, ρ=28, β=8/3)")
    plt.savefig('/tmp/claude-attractors/run_2026-01-16_19-33-06/output/lorenz_attractor.png',
                dpi=150, bbox_inches='tight')

    fig2, _ = rossler.plot_3d_matplotlib(rossler_trajectory,
                                          title="Rössler Attractor (a=0.2, b=0.2, c=5.7)")
    plt.savefig('/tmp/claude-attractors/run_2026-01-16_19-33-06/output/rossler_attractor.png',
                dpi=150, bbox_inches='tight')

    print("Saved static plots to output directory")
    print(f"Lorenz trajectory points: {len(lorenz_trajectory)}")
    print(f"Rössler trajectory points: {len(rossler_trajectory)}")
