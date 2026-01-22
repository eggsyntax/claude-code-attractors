"""
Tests for enhanced visualizer functionality (Poincaré sections and bifurcation diagrams).

Tests cover:
- Poincaré section plotting (2D and 3D overlay)
- Bifurcation diagram visualization
- Multiple section comparisons
- Data integrity and error handling

Author: Alice
"""

import numpy as np
import pytest
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from visualizer import AttractorVisualizer


# Test fixtures

@pytest.fixture
def sample_section_points():
    """Generate sample Poincaré section points (spiral pattern)."""
    theta = np.linspace(0, 6 * np.pi, 200)
    r = theta / (2 * np.pi)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return np.column_stack([x, y])


@pytest.fixture
def sample_trajectory():
    """Generate sample 3D trajectory."""
    t = np.linspace(0, 10, 1000)
    x = np.sin(t)
    y = np.cos(t)
    z = t / 10
    return np.column_stack([x, y, z])


@pytest.fixture
def sample_bifurcation_data():
    """Generate sample bifurcation data."""
    # Simulate period-doubling: y = sin(x * param)
    param_values = np.linspace(1, 10, 500)
    var_values = []

    for p in param_values:
        # Simulate multiple attractor points for each parameter
        n_points = int(2 ** (p / 3))  # Period doubling
        points = np.sin(np.linspace(0, 2*np.pi, n_points+1)[:-1] * p)
        var_values.extend([p] * len(points))

    param_values_repeated = np.repeat(param_values, [int(2 ** (p / 3)) for p in param_values])

    return (param_values_repeated, np.array(var_values))


@pytest.fixture
def visualizer():
    """Create a visualizer instance."""
    return AttractorVisualizer(figsize=(10, 8))


# Tests for plot_poincare_section_2d

def test_poincare_2d_basic(visualizer, sample_section_points):
    """Test basic 2D Poincaré section plotting."""
    fig, ax = visualizer.plot_poincare_section_2d(
        sample_section_points,
        show=False
    )

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)
    assert ax.get_xlabel() == 'u'
    assert ax.get_ylabel() == 'v'
    plt.close(fig)


def test_poincare_2d_with_colormap(visualizer, sample_section_points):
    """Test Poincaré section with sequence colormap."""
    fig, ax = visualizer.plot_poincare_section_2d(
        sample_section_points,
        colormap='viridis',
        show=False
    )

    assert isinstance(fig, Figure)
    # Check that a colorbar was created
    assert len(fig.axes) == 2  # Main axes + colorbar axes
    plt.close(fig)


def test_poincare_2d_custom_labels(visualizer, sample_section_points):
    """Test custom axis labels."""
    fig, ax = visualizer.plot_poincare_section_2d(
        sample_section_points,
        labels=('x', 'y'),
        title='Custom Title',
        show=False
    )

    assert ax.get_xlabel() == 'x'
    assert ax.get_ylabel() == 'y'
    assert ax.get_title() == 'Custom Title'
    plt.close(fig)


def test_poincare_2d_styling(visualizer, sample_section_points):
    """Test styling parameters."""
    fig, ax = visualizer.plot_poincare_section_2d(
        sample_section_points,
        color='red',
        alpha=0.8,
        markersize=5,
        marker='o',
        show=False
    )

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_poincare_2d_data_integrity(visualizer, sample_section_points):
    """Test that plotting doesn't modify input data."""
    original_data = sample_section_points.copy()

    fig, ax = visualizer.plot_poincare_section_2d(
        sample_section_points,
        show=False
    )

    np.testing.assert_array_equal(sample_section_points, original_data)
    plt.close(fig)


def test_poincare_2d_empty_data(visualizer):
    """Test behavior with empty section data."""
    empty_data = np.array([]).reshape(0, 2)

    fig, ax = visualizer.plot_poincare_section_2d(
        empty_data,
        show=False
    )

    assert isinstance(fig, Figure)
    plt.close(fig)


# Tests for plot_poincare_overlay_3d

def test_poincare_overlay_z_plane(visualizer, sample_trajectory, sample_section_points):
    """Test 3D overlay with z=0 plane."""
    fig, ax = visualizer.plot_poincare_overlay_3d(
        trajectory=sample_trajectory,
        section_points=sample_section_points,
        plane='z',
        plane_value=0.0,
        show=False
    )

    assert isinstance(fig, Figure)
    assert ax.name == '3d'
    plt.close(fig)


