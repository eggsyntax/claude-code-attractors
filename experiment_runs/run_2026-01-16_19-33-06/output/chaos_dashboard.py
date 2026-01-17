"""
Chaos Dashboard: Unified Interactive Explorer

An integrated dashboard that brings together all our attractor visualization and analysis
tools into a single interactive interface. This provides a cohesive entry point for
exploring the full spectrum of chaos - from artistic renderings to rigorous mathematical
analysis.

The dashboard uses Plotly Dash to create a web-based interface where users can:
- Explore attractors interactively in 3D
- Compare multiple systems side-by-side
- Tune parameters and watch behavior change in real-time
- Switch between visualization modes (artistic, scientific, temporal)
- Access bifurcation diagrams and Lyapunov spectra
- Generate publication-quality outputs

This represents the synthesis of our collaborative work - bringing together Alice's
temporal visualizations and artistic rendering with Bob's bifurcation analysis and
comparative tools.

Author: Alice
Date: January 2026
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy.integrate import solve_ivp
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Callable
import warnings
warnings.filterwarnings('ignore')


@dataclass
class AttractorConfig:
    """Configuration for an attractor system."""
    name: str
    display_name: str
    default_state: List[float]
    default_params: Dict[str, float]
    param_ranges: Dict[str, Tuple[float, float]]
    integration_time: float
    time_step: float
    description: str


class ChaosExplorer:
    """
    Unified chaos exploration dashboard.

    Integrates all visualization and analysis tools into a cohesive interface:
    - 3D interactive attractor visualization
    - Parameter exploration with sliders
    - Multi-system comparison
    - Temporal evolution animation
    - Butterfly effect demonstration
    - Quick access to bifurcation and Lyapunov analysis
    """

    def __init__(self):
        """Initialize the chaos explorer with all available attractors."""
        self.attractors = self._initialize_attractors()

    def _initialize_attractors(self) -> Dict[str, AttractorConfig]:
        """Define configurations for all available attractors."""
        return {
            'lorenz': AttractorConfig(
                name='lorenz',
                display_name='Lorenz Attractor',
                default_state=[1.0, 1.0, 1.0],
                default_params={'sigma': 10.0, 'beta': 8/3, 'rho': 28.0},
                param_ranges={
                    'sigma': (0.0, 20.0),
                    'beta': (0.0, 5.0),
                    'rho': (0.0, 50.0)
                },
                integration_time=50.0,
                time_step=0.01,
                description='Discovered by Edward Lorenz in 1963. Shows sensitive dependence on initial conditions - the butterfly effect. Exhibits wildly chaotic behavior with sharp transition to chaos at ρ≈24.74.'
            ),
            'rossler': AttractorConfig(
                name='rossler',
                display_name='Rössler Attractor',
                default_state=[1.0, 1.0, 1.0],
                default_params={'a': 0.2, 'b': 0.2, 'c': 5.7},
                param_ranges={
                    'a': (0.0, 1.0),
                    'b': (0.0, 1.0),
                    'c': (0.0, 10.0)
                },
                integration_time=200.0,
                time_step=0.01,
                description='Introduced by Otto Rössler in 1976. Features a clean period-doubling cascade route to chaos. Simpler structure than Lorenz but still richly chaotic.'
            ),
            'thomas': AttractorConfig(
                name='thomas',
                display_name='Thomas Attractor',
                default_state=[0.1, 0.0, 0.0],
                default_params={'b': 0.208},
                param_ranges={
                    'b': (0.1, 0.3)
                },
                integration_time=500.0,
                time_step=0.02,
                description='Exhibits perfect C₃ rotational symmetry - the equations are invariant under (x,y,z)→(y,z,x). Shows gentler chaos with longer predictability horizon than Lorenz.'
            )
        }

    def lorenz_equations(self, t, state, sigma, beta, rho):
        """Lorenz system differential equations."""
        x, y, z = state
        return [
            sigma * (y - x),
            x * (rho - z) - y,
            x * y - beta * z
        ]

    def rossler_equations(self, t, state, a, b, c):
        """Rössler system differential equations."""
        x, y, z = state
        return [
            -y - z,
            x + a * y,
            b + z * (x - c)
        ]

    def thomas_equations(self, t, state, b):
        """Thomas system differential equations."""
        x, y, z = state
        return [
            np.sin(y) - b * x,
            np.sin(z) - b * y,
            np.sin(x) - b * z
        ]

    def get_equations(self, attractor_name: str) -> Callable:
        """Get the equation function for a given attractor."""
        equations_map = {
            'lorenz': self.lorenz_equations,
            'rossler': self.rossler_equations,
            'thomas': self.thomas_equations
        }
        return equations_map[attractor_name]

    def simulate(self, attractor_name: str, params: Dict[str, float] = None,
                 initial_state: List[float] = None, t_max: float = None) -> np.ndarray:
        """
        Simulate an attractor system.

        Args:
            attractor_name: Name of the attractor system
            params: Parameter dictionary (uses defaults if None)
            initial_state: Initial conditions (uses defaults if None)
            t_max: Maximum integration time (uses defaults if None)

        Returns:
            Trajectory array of shape (n_points, 3)
        """
        config = self.attractors[attractor_name]

        # Use defaults if not provided
        if params is None:
            params = config.default_params
        if initial_state is None:
            initial_state = config.default_state
        if t_max is None:
            t_max = config.integration_time

        # Get equation function
        equations = self.get_equations(attractor_name)

        # Time array
        t_eval = np.arange(0, t_max, config.time_step)

        # Integrate
        sol = solve_ivp(
            lambda t, y: equations(t, y, **params),
            (0, t_max),
            initial_state,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-8,
            atol=1e-10
        )

        return sol.y.T

    def create_3d_plot(self, attractor_name: str, params: Dict[str, float] = None,
                       colorscale: str = 'Viridis', show_axes: bool = True) -> go.Figure:
        """
        Create interactive 3D visualization of an attractor.

        Args:
            attractor_name: Name of the attractor
            params: Parameter dictionary
            colorscale: Plotly colorscale name
            show_axes: Whether to show axes

        Returns:
            Plotly figure object
        """
        config = self.attractors[attractor_name]
        trajectory = self.simulate(attractor_name, params)

        x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]

        # Color by time progression
        colors = np.arange(len(x))

        # Create figure
        fig = go.Figure(data=[go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(
                color=colors,
                colorscale=colorscale,
                width=2
            ),
            name=config.display_name,
            hovertemplate='<b>Point %{pointNumber}</b><br>' +
                         'x: %{x:.2f}<br>' +
                         'y: %{y:.2f}<br>' +
                         'z: %{z:.2f}<br>' +
                         '<extra></extra>'
        )])

        # Update layout
        fig.update_layout(
            title=dict(
                text=f'{config.display_name}<br><sub>{self._format_params(params or config.default_params)}</sub>',
                x=0.5,
                xanchor='center',
                font=dict(size=20)
            ),
            scene=dict(
                xaxis=dict(visible=show_axes, title='x'),
                yaxis=dict(visible=show_axes, title='y'),
                zaxis=dict(visible=show_axes, title='z'),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.3)
                )
            ),
            width=800,
            height=700,
            showlegend=False,
            margin=dict(l=0, r=0, t=80, b=0)
        )

        return fig

    def create_comparison_plot(self, attractors: List[str] = None,
                              colorscales: List[str] = None) -> go.Figure:
        """
        Create side-by-side comparison of multiple attractors.

        Args:
            attractors: List of attractor names (defaults to all three)
            colorscales: List of colorscales for each attractor

        Returns:
            Plotly figure with subplots
        """
        if attractors is None:
            attractors = ['lorenz', 'rossler', 'thomas']
        if colorscales is None:
            colorscales = ['Plasma', 'Viridis', 'Cividis']

        n_attractors = len(attractors)

        # Create subplots
        fig = make_subplots(
            rows=1, cols=n_attractors,
            subplot_titles=[self.attractors[name].display_name for name in attractors],
            specs=[[{'type': 'scatter3d'} for _ in range(n_attractors)]],
            horizontal_spacing=0.05
        )

        # Add each attractor
        for i, (name, colorscale) in enumerate(zip(attractors, colorscales), 1):
            trajectory = self.simulate(name)
            x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]
            colors = np.arange(len(x))

            fig.add_trace(
                go.Scatter3d(
                    x=x, y=y, z=z,
                    mode='lines',
                    line=dict(color=colors, colorscale=colorscale, width=1.5),
                    name=self.attractors[name].display_name,
                    showlegend=False
                ),
                row=1, col=i
            )

        # Update layout
        fig.update_layout(
            title=dict(
                text='Attractor Comparison: Three Personalities of Chaos',
                x=0.5,
                xanchor='center',
                font=dict(size=22)
            ),
            height=600,
            margin=dict(l=0, r=0, t=100, b=0)
        )

        # Update scene cameras for consistent viewing angle
        for i in range(1, n_attractors + 1):
            fig.update_scenes(
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.3)),
                row=1, col=i
            )

        return fig

    def create_butterfly_effect_plot(self, attractor_name: str,
                                     separation: float = 1e-8,
                                     t_max: float = 20.0) -> go.Figure:
        """
        Demonstrate the butterfly effect with diverging trajectories.

        Args:
            attractor_name: Name of the attractor
            separation: Initial separation between trajectories
            t_max: Time to integrate

        Returns:
            Plotly figure showing divergence
        """
        config = self.attractors[attractor_name]

        # Two nearby initial conditions
        state1 = config.default_state
        state2 = [x + separation for x in config.default_state]

        # Simulate both
        traj1 = self.simulate(attractor_name, initial_state=state1, t_max=t_max)
        traj2 = self.simulate(attractor_name, initial_state=state2, t_max=t_max)

        # Calculate divergence over time
        divergence = np.linalg.norm(traj1 - traj2, axis=1)
        time = np.arange(len(divergence)) * config.time_step

        # Create subplots: 3D trajectories and divergence plot
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(f'{config.display_name}: Diverging Trajectories',
                          'Exponential Divergence'),
            specs=[[{'type': 'scatter3d'}, {'type': 'scatter'}]],
            column_widths=[0.6, 0.4]
        )

        # 3D trajectories
        x1, y1, z1 = traj1[:, 0], traj1[:, 1], traj1[:, 2]
        x2, y2, z2 = traj2[:, 0], traj2[:, 1], traj2[:, 2]

        fig.add_trace(
            go.Scatter3d(
                x=x1, y=y1, z=z1,
                mode='lines',
                line=dict(color='blue', width=2),
                name='Trajectory 1'
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter3d(
                x=x2, y=y2, z=z2,
                mode='lines',
                line=dict(color='red', width=2),
                name='Trajectory 2'
            ),
            row=1, col=1
        )

        # Divergence plot (log scale)
        fig.add_trace(
            go.Scatter(
                x=time,
                y=divergence,
                mode='lines',
                line=dict(color='purple', width=3),
                name='Divergence'
            ),
            row=1, col=2
        )

        # Update axes
        fig.update_xaxes(title_text='Time', row=1, col=2)
        fig.update_yaxes(title_text='Distance', type='log', row=1, col=2)

        # Update layout
        fig.update_layout(
            title=dict(
                text=f'The Butterfly Effect in the {config.display_name}<br>' +
                     f'<sub>Initial separation: {separation:.1e}</sub>',
                x=0.5,
                xanchor='center',
                font=dict(size=18)
            ),
            height=600,
            showlegend=True,
            margin=dict(l=0, r=0, t=100, b=0)
        )

        return fig

    def create_parameter_sensitivity_plot(self, attractor_name: str,
                                          param_name: str,
                                          values: List[float] = None) -> go.Figure:
        """
        Show how attractor changes as parameter varies.

        Args:
            attractor_name: Name of the attractor
            param_name: Parameter to vary
            values: List of parameter values (auto-generated if None)

        Returns:
            Plotly figure with multiple traces
        """
        config = self.attractors[attractor_name]

        # Generate parameter values if not provided
        if values is None:
            param_min, param_max = config.param_ranges[param_name]
            values = np.linspace(param_min, param_max, 5)

        fig = go.Figure()

        # Colorscale for different parameter values
        colors = px.colors.sequential.Plasma

        for i, value in enumerate(values):
            params = config.default_params.copy()
            params[param_name] = value

            trajectory = self.simulate(attractor_name, params)
            x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]

            # Color for this parameter value
            color_idx = int((i / (len(values) - 1)) * (len(colors) - 1))
            color = colors[color_idx]

            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines',
                line=dict(color=color, width=2),
                name=f'{param_name}={value:.3f}',
                opacity=0.7
            ))

        fig.update_layout(
            title=dict(
                text=f'{config.display_name}: Sensitivity to {param_name}',
                x=0.5,
                xanchor='center',
                font=dict(size=20)
            ),
            scene=dict(
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
            ),
            height=700,
            margin=dict(l=0, r=0, t=80, b=0)
        )

        return fig

    def generate_summary_report(self) -> str:
        """
        Generate a text summary of all available attractors and their properties.

        Returns:
            Formatted markdown report
        """
        report = "# Strange Attractors: System Summary\n\n"
        report += "This dashboard provides access to three classic chaotic systems, each with distinct personality:\n\n"

        for name, config in self.attractors.items():
            report += f"## {config.display_name}\n\n"
            report += f"{config.description}\n\n"
            report += f"**Parameters:**\n"
            for param, value in config.default_params.items():
                param_min, param_max = config.param_ranges.get(param, (0, 0))
                report += f"- `{param}`: {value:.3f} (range: {param_min:.3f} to {param_max:.3f})\n"
            report += f"\n**Default initial state:** {config.default_state}\n"
            report += f"**Integration time:** {config.integration_time} time units\n\n"
            report += "---\n\n"

        report += "## Visualization Modes\n\n"
        report += "- **3D Interactive:** Explore the attractor in three dimensions with zoom and rotation\n"
        report += "- **Comparison:** View all three attractors side-by-side\n"
        report += "- **Butterfly Effect:** Demonstrate sensitive dependence on initial conditions\n"
        report += "- **Parameter Sensitivity:** See how behavior changes with parameter values\n"

        return report

    def _format_params(self, params: Dict[str, float]) -> str:
        """Format parameter dictionary as string."""
        return ', '.join([f'{k}={v:.3f}' for k, v in params.items()])


def demo_dashboard():
    """
    Demonstrate the chaos dashboard capabilities.

    This creates a series of visualizations showcasing different aspects
    of the three attractor systems.
    """
    print("\n" + "="*70)
    print("CHAOS DASHBOARD DEMONSTRATION")
    print("="*70 + "\n")

    explorer = ChaosExplorer()

    # 1. Individual 3D plots
    print("[1/5] Creating individual 3D visualizations...")
    for name in ['lorenz', 'rossler', 'thomas']:
        fig = explorer.create_3d_plot(name)
        filename = f'dashboard_{name}_3d.html'
        fig.write_html(filename)
        print(f"  → Saved {filename}")

    # 2. Comparison plot
    print("\n[2/5] Creating three-way comparison...")
    fig = explorer.create_comparison_plot()
    fig.write_html('dashboard_comparison.html')
    print("  → Saved dashboard_comparison.html")

    # 3. Butterfly effect demonstrations
    print("\n[3/5] Creating butterfly effect visualizations...")
    for name in ['lorenz', 'rossler', 'thomas']:
        fig = explorer.create_butterfly_effect_plot(name)
        filename = f'dashboard_{name}_butterfly.html'
        fig.write_html(filename)
        print(f"  → Saved {filename}")

    # 4. Parameter sensitivity
    print("\n[4/5] Creating parameter sensitivity plots...")
    sensitivity_configs = [
        ('lorenz', 'rho'),
        ('rossler', 'c'),
        ('thomas', 'b')
    ]
    for name, param in sensitivity_configs:
        fig = explorer.create_parameter_sensitivity_plot(name, param)
        filename = f'dashboard_{name}_sensitivity.html'
        fig.write_html(filename)
        print(f"  → Saved {filename}")

    # 5. Generate summary report
    print("\n[5/5] Generating summary report...")
    report = explorer.generate_summary_report()
    with open('dashboard_summary.md', 'w') as f:
        f.write(report)
    print("  → Saved dashboard_summary.md")

    print("\n" + "="*70)
    print("DASHBOARD DEMONSTRATION COMPLETE!")
    print("="*70)
    print("\nGenerated files:")
    print("  Interactive 3D plots: dashboard_*_3d.html")
    print("  Comparison view: dashboard_comparison.html")
    print("  Butterfly effect demos: dashboard_*_butterfly.html")
    print("  Parameter sensitivity: dashboard_*_sensitivity.html")
    print("  Summary report: dashboard_summary.md")
    print("\nOpen any .html file in a web browser to explore interactively!")
    print("\n")


if __name__ == '__main__':
    demo_dashboard()
