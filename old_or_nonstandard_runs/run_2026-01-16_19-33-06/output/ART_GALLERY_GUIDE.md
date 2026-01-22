# Attractor Art Gallery Guide

## Overview

The Art Gallery module creates publication-quality, artistic visualizations of strange attractors. It combines scientific accuracy with aesthetic beauty, using advanced rendering techniques to showcase the visual elegance of chaotic systems.

## Purpose

While our other visualization tools are designed for exploration and analysis, the Art Gallery focuses on **presentation and communication**:

- **Publication-quality** images at 300 DPI
- **Artistic rendering** with custom color schemes and lighting
- **Multiple composition styles** (single, triptych, multi-perspective)
- **Clean, minimalist aesthetic** suitable for presentations, papers, or display

## Quick Start

```python
from art_gallery import create_gallery

# Generate complete gallery (5 images)
create_gallery()
```

This creates:
- `attractor_triptych.png` - Three-panel comparison of all attractors
- `lorenz_perspectives.png` - Four viewing angles of Lorenz
- `lorenz_highres.png` - High-resolution Lorenz render
- `rossler_highres.png` - High-resolution Rössler render
- `thomas_highres.png` - High-resolution Thomas render

## Artistic Rendering Techniques

### 1. Density-Based Alpha Blending

The renderer uses progressive alpha values along the trajectory:
- **Early points**: More transparent (α ≈ 0.1)
- **Later points**: More opaque (α ≈ 0.8)

This creates a **fade-in effect** that emphasizes the attractor's shape while showing temporal flow. The trajectory appears to "build up" density where it spends more time.

```python
# Traditional: uniform alpha
ax.plot(x, y, z, alpha=0.5)

# Art Gallery: progressive alpha
alphas = np.linspace(0.1, 0.8, n_points)
for i in range(n_points - 1):
    ax.plot(x[i:i+2], y[i:i+2], z[i:i+2], alpha=alphas[i])
```

### 2. Custom Color Schemes

Five carefully designed color schemes:

#### **Fire** (Lorenz default)
Hot colors suggesting energy and chaos: deep purple → crimson → orange → yellow

Best for: High-energy systems, dramatic presentations

#### **Ice** (Rössler default)
Cool colors suggesting precision and flow: deep blue → cyan → pale blue

Best for: Structured systems, scientific contexts

#### **Gradient** (Thomas default)
Subtle progression: midnight blue → steel blue → silver

Best for: Elegant displays, minimalist aesthetics

#### **Monochrome**
Grayscale progression: black → white

Best for: Publications with printing constraints, formal documents

#### **Rainbow**
Vibrant spectrum: purple → red → yellow → green

Best for: Educational contexts, engaging presentations

### 3. Temporal Color Mapping

Colors progress along the trajectory to show temporal evolution:
- Darker/cooler colors = early in trajectory
- Lighter/warmer colors = later in trajectory

This helps the viewer understand the flow of the system over time.

### 4. Minimalist Aesthetic

Clean design choices:
- **No axis labels** - let the attractor speak for itself
- **No tick marks** - removes visual clutter
- **Transparent background panes** - emphasizes the structure
- **Subtle grid** (α = 0.1) - provides spatial reference without distraction
- **High-quality typography** - bold, readable titles

## Usage Examples

### Basic: Generate Complete Gallery

```python
from art_gallery import create_gallery
create_gallery()
```

### Custom: Single High-Resolution Render

```python
from art_gallery import ArtisticRenderer

renderer = ArtisticRenderer(dpi=300, figsize=(12, 8))

# Lorenz with fire colormap
renderer.render_high_res_single(
    system_name='lorenz',
    color_style='fire',
    save_path='lorenz_fire.png'
)

# Thomas with monochrome (for publication)
renderer.render_high_res_single(
    system_name='thomas',
    color_style='monochrome',
    save_path='thomas_bw.png'
)
```

### Custom: Multi-Perspective View

```python
# Four viewing angles of Rössler
renderer.render_multi_perspective(
    system_name='rossler',
    save_path='rossler_4views.png'
)
```

### Custom: Triptych with Different Settings

```python
# Lower DPI for web use
web_renderer = ArtisticRenderer(dpi=150, figsize=(18, 6))
web_renderer.render_triptych('attractors_web.png')
```

### Advanced: Manual Trajectory Control

```python
# Generate custom trajectory
trajectory = renderer.generate_trajectory(
    renderer.lorenz,
    initial_state=[1.0, 1.0, 1.0],
    t_span=(0, 200),  # Longer for more density
    dt=0.005  # Smaller for smoother lines
)

# Render with custom settings
fig = renderer.render_single_attractor(
    trajectory,
    title='Lorenz: Extended Evolution',
    color_style='ice',
    elevation=30,  # View from above
    azimuth=60,    # Rotated perspective
    alpha_fade=True
)

import matplotlib.pyplot as plt
plt.savefig('lorenz_custom.png', dpi=300, bbox_inches='tight')
plt.close()
```

## Output Specifications

### Resolution
- **Default DPI**: 300 (publication quality)
- **Minimum recommended**: 150 (web/screen)
- **High quality**: 300-600 (print/display)

### Figure Sizes
- **Single attractor**: 12" × 8" (landscape)
- **Triptych**: 18" × 6" (wide panoramic)
- **Multi-perspective**: 14" × 14" (square grid)

### File Sizes
Typical output sizes at 300 DPI:
- Single attractor: 2-4 MB
- Triptych: 4-6 MB
- Multi-perspective: 6-8 MB

## Color Scheme Selection Guide

| Context | Recommended Scheme | Rationale |
|---------|-------------------|-----------|
| Journal publication | Monochrome or Gradient | Professional, prints reliably |
| Conference presentation | Fire or Ice | High contrast, visible from distance |
| Educational material | Rainbow | Engaging, helps distinguish regions |
| Art display | Fire, Ice, or Gradient | Aesthetically compelling |
| Technical report | Gradient or Ice | Subtle, professional |
| Poster | Fire or Rainbow | Eye-catching, vibrant |

## Viewing Angle Guidelines

### Elevation (vertical angle)
- **20°**: Standard perspective (default)
- **0°**: Edge-on view (emphasizes flatness)
- **45°**: High perspective (shows 3D structure)
- **90°**: Top-down view (reveals 2D projection)

### Azimuth (horizontal rotation)
- **45°**: Front-right (default, balanced)
- **135°**: Front-left (mirror of 45°)
- **0°** or **180°**: Side views (emphasize depth)
- **90°** or **270°**: Front/back views

**Pro tip**: For Lorenz, azimuth 45° shows the butterfly wings clearly. For Thomas, any azimuth works due to rotational symmetry!

## Comparison: Art Gallery vs Other Visualizations

| Feature | Art Gallery | Interactive Explorer | Static Plots | Temporal Viz |
|---------|-------------|---------------------|--------------|--------------|
| **Purpose** | Presentation | Exploration | Analysis | Understanding |
| **Resolution** | 300 DPI | 72 DPI | 100 DPI | 100 DPI |
| **Aesthetic** | Artistic | Functional | Scientific | Educational |
| **File size** | 2-8 MB | Interactive | 100-500 KB | 500 KB - 2 MB |
| **Best for** | Papers, posters | Parameter tuning | Quick reference | Teaching dynamics |

## Tips for Best Results

### 1. Integration Time
Longer integration = more trajectory = denser visualization:
- **Quick preview**: t_span = (0, 50), dt = 0.01
- **Standard**: t_span = (0, 100), dt = 0.01
- **High density**: t_span = (0, 200), dt = 0.005

### 2. Performance Optimization
For faster rendering during development:
```python
# Quick preview renderer
preview = ArtisticRenderer(dpi=72, figsize=(8, 6))
```

Then switch to high-res for final output:
```python
# Final output renderer
final = ArtisticRenderer(dpi=300, figsize=(12, 8))
```

### 3. Color Scheme Testing
Try multiple schemes and pick the best:
```python
schemes = ['fire', 'ice', 'gradient', 'monochrome']
for scheme in schemes:
    renderer.render_high_res_single(
        'lorenz',
        color_style=scheme,
        save_path=f'lorenz_{scheme}.png'
    )
```

### 4. Batch Processing
Generate multiple versions efficiently:
```python
systems = ['lorenz', 'rossler', 'thomas']
colors = ['fire', 'ice', 'gradient']

for system in systems:
    for color in colors:
        filename = f'{system}_{color}.png'
        renderer.render_high_res_single(system, color, filename)
```

## Technical Details

### Trajectory Generation
Uses `scipy.integrate.solve_ivp` with:
- **Method**: RK45 (adaptive Runge-Kutta)
- **Tolerances**: rtol=1e-8, atol=1e-10 (high accuracy)
- **Time step**: Adaptive based on dynamics

### Alpha Blending Formula
```python
alphas = np.linspace(0.1, 0.8, n_points)
# Creates progressive fade-in effect
```

### Colormap Construction
Uses `LinearSegmentedColormap.from_list()` with 5-10 carefully chosen hex colors, creating smooth gradients between anchor points.

### Performance Considerations
- **Skip factor**: Renders every 2nd point for triptych (2x speedup)
- **Vectorization**: Uses NumPy for all computations
- **Backend**: Agg backend for non-interactive rendering

## Integration with Existing Tools

The Art Gallery complements our other visualization tools:

```python
# 1. Explore parameters interactively
from interactive_explorer import explore_lorenz
explore_lorenz()

# 2. Analyze bifurcations
from bifurcation import create_bifurcation_diagram
create_bifurcation_diagram('lorenz')

# 3. Calculate Lyapunov exponents
from lyapunov import compute_lyapunov_spectrum
spectrum = compute_lyapunov_spectrum('lorenz')

# 4. Generate publication figure
from art_gallery import ArtisticRenderer
renderer = ArtisticRenderer()
renderer.render_high_res_single('lorenz', 'fire', 'figure1.png')
```

## Example Workflow: From Exploration to Publication

```python
# Step 1: Explore parameter space
from interactive_explorer import explore_lorenz
explore_lorenz()  # Find interesting parameter values

# Step 2: Analyze transition to chaos
from bifurcation import create_bifurcation_diagram
create_bifurcation_diagram('lorenz')

# Step 3: Create publication-quality figure
from art_gallery import ArtisticRenderer
renderer = ArtisticRenderer(dpi=300)
renderer.render_high_res_single('lorenz', 'monochrome', 'figure_1.png')

# Step 4: Create multi-panel comparison
renderer.render_triptych('figure_2.png')
```

## Troubleshooting

### Issue: Images are too large
**Solution**: Reduce DPI or figure size
```python
renderer = ArtisticRenderer(dpi=150, figsize=(10, 6))
```

### Issue: Rendering is slow
**Solution**: Reduce trajectory length or increase dt
```python
trajectory = renderer.generate_trajectory(
    system, state, t_span=(0, 50), dt=0.02  # Faster
)
```

### Issue: Colors look washed out
**Solution**: Use higher alpha values or darker colormap
```python
# Modify source to use higher alphas
alphas = np.linspace(0.3, 0.9, n_points)  # Less transparent
```

### Issue: Structure is hard to see
**Solution**: Try different viewing angles
```python
fig = renderer.render_single_attractor(
    trajectory,
    title='Custom View',
    elevation=30,   # Higher elevation
    azimuth=60      # Different rotation
)
```

## Credits and Philosophy

The Art Gallery module embodies a core principle: **scientific visualization should be both accurate and beautiful**.

Chaotic systems produce structures of genuine aesthetic appeal. By using careful rendering techniques - progressive alpha blending, custom color schemes, minimalist design - we reveal this beauty without compromising scientific integrity.

The result is images that work equally well in a research paper, on a conference poster, or framed on a wall.

---

**Author**: Alice
**Date**: January 2026
**Part of**: Strange Attractors Explorer
**License**: MIT

---

*"In chaos, there is beauty. In mathematics, there is art."*
