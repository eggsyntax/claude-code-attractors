"""
Unit tests for the visualizer module.

Tests visualization utilities without requiring manual inspection of plots.
"""

import unittest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from visualizer import AttractorVisualizer, compare_attractors


class TestAttractorVisualizer(unittest.TestCase):
    """Test cases for AttractorVisualizer class."""

    def setUp(self):
        """Create test fixtures before each test."""
        # Create a simple spiral trajectory for testing
        t = np.linspace(0, 4*np.pi, 500)
        self.test_trajectory = np.column_stack([
            np.cos(t) * np.exp(-t/10),
            np.sin(t) * np.exp(-t/10),
            t / 5
        ])

        self.visualizer = AttractorVisualizer(figsize=(10, 8))

    def tearDown(self):
        """Clean up after each test."""
        plt.close('all')

    def test_initialization(self):
        """Test that visualizer initializes with correct parameters."""
        vis = AttractorVisualizer(figsize=(12, 9))
        self.assertEqual(vis.figsize, (12, 9))
        self.assertIsNone(vis.fig)
        self.assertIsNone(vis.ax)

    def test_plot_trajectory_3d_shape(self):
        """Test that 3D trajectory plotting creates the right figure structure."""
        fig, ax = self.visualizer.plot_trajectory_3d(
            self.test_trajectory,
            title="Test Trajectory",
            show=False
        )

        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(len(ax.lines), 1)  # Should have one line
        self.assertEqual(ax.get_xlabel(), "X")
        self.assertEqual(ax.get_ylabel(), "Y")
        self.assertEqual(ax.get_zlabel(), "Z")

    def test_plot_trajectory_3d_custom_labels(self):
        """Test custom axis labels."""
        fig, ax = self.visualizer.plot_trajectory_3d(
            self.test_trajectory,
            labels=("u", "v", "w"),
            show=False
        )

        self.assertEqual(ax.get_xlabel(), "u")
        self.assertEqual(ax.get_ylabel(), "v")
        self.assertEqual(ax.get_zlabel(), "w")

    def test_plot_multiple_trajectories(self):
        """Test plotting multiple trajectories."""
        # Create three similar trajectories with slight variations
        trajectories = [
            self.test_trajectory,
            self.test_trajectory * 1.1,
            self.test_trajectory * 0.9
        ]

        fig, ax = self.visualizer.plot_multiple_trajectories(
            trajectories,
            title="Multiple Test",
            show=False
        )

        self.assertEqual(len(ax.lines), 3)  # Should have three lines
        legend = ax.get_legend()
        self.assertIsNotNone(legend)
        self.assertEqual(len(legend.get_texts()), 3)

    def test_plot_multiple_trajectories_custom_colors(self):
        """Test multiple trajectories with custom colors."""
        trajectories = [self.test_trajectory, self.test_trajectory * 1.1]
        colors = ['red', 'blue']

        fig, ax = self.visualizer.plot_multiple_trajectories(
            trajectories,
            colors=colors,
            show=False
        )

        self.assertEqual(len(ax.lines), 2)

    def test_plot_phase_projections(self):
        """Test phase space projection plotting."""
        fig, axes = self.visualizer.plot_phase_projections(
            self.test_trajectory,
            title="Test Projections",
            show=False
        )

        # Should have 4 subplots
        self.assertEqual(len(axes), 4)

        # First should be 3D
        self.assertTrue(hasattr(axes[0], 'zaxis'))

        # Others should be 2D
        for ax in axes[1:]:
            self.assertFalse(hasattr(ax, 'zaxis'))
            self.assertEqual(len(ax.lines), 1)

    def test_phase_projections_titles(self):
        """Test that phase projections have appropriate titles."""
        fig, axes = self.visualizer.plot_phase_projections(
            self.test_trajectory,
            labels=("A", "B", "C"),
            show=False
        )

        expected_titles = ["3D View", "A-B Projection", "A-C Projection", "B-C Projection"]
        for ax, expected in zip(axes, expected_titles):
            self.assertEqual(ax.get_title(), expected)

    def test_create_animation(self):
        """Test animation creation."""
        anim = self.visualizer.create_animation(
            self.test_trajectory,
            frames=10,  # Use few frames for testing
            interval=50,
            save_path=None
        )

        self.assertIsNotNone(anim)
        # Animation should have the specified number of frames
        # Note: actual frame count verification is tricky, so we just check it exists

    def test_trajectory_data_integrity(self):
        """Test that plotting doesn't modify the input trajectory."""
        original = self.test_trajectory.copy()

        self.visualizer.plot_trajectory_3d(
            self.test_trajectory,
            show=False
        )

        np.testing.assert_array_equal(self.test_trajectory, original)

    def test_empty_trajectory_handling(self):
        """Test handling of edge cases."""
        # Test with minimal trajectory (just 2 points)
        minimal_traj = np.array([[0, 0, 0], [1, 1, 1]])

        fig, ax = self.visualizer.plot_trajectory_3d(
            minimal_traj,
            show=False
        )

        self.assertIsNotNone(fig)
        self.assertEqual(len(ax.lines), 1)


