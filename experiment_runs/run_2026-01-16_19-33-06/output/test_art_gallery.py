"""
Test suite for Attractor Art Gallery.

Tests the artistic rendering functionality including trajectory generation,
colormap creation, and rendering methods.

Author: Alice
Date: January 2026
"""

import unittest
import numpy as np
import os
import tempfile
from art_gallery import ArtisticRenderer


class TestArtisticRenderer(unittest.TestCase):
    """Test suite for the ArtisticRenderer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.renderer = ArtisticRenderer(dpi=100, figsize=(6, 4))

    def test_initialization(self):
        """Test renderer initialization with parameters."""
        renderer = ArtisticRenderer(dpi=150, figsize=(10, 8))
        self.assertEqual(renderer.dpi, 150)
        self.assertEqual(renderer.figsize, (10, 8))

    def test_lorenz_equations(self):
        """Test Lorenz system equations return correct derivatives."""
        state = [1.0, 2.0, 3.0]
        derivatives = self.renderer.lorenz(0, state, sigma=10.0, beta=8/3, rho=28.0)

        # Expected: [sigma*(y-x), x*(rho-z)-y, x*y-beta*z]
        expected = [
            10.0 * (2.0 - 1.0),  # 10
            1.0 * (28.0 - 3.0) - 2.0,  # 23
            1.0 * 2.0 - (8/3) * 3.0  # -6
        ]

        np.testing.assert_array_almost_equal(derivatives, expected, decimal=10)

    def test_rossler_equations(self):
        """Test Rössler system equations return correct derivatives."""
        state = [1.0, 2.0, 3.0]
        derivatives = self.renderer.rossler(0, state, a=0.2, b=0.2, c=5.7)

        # Expected: [-y-z, x+a*y, b+z*(x-c)]
        expected = [
            -2.0 - 3.0,  # -5
            1.0 + 0.2 * 2.0,  # 1.4
            0.2 + 3.0 * (1.0 - 5.7)  # -13.9
        ]

        np.testing.assert_array_almost_equal(derivatives, expected, decimal=10)

    def test_thomas_equations(self):
        """Test Thomas system equations return correct derivatives."""
        state = [0.5, 0.3, 0.1]
        derivatives = self.renderer.thomas(0, state, b=0.208)

        # Expected: [sin(y)-b*x, sin(z)-b*y, sin(x)-b*z]
        expected = [
            np.sin(0.3) - 0.208 * 0.5,
            np.sin(0.1) - 0.208 * 0.3,
            np.sin(0.5) - 0.208 * 0.1
        ]

        np.testing.assert_array_almost_equal(derivatives, expected, decimal=10)

    def test_thomas_cyclical_symmetry(self):
        """Test that Thomas equations respect cyclical symmetry: (x,y,z) → (y,z,x)."""
        state_xyz = [0.5, 0.3, 0.1]
        state_yzx = [0.3, 0.1, 0.5]  # Rotated version

        deriv_xyz = self.renderer.thomas(0, state_xyz)
        deriv_yzx = self.renderer.thomas(0, state_yzx)

        # If (x,y,z) gives derivatives (dx,dy,dz), then (y,z,x) should give (dy,dz,dx)
        expected_rotated = [deriv_xyz[1], deriv_xyz[2], deriv_xyz[0]]

        np.testing.assert_array_almost_equal(deriv_yzx, expected_rotated, decimal=10)

    def test_trajectory_generation_shape(self):
        """Test that generated trajectories have correct shape."""
        trajectory = self.renderer.generate_trajectory(
            self.renderer.lorenz,
            [1.0, 1.0, 1.0],
            t_span=(0, 10),
            dt=0.1
        )

        # Should have ~100 points (10/0.1) and 3 dimensions
        self.assertEqual(trajectory.shape[1], 3)
        self.assertGreater(trajectory.shape[0], 90)  # Allow some flexibility
        self.assertLess(trajectory.shape[0], 110)

    def test_trajectory_continuity(self):
        """Test that trajectories are continuous (no large jumps)."""
        trajectory = self.renderer.generate_trajectory(
            self.renderer.lorenz,
            [1.0, 1.0, 1.0],
            t_span=(0, 20),
            dt=0.01
        )

        # Calculate step sizes
        steps = np.diff(trajectory, axis=0)
        step_sizes = np.linalg.norm(steps, axis=1)

        # With dt=0.01, steps should be small
        self.assertLess(np.max(step_sizes), 2.0)
        self.assertGreater(np.mean(step_sizes), 0.0)

    def test_trajectory_boundedness_lorenz(self):
        """Test that Lorenz trajectories remain bounded."""
        trajectory = self.renderer.generate_trajectory(
            self.renderer.lorenz,
            [1.0, 1.0, 1.0],
            t_span=(0, 50),
            dt=0.01
        )

        # Lorenz attractor is bounded (roughly within [-20, 20] for x,y and [0, 50] for z)
        self.assertTrue(np.all(np.abs(trajectory[:, 0]) < 30))
        self.assertTrue(np.all(np.abs(trajectory[:, 1]) < 30))
        self.assertTrue(np.all(trajectory[:, 2] >= 0))
        self.assertTrue(np.all(trajectory[:, 2] < 60))

    def test_trajectory_boundedness_thomas(self):
        """Test that Thomas trajectories remain bounded."""
        trajectory = self.renderer.generate_trajectory(
            self.renderer.thomas,
            [0.1, 0.0, 0.0],
            t_span=(0, 100),
            dt=0.02
        )

        # Thomas attractor is bounded (roughly within [-5, 5] for all coordinates)
        self.assertTrue(np.all(np.abs(trajectory) < 10))

    def test_custom_colormap_styles(self):
        """Test that all colormap styles can be created."""
        styles = ['gradient', 'fire', 'ice', 'monochrome', 'rainbow', 'unknown']

        for style in styles:
            cmap = self.renderer.create_custom_colormap(style)
            self.assertIsNotNone(cmap)

            # Test that colormap can be evaluated
            colors = cmap(np.linspace(0, 1, 10))
            self.assertEqual(colors.shape, (10, 4))  # RGBA

    def test_colormap_gradient_properties(self):
        """Test that colormaps produce smooth gradients."""
        cmap = self.renderer.create_custom_colormap('gradient')

        # Sample colormap at multiple points
        values = np.linspace(0, 1, 100)
        colors = cmap(values)

        # Colors should change smoothly (no large jumps)
        color_diffs = np.diff(colors[:, :3], axis=0)  # Ignore alpha channel
        max_diff = np.max(np.abs(color_diffs))

        # No single step should change by more than ~0.1 in RGB space
        self.assertLess(max_diff, 0.15)

    def test_render_single_attractor_creates_figure(self):
        """Test that render_single_attractor creates a figure."""
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend

        trajectory = self.renderer.generate_trajectory(
            self.renderer.lorenz,
            [1.0, 1.0, 1.0],
            t_span=(0, 10),
            dt=0.1
        )

        fig = self.renderer.render_single_attractor(
            trajectory,
            'Test Attractor',
            color_style='gradient',
            elevation=20,
            azimuth=45,
            alpha_fade=True
        )

        self.assertIsNotNone(fig)
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_render_with_different_alpha_modes(self):
        """Test rendering with and without alpha fading."""
        import matplotlib
        matplotlib.use('Agg')

        trajectory = self.renderer.generate_trajectory(
            self.renderer.lorenz,
            [1.0, 1.0, 1.0],
            t_span=(0, 10),
            dt=0.1
        )

        # With alpha fade
        fig1 = self.renderer.render_single_attractor(
            trajectory, 'Test 1', alpha_fade=True
        )
        self.assertIsNotNone(fig1)

        # Without alpha fade
        fig2 = self.renderer.render_single_attractor(
            trajectory, 'Test 2', alpha_fade=False
        )
        self.assertIsNotNone(fig2)

        import matplotlib.pyplot as plt
        plt.close(fig1)
        plt.close(fig2)

    def test_triptych_rendering(self):
        """Test that triptych rendering completes without error."""
        import matplotlib
        matplotlib.use('Agg')

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, 'test_triptych.png')
            self.renderer.render_triptych(save_path)

            # Check that file was created
            self.assertTrue(os.path.exists(save_path))
            self.assertGreater(os.path.getsize(save_path), 1000)  # Non-trivial size

    def test_multi_perspective_rendering(self):
        """Test that multi-perspective rendering works for all systems."""
        import matplotlib
        matplotlib.use('Agg')

        systems = ['lorenz', 'rossler', 'thomas']

        with tempfile.TemporaryDirectory() as tmpdir:
            for system in systems:
                save_path = os.path.join(tmpdir, f'test_{system}.png')
                self.renderer.render_multi_perspective(system, save_path)

                # Check that file was created
                self.assertTrue(os.path.exists(save_path))
                self.assertGreater(os.path.getsize(save_path), 1000)

    def test_high_res_rendering(self):
        """Test high-resolution single attractor rendering."""
        import matplotlib
        matplotlib.use('Agg')

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, 'test_highres.png')
            self.renderer.render_high_res_single('lorenz', 'fire', save_path)

            # Check that file was created
            self.assertTrue(os.path.exists(save_path))
            self.assertGreater(os.path.getsize(save_path), 1000)

    def test_sensitive_dependence(self):
        """Test that nearby initial conditions diverge (butterfly effect)."""
        # Two very close initial conditions
        ic1 = [1.0, 1.0, 1.0]
        ic2 = [1.0 + 1e-8, 1.0, 1.0]

        traj1 = self.renderer.generate_trajectory(
            self.renderer.lorenz,
            ic1,
            t_span=(0, 20),
            dt=0.01
        )

        traj2 = self.renderer.generate_trajectory(
            self.renderer.lorenz,
            ic2,
            t_span=(0, 20),
            dt=0.01
        )

        # Calculate divergence over time
        distances = np.linalg.norm(traj1 - traj2, axis=1)

        # Should start very small
        self.assertLess(distances[0], 1e-7)

        # Should grow substantially (divergence)
        self.assertGreater(distances[-1], 1.0)

        # Should show exponential growth (increasing distances)
        self.assertGreater(distances[-1], distances[len(distances)//2])


class TestGalleryCreation(unittest.TestCase):
    """Test the gallery creation function."""

    def test_create_gallery_runs(self):
        """Test that create_gallery completes without error."""
        import matplotlib
        matplotlib.use('Agg')

        from art_gallery import create_gallery

        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory so files are created there
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                create_gallery()

                # Check that expected files exist
                expected_files = [
                    'attractor_triptych.png',
                    'lorenz_perspectives.png',
                    'lorenz_highres.png',
                    'rossler_highres.png',
                    'thomas_highres.png'
                ]

                for filename in expected_files:
                    self.assertTrue(os.path.exists(filename))
                    self.assertGreater(os.path.getsize(filename), 1000)
            finally:
                os.chdir(original_dir)


def run_tests():
    """Run all tests and print results."""
    # Run with verbosity
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
