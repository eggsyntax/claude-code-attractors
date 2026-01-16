# Attractor Visualizer

A comprehensive visualization toolkit for 3D strange attractor trajectories.

## Features

### Core Visualization
- **3D Trajectory Plotting**: Visualize attractor trajectories in 3D space with customizable styling
- **Multiple Trajectory Overlays**: Compare multiple trajectories to demonstrate sensitivity to initial conditions
- **Phase Space Projections**: View 2D projections onto XY, XZ, and YZ planes alongside 3D view
- **Animation Support**: Create animated visualizations showing trajectory evolution over time
- **Attractor Comparison**: Side-by-side comparison of multiple different attractor systems

### Advanced Analysis (NEW!)
- **Poincaré Sections**: Reveal the hidden fractal structure within chaotic attractors
  - 2D section plots with sequence coloring
  - 3D overlay showing section plane and crossing points
  - Side-by-side comparison of multiple sections
- **Bifurcation Diagrams**: Visualize the route to chaos through parameter space
  - Static bifurcation plots
  - Animated bifurcation showing period-doubling cascade
  - Perfect for exploring parameter-dependent behavior

## Quick Start

```python
from visualizer import AttractorVisualizer
import numpy as np

# Create some trajectory data (shape: n_points x 3)
trajectory = np.array([...])  # Your attractor data here

# Initialize visualizer
vis = AttractorVisualizer()

# Plot in 3D
vis.plot_trajectory_3d(
    trajectory,
    title="My Attractor",
    color='blue'
)
```

## API Reference

### AttractorVisualizer Class

#### `__init__(figsize=(12, 9))`
Initialize the visualizer with optional figure size.

#### `plot_trajectory_3d(trajectory, title, labels, color, alpha, linewidth, show)`
Plot a single 3D trajectory.

**Parameters:**
- `trajectory` (np.ndarray): Array of shape (n_points, 3) with [x, y, z] coordinates
- `title` (str): Plot title
- `labels` (tuple): Axis labels as (x_label, y_label, z_label)
- `color` (str): Line color
- `alpha` (float): Line transparency (0-1)
- `linewidth` (float): Line width
- `show` (bool): Whether to display immediately

**Returns:** (Figure, Axes) tuple

#### `plot_multiple_trajectories(trajectories, title, labels, colors, alpha, linewidth, show)`
Plot multiple trajectories on the same axes.

**Parameters:**
- `trajectories` (list): List of trajectory arrays
- `colors` (list, optional): List of colors for each trajectory

Useful for showing how slightly different initial conditions lead to divergent trajectories.

#### `plot_phase_projections(trajectory, title, labels, color, alpha, linewidth, show)`
Create 2x2 grid showing 3D view and three 2D projections.

**Layout:**
```
[3D View]      [XY Projection]
[XZ Projection] [YZ Projection]
```

#### `create_animation(trajectory, title, labels, color, frames, interval, save_path)`
Create animated visualization of trajectory evolution.

**Parameters:**
- `frames` (int): Number of animation frames
- `interval` (int): Delay between frames in milliseconds
- `save_path` (str, optional): Path to save animation (e.g., "output.gif")

**Returns:** matplotlib FuncAnimation object

### Utility Functions

#### `compare_attractors(attractors_data, figsize)`
Compare multiple attractor systems side-by-side.

**Parameters:**
- `attractors_data` (list): List of (trajectory, name) tuples

**Example:**
```python
from visualizer import compare_attractors

attractors = [
    (lorenz_trajectory, "Lorenz"),
    (rossler_trajectory, "Rössler"),
    (aizawa_trajectory, "Aizawa")
]

fig, axes = compare_attractors(attractors)
```

## Usage Examples

### Basic 3D Plot
```python
vis = AttractorVisualizer()
vis.plot_trajectory_3d(
    my_trajectory,
    title="Lorenz Attractor",
    labels=("X", "Y", "Z"),
    color='darkblue',
    alpha=0.7
)
```

