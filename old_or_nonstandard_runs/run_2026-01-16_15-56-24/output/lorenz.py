"""
Lorenz attractor implementation.

The Lorenz system is a set of three coupled ordinary differential equations
originally studied by Edward Lorenz in 1963 as a simplified model of atmospheric
convection. It was one of the first examples of a chaotic dynamical system and
gave rise to the famous "butterfly effect."

The system equations are:
    dx/dt = σ(y - x)
    dy/dt = x(ρ - z) - y
    dz/dt = xy - βz

Where:
    σ (sigma): Prandtl number (relates viscosity to thermal conductivity)
    ρ (rho): Rayleigh number (relates buoyancy to viscosity)
    β (beta): Geometric factor

For the classic chaotic behavior, use σ=10, ρ=28, β=8/3.

Example:
    from lorenz import LorenzAttractor
    from visualizer import AttractorVisualizer

    # Create attractor with default parameters
    lorenz = LorenzAttractor()

    # Generate trajectory
    trajectory = lorenz.generate_trajectory(t_span=(0, 50), n_points=10000)

    # Visualize
    vis = AttractorVisualizer()
    vis.plot_trajectory_3d(trajectory, title="Lorenz Attractor")

    # Explore parameter space
    lorenz.update_parameters(rho=99.96)  # Different behavior at rho≈100
    trajectory2 = lorenz.generate_trajectory(t_span=(0, 50), n_points=10000)
"""

import numpy as np
from typing import Dict
from attractor_base import AttractorBase


class LorenzAttractor(AttractorBase):
    """
    The Lorenz attractor - the iconic butterfly-shaped strange attractor.

    This system exhibits chaotic behavior for certain parameter values,
    most famously for σ=10, ρ=28, β=8/3. The attractor has two lobes
    resembling butterfly wings, with trajectories spiraling around one
    lobe before unpredictably switching to the other.

    Key behaviors at different ρ values:
        ρ < 1: Trajectories converge to origin
        1 < ρ < 13.926: Converges to fixed points
        13.926 < ρ < 24.74: Oscillates between fixed points
        ρ ≈ 24.74: Onset of chaos
        ρ = 28: Classic chaotic attractor (most famous)
        ρ > 28: Various chaotic and periodic behaviors
    """

    def __init__(
        self,
        initial_state: np.ndarray = None,
        parameters: Dict[str, float] = None
    ):
        """
        Initialize the Lorenz attractor.

        Args:
            initial_state: Initial [x, y, z]. If None, uses [1.0, 1.0, 1.0]
            parameters: Dict with 'sigma', 'rho', 'beta'. If None, uses classic values
        """
        super().__init__(
            initial_state=initial_state,
            parameters=parameters,
            dimension=3
        )

    def default_parameters(self) -> Dict[str, float]:
        """
        Return classic Lorenz parameters that produce chaotic behavior.

        Returns:
            σ=10, ρ=28, β=8/3
        """
        return {
            'sigma': 10.0,
            'rho': 28.0,
            'beta': 8.0 / 3.0
        }

    def default_initial_state(self) -> np.ndarray:
        """
        Return default initial conditions.

        Returns:
            [1.0, 1.0, 1.0] - a point near the attractor
        """
        return np.array([1.0, 1.0, 1.0])

    def derivatives(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Compute Lorenz system derivatives.

        The Lorenz equations are:
            dx/dt = σ(y - x)
            dy/dt = x(ρ - z) - y
            dz/dt = xy - βz

        Args:
            t: Time (not used - system is autonomous)
            state: Current state [x, y, z]

        Returns:
            Derivatives [dx/dt, dy/dt, dz/dt]
        """
        x, y, z = state
        sigma = self.parameters['sigma']
        rho = self.parameters['rho']
        beta = self.parameters['beta']

        dx_dt = sigma * (y - x)
        dy_dt = x * (rho - z) - y
        dz_dt = x * y - beta * z

        return np.array([dx_dt, dy_dt, dz_dt])

    def generate_butterfly_effect_demo(
        self,
        epsilon: float = 1e-8,
        t_span: tuple = (0, 40),
        n_points: int = 10000
    ) -> tuple:
        """
        Generate two trajectories with nearly identical initial conditions.

        This demonstrates the butterfly effect: tiny differences in initial
        conditions lead to dramatically different trajectories over time.

        Args:
            epsilon: Small perturbation to add to initial conditions
            t_span: Time span for integration
            n_points: Number of points in trajectory

        Returns:
            tuple: (trajectory1, trajectory2) where trajectories start
                   nearly identically but diverge over time

        Example:
            lorenz = LorenzAttractor()
            traj1, traj2 = lorenz.generate_butterfly_effect_demo()

            # Initially very close
            assert np.allclose(traj1[0], traj2[0], atol=1e-7)

            # But diverge significantly by the end
            assert not np.allclose(traj1[-1], traj2[-1], atol=1)
        """
        # Generate first trajectory
        traj1 = self.generate_trajectory(t_span=t_span, n_points=n_points)

        # Perturb initial state slightly
        original_state = self.initial_state.copy()
        perturbed_state = original_state + epsilon
        self.set_initial_state(perturbed_state)

        # Generate second trajectory
        traj2 = self.generate_trajectory(t_span=t_span, n_points=n_points)

        # Restore original state
        self.set_initial_state(original_state)

        return traj1, traj2

    @staticmethod
    def get_parameter_recommendations() -> Dict[str, Dict]:
        """
        Get recommended parameter values for exploring different behaviors.

        Returns:
            Dictionary of named parameter sets with descriptions

        Example:
            recommendations = LorenzAttractor.get_parameter_recommendations()
            lorenz = LorenzAttractor()
            lorenz.update_parameters(**recommendations['classic']['params'])
        """
        return {
            'classic': {
                'params': {'sigma': 10.0, 'rho': 28.0, 'beta': 8.0/3.0},
                'description': 'Classic chaotic butterfly attractor'
            },
            'pre_turbulent': {
                'params': {'sigma': 10.0, 'rho': 99.96, 'beta': 8.0/3.0},
                'description': 'Pre-turbulent regime, more complex structure'
            },
            'periodic': {
                'params': {'sigma': 10.0, 'rho': 160.0, 'beta': 8.0/3.0},
                'description': 'Periodic behavior, loses chaos'
            },
            'onset_of_chaos': {
                'params': {'sigma': 10.0, 'rho': 24.74, 'beta': 8.0/3.0},
                'description': 'Right at the edge of chaos'
            },
            'converging': {
                'params': {'sigma': 10.0, 'rho': 0.5, 'beta': 8.0/3.0},
                'description': 'Converges to origin, no chaos'
            }
        }
