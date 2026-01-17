# Poincaré Sections: A Visual Guide to Hidden Structure

## What is a Poincaré Section?

A **Poincaré section** (or Poincaré map) is a powerful technique for understanding the structure of dynamical systems. It works by reducing a continuous 3D flow to a discrete 2D map.

### The Basic Idea

Imagine a trajectory flowing through 3D phase space. Now imagine a 2D plane cutting through that space (like slicing through a loaf of bread). Every time the trajectory crosses the plane in a specific direction, we mark that point. The collection of these crossing points is the Poincaré section.

**Why is this useful?**
- **Dimension reduction**: Simplifies 3D dynamics to 2D, making patterns easier to see
- **Reveals structure**: Shows fractal organization and self-similarity
- **Distinguishes chaos from randomness**: Chaotic systems produce structured sections; random systems produce scattered points
- **Identifies periodic orbits**: Periodic motion appears as discrete points; chaos appears as continuous curves or clouds

## Mathematical Foundation

### Definition

For a continuous dynamical system **dx/dt = f(x)** in 3D phase space, a Poincaré section is defined by:

1. A **plane** Σ (e.g., z = z₀)
2. A **direction** (usually positive velocity through the plane)
3. The **return map** P: Σ → Σ that maps each crossing point to the next

The section is constructed by recording points **x_n** where the trajectory crosses Σ:
- x_{n+1} = P(x_n)

### What Sections Reveal

**For Periodic Orbits:**
- Period-1 orbit → 1 point in section
- Period-2 orbit → 2 points
- Period-k orbit → k points

**For Chaotic Attractors:**
- Dense collection of points forming intricate curves
- Self-similar (fractal) structure at multiple scales
- Points never exactly repeat (aperiodic)

**For Random Motion:**
- Uniformly scattered points with no structure

## Poincaré Sections of Strange Attractors

### Lorenz Attractor

**Plane**: z = 27 (cutting through the center of the butterfly)

**What you see:**
- **Two distinct regions**: Corresponding to the left and right "wings" of the butterfly
- **Fractal folding**: Each wing shows fine-scale structure from repeated stretching and folding
- **Layered lines**: If you zoom in, you'd see lines splitting into more lines (self-similarity)

**Physical meaning**: Each crossing represents one "orbit" around a wing before crossing to the plane. The complex structure shows why predicting which wing the system will visit next becomes impossible after a few iterations.

**Parameter dependence (ρ):**
- ρ < 24.06: Simple fixed points (few crossing points)
- ρ ≈ 24.74: Transition to chaos begins
- ρ = 28: Fully developed strange attractor with rich fractal structure
- ρ > 28: Even more complex structure

### Rössler Attractor

**Plane**: z = 0 (cutting through the orbital plane)

**What you see:**
- **Spiral structure**: Points arranged in a rotating pattern
- **Continuous curve**: In the chaotic regime (c = 5.7), points form a dense curve
- **Single-lobed**: Unlike Lorenz's two lobes, Rössler has one main region

**Physical meaning**: Each crossing represents one loop around the attractor's spiral. The curve's thickness and structure reveal the mixing dynamics.

**Parameter dependence (c):**
- c = 2: Simple closed curve (period-1 orbit) → single isolated point
- c = 3: Period-2 orbit → two points
- c = 4: Period-4 orbit → four points
- c = 5.7: Chaos → continuous dense curve with structure
- c = 6+: More complex chaotic patterns

## How to Use This Module

### Basic Usage

```python
from poincare import create_lorenz_section, create_rossler_section

# Create Lorenz section
section, poincare = create_lorenz_section(rho=28.0, plane='z')

# Visualize it
fig = poincare.visualize_section(section, title="Lorenz Attractor Section")
fig.savefig('lorenz_section.png', dpi=300)

# Create Rössler section
section, poincare = create_rossler_section(c=5.7, plane='z')
fig = poincare.visualize_section(section, title="Rössler Attractor Section")
fig.savefig('rossler_section.png', dpi=300)
```

### Custom Systems

```python
from poincare import PoincareSection
import numpy as np

# Define your equations
def my_equations(t, state):
    x, y, z = state
    # Your differential equations here
    return [dx_dt, dy_dt, dz_dt]

# Create Poincaré section
poincare = PoincareSection(
    my_equations,
    plane_coord=1,      # 0=x, 1=y, 2=z
    plane_value=0.0,    # y = 0
    direction='positive' # Cross with dy/dt > 0
)

# Compute section
initial_state = np.array([1.0, 1.0, 1.0])
section = poincare.compute_section(initial_state, t_max=100.0)

# Visualize
fig = poincare.visualize_section(section)
```

### Parameter Comparison

```python
from poincare import compare_parameter_sections

# Compare Lorenz at different ρ values
fig = compare_parameter_sections('lorenz', param_values=[14, 20, 24, 28])
fig.savefig('lorenz_comparison.png', dpi=300)

# Compare Rössler at different c values
fig = compare_parameter_sections('rossler', param_values=[2, 4, 5.7, 6])
fig.savefig('rossler_comparison.png', dpi=300)
```

### Multiple Trajectories

