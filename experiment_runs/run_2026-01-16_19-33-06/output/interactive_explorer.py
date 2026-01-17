"""
Interactive Attractor Explorer

This script creates an interactive web-based visualization where you can
adjust parameters in real-time and watch how the attractor morphs.

Usage:
    python interactive_explorer.py

This will open a browser window with interactive controls for exploring
the Lorenz and Rössler attractors.
"""

import numpy as np
from attractors import LorenzAttractor, RosslerAttractor
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


def create_lorenz_explorer():
    """
    Create an interactive Lorenz attractor explorer

    Returns:
        Plotly figure with parameter sliders
    """
    # Default parameters
    sigma_default = 10.0
    rho_default = 28.0
    beta_default = 8/3

    # Create figure
    fig = go.Figure()

    # Generate trajectories for different parameter values to create frames
    # We'll create a slider for rho (most visually dramatic)
    rho_values = np.linspace(10, 40, 31)  # 31 frames from rho=10 to rho=40

    for i, rho in enumerate(rho_values):
        lorenz = LorenzAttractor(sigma=sigma_default, rho=rho, beta=beta_default)
        trajectory = lorenz.simulate(duration=30.0, dt=0.01)

        # Color by time progression
        colors = np.arange(len(trajectory))

        # Add trace for this frame
        visible = (i == 20)  # Make rho=28 visible by default (index 20)

        fig.add_trace(go.Scatter3d(
            x=trajectory[:, 0],
            y=trajectory[:, 1],
            z=trajectory[:, 2],
            mode='lines',
            line=dict(
                color=colors,
                colorscale='Viridis',
                width=2
            ),
            name=f'ρ={rho:.1f}',
            visible=visible
        ))

    # Create slider steps
    steps = []
    for i, rho in enumerate(rho_values):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)}],
            label=f"{rho:.1f}"
        )
        step["args"][0]["visible"][i] = True
        steps.append(step)

    sliders = [dict(
        active=20,  # Start at rho=28
        currentvalue={"prefix": "Rayleigh number (ρ): "},
        pad={"t": 50},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders,
        title=dict(
            text="Lorenz Attractor - Explore the Rayleigh Number (ρ)<br>" +
                 "<sub>σ=10.0, β=2.667 | Drag to rotate, scroll to zoom</sub>",
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            ),
            bgcolor='rgb(240, 240, 245)'
        ),
        width=1000,
        height=800,
        showlegend=False
    )

    return fig


def create_rossler_explorer():
    """
    Create an interactive Rössler attractor explorer

    Returns:
        Plotly figure with parameter sliders
    """
    # Default parameters
    a_default = 0.2
    b_default = 0.2

    # Create figure
    fig = go.Figure()

    # Vary parameter c (most visually interesting)
    c_values = np.linspace(2.0, 10.0, 41)  # 41 frames from c=2 to c=10

    for i, c in enumerate(c_values):
        rossler = RosslerAttractor(a=a_default, b=b_default, c=c)
        trajectory = rossler.simulate(duration=200.0, dt=0.05)

        # Color by time progression
        colors = np.arange(len(trajectory))

        # Add trace for this frame
        visible = (i == 19)  # Make c=5.7 visible by default (approximately index 19)

        fig.add_trace(go.Scatter3d(
            x=trajectory[:, 0],
            y=trajectory[:, 1],
            z=trajectory[:, 2],
            mode='lines',
            line=dict(
                color=colors,
                colorscale='Plasma',
                width=2
            ),
            name=f'c={c:.1f}',
            visible=visible
        ))

    # Create slider steps
    steps = []
    for i, c in enumerate(c_values):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)}],
            label=f"{c:.1f}"
        )
        step["args"][0]["visible"][i] = True
        steps.append(step)

    sliders = [dict(
        active=19,  # Start at c≈5.7
        currentvalue={"prefix": "Parameter c: "},
        pad={"t": 50},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders,
        title=dict(
            text="Rössler Attractor - Explore Parameter c<br>" +
                 "<sub>a=0.2, b=0.2 | Drag to rotate, scroll to zoom</sub>",
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            ),
            bgcolor='rgb(245, 240, 240)'
        ),
        width=1000,
        height=800,
        showlegend=False
    )

    return fig


def create_comparison_view():
    """
    Create a side-by-side comparison of Lorenz and Rössler attractors

    Returns:
        Plotly figure with both attractors
    """
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Lorenz Attractor', 'Rössler Attractor'),
        specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}]]
    )

    # Generate Lorenz
    lorenz = LorenzAttractor()
    lorenz_traj = lorenz.simulate(duration=30.0, dt=0.01)
    colors_l = np.arange(len(lorenz_traj))

    fig.add_trace(
        go.Scatter3d(
            x=lorenz_traj[:, 0],
            y=lorenz_traj[:, 1],
            z=lorenz_traj[:, 2],
            mode='lines',
            line=dict(color=colors_l, colorscale='Viridis', width=2),
            name='Lorenz'
        ),
        row=1, col=1
    )

    # Generate Rössler
    rossler = RosslerAttractor()
    rossler_traj = rossler.simulate(duration=100.0, dt=0.05)
    colors_r = np.arange(len(rossler_traj))

    fig.add_trace(
        go.Scatter3d(
            x=rossler_traj[:, 0],
            y=rossler_traj[:, 1],
            z=rossler_traj[:, 2],
            mode='lines',
            line=dict(color=colors_r, colorscale='Plasma', width=2),
            name='Rössler'
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="Classic Strange Attractors: Side by Side",
        width=1600,
        height=700,
        showlegend=False
    )

    return fig


if __name__ == "__main__":
    print("Creating interactive visualizations...")
    print("\n" + "="*60)

    # Create Lorenz explorer
    print("\n1. Lorenz Attractor Explorer")
    print("   Adjust the Rayleigh number (ρ) to see how the attractor changes")
    print("   Notice the transition from simple attractors to the butterfly shape")
    lorenz_fig = create_lorenz_explorer()
    lorenz_fig.write_html('/tmp/claude-attractors/run_2026-01-16_19-33-06/output/lorenz_explorer.html')
    print("   → Saved to: lorenz_explorer.html")

    # Create Rössler explorer
    print("\n2. Rössler Attractor Explorer")
    print("   Adjust parameter c to see transitions in the attractor topology")
    rossler_fig = create_rossler_explorer()
    rossler_fig.write_html('/tmp/claude-attractors/run_2026-01-16_19-33-06/output/rossler_explorer.html')
    print("   → Saved to: rossler_explorer.html")

    # Create comparison view
    print("\n3. Side-by-Side Comparison")
    print("   Compare Lorenz and Rössler at their classic parameter values")
    comparison_fig = create_comparison_view()
    comparison_fig.write_html('/tmp/claude-attractors/run_2026-01-16_19-33-06/output/comparison.html')
    print("   → Saved to: comparison.html")

    print("\n" + "="*60)
    print("\nAll visualizations generated successfully!")
    print("Open the HTML files in your browser to explore interactively.")
    print("\nTip: In the 3D views, you can:")
    print("  • Drag to rotate")
    print("  • Scroll to zoom")
    print("  • Use the slider to change parameters")
