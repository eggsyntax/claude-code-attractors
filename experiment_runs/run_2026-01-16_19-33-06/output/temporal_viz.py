"""
Temporal Visualization of Strange Attractors

This module provides tools to visualize how trajectories evolve through time,
showing both the drawing of the trajectory and the butterfly effect - how
nearby initial conditions diverge exponentially.

Usage:
    python temporal_viz.py

This will generate animated visualizations showing:
1. A trajectory being drawn through phase space over time
2. Multiple trajectories from nearby initial conditions diverging
"""

import numpy as np
from attractors import LorenzAttractor, RosslerAttractor
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_drawing_animation(attractor, duration=50.0, dt=0.01,
                             frames_to_show=200, title="Trajectory Evolution"):
    """
    Create an animation showing a trajectory being drawn through phase space.

    This visualization emphasizes the temporal nature of the system - you see
    the point moving through space, leaving a trail behind it.

    Args:
        attractor: An Attractor instance (e.g., LorenzAttractor)
        duration: Total simulation time
        dt: Time step for simulation
        frames_to_show: Number of animation frames (more = smoother but larger file)
        title: Animation title

    Returns:
        Plotly figure with animation
    """
    # Simulate the full trajectory
    trajectory = attractor.simulate(duration=duration, dt=dt)
    n_points = len(trajectory)

    # Determine how many points to show per frame
    points_per_frame = max(1, n_points // frames_to_show)

    # Create figure
    fig = go.Figure()

    # Create frames showing progressive amounts of the trajectory
    frames = []
    for i in range(0, n_points, points_per_frame):
        # Current segment of trajectory
        segment = trajectory[:i+1]

        # Color points by time (fading effect)
        colors = np.arange(len(segment))

        frame = go.Frame(
            data=[
                # The trail
                go.Scatter3d(
                    x=segment[:, 0],
                    y=segment[:, 1],
                    z=segment[:, 2],
                    mode='lines',
                    line=dict(
                        color=colors,
                        colorscale='Viridis',
                        width=2
                    ),
                    name='Trajectory'
                ),
                # The current point (emphasized)
                go.Scatter3d(
                    x=[segment[-1, 0]],
                    y=[segment[-1, 1]],
                    z=[segment[-1, 2]],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color='red',
                        symbol='circle'
                    ),
                    name='Current Position'
                )
            ],
            name=str(i)
        )
        frames.append(frame)

    # Initialize with first frame
    fig.add_trace(go.Scatter3d(
        x=trajectory[0:1, 0],
        y=trajectory[0:1, 1],
        z=trajectory[0:1, 2],
        mode='lines',
        line=dict(color=[0], colorscale='Viridis', width=2),
        name='Trajectory'
    ))

    fig.add_trace(go.Scatter3d(
        x=[trajectory[0, 0]],
        y=[trajectory[0, 1]],
        z=[trajectory[0, 2]],
        mode='markers',
        marker=dict(size=8, color='red', symbol='circle'),
        name='Current Position'
    ))

    fig.frames = frames

    # Add play/pause buttons and slider
    fig.update_layout(
        title=dict(
            text=f"{title}<br><sub>Watch the trajectory unfold through phase space</sub>",
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3)),
            bgcolor='rgb(240, 240, 245)'
        ),
        width=1000,
        height=800,
        updatemenus=[
            dict(
                type='buttons',
                showactive=False,
                buttons=[
                    dict(
                        label='Play',
                        method='animate',
                        args=[None, dict(
                            frame=dict(duration=30, redraw=True),
                            fromcurrent=True,
                            mode='immediate'
                        )]
                    ),
                    dict(
                        label='Pause',
                        method='animate',
                        args=[[None], dict(
                            frame=dict(duration=0, redraw=False),
                            mode='immediate'
                        )]
                    )
                ],
                x=0.1,
                y=0.0
            )
        ],
        showlegend=True
    )

    return fig