```python
# Show that different initial conditions converge to same attractor
initial_states = [
    np.array([1.0, 1.0, 1.0]),
    np.array([5.0, 5.0, 5.0]),
    np.array([-1.0, 2.0, 3.0])
]

sections = poincare.multi_trajectory_section(initial_states)

# Plot all on same axes to show convergence
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 10))
for i, section in enumerate(sections):
    ax.scatter(section[:, 0], section[:, 1], s=1, alpha=0.5, label=f'IC {i+1}')
ax.legend()
ax.set_title('Different Initial Conditions → Same Attractor')
```

## Interpreting Your Results

### Visual Indicators

**Structured patterns = Deterministic chaos**
- Dense curves with repeated folding
- Self-similar at different scales
- Never-repeating but not random

**Isolated points = Periodic motion**
- Discrete crossing points
- Number of points = period of orbit
- Completely predictable

**Scattered points = Random/stochastic**
- No visible structure
- Uniform distribution
- True randomness (not chaos)

### Quantitative Analysis

From Poincaré sections, you can:

1. **Count periodic points**: Identify period-k orbits
2. **Measure fractal dimension**: Use box-counting on the section
3. **Estimate Lyapunov exponents**: From separation rates between nearby points
4. **Find bifurcation points**: See where structure changes as parameters vary

## Connection to Other Visualizations

### Poincaré Sections ↔ Bifurcation Diagrams

A bifurcation diagram is essentially many Poincaré sections stacked together:
- Horizontal axis = parameter value
- Vertical axis = section coordinate
- Each vertical slice is one Poincaré section

### Poincaré Sections ↔ 3D Attractors

The section is a 2D slice through the 3D attractor:
- **3D view**: Shows overall geometry and flow
- **Poincaré section**: Shows detailed structure and folding
- Together they give complete understanding

### Poincaré Sections ↔ Lyapunov Exponents

Lyapunov exponents measure **rate** of divergence; Poincaré sections show **structure** of divergence:
- Positive Lyapunov → Section has fractal structure
- Zero Lyapunov → Section shows periodic points
- Negative Lyapunov → Section collapses to fixed point

## Technical Notes

### Choosing the Plane

**Guidelines:**
1. **Avoid tangent planes**: Choose planes the trajectory crosses transversely (not grazing)
2. **Cut through the center**: For Lorenz, z = 27 cuts through both wings
3. **Natural symmetries**: For Rössler, z = 0 aligns with the orbital plane

**Common choices:**
- Coordinate planes (x=0, y=0, z=0)
- Planes at special parameter values
- Planes perpendicular to flow direction

### Integration Parameters

```python
section = poincare.compute_section(
    initial_state,
    t_max=100.0,       # Total integration time
    t_transient=10.0,  # Time to discard (settle onto attractor)
    dt=0.01            # Time step for dense output
)
```

**Recommendations:**
- **t_transient**: 10-20% of t_max to remove initial transient
- **t_max**: Longer for higher resolution (more crossing points)
- **dt**: Small enough to not miss crossings (0.01 is usually good)

### Computational Cost

- **Integration**: O(t_max / dt) time steps
- **Crossing detection**: O(n) where n = number of time steps
- **Memory**: Stores all crossings (typically 100-1000 points)

**Optimization tips:**
- Use adaptive integrators (RK45)
- Only store crossings, not full trajectory
- Parallelize multiple parameter values

## Advanced Applications

### Fractal Dimension Estimation

The Poincaré section can be used to estimate the attractor's dimension:
1. Cover section with boxes of size ε
2. Count boxes N(ε) needed to cover all points
3. Dimension d = lim(ε→0) log N(ε) / log(1/ε)

For Lorenz: d ≈ 2.06 (fractal, between 2D surface and 3D volume)

### Return Maps

Plot x_n vs x_{n+1} (successive crossing points) to see the **return map**:
- Shows how dynamics evolve from one crossing to the next
- Can identify periodic windows and chaos
- Reveals the one-dimensional structure underlying 3D flow

### First Return Time

Plot the time between successive crossings:
- Periodic orbits → constant return time
- Chaotic attractors → distribution of return times
- Can detect intermittency and clustering

## Troubleshooting

**Problem**: No crossings detected
- **Solution**: Check that trajectory actually crosses the plane (try different initial conditions)
- **Solution**: Ensure plane_value is within attractor's range

**Problem**: Too few points in section
- **Solution**: Increase t_max (integrate longer)
- **Solution**: Decrease dt (finer time resolution)

**Problem**: Section looks random, not structured
- **Solution**: Check you're in chaotic regime (verify parameters)
- **Solution**: Remove longer transient (increase t_transient)
- **Solution**: Verify equations are correct

**Problem**: Section shows only a few points (expecting chaos)
- **Solution**: You may be in periodic regime - check parameter values
- **Solution**: Try different initial conditions

## References & Further Reading

**Classic Papers:**
- Poincaré, H. (1890). "Sur le problème des trois corps et les équations de la dynamique"
- Lorenz, E. (1963). "Deterministic Nonperiodic Flow"

**Books:**
- Strogatz, "Nonlinear Dynamics and Chaos" (Section 12.4)
- Alligood, Sauer & Yorke, "Chaos: An Introduction to Dynamical Systems"

**Connections:**
- Use with bifurcation diagrams (`bifurcation.py`) to see parameter evolution
- Combine with Lyapunov calculations (`lyapunov.py`) for quantitative chaos measures
- Compare with 3D visualizations (`attractors.py`) for complete picture

---

*Created by Alice & Bob as part of the Strange Attractors exploration project.*
