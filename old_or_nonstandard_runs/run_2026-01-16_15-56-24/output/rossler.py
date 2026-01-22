"""
Rössler attractor implementation.

The Rössler system is a system of three non-linear ordinary differential equations
originally studied by Otto Rössler in 1976. It exhibits chaotic dynamics with a
simpler structure than the Lorenz system, featuring a single-lobed attractor.

Equations:
    dx/dt = -y - z
    dy/dt = x + a*y
    dz/dt = b + z*(x - c)

Standard parameters for chaotic behavior: a=0.2, b=0.2, c=5.7

References:
    Rössler, O. E. (1976). "An equation for continuous chaos".
    Physics Letters A, 57(5), 397-398.
"""

import numpy as np
from typing import Dict, Tuple, Literal
from attractor_base import AttractorBase


class RosslerAttractor(AttractorBase):
    """
    Rössler attractor - a three-dimensional continuous-time chaotic system.

    The Rössler system is simpler than the Lorenz system (only one nonlinear term)
    but still exhibits rich chaotic behavior. Its phase space structure features
    a single-lobed attractor with a distinctive ribbon-like appearance.

    Key features:
        - Single nonlinear term (z*x) makes it easier to analyze
        - Classic demonstration of period-doubling route to chaos
        - Clean geometry suitable for pedagogical purposes
        - Well-suited for Poincaré section analysis

    Example:
        >>> rossler = RosslerAttractor()
        >>> trajectory = rossler.generate_trajectory(t_span=(0, 100), n_points=10000)
        >>> print(trajectory.shape)
        (10000, 3)
    """

    def derivatives(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Compute the Rössler system derivatives.

        Equations:
            dx/dt = -y - z
            dy/dt = x + a*y
            dz/dt = b + z*(x - c)

        Args:
            t: Time (not used in autonomous Rössler system, but required by solve_ivp)
            state: Current state [x, y, z]

        Returns:
            Array of derivatives [dx/dt, dy/dt, dz/dt]
        """
        x, y, z = state
        a = self.parameters['a']
        b = self.parameters['b']
        c = self.parameters['c']

        dx_dt = -y - z
        dy_dt = x + a * y
        dz_dt = b + z * (x - c)

        return np.array([dx_dt, dy_dt, dz_dt])

    @staticmethod
    def default_parameters() -> Dict[str, float]:
        """
        Return default parameters that produce chaotic behavior.

        Returns:
            Dictionary with a=0.2, b=0.2, c=5.7 (classic chaotic regime)
        """
        return {
            'a': 0.2,
            'b': 0.2,
            'c': 5.7
        }

    @staticmethod
    def default_initial_state() -> np.ndarray:
        """
        Return default initial conditions.

        Returns:
            Array [1.0, 1.0, 1.0]
        """
        return np.array([1.0, 1.0, 1.0])

    @staticmethod
    def get_parameter_recommendations() -> Dict[str, Dict[str, float]]:
        """
        Get recommended parameter sets for different dynamical regimes.

        The Rössler system shows rich behavior as parameter 'c' varies while
        keeping a=0.2, b=0.2 fixed. It's a classic example of the period-doubling
        route to chaos.

        Returns:
            Dictionary mapping regime names to parameter dictionaries

        Regimes:
            - periodic: Simple limit cycle (c=2.0)
            - period_2: Period-2 orbit (c=3.5)
            - chaotic: Classic chaotic attractor (c=5.7)
            - highly_chaotic: More complex chaotic behavior (c=10.0)
        """
        return {
            'periodic': {'a': 0.2, 'b': 0.2, 'c': 2.0},
            'period_2': {'a': 0.2, 'b': 0.2, 'c': 3.5},
            'transition': {'a': 0.2, 'b': 0.2, 'c': 4.0},
            'chaotic': {'a': 0.2, 'b': 0.2, 'c': 5.7},
            'highly_chaotic': {'a': 0.2, 'b': 0.2, 'c': 10.0}
        }

    def compute_poincare_section(
        self,
        trajectory: np.ndarray,
        plane: Literal['x', 'y', 'z'] = 'z',
        value: float = 0.0,
        direction: Literal['up', 'down', 'both'] = 'both',
        tolerance: float = None
    ) -> np.ndarray:
        """
        Compute Poincaré section by finding intersections with a plane.

        A Poincaré section reduces the dimensionality of the system by recording
        points where trajectories intersect a specified plane. This is a powerful
        tool for visualizing and analyzing chaotic dynamics.

        Args:
            trajectory: Trajectory array of shape (n_points, 3)
            plane: Which coordinate plane to intersect ('x', 'y', or 'z')
            value: The plane location (e.g., z=0 means the xy-plane)
            direction: 'up' for positive crossings, 'down' for negative, 'both' for all
            tolerance: Maximum distance from plane to count as intersection
                      (if None, uses interpolation for exact crossings)

        Returns:
            Array of shape (n_intersections, 2) containing the intersection points
            in the plane's coordinates. For example, if plane='z', returns (x, y) points.

        Example:
            >>> rossler = RosslerAttractor()
            >>> traj = rossler.generate_trajectory(t_span=(0, 200), n_points=10000)
            >>> section = rossler.compute_poincare_section(traj, plane='z', value=0.0)
            >>> print(f"Found {len(section)} intersections")
        """
        # Determine indices for coordinates
        plane_idx = {'x': 0, 'y': 1, 'z': 2}[plane]
        other_indices = [i for i in range(3) if i != plane_idx]

        # Extract the coordinate perpendicular to the plane
        perp_coord = trajectory[:, plane_idx]

        # Find crossings
        crossings = perp_coord - value

        if tolerance is not None:
            # Simple tolerance-based approach
            near_plane = np.abs(crossings) < tolerance
            indices = np.where(near_plane)[0]

            if direction != 'both':
                # Check direction of crossing
                if len(indices) > 1:
                    velocities = np.diff(perp_coord)
                    if direction == 'up':
                        valid = velocities[indices[:-1]] > 0
                    else:  # down
                        valid = velocities[indices[:-1]] < 0
                    indices = indices[:-1][valid]

            section_points = trajectory[indices][:, other_indices]

        else:
            # Interpolation-based approach for exact crossings
            # Find where sign changes (crossing through the plane)
            signs = np.sign(crossings)
            sign_changes = np.diff(signs) != 0

            indices = np.where(sign_changes)[0]

            if len(indices) == 0:
                return np.array([]).reshape(0, 2)

            # Filter by direction
            if direction == 'up':
                # Only keep upward crossings (negative to positive)
                indices = indices[signs[indices] < 0]
            elif direction == 'down':
                # Only keep downward crossings (positive to negative)
                indices = indices[signs[indices] > 0]

            if len(indices) == 0:
                return np.array([]).reshape(0, 2)

            # Linear interpolation to find exact crossing points
            section_points = []
            for idx in indices:
                # Two points bracketing the crossing
                p1 = trajectory[idx]
                p2 = trajectory[idx + 1]
                c1 = crossings[idx]
                c2 = crossings[idx + 1]

                # Linear interpolation factor
                t = -c1 / (c2 - c1) if c2 != c1 else 0.5

                # Interpolated point
                point = p1 + t * (p2 - p1)

                # Extract coordinates in the plane
                section_points.append(point[other_indices])

            section_points = np.array(section_points)

        return section_points

    def generate_bifurcation_data(
        self,
        parameter: str = 'c',
        param_range: Tuple[float, float] = (2.0, 6.0),
        n_params: int = 200,
        transient_time: float = 50.0,
        sample_time: float = 50.0,
        n_points: int = 2000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate data for a bifurcation diagram.

        A bifurcation diagram shows how the system's behavior changes as a parameter
        varies. For Rössler, varying 'c' shows the period-doubling route to chaos.

        Args:
            parameter: Which parameter to vary (typically 'c')
            param_range: (min, max) range for the parameter
            n_params: Number of parameter values to sample
            transient_time: Time to let system settle before sampling
            sample_time: Time period to sample after transient
            n_points: Number of trajectory points for sampling

        Returns:
            Tuple of (parameter_values, sampled_points) where:
                - parameter_values: array of shape (n_params,)
                - sampled_points: list of arrays, one per parameter value

        Example:
            >>> rossler = RosslerAttractor()
            >>> params, points = rossler.generate_bifurcation_data()
            >>> # Plot points[i] vs params[i] to see bifurcation diagram
        """
        param_values = np.linspace(param_range[0], param_range[1], n_params)
        all_samples = []

        original_param = self.parameters[parameter]

        for param_val in param_values:
            # Update parameter
            self.update_parameters(**{parameter: param_val})

            # Generate trajectory with transient
            total_time = transient_time + sample_time
            trajectory = self.generate_trajectory(
                t_span=(0, total_time),
                n_points=n_points
            )

            # Skip transient, keep only the sampled portion
            transient_points = int(n_points * transient_time / total_time)
            samples = trajectory[transient_points:, :]

            # For bifurcation diagram, often we look at one coordinate (e.g., z)
            # or at Poincaré section points
            all_samples.append(samples)

        # Restore original parameter
        self.update_parameters(**{parameter: original_param})

        return param_values, all_samples

    def get_info(self) -> Dict:
        """
        Get information about the current Rössler attractor configuration.

        Returns:
            Dictionary with type='Rössler' and other system info
        """
        info = super().get_info()
        info['type'] = 'Rössler'
        return info


if __name__ == '__main__':
    # Quick demo
    print("Rössler Attractor Demo")
    print("=" * 50)

    rossler = RosslerAttractor()
    print(f"\nDefault parameters: {rossler.parameters}")
    print(f"Initial state: {rossler.initial_state}")

    # Generate trajectory
    print("\nGenerating trajectory...")
    trajectory = rossler.generate_trajectory(t_span=(0, 100), n_points=10000)
    print(f"Trajectory shape: {trajectory.shape}")
    print(f"X range: [{trajectory[:, 0].min():.2f}, {trajectory[:, 0].max():.2f}]")
    print(f"Y range: [{trajectory[:, 1].min():.2f}, {trajectory[:, 1].max():.2f}]")
    print(f"Z range: [{trajectory[:, 2].min():.2f}, {trajectory[:, 2].max():.2f}]")

    # Compute Poincaré section
    print("\nComputing Poincaré section (z=0 plane)...")
    section = rossler.compute_poincare_section(trajectory, plane='z', value=0.0)
    print(f"Found {len(section)} intersection points")

    print("\nParameter recommendations:")
    for name, params in RosslerAttractor.get_parameter_recommendations().items():
        print(f"  {name}: c={params['c']}")
