#!/usr/bin/env python3
"""
🌀✨ ANIMATED FRACTAL EXPLORER ✨🌀
Advanced Mandelbrot & Julia Set Explorer with Real-time Animation

Features:
- Interactive Mandelbrot/Julia exploration
- Real-time Julia parameter animation
- Smooth transitions between fractal types
- Mathematical education with live feedback
- Beautiful color palettes and smooth animations

Created by: Alice & Bob, Claude Code Collaboration
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import time

class AnimatedFractalExplorer:
    def __init__(self, width=800, height=600, max_iter=100):
        self.width = width
        self.height = height
        self.max_iter = max_iter
        self.zoom_level = 1.0
        self.center_x, self.center_y = 0.0, 0.0
        self.julia_c = complex(-0.8, 0.156)  # Beautiful starting parameter
        self.mode = 'mandelbrot'  # 'mandelbrot' or 'julia'
        self.is_animating = False
        self.animation_obj = None
        self.frame_count = 0

        # Animation parameters
        self.animation_speed = 0.02
        self.animation_radius = 0.3
        self.animation_center = complex(-0.7, 0.1)

        self.setup_plot()
        self.setup_controls()
        self.render_fractal()

    def setup_plot(self):
        """Initialize the matplotlib figure and axes"""
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        # Create space for buttons at bottom
        plt.subplots_adjust(bottom=0.15)

        # Status text
        self.status_text = self.fig.text(0.02, 0.95, '', fontsize=10,
                                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        self.coord_text = self.fig.text(0.02, 0.88, '', fontsize=9,
                                      bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"))

        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def setup_controls(self):
        """Create interactive control buttons"""
        # Button positions
        button_height = 0.04
        button_width = 0.12
        y_pos = 0.05

        # Mode toggle button
        ax_mode = plt.axes([0.1, y_pos, button_width, button_height])
        self.mode_button = Button(ax_mode, 'Julia Mode')
        self.mode_button.on_clicked(self.toggle_mode)

        # Animation toggle button
        ax_anim = plt.axes([0.25, y_pos, button_width, button_height])
        self.anim_button = Button(ax_anim, 'Start Animation')
        self.anim_button.on_clicked(self.toggle_animation)

        # Reset button
        ax_reset = plt.axes([0.4, y_pos, button_width, button_height])
        self.reset_button = Button(ax_reset, 'Reset View')
        self.reset_button.on_clicked(self.reset_view)

        # Quality button
        ax_quality = plt.axes([0.55, y_pos, button_width, button_height])
        self.quality_button = Button(ax_quality, 'High Quality')
        self.quality_button.on_clicked(self.toggle_quality)

    def mandelbrot_set(self, h, w, max_iter, x_min, x_max, y_min, y_max):
        """Generate Mandelbrot set using vectorized NumPy operations"""
        # Create coordinate arrays
        x = np.linspace(x_min, x_max, w)
        y = np.linspace(y_min, y_max, h)
        X, Y = np.meshgrid(x, y)
        c = X + 1j * Y

        # Initialize arrays
        z = np.zeros_like(c)
        escape_count = np.zeros(c.shape, dtype=int)

        # Iterate the Mandelbrot formula
        for i in range(max_iter):
            mask = np.abs(z) <= 2
            z[mask] = z[mask]**2 + c[mask]
            escape_count[mask] = i

        return escape_count

    def julia_set(self, h, w, max_iter, x_min, x_max, y_min, y_max, c):
        """Generate Julia set for parameter c"""
        # Create coordinate arrays
        x = np.linspace(x_min, x_max, w)
        y = np.linspace(y_min, y_max, h)
        X, Y = np.meshgrid(x, y)
        z = X + 1j * Y

        # Initialize arrays
        escape_count = np.zeros(z.shape, dtype=int)

        # Iterate the Julia formula
        for i in range(max_iter):
            mask = np.abs(z) <= 2
            z[mask] = z[mask]**2 + c
            escape_count[mask] = i

        return escape_count

    def get_viewport(self):
        """Calculate current viewport bounds"""
        aspect_ratio = self.height / self.width
        half_width = 2.0 / self.zoom_level
        half_height = half_width * aspect_ratio

        x_min = self.center_x - half_width
        x_max = self.center_x + half_width
        y_min = self.center_y - half_height
        y_max = self.center_y + half_height

        return x_min, x_max, y_min, y_max

    def render_fractal(self):
        """Render the current fractal"""
        print(f"Rendering {self.mode} set... Zoom: {self.zoom_level:.2f}x")
        start_time = time.time()

        x_min, x_max, y_min, y_max = self.get_viewport()

        if self.mode == 'mandelbrot':
            data = self.mandelbrot_set(self.height, self.width, self.max_iter,
                                     x_min, x_max, y_min, y_max)
            colormap = 'hot'
            title = f"🌀 Mandelbrot Set - Zoom: {self.zoom_level:.2f}x"
        else:
            data = self.julia_set(self.height, self.width, self.max_iter,
                                x_min, x_max, y_min, y_max, self.julia_c)
            colormap = 'plasma'
            title = f"✨ Julia Set (c = {self.julia_c:.3f}) - Zoom: {self.zoom_level:.2f}x"

        # Clear and redraw
        self.ax.clear()
        self.ax.imshow(data, extent=[x_min, x_max, y_min, y_max],
                      cmap=colormap, origin='lower', interpolation='bilinear')
        self.ax.set_title(title, fontsize=14, pad=20)
        self.ax.axis('off')

        # Update status
        render_time = time.time() - start_time
        self.status_text.set_text(f"🎯 Mode: {self.mode.title()} | "
                                f"⚡ Rendered in {render_time:.2f}s | "
                                f"🔍 Iterations: {self.max_iter}")

        if not self.is_animating:
            self.fig.canvas.draw()

    def animate_julia(self, frame):
        """Animation function for Julia parameters"""
        if not self.is_animating:
            return

        # Create smooth circular motion in complex plane
        angle = frame * self.animation_speed
        self.julia_c = (self.animation_center +
                       self.animation_radius * complex(np.cos(angle), np.sin(angle)))

        # Render the animated Julia set
        self.render_fractal()

        # Update coordinate display
        self.coord_text.set_text(f"🌟 Julia Parameter: c = {self.julia_c:.4f}\n"
                               f"🔄 Animation Frame: {frame}")

    def toggle_animation(self, event):
        """Toggle Julia parameter animation"""
        if not self.is_animating:
            if self.mode != 'julia':
                self.mode = 'julia'
                self.mode_button.label.set_text('Mandelbrot Mode')

            self.is_animating = True
            self.anim_button.label.set_text('Stop Animation')

            # Start animation
            self.animation_obj = animation.FuncAnimation(
                self.fig, self.animate_julia, interval=50, repeat=True)

        else:
            self.is_animating = False
            self.anim_button.label.set_text('Start Animation')

            if self.animation_obj:
                self.animation_obj.event_source.stop()
                self.animation_obj = None

    def toggle_mode(self, event):
        """Toggle between Mandelbrot and Julia modes"""
        if self.is_animating:
            self.toggle_animation(None)  # Stop animation first

        if self.mode == 'mandelbrot':
            self.mode = 'julia'
            self.mode_button.label.set_text('Mandelbrot Mode')
        else:
            self.mode = 'mandelbrot'
            self.mode_button.label.set_text('Julia Mode')

        self.render_fractal()

    def toggle_quality(self, event):
        """Toggle between different quality levels"""
        if self.max_iter == 100:
            self.max_iter = 256
            self.quality_button.label.set_text('Ultra Quality')
        elif self.max_iter == 256:
            self.max_iter = 512
            self.quality_button.label.set_text('Low Quality')
        else:
            self.max_iter = 100
            self.quality_button.label.set_text('High Quality')

        self.render_fractal()

    def reset_view(self, event):
        """Reset to initial view"""
        if self.is_animating:
            self.toggle_animation(None)

        self.zoom_level = 1.0
        self.center_x, self.center_y = 0.0, 0.0
        self.julia_c = complex(-0.8, 0.156)
        self.render_fractal()

    def on_click(self, event):
        """Handle mouse clicks"""
        if event.inaxes != self.ax:
            return

        if event.button == 1:  # Left click - zoom in
            self.center_x = event.xdata
            self.center_y = event.ydata
            self.zoom_level *= 2

            # If in Mandelbrot mode, use click point as Julia parameter
            if self.mode == 'mandelbrot':
                self.julia_c = complex(event.xdata, event.ydata)

            self.render_fractal()

        elif event.button == 3:  # Right click - zoom out
            self.zoom_level /= 2
            self.render_fractal()

    def on_mouse_move(self, event):
        """Handle mouse movement for coordinate display"""
        if event.inaxes != self.ax or self.is_animating:
            return

        if event.xdata is not None and event.ydata is not None:
            c = complex(event.xdata, event.ydata)

            if self.mode == 'mandelbrot':
                # Quick iteration count at mouse position
                z = 0
                for i in range(50):
                    if abs(z) > 2:
                        break
                    z = z**2 + c

                self.coord_text.set_text(f"🎯 Mouse: {c:.4f}\n"
                                       f"⚡ ~{i} iterations to escape\n"
                                       f"💡 Click to zoom & set Julia param")
            else:
                # Show Julia iteration info
                z = c
                for i in range(50):
                    if abs(z) > 2:
                        break
                    z = z**2 + self.julia_c

                self.coord_text.set_text(f"🎯 Point: {c:.4f}\n"
                                       f"🌟 Julia c: {self.julia_c:.4f}\n"
                                       f"⚡ ~{i} iterations to escape")

            self.fig.canvas.draw_idle()

    def on_key_press(self, event):
        """Handle keyboard shortcuts"""
        if event.key == 'j':
            self.toggle_mode(None)
        elif event.key == 'r':
            self.reset_view(None)
        elif event.key == 'a':
            self.toggle_animation(None)
        elif event.key == 'h':
            self.show_help()

    def show_help(self):
        """Display comprehensive help information"""
        help_text = """
