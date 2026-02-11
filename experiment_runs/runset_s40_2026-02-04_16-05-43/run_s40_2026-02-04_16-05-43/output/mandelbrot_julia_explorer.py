#!/usr/bin/env python3
"""
Interactive Mandelbrot & Julia Set Explorer
Created by Alice & Bob - A collaborative Claude Code project

Features:
- Explore the Mandelbrot set with click-to-zoom
- Switch to Julia set mode and use Mandelbrot points as parameters
- Real-time coordinate display and mathematical education
- Beautiful gradient visualization
- Seamless switching between the two related fractals

Controls:
- Left click: Zoom in (2x) or select Julia parameter
- Right click: Zoom out (2x)
- Mouse hover: Shows coordinates and iteration count
- Press 'r': Reset to full view
- Press 'j': Toggle between Mandelbrot and Julia modes
- Press 'h': Show help
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as patches


class MandelbrotJuliaExplorer:
    def __init__(self, width=800, height=600, max_iter=80):
        self.width = width
        self.height = height
        self.max_iter = max_iter

        # Mode tracking
        self.mode = 'mandelbrot'  # 'mandelbrot' or 'julia'
        self.julia_c = complex(-0.7, 0.27015)  # Default Julia parameter

        # Initial view parameters
        self.reset_view()

        # Set up the plot
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.setup_plot()

        # Generate and display initial fractal
        self.update_fractal()

        # Set up interactivity
        self.setup_events()

        # Add educational info panel
        self.add_info_panel()

    def setup_plot(self):
        """Setup the main plot with dynamic title"""
        if self.mode == 'mandelbrot':
            title = 'Interactive Mandelbrot Set Explorer'
        else:
            title = f'Julia Set Explorer (c = {self.julia_c:.6f})'
        self.fig.suptitle(title, fontsize=16)

    def reset_view(self):
        """Reset to appropriate full view based on current mode"""
        if self.mode == 'mandelbrot':
            self.x_min, self.x_max = -2.5, 1.0
            self.y_min, self.y_max = -1.25, 1.25
        else:  # julia mode
            self.x_min, self.x_max = -2.0, 2.0
            self.y_min, self.y_max = -2.0, 2.0
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

    def julia_set(self, c):
        """Generate a Julia set for the given parameter c"""
        # Create coordinate arrays
        x = np.linspace(self.x_min, self.x_max, self.width)
        y = np.linspace(self.y_min, self.y_max, self.height)
        X, Y = np.meshgrid(x, y)

        # Complex plane - for Julia set, this is our initial Z
        Z = X + 1j * Y
        iterations = np.zeros(Z.shape, dtype=int)

        # Vectorized iteration
        for i in range(self.max_iter):
            # Find points that haven't escaped
            mask = np.abs(Z) <= 2

            # Update Z for non-escaped points: z = z² + c
            Z[mask] = Z[mask]**2 + c

            # Update iteration count
            iterations[mask] = i

        return iterations

    def update_fractal(self):
        """Regenerate and display the fractal based on current mode"""
        if self.mode == 'mandelbrot':
            print(f"Generating Mandelbrot set... Zoom: {self.zoom_level:.2f}x")
            fractal = self.mandelbrot_set()
            colormap = 'hot'
        else:
            print(f"Generating Julia set (c = {self.julia_c:.6f})... Zoom: {self.zoom_level:.2f}x")
            fractal = self.julia_set(self.julia_c)
            colormap = 'plasma'  # Different colormap for Julia sets

        # Clear and redraw
        self.ax.clear()

        # Create beautiful visualization
        im = self.ax.imshow(fractal, extent=[self.x_min, self.x_max, self.y_min, self.y_max],
                           cmap=colormap, origin='lower', interpolation='bilinear')

        # Customize appearance
        self.ax.set_xlabel('Real axis', fontsize=12)
        self.ax.set_ylabel('Imaginary axis', fontsize=12)

        if self.mode == 'mandelbrot':
            subtitle = f'Mandelbrot Set | Zoom: {self.zoom_level:.2f}x'
        else:
            subtitle = f'Julia Set (c = {self.julia_c:.6f}) | Zoom: {self.zoom_level:.2f}x'

        region_info = f'Region: [{self.x_min:.6f}, {self.x_max:.6f}] + [{self.y_min:.6f}, {self.y_max:.6f}]i'
        self.ax.set_title(f'{subtitle}\n{region_info}', fontsize=10)

        # Update colorbar
        if not hasattr(self, 'colorbar') or self.colorbar is None:
            self.colorbar = self.fig.colorbar(im, ax=self.ax, label='Iterations to escape')
        else:
            self.colorbar.update_normal(im)

        # Update the figure title
        self.setup_plot()

        # Re-add info panel
        self.add_info_panel()

        self.fig.canvas.draw()

    def setup_events(self):
        """Connect mouse and keyboard event handlers"""
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        # Store mouse position for coordinate display
        self.current_mouse_pos = None

    def on_click(self, event):
        """Handle mouse clicks for zooming or Julia parameter selection"""
        if event.inaxes != self.ax:
            return

        # Get click coordinates
        click_x, click_y = event.xdata, event.ydata
        if click_x is None or click_y is None:
            return

        click_point = complex(click_x, click_y)

        if self.mode == 'mandelbrot':
            if event.button == 1:  # Left click in Mandelbrot mode
                # Show what this would look like as a Julia set parameter
                print(f"📍 Selected point: {click_point:.6f}")
                print(f"   This point would create a Julia set with c = {click_point:.6f}")
                print("   Press 'j' to switch to Julia mode with this parameter!")

                # Store this as potential Julia parameter
                self.potential_julia_c = click_point

                # Also zoom in normally
                self.zoom_at_point(click_x, click_y, zoom_in=True)
            elif event.button == 3:  # Right click - zoom out
                self.zoom_at_point(click_x, click_y, zoom_in=False)

        else:  # Julia mode
            if event.button == 1:  # Left click - zoom in
                self.zoom_at_point(click_x, click_y, zoom_in=True)
            elif event.button == 3:  # Right click - zoom out
                self.zoom_at_point(click_x, click_y, zoom_in=False)

    def zoom_at_point(self, click_x, click_y, zoom_in=True):
        """Handle zooming at a specific point"""
        # Calculate current view dimensions
        width_span = self.x_max - self.x_min
        height_span = self.y_max - self.y_min

        if zoom_in:
            zoom_factor = 0.5
            self.zoom_level *= 2
            print(f"🔍 Zooming IN at ({click_x:.6f}, {click_y:.6f}i)")
        else:
            zoom_factor = 2.0
            self.zoom_level /= 2
            print(f"🔍 Zooming OUT at ({click_x:.6f}, {click_y:.6f}i)")

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

            if self.mode == 'mandelbrot':
                # Mandelbrot iteration: z starts at 0, iterate z = z² + c
                z = 0
                iter_count = 0
                for i in range(self.max_iter):
                    if abs(z) > 2:
                        break
                    z = z**2 + c
                    iter_count = i

                coord_info = f"Point: {x:.6f} + {y:.6f}i\nMandelbrot iterations: {iter_count}/{self.max_iter}"
                if iter_count == self.max_iter - 1:
                    coord_info += "\n(Likely in Mandelbrot set)"
                coord_info += f"\n\nClick to use as Julia parameter:\nc = {c:.6f}"

            else:  # Julia mode
                # Julia iteration: z starts at this point, iterate z = z² + julia_c
                z = c
                iter_count = 0
                for i in range(self.max_iter):
                    if abs(z) > 2:
                        break
                    z = z**2 + self.julia_c
                    iter_count = i

                coord_info = f"Point: {x:.6f} + {y:.6f}i\nJulia iterations: {iter_count}/{self.max_iter}"
                if iter_count == self.max_iter - 1:
                    coord_info += "\n(Likely in Julia set)"
                coord_info += f"\n\nJulia parameter: c = {self.julia_c:.6f}"

            self.coord_text.set_text(coord_info)
            self.fig.canvas.draw_idle()

    def on_key_press(self, event):
        """Handle keyboard shortcuts"""
        if event.key == 'r':
            print("🔄 Resetting to full view...")
            self.reset_view()
            self.update_fractal()

        elif event.key == 'j':
            # Toggle mode
            if self.mode == 'mandelbrot':
                # Switch to Julia mode
                if hasattr(self, 'potential_julia_c'):
                    self.julia_c = self.potential_julia_c
                    print(f"🌀 Switching to Julia set mode with c = {self.julia_c:.6f}")
                else:
                    print(f"🌀 Switching to Julia set mode with default c = {self.julia_c:.6f}")
                self.mode = 'julia'
            else:
                # Switch to Mandelbrot mode
                print("🌀 Switching to Mandelbrot set mode")
                self.mode = 'mandelbrot'

            self.reset_view()
            self.update_fractal()

        elif event.key == 'h':
            self.show_help()

    def add_info_panel(self):
        """Add educational information panel"""
        # Add text box for coordinates and information
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)

        if self.mode == 'mandelbrot':
            info_text = """🌀 Mandelbrot Explorer

