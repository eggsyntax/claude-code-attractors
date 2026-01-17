"""
Thomas Attractor - A beautiful 3D strange attractor with rotational symmetry.

The Thomas attractor was introduced by René Thomas as a simplified model
demonstrating chaotic behavior with elegant cyclical symmetry. Unlike the
Lorenz and Rössler attractors, it has a distinctive circular flow pattern.

System equations:
    dx/dt = sin(y) - b*x
    dy/dt = sin(z) - b*y
    dz/dt = sin(x) - b*z

Parameter:
    b: Damping coefficient (classic value: b = 0.208186)

The attractor exhibits chaotic behavior for b ≈ 0.208186, creating a
beautiful attractor with approximate rotational symmetry around the
main diagonal (x=y=z line).

References:
    Thomas, R. (1999). "Deterministic chaos seen in terms of feedback circuits:
    Analysis, synthesis, 'labyrinth chaos'". International Journal of
    Bifurcation and Chaos.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.integrate import solve_ivp
import plotly.graph_objects as go
from attractors import Attractor


class ThomasAttractor(Attractor):
    """
    Thomas attractor implementation.

    A 3D strange attractor with elegant cyclical symmetry discovered by
    René Thomas. The system has beautiful rotational properties and creates
    a distinctive circular flow pattern.

    Parameters
    ----------
    b : float, default=0.208186
        Damping coefficient. Classic chaotic value is b ≈ 0.208186.
        - b < 0.1: More complex, multi-looped behavior
        - b ≈ 0.208186: Classic Thomas attractor
        - b > 0.3: Simpler, more regular behavior

    Attributes
    ----------
    b : float
        The damping coefficient

    Examples
    --------
    >>> thomas = ThomasAttractor(b=0.208186)
    >>> trajectory = thomas.simulate(duration=200.0, dt=0.01)
    >>> fig, ax = thomas.plot_3d_matplotlib(trajectory)
    """

    def __init__(self, b=0.208186):
        """
        Initialize Thomas attractor with given parameter.

        Parameters
        ----------
        b : float, default=0.208186
            Damping coefficient
        """
        self.b = b
        super().__init__()

    def equations(self, t, state):
        """
        Compute derivatives for the Thomas system.

        The Thomas attractor uses trigonometric coupling between variables,
        creating its distinctive circular symmetry:

        dx/dt = sin(y) - b*x
        dy/dt = sin(z) - b*y
        dz/dt = sin(x) - b*z

        Notice the cyclic symmetry: each variable is driven by the sine of
        the next variable in the cycle, with damping on itself.

        Parameters
        ----------
        t : float
            Time (not used, system is autonomous)
        state : array-like, shape (3,)
            Current state [x, y, z]

        Returns
        -------
        derivatives : ndarray, shape (3,)
            Time derivatives [dx/dt, dy/dt, dz/dt]
        """
        x, y, z = state

        dx_dt = np.sin(y) - self.b * x
        dy_dt = np.sin(z) - self.b * y
        dz_dt = np.sin(x) - self.b * z

        return np.array([dx_dt, dy_dt, dz_dt])

    def default_initial_state(self):
        """
        Return a sensible initial condition for the Thomas attractor.

        Returns
        -------
        state : ndarray, shape (3,)
            Initial state [x, y, z]
        """
        # A small perturbation from origin works well
        return np.array([0.1, 0.0, 0.0])


def demonstrate_thomas():
    """
    Create comprehensive visualizations of the Thomas attractor.

    Generates:
    1. Static matplotlib 3D plot
    2. Interactive plotly visualization
    3. Multiple views showing different perspectives
    """
    print("=" * 60)
    print("Thomas Attractor Demonstration")
    print("=" * 60)
    print()
    print("The Thomas attractor is a beautiful strange attractor with")
    print("elegant rotational symmetry. It was introduced by René Thomas")
    print("as a simplified chaotic system with cyclical coupling.")
    print()

    # Create Thomas attractor with classic parameter
    thomas = ThomasAttractor(b=0.208186)

    print(f"Parameters: b = {thomas.b}")
    print(f"Initial state: {thomas.default_initial_state()}")
    print()

    # Simulate for a long time to get the full structure
    print("Simulating trajectory (200 time units)...")
    trajectory = thomas.simulate(duration=200.0, dt=0.01)
    print(f"Generated {len(trajectory)} points")
    print()

    # Create static matplotlib visualization
    print("Creating static visualization...")
    fig, ax = thomas.plot_3d_matplotlib(
        trajectory,
        title="Thomas Attractor (b=0.208186)",
        figsize=(12, 10)
    )
    filename = 'thomas_attractor_static.png'
    fig.savefig(filename, dpi=200, bbox_inches='tight')
    print(f"✓ Saved: {filename}")
    plt.close()

    # Create interactive plotly visualization
    print("Creating interactive visualization...")
    fig = thomas.plot_3d_interactive(
        trajectory,
        title="Thomas Attractor - Interactive 3D View (b=0.208186)"
    )
    filename = 'thomas_attractor_interactive.html'
    fig.write_html(filename)
    print(f"✓ Saved: {filename}")
    print()

    # Create multi-view figure showing different perspectives
    print("Creating multi-view perspective plot...")
    fig = plt.figure(figsize=(16, 12))

    # Extract coordinates
    x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]

    # 3D view
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    ax1.plot(x, y, z, linewidth=0.5, alpha=0.8, color='purple')
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_zlabel('z')
    ax1.set_title('3D View')
    ax1.grid(True, alpha=0.3)

    # XY projection
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(x, y, linewidth=0.3, alpha=0.6, color='purple')
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    ax2.set_title('XY Projection')
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')

    # XZ projection
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(x, z, linewidth=0.3, alpha=0.6, color='purple')
    ax3.set_xlabel('x')
    ax3.set_ylabel('z')
    ax3.set_title('XZ Projection')
    ax3.grid(True, alpha=0.3)
    ax3.set_aspect('equal')

    # YZ projection
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(y, z, linewidth=0.3, alpha=0.6, color='purple')
    ax4.set_xlabel('y')
    ax4.set_ylabel('z')
    ax4.set_title('YZ Projection')
    ax4.grid(True, alpha=0.3)
    ax4.set_aspect('equal')

    fig.suptitle('Thomas Attractor - Multiple Perspectives (b=0.208186)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    filename = 'thomas_attractor_multiview.png'
    fig.savefig(filename, dpi=200, bbox_inches='tight')
    print(f"✓ Saved: {filename}")
    plt.close()

    print()
    print("=" * 60)
    print("Key Properties of Thomas Attractor")
    print("=" * 60)
    print()
    print("• Rotational Symmetry: Near-symmetric around x=y=z diagonal")
    print("• Circular Flow: Distinctive loop structure, unlike Lorenz butterfly")
    print("• Trigonometric Coupling: Uses sin() functions for smooth dynamics")
    print("• Cyclic Equations: Each variable depends on next in cycle")
    print("• Chaotic Regime: b ≈ 0.208186 gives classic strange attractor")
    print()
    print("Notice in the projections how the attractor maintains approximate")
    print("circular symmetry - each 2D projection shows similar loop structure.")
    print("This is quite different from the asymmetric Lorenz butterfly!")
    print()
    print("=" * 60)


def compare_thomas_parameters():
    """
    Show how Thomas attractor changes with parameter b.

    Creates a comparison grid showing the attractor at different b values,
    demonstrating the transition from simpler to more complex behavior.
    """
    print("=" * 60)
    print("Thomas Parameter Exploration")
    print("=" * 60)
    print()

    # Sample different b values
    b_values = [0.1, 0.15, 0.208186, 0.25, 0.3, 0.35]

    fig = plt.figure(figsize=(18, 12))

    for idx, b in enumerate(b_values, 1):
        print(f"Simulating b = {b:.6f}...")

        thomas = ThomasAttractor(b=b)
        trajectory = thomas.simulate(duration=200.0, dt=0.01)

        x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]

        ax = fig.add_subplot(2, 3, idx, projection='3d')
        ax.plot(x, y, z, linewidth=0.4, alpha=0.7, color='purple')
        ax.set_xlabel('x', fontsize=8)
        ax.set_ylabel('y', fontsize=8)
        ax.set_zlabel('z', fontsize=8)
        ax.set_title(f'b = {b:.6f}', fontsize=10, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Add note for classic value
        if abs(b - 0.208186) < 0.0001:
            ax.text2D(0.5, 0.95, '(Classic)', transform=ax.transAxes,
                     ha='center', fontsize=9, style='italic',
                     bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    fig.suptitle('Thomas Attractor - Parameter Exploration',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    filename = 'thomas_parameter_comparison.png'
    fig.savefig(filename, dpi=200, bbox_inches='tight')
    print(f"\n✓ Saved: {filename}")
    plt.close()

    print()
    print("=" * 60)
    print("Parameter Effects")
    print("=" * 60)
    print()
    print("As b changes, the Thomas attractor morphs significantly:")
    print()
    print("• b < 0.15: More spread out, complex multi-loop structure")
    print("• b ≈ 0.208186: Classic compact attractor with clear loops")
    print("• b > 0.25: More compressed, simpler trajectories")
    print()
    print("The 'sweet spot' around b = 0.208186 gives the most aesthetically")
    print("pleasing and mathematically interesting behavior!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_thomas()
    print()
    compare_thomas_parameters()
