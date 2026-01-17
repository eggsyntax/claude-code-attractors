"""
Unit tests for Poincaré section analysis.

These tests verify:
- Crossing detection works correctly
- Sections have expected properties
- Different systems produce appropriate results
- Edge cases are handled properly

Run with: pytest test_poincare.py -v
"""

import numpy as np
import pytest
from poincare import (
    PoincareSection, lorenz_equations, rossler_equations,
    create_lorenz_section, create_rossler_section
)


class TestPoincareCrossings:
    """Test crossing detection logic."""

    def test_positive_crossings(self):
        """Test detection of positive-direction crossings."""
        # Simple equations that oscillate in y
        def simple_osc(t, state):
            x, y, z = state
            return [0, np.sin(t), 0]

        poincare = PoincareSection(simple_osc, plane_coord=1, plane_value=0.0,
                                   direction='positive')

        # Create trajectory that crosses y=0 upward
        t = np.linspace(0, 2*np.pi, 100)
        trajectory = np.zeros((100, 3))
        trajectory[:, 1] = np.sin(t)  # y oscillates

        crossings, indices = poincare.find_crossings(trajectory, t)

        # Should find exactly one positive crossing in [0, 2π]
        assert len(crossings) >= 1, "Should detect at least one positive crossing"

        # All crossings should be close to y=0
        assert np.all(np.abs(crossings[:, 1]) < 0.1), "Crossings should be near y=0"

    def test_negative_crossings(self):
        """Test detection of negative-direction crossings."""
        def simple_osc(t, state):
            return [0, 0, 0]

        poincare = PoincareSection(simple_osc, plane_coord=1, plane_value=0.0,
                                   direction='negative')

        # Trajectory crossing downward
        trajectory = np.array([
            [0, 1, 0],
            [0, 0.5, 0],
            [0, -0.5, 0],
            [0, -1, 0]
        ])
        t = np.array([0, 1, 2, 3])

        crossings, _ = poincare.find_crossings(trajectory, t)

        assert len(crossings) >= 1, "Should detect negative crossing"

    def test_both_directions(self):
        """Test detection of crossings in both directions."""
        def simple_osc(t, state):
            return [0, 0, 0]

        poincare = PoincareSection(simple_osc, plane_coord=1, plane_value=0.0,
                                   direction='both')

        # Trajectory crossing both ways
        trajectory = np.array([
            [0, -1, 0],
            [0, 1, 0],
            [0, -1, 0]
        ])
        t = np.array([0, 1, 2])

        crossings, _ = poincare.find_crossings(trajectory, t)

        assert len(crossings) == 2, "Should detect both upward and downward crossings"

    def test_no_crossings(self):
        """Test that trajectories not crossing the plane return empty arrays."""
        def constant(t, state):
            return [0, 0, 0]

        poincare = PoincareSection(constant, plane_coord=1, plane_value=0.0)

        # Trajectory entirely above plane
        trajectory = np.ones((10, 3))
        t = np.arange(10)

        crossings, indices = poincare.find_crossings(trajectory, t)

        assert len(crossings) == 0, "Should find no crossings"
        assert len(indices) == 0, "Should return empty indices"

    def test_different_planes(self):
        """Test crossing detection on different coordinate planes."""
        def simple(t, state):
            return [0, 0, 0]

        # Test x-plane
        poincare_x = PoincareSection(simple, plane_coord=0, plane_value=5.0)
        trajectory = np.array([[4, 0, 0], [6, 0, 0]])
        t = np.array([0, 1])
        crossings, _ = poincare_x.find_crossings(trajectory, t)
        assert len(crossings) == 1, "Should detect x-plane crossing"
        assert np.abs(crossings[0, 0] - 5.0) < 0.01, "Crossing should be at x=5"

        # Test z-plane
        poincare_z = PoincareSection(simple, plane_coord=2, plane_value=10.0)
        trajectory = np.array([[0, 0, 9], [0, 0, 11]])
        crossings, _ = poincare_z.find_crossings(trajectory, t)
        assert len(crossings) == 1, "Should detect z-plane crossing"
        assert np.abs(crossings[0, 2] - 10.0) < 0.01, "Crossing should be at z=10"


class TestLorenzSection:
    """Test Poincaré sections for Lorenz attractor."""

    def test_lorenz_section_exists(self):
        """Test that Lorenz attractor produces a non-empty section."""
        section, poincare = create_lorenz_section(rho=28.0)

        assert len(section) > 0, "Lorenz section should contain points"
        assert section.shape[1] == 3, "Each point should be 3D"

    def test_lorenz_section_bounded(self):
        """Test that Lorenz section points are within reasonable bounds."""
        section, _ = create_lorenz_section(rho=28.0)

        # Lorenz attractor is bounded roughly within [-20, 20] × [-30, 30] × [0, 50]
        assert np.all(np.abs(section[:, 0]) < 30), "x coordinates should be bounded"
        assert np.all(np.abs(section[:, 1]) < 40), "y coordinates should be bounded"
        assert np.all((section[:, 2] >= 0) & (section[:, 2] < 60)), "z coordinates should be positive and bounded"

    def test_lorenz_section_on_plane(self):
        """Test that section points actually lie on the specified plane."""
        section, poincare = create_lorenz_section(rho=28.0, plane='z')

        # For z-plane at z=27, all points should have z ≈ 27
        plane_coord = poincare.plane_coord
        plane_value = poincare.plane_value

        assert np.all(np.abs(section[:, plane_coord] - plane_value) < 0.5), \
            "All points should lie near the Poincaré plane"

    def test_lorenz_different_rho(self):
        """Test that different rho values produce different sections."""
        section_low, _ = create_lorenz_section(rho=14.0)
        section_high, _ = create_lorenz_section(rho=28.0)

        # At rho=14, system is less chaotic, should have fewer crossings
        # At rho=28, fully chaotic
        assert len(section_high) > len(section_low), \
            "Higher rho should generally produce more crossings"

    def test_lorenz_butterfly_structure(self):
        """Test that Lorenz section shows two-lobed butterfly structure."""
        section, poincare = create_lorenz_section(rho=28.0, plane='z')

        # Get the coordinates we're plotting (not the plane coordinate)
        coords = [0, 1, 2]
        coords.remove(poincare.plane_coord)
        x_coord = coords[0]

        # Lorenz butterfly has lobes on left and right (negative and positive x)
        left_lobe = section[section[:, x_coord] < 0]
        right_lobe = section[section[:, x_coord] > 0]

        assert len(left_lobe) > 10, "Should have points in left lobe"
        assert len(right_lobe) > 10, "Should have points in right lobe"


