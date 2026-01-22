# Thomas Attractor - Complete Guide

## Introduction

The Thomas attractor is a beautiful three-dimensional strange attractor discovered by René Thomas. What makes it distinctive among chaotic systems is its elegant **cyclical symmetry** - unlike the asymmetric Lorenz butterfly or the single-lobed Rössler spiral, the Thomas attractor exhibits a balanced, rotating flow pattern.

## The Mathematics

### Differential Equations

The Thomas system is governed by three coupled differential equations:

```
dx/dt = sin(y) - b·x
dy/dt = sin(z) - b·y
dz/dt = sin(x) - b·z
```

### Parameters

**b** (damping coefficient): Controls the system's behavior
- Classic chaotic value: **b ≈ 0.208186**
- Range of interest: 0.1 ≤ b ≤ 0.4

### Key Properties

1. **Cyclical Structure**: Each variable depends on the sine of the *next* variable in a cycle:
   - x depends on sin(y)
   - y depends on sin(z)
   - z depends on sin(x)

2. **Rotational Symmetry**: The system is nearly symmetric under rotation of coordinates:
   - (x, y, z) → (y, z, x) transforms the equations in a consistent way
   - The attractor has approximate threefold rotational symmetry

3. **Trigonometric Coupling**: Unlike polynomial systems (Lorenz, Rössler), Thomas uses trigonometric functions, creating smooth, flowing dynamics

4. **Bounded Dynamics**: The sine functions keep the system naturally bounded without needing complex parameter tuning

## Visual Characteristics

### The Classic Shape (b = 0.208186)

The Thomas attractor creates a distinctive **circular flow pattern** with several loops that wind around each other. Key visual features:

- **Multiple interconnected loops** arranged symmetrically
- **Circular overall structure** (not butterfly-like or spiral-like)
- **Smooth trajectories** due to trigonometric coupling
- **Balanced appearance** from most viewing angles

### 2D Projections

Unlike the Lorenz attractor (which looks very different from different angles), the Thomas attractor maintains similar appearance across different projections:

- **XY projection**: Circular loops
- **XZ projection**: Similar circular structure
- **YZ projection**: Also circular

This reflects the system's rotational symmetry around the main diagonal (x=y=z line).

## Parameter Exploration

### Effect of b (Damping Coefficient)

The parameter b dramatically affects the attractor's size and complexity:

#### Small b (b < 0.15)
- **More spread out** in phase space
- **Complex multi-loop structure**
- Trajectories explore larger regions
- More chaotic, less compact

#### Classic Value (b ≈ 0.208186)
- **Optimal chaotic behavior**
- **Compact, well-defined loops**
- Beautiful balance between order and chaos
- Most aesthetically pleasing

#### Large b (b > 0.3)
- **More compressed** attractor
- **Simpler trajectories**
- Loops pull closer together
- Less complex dynamics

### Finding Chaos

Unlike some systems with narrow chaotic windows, the Thomas attractor shows chaotic behavior across a fairly wide range of b values (roughly 0.15 to 0.3). However, the "sweet spot" at b ≈ 0.208186 provides the most interesting and visually appealing dynamics.

## Comparison with Other Attractors

| Property | Thomas | Lorenz | Rössler |
|----------|--------|--------|---------|
| **Shape** | Circular loops | Butterfly | Single spiral |
| **Symmetry** | ~3-fold rotational | Mirror symmetry | No symmetry |
| **Coupling** | Trigonometric | Polynomial | Polynomial |
| **Projections** | Similar across views | Very different | Moderately different |
| **Parameter sensitivity** | Moderate | High | High |
| **Visual complexity** | Balanced | High | Moderate |

## Physical Interpretations

While the Thomas attractor was introduced as a mathematical model rather than derived from physical principles, it has connections to:

1. **Feedback Circuits**: The cyclic coupling (x→y→z→x) represents systems where each component influences the next in a loop

2. **Oscillator Networks**: Three coupled oscillators with nonlinear (sinusoidal) coupling

3. **Biological Systems**: Simplified models of regulatory networks with cyclical interactions (though highly abstracted)

The elegance comes from its **mathematical simplicity** rather than physical derivation - it demonstrates that beautiful chaos doesn't require complex equations.

## Computational Considerations

