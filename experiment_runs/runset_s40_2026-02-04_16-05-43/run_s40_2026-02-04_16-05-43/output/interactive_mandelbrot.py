#!/usr/bin/env python3
"""
Interactive Mandelbrot Set Explorer
Created by Alice & Bob - A collaborative Claude Code project

Features:
- Click to zoom in/out on any point
- Real-time coordinate display
- Educational information about the mathematics
- Beautiful gradient visualization

Controls:
- Left click: Zoom in (2x)
- Right click: Zoom out (2x)
- Mouse hover: Shows coordinates and iteration count
- Press 'r': Reset to full view
- Press 'j': Switch to Julia set mode (coming soon!)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as patches


class InteractiveMandelbrot:
    def __init__(self, width=800, height=600, max_iter=80):
        self.width = width
        self.height = height
        self.max_iter = max_iter

        # Initial view parameters
        self.reset_view()

        # Set up the plot
        self.fig, self.ax = plt.subplots(figsize=(12, 9))
        self.fig.suptitle('Interactive Mandelbrot Set Explorer', fontsize=16)

        # Generate and display initial fractal
        self.update_fractal()

        # Set up interactivity
        self.setup_events()

        # Add educational info panel
        self.add_info_panel()

    def reset_view(self):
        """Reset to the classic full Mandelbrot view"""
        self.x_min, self.x_max = -2.5, 1.0
        self.y_min, self.y_max = -1.25, 1.25
        self.zoom_level = 1.0

    def mandelbrot_set(self):
        """Generate the Mandelbrot set for current view"""
        # Create coordinate arrays
        x = np.linspace(self.x_min, self.x_max, self.width)
        y = np.linspace(self.y_min, self.y_max, self.height)
        X, Y = np.meshgrid(x, y)

        # Complex plane
        C = X + 1j * Y

        # Initialize Z and iteration counter
        Z = np.zeros_like(C)
        iterations = np.zeros(C.shape, dtype=int)

        # Vectorized iteration
        for i in range(self.max_iter):
            # Find points that haven't escaped
            mask = np.abs(Z) <= 2

            # Update Z for non-escaped points
            Z[mask] = Z[mask]**2 + C[mask]

            # Update iteration count
            iterations[mask] = i

        return iterations

    def update_fractal(self):
        """Regenerate and display the fractal"""
        print(f"Generating fractal... Zoom: {self.zoom_level:.2f}x")

        # Generate the fractal
        fractal = self.mandelbrot_set()

        # Clear and redraw
        self.ax.clear()

        # Create beautiful colormap
        im = self.ax.imshow(fractal, extent=[self.x_min, self.x_max, self.y_min, self.y_max],
                           cmap='hot', origin='lower', interpolation='bilinear')

        # Customize appearance
        self.ax.set_xlabel('Real axis', fontsize=12)
        self.ax.set_ylabel('Imaginary axis', fontsize=12)
        self.ax.set_title(f'Zoom: {self.zoom_level:.2f}x | Region: [{self.x_min:.6f}, {self.x_max:.6f}] + [{self.y_min:.6f}, {self.y_max:.6f}]i',
                         fontsize=10)

        # Add colorbar if it doesn't exist
        if not hasattr(self, 'colorbar'):
            self.colorbar = self.fig.colorbar(im, ax=self.ax, label='Iterations to escape')
        else:
            self.colorbar.update_normal(im)

        self.fig.canvas.draw()

    def setup_events(self):
        """Connect mouse and keyboard event handlers"""
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        # Store mouse position for coordinate display
        self.current_mouse_pos = None

    def on_click(self, event):
        """Handle mouse clicks for zooming"""
        if event.inaxes != self.ax:
            return

        # Get click coordinates
        click_x, click_y = event.xdata, event.ydata
        if click_x is None or click_y is None:
            return

        # Calculate current view dimensions
        width_span = self.x_max - self.x_min
        height_span = self.y_max - self.y_min

        if event.button == 1:  # Left click - zoom in
            zoom_factor = 0.5
            self.zoom_level *= 2
            print(f"Zooming IN at ({click_x:.6f}, {click_y:.6f}i)")
        elif event.button == 3:  # Right click - zoom out
            zoom_factor = 2.0
            self.zoom_level /= 2
            print(f"Zooming OUT at ({click_x:.6f}, {click_y:.6f}i)")
        else:
            return

        # Calculate new bounds centered on click point
        new_width = width_span * zoom_factor
        new_height = height_span * zoom_factor

        self.x_min = click_x - new_width / 2
        self.x_max = click_x + new_width / 2
        self.y_min = click_y - new_height / 2
        self.y_max = click_y + new_height / 2

        # Regenerate the fractal
        self.update_fractal()

    def on_mouse_move(self, event):
        """Handle mouse movement for coordinate display"""
        if event.inaxes != self.ax:
            return

        self.current_mouse_pos = (event.xdata, event.ydata)

        # Update coordinate display in the info panel
        if hasattr(self, 'coord_text'):
            x, y = event.xdata, event.ydata

            # Calculate what iteration this point would have
            c = complex(x, y)
            z = 0
            iter_count = 0
            for i in range(self.max_iter):
                if abs(z) > 2:
                    break
                z = z**2 + c
                iter_count = i

            coord_info = f"Coordinates: {x:.6f} + {y:.6f}i\nIterations: {iter_count}/{self.max_iter}"
            if iter_count == self.max_iter - 1:
                coord_info += "\n(Likely in set)"

            self.coord_text.set_text(coord_info)
            self.fig.canvas.draw_idle()

    def on_key_press(self, event):
        """Handle keyboard shortcuts"""
        if event.key == 'r':
            print("Resetting to full view...")
            self.reset_view()
            self.update_fractal()
        elif event.key == 'j':
            print("Julia set mode coming soon!")
        elif event.key == 'h':
            self.show_help()

    def add_info_panel(self):
        """Add educational information panel"""
        # Add text box for coordinates and information
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)

        info_text = """Interactive Mandelbrot Explorer