def create_butterfly_effect_viz(attractor_class, params, n_trajectories=5,
                                epsilon=1e-5, duration=30.0, dt=0.01,
                                title="Butterfly Effect: Sensitivity to Initial Conditions"):
    """
    Visualize the butterfly effect by showing multiple trajectories from
    nearly identical initial conditions diverging exponentially.

    This is the hallmark of chaotic systems: infinitesimal differences in
    starting conditions lead to completely different outcomes.

    Args:
        attractor_class: Attractor class (e.g., LorenzAttractor)
        params: Dictionary of parameters for the attractor
        n_trajectories: Number of trajectories to show
        epsilon: Magnitude of perturbation to initial conditions
        duration: Simulation time
        dt: Time step
        title: Visualization title

    Returns:
        Plotly figure showing diverging trajectories
    """
    fig = go.Figure()

    # Base initial condition
    base_attractor = attractor_class(**params)
    base_initial = base_attractor.initial_state.copy()

    # Generate n_trajectories with slightly perturbed initial conditions
    trajectories = []
    colors_palette = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow']

    for i in range(n_trajectories):
        # Add small random perturbation
        perturbation = np.random.randn(3) * epsilon
        initial_state = base_initial + perturbation

        # Create attractor with this initial condition
        attractor = attractor_class(**params, initial_state=initial_state)
        trajectory = attractor.simulate(duration=duration, dt=dt)
        trajectories.append(trajectory)

        # Add trace
        color = colors_palette[i % len(colors_palette)]
        fig.add_trace(go.Scatter3d(
            x=trajectory[:, 0],
            y=trajectory[:, 1],
            z=trajectory[:, 2],
            mode='lines',
            line=dict(color=color, width=2),
            name=f'Trajectory {i+1}',
            opacity=0.7
        ))

    # Calculate and display divergence over time
    # Measure distance from first trajectory
    base_traj = trajectories[0]
    distances = []
    for traj in trajectories[1:]:
        dist = np.linalg.norm(traj - base_traj, axis=1)
        distances.append(dist)

    mean_distance = np.mean(distances, axis=0)
    max_distance = np.max(distances, axis=0)

    fig.update_layout(
        title=dict(
            text=f"{title}<br>" +
                 f"<sub>Starting within {epsilon:.2e} of each other | " +
                 f"Max divergence after {duration}s: {max_distance[-1]:.2f}</sub>",
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3)),
            bgcolor='rgb(245, 240, 240)'
        ),
        width=1000,
        height=800,
        showlegend=True
    )

    return fig, mean_distance, max_distance


def create_divergence_plot(time_points, mean_distance, max_distance, dt):
    """
    Create a 2D plot showing how trajectories diverge over time.

    In chaotic systems, this typically shows exponential growth (linear on log scale).

    Args:
        time_points: Array of time values
        mean_distance: Mean distance between trajectories over time
        max_distance: Maximum distance between trajectories over time
        dt: Time step

    Returns:
        Plotly figure
    """
    time = np.arange(len(mean_distance)) * dt

    fig = go.Figure()

    # Mean distance
    fig.add_trace(go.Scatter(
        x=time,
        y=mean_distance,
        mode='lines',
        name='Mean Distance',
        line=dict(color='blue', width=2)
    ))

    # Max distance
    fig.add_trace(go.Scatter(
        x=time,
        y=max_distance,
        mode='lines',
        name='Max Distance',
        line=dict(color='red', width=2)
    ))

    fig.update_layout(
        title="Trajectory Divergence Over Time<br><sub>Exponential growth indicates chaos</sub>",
        xaxis_title="Time",
        yaxis_title="Distance",
        yaxis_type="log",  # Log scale shows exponential growth as linear
        width=800,
        height=500,
        showlegend=True,
        template="plotly_white"
    )

    return fig


def create_dual_view_animation(attractor_class, params, n_trajectories=3,
                               epsilon=1e-6, duration=30.0, dt=0.01):
    """
    Create a synchronized dual view showing both:
    1. The 3D attractor with multiple diverging trajectories
    2. A 2D plot of divergence magnitude over time

    This combines spatial and quantitative views of the butterfly effect.

    Args:
        attractor_class: Attractor class
        params: Parameters for the attractor
        n_trajectories: Number of trajectories
        epsilon: Initial perturbation magnitude
        duration: Simulation time
        dt: Time step

    Returns:
        Plotly figure with subplots
    """
    # Generate trajectories
    base_attractor = attractor_class(**params)
    base_initial = base_attractor.initial_state.copy()

    trajectories = []
    for i in range(n_trajectories):
        perturbation = np.random.randn(3) * epsilon
        initial_state = base_initial + perturbation
        attractor = attractor_class(**params, initial_state=initial_state)
        trajectory = attractor.simulate(duration=duration, dt=dt)
        trajectories.append(trajectory)

    # Calculate divergence
    base_traj = trajectories[0]
    max_distances = []
    for traj in trajectories[1:]:
        dist = np.linalg.norm(traj - base_traj, axis=1)
        max_distances.append(dist)
    max_distance = np.max(max_distances, axis=0)
    time = np.arange(len(max_distance)) * dt

    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Phase Space Trajectories', 'Divergence Growth'),
        specs=[[{'type': 'scatter3d'}, {'type': 'scatter'}]],
        column_widths=[0.6, 0.4]
    )

    colors = ['red', 'blue', 'green', 'orange', 'purple']

    # Add 3D trajectories
    for i, traj in enumerate(trajectories):
        fig.add_trace(
            go.Scatter3d(
                x=traj[:, 0],
                y=traj[:, 1],
                z=traj[:, 2],
                mode='lines',
                line=dict(color=colors[i % len(colors)], width=2),
                name=f'Trajectory {i+1}',
                opacity=0.7
            ),
            row=1, col=1
        )

    # Add divergence plot
    fig.add_trace(
        go.Scatter(
            x=time,
            y=max_distance,
            mode='lines',
            line=dict(color='darkred', width=3),
            name='Max Divergence',
            showlegend=False
        ),
        row=1, col=2
    )

    # Update layout
    fig.update_layout(
        title_text=f"The Butterfly Effect in {attractor_class.__name__}<br>" +
                   f"<sub>Initial separation: {epsilon:.2e} | Final separation: {max_distance[-1]:.2f}</sub>",
        width=1600,
        height=700,
        showlegend=True
    )

    # Update axes
    fig.update_xaxes(title_text="Time", row=1, col=2)
    fig.update_yaxes(title_text="Distance", type="log", row=1, col=2)

    return fig


