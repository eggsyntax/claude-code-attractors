# Rössler Attractor Implementation

## Overview

The Rössler attractor is a system of three coupled nonlinear ordinary differential equations that exhibits chaotic behavior. It was introduced by Otto Rössler in 1976 as a simpler alternative to the Lorenz system while still demonstrating the essential features of chaos.

## Mathematical Definition

The Rössler system is defined by:

```
dx/dt = -y - z
dy/dt = x + a*y
dz/dt = b + z*(x - c)
```

### Key Characteristics

- **Simplicity**: Only one nonlinear term (z·x) compared to Lorenz's two
- **Single-lobed structure**: Distinctive ribbon-like attractor in phase space
- **Classic chaos**: Demonstrates period-doubling route to chaos
- **Pedagogical value**: Excellent for teaching chaos theory fundamentals

## Quick Start

```python
from rossler import RosslerAttractor

# Create attractor with default chaotic parameters (a=0.2, b=0.2, c=5.7)
rossler = RosslerAttractor()

# Generate trajectory
trajectory = rossler.generate_trajectory(t_span=(0, 100), n_points=10000)

# Visualize
from visualizer import AttractorVisualizer
vis = AttractorVisualizer()
vis.plot_trajectory_3d(trajectory, title="Rössler Attractor")
```

## Parameter Regimes

The system exhibits different behaviors as parameters change. Most commonly, we fix a=0.2 and b=0.2 while varying c:

| Parameter c | Behavior | Description |
|-------------|----------|-------------|
| c = 2.0 | Periodic | Simple limit cycle |
| c = 3.5 | Period-2 | Period-doubled orbit |
| c = 4.0 | Transition | Between period-doubling and chaos |
| c = 5.7 | **Chaotic** | **Classic chaotic attractor (default)** |
| c = 10.0 | Highly Chaotic | More complex chaotic behavior |

### Using Parameter Recommendations

```python
# Get all recommended parameter sets
recommendations = RosslerAttractor.get_parameter_recommendations()

# Try periodic behavior
rossler_periodic = RosslerAttractor(parameters=recommendations['periodic'])
trajectory = rossler_periodic.generate_trajectory(t_span=(0, 100), n_points=5000)

# Try chaotic behavior
rossler_chaotic = RosslerAttractor(parameters=recommendations['chaotic'])
trajectory = rossler_chaotic.generate_trajectory(t_span=(0, 100), n_points=10000)
```

## Advanced Features

### 1. Poincaré Sections

Poincaré sections are a powerful tool for visualizing and analyzing chaotic dynamics. They reduce the 3D attractor to a 2D map by recording where trajectories cross a specified plane.

```python
rossler = RosslerAttractor()
trajectory = rossler.generate_trajectory(t_span=(0, 200), n_points=20000)

# Compute Poincaré section at z=0 plane
section = rossler.compute_poincare_section(
    trajectory,
    plane='z',        # Which plane: 'x', 'y', or 'z'
    value=0.0,        # Location of the plane
    direction='up'    # 'up', 'down', or 'both'
)

# section is an array of shape (n_intersections, 2)
# For plane='z', it contains (x, y) coordinates where trajectory crosses z=0

# Visualize
import matplotlib.pyplot as plt
plt.scatter(section[:, 0], section[:, 1], s=1, alpha=0.5)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Poincaré Section (z=0)')
plt.show()
```

**Poincaré Section Parameters:**
- `plane`: Which coordinate to fix ('x', 'y', or 'z')
- `value`: The value at which to intersect (e.g., z=0)
- `direction`:
  - `'up'`: Only record upward crossings (increasing coordinate)
  - `'down'`: Only record downward crossings (decreasing coordinate)
  - `'both'`: Record all crossings
- `tolerance`: Optional tolerance for approximate intersections (default uses exact interpolation)

### 2. Return Maps

Return maps show the relationship between successive crossings in a Poincaré section, revealing the structure of the attractor.

```python
# Get Poincaré section points
section = rossler.compute_poincare_section(trajectory, plane='z', value=0.0)

# Create return map: plot x_n+1 vs x_n
x_current = section[:-1, 0]
x_next = section[1:, 0]

plt.scatter(x_current, x_next, s=1)
plt.xlabel('x_n')
plt.ylabel('x_n+1')
plt.title('Return Map')
plt.show()
```

### 3. Bifurcation Diagrams

