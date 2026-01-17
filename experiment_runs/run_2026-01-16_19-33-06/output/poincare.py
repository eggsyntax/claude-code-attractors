"""
Poincaré Section Analysis for Strange Attractors

This module provides tools for creating and visualizing Poincaré sections - 2D slices
through the phase space of 3D attractors. These sections reveal the fractal structure
and underlying geometry that's often hard to see in 3D visualizations.

Mathematical Background:
-----------------------
A Poincaré section (or Poincaré map) is created by:
1. Choosing a plane in phase space (e.g., y = 0)
2. Recording points where trajectories cross this plane in a specific direction
3. The resulting 2D plot reveals the attractor's structure

For chaotic attractors, the section typically shows:
- Self-similar (fractal) structure at multiple scales
- Dense point clouds indicating aperiodic motion
- Folding patterns that create sensitive dependence

Author: Alice & Bob
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from typing import Tuple, Callable, Optional, List
import warnings


class PoincareSection:
    """
    Creates and visualizes Poincaré sections for dynamical systems.

    A Poincaré section reduces a continuous flow in 3D to a discrete map in 2D,
    revealing structure that's difficult to see in the full phase space.
    """

    def __init__(self, equations: Callable, plane_coord: int = 1,
                 plane_value: float = 0.0, direction: str = 'positive'):
        """
        Initialize Poincaré section analyzer.

        Parameters:
        -----------
        equations : callable
            Function f(t, state) returning derivatives [dx/dt, dy/dt, dz/dt]
        plane_coord : int
            Which coordinate defines the plane (0=x, 1=y, 2=z). Default is 1 (y).
        plane_value : float
            The value of the plane (e.g., y=0). Default is 0.
        direction : str
            'positive' for crossings with positive velocity, 'negative' for negative,
            'both' for all crossings.
        """
        self.equations = equations
        self.plane_coord = plane_coord
        self.plane_value = plane_value
        self.direction = direction

    def find_crossings(self, trajectory: np.ndarray, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find points where trajectory crosses the Poincaré plane.

        Parameters:
        -----------
        trajectory : ndarray, shape (n, 3)
            The trajectory through phase space
        t : ndarray
            Time points corresponding to trajectory

        Returns:
        --------
        crossings : ndarray, shape (m, 3)
            Points where trajectory crosses the plane
        indices : ndarray
            Indices of crossing points in original trajectory
        """
        coords = trajectory[:, self.plane_coord]

        # Find sign changes (crossings)
        differences = coords[:-1] - self.plane_value
        next_differences = coords[1:] - self.plane_value

        # Detect crossings
        if self.direction == 'positive':
            # Crossing from below to above (positive velocity)
            crossings_mask = (differences <= 0) & (next_differences > 0)
        elif self.direction == 'negative':
            # Crossing from above to below (negative velocity)
            crossings_mask = (differences >= 0) & (next_differences < 0)
        else:  # 'both'
            # Any crossing
            crossings_mask = (differences * next_differences) <= 0

        crossing_indices = np.where(crossings_mask)[0]

        # Interpolate to find exact crossing points
        crossings = []
        for idx in crossing_indices:
            # Linear interpolation between points
            c1, c2 = coords[idx], coords[idx + 1]
            if c2 == c1:
                continue
            alpha = (self.plane_value - c1) / (c2 - c1)
            crossing = trajectory[idx] + alpha * (trajectory[idx + 1] - trajectory[idx])
            crossings.append(crossing)

        if len(crossings) == 0:
            return np.array([]), np.array([])

        return np.array(crossings), crossing_indices

    def compute_section(self, initial_state: np.ndarray, t_max: float = 100.0,
                       t_transient: float = 10.0, dt: float = 0.01) -> np.ndarray:
        """
        Compute Poincaré section for a trajectory.

        Parameters:
        -----------
        initial_state : ndarray
            Initial conditions [x0, y0, z0]
        t_max : float
            Total integration time
        t_transient : float
            Transient time to discard (let system settle onto attractor)
        dt : float
            Time step for dense output

        Returns:
        --------
        section : ndarray, shape (m, 3)
            Points in the Poincaré section
        """
        # Integrate with dense output
        t_span = (0, t_max)
        t_eval = np.arange(0, t_max, dt)

        sol = solve_ivp(
            self.equations,
            t_span,
            initial_state,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-8,
            atol=1e-10
        )

        trajectory = sol.y.T

        # Find crossings
        crossings, _ = self.find_crossings(trajectory, sol.t)

        # Remove transient crossings
        if len(crossings) > 0:
            # Estimate which crossings are after transient
            # Approximate: assume roughly uniform distribution
            n_transient = int(len(crossings) * t_transient / t_max)
            crossings = crossings[n_transient:]

        return crossings

    def visualize_section(self, section: np.ndarray, title: str = "Poincaré Section",
                         figsize: Tuple[int, int] = (10, 10),
                         alpha: float = 0.3, s: float = 1.0) -> plt.Figure:
        """
        Visualize a Poincaré section.

        Parameters:
        -----------
        section : ndarray
            Points in the Poincaré section
        title : str
            Plot title
        figsize : tuple
            Figure size
        alpha : float
            Point transparency
        s : float
            Point size

        Returns:
        --------
        fig : matplotlib Figure
        """
        # Determine which coordinates to plot (the two that aren't the plane coordinate)
        coords = [0, 1, 2]
        coords.remove(self.plane_coord)
        x_coord, y_coord = coords
        coord_names = ['x', 'y', 'z']

        fig, ax = plt.subplots(figsize=figsize)

        if len(section) > 0:
            ax.scatter(section[:, x_coord], section[:, y_coord],
                      s=s, alpha=alpha, c='navy', edgecolors='none')

        ax.set_xlabel(f'{coord_names[x_coord]}', fontsize=12)
        ax.set_ylabel(f'{coord_names[y_coord]}', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Equal aspect ratio to avoid distortion
        ax.set_aspect('equal', adjustable='box')

        plt.tight_layout()
        return fig

    def multi_trajectory_section(self, initial_states: List[np.ndarray],
                                t_max: float = 100.0, t_transient: float = 10.0,
                                dt: float = 0.01) -> List[np.ndarray]:
        """
        Compute Poincaré sections for multiple trajectories.

        Useful for showing that different initial conditions converge to the same
        attractor structure.

        Parameters:
        -----------
        initial_states : list of ndarray
            Multiple initial conditions
        t_max, t_transient, dt : float
            Integration parameters

        Returns:
        --------
        sections : list of ndarray
            Poincaré sections for each trajectory
        """
        return [self.compute_section(state, t_max, t_transient, dt)
                for state in initial_states]


def lorenz_equations(t, state, sigma=10.0, rho=28.0, beta=8/3):
    """Lorenz system equations."""
    x, y, z = state
    return [
        sigma * (y - x),
        x * (rho - z) - y,
        x * y - beta * z
    ]


def rossler_equations(t, state, a=0.2, b=0.2, c=5.7):
    """Rössler system equations."""
    x, y, z = state
    return [
        -y - z,
        x + a * y,
        b + z * (x - c)
    ]


def create_lorenz_section(rho: float = 28.0, plane: str = 'z',
                         initial_state: Optional[np.ndarray] = None) -> Tuple[np.ndarray, PoincareSection]:
    """
    Create Poincaré section for Lorenz attractor.

    Parameters:
    -----------
    rho : float
        Lorenz parameter (Rayleigh number)
    plane : str
        Which plane to use: 'x', 'y', or 'z'. Default 'z' (z=27 for Lorenz).
    initial_state : ndarray, optional
        Initial conditions. If None, uses [1, 1, 1].

    Returns:
    --------
    section : ndarray
        Points in the Poincaré section
    poincare : PoincareSection
        The Poincaré section object
    """
    if initial_state is None:
        initial_state = np.array([1.0, 1.0, 1.0])

    # For Lorenz, z=27 is a nice plane (near the attractor's "center")
    plane_values = {'x': 0, 'y': 0, 'z': 27}
    plane_coords = {'x': 0, 'y': 1, 'z': 2}

    equations = lambda t, state: lorenz_equations(t, state, rho=rho)

    poincare = PoincareSection(
        equations,
        plane_coord=plane_coords[plane],
        plane_value=plane_values[plane],
        direction='positive'
    )

    section = poincare.compute_section(initial_state, t_max=100.0, t_transient=10.0)
    return section, poincare


def create_rossler_section(c: float = 5.7, plane: str = 'z',
                          initial_state: Optional[np.ndarray] = None) -> Tuple[np.ndarray, PoincareSection]:
    """
    Create Poincaré section for Rössler attractor.

    Parameters:
    -----------
    c : float
        Rössler parameter
    plane : str
        Which plane to use: 'x', 'y', or 'z'. Default 'z' (z=0 for Rössler).
    initial_state : ndarray, optional
        Initial conditions. If None, uses [1, 1, 1].

    Returns:
    --------
    section : ndarray
        Points in the Poincaré section
    poincare : PoincareSection
        The Poincaré section object
    """
    if initial_state is None:
        initial_state = np.array([1.0, 1.0, 1.0])

    plane_values = {'x': 0, 'y': 0, 'z': 0}
    plane_coords = {'x': 0, 'y': 1, 'z': 2}

    equations = lambda t, state: rossler_equations(t, state, c=c)

    poincare = PoincareSection(
        equations,
        plane_coord=plane_coords[plane],
        plane_value=plane_values[plane],
        direction='positive'
    )

    section = poincare.compute_section(initial_state, t_max=200.0, t_transient=20.0)
    return section, poincare


def compare_parameter_sections(system: str = 'lorenz', param_values: List[float] = None,
                               figsize: Tuple[int, int] = (15, 10)) -> plt.Figure:
    """
    Create a comparison plot showing how Poincaré sections change with parameters.

    Parameters:
    -----------
    system : str
        'lorenz' or 'rossler'
    param_values : list of float
        Parameter values to compare
    figsize : tuple
        Figure size

    Returns:
    --------
    fig : matplotlib Figure
    """
    if param_values is None:
        if system == 'lorenz':
            param_values = [14, 20, 24, 28]  # Different rho values
        else:
            param_values = [2, 4, 5.7, 6]  # Different c values

    n_params = len(param_values)
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.flatten()

    for idx, param in enumerate(param_values):
        if system == 'lorenz':
            section, poincare_obj = create_lorenz_section(rho=param)
            param_name = 'ρ'
        else:
            section, poincare_obj = create_rossler_section(c=param)
            param_name = 'c'

        ax = axes[idx]

        # Determine which coordinates to plot
        coords = [0, 1, 2]
        coords.remove(poincare_obj.plane_coord)
        x_coord, y_coord = coords
        coord_names = ['x', 'y', 'z']

        if len(section) > 0:
            ax.scatter(section[:, x_coord], section[:, y_coord],
                      s=1, alpha=0.5, c='navy', edgecolors='none')

        ax.set_xlabel(coord_names[x_coord], fontsize=11)
        ax.set_ylabel(coord_names[y_coord], fontsize=11)
        ax.set_title(f'{param_name} = {param}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')

    fig.suptitle(f'{system.capitalize()} Attractor Poincaré Sections',
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()

    return fig


if __name__ == "__main__":
    print("Generating Poincaré sections for strange attractors...\n")

    # 1. Lorenz attractor section
    print("Creating Lorenz Poincaré section (z=27 plane)...")
    section, poincare = create_lorenz_section(rho=28.0, plane='z')
    fig = poincare.visualize_section(
        section,
        title=f"Lorenz Attractor Poincaré Section (z=27, ρ=28)\n{len(section)} crossing points"
    )
    fig.savefig('lorenz_poincare_section.png', dpi=300, bbox_inches='tight')
    print(f"  Saved: lorenz_poincare_section.png ({len(section)} points)")
    plt.close()

    # 2. Rössler attractor section
    print("\nCreating Rössler Poincaré section (z=0 plane)...")
    section, poincare = create_rossler_section(c=5.7, plane='z')
    fig = poincare.visualize_section(
        section,
        title=f"Rössler Attractor Poincaré Section (z=0, c=5.7)\n{len(section)} crossing points"
    )
    fig.savefig('rossler_poincare_section.png', dpi=300, bbox_inches='tight')
    print(f"  Saved: rossler_poincare_section.png ({len(section)} points)")
    plt.close()

    # 3. Parameter comparison for Lorenz
    print("\nCreating parameter comparison for Lorenz attractor...")
    fig = compare_parameter_sections('lorenz', param_values=[14, 20, 24, 28])
    fig.savefig('lorenz_poincare_comparison.png', dpi=300, bbox_inches='tight')
    print("  Saved: lorenz_poincare_comparison.png")
    plt.close()

    # 4. Parameter comparison for Rössler
    print("\nCreating parameter comparison for Rössler attractor...")
    fig = compare_parameter_sections('rossler', param_values=[2, 4, 5.7, 6])
    fig.savefig('rossler_poincare_comparison.png', dpi=300, bbox_inches='tight')
    print("  Saved: rossler_poincare_comparison.png")
    plt.close()

    print("\n✓ All Poincaré sections generated successfully!")
    print("\nWhat the sections reveal:")
    print("  • Lorenz: Two distinct regions (the butterfly wings) with fractal folding")
    print("  • Rössler: Spiral structure showing the attractor's rotation")
    print("  • Parameter variation: Transition from simple to complex structure")