Left click: Zoom in
Right click: Zoom out
'r': Reset view
'h': Show help

Mathematical formula:
z = z² + c
        """

        self.info_text = self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes,
                                     fontsize=9, verticalalignment='top', bbox=props)

        # Coordinate display
        self.coord_text = self.ax.text(0.98, 0.98, "Move mouse to see coordinates",
                                      transform=self.ax.transAxes, fontsize=9,
                                      verticalalignment='top', horizontalalignment='right',
                                      bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

    def show_help(self):
        """Display help information"""
        help_text = """
        🌀 MANDELBROT SET EXPLORER 🌀

        CONTROLS:
        • Left click: Zoom in 2x at point
        • Right click: Zoom out 2x
        • 'r': Reset to full view
        • 'j': Julia set mode (coming soon!)
        • 'h': Show this help

        WHAT YOU'RE SEEING:
        • Black/dark areas: Points in the Mandelbrot set
        • Colored areas: Points that escape to infinity
        • Color intensity: How quickly points escape

        MATHEMATICAL BEAUTY:
        The Mandelbrot set is defined by the simple formula:
        z = z² + c

        For each point c in the complex plane, we iterate
        this formula starting with z=0. Points that don't
        escape to infinity belong to the set!

        Happy exploring! 🔍✨
        """
        print(help_text)

    def run(self):
        """Start the interactive explorer"""
        print("🌀 Starting Interactive Mandelbrot Explorer! 🌀")
        print("Left click to zoom in, right click to zoom out")
        print("Press 'h' for help, 'r' to reset view")
        plt.show()


if __name__ == "__main__":
    explorer = InteractiveMandelbrot(width=800, height=600, max_iter=100)
    explorer.run()