"""
Visualization utilities for strange attractors.

This module provides tools for visualizing 3D attractor trajectories,
including multiple trajectory overlays and phase space projections.

Author: Alice
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple, Optional
import matplotlib.animation as animation


class AttractorVisualizer:
    """
    Visualizer for 3D strange attractor trajectories.

    Supports:
    - 3D trajectory plotting with customizable styling
    - Multiple trajectory overlays (useful for showing sensitivity to initial conditions)
    - 2D phase space projections from different viewing angles
    - Animation of trajectory evolution
    """

    def __init__(self, figsize: Tuple[int, int] = (12, 9)):
        """
        Initialize the visualizer.

        Args:
            figsize: Figure size as (width, height) in inches
        """
        self.figsize = figsize
        self.fig = None
        self.ax = None

    def plot_trajectory_3d(
        self,
        trajectory: np.ndarray,
        title: str = "Strange Attractor",
        labels: Tuple[str, str, str] = ("X", "Y", "Z"),
        color: str = 'blue',
        alpha: float = 0.7,
        linewidth: float = 0.5,
        show: bool = True
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot a single 3D trajectory.

        Args:
            trajectory: Array of shape (n_points, 3) containing [x, y, z] coordinates
            title: Plot title
            labels: Axis labels as (x_label, y_label, z_label)
            color: Line color
            alpha: Line transparency (0=transparent, 1=opaque)
            linewidth: Line width
            show: Whether to display the plot immediately

        Returns:
            Figure and axes objects for further customization
        """
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection='3d')

        x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]

        self.ax.plot(x, y, z, color=color, alpha=alpha, linewidth=linewidth)
        self.ax.set_xlabel(labels[0])
        self.ax.set_ylabel(labels[1])
        self.ax.set_zlabel(labels[2])
        self.ax.set_title(title)

        if show:
            plt.show()

        return self.fig, self.ax

    def plot_multiple_trajectories(
        self,
        trajectories: List[np.ndarray],
        title: str = "Multiple Trajectories",
        labels: Tuple[str, str, str] = ("X", "Y", "Z"),
        colors: Optional[List[str]] = None,
        alpha: float = 0.6,
        linewidth: float = 0.5,
        show: bool = True
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot multiple trajectories on the same axes to show sensitivity to initial conditions.

        Args:
            trajectories: List of arrays, each of shape (n_points, 3)
            title: Plot title
            labels: Axis labels
            colors: List of colors for each trajectory (if None, uses color cycle)
            alpha: Line transparency
            linewidth: Line width
            show: Whether to display immediately

        Returns:
            Figure and axes objects
        """
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection='3d')

        if colors is None:
            # Use matplotlib's default color cycle
            colors = plt.cm.tab10(np.linspace(0, 1, len(trajectories)))

        for i, traj in enumerate(trajectories):
            x, y, z = traj[:, 0], traj[:, 1], traj[:, 2]
            color = colors[i] if i < len(colors) else colors[-1]
            self.ax.plot(x, y, z, color=color, alpha=alpha, linewidth=linewidth,
                        label=f"Trajectory {i+1}")

        self.ax.set_xlabel(labels[0])
        self.ax.set_ylabel(labels[1])
        self.ax.set_zlabel(labels[2])
        self.ax.set_title(title)
        self.ax.legend()

        if show:
            plt.show()

        return self.fig, self.ax

    def plot_phase_projections(
        self,
        trajectory: np.ndarray,
        title: str = "Phase Space Projections",
        labels: Tuple[str, str, str] = ("X", "Y", "Z"),
        color: str = 'blue',
        alpha: float = 0.7,
        linewidth: float = 0.5,
        show: bool = True
    ) -> Tuple[plt.Figure, List[plt.Axes]]:
        """
        Plot 2D projections of the trajectory onto each coordinate plane.

        Creates a 2x2 grid with:
        - Top left: 3D view
        - Top right: XY projection
        - Bottom left: XZ projection
        - Bottom right: YZ projection

        Args:
            trajectory: Array of shape (n_points, 3)
            title: Overall figure title
            labels: Axis labels
            color: Line color
            alpha: Line transparency
            linewidth: Line width
            show: Whether to display immediately

        Returns:
            Figure and list of axes objects
        """
        self.fig = plt.figure(figsize=self.figsize)
        self.fig.suptitle(title, fontsize=14)

        x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]

        # 3D view
        ax1 = self.fig.add_subplot(221, projection='3d')
        ax1.plot(x, y, z, color=color, alpha=alpha, linewidth=linewidth)
        ax1.set_xlabel(labels[0])
        ax1.set_ylabel(labels[1])
        ax1.set_zlabel(labels[2])
        ax1.set_title("3D View")

        # XY projection
        ax2 = self.fig.add_subplot(222)
        ax2.plot(x, y, color=color, alpha=alpha, linewidth=linewidth)
        ax2.set_xlabel(labels[0])
        ax2.set_ylabel(labels[1])
        ax2.set_title(f"{labels[0]}-{labels[1]} Projection")
        ax2.grid(True, alpha=0.3)

        # XZ projection
        ax3 = self.fig.add_subplot(223)
        ax3.plot(x, z, color=color, alpha=alpha, linewidth=linewidth)
        ax3.set_xlabel(labels[0])
        ax3.set_ylabel(labels[2])
        ax3.set_title(f"{labels[0]}-{labels[2]} Projection")
        ax3.grid(True, alpha=0.3)

        # YZ projection
        ax4 = self.fig.add_subplot(224)
        ax4.plot(y, z, color=color, alpha=alpha, linewidth=linewidth)
        ax4.set_xlabel(labels[1])
        ax4.set_ylabel(labels[2])
        ax4.set_title(f"{labels[1]}-{labels[2]} Projection")
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        if show:
            plt.show()

        return self.fig, [ax1, ax2, ax3, ax4]

    def create_animation(
        self,
        trajectory: np.ndarray,
        title: str = "Attractor Animation",
        labels: Tuple[str, str, str] = ("X", "Y", "Z"),
        color: str = 'blue',
        frames: int = 200,
        interval: int = 50,
        save_path: Optional[str] = None
    ) -> animation.FuncAnimation:
        """
        Create an animation showing the trajectory being drawn over time.

        Args:
            trajectory: Array of shape (n_points, 3)
            title: Animation title
            labels: Axis labels
            color: Line color
            frames: Number of animation frames
            interval: Delay between frames in milliseconds
            save_path: If provided, save animation to this path (e.g., "attractor.gif")

        Returns:
            Animation object
        """
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection='3d')

        x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]

        self.ax.set_xlabel(labels[0])
        self.ax.set_ylabel(labels[1])
        self.ax.set_zlabel(labels[2])
        self.ax.set_title(title)

        # Set fixed axis limits based on trajectory bounds
        self.ax.set_xlim([x.min(), x.max()])
        self.ax.set_ylim([y.min(), y.max()])
        self.ax.set_zlim([z.min(), z.max()])

        line, = self.ax.plot([], [], [], color=color, linewidth=0.5)

        # Calculate how many points to show per frame
        points_per_frame = max(1, len(trajectory) // frames)

        def init():
            line.set_data([], [])
            line.set_3d_properties([])
            return line,

        def animate(frame):
            end_idx = min((frame + 1) * points_per_frame, len(trajectory))
            line.set_data(x[:end_idx], y[:end_idx])
            line.set_3d_properties(z[:end_idx])
            return line,

        anim = animation.FuncAnimation(
            self.fig, animate, init_func=init,
            frames=frames, interval=interval, blit=True
        )

        if save_path:
            anim.save(save_path, writer='pillow')
            print(f"Animation saved to {save_path}")

        return anim


    def plot_poincare_section_2d(
        self,
        section_points: np.ndarray,
        title: str = "Poincaré Section",
        labels: Tuple[str, str] = ("u", "v"),
        color: str = 'red',
        alpha: float = 0.6,
        marker: str = '.',
        markersize: float = 2,
        colormap: Optional[str] = None,
        show: bool = True
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot a 2D Poincaré section.

        Args:
            section_points: Array of shape (n_points, 2) containing section coordinates
            title: Plot title
            labels: Axis labels as (u_label, v_label)
            color: Marker color (ignored if colormap is specified)
            alpha: Marker transparency
            marker: Marker style
            markersize: Marker size
            colormap: If provided, color points by sequence (e.g., 'viridis', 'plasma')
            show: Whether to display immediately

        Returns:
            Figure and axes objects
        """
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111)

        u, v = section_points[:, 0], section_points[:, 1]

        if colormap:
            # Color by sequence to show spiral structure
            colors = np.arange(len(section_points))
            scatter = self.ax.scatter(u, v, c=colors, cmap=colormap,
                                     alpha=alpha, s=markersize, marker=marker)
            plt.colorbar(scatter, ax=self.ax, label='Sequence')
        else:
            self.ax.scatter(u, v, color=color, alpha=alpha,
                           s=markersize, marker=marker)

        self.ax.set_xlabel(labels[0])
        self.ax.set_ylabel(labels[1])
        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)

        if show:
            plt.show()

        return self.fig, self.ax

    def plot_poincare_overlay_3d(
        self,
        trajectory: np.ndarray,
        section_points: np.ndarray,
        plane: str = 'z',
        plane_value: float = 0.0,
        title: str = "Poincaré Section Overlay",
        labels: Tuple[str, str, str] = ("X", "Y", "Z"),
        traj_color: str = 'blue',
        section_color: str = 'red',
        traj_alpha: float = 0.3,
        section_alpha: float = 0.8,
        show: bool = True
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot trajectory with Poincaré section plane and points overlaid in 3D.

        Args:
            trajectory: Full trajectory array of shape (n_points, 3)
            section_points: Poincaré section points of shape (n_section, 2)
            plane: Which plane to show ('x', 'y', or 'z')
            plane_value: The coordinate value of the section plane
            title: Plot title
            labels: Axis labels
            traj_color: Trajectory line color
            section_color: Section points color
            traj_alpha: Trajectory transparency
            section_alpha: Section points transparency
            show: Whether to display immediately

        Returns:
            Figure and axes objects
        """
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Plot trajectory
        x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]
        self.ax.plot(x, y, z, color=traj_color, alpha=traj_alpha, linewidth=0.5)

        # Reconstruct 3D section points
        if plane.lower() == 'x':
            section_3d_x = np.full(len(section_points), plane_value)
            section_3d_y = section_points[:, 0]
            section_3d_z = section_points[:, 1]
            # Draw plane
            yy, zz = np.meshgrid(
                np.linspace(y.min(), y.max(), 10),
                np.linspace(z.min(), z.max(), 10)
            )
            xx = np.full_like(yy, plane_value)
            self.ax.plot_surface(xx, yy, zz, alpha=0.2, color='gray')
        elif plane.lower() == 'y':
            section_3d_x = section_points[:, 0]
            section_3d_y = np.full(len(section_points), plane_value)
            section_3d_z = section_points[:, 1]
            # Draw plane
            xx, zz = np.meshgrid(
                np.linspace(x.min(), x.max(), 10),
                np.linspace(z.min(), z.max(), 10)
            )
            yy = np.full_like(xx, plane_value)
            self.ax.plot_surface(xx, yy, zz, alpha=0.2, color='gray')
        else:  # z plane
            section_3d_x = section_points[:, 0]
            section_3d_y = section_points[:, 1]
            section_3d_z = np.full(len(section_points), plane_value)
            # Draw plane
            xx, yy = np.meshgrid(
                np.linspace(x.min(), x.max(), 10),
                np.linspace(y.min(), y.max(), 10)
            )
            zz = np.full_like(xx, plane_value)
            self.ax.plot_surface(xx, yy, zz, alpha=0.2, color='gray')

        # Plot section points
        self.ax.scatter(section_3d_x, section_3d_y, section_3d_z,
                       color=section_color, alpha=section_alpha, s=20)

        self.ax.set_xlabel(labels[0])
        self.ax.set_ylabel(labels[1])
        self.ax.set_zlabel(labels[2])
        self.ax.set_title(title)

        if show:
            plt.show()

        return self.fig, self.ax

    def plot_bifurcation_diagram(
        self,
        bifurcation_data: Tuple[np.ndarray, np.ndarray],
        title: str = "Bifurcation Diagram",
        xlabel: str = "Parameter",
        ylabel: str = "Variable",
        color: str = 'black',
        alpha: float = 0.5,
        markersize: float = 0.5,
        show: bool = True
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot a bifurcation diagram showing how attractor behavior changes with parameter.

        Args:
            bifurcation_data: Tuple of (param_values, variable_values) arrays
            title: Plot title
            xlabel: Parameter axis label
            ylabel: Variable axis label
            color: Point color
            alpha: Point transparency
            markersize: Point size
            show: Whether to display immediately

        Returns:
            Figure and axes objects
        """
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111)

        param_values, var_values = bifurcation_data

        self.ax.plot(param_values, var_values, '.', color=color,
                    alpha=alpha, markersize=markersize)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)

        if show:
            plt.show()

        return self.fig, self.ax

    def animate_bifurcation(
        self,
        bifurcation_data: Tuple[np.ndarray, np.ndarray],
        title: str = "Bifurcation Animation",
        xlabel: str = "Parameter",
        ylabel: str = "Variable",
        color: str = 'black',
        frames: int = 100,
        interval: int = 100,
        save_path: Optional[str] = None
    ) -> animation.FuncAnimation:
        """
        Create an animation showing bifurcation diagram building up over time.

        Watch the period-doubling cascade emerge as the parameter increases!

        Args:
            bifurcation_data: Tuple of (param_values, variable_values) arrays
            title: Animation title
            xlabel: Parameter axis label
            ylabel: Variable axis label
            color: Point color
            frames: Number of animation frames
            interval: Delay between frames in milliseconds
            save_path: If provided, save animation to this path

        Returns:
            Animation object
        """
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111)

        param_values, var_values = bifurcation_data

        # Set fixed axis limits
        self.ax.set_xlim([param_values.min(), param_values.max()])
        self.ax.set_ylim([var_values.min(), var_values.max()])
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)

        line, = self.ax.plot([], [], '.', color=color, markersize=1)

        # Calculate how many points to show per frame
        points_per_frame = max(1, len(param_values) // frames)

        def init():
            line.set_data([], [])
            return line,

        def animate_frame(frame):
            end_idx = min((frame + 1) * points_per_frame, len(param_values))
            line.set_data(param_values[:end_idx], var_values[:end_idx])
            return line,

        anim = animation.FuncAnimation(
            self.fig, animate_frame, init_func=init,
            frames=frames, interval=interval, blit=True
        )

        if save_path:
            anim.save(save_path, writer='pillow')
            print(f"Bifurcation animation saved to {save_path}")

        return anim

    def plot_multiple_poincare_sections(
        self,
        sections_data: List[Tuple[np.ndarray, str]],
        title: str = "Poincaré Section Comparison",
        labels: Tuple[str, str] = ("u", "v"),
        colormap: str = 'viridis',
        show: bool = True
    ) -> Tuple[plt.Figure, List[plt.Axes]]:
        """
        Compare Poincaré sections from multiple attractors side-by-side.

        Args:
            sections_data: List of (section_points, name) tuples
            title: Overall figure title
            labels: Axis labels for sections
            colormap: Colormap for sequence coloring
            show: Whether to display immediately

        Returns:
            Figure and list of axes objects
        """
        n_sections = len(sections_data)

        # Create grid layout
        cols = min(3, n_sections)
        rows = (n_sections + cols - 1) // cols

        self.fig = plt.figure(figsize=self.figsize)
        self.fig.suptitle(title, fontsize=14)

        axes = []

        for i, (section_points, name) in enumerate(sections_data):
            ax = self.fig.add_subplot(rows, cols, i+1)

            u, v = section_points[:, 0], section_points[:, 1]
            colors = np.arange(len(section_points))
            scatter = ax.scatter(u, v, c=colors, cmap=colormap,
                               alpha=0.6, s=2, marker='.')

            ax.set_xlabel(labels[0])
            ax.set_ylabel(labels[1])
            ax.set_title(name)
            ax.grid(True, alpha=0.3)

            axes.append(ax)

        plt.tight_layout()

        if show:
            plt.show()

        return self.fig, axes

    def plot_return_map(
        self,
        return_map_data: dict,
        title: str = "Return Map",
        color: str = 'blue',
        alpha: float = 0.6,
        show_diagonal: bool = True,
        show_identity: bool = False,
        colormap: str = 'viridis',
        use_sequence_colors: bool = False,
        show: bool = True
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot a return map (x_n+1 vs x_n) from Poincaré section or time series.

        Return maps reveal structure in chaotic systems:
        - Fixed points: points on the diagonal
        - Periodic orbits: closed loops
        - Chaos: complex fractal-like curves

        Args:
            return_map_data: Dictionary from analysis.compute_return_map() with keys:
                            'x_n', 'x_n_plus_delay', 'dimension', 'delay', 'metadata'
            title: Plot title
            color: Point color (if not using sequence colors)
            alpha: Transparency
            show_diagonal: If True, show diagonal line (y=x) to identify fixed points
            show_identity: Alias for show_diagonal (for compatibility)
            colormap: Colormap to use if use_sequence_colors=True
            use_sequence_colors: If True, color points by sequence to show temporal evolution
            show: Whether to display the plot

        Returns:
            Figure and axes objects

        Example:
            >>> from rossler import RosslerAttractor
            >>> import analysis
            >>> rossler = RosslerAttractor()
            >>> trajectory = rossler.generate_trajectory(t_span=(0, 500), n_points=50000)
            >>> section = rossler.compute_poincare_section(trajectory, plane='z', plane_value=0.0)
            >>> return_map = analysis.compute_return_map(section, dimension=0, delay=1)
            >>> vis = AttractorVisualizer()
            >>> vis.plot_return_map(return_map, use_sequence_colors=True)
        """
        x_n = return_map_data['x_n']
        x_n_plus_delay = return_map_data['x_n_plus_delay']
        delay = return_map_data['delay']
        dimension = return_map_data['dimension']

        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111)

        if len(x_n) == 0:
            self.ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            self.ax.set_title(title)
            if show:
                plt.show()
            return self.fig, self.ax

        # Plot return map
        if use_sequence_colors:
            colors = np.arange(len(x_n))
            scatter = self.ax.scatter(x_n, x_n_plus_delay, c=colors, cmap=colormap,
                                     alpha=alpha, s=5, marker='.')
            plt.colorbar(scatter, ax=self.ax, label='Sequence')
        else:
            self.ax.scatter(x_n, x_n_plus_delay, color=color, alpha=alpha, s=5, marker='.')

        # Show diagonal line (x_{n+delay} = x_n) to identify fixed points
        if show_diagonal or show_identity:
            min_val = min(np.min(x_n), np.min(x_n_plus_delay))
            max_val = max(np.max(x_n), np.max(x_n_plus_delay))
            self.ax.plot([min_val, max_val], [min_val, max_val],
                        'r--', alpha=0.5, linewidth=1, label='Identity line (y=x)')
            self.ax.legend()

        self.ax.set_xlabel(f'$x_n$ (dimension {dimension})')
        self.ax.set_ylabel(f'$x_{{n+{delay}}}$ (dimension {dimension})')
        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if show:
            plt.show()

        return self.fig, self.ax

    def plot_divergence(
        self,
        divergence_array: np.ndarray,
        time_array: Optional[np.ndarray] = None,
        title: str = "Trajectory Divergence (Butterfly Effect)",
        log_scale: bool = False,
        fit_exponential: bool = False,
        color: str = 'blue',
        show: bool = True
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot divergence between two trajectories (quantifying the butterfly effect).

        Chaotic systems show exponential divergence of initially close trajectories.
        This plot quantifies that sensitivity to initial conditions.

        Args:
            divergence_array: Array of divergence values (distance over time)
            time_array: Optional time values. If None, uses index
            title: Plot title
            log_scale: If True, use log scale for y-axis to highlight exponential growth
            fit_exponential: If True, fit and overlay exponential curve
            color: Line color
            show: Whether to display the plot

        Returns:
            Figure and axes objects

        Example:
            >>> from lorenz import LorenzAttractor
            >>> import analysis
            >>> lorenz = LorenzAttractor()
            >>> traj1, traj2 = lorenz.generate_butterfly_effect_demo()
            >>> divergence = analysis.compute_divergence(traj1, traj2)
            >>> vis = AttractorVisualizer()
            >>> vis.plot_divergence(divergence, log_scale=True, fit_exponential=True)
        """
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111)

        if time_array is None:
            time_array = np.arange(len(divergence_array))

        # Plot divergence
        self.ax.plot(time_array, divergence_array, color=color, linewidth=1.5,
                    label='Divergence')

        # Fit exponential if requested
        if fit_exponential and len(divergence_array) > 10:
            # Fit to exponential: d(t) = d0 * exp(λt)
            # Use linear fit on log(d) for stability
            valid_mask = divergence_array > 0
            if np.sum(valid_mask) > 10:
                log_div = np.log(divergence_array[valid_mask])
                time_valid = time_array[valid_mask]

                # Linear fit on log scale
                coeffs = np.polyfit(time_valid, log_div, 1)
                growth_rate = coeffs[0]

                # Generate fit curve
                fit_curve = np.exp(coeffs[1]) * np.exp(growth_rate * time_array)
                self.ax.plot(time_array, fit_curve, 'r--', linewidth=1.5,
                           label=f'Exponential fit (λ≈{growth_rate:.3f})')

        if log_scale:
            self.ax.set_yscale('log')
            self.ax.set_ylabel('Divergence (log scale)')
        else:
            self.ax.set_ylabel('Divergence')

        self.ax.set_xlabel('Time')
        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()

        plt.tight_layout()

        if show:
            plt.show()

        return self.fig, self.ax

    def plot_lyapunov_convergence(
        self,
        lyapunov_result: dict,
        title: str = "Lyapunov Exponent Convergence",
        show_confidence: bool = True,
        color: str = 'blue',
        show: bool = True
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot convergence of Lyapunov exponent estimate.

        Shows how the estimate evolves and stabilizes, indicating
        whether the calculation has converged to a reliable value.

        Args:
            lyapunov_result: Dictionary from analysis.estimate_lyapunov_exponents()
                            with 'exponent', 'convergence_data', etc.
            title: Plot title
            show_confidence: If True and confidence interval available, shade it
            color: Line color
            show: Whether to display the plot

        Returns:
            Figure and axes objects

        Example:
            >>> from lorenz import LorenzAttractor
            >>> import analysis
            >>> lorenz = LorenzAttractor()
            >>> result = analysis.estimate_lyapunov_exponents(
            ...     lorenz, include_diagnostics=True
            ... )
            >>> vis = AttractorVisualizer()
            >>> vis.plot_lyapunov_convergence(result)
        """
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111)

        final_exponent = lyapunov_result['exponent']
        method = lyapunov_result.get('method', 'unknown')

        # Check if convergence data is available
        if 'convergence_data' in lyapunov_result and lyapunov_result['convergence_data']:
            conv_data = lyapunov_result['convergence_data']
            estimates = conv_data.get('estimates', np.array([]))

            if len(estimates) > 0:
                iterations = np.arange(len(estimates))

                # Plot convergence
                self.ax.plot(iterations, estimates, color=color, linewidth=1.5,
                           label='Running estimate')

                # Show final value
                self.ax.axhline(y=final_exponent, color='red', linestyle='--',
                              linewidth=1.5, alpha=0.7,
                              label=f'Final: λ₁={final_exponent:.4f}')

                # Show confidence interval if available
                if show_confidence and 'confidence_interval' in lyapunov_result:
                    ci_lower, ci_upper = lyapunov_result['confidence_interval']
                    self.ax.axhspan(ci_lower, ci_upper, alpha=0.2, color='green',
                                  label=f'95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]')

                self.ax.set_xlabel('Iteration')
                self.ax.set_ylabel('Lyapunov Exponent (λ₁)')

                # Add convergence status
                if conv_data.get('converged', False):
                    status = '✓ Converged'
                else:
                    status = '⚠ May not be fully converged'
                self.ax.text(0.02, 0.98, status, transform=self.ax.transAxes,
                           verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        else:
            # No convergence data - just show the final value
            self.ax.text(0.5, 0.5,
                        f'λ₁ = {final_exponent:.4f}\n(method: {method})\n\n'
                        'No convergence data available',
                        ha='center', va='center',
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)

        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='best')

        plt.tight_layout()

        if show:
            plt.show()

        return self.fig, self.ax

    def plot_phase_space_reconstruction(
        self,
        embedded_trajectory: np.ndarray,
        title: str = "Phase Space Reconstruction (Takens Embedding)",
        color: str = 'blue',
        alpha: float = 0.7,
        linewidth: float = 0.5,
        show: bool = True
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Visualize reconstructed attractor from time delay embedding.

        Demonstrates Takens' theorem: a full attractor can be reconstructed
        from a single observable using time-delay embedding.

        Args:
            embedded_trajectory: Array of shape (n_points, embedding_dim)
                                from analysis.compute_time_delay_embedding()
            title: Plot title
            color: Line/point color
            alpha: Transparency
            linewidth: Line width for 3D plots
            show: Whether to display the plot

        Returns:
            Figure and axes objects

        Example:
            >>> from lorenz import LorenzAttractor
            >>> import analysis
            >>> lorenz = LorenzAttractor()
            >>> trajectory = lorenz.generate_trajectory(t_span=(0, 100), n_points=10000)
            >>> # Extract just x-coordinate (1D time series)
            >>> x_series = trajectory[:, 0]
            >>> # Reconstruct full attractor from x alone!
            >>> embedded = analysis.compute_time_delay_embedding(x_series, delay=10, embedding_dim=3)
            >>> vis = AttractorVisualizer()
            >>> vis.plot_phase_space_reconstruction(embedded)
        """
        embedding_dim = embedded_trajectory.shape[1]

        if embedding_dim == 3:
            # 3D visualization
            self.fig = plt.figure(figsize=self.figsize)
            self.ax = self.fig.add_subplot(111, projection='3d')

            x, y, z = embedded_trajectory[:, 0], embedded_trajectory[:, 1], embedded_trajectory[:, 2]
            self.ax.plot(x, y, z, color=color, alpha=alpha, linewidth=linewidth)

            self.ax.set_xlabel('x(t)')
            self.ax.set_ylabel('x(t+τ)')
            self.ax.set_zlabel('x(t+2τ)')
            self.ax.set_title(title)

        elif embedding_dim == 2:
            # 2D visualization
            self.fig = plt.figure(figsize=self.figsize)
            self.ax = self.fig.add_subplot(111)

            x, y = embedded_trajectory[:, 0], embedded_trajectory[:, 1]
            self.ax.plot(x, y, color=color, alpha=alpha, linewidth=linewidth)

            self.ax.set_xlabel('x(t)')
            self.ax.set_ylabel('x(t+τ)')
            self.ax.set_title(title)
            self.ax.grid(True, alpha=0.3)

        else:
            # For higher dimensions, show projection to first 3 dims
            self.fig = plt.figure(figsize=self.figsize)
            self.ax = self.fig.add_subplot(111, projection='3d')

            x, y, z = embedded_trajectory[:, 0], embedded_trajectory[:, 1], embedded_trajectory[:, 2]
            self.ax.plot(x, y, z, color=color, alpha=alpha, linewidth=linewidth)

            self.ax.set_xlabel('Dimension 1')
            self.ax.set_ylabel('Dimension 2')
            self.ax.set_zlabel('Dimension 3')
            self.ax.set_title(f"{title}\n(showing first 3 of {embedding_dim} dimensions)")

        plt.tight_layout()

        if show:
            plt.show()

        return self.fig, self.ax

    def plot_analysis_summary(
        self,
        attractor,
        trajectory: np.ndarray,
        section_data: Optional[np.ndarray] = None,
        return_map_data: Optional[dict] = None,
        lyapunov_result: Optional[dict] = None,
        title: Optional[str] = None,
        show: bool = True
    ) -> Tuple[plt.Figure, List[plt.Axes]]:
        """
        Create a comprehensive 4-panel analysis summary figure.

        Combines:
        - 3D trajectory (top left)
        - Poincaré section (top right)
        - Return map (bottom left)
        - Lyapunov convergence (bottom right)

        This creates publication-ready multi-panel figures.

        Args:
            attractor: AttractorBase instance
            trajectory: 3D trajectory array
            section_data: Poincaré section points (optional)
            return_map_data: Return map dict (optional)
            lyapunov_result: Lyapunov exponent result dict (optional)
            title: Overall figure title. If None, auto-generated from attractor info
            show: Whether to display the plot

        Returns:
            Figure and list of axes objects

        Example:
            >>> from lorenz import LorenzAttractor
            >>> import analysis
            >>> lorenz = LorenzAttractor()
            >>> trajectory = lorenz.generate_trajectory(t_span=(0, 100), n_points=10000)
            >>> section = lorenz.compute_poincare_section(trajectory, plane='z', plane_value=27)
            >>> return_map = analysis.compute_return_map(section)
            >>> lyapunov = analysis.estimate_lyapunov_exponents(lorenz, include_diagnostics=True)
            >>> vis = AttractorVisualizer()
            >>> vis.plot_analysis_summary(lorenz, trajectory, section, return_map, lyapunov)
        """
        self.fig = plt.figure(figsize=(16, 12))

        # Generate title if not provided
        if title is None:
            info = attractor.get_info()
            attractor_type = info.get('type', 'Unknown')
            params = info.get('parameters', {})
            param_str = ', '.join([f'{k}={v:.2f}' for k, v in list(params.items())[:3]])
            title = f"{attractor_type} Attractor Analysis\n({param_str})"

        self.fig.suptitle(title, fontsize=16, fontweight='bold')

        axes = []

        # Top left: 3D trajectory
        ax1 = self.fig.add_subplot(2, 2, 1, projection='3d')
        x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]
        ax1.plot(x, y, z, color='blue', alpha=0.6, linewidth=0.5)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax1.set_title('3D Trajectory')
        axes.append(ax1)

        # Top right: Poincaré section
        ax2 = self.fig.add_subplot(2, 2, 2)
        if section_data is not None and len(section_data) > 0:
            colors = np.arange(len(section_data))
            scatter = ax2.scatter(section_data[:, 0], section_data[:, 1],
                                c=colors, cmap='viridis', alpha=0.6, s=2)
            ax2.set_xlabel('U')
            ax2.set_ylabel('V')
            ax2.set_title('Poincaré Section')
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'Poincaré section\nnot provided',
                    ha='center', va='center')
            ax2.set_title('Poincaré Section')
        axes.append(ax2)

        # Bottom left: Return map
        ax3 = self.fig.add_subplot(2, 2, 3)
        if return_map_data is not None:
            x_n = return_map_data['x_n']
            x_n_plus_delay = return_map_data['x_n_plus_delay']
            if len(x_n) > 0:
                ax3.scatter(x_n, x_n_plus_delay, color='green', alpha=0.6, s=5)
                # Add diagonal
                min_val = min(np.min(x_n), np.min(x_n_plus_delay))
                max_val = max(np.max(x_n), np.max(x_n_plus_delay))
                ax3.plot([min_val, max_val], [min_val, max_val],
                        'r--', alpha=0.5, linewidth=1)
                ax3.set_xlabel('$x_n$')
                ax3.set_ylabel('$x_{n+1}$')
                ax3.set_title('Return Map')
                ax3.grid(True, alpha=0.3)
            else:
                ax3.text(0.5, 0.5, 'Return map\ndata empty',
                        ha='center', va='center')
                ax3.set_title('Return Map')
        else:
            ax3.text(0.5, 0.5, 'Return map\nnot provided',
                    ha='center', va='center')
            ax3.set_title('Return Map')
        axes.append(ax3)

        # Bottom right: Lyapunov convergence
        ax4 = self.fig.add_subplot(2, 2, 4)
        if lyapunov_result is not None:
            final_exp = lyapunov_result['exponent']

            if 'convergence_data' in lyapunov_result and lyapunov_result['convergence_data']:
                estimates = lyapunov_result['convergence_data'].get('estimates', np.array([]))
                if len(estimates) > 0:
                    iterations = np.arange(len(estimates))
                    ax4.plot(iterations, estimates, color='blue', linewidth=1.5)
                    ax4.axhline(y=final_exp, color='red', linestyle='--',
                              linewidth=1.5, alpha=0.7)
                    ax4.set_xlabel('Iteration')
                    ax4.set_ylabel('λ₁')
                    ax4.set_title(f'Lyapunov Exponent: λ₁={final_exp:.4f}')
                    ax4.grid(True, alpha=0.3)
                else:
                    ax4.text(0.5, 0.5, f'λ₁ = {final_exp:.4f}',
                            ha='center', va='center', fontsize=14)
                    ax4.set_title('Lyapunov Exponent')
            else:
                ax4.text(0.5, 0.5, f'λ₁ = {final_exp:.4f}',
                        ha='center', va='center', fontsize=14)
                ax4.set_title('Lyapunov Exponent')
        else:
            ax4.text(0.5, 0.5, 'Lyapunov exponent\nnot computed',
                    ha='center', va='center')
            ax4.set_title('Lyapunov Exponent')
        axes.append(ax4)

        plt.tight_layout()

        if show:
            plt.show()

        return self.fig, axes


def compare_attractors(
    attractors_data: List[Tuple[np.ndarray, str]],
    figsize: Tuple[int, int] = (15, 10)
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """
    Create a comparison visualization of multiple different attractors.

    Args:
        attractors_data: List of (trajectory, name) tuples
        figsize: Figure size

    Returns:
        Figure and list of axes objects
    """
    n_attractors = len(attractors_data)

    # Create a grid layout
    cols = min(3, n_attractors)
    rows = (n_attractors + cols - 1) // cols

    fig = plt.figure(figsize=figsize)
    axes = []

    colors = plt.cm.viridis(np.linspace(0, 1, n_attractors))

    for i, (trajectory, name) in enumerate(attractors_data):
        ax = fig.add_subplot(rows, cols, i+1, projection='3d')

        x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]
        ax.plot(x, y, z, color=colors[i], alpha=0.7, linewidth=0.5)
        ax.set_title(name)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        axes.append(ax)

    plt.tight_layout()
    return fig, axes