Bifurcation diagrams show how the system's long-term behavior changes as a parameter varies, revealing the period-doubling route to chaos.

```python
rossler = RosslerAttractor()

# Generate bifurcation data
param_values, samples = rossler.generate_bifurcation_data(
    parameter='c',              # Which parameter to vary
    param_range=(2.0, 6.5),     # Range to explore
    n_params=200,               # Resolution
    transient_time=50.0,        # Time to let system settle
    sample_time=50.0,           # Time to sample behavior
    n_points=2000               # Trajectory resolution
)

# Plot bifurcation diagram
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 6))

for i, param_val in enumerate(param_values):
    z_values = samples[i][:, 2]  # z coordinate
    # Plot a subset of points
    step = max(1, len(z_values) // 50)
    ax.plot([param_val] * len(z_values[::step]), z_values[::step],
            'k.', markersize=0.5)

ax.set_xlabel('Parameter c')
ax.set_ylabel('Z (sampled values)')
ax.set_title('Bifurcation Diagram')
plt.show()
```

## Comparison with Lorenz Attractor

| Feature | Lorenz | Rössler |
|---------|--------|---------|
| **Structure** | Double-lobed (butterfly) | Single-lobed (ribbon) |
| **Nonlinear terms** | 2 (x·y, x·z) | 1 (z·x) |
| **Complexity** | More complex | Simpler |
| **Origin** | Atmospheric convection | Designed for chaos research |
| **Best for** | Demonstrating chaos in physical systems | Teaching period-doubling route |

### Side-by-Side Comparison

```python
from lorenz import LorenzAttractor
from rossler import RosslerAttractor
from visualizer import AttractorVisualizer

# Generate both
lorenz = LorenzAttractor()
rossler = RosslerAttractor()

traj_l = lorenz.generate_trajectory(t_span=(0, 50), n_points=10000)
traj_r = rossler.generate_trajectory(t_span=(0, 100), n_points=10000)

# Compare
vis = AttractorVisualizer()
fig = vis.compare_attractors(
    [traj_l, traj_r],
    ['Lorenz', 'Rössler'],
    ['blue', 'purple']
)
```

## API Reference

### Class: `RosslerAttractor`

Inherits from `AttractorBase`. Implements the Rössler chaotic system.

#### Constructor

```python
RosslerAttractor(
    initial_state: Optional[np.ndarray] = None,
    parameters: Optional[Dict[str, float]] = None
)
```

**Parameters:**
- `initial_state`: Initial conditions [x₀, y₀, z₀]. Default: [1.0, 1.0, 1.0]
- `parameters`: Dictionary with keys 'a', 'b', 'c'. Default: {'a': 0.2, 'b': 0.2, 'c': 5.7}

#### Methods

**`generate_trajectory(t_span, n_points, method='RK45')`**

Generate a trajectory through phase space.

**Returns:** numpy array of shape (n_points, 3)

---

**`compute_poincare_section(trajectory, plane='z', value=0.0, direction='both', tolerance=None)`**

Compute Poincaré section by finding plane intersections.

**Parameters:**
- `trajectory`: Trajectory array of shape (n_points, 3)
- `plane`: Which plane to intersect ('x', 'y', or 'z')
- `value`: Location of the plane
- `direction`: 'up', 'down', or 'both'
- `tolerance`: Optional tolerance (if None, uses exact interpolation)

**Returns:** Array of shape (n_intersections, 2) with intersection points

---

**`generate_bifurcation_data(parameter='c', param_range=(2.0, 6.0), n_params=200, ...)`**

Generate data for a bifurcation diagram.

**Returns:** Tuple of (parameter_values, sampled_trajectories)

---

**`get_parameter_recommendations()`** (static method)

Get recommended parameter sets for different dynamical regimes.

**Returns:** Dictionary mapping regime names to parameter dictionaries

---

**`update_parameters(**kwargs)`**

Update system parameters.

**Example:** `rossler.update_parameters(c=4.0)`

---

**`get_info()`**

Get metadata about current configuration.

**Returns:** Dictionary with type, dimension, parameters, initial_state

## Physical Interpretation

Unlike the Lorenz system (which models atmospheric convection), the Rössler system was designed purely for chaos research. However, it can be interpreted as:

- A simplified chemical reaction model
- An abstract oscillator with nonlinear coupling
- A pedagogical example of how minimal nonlinearity creates chaos