### Show Sensitivity to Initial Conditions
```python
# Generate multiple trajectories with slight variations
trajectories = [traj1, traj2, traj3]

vis = AttractorVisualizer()
vis.plot_multiple_trajectories(
    trajectories,
    title="Butterfly Effect Demonstration",
    alpha=0.6
)
```

### Phase Space Analysis
```python
vis = AttractorVisualizer()
vis.plot_phase_projections(
    trajectory,
    title="Phase Space Views",
    color='red'
)
```

### Create Animation
```python
vis = AttractorVisualizer()
anim = vis.create_animation(
    trajectory,
    title="Attractor Evolution",
    frames=200,
    interval=50,
    save_path="attractor.gif"
)
```

## Testing

Run the test suite:
```bash
python test_visualizer.py
```

Run the demo:
```bash
python visualizer_demo.py
```

## Design Philosophy

1. **Clean API**: Simple, intuitive function signatures
2. **Flexibility**: Extensive customization options for colors, styling, labels
3. **Non-destructive**: Input data is never modified
4. **Self-contained**: Each visualization is independent
5. **Well-tested**: Comprehensive unit test coverage

## Integration with Attractor Systems

This visualizer is designed to work seamlessly with the attractor framework:

```python
from lorenz import LorenzAttractor
from visualizer import AttractorVisualizer

# Generate attractor data
lorenz = LorenzAttractor()
trajectory = lorenz.generate_trajectory(t_max=50, dt=0.01)

# Visualize
vis = AttractorVisualizer()
vis.plot_trajectory_3d(trajectory, title="Lorenz Attractor")
vis.plot_phase_projections(trajectory)
```

## Advanced Features

### Poincaré Section Visualization

#### 2D Poincaré Section Plot
```python
vis = AttractorVisualizer()

# Plot section with sequence coloring to reveal spiral structure
vis.plot_poincare_section_2d(
    section_points,
    title="Rössler Poincaré Section at z=0",
    labels=("x", "y"),
    colormap='plasma',  # Colors points by sequence
    markersize=3
)
```

#### 3D Overlay with Section Plane
```python
# Show trajectory with Poincaré section plane and crossing points
vis.plot_poincare_overlay_3d(
    trajectory=full_trajectory,
    section_points=section_points,
    plane='z',
    plane_value=0.0,
    traj_color='blue',
    section_color='red',
    traj_alpha=0.3,
    section_alpha=0.9
)
```

#### Compare Multiple Sections
```python
# Side-by-side comparison of different attractors' sections
sections_data = [
    (lorenz_section, "Lorenz (x=0)"),
    (rossler_section, "Rössler (z=0)")
]

vis.plot_multiple_poincare_sections(
    sections_data,
    title="Section Comparison",
    colormap='viridis'
)
```

### Bifurcation Diagram Visualization

#### Static Bifurcation Diagram
```python
# Visualize period-doubling route to chaos
bifurcation_data = attractor.generate_bifurcation_data(
    param_name='c',
    param_range=(2.0, 8.0),
    n_values=300
)

vis.plot_bifurcation_diagram(
    bifurcation_data,
    title="Rössler Bifurcation (parameter c)",
    xlabel="Parameter c",
    ylabel="z"
)
```

#### Animated Bifurcation
```python
# Watch the period-doubling cascade emerge!
anim = vis.animate_bifurcation(
    bifurcation_data,
    title="Chaos Emerging",
    frames=100,
    interval=100,
    save_path="bifurcation.gif"
)
```

## Complete API Reference

### New Methods (Enhanced Visualizer)

#### `plot_poincare_section_2d(section_points, title, labels, color, alpha, marker, markersize, colormap, show)`
Plot 2D Poincaré section revealing attractor structure.

**Parameters:**
- `section_points` (np.ndarray): Array of shape (n_points, 2) with section coordinates
- `colormap` (str, optional): If provided, colors points by sequence ('viridis', 'plasma', etc.)
- Other parameters similar to 3D plotting

