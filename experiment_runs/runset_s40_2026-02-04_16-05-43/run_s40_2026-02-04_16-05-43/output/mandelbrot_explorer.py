#!/usr/bin/env python3
"""
Mandelbrot Set Explorer
A collaborative project by Alice and Bob

This module generates and visualizes the Mandelbrot set using NumPy for performance
and matplotlib for visualization. The core algorithm iterates z = z² + c for each
point in the complex plane to determine set membership.

Mathematical Foundation:
- For each complex number c, iterate z_{n+1} = z_n² + c with z_0 = 0
- If |z_n| > 2, the point escapes to infinity (not in the set)
- Points that don't escape (or take many iterations) belong to the set

Author: Alice & Bob (Claude Code collaborative session)
Date: 2026-02-04
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import time
from typing import Tuple, Optional


class MandelbrotExplorer:
    """
    A class for generating and visualizing the Mandelbrot set with various
    optimization techniques and visualization options.
    """

    def __init__(self, width: int = 800, height: int = 600, max_iter: int = 100):
        """
        Initialize the Mandelbrot explorer.

        Args:
            width: Width of the output image in pixels
            height: Height of the output image in pixels
            max_iter: Maximum number of iterations before assuming convergence
        """
        self.width = width
        self.height = height
        self.max_iter = max_iter

        # Default viewing window (can be modified for zoom)
        self.x_min, self.x_max = -2.5, 1.5
        self.y_min, self.y_max = -1.5, 1.5

        # Create custom colormap for beautiful visualization
        self.setup_colormap()

    def setup_colormap(self):
        """Create a custom colormap for visualizing escape times."""
        colors = ['#000428', '#004e92', '#009ffd', '#00d2ff', '#ffffff']
        n_bins = 256
        self.cmap = LinearSegmentedColormap.from_list('mandelbrot', colors, N=n_bins)

    def mandelbrot_set_vectorized(self) -> np.ndarray:
        """
        Generate the Mandelbrot set using vectorized NumPy operations.

        This is significantly faster than naive Python loops for large arrays.

        Returns:
            2D array where each element represents the escape time for that point
        """
        # Create coordinate arrays
        x = np.linspace(self.x_min, self.x_max, self.width)
        y = np.linspace(self.y_min, self.y_max, self.height)
        X, Y = np.meshgrid(x, y)

        # Complex plane coordinates
        c = X + 1j * Y
        z = np.zeros_like(c)

        # Track escape times
        escape_times = np.zeros(c.shape, dtype=int)

        for i in range(self.max_iter):
            # Find points that haven't escaped yet
            mask = np.abs(z) <= 2

            # Update z for non-escaped points: z = z² + c
            z[mask] = z[mask]**2 + c[mask]

            # Update escape times
            escape_times[mask] = i

        return escape_times

    def set_view_window(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """
        Set the viewing window for zooming into specific regions.

        Args:
            x_min, x_max: Real axis bounds
            y_min, y_max: Imaginary axis bounds
        """
        self.x_min, self.x_max = x_min, x_max
        self.y_min, self.y_max = y_min, y_max

    def generate_and_plot(self, save_path: Optional[str] = None, show_plot: bool = True) -> np.ndarray:
        """
        Generate the Mandelbrot set and create a visualization.

        Args:
            save_path: Optional path to save the image
            show_plot: Whether to display the plot interactively

        Returns:
            The escape time array
        """
        print(f"Generating Mandelbrot set ({self.width}x{self.height}, max_iter={self.max_iter})")
        print(f"View window: [{self.x_min:.3f}, {self.x_max:.3f}] × [{self.y_min:.3f}, {self.y_max:.3f}]")

        start_time = time.time()
        escape_times = self.mandelbrot_set_vectorized()
        generation_time = time.time() - start_time

        print(f"Generation completed in {generation_time:.2f} seconds")

        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 9))

        # Display the fractal
        im = ax.imshow(escape_times, extent=[self.x_min, self.x_max, self.y_min, self.y_max],
                      cmap=self.cmap, origin='lower', interpolation='bilinear')

        # Formatting
        ax.set_title('Mandelbrot Set Explorer\n' +
                    f'View: [{self.x_min:.3f}, {self.x_max:.3f}] × [{self.y_min:.3f}, {self.y_max:.3f}]',
                    fontsize=14, pad=20)
        ax.set_xlabel('Real axis', fontsize=12)
        ax.set_ylabel('Imaginary axis', fontsize=12)

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Escape time (iterations)', fontsize=10)

        # Add grid for reference
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved to: {save_path}")

        if show_plot:
            plt.show()

        return escape_times


def main():
    """Demo function showing various views of the Mandelbrot set."""
    explorer = MandelbrotExplorer(width=1000, height=800, max_iter=150)

    # Generate the classic full view
    print("=== Classic Mandelbrot Set View ===")
    explorer.generate_and_plot(save_path="/tmp/cc-exp/run_s40_2026-02-04_16-05-43/output/mandelbrot_classic.png",
                              show_plot=False)

    # Zoom into an interesting region (the "seahorse valley")
    print("\n=== Zoomed View: Seahorse Valley ===")
    explorer.set_view_window(-0.75, -0.73, 0.1, 0.12)
    explorer.max_iter = 200  # More iterations for detailed zoom
    explorer.generate_and_plot(save_path="/tmp/cc-exp/run_s40_2026-02-04_16-05-43/output/mandelbrot_seahorse.png",
                              show_plot=False)

    # Another interesting zoom (mini Mandelbrot)
    print("\n=== Zoomed View: Mini Mandelbrot ===")
    explorer.set_view_window(-0.16, -0.14, 1.03, 1.05)
    explorer.max_iter = 250
    explorer.generate_and_plot(save_path="/tmp/cc-exp/run_s40_2026-02-04_16-05-43/output/mandelbrot_mini.png",
                              show_plot=False)


if __name__ == "__main__":
    main()