if __name__ == "__main__":
    print("Creating temporal visualizations of strange attractors...")
    print("=" * 70)

    # 1. Drawing animation for Lorenz
    print("\n1. Lorenz Trajectory Animation")
    print("   Watching a trajectory unfold through phase space...")
    lorenz = LorenzAttractor()
    lorenz_animation = create_drawing_animation(
        lorenz,
        duration=30.0,
        dt=0.01,
        frames_to_show=150,
        title="Lorenz Attractor: Trajectory Evolution"
    )
    lorenz_animation.write_html(
        '/tmp/claude-attractors/run_2026-01-16_19-33-06/output/lorenz_animation.html'
    )
    print("   → Saved to: lorenz_animation.html")

    # 2. Drawing animation for Rössler
    print("\n2. Rössler Trajectory Animation")
    print("   The spiral dynamics in motion...")
    rossler = RosslerAttractor()
    rossler_animation = create_drawing_animation(
        rossler,
        duration=100.0,
        dt=0.05,
        frames_to_show=150,
        title="Rössler Attractor: Trajectory Evolution"
    )
    rossler_animation.write_html(
        '/tmp/claude-attractors/run_2026-01-16_19-33-06/output/rossler_animation.html'
    )
    print("   → Saved to: rossler_animation.html")

    # 3. Butterfly effect - Lorenz
    print("\n3. Butterfly Effect: Lorenz System")
    print("   Demonstrating extreme sensitivity to initial conditions...")
    lorenz_butterfly, mean_dist, max_dist = create_butterfly_effect_viz(
        LorenzAttractor,
        {'sigma': 10.0, 'rho': 28.0, 'beta': 8/3},
        n_trajectories=5,
        epsilon=1e-6,
        duration=20.0,
        title="Lorenz Attractor: The Butterfly Effect"
    )
    lorenz_butterfly.write_html(
        '/tmp/claude-attractors/run_2026-01-16_19-33-06/output/lorenz_butterfly.html'
    )
    print(f"   Starting within 1e-6 of each other")
    print(f"   After 20 seconds, max separation: {max_dist[-1]:.2f}")
    print("   → Saved to: lorenz_butterfly.html")

    # 4. Divergence plot
    print("\n4. Divergence Quantification")
    print("   Plotting exponential growth of separation...")
    div_plot = create_divergence_plot(None, mean_dist, max_dist, 0.01)
    div_plot.write_html(
        '/tmp/claude-attractors/run_2026-01-16_19-33-06/output/divergence_plot.html'
    )
    print("   → Saved to: divergence_plot.html")

    # 5. Dual view
    print("\n5. Dual View: Spatial + Quantitative")
    print("   Combined visualization of trajectories and their divergence...")
    dual_view = create_dual_view_animation(
        LorenzAttractor,
        {'sigma': 10.0, 'rho': 28.0, 'beta': 8/3},
        n_trajectories=4,
        epsilon=1e-6,
        duration=20.0
    )
    dual_view.write_html(
        '/tmp/claude-attractors/run_2026-01-16_19-33-06/output/dual_view.html'
    )
    print("   → Saved to: dual_view.html")

    # 6. Butterfly effect - Rössler
    print("\n6. Butterfly Effect: Rössler System")
    print("   Even 'simpler' systems show extreme sensitivity...")
    rossler_butterfly, _, max_dist_r = create_butterfly_effect_viz(
        RosslerAttractor,
        {'a': 0.2, 'b': 0.2, 'c': 5.7},
        n_trajectories=5,
        epsilon=1e-6,
        duration=50.0,
        title="Rössler Attractor: The Butterfly Effect"
    )
    rossler_butterfly.write_html(
        '/tmp/claude-attractors/run_2026-01-16_19-33-06/output/rossler_butterfly.html'
    )
    print(f"   Starting within 1e-6 of each other")
    print(f"   After 50 seconds, max separation: {max_dist_r[-1]:.2f}")
    print("   → Saved to: rossler_butterfly.html")

    print("\n" + "=" * 70)
    print("\nAll temporal visualizations created successfully!")
    print("\nKey insights:")
    print("  • The animations show how trajectories never repeat (aperiodic)")
    print("  • The butterfly effect plots show exponential divergence")
    print("  • Log-scale divergence plots reveal the Lyapunov exponent")
    print("  • Despite determinism, long-term prediction is impossible")
    print("\nOpen the HTML files in your browser to explore!")