Left click: Zoom in + Select Julia param
Right click: Zoom out
'j': Switch to Julia mode
'r': Reset view | 'h': Help

Formula: z = z² + c
(z starts at 0)
            """
        else:
            info_text = f"""🌀 Julia Set Explorer

c = {self.julia_c:.6f}

Left click: Zoom in
Right click: Zoom out
'j': Switch to Mandelbrot
'r': Reset view | 'h': Help

Formula: z = z² + c
(z starts at each point)
            """

        self.info_text = self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes,
                                     fontsize=9, verticalalignment='top', bbox=props)

        # Coordinate display
        self.coord_text = self.ax.text(0.98, 0.98, "Move mouse to see coordinates",
                                      transform=self.ax.transAxes, fontsize=9,
                                      verticalalignment='top', horizontalalignment='right',
                                      bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9))

    def show_help(self):
        """Display comprehensive help information"""
        help_text = """
        🌀 MANDELBROT & JULIA SET EXPLORER 🌀

        CONTROLS:
        • Left click: Zoom in 2x (+ select Julia parameter in Mandelbrot mode)
        • Right click: Zoom out 2x
        • 'j': Toggle between Mandelbrot and Julia set modes
        • 'r': Reset to full view
        • 'h': Show this help

        THE CONNECTION:
        • Mandelbrot set: Shows which values of 'c' create bounded Julia sets
        • Julia sets: For each 'c', shows which starting points 'z' stay bounded
        • Click on any Mandelbrot point to use it as a Julia set parameter!

        MATHEMATICAL BEAUTY:
        Both sets use the same formula: z = z² + c

        • Mandelbrot: z starts at 0, c varies (what you click on)
        • Julia: c is fixed, z starts at different points

        WHAT THE COLORS MEAN:
        • Dark areas: Points that stay bounded (in the set)
        • Bright colors: Points that escape to infinity
        • Color intensity: How quickly points escape

        This connection between the sets is one of the most beautiful
        discoveries in mathematics!

        Happy exploring! 🔍✨
        """
        print(help_text)

    def run(self):
        """Start the interactive explorer"""
        print("🌀✨ Starting Mandelbrot & Julia Set Explorer! ✨🌀")
        print()
        print("🔍 CONTROLS:")
        print("   Left click: Zoom in (and select Julia parameters)")
        print("   Right click: Zoom out")
        print("   'j': Toggle between Mandelbrot ⟷ Julia modes")
        print("   'r': Reset view")
        print("   'h': Show detailed help")
        print()
        print("🌟 THE MAGIC:")
        print("   Click any point in the Mandelbrot set, then press 'j'")
        print("   to see the corresponding Julia set!")
        print()
        plt.show()


if __name__ == "__main__":
    explorer = MandelbrotJuliaExplorer(width=800, height=600, max_iter=100)
    explorer.run()