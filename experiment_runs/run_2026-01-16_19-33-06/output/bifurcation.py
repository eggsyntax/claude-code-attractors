"""
Bifurcation Diagram Generator for Strange Attractors

This module creates bifurcation diagrams that show how an attractor's behavior
changes as a parameter is varied. These diagrams reveal the routes to chaos,
period-doubling cascades, and other fascinating transitions.

A bifurcation diagram plots:
- X-axis: The varying parameter value
- Y-axis: The values of one state variable at specific intervals (often at Poincaré crossings)

For chaotic systems, as parameters change, we see transitions from:
- Fixed points (single value)
- Periodic orbits (multiple discrete values)
- Period-doubling (2, 4, 8, 16... values)
- Chaos (dense vertical lines of values)

Author: Bob (building on Alice's temporal work and our joint foundation)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from typing import Callable, Tuple, List
import warnings


class BifurcationDiagram:
    """
    Generates bifurcation diagrams for dynamical systems.

    The diagram shows how the long-term behavior of a system changes
    as a parameter is varied, revealing the structure of the route to chaos.
    """

    def __init__(
        self,
        system_func: Callable,
        param_range: Tuple[float, float],
        param_steps: int = 200,
        initial_state: np.ndarray = None,
        t_transient: float = 50.0,
        t_sample: float = 50.0,
        dt: float = 0.01
    ):
        """
        Initialize the bifurcation diagram generator.

        Args:
            system_func: Function that returns derivatives given (t, state, param)
            param_range: (min, max) range for the bifurcation parameter
            param_steps: Number of parameter values to test
            initial_state: Starting state for the system
            t_transient: Time to integrate before sampling (to reach attractor)
            t_sample: Time to sample after transient
            dt: Time step for sampling
        """
        self.system_func = system_func
        self.param_range = param_range
        self.param_steps = param_steps
        self.initial_state = initial_state
        self.t_transient = t_transient
        self.t_sample = t_sample
        self.dt = dt

    def compute(
        self,
        state_index: int = 2,
        condition_index: int = 1,
        condition_value: float = 0.0,
        condition_direction: str = 'positive'
    ) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        Compute the bifurcation diagram using Poincaré sections.

        Args:
            state_index: Which state variable to plot on y-axis
            condition_index: Which state variable to use for Poincaré condition
            condition_value: Value to cross for Poincaré section
            condition_direction: 'positive' or 'negative' for crossing direction

        Returns:
            params: Array of parameter values
            values: List of arrays, each containing Poincaré crossing values for that parameter
        """
        params = np.linspace(self.param_range[0], self.param_range[1], self.param_steps)
        values = []

        for i, param in enumerate(params):
            # Create a wrapper function with the current parameter value
            def system_with_param(t, state):
                return self.system_func(t, state, param)

            # Integrate through transient period
            t_span = [0, self.t_transient]
            sol_transient = solve_ivp(
                system_with_param,
                t_span,
                self.initial_state,
                method='RK45',
                dense_output=True,
                rtol=1e-8,
                atol=1e-10
            )

            # Use the final state as the new initial condition
            state_after_transient = sol_transient.y[:, -1]

            # Now sample the attractor
            t_span = [0, self.t_sample]
            t_eval = np.arange(0, self.t_sample, self.dt)
            sol_sample = solve_ivp(
                system_with_param,
                t_span,
                state_after_transient,
                method='RK45',
                t_eval=t_eval,
                rtol=1e-8,
                atol=1e-10
            )

            # Extract Poincaré section crossings
            crossings = self._find_poincare_crossings(
                sol_sample.y,
                condition_index,
                condition_value,
                condition_direction
            )

            # Get values of the plotted variable at crossings
            if len(crossings) > 0:
                crossing_values = sol_sample.y[state_index, crossings]
                values.append(crossing_values)
            else:
                values.append(np.array([]))

            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"Progress: {i+1}/{self.param_steps} parameter values computed")

        return params, values

    def _find_poincare_crossings(
        self,
        trajectory: np.ndarray,
        condition_index: int,
        condition_value: float,
        direction: str
    ) -> List[int]:
        """
        Find indices where trajectory crosses the Poincaré section.

        Args:
            trajectory: State trajectory (state_dim x time_steps)
            condition_index: Which variable to check for crossing
            condition_value: Value to cross
            direction: 'positive' for upward crossing, 'negative' for downward

        Returns:
            List of indices where crossings occur
        """
        var = trajectory[condition_index, :]
        crossings = []

        for i in range(1, len(var)):
            if direction == 'positive':
                if var[i-1] < condition_value <= var[i]:
                    crossings.append(i)
            else:  # negative
                if var[i-1] > condition_value >= var[i]:
                    crossings.append(i)

        return crossings

    def plot(
        self,
        params: np.ndarray,
        values: List[np.ndarray],
        param_name: str = 'Parameter',
        state_name: str = 'State Variable',
        title: str = 'Bifurcation Diagram',
        figsize: Tuple[int, int] = (12, 8),
        save_path: str = None
    ):
        """
        Create a bifurcation diagram plot.

        Args:
            params: Parameter values
            values: Corresponding state values at Poincaré crossings
            param_name: Name of the parameter for x-axis label
            state_name: Name of the state variable for y-axis label
            title: Plot title
            figsize: Figure size
            save_path: If provided, save the figure to this path
        """
        fig, ax = plt.subplots(figsize=figsize, facecolor='white')

        # Plot each parameter's values
        for param, vals in zip(params, values):
            if len(vals) > 0:
                # Use small points for dense regions (chaos)
                # and slightly larger for sparse regions (periodic)
                size = 1.0 if len(vals) > 10 else 2.0
                ax.plot(
                    [param] * len(vals),
                    vals,
                    'k.',
                    markersize=size,
                    alpha=0.3
                )

        ax.set_xlabel(param_name, fontsize=12, fontweight='bold')
        ax.set_ylabel(state_name, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Bifurcation diagram saved to {save_path}")

        return fig, ax


def lorenz_system(t: float, state: np.ndarray, rho: float) -> np.ndarray:
    """
    Lorenz system equations with rho as the bifurcation parameter.

    The Lorenz system shows complex bifurcation behavior as rho varies:
    - rho < 1: Stable fixed point at origin
    - 1 < rho < 13.926: Two stable fixed points
    - 13.926 < rho < 24.74: Stable periodic orbits (with some chaos)
    - rho > 24.74: Chaotic behavior (the famous strange attractor)

    Args:
        t: Time (unused but required by scipy)
        state: [x, y, z] state vector
        rho: Rayleigh number (bifurcation parameter)

    Returns:
        Derivatives [dx/dt, dy/dt, dz/dt]
    """
    sigma = 10.0
    beta = 8.0 / 3.0

    x, y, z = state
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z

    return np.array([dx, dy, dz])


def rossler_system(t: float, state: np.ndarray, c: float) -> np.ndarray:
    """
    Rössler system equations with c as the bifurcation parameter.

    The Rössler system exhibits a classic period-doubling route to chaos:
    - c < ~2.0: Stable fixed point
    - ~2.0 < c < ~4.2: Period-doubling cascade (1 → 2 → 4 → 8 ...)
    - c > ~4.2: Chaotic behavior

    Args:
        t: Time (unused but required by scipy)
        state: [x, y, z] state vector
        c: Bifurcation parameter

    Returns:
        Derivatives [dx/dt, dy/dt, dz/dt]
    """
    a = 0.2
    b = 0.2

    x, y, z = state
    dx = -y - z
    dy = x + a * y
    dz = b + z * (x - c)

    return np.array([dx, dy, dz])


def create_lorenz_bifurcation(save_path: str = 'lorenz_bifurcation.png'):
    """
    Create a bifurcation diagram for the Lorenz system.

    This diagram shows the transition from stable behavior to chaos
    as the Rayleigh number (rho) increases.
    """
    print("Computing Lorenz bifurcation diagram...")
    print("This may take a few minutes for high-resolution diagrams.\n")

    bifurcation = BifurcationDiagram(
        system_func=lorenz_system,
        param_range=(0, 50),
        param_steps=300,
        initial_state=np.array([1.0, 1.0, 1.0]),
        t_transient=100.0,
        t_sample=100.0,
        dt=0.02
    )

    # Use z-coordinate with y=0 plane as Poincaré section
    params, values = bifurcation.compute(
        state_index=2,  # z coordinate
        condition_index=1,  # y coordinate
        condition_value=0.0,
        condition_direction='positive'
    )

    bifurcation.plot(
        params,
        values,
        param_name='ρ (Rayleigh number)',
        state_name='z at Poincaré section (y=0, dy/dt>0)',
        title='Lorenz System Bifurcation Diagram: Route to Chaos',
        save_path=save_path
    )

    print(f"\nKey features visible in the diagram:")
    print(f"  • ρ < ~13.9: Two stable fixed points")
    print(f"  • ~13.9 < ρ < ~24.7: Complex transitional behavior")
    print(f"  • ρ > ~24.7: Chaotic attractor (dense vertical bands)")
    print(f"  • Around ρ=28: Classic 'butterfly' attractor")


def create_rossler_bifurcation(save_path: str = 'rossler_bifurcation.png'):
    """
    Create a bifurcation diagram for the Rössler system.

    This diagram beautifully shows the period-doubling cascade
    leading to chaos.
    """
    print("Computing Rössler bifurcation diagram...")
    print("This may take a few minutes for high-resolution diagrams.\n")

    bifurcation = BifurcationDiagram(
        system_func=rossler_system,
        param_range=(2.0, 6.0),
        param_steps=300,
        initial_state=np.array([1.0, 1.0, 1.0]),
        t_transient=200.0,
        t_sample=100.0,
        dt=0.05
    )

    # Use z-coordinate with y=0 plane as Poincaré section
    params, values = bifurcation.compute(
        state_index=2,  # z coordinate
        condition_index=1,  # y coordinate
        condition_value=0.0,
        condition_direction='positive'
    )

    bifurcation.plot(
        params,
        values,
        param_name='c (bifurcation parameter)',
        state_name='z at Poincaré section (y=0, dy/dt>0)',
        title='Rössler System Bifurcation Diagram: Period-Doubling Route to Chaos',
        save_path=save_path
    )

    print(f"\nKey features visible in the diagram:")
    print(f"  • c < ~2.5: Period-1 orbit (single value)")
    print(f"  • ~2.5 < c < ~3.0: Period-2 orbit (two values)")
    print(f"  • ~3.0 < c < ~4.2: Period-doubling cascade (4, 8, 16...)")
    print(f"  • c > ~4.2: Chaos (dense vertical bands)")
    print(f"  • Notice 'windows' where periodic behavior returns briefly")


if __name__ == '__main__':
    # Create both bifurcation diagrams
    create_lorenz_bifurcation('lorenz_bifurcation.png')
    print("\n" + "="*60 + "\n")
    create_rossler_bifurcation('rossler_bifurcation.png')

    plt.show()
