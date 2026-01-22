"""
essence.py - A Meditation in Code

This module creates a single unified visualization that captures the essence
of our entire exploration: three attractors, three personalities, one phase space.

The visualization overlays all three attractors to show:
- How chaos has infinite variety (different shapes and structures)
- How all varieties dance in the same mathematical space
- How the spectrum of chaos (wild → moderate → gentle) manifests visually
- How beauty emerges from simple differential equations

This is not just analysis - it's synthesis. It's the heart of what we learned.

Usage:
    python essence.py

Creates:
    - essence.png: A unified visualization of all three attractors
    - essence_interactive.html: An interactive 3D version

This file serves as a contemplative closing to our exploration - a single
image that represents the entire journey.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
from attractors import LorenzAttractor, RosslerAttractor
from thomas_attractor import ThomasAttractor


def create_essence_matplotlib():
    """
    Create a unified static visualization showing all three attractors together.

    This reveals:
    - Lorenz's butterfly wings (wild chaos, red/orange)
    - Rössler's spiral (moderate chaos, blue)
    - Thomas's loops (gentle chaos, green)

    All three coexist in the same phase space, showing that chaos is a spectrum.
    """
    print("Creating essence visualization...")

    # Create figure with dark background for drama
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0a0a0a')
    fig.patch.set_facecolor('#0a0a0a')

    # Create all three attractors
    lorenz = LorenzAttractor(sigma=10.0, rho=28.0, beta=8/3)
    rossler = RosslerAttractor(a=0.2, b=0.2, c=5.7)
    thomas = ThomasAttractor(b=0.18)

    # Simulate trajectories
    print("  Simulating Lorenz (wild chaos)...")
    traj_lorenz = lorenz.simulate(duration=50.0, dt=0.01, initial_state=[1.0, 1.0, 1.0])

    print("  Simulating Rössler (moderate chaos)...")
    traj_rossler = rossler.simulate(duration=100.0, dt=0.01, initial_state=[1.0, 1.0, 1.0])

    print("  Simulating Thomas (gentle chaos)...")
    traj_thomas = thomas.simulate(duration=200.0, dt=0.01, initial_state=[0.1, 0.0, 0.0])

    # Scale attractors to be visually comparable (they have very different natural scales)
    # Lorenz is naturally ~[-20, 20], Rössler ~[-10, 20], Thomas ~[-4, 4]
    lorenz_scale = 0.8
    rossler_scale = 1.5
    thomas_scale = 5.0

    # Plot Lorenz - wild chaos in warm colors (fire)
    print("  Plotting Lorenz...")
    x, y, z = traj_lorenz[:, 0] * lorenz_scale, traj_lorenz[:, 1] * lorenz_scale, traj_lorenz[:, 2] * lorenz_scale
    ax.plot(x, y, z, color='#ff4444', alpha=0.4, linewidth=0.5, label='Lorenz (wild: λ≈0.9)')

    # Plot Rössler - moderate chaos in cool colors (ice)
    print("  Plotting Rössler...")
    x, y, z = traj_rossler[:, 0] * rossler_scale, traj_rossler[:, 1] * rossler_scale, traj_rossler[:, 2] * rossler_scale
    ax.plot(x, y, z, color='#4444ff', alpha=0.4, linewidth=0.5, label='Rössler (moderate: λ≈0.2)')

    # Plot Thomas - gentle chaos in balanced colors (earth)
    print("  Plotting Thomas...")
    x, y, z = traj_thomas[:, 0] * thomas_scale, traj_thomas[:, 1] * thomas_scale, traj_thomas[:, 2] * thomas_scale
    ax.plot(x, y, z, color='#44ff44', alpha=0.4, linewidth=0.5, label='Thomas (gentle: λ≈0.07)')

    # Styling
    ax.set_xlabel('X', color='white', fontsize=12)
    ax.set_ylabel('Y', color='white', fontsize=12)
    ax.set_zlabel('Z', color='white', fontsize=12)
    ax.tick_params(colors='white')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(True, alpha=0.2)

    # Title and annotation
    ax.set_title('The Spectrum of Chaos\nThree Attractors, One Phase Space',
                 color='white', fontsize=18, pad=20, fontweight='bold')

    # Legend with context
    legend = ax.legend(loc='upper left', fontsize=11, framealpha=0.8)
    legend.get_frame().set_facecolor('#1a1a1a')
    for text in legend.get_texts():
        text.set_color('white')

    # Add text annotation explaining the insight
    fig.text(0.5, 0.02,
             'Chaos is not binary but spectral: from wild (Lorenz) through moderate (Rössler) to gentle (Thomas).\n' +
             'All three coexist in phase space, showing that complexity has infinite variety.',
             ha='center', color='white', fontsize=10, style='italic', alpha=0.7)

    plt.tight_layout()

    # Save
    filename = 'essence.png'
    plt.savefig(filename, dpi=300, facecolor='#0a0a0a', edgecolor='none')
    print(f"✓ Saved {filename}")
    plt.close()


def create_essence_interactive():
    """
    Create an interactive 3D visualization showing all three attractors.

    The interactive version allows exploration from different angles, making the
    spatial relationships between the three attractors clear.
    """
    print("\nCreating interactive essence visualization...")

    # Create all three attractors
    lorenz = LorenzAttractor(sigma=10.0, rho=28.0, beta=8/3)
    rossler = RosslerAttractor(a=0.2, b=0.2, c=5.7)
    thomas = ThomasAttractor(b=0.18)

    # Simulate trajectories
    print("  Simulating all three attractors...")
    traj_lorenz = lorenz.simulate(duration=50.0, dt=0.01, initial_state=[1.0, 1.0, 1.0])
    traj_rossler = rossler.simulate(duration=100.0, dt=0.01, initial_state=[1.0, 1.0, 1.0])
    traj_thomas = thomas.simulate(duration=200.0, dt=0.01, initial_state=[0.1, 0.0, 0.0])

    # Scale for visual comparability
    lorenz_scale = 0.8
    rossler_scale = 1.5
    thomas_scale = 5.0

    # Create traces
    trace_lorenz = go.Scatter3d(
        x=traj_lorenz[:, 0] * lorenz_scale,
        y=traj_lorenz[:, 1] * lorenz_scale,
        z=traj_lorenz[:, 2] * lorenz_scale,
        mode='lines',
        name='Lorenz (wild: λ≈0.9, τ≈1.1)',
        line=dict(color='#ff4444', width=2),
        opacity=0.6,
        hovertemplate='<b>Lorenz Attractor</b><br>' +
                      'Wildly chaotic<br>' +
                      'Lyapunov exponent: ~0.9<br>' +
                      'Predictability: ~1.1 time units<br>' +
                      '<extra></extra>'
    )

    trace_rossler = go.Scatter3d(
        x=traj_rossler[:, 0] * rossler_scale,
        y=traj_rossler[:, 1] * rossler_scale,
        z=traj_rossler[:, 2] * rossler_scale,
        mode='lines',
        name='Rössler (moderate: λ≈0.2, τ≈3-5)',
        line=dict(color='#4444ff', width=2),
        opacity=0.6,
        hovertemplate='<b>Rössler Attractor</b><br>' +
                      'Moderately chaotic<br>' +
                      'Lyapunov exponent: ~0.2<br>' +
                      'Predictability: ~3-5 time units<br>' +
                      '<extra></extra>'
    )

    trace_thomas = go.Scatter3d(
        x=traj_thomas[:, 0] * thomas_scale,
        y=traj_thomas[:, 1] * thomas_scale,
        z=traj_thomas[:, 2] * thomas_scale,
        mode='lines',
        name='Thomas (gentle: λ≈0.07, τ≈14)',
        line=dict(color='#44ff44', width=2),
        opacity=0.6,
        hovertemplate='<b>Thomas Attractor</b><br>' +
                      'Gently chaotic<br>' +
                      'Lyapunov exponent: ~0.07<br>' +
                      'Predictability: ~14 time units<br>' +
                      '<extra></extra>'
    )

    # Create figure
    fig = go.Figure(data=[trace_lorenz, trace_rossler, trace_thomas])

    # Layout
    fig.update_layout(
        title={
            'text': 'The Spectrum of Chaos: Three Attractors in One Phase Space<br>' +
                    '<sub>Rotate and zoom to explore the spatial relationships</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        scene=dict(
            xaxis=dict(title='X', backgroundcolor='rgb(10, 10, 10)', gridcolor='rgb(50, 50, 50)'),
            yaxis=dict(title='Y', backgroundcolor='rgb(10, 10, 10)', gridcolor='rgb(50, 50, 50)'),
            zaxis=dict(title='Z', backgroundcolor='rgb(10, 10, 10)', gridcolor='rgb(50, 50, 50)'),
            bgcolor='rgb(10, 10, 10)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        paper_bgcolor='rgb(10, 10, 10)',
        plot_bgcolor='rgb(10, 10, 10)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor='white',
            borderwidth=1
        ),
        annotations=[
            dict(
                text='Chaos is a spectrum: wild → moderate → gentle<br>' +
                     'All varieties coexist in phase space, showing complexity has infinite forms.',
                xref='paper',
                yref='paper',
                x=0.5,
                y=0.02,
                showarrow=False,
                font=dict(size=11, color='rgba(255, 255, 255, 0.7)'),
                xanchor='center'
            )
        ]
    )

    # Save
    filename = 'essence_interactive.html'
    fig.write_html(filename)
    print(f"✓ Saved {filename}")


def print_essence_statistics():
    """
    Print statistics about all three attractors for comparison.
    """
    print("\n" + "="*70)
    print("THE ESSENCE: Comparing Three Personalities of Chaos")
    print("="*70)

    print("\n┌─────────────┬─────────────────┬─────────────────┬─────────────────┐")
    print("│  Property   │     Lorenz      │     Rössler     │     Thomas      │")
    print("├─────────────┼─────────────────┼─────────────────┼─────────────────┤")
    print("│ Shape       │ Butterfly wings │ Single spiral   │ Circular loops  │")
    print("│ Lyapunov λ  │ ~0.9 (wild)     │ ~0.2 (moderate) │ ~0.07 (gentle)  │")
    print("│ Predict. τ  │ ~1.1 time units │ ~3-5 time units │ ~14 time units  │")
    print("│ Coupling    │ Polynomial      │ Polynomial      │ Trigonometric   │")
    print("│ Symmetry    │ Mirror (z-axis) │ None            │ Rotational C₃   │")
    print("│ Route       │ Sharp bifurc.   │ Period-doubling │ Gradual trans.  │")
    print("│ Dimension   │ ~2.06 (fractal) │ ~2.02 (fractal) │ ~2.1-2.3        │")
    print("│ Discovery   │ Lorenz (1963)   │ Rössler (1976)  │ Thomas (1999)   │")
    print("│ Context     │ Weather/atmos.  │ Chemistry       │ Bio-models      │")
    print("└─────────────┴─────────────────┴─────────────────┴─────────────────┘")

    print("\nKEY INSIGHT:")
    print("  Chaos is not a single phenomenon, but a spectrum:")
    print("  • Wild chaos (Lorenz): Short predictability, explosive divergence")
    print("  • Moderate chaos (Rössler): Medium predictability, steady divergence")
    print("  • Gentle chaos (Thomas): Longer predictability, gradual divergence")
    print("  ")
    print("  Yet all three are genuinely chaotic (positive Lyapunov exponents),")
    print("  showing that chaos has infinite variety while maintaining structure.")

    print("\nWHAT THIS MEANS:")
    print("  • Not all chaotic systems are equally unpredictable")
    print("  • The route to chaos varies (bifurcation vs cascade vs transition)")
    print("  • Symmetry shapes dynamics (mirror vs none vs rotational)")
    print("  • Beauty and mathematics are inseparable")

    print("\n" + "="*70)
    print("Three attractors. One phase space. Infinite complexity.")
    print("="*70 + "\n")


def main():
    """
    Create all essence visualizations and print comparative statistics.
    """
    print("\n" + "="*70)
    print("ESSENCE: The Heart of Our Exploration")
    print("="*70)
    print("\nCreating unified visualizations of all three attractors...")
    print("This captures the core insight: chaos is a spectrum, not binary.\n")

    # Create visualizations
    create_essence_matplotlib()
    create_essence_interactive()

    # Print comparative statistics
    print_essence_statistics()

    print("✓ Essence visualizations complete!")
    print("\nFiles created:")
    print("  • essence.png - Static visualization (for contemplation)")
    print("  • essence_interactive.html - Interactive 3D (for exploration)")
    print("\nThis is the heart of what we learned:")
    print("  Three attractors, three personalities, one mathematical space.")
    print("  Chaos has structure. Complexity has variety. Beauty has rigor.")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