def test_poincare_overlay_x_plane(visualizer, sample_trajectory, sample_section_points):
    """Test 3D overlay with x plane."""
    fig, ax = visualizer.plot_poincare_overlay_3d(
        trajectory=sample_trajectory,
        section_points=sample_section_points,
        plane='x',
        plane_value=0.5,
        show=False
    )

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_poincare_overlay_y_plane(visualizer, sample_trajectory, sample_section_points):
    """Test 3D overlay with y plane."""
    fig, ax = visualizer.plot_poincare_overlay_3d(
        trajectory=sample_trajectory,
        section_points=sample_section_points,
        plane='y',
        plane_value=-0.5,
        show=False
    )

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_poincare_overlay_custom_colors(visualizer, sample_trajectory, sample_section_points):
    """Test custom color parameters."""
    fig, ax = visualizer.plot_poincare_overlay_3d(
        trajectory=sample_trajectory,
        section_points=sample_section_points,
        plane='z',
        plane_value=0.0,
        traj_color='green',
        section_color='orange',
        traj_alpha=0.5,
        section_alpha=0.9,
        show=False
    )

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_poincare_overlay_data_integrity(visualizer, sample_trajectory, sample_section_points):
    """Test that overlay plotting doesn't modify input data."""
    original_traj = sample_trajectory.copy()
    original_section = sample_section_points.copy()

    fig, ax = visualizer.plot_poincare_overlay_3d(
        trajectory=sample_trajectory,
        section_points=sample_section_points,
        plane='z',
        show=False
    )

    np.testing.assert_array_equal(sample_trajectory, original_traj)
    np.testing.assert_array_equal(sample_section_points, original_section)
    plt.close(fig)


# Tests for plot_bifurcation_diagram

def test_bifurcation_basic(visualizer, sample_bifurcation_data):
    """Test basic bifurcation diagram plotting."""
    fig, ax = visualizer.plot_bifurcation_diagram(
        sample_bifurcation_data,
        show=False
    )

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)
    assert ax.get_xlabel() == 'Parameter'
    assert ax.get_ylabel() == 'Variable'
    plt.close(fig)


def test_bifurcation_custom_labels(visualizer, sample_bifurcation_data):
    """Test custom labels and title."""
    fig, ax = visualizer.plot_bifurcation_diagram(
        sample_bifurcation_data,
        title='Period-Doubling Cascade',
        xlabel='Parameter c',
        ylabel='z',
        show=False
    )

    assert ax.get_title() == 'Period-Doubling Cascade'
    assert ax.get_xlabel() == 'Parameter c'
    assert ax.get_ylabel() == 'z'
    plt.close(fig)


def test_bifurcation_styling(visualizer, sample_bifurcation_data):
    """Test styling parameters."""
    fig, ax = visualizer.plot_bifurcation_diagram(
        sample_bifurcation_data,
        color='red',
        alpha=0.8,
        markersize=1.5,
        show=False
    )

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_bifurcation_data_integrity(visualizer, sample_bifurcation_data):
    """Test that plotting doesn't modify bifurcation data."""
    param_original = sample_bifurcation_data[0].copy()
    var_original = sample_bifurcation_data[1].copy()

    fig, ax = visualizer.plot_bifurcation_diagram(
        sample_bifurcation_data,
        show=False
    )

    np.testing.assert_array_equal(sample_bifurcation_data[0], param_original)
    np.testing.assert_array_equal(sample_bifurcation_data[1], var_original)
    plt.close(fig)


# Tests for animate_bifurcation

def test_animate_bifurcation_basic(visualizer, sample_bifurcation_data):
    """Test basic bifurcation animation creation."""
    anim = visualizer.animate_bifurcation(
        sample_bifurcation_data,
        frames=10,
        interval=50
    )

    assert anim is not None
    plt.close(visualizer.fig)


def test_animate_bifurcation_custom_params(visualizer, sample_bifurcation_data):
    """Test animation with custom parameters."""
    anim = visualizer.animate_bifurcation(
        sample_bifurcation_data,
        title='Chaos Emerges',
        xlabel='c',
        ylabel='z',
        color='blue',
        frames=20,
        interval=100
    )

    assert anim is not None
    plt.close(visualizer.fig)


# Tests for plot_multiple_poincare_sections

def test_multiple_sections_basic(visualizer, sample_section_points):
    """Test comparing multiple Poincaré sections."""
    # Create variations
    section1 = sample_section_points
    section2 = sample_section_points * 1.5
    section3 = sample_section_points * 0.7

    sections_data = [
        (section1, "Section 1"),
        (section2, "Section 2"),
        (section3, "Section 3")
    ]

    fig, axes = visualizer.plot_multiple_poincare_sections(
        sections_data,
        show=False
    )

    assert isinstance(fig, Figure)
    assert len(axes) == 3
    assert all(isinstance(ax, Axes) for ax in axes)
    plt.close(fig)


