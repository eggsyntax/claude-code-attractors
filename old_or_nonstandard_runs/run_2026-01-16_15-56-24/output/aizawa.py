"""
Aizawa Attractor Implementation

The Aizawa attractor is a three-dimensional chaotic system discovered by Yoji Aizawa.
It produces visually stunning trajectories with a complex, multi-lobed structure that
differs significantly from both the Lorenz and Rössler attractors.

System Equations:
    dx/dt = (z - b) * x - d * y
    dy/dt = d * x + (z - b) * y
    dz/dt = c + a * z - (z^3)/3 - (x^2 + y^2) * (1 + e * z) + f * z * x^3

Default parameters (a=0.95, b=0.7, c=0.6, d=3.5, e=0.25, f=0.1) produce
chaotic behavior with a distinctive visual structure.

Mathematical Properties:
- Dimension: 3D
- Type: Dissipative dynamical system
- Typical Lyapunov exponent: λ₁ ≈ 0.15 (weakly chaotic)
- Fractal dimension: D₂ ≈ 2.2
- Symmetry: Rotational symmetry around z-axis

Author: Bob
Date: January 2026
Part of the Alice & Bob Chaotic Attractor Toolkit
"""

import numpy as np
from typing import Dict, Tuple, List
from attractor_base import AttractorBase