### Integration

The Thomas system integrates cleanly with standard ODE solvers:

```python
from thomas_attractor import ThomasAttractor

thomas = ThomasAttractor(b=0.208186)
trajectory = thomas.simulate(duration=200.0, dt=0.01)
```

**Recommended parameters:**
- Duration: 150-200 time units (to see full structure)
- Time step: dt = 0.01
- Initial condition: Near origin, e.g., [0.1, 0.0, 0.0]

### Transient Behavior

The Thomas attractor settles quickly:
- **Transient period**: ~10-20 time units
- After settling, trajectories stay on the attractor
- No need for long transient elimination (unlike some attractors)

### Numerical Stability

The trigonometric functions provide natural boundedness:
- No risk of trajectories escaping to infinity
- Stable numerical integration
- No special solver settings needed

## Chaotic Properties

### Lyapunov Exponents

For b = 0.208186, the Thomas attractor has:
- **Largest Lyapunov exponent** (λ₁): Positive (~0.05-0.1)
- **Second Lyapunov exponent** (λ₂): Near zero
- **Third Lyapunov exponent** (λ₃): Negative

This signature (+ 0 -) is characteristic of a strange attractor:
- Positive λ₁: Exponential divergence (chaos)
- Zero λ₂: Flow direction (continuous time)
- Negative λ₃: Volume contraction (dissipative)

### Sensitive Dependence

Like all chaotic systems, the Thomas attractor exhibits the butterfly effect:

```python
# Two trajectories starting 10⁻⁸ apart
state1 = [0.1, 0.0, 0.0]
state2 = [0.1 + 1e-8, 0.0, 0.0]

# After 20 time units, they're ~10⁴ times farther apart!
```

### Predictability Horizon

With λ ≈ 0.07, the e-folding time is:
- τ = 1/λ ≈ 14 time units

This means:
- Accurate prediction possible for ~10-15 time units
- Beyond that, chaos dominates
- Much longer than Lorenz (τ ≈ 1.1)!

The Thomas attractor is **less wildly chaotic** than Lorenz - it's chaotic but relatively well-behaved.

## Poincaré Sections

Taking a Poincaré section (e.g., z = 0 plane) reveals:

1. **Loop structure** appears as discrete curves
2. **Fractal folding** visible but less dramatic than Lorenz
3. **Rotational pattern** evident in the point distribution
4. **Multiple intersection curves** corresponding to different loops

The sections show that while the attractor looks circular in 3D, it has complex internal structure.

## Visualization Tips

### Colors

Good color schemes for Thomas:
- **Purple/magenta**: Emphasizes the smooth, elegant flow
- **Viridis**: Shows trajectory progression through time
- **Cyan/blue**: Clean, modern look

### Viewing Angles

Unlike Lorenz (which has a canonical view), Thomas looks good from many angles:
- **Diagonal view** (elevation ≈ 30°, azimuth ≈ 45°): Shows 3D structure
- **Top view**: Reveals circular symmetry
- **Side views**: Each shows similar loop patterns

Try rotating interactively to appreciate the full 3D structure!

### Line Thickness

For publication-quality figures:
- Use **thin lines** (linewidth=0.3-0.5) to see structure
- Include **transparency** (alpha=0.6-0.8) to show depth
- **High point count** (20,000+ points) for smooth curves

## Code Examples

### Basic Visualization

```python
from thomas_attractor import ThomasAttractor

# Create attractor
thomas = ThomasAttractor(b=0.208186)

# Simulate
trajectory = thomas.simulate(duration=200.0, dt=0.01)

# Plot
fig, ax = thomas.plot_3d_matplotlib(trajectory)
fig.savefig('thomas.png', dpi=200)
```

### Parameter Exploration

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

b_values = [0.15, 0.208186, 0.28]
fig = plt.figure(figsize=(15, 5))

for idx, b in enumerate(b_values, 1):
    thomas = ThomasAttractor(b=b)
    traj = thomas.simulate(duration=200.0, dt=0.01)

    ax = fig.add_subplot(1, 3, idx, projection='3d')
    ax.plot(traj[:, 0], traj[:, 1], traj[:, 2],
            linewidth=0.4, alpha=0.7)
    ax.set_title(f'b = {b}')