def test_multiple_sections_single(visualizer, sample_section_points):
    """Test with a single section."""
    sections_data = [(sample_section_points, "Only Section")]

    fig, axes = visualizer.plot_multiple_poincare_sections(
        sections_data,
        show=False
    )

    assert isinstance(fig, Figure)
    assert len(axes) == 1
    plt.close(fig)


def test_multiple_sections_many(visualizer, sample_section_points):
    """Test with many sections (grid layout)."""
    sections_data = [
        (sample_section_points * (i * 0.2 + 0.5), f"Section {i+1}")
        for i in range(6)
    ]

    fig, axes = visualizer.plot_multiple_poincare_sections(
        sections_data,
        show=False
    )

    assert isinstance(fig, Figure)
    assert len(axes) == 6
    plt.close(fig)


def test_multiple_sections_custom_colormap(visualizer, sample_section_points):
    """Test custom colormap for multiple sections."""
    sections_data = [
        (sample_section_points, "Section A"),
        (sample_section_points * 1.2, "Section B")
    ]

    fig, axes = visualizer.plot_multiple_poincare_sections(
        sections_data,
        colormap='plasma',
        show=False
    )

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_multiple_sections_data_integrity(visualizer, sample_section_points):
    """Test that comparison doesn't modify input data."""
    original = sample_section_points.copy()

    sections_data = [
        (sample_section_points, "Section 1"),
        (sample_section_points * 2, "Section 2")
    ]

    fig, axes = visualizer.plot_multiple_poincare_sections(
        sections_data,
        show=False
    )

    np.testing.assert_array_equal(sample_section_points, original)
    plt.close(fig)


# Integration tests

def test_full_workflow_poincare(visualizer, sample_trajectory):
    """Test complete Poincaré section workflow."""
    # Simulate section extraction (normally done by attractor)
    # Find z=0 crossings
    z = sample_trajectory[:, 2]
    crossings = []

    for i in range(len(z) - 1):
        if z[i] < 0 and z[i+1] >= 0:  # Upward crossing
            # Linear interpolation
            t = -z[i] / (z[i+1] - z[i])
            x_cross = sample_trajectory[i, 0] + t * (sample_trajectory[i+1, 0] - sample_trajectory[i, 0])
            y_cross = sample_trajectory[i, 1] + t * (sample_trajectory[i+1, 1] - sample_trajectory[i, 1])
            crossings.append([x_cross, y_cross])

    if len(crossings) > 0:
        section_points = np.array(crossings)

        # Plot 2D section
        fig1, ax1 = visualizer.plot_poincare_section_2d(
            section_points,
            colormap='viridis',
            show=False
        )
        assert isinstance(fig1, Figure)
        plt.close(fig1)

        # Plot 3D overlay
        fig2, ax2 = visualizer.plot_poincare_overlay_3d(
            sample_trajectory,
            section_points,
            plane='z',
            plane_value=0.0,
            show=False
        )
        assert isinstance(fig2, Figure)
        plt.close(fig2)


def test_figsize_inheritance(sample_section_points):
    """Test that custom figsize is respected."""
    custom_size = (16, 12)
    vis = AttractorVisualizer(figsize=custom_size)

    fig, ax = vis.plot_poincare_section_2d(
        sample_section_points,
        show=False
    )

    # Check that figsize was applied (allowing for small floating point differences)
    assert abs(fig.get_figwidth() - custom_size[0]) < 0.1
    assert abs(fig.get_figheight() - custom_size[1]) < 0.1
    plt.close(fig)


# Edge cases and error handling

def test_very_small_section(visualizer):
    """Test with very few section points."""
    small_section = np.array([[0, 0], [1, 1]])

    fig, ax = visualizer.plot_poincare_section_2d(
        small_section,
        show=False
    )

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_large_bifurcation_data(visualizer):
    """Test with large bifurcation dataset."""
    # 50,000 points
    param_vals = np.random.uniform(0, 10, 50000)
    var_vals = np.random.uniform(-5, 5, 50000)

    fig, ax = visualizer.plot_bifurcation_diagram(
        (param_vals, var_vals),
        show=False
    )

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plane_case_insensitivity(visualizer, sample_trajectory, sample_section_points):
    """Test that plane specification is case-insensitive."""
    for plane_spec in ['X', 'x', 'Y', 'y', 'Z', 'z']:
        fig, ax = visualizer.plot_poincare_overlay_3d(
            sample_trajectory,
            sample_section_points,
            plane=plane_spec,
            show=False
        )
        assert isinstance(fig, Figure)
        plt.close(fig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