The beauty of Rössler is in its **simplicity**: with just one nonlinear term (z·x), it captures the essential features of chaos:
- Sensitive dependence on initial conditions
- Aperiodic long-term behavior
- Bounded attractor in phase space
- Period-doubling route to chaos

## Examples from Literature

### Classic Chaotic Regime (c=5.7)

```python
rossler = RosslerAttractor()  # Default parameters
trajectory = rossler.generate_trajectory(t_span=(0, 200), n_points=20000)

# Typical bounds:
# X: approximately [-10, 15]
# Y: approximately [-10, 10]
# Z: approximately [0, 40]
```

### Period-Doubling Sequence

As c increases from ~2 to ~5, the system undergoes period-doubling:
- c ≈ 2.0: Period 1 (simple cycle)
- c ≈ 3.0: Period 2 (orbit doubles)
- c ≈ 3.8: Period 4
- c ≈ 4.2: Period 8
- c ≈ 4.6: Period 16
- c ≈ 5.0+: Chaotic windows and periodic windows intermix
- c ≈ 5.7: Fully developed chaos

## Demonstrations

Run `demo_rossler.py` for comprehensive demonstrations:

```bash
python demo_rossler.py
```

This generates:
1. Basic 3D visualization
2. Poincaré section analysis with return map
3. Parameter regime exploration
4. Butterfly effect demonstration
5. Comparison with Lorenz attractor
6. Bifurcation diagram

## Testing

Comprehensive test suite with 25+ test cases:

```bash
pytest test_rossler.py -v
```

Tests cover:
- Derivative calculations
- Trajectory generation
- Different parameter regimes
- Poincaré section computation
- Return map structure
- Butterfly effect (sensitivity)
- Attractor convergence
- Boundedness checks

## References

1. Rössler, O. E. (1976). "An equation for continuous chaos". *Physics Letters A*, 57(5), 397-398.

2. Strogatz, S. H. (2015). *Nonlinear Dynamics and Chaos*. Westview Press. (Chapter 9 covers Rössler attractor)

3. Alligood, K. T., Sauer, T. D., & Yorke, J. A. (1996). *Chaos: An Introduction to Dynamical Systems*. Springer.

## Tips for Exploration

1. **Start with visualization**: Plot the basic attractor in 3D to see its structure
2. **Try different parameters**: Use `get_parameter_recommendations()` to explore regimes
3. **Compute Poincaré sections**: They reveal the fractal structure of the attractor
4. **Create return maps**: These show the deterministic nature of chaos
5. **Generate bifurcation diagrams**: Watch the period-doubling cascade
6. **Compare with Lorenz**: See how different equations create different structures
7. **Test sensitivity**: Run two nearby initial conditions to see divergence

## Integration with Visualizer

The Rössler implementation works seamlessly with Alice's visualization toolkit:

```python
from rossler import RosslerAttractor
from visualizer import AttractorVisualizer

rossler = RosslerAttractor()
trajectory = rossler.generate_trajectory(t_span=(0, 100), n_points=10000)

vis = AttractorVisualizer()

# 3D plot
vis.plot_trajectory_3d(trajectory, title="Rössler Attractor", color='purple')

# Phase space projections
vis.plot_phase_projections(trajectory, title="Rössler Phase Space")

# Multiple trajectories (butterfly effect)
state1 = [1.0, 1.0, 1.0]
state2 = [1.0, 1.0, 1.0001]
rossler1 = RosslerAttractor(initial_state=state1)
rossler2 = RosslerAttractor(initial_state=state2)
traj1 = rossler1.generate_trajectory(t_span=(0, 50), n_points=5000)
traj2 = rossler2.generate_trajectory(t_span=(0, 50), n_points=5000)

vis.plot_multiple_trajectories(
    [traj1, traj2],
    colors=['red', 'blue'],
    labels=['IC 1', 'IC 2']
)
```

## What Makes This Implementation Special

1. **Complete analytical features**: Not just trajectory generation, but Poincaré sections, return maps, and bifurcation data
2. **Well-tested**: Comprehensive test suite validates correctness
3. **Well-documented**: Extensive docstrings and examples
4. **Seamless integration**: Works perfectly with the visualizer toolkit
5. **Pedagogical focus**: Designed for exploration and learning
6. **Production-ready**: Robust error handling, type hints, proper abstractions

---

*Implementation by Bob. Part of the collaborative attractor exploration framework with Alice.*
