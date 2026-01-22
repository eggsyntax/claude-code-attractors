"""
Attractor Art Gallery: Publication-Quality Artistic Visualizations

This module creates beautiful, high-resolution artistic renderings of strange attractors
suitable for publication, presentation, or display. It uses advanced matplotlib techniques
including alpha blending, custom colormaps, strategic lighting, and density-based rendering.

The goal is to showcase the beauty of chaos - making the mathematical structures visually
compelling while remaining scientifically accurate.

Author: Alice
Date: January 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from scipy.integrate import solve_ivp
from mpl_toolkits.mplot3d import Axes3D
import warnings
warnings.filterwarnings('ignore')


class ArtisticRenderer:
    """
    Creates publication-quality artistic renderings of strange attractors.

    Features:
    - High-resolution rendering with density-based alpha blending
    - Custom color schemes (monochrome, gradient, rainbow, fire)
    - Strategic lighting and perspective
    - Clean, minimalist aesthetic
    - Multiple composition styles (single, triptych, comparison)
    """

    def __init__(self, dpi=300, figsize=(12, 8)):
        """
        Initialize the artistic renderer.

        Args:
            dpi: Resolution in dots per inch (default 300 for publication quality)
            figsize: Figure size in inches (default 12x8)
        """
        self.dpi = dpi
        self.figsize = figsize

    def lorenz(self, t, state, sigma=10.0, beta=8/3, rho=28.0):
        """Lorenz system equations."""
        x, y, z = state
        return [
            sigma * (y - x),
            x * (rho - z) - y,
            x * y - beta * z
        ]

    def rossler(self, t, state, a=0.2, b=0.2, c=5.7):
        """Rössler system equations."""
        x, y, z = state
        return [
            -y - z,
            x + a * y,
            b + z * (x - c)
        ]

    def thomas(self, t, state, b=0.208):
        """Thomas system equations."""
        x, y, z = state
        return [
            np.sin(y) - b * x,
            np.sin(z) - b * y,
            np.sin(x) - b * z
        ]

    def generate_trajectory(self, system, initial_state, t_span=(0, 100), dt=0.01):
        """
        Generate trajectory for a given system.

        Args:
            system: Function defining the differential equations
            initial_state: Initial conditions [x0, y0, z0]
            t_span: Time span tuple (t_start, t_end)
            dt: Time step for integration

        Returns:
            Array of shape (n_points, 3) containing trajectory
        """
        t_eval = np.arange(t_span[0], t_span[1], dt)
        sol = solve_ivp(
            system,
            t_span,
            initial_state,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-8,
            atol=1e-10
        )
        return sol.y.T

    def create_custom_colormap(self, style='gradient'):
        """
        Create custom colormaps for artistic rendering.

        Args:
            style: Color style - 'gradient', 'fire', 'ice', 'monochrome', 'rainbow'

        Returns:
            matplotlib colormap
        """
        if style == 'gradient':
            colors = ['#0d1b2a', '#1b263b', '#415a77', '#778da9', '#e0e1dd']
        elif style == 'fire':
            colors = ['#03071e', '#370617', '#6a040f', '#9d0208', '#d00000', '#dc2f02', '#e85d04', '#f48c06', '#faa307', '#ffba08']
        elif style == 'ice':
            colors = ['#03045e', '#023e8a', '#0077b6', '#0096c7', '#00b4d8', '#48cae4', '#90e0ef', '#ade8f4', '#caf0f8']
        elif style == 'monochrome':
            colors = ['#000000', '#1a1a1a', '#333333', '#4d4d4d', '#666666', '#808080', '#999999', '#b3b3b3', '#cccccc', '#e6e6e6']
        elif style == 'rainbow':
            colors = ['#540d6e', '#ee4266', '#ffd23f', '#3bceac', '#0ead69']
        else:
            colors = ['#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51']

        return LinearSegmentedColormap.from_list('custom', colors)

    def render_single_attractor(self, trajectory, title, color_style='gradient',
                                elevation=20, azimuth=45, alpha_fade=True):
        """
        Render a single attractor with artistic styling.

        Args:
            trajectory: Array of shape (n_points, 3)
            title: Title for the plot
            color_style: Color scheme to use
            elevation: Viewing elevation angle
            azimuth: Viewing azimuth angle
            alpha_fade: Whether to use density-based alpha blending

        Returns:
            matplotlib figure
        """
        fig = plt.figure(figsize=self.figsize, dpi=self.dpi, facecolor='white')
        ax = fig.add_subplot(111, projection='3d', facecolor='white')

        # Extract coordinates
        x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]

        # Create color array based on trajectory progression
        n_points = len(x)
        colors = np.linspace(0, 1, n_points)

        # Create custom colormap
        cmap = self.create_custom_colormap(color_style)

        # Render with density-based alpha
        if alpha_fade:
            # Use alpha that increases along trajectory (fades in)
            alphas = np.linspace(0.1, 0.8, n_points)
            for i in range(n_points - 1):
                ax.plot(x[i:i+2], y[i:i+2], z[i:i+2],
                       color=cmap(colors[i]),
                       alpha=alphas[i],
                       linewidth=0.5)
        else:
            ax.plot(x, y, z, color=cmap(0.5), alpha=0.6, linewidth=0.5)

        # Customize view
        ax.view_init(elev=elevation, azim=azimuth)

        # Remove axes for clean aesthetic
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_zlabel('')
        ax.set_title(title, fontsize=20, fontweight='bold', pad=20)

        # Minimal grid
        ax.grid(True, alpha=0.1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

        # Remove background panes
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False

        plt.tight_layout()
        return fig

    def render_triptych(self, save_path='attractor_triptych.png'):
        """
        Create a triptych (three-panel) artistic rendering of all three attractors.

        This creates a unified artistic composition showing Lorenz, Rössler, and Thomas
        side by side with consistent styling.

        Args:
            save_path: Path to save the output image
        """
        # Generate trajectories
        print("Generating trajectories...")
        lorenz_traj = self.generate_trajectory(
            self.lorenz,
            [1.0, 1.0, 1.0],
            t_span=(0, 100),
            dt=0.01
        )

        rossler_traj = self.generate_trajectory(
            self.rossler,
            [1.0, 1.0, 1.0],
            t_span=(0, 300),
            dt=0.01
        )

        thomas_traj = self.generate_trajectory(
            self.thomas,
            [0.1, 0.0, 0.0],
            t_span=(0, 1000),
            dt=0.02
        )

        # Create figure with three subplots
        print("Rendering triptych...")
        fig = plt.figure(figsize=(18, 6), dpi=self.dpi, facecolor='white')

        # Lorenz (left panel)
        ax1 = fig.add_subplot(131, projection='3d', facecolor='white')
        self._render_on_axis(ax1, lorenz_traj, 'Lorenz Attractor', 'fire', 20, 45)

        # Rössler (center panel)
        ax2 = fig.add_subplot(132, projection='3d', facecolor='white')
        self._render_on_axis(ax2, rossler_traj, 'Rössler Attractor', 'ice', 20, 45)

        # Thomas (right panel)
        ax3 = fig.add_subplot(133, projection='3d', facecolor='white')
        self._render_on_axis(ax3, thomas_traj, 'Thomas Attractor', 'gradient', 20, 45)

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight', facecolor='white')
        print(f"Saved triptych to {save_path}")
        plt.close()

    def _render_on_axis(self, ax, trajectory, title, color_style, elevation, azimuth):
        """Helper method to render trajectory on an existing axis."""
        x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]
        n_points = len(x)
        colors = np.linspace(0, 1, n_points)
        cmap = self.create_custom_colormap(color_style)

        # Density-based alpha blending
        alphas = np.linspace(0.1, 0.8, n_points)
        for i in range(0, n_points - 1, 2):  # Skip points for performance
            ax.plot(x[i:i+2], y[i:i+2], z[i:i+2],
                   color=cmap(colors[i]),
                   alpha=alphas[i],
                   linewidth=0.4)

        ax.view_init(elev=elevation, azim=azimuth)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False

    def render_multi_perspective(self, system_name='lorenz', save_path='multi_perspective.png'):
        """
        Create a multi-perspective view of a single attractor from four angles.

        Args:
            system_name: Which system to render ('lorenz', 'rossler', 'thomas')
            save_path: Path to save the output image
        """
        # Generate trajectory
        print(f"Generating {system_name} trajectory...")
        if system_name.lower() == 'lorenz':
            trajectory = self.generate_trajectory(self.lorenz, [1.0, 1.0, 1.0], t_span=(0, 100), dt=0.01)
            title_base = 'Lorenz Attractor'
            color_style = 'fire'
        elif system_name.lower() == 'rossler':
            trajectory = self.generate_trajectory(self.rossler, [1.0, 1.0, 1.0], t_span=(0, 300), dt=0.01)
            title_base = 'Rössler Attractor'
            color_style = 'ice'
        else:  # thomas
            trajectory = self.generate_trajectory(self.thomas, [0.1, 0.0, 0.0], t_span=(0, 1000), dt=0.02)
            title_base = 'Thomas Attractor'
            color_style = 'gradient'

        # Create figure with 2x2 grid
        print("Rendering multi-perspective view...")
        fig = plt.figure(figsize=(14, 14), dpi=self.dpi, facecolor='white')

        perspectives = [
            (20, 45, 'Front-Right View'),
            (20, 135, 'Front-Left View'),
            (20, 225, 'Back-Left View'),
            (20, 315, 'Back-Right View')
        ]

        for i, (elev, azim, subtitle) in enumerate(perspectives, 1):
            ax = fig.add_subplot(2, 2, i, projection='3d', facecolor='white')
            self._render_on_axis(ax, trajectory, f'{title_base}\n{subtitle}', color_style, elev, azim)

        plt.suptitle(f'{title_base}: Four Perspectives', fontsize=20, fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight', facecolor='white')
        print(f"Saved multi-perspective view to {save_path}")
        plt.close()

    def render_high_res_single(self, system_name='lorenz', color_style='fire',
                              save_path='attractor_highres.png'):
        """
        Create a single high-resolution artistic rendering perfect for display or publication.

        Args:
            system_name: Which system to render
            color_style: Color scheme
            save_path: Path to save the output
        """
        print(f"Generating high-resolution {system_name} attractor...")

        # Generate long trajectory for density
        if system_name.lower() == 'lorenz':
            trajectory = self.generate_trajectory(self.lorenz, [1.0, 1.0, 1.0], t_span=(0, 150), dt=0.005)
            title = 'The Lorenz Attractor'
        elif system_name.lower() == 'rossler':
            trajectory = self.generate_trajectory(self.rossler, [1.0, 1.0, 1.0], t_span=(0, 400), dt=0.005)
            title = 'The Rössler Attractor'
        else:  # thomas
            trajectory = self.generate_trajectory(self.thomas, [0.1, 0.0, 0.0], t_span=(0, 1500), dt=0.01)
            title = 'The Thomas Attractor'

        print("Rendering high-resolution image...")
        fig = self.render_single_attractor(
            trajectory,
            title,
            color_style=color_style,
            elevation=20,
            azimuth=45,
            alpha_fade=True
        )

        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight', facecolor='white')
        print(f"Saved high-resolution image to {save_path}")
        plt.close()


def create_gallery():
    """
    Create a complete art gallery of attractor visualizations.

    Generates:
    1. Triptych of all three attractors
    2. Multi-perspective view of Lorenz
    3. High-resolution individual renders
    """
    print("\n" + "="*60)
    print("STRANGE ATTRACTORS ART GALLERY")
    print("="*60 + "\n")

    renderer = ArtisticRenderer(dpi=300, figsize=(12, 8))

    # 1. Triptych
    print("\n[1/5] Creating triptych (three-panel composition)...")
    renderer.render_triptych('attractor_triptych.png')

    # 2. Multi-perspective Lorenz
    print("\n[2/5] Creating multi-perspective Lorenz view...")
    renderer.render_multi_perspective('lorenz', 'lorenz_perspectives.png')

    # 3. High-res individual renders
    print("\n[3/5] Creating high-res Lorenz (fire colormap)...")
    renderer.render_high_res_single('lorenz', 'fire', 'lorenz_highres.png')

    print("\n[4/5] Creating high-res Rössler (ice colormap)...")
    renderer.render_high_res_single('rossler', 'ice', 'rossler_highres.png')

    print("\n[5/5] Creating high-res Thomas (gradient colormap)...")
    renderer.render_high_res_single('thomas', 'gradient', 'thomas_highres.png')

    print("\n" + "="*60)
    print("GALLERY COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print("  - attractor_triptych.png (three-panel comparison)")
    print("  - lorenz_perspectives.png (four viewing angles)")
    print("  - lorenz_highres.png (publication-quality)")
    print("  - rossler_highres.png (publication-quality)")
    print("  - thomas_highres.png (publication-quality)")
    print("\nAll images are 300 DPI, suitable for publication or display.\n")


if __name__ == '__main__':
    create_gallery()