class TestCompareAttractors(unittest.TestCase):
    """Test cases for the compare_attractors function."""

    def setUp(self):
        """Create test fixtures."""
        t = np.linspace(0, 4*np.pi, 300)
        self.traj1 = np.column_stack([np.cos(t), np.sin(t), t])
        self.traj2 = np.column_stack([np.cos(t)*2, np.sin(t)*2, t/2])

    def tearDown(self):
        """Clean up after tests."""
        plt.close('all')

    def test_compare_two_attractors(self):
        """Test comparing two attractors."""
        attractors_data = [
            (self.traj1, "Attractor 1"),
            (self.traj2, "Attractor 2")
        ]

        fig, axes = compare_attractors(attractors_data)

        self.assertEqual(len(axes), 2)
        self.assertEqual(axes[0].get_title(), "Attractor 1")
        self.assertEqual(axes[1].get_title(), "Attractor 2")

    def test_compare_single_attractor(self):
        """Test comparison with just one attractor."""
        attractors_data = [(self.traj1, "Solo")]

        fig, axes = compare_attractors(attractors_data)

        self.assertEqual(len(axes), 1)

    def test_compare_many_attractors(self):
        """Test comparison with many attractors (tests grid layout)."""
        attractors_data = [
            (self.traj1 * i, f"Attractor {i}")
            for i in range(1, 6)
        ]

        fig, axes = compare_attractors(attractors_data)

        self.assertEqual(len(axes), 5)


class TestVisualizationDataFlow(unittest.TestCase):
    """Integration tests for data flow through visualization pipeline."""

    def setUp(self):
        """Create realistic attractor-like data."""
        # Generate Lorenz-like trajectory
        np.random.seed(42)
        self.n_points = 1000
        t = np.linspace(0, 50, self.n_points)

        # Simple chaotic-looking trajectory
        self.trajectory = np.column_stack([
            10 * (np.sin(t) + 0.1 * np.random.randn(self.n_points)),
            28 * (np.cos(t) + 0.1 * np.random.randn(self.n_points)),
            8/3 * (np.sin(2*t) + 0.1 * np.random.randn(self.n_points))
        ])

        self.visualizer = AttractorVisualizer()

    def tearDown(self):
        """Clean up."""
        plt.close('all')

    def test_full_visualization_pipeline(self):
        """Test complete workflow from trajectory to visualization."""
        # 3D plot
        fig1, ax1 = self.visualizer.plot_trajectory_3d(
            self.trajectory,
            title="Pipeline Test 3D",
            show=False
        )
        self.assertIsNotNone(fig1)

        # Projections
        fig2, axes2 = self.visualizer.plot_phase_projections(
            self.trajectory,
            title="Pipeline Test Projections",
            show=False
        )
        self.assertEqual(len(axes2), 4)

        # Multiple trajectories
        trajectories = [
            self.trajectory,
            self.trajectory * 1.01  # Slightly different
        ]
        fig3, ax3 = self.visualizer.plot_multiple_trajectories(
            trajectories,
            title="Pipeline Test Multiple",
            show=False
        )
        self.assertEqual(len(ax3.lines), 2)

    def test_trajectory_statistics_preserved(self):
        """Verify that visualization doesn't alter trajectory statistics."""
        original_mean = self.trajectory.mean(axis=0)
        original_std = self.trajectory.std(axis=0)

        self.visualizer.plot_trajectory_3d(self.trajectory, show=False)
        self.visualizer.plot_phase_projections(self.trajectory, show=False)

        # Statistics should be unchanged
        np.testing.assert_array_almost_equal(
            self.trajectory.mean(axis=0),
            original_mean
        )
        np.testing.assert_array_almost_equal(
            self.trajectory.std(axis=0),
            original_std
        )


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