**Returns:** (Figure, Axes) tuple

#### `plot_poincare_overlay_3d(trajectory, section_points, plane, plane_value, title, labels, traj_color, section_color, traj_alpha, section_alpha, show)`
Overlay Poincaré section on 3D trajectory.

**Parameters:**
- `trajectory` (np.ndarray): Full trajectory of shape (n_points, 3)
- `section_points` (np.ndarray): Section points of shape (n_section, 2)
- `plane` (str): Which plane ('x', 'y', or 'z')
- `plane_value` (float): Coordinate value of the section plane
- `traj_color`, `section_color`: Colors for trajectory and section points
- `traj_alpha`, `section_alpha`: Transparency values

**Returns:** (Figure, Axes) tuple

#### `plot_bifurcation_diagram(bifurcation_data, title, xlabel, ylabel, color, alpha, markersize, show)`
Plot bifurcation diagram showing parameter-dependent behavior.

**Parameters:**
- `bifurcation_data` (tuple): (param_values, variable_values) arrays
- Standard plotting parameters

**Returns:** (Figure, Axes) tuple

#### `animate_bifurcation(bifurcation_data, title, xlabel, ylabel, color, frames, interval, save_path)`
Animate bifurcation diagram building up over parameter range.

**Parameters:**
- `frames` (int): Number of animation frames
- `interval` (int): Delay between frames in milliseconds
- `save_path` (str, optional): Path to save animation

**Returns:** matplotlib FuncAnimation object

#### `plot_multiple_poincare_sections(sections_data, title, labels, colormap, show)`
Compare Poincaré sections from multiple attractors.

**Parameters:**
- `sections_data` (list): List of (section_points, name) tuples
- `colormap` (str): Colormap for sequence coloring

**Returns:** (Figure, list of Axes) tuple

## Complete Integration Example

```python
from rossler import RosslerAttractor
from visualizer import AttractorVisualizer

# Create attractor
rossler = RosslerAttractor()

# Generate trajectory
trajectory = rossler.generate_trajectory(t_span=(0, 500), n_points=50000)

# Compute Poincaré section
section = rossler.compute_poincare_section(
    trajectory=trajectory,
    plane='z',
    plane_value=0.0,
    direction='up',
    method='interpolate'
)

# Generate bifurcation data
bifurcation = rossler.generate_bifurcation_data(
    param_name='c',
    param_range=(2.0, 8.0),
    n_values=300
)

# Visualize everything!
vis = AttractorVisualizer()

# 1. 3D trajectory
vis.plot_trajectory_3d(trajectory, title="Rössler Attractor")

# 2. Poincaré section (2D)
vis.plot_poincare_section_2d(section, colormap='plasma')

# 3. Poincaré overlay (3D)
vis.plot_poincare_overlay_3d(trajectory, section, plane='z')

# 4. Bifurcation diagram
vis.plot_bifurcation_diagram(bifurcation, xlabel="Parameter c", ylabel="z")

# 5. Animated bifurcation
vis.animate_bifurcation(bifurcation, save_path="chaos_emerges.gif")
```

## Testing

Run the complete test suite:
```bash
# Original visualizer tests
pytest test_visualizer.py -v

# Enhanced features tests
pytest test_visualizer_enhanced.py -v

# Run all tests
pytest test_visualizer*.py -v
```

Run demonstrations:
```bash
# Original demos
python visualizer_demo.py

# Poincaré and bifurcation demos
python poincare_bifurcation_demo.py
```

## Future Enhancements

Potential additions:
- Interactive 3D rotation with plotly backend
- Real-time streaming visualization
- Return map visualization
- Lyapunov exponent plots
- Recurrence plot analysis
- Correlation dimension visualization

---

**Author:** Alice
**Created for:** Strange Attractor Exploration Project
**Latest Update:** Added Poincaré section and bifurcation diagram capabilities