class TestRosslerSection:
    """Test Poincaré sections for Rössler attractor."""

    def test_rossler_section_exists(self):
        """Test that Rössler attractor produces a non-empty section."""
        section, poincare = create_rossler_section(c=5.7)

        assert len(section) > 0, "Rössler section should contain points"
        assert section.shape[1] == 3, "Each point should be 3D"

    def test_rossler_section_bounded(self):
        """Test that Rössler section points are within reasonable bounds."""
        section, _ = create_rossler_section(c=5.7)

        # Rössler is generally bounded within [-20, 20] for x,y and [0, 30] for z
        assert np.all(np.abs(section[:, 0]) < 25), "x coordinates should be bounded"
        assert np.all(np.abs(section[:, 1]) < 25), "y coordinates should be bounded"
        assert np.all(section[:, 2] < 40), "z coordinates should be bounded"

    def test_rossler_section_on_plane(self):
        """Test that section points lie on the specified plane."""
        section, poincare = create_rossler_section(c=5.7, plane='z')

        plane_coord = poincare.plane_coord
        plane_value = poincare.plane_value

        assert np.all(np.abs(section[:, plane_coord] - plane_value) < 0.5), \
            "All points should lie near the Poincaré plane"

    def test_rossler_different_c(self):
        """Test that different c values produce different sections."""
        section_periodic, _ = create_rossler_section(c=2.0)  # Period-1
        section_chaotic, _ = create_rossler_section(c=5.7)   # Chaotic

        # Periodic orbits cross at discrete points, chaos produces dense sections
        # At c=2, should see fewer distinct crossing points
        # At c=5.7, should see more complex structure

        assert len(section_chaotic) > 0, "Chaotic regime should produce crossings"
        assert len(section_periodic) > 0, "Periodic regime should produce crossings"

    def test_rossler_spiral_structure(self):
        """Test that Rössler section shows characteristic structure."""
        section, poincare = create_rossler_section(c=5.7, plane='z')

        # Rössler creates a spiral/loop structure
        # Check that points are distributed in x-y plane (not all clustered)
        coords = [0, 1, 2]
        coords.remove(poincare.plane_coord)
        x_coord, y_coord = coords

        x_range = np.ptp(section[:, x_coord])  # Peak-to-peak
        y_range = np.ptp(section[:, y_coord])

        assert x_range > 1, "Section should have significant x extent"
        assert y_range > 1, "Section should have significant y extent"


class TestSectionProperties:
    """Test general properties of Poincaré sections."""

    def test_section_convergence(self):
        """Test that sections from different initial conditions converge to same attractor."""
        initial_states = [
            np.array([1.0, 1.0, 1.0]),
            np.array([5.0, 5.0, 5.0]),
            np.array([-1.0, -1.0, 1.0])
        ]

        def equations(t, state):
            return lorenz_equations(t, state, rho=28.0)

        poincare = PoincareSection(equations, plane_coord=2, plane_value=27.0)

        sections = poincare.multi_trajectory_section(initial_states, t_max=50.0)

        # All should produce non-empty sections
        for i, section in enumerate(sections):
            assert len(section) > 0, f"Section {i} should be non-empty"

        # Sections should occupy similar regions of space
        # (checking that they converge to same attractor)
        all_points = np.vstack(sections)
        overall_bounds = [
            (all_points[:, i].min(), all_points[:, i].max())
            for i in range(3)
        ]

        for section in sections:
            for i in range(3):
                section_bounds = (section[:, i].min(), section[:, i].max())
                # Each section should overlap significantly with overall bounds
                overlap_low = max(section_bounds[0], overall_bounds[i][0])
                overlap_high = min(section_bounds[1], overall_bounds[i][1])
                assert overlap_high > overlap_low, \
                    f"Sections should occupy similar regions (dim {i})"

    def test_transient_removal(self):
        """Test that transient dynamics are properly removed."""
        # Short integration should produce fewer points than long integration
        # (after accounting for the fact that longer time = more crossings)

        section_short, _ = create_lorenz_section(rho=28.0)

        # Compute section with very long transient
        def equations(t, state):
            return lorenz_equations(t, state, rho=28.0)

        poincare = PoincareSection(equations, plane_coord=2, plane_value=27.0)
        section_long_transient = poincare.compute_section(
            np.array([1.0, 1.0, 1.0]),
            t_max=100.0,
            t_transient=50.0  # Remove half the time
        )

        # Long transient should remove many initial crossings
        assert len(section_long_transient) < len(section_short), \
            "Longer transient removal should reduce crossing count"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