plt.tight_layout()
plt.savefig('thomas_comparison.png', dpi=200)
```

### Butterfly Effect Demo

```python
import numpy as np

# Near-identical initial conditions
epsilon = 1e-8
state1 = np.array([0.1, 0.0, 0.0])
state2 = state1 + np.array([epsilon, 0, 0])

thomas = ThomasAttractor(b=0.208186)

traj1 = thomas.simulate(duration=50.0, dt=0.01, initial_state=state1)
traj2 = thomas.simulate(duration=50.0, dt=0.01, initial_state=state2)

# Compute separation over time
distances = np.linalg.norm(traj1 - traj2, axis=1)

# Plot divergence
plt.semilogy(distances)
plt.xlabel('Time steps')
plt.ylabel('Distance between trajectories')
plt.title('Butterfly Effect in Thomas Attractor')
```

## Advanced Topics

### Symmetry Analysis

The Thomas attractor has a fascinating near-symmetry. Consider the transformation:

```
T: (x, y, z) → (y, z, x)
```

This is a 120° rotation around the main diagonal. The equations transform as:

```
dx/dt = sin(y) - b·x  →  dy/dt = sin(z) - b·y
dy/dt = sin(z) - b·y  →  dz/dt = sin(x) - b·z
dz/dt = sin(x) - b·z  →  dx/dt = sin(y) - b·x
```

The system is **exactly invariant** under this transformation! This threefold symmetry (C₃) is what gives the attractor its balanced appearance.

### Bifurcation Structure

While the Thomas attractor doesn't show the dramatic period-doubling of Rössler, it does have interesting bifurcations:

- **b < 0.08**: Periodic behavior (limit cycles)
- **b ≈ 0.08-0.15**: Transition region with intermittency
- **b ≈ 0.15-0.35**: Chaotic attractor
- **b > 0.35**: Simpler dynamics, less chaotic

Unlike the sharp Lorenz transition, Thomas has a more gradual entry into chaos.

### Fractal Dimension

The Thomas attractor has a **correlation dimension** of approximately:
- D ≈ 2.1-2.3 (depending on b)

This is:
- Greater than 2 (not a simple surface)
- Less than 3 (fractal, not space-filling)
- Similar to Lorenz (D ≈ 2.06) and Rössler (D ≈ 2.01)

## Connections to Other Systems

### Thomas vs. Cyclic Systems

The cyclic coupling (x→y→z→x) connects Thomas to other cyclic attractors:
- **Rock-paper-scissors dynamics**: Cyclic competition
- **Three-species food chains**: Predator-prey-resource loops
- **Phase-coupled oscillators**: Circular coupling networks

### Generalization

The Thomas attractor can be generalized to N dimensions:

```
dx₁/dt = sin(x₂) - b·x₁
dx₂/dt = sin(x₃) - b·x₂
...
dxₙ/dt = sin(x₁) - b·xₙ
```

For N > 3, these create hyperchaotic attractors (multiple positive Lyapunov exponents).

## References

**Primary Source:**
- Thomas, R. (1999). "Deterministic chaos seen in terms of feedback circuits: Analysis, synthesis, 'labyrinth chaos'". *International Journal of Bifurcation and Chaos*, 9(10), 1889-1905.

**Related Work:**
- Sprott, J. C. (2010). *Elegant Chaos: Algebraically Simple Chaotic Flows*. World Scientific.
- Strogatz, S. H. (2015). *Nonlinear Dynamics and Chaos*. Westview Press.

**Symmetry and Chaos:**
- Golubitsky, M., & Stewart, I. (2002). *The Symmetry Perspective*. Birkhäuser.

## Summary

The Thomas attractor stands out for its:
- ✨ **Elegant simplicity**: Three equations with cyclic symmetry
- 🔄 **Rotational beauty**: Balanced appearance from all angles
- 📐 **Geometric clarity**: Circular loops in 3D space
- 🎨 **Visual appeal**: Smooth, flowing trajectories
- 🔢 **Mathematical interest**: Exact symmetry with chaotic behavior

It's an excellent example of how simple rules can create complex, beautiful patterns - and how chaos can coexist with symmetry.

---

*"Symmetry is a beautiful thing, but when combined with chaos, it becomes profound."*