class AizawaAttractor(AttractorBase):
    """
    Implementation of the Aizawa attractor system.

    The Aizawa attractor is characterized by its complex, multi-lobed structure
    and moderate chaos. It's visually more intricate than Rössler but less
    "symmetric" than Lorenz.

    Example:
        >>> aizawa = AizawaAttractor()
        >>> trajectory = aizawa.generate_trajectory(t_span=(0, 500), n_points=50000)
        >>> print(f"Trajectory shape: {trajectory.shape}")
        Trajectory shape: (50000, 3)

        >>> # Custom parameters for different dynamics
        >>> aizawa.update_parameters({'a': 0.8, 'c': 0.5})
        >>> custom_traj = aizawa.generate_trajectory(t_span=(0, 500))
    """

    def __init__(self, **kwargs):
        """
        Initialize the Aizawa attractor.

        Parameters:
            **kwargs: Optional parameter overrides (a, b, c, d, e, f)
                     and initial_state override
        """
        super().__init__(**kwargs)

    def derivatives(self, state: np.ndarray, t: float) -> np.ndarray:
        """
        Compute derivatives for the Aizawa system.

        Equations:
            dx/dt = (z - b) * x - d * y
            dy/dt = d * x + (z - b) * y
            dz/dt = c + a * z - (z^3)/3 - (x^2 + y^2) * (1 + e * z) + f * z * x^3

        Parameters:
            state: Current state [x, y, z]
            t: Current time (not used, but required by scipy.integrate.solve_ivp)

        Returns:
            Derivatives [dx/dt, dy/dt, dz/dt]
        """
        x, y, z = state
        a = self.parameters['a']
        b = self.parameters['b']
        c = self.parameters['c']
        d = self.parameters['d']
        e = self.parameters['e']
        f = self.parameters['f']

        dx_dt = (z - b) * x - d * y
        dy_dt = d * x + (z - b) * y
        dz_dt = c + a * z - (z**3)/3 - (x**2 + y**2) * (1 + e * z) + f * z * x**3

        return np.array([dx_dt, dy_dt, dz_dt])

    @staticmethod
    def default_parameters() -> Dict[str, float]:
        """
        Return default parameters that produce chaotic behavior.

        These are the standard parameters used in the literature:
            a = 0.95  (z-damping)
            b = 0.7   (z-shift in x,y equations)
            c = 0.6   (constant forcing)
            d = 3.5   (rotation rate)
            e = 0.25  (nonlinear coupling strength)
            f = 0.1   (cubic coupling strength)

        Returns:
            Dictionary of default parameters
        """
        return {
            'a': 0.95,
            'b': 0.7,
            'c': 0.6,
            'd': 3.5,
            'e': 0.25,
            'f': 0.1
        }

    @staticmethod
    def default_initial_state() -> np.ndarray:
        """
        Return a default initial state that produces typical chaotic behavior.

        Returns:
            Initial state [x0, y0, z0]
        """
        return np.array([0.1, 0.0, 0.0])

    @staticmethod
    def parameter_recommendations() -> Dict[str, Dict[str, float]]:
        """
        Provide parameter sets for different dynamical behaviors.

        Returns:
            Dictionary mapping regime names to parameter sets

        Example:
            >>> params = AizawaAttractor.parameter_recommendations()
            >>> aizawa = AizawaAttractor(**params['chaotic'])
        """
        return {
            'chaotic': {
                'a': 0.95,
                'b': 0.7,
                'c': 0.6,
                'd': 3.5,
                'e': 0.25,
                'f': 0.1
            },
            'alternative_chaotic': {
                'a': 0.85,
                'b': 0.7,
                'c': 0.55,
                'd': 3.5,
                'e': 0.25,
                'f': 0.1
            },
            'more_symmetric': {
                'a': 0.95,
                'b': 0.65,
                'c': 0.6,
                'd': 3.5,
                'e': 0.2,
                'f': 0.15
            },
            'weaker_chaos': {
                'a': 0.8,
                'b': 0.7,
                'c': 0.5,
                'd': 3.0,
                'e': 0.25,
                'f': 0.1
            }
        }

    def generate_butterfly_effect_demo(
        self,
        t_span: Tuple[float, float] = (0, 500),
        n_points: int = 50000,
        perturbation: float = 1e-8
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate two trajectories with nearly identical initial conditions.

        This demonstrates sensitive dependence on initial conditions (butterfly effect).
        Despite starting almost identically, the trajectories diverge exponentially.

        Parameters:
            t_span: Time interval (start, end)
            n_points: Number of points to generate
            perturbation: Size of initial perturbation (default: 1e-8)

        Returns:
            Tuple of (trajectory1, trajectory2), each shape (n_points, 3)

        Example:
            >>> aizawa = AizawaAttractor()
            >>> traj1, traj2 = aizawa.generate_butterfly_effect_demo()
            >>> # Initially close
            >>> print(f"Initial distance: {np.linalg.norm(traj1[0] - traj2[0]):.2e}")
            >>> # Eventually far apart
            >>> print(f"Final distance: {np.linalg.norm(traj1[-1] - traj2[-1]):.2f}")
        """
        # Generate first trajectory
        traj1 = self.generate_trajectory(t_span=t_span, n_points=n_points)

        # Generate second trajectory with tiny perturbation
        original_state = self.initial_state.copy()
        self.initial_state = original_state + perturbation * np.random.randn(3)
        traj2 = self.generate_trajectory(t_span=t_span, n_points=n_points)

        # Restore original state
        self.initial_state = original_state

        return traj1, traj2


if __name__ == "__main__":
    """
    Quick demonstration of the Aizawa attractor.
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    print("=== Aizawa Attractor Demo ===\n")

    # Create attractor
    aizawa = AizawaAttractor()
    print(f"Type: {aizawa.get_info()['type']}")
    print(f"Dimension: {aizawa.get_info()['dimension']}")
    print(f"Parameters: {aizawa.parameters}\n")

    # Generate trajectory
    print("Generating trajectory...")
    trajectory = aizawa.generate_trajectory(t_span=(0, 500), n_points=50000)
    print(f"Generated {len(trajectory)} points\n")

    # Basic statistics
    print("Trajectory Statistics:")
    print(f"  X range: [{trajectory[:, 0].min():.2f}, {trajectory[:, 0].max():.2f}]")
    print(f"  Y range: [{trajectory[:, 1].min():.2f}, {trajectory[:, 1].max():.2f}]")
    print(f"  Z range: [{trajectory[:, 2].min():.2f}, {trajectory[:, 2].max():.2f}]\n")

    # Plot
    print("Creating visualization...")
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
            linewidth=0.5, alpha=0.7, color='purple')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Aizawa Attractor')

    plt.tight_layout()
    plt.savefig('aizawa_demo.png', dpi=150, bbox_inches='tight')
    print("Saved to: aizawa_demo.png")

    print("\n=== Demo Complete ===")