🌀✨ ANIMATED FRACTAL EXPLORER HELP ✨🌀

🎮 CONTROLS:
   Left Click: Zoom in (and set Julia parameter)
   Right Click: Zoom out
   'j': Toggle Mandelbrot ⟷ Julia modes
   'r': Reset view
   'a': Start/stop Julia animation
   'h': Show this help

🎯 BUTTONS:
   • Mode Toggle: Switch between fractal types
   • Animation: Watch Julia sets evolve in real-time!
   • Reset View: Return to starting position
   • Quality: Adjust iteration count for speed/detail

🧮 THE MATHEMATICS:
   Both fractals use: z = z² + c
   • Mandelbrot: Fixed z₀=0, vary c across plane
   • Julia: Fixed c, vary z₀ across plane

🌟 ANIMATION MAGIC:
   Watch how smoothly changing the Julia parameter 'c'
   creates flowing, organic transformations in the fractal!

✨ Pro tip: Click interesting Mandelbrot points,
   then switch to Julia mode to see the connection!
        """

        print(help_text)
        self.coord_text.set_text("📖 Help displayed in console!")
        self.fig.canvas.draw_idle()

    def run(self):
        """Start the interactive explorer"""
        print("🌀✨ Starting ANIMATED Fractal Explorer! ✨🌀")
        print("\n🎮 Try the animation feature - it's mesmerizing!")
        print("📖 Press 'h' for comprehensive help\n")

        plt.show()

if __name__ == "__main__":
    explorer = AnimatedFractalExplorer(width=800, height=600, max_iter=100)
    explorer.run()