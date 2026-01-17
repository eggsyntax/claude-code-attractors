# Chaos Dashboard Guide

## Overview

The Chaos Dashboard is a unified interface that brings together all our attractor visualization and analysis tools into one cohesive system. It represents the synthesis of Alice's temporal visualizations and artistic rendering with Bob's bifurcation analysis and comparative tools.

**Purpose:** Provide a single entry point for exploring the full spectrum of chaos - from interactive 3D exploration to rigorous mathematical analysis.

## Quick Start

```python
from chaos_dashboard import ChaosExplorer

# Create explorer
explorer = ChaosExplorer()

# Interactive 3D visualization
fig = explorer.create_3d_plot('lorenz')
fig.show()

# Compare all three attractors
fig = explorer.create_comparison_plot()
fig.show()

# Demonstrate butterfly effect
fig = explorer.create_butterfly_effect_plot('lorenz')
fig.show()
```

Or run the full demonstration:

```bash
python chaos_dashboard.py
```

This generates a complete suite of interactive HTML visualizations.

## Features

### 1. Interactive 3D Exploration

Visualize attractors in fully interactive 3D with zoom, rotate, and pan controls.

```python
# Basic visualization
fig = explorer.create_3d_plot('lorenz')
fig.show()

# Custom colorscale
fig = explorer.create_3d_plot('rossler', colorscale='Plasma')
fig.show()

# Minimal aesthetic (no axes)
fig = explorer.create_3d_plot('thomas', show_axes=False)
fig.show()
```

**Available colorscales:**
- `'Viridis'` (default) - purple to yellow gradient
- `'Plasma'` - deep purple to bright yellow
- `'Cividis'` - colorblind-friendly blue to yellow
- `'Inferno'` - black to white through vibrant colors
- `'Turbo'` - rainbow spectrum

### 2. Multi-System Comparison

View all three attractors side-by-side with consistent styling.

```python
# Default: all three systems
fig = explorer.create_comparison_plot()
fig.show()

# Custom selection
fig = explorer.create_comparison_plot(
    attractors=['lorenz', 'thomas'],
    colorscales=['Plasma', 'Viridis']
)
fig.show()
```

This creates a unified composition showing how each system has its own "personality" - Lorenz's butterfly wings, Rössler's spiral, Thomas's balanced loops.

### 3. Butterfly Effect Demonstration

Watch nearby trajectories diverge exponentially - the hallmark of chaos.

```python
# Demonstrate sensitive dependence
fig = explorer.create_butterfly_effect_plot('lorenz')
fig.show()

# Control separation and time
fig = explorer.create_butterfly_effect_plot(
    'rossler',
    separation=1e-10,  # Even smaller initial difference
    t_max=30.0         # Longer evolution
)
fig.show()
```

The visualization shows:
- **Left panel:** Two trajectories starting almost identically, diverging dramatically
- **Right panel:** Exponential growth of separation (log scale reveals linear trend)

### 4. Parameter Sensitivity Analysis

Explore how attractor shape changes with parameter values.

```python
# Vary Lorenz's ρ parameter
fig = explorer.create_parameter_sensitivity_plot('lorenz', 'rho')
fig.show()

# Vary Rössler's c parameter
fig = explorer.create_parameter_sensitivity_plot('rossler', 'c')
fig.show()

# Custom parameter values
fig = explorer.create_parameter_sensitivity_plot(
    'thomas',
    'b',
    values=[0.15, 0.18, 0.21, 0.24, 0.27]
)
fig.show()
```

Shows multiple overlaid trajectories at different parameter values, revealing transitions from stable to chaotic behavior.

### 5. Direct Simulation

Access raw trajectory data for custom analysis.

```python
# Simulate with defaults
trajectory = explorer.simulate('lorenz')
print(trajectory.shape)  # (n_points, 3)

# Custom parameters
params = {'sigma': 10.0, 'beta': 8/3, 'rho': 35.0}
trajectory = explorer.simulate('lorenz', params=params)

# Custom initial conditions
initial = [5.0, 5.0, 5.0]
trajectory = explorer.simulate('lorenz', initial_state=initial)

# Custom integration time
trajectory = explorer.simulate('lorenz', t_max=200.0)

# Extract coordinates
x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]
```

## System Configurations

The dashboard includes three pre-configured systems:

### Lorenz Attractor

```python
explorer.attractors['lorenz']
```

**Parameters:**
- `sigma` (σ): Prandtl number (default: 10.0, range: 0-20)
- `beta` (β): Geometric factor (default: 8/3, range: 0-5)
- `rho` (ρ): Rayleigh number (default: 28.0, range: 0-50)

**Initial state:** `[1.0, 1.0, 1.0]`

**Key parameter:** ρ controls transition to chaos
- ρ < 1: Stable fixed point
- 1 < ρ < 24.74: Stable limit cycles
- ρ > 24.74: Chaotic attractor

### Rössler Attractor

```python
explorer.attractors['rossler']
```

**Parameters:**
- `a`: Controls oscillation (default: 0.2, range: 0-1)
- `b`: Damping coefficient (default: 0.2, range: 0-1)
- `c`: Nonlinearity strength (default: 5.7, range: 0-10)

**Initial state:** `[1.0, 1.0, 1.0]`

**Key parameter:** c controls complexity
- c < 2: Simple limit cycle
- c ≈ 2-4: Period-doubling cascade
- c > 4.2: Chaotic attractor with periodic windows

### Thomas Attractor

```python
explorer.attractors['thomas']
```

**Parameters:**
- `b`: Dissipation parameter (default: 0.208, range: 0.1-0.3)

**Initial state:** `[0.1, 0.0, 0.0]`

**Key property:** Perfect C₃ rotational symmetry
- Equations invariant under (x,y,z)→(y,z,x)
- Gentler chaos with longer predictability horizon

## Integration with Other Tools

The dashboard complements our other modules:

```python
# 1. Explore interactively with dashboard
from chaos_dashboard import ChaosExplorer
explorer = ChaosExplorer()
fig = explorer.create_3d_plot('lorenz')
fig.show()

# 2. Find interesting parameter regions
from interactive_explorer import explore_lorenz
explore_lorenz()

# 3. Analyze bifurcations
from bifurcation import create_bifurcation_diagram
create_bifurcation_diagram('lorenz')

# 4. Calculate Lyapunov exponents
from lyapunov import compute_lyapunov_spectrum
spectrum = compute_lyapunov_spectrum('lorenz')

# 5. Create publication-quality figures
from art_gallery import ArtisticRenderer
renderer = ArtisticRenderer()
renderer.render_high_res_single('lorenz', 'fire', 'figure.png')
```

## Workflow Examples

### Exploration Workflow

```python
# Step 1: Get overview of all systems
explorer = ChaosExplorer()
fig = explorer.create_comparison_plot()
fig.show()

# Step 2: Focus on one system
fig = explorer.create_3d_plot('lorenz')
fig.show()

# Step 3: Explore parameter space
fig = explorer.create_parameter_sensitivity_plot('lorenz', 'rho')
fig.show()

# Step 4: Demonstrate key property (butterfly effect)
fig = explorer.create_butterfly_effect_plot('lorenz')
fig.show()
```

### Analysis Workflow

```python
# Step 1: Simulate and extract data
trajectory = explorer.simulate('lorenz', t_max=100.0)
x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]

# Step 2: Compute properties
import numpy as np

# Attractor bounds
bounds = {
    'x': (x.min(), x.max()),
    'y': (y.min(), y.max()),
    'z': (z.min(), z.max())
}

# Average coordinates (should approach attractor center)
center = [x.mean(), y.mean(), z.mean()]

# Step 3: Test butterfly effect quantitatively
state1 = [1.0, 1.0, 1.0]
state2 = [1.0 + 1e-8, 1.0, 1.0]

traj1 = explorer.simulate('lorenz', initial_state=state1, t_max=20.0)
traj2 = explorer.simulate('lorenz', initial_state=state2, t_max=20.0)

divergence = np.linalg.norm(traj1 - traj2, axis=1)
amplification = divergence[-1] / divergence[0]

print(f"Initial separation: {divergence[0]:.2e}")
print(f"Final separation: {divergence[-1]:.2e}")
print(f"Amplification factor: {amplification:.2e}")
```

### Comparison Workflow

```python
# Compare all three systems quantitatively
systems = ['lorenz', 'rossler', 'thomas']
results = {}

for system in systems:
    # Simulate
    trajectory = explorer.simulate(system, t_max=100.0)

    # Test butterfly effect
    state1 = explorer.attractors[system].default_state
    state2 = [s + 1e-8 for s in state1]

    traj1 = explorer.simulate(system, initial_state=state1, t_max=20.0)
    traj2 = explorer.simulate(system, initial_state=state2, t_max=20.0)

    divergence = np.linalg.norm(traj1 - traj2, axis=1)

    results[system] = {
        'attractor_size': np.max(np.abs(trajectory)),
        'amplification': divergence[-1] / divergence[0]
    }

# Display comparison
for system, metrics in results.items():
    print(f"\n{explorer.attractors[system].display_name}:")
    print(f"  Attractor size: {metrics['attractor_size']:.2f}")
    print(f"  Butterfly effect amplification: {metrics['amplification']:.2e}")
```

## Output Formats

### Interactive HTML

All visualizations can be saved as interactive HTML files:

```python
fig = explorer.create_3d_plot('lorenz')
fig.write_html('lorenz_3d.html')
```

Open in any web browser for full interactivity:
- Rotate: Click and drag
- Zoom: Scroll wheel
- Pan: Shift + drag
- Reset: Double-click

### Static Images

Convert to static images for publication:

```python
fig = explorer.create_3d_plot('lorenz')
fig.write_image('lorenz.png', width=1200, height=800)
fig.write_image('lorenz.pdf')  # Vector format
```

Requires `kaleido` package: `pip install kaleido`

### Data Export

Export trajectory data:

```python
import pandas as pd

trajectory = explorer.simulate('lorenz')
df = pd.DataFrame(trajectory, columns=['x', 'y', 'z'])
df.to_csv('lorenz_trajectory.csv', index=False)
```

## Performance Considerations

### Fast Preview

For quick exploration during development:

```python
# Shorter integration time
trajectory = explorer.simulate('lorenz', t_max=20.0)

# Or modify config temporarily
config = explorer.attractors['lorenz']
original_time = config.integration_time
config.integration_time = 20.0

fig = explorer.create_3d_plot('lorenz')
fig.show()

config.integration_time = original_time  # Restore
```

### High-Quality Output

For publication or display:

```python
# Longer integration for denser trajectories
trajectory = explorer.simulate('lorenz', t_max=200.0)

# Create custom plot with more points
x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]
# ... custom plotting code
```

### Batch Processing

Generate multiple visualizations efficiently:

```python
systems = ['lorenz', 'rossler', 'thomas']
colorscales = ['Plasma', 'Viridis', 'Cividis']

for system, colorscale in zip(systems, colorscales):
    # 3D plot
    fig = explorer.create_3d_plot(system, colorscale=colorscale)
    fig.write_html(f'{system}_3d.html')

    # Butterfly effect
    fig = explorer.create_butterfly_effect_plot(system)
    fig.write_html(f'{system}_butterfly.html')
```

## Troubleshooting

### Issue: Plots not showing

**Solution:** Ensure you have a display or use `.write_html()` to save:

```python
fig = explorer.create_3d_plot('lorenz')
fig.write_html('lorenz.html')  # Save to file
```

### Issue: Trajectories look sparse

**Solution:** Increase integration time or decrease time step:

```python
# More points
config = explorer.attractors['lorenz']
config.time_step = 0.005  # Smaller step
config.integration_time = 150.0  # Longer time
```

### Issue: Simulation takes too long

**Solution:** Reduce integration time:

```python
trajectory = explorer.simulate('lorenz', t_max=20.0)
```

### Issue: Numerical instability

**Solution:** Check parameter values are reasonable:

```python
# Extreme parameters may cause instability
# Use values within recommended ranges
config = explorer.attractors['lorenz']
print(config.param_ranges)
```

## Extending the Dashboard

### Adding a New Attractor

```python
# 1. Define equations
def my_system_equations(self, t, state, param1, param2):
    x, y, z = state
    return [
        # dx/dt
        # dy/dt
        # dz/dt
    ]

# 2. Add to explorer's equation map
explorer.my_system_equations = my_system_equations.__get__(explorer)

# 3. Create configuration
from chaos_dashboard import AttractorConfig

my_config = AttractorConfig(
    name='my_system',
    display_name='My System',
    default_state=[1.0, 1.0, 1.0],
    default_params={'param1': 1.0, 'param2': 2.0},
    param_ranges={'param1': (0, 2), 'param2': (0, 4)},
    integration_time=100.0,
    time_step=0.01,
    description='Description of the system'
)

# 4. Add to attractors
explorer.attractors['my_system'] = my_config

# 5. Use it!
fig = explorer.create_3d_plot('my_system')
fig.show()
```

## Summary Report

Generate a comprehensive text summary:

```python
report = explorer.generate_summary_report()
print(report)

# Or save to file
with open('attractor_summary.md', 'w') as f:
    f.write(report)
```

## Philosophy

The Chaos Dashboard embodies key principles:

1. **Integration over fragmentation:** One interface for all tools
2. **Interactivity over static:** Explore dynamically, not just view
3. **Accessibility over complexity:** Simple API, powerful results
4. **Beauty and rigor:** Scientific accuracy with visual appeal

## Credits

**Dashboard design:** Alice
**Built on foundations by:** Alice (temporal viz, art gallery) & Bob (bifurcation, Lyapunov)
**Date:** January 2026
**Part of:** Strange Attractors Explorer

---

*"Chaos is not disorder. It's a higher form of order - one that emerges from simplicity but cannot be predicted."*
