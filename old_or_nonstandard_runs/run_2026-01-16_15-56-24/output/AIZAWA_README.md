# Aizawa Attractor

A complete implementation of the Aizawa chaotic attractor with comprehensive analysis and visualization capabilities.

## Overview

The Aizawa attractor is a three-dimensional chaotic dynamical system discovered by Yoji Aizawa. It produces visually stunning trajectories with a complex, multi-lobed structure that differs significantly from both the Lorenz and Rössler attractors. The system exhibits moderate chaos (Lyapunov exponent λ₁ ≈ 0.15) and has a distinctive visual appearance characterized by intricate, rotating patterns.

## Mathematical Description

### System Equations

```
dx/dt = (z - b) * x - d * y
dy/dt = d * x + (z - b) * y
dz/dt = c + a * z - (z³)/3 - (x² + y²) * (1 + e * z) + f * z * x³
```

### Default Parameters

For standard chaotic behavior:
- **a = 0.95**: z-damping coefficient
- **b = 0.7**: z-shift in x,y equations
- **c = 0.6**: constant forcing term
- **d = 3.5**: rotation rate (couples x and y)
- **e = 0.25**: nonlinear coupling strength
- **f = 0.1**: cubic coupling strength

### Properties

- **Dimension**: 3D continuous-time system
- **Type**: Dissipative dynamical system
- **Lyapunov exponent**: λ₁ ≈ 0.15 (weakly to moderately chaotic)
- **Fractal dimension**: D₂ ≈ 2.2
- **Symmetry**: Approximate rotational symmetry around z-axis
- **Boundedness**: Trajectories remain bounded in phase space

## Quick Start

### Basic Usage

```python
from aizawa import AizawaAttractor
from visualizer import AttractorVisualizer

# Create attractor with default parameters
aizawa = AizawaAttractor()

# Generate trajectory
trajectory = aizawa.generate_trajectory(t_span=(0, 500), n_points=50000)

# Visualize
vis = AttractorVisualizer()
vis.plot_trajectory_3d(trajectory, title="Aizawa Attractor", color='purple')
```

### Custom Parameters

```python
# Use alternative parameter set
params = AizawaAttractor.parameter_recommendations()
aizawa = AizawaAttractor(**params['alternative_chaotic'])
trajectory = aizawa.generate_trajectory(t_span=(0, 500), n_points=50000)
```

### Butterfly Effect Demonstration

```python
# Generate two trajectories with tiny initial difference
traj1, traj2 = aizawa.generate_butterfly_effect_demo(
    t_span=(0, 500),
    n_points=50000,
    perturbation=1e-8
)

# Visualize divergence
import analysis
divergence = analysis.compute_divergence(traj1, traj2)
vis.plot_divergence(divergence, log_scale=True)
```

## Parameter Regimes

The `parameter_recommendations()` method provides pre-configured parameter sets:

### 1. Chaotic (Default)
```python
{'a': 0.95, 'b': 0.7, 'c': 0.6, 'd': 3.5, 'e': 0.25, 'f': 0.1}
```
- **Behavior**: Moderate chaos with complex structure
- **Visual**: Multi-lobed, rotating patterns
- **Use case**: Standard exploration and demonstrations

### 2. Alternative Chaotic
```python
{'a': 0.85, 'b': 0.7, 'c': 0.55, 'd': 3.5, 'e': 0.25, 'f': 0.1}
```
- **Behavior**: Slightly different chaotic dynamics
- **Visual**: Similar but subtly different structure
- **Use case**: Parameter sensitivity studies

### 3. More Symmetric
```python
{'a': 0.95, 'b': 0.65, 'c': 0.6, 'd': 3.5, 'e': 0.2, 'f': 0.15}
```
- **Behavior**: Chaotic with enhanced symmetry
- **Visual**: More regular appearance
- **Use case**: Exploring symmetry-chaos relationship

### 4. Weaker Chaos
```python
{'a': 0.8, 'b': 0.7, 'c': 0.5, 'd': 3.0, 'e': 0.25, 'f': 0.1}
```
- **Behavior**: Less chaotic, more regular
- **Visual**: Simpler patterns
- **Use case**: Comparing weak vs strong chaos

## Complete Analysis Workflow

### Comprehensive Analysis with Chaos Reporter

```python
from aizawa import AizawaAttractor
from chaos_reporter import ChaosReporter

# Create attractor
aizawa = AizawaAttractor()

# Generate comprehensive report
reporter = ChaosReporter()
text_file, pdf_file = reporter.generate_full_report(
    aizawa,
    output_dir='aizawa_analysis'
)

# Report includes:
# - 3D trajectory visualization
# - Phase space projections
# - Poincaré section analysis
# - Return map
# - Lyapunov exponent estimation
# - Divergence quantification
# - Text summary with interpretations
```

### Manual Analysis Pipeline

```python
import analysis
from visualizer import AttractorVisualizer

# Generate trajectory
trajectory = aizawa.generate_trajectory(t_span=(0, 500), n_points=50000)

# Compute Poincaré section
section = aizawa.compute_poincare_section(
    trajectory,
    plane='z',
    plane_value=0.0,
    direction='up',
    method='interpolation'
)

# Compute return map
return_map = analysis.compute_return_map(section, dimension=0, delay=1)

# Estimate Lyapunov exponent
lyapunov = analysis.estimate_lyapunov_exponents(
    aizawa,
    n_trajectories=10,
    n_iterations=1000,
    include_diagnostics=True
)

# Visualize everything
vis = AttractorVisualizer()
vis.plot_trajectory_3d(trajectory, title="Aizawa Attractor", color='purple')
vis.plot_poincare_section_2d(section, use_sequence_colors=True)
vis.plot_return_map(return_map)
vis.plot_lyapunov_convergence(lyapunov, show_confidence=True)

print(f"Lyapunov exponent: λ₁ = {lyapunov['exponent']:.3f}")
```

## Comparing with Other Attractors

### Three-Way Comparison

```python
from lorenz import LorenzAttractor
from rossler import RosslerAttractor
from aizawa import AizawaAttractor
from chaos_reporter import ChaosReporter

# Create all three attractors
lorenz = LorenzAttractor()
rossler = RosslerAttractor()
aizawa = AizawaAttractor()

# Generate comparative report
reporter = ChaosReporter()
reporter.compare_attractors(
    [lorenz, rossler, aizawa],
    attractor_names=["Lorenz", "Rössler", "Aizawa"],
    output_dir='three_way_comparison'
)
```

### Key Differences

| Attractor | Structure | Chaos Strength (λ₁) | Visual Character |
|-----------|-----------|---------------------|------------------|
| **Lorenz** | Double-lobed butterfly | ~0.9 (strong) | Symmetric wings |
| **Rössler** | Single-lobed spiral | ~0.07 (weak) | Simple spiral |
| **Aizawa** | Multi-lobed complex | ~0.15 (moderate) | Intricate patterns |

## Integration with Analysis Tools

### All analysis tools work seamlessly with Aizawa:

**Poincaré Sections**:
```python
section = aizawa.compute_poincare_section(trajectory, plane='z', plane_value=0.0)
```

**Return Maps**:
```python
return_map = analysis.compute_return_map(section)
```

**Lyapunov Exponents**:
```python
lyapunov = analysis.estimate_lyapunov_exponents(aizawa)
```

**Divergence Analysis**:
```python
traj1, traj2 = aizawa.generate_butterfly_effect_demo()
divergence = analysis.compute_divergence(traj1, traj2)
```

**Time-Delay Embedding** (Takens' Theorem):
```python
x_series = trajectory[:, 0]  # Just the x-coordinate
embedded = analysis.compute_time_delay_embedding(x_series, delay=10, embedding_dim=3)
```

## Technical Details

### Implementation

- **Base class**: Inherits from `AttractorBase`
- **Integration**: Uses scipy's `solve_ivp` with RK45 adaptive stepping
- **Validation**: 40+ comprehensive tests covering all functionality
- **Documentation**: Extensive docstrings with examples

### Performance Notes

**Recommended settings for smooth visualization:**
```python
trajectory = aizawa.generate_trajectory(
    t_span=(0, 500),      # Long enough to explore the attractor
    n_points=50000,       # Dense sampling for smooth curves
    method='RK45'         # Good balance of speed and accuracy
)
```

**For quick exploration:**
```python
trajectory = aizawa.generate_trajectory(
    t_span=(0, 200),
    n_points=10000,
    method='RK23'         # Faster, slightly less accurate
)
```

**For publication-quality analysis:**
```python
trajectory = aizawa.generate_trajectory(
    t_span=(0, 1000),     # Very long trajectory
    n_points=100000,      # Very dense sampling
    method='DOP853',      # Highest accuracy
    rtol=1e-10,
    atol=1e-12
)
```

### Typical Computation Times

On a modern CPU:
- 10,000 points: ~0.1 seconds
- 50,000 points: ~0.5 seconds
- 100,000 points: ~1 second

## Physical Interpretation

While the Aizawa attractor is primarily a mathematical construction (not derived from physical laws like the Lorenz attractor), it exhibits several interesting features:

1. **Rotational Coupling**: The 'd' parameter creates rotation in the x-y plane
2. **Vertical Damping**: The 'a' parameter controls z-direction damping
3. **Nonlinear Feedback**: The z³ and x³ terms create rich nonlinear dynamics
4. **Energy Dissipation**: The system is dissipative, causing volume contraction in phase space

## Theoretical Background

### Chaos Characteristics

- **Sensitive Dependence**: Tiny initial differences grow exponentially
- **Bounded**: Despite chaos, trajectories stay in a finite region
- **Aperiodic**: Never repeats exactly
- **Deterministic**: No randomness; fully determined by initial conditions
- **Strange Attractor**: Trajectories converge to a fractal set

### Lyapunov Exponents

The Aizawa attractor has three Lyapunov exponents:
- **λ₁ ≈ +0.15**: Positive (sensitive dependence, chaos)
- **λ₂ ≈ 0**: Zero (marginal stability along flow)
- **λ₃ < 0**: Negative (volume contraction, dissipation)

The sum λ₁ + λ₂ + λ₃ < 0 confirms the system is dissipative.

## Examples

### Example 1: Basic Visualization

```python
from aizawa import AizawaAttractor
import matplotlib.pyplot as plt

aizawa = AizawaAttractor()
trajectory = aizawa.generate_trajectory(t_span=(0, 500), n_points=50000)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
        linewidth=0.5, alpha=0.7, color='purple')
ax.set_title("Aizawa Attractor")
plt.show()
```

### Example 2: Parameter Exploration

```python
params_list = AizawaAttractor.parameter_recommendations()

for regime_name, params in params_list.items():
    aizawa = AizawaAttractor(**params)
    trajectory = aizawa.generate_trajectory(t_span=(0, 200), n_points=20000)
    # Plot or analyze each regime...
```

### Example 3: Quantifying Chaos

```python
import analysis

aizawa = AizawaAttractor()

# Estimate Lyapunov exponent
lyapunov = analysis.estimate_lyapunov_exponents(aizawa, include_diagnostics=True)

print(f"Lyapunov Exponent: λ₁ = {lyapunov['exponent']:.3f} ± {lyapunov['std_error']:.3f}")
print(f"Converged: {lyapunov['convergence_data']['converged']}")

if lyapunov['exponent'] > 0.1:
    print("Interpretation: CHAOTIC")
elif lyapunov['exponent'] > 0:
    print("Interpretation: WEAKLY CHAOTIC")
else:
    print("Interpretation: REGULAR (not chaotic)")
```

## Testing

Run the comprehensive test suite:

```bash
pytest test_aizawa.py -v
```

Test coverage includes:
- Initialization and parameter management
- Derivative calculations
- Trajectory generation and boundedness
- Sensitivity to initial conditions
- Parameter regimes
- Butterfly effect demonstration
- Integration with analysis tools
- Edge cases and error handling
- Comparison with other attractors

## References

1. Aizawa, Y. (1982). "Synergetic approach to the phenomena of mode-locking in nonlinear systems"
2. Sprott, J.C. (2003). "Chaos and Time-Series Analysis", Oxford University Press
3. Strogatz, S.H. (2015). "Nonlinear Dynamics and Chaos", Westview Press

## Related Modules

- `attractor_base.py`: Base class defining the attractor interface
- `lorenz.py`: The classic Lorenz attractor
- `rossler.py`: The Rössler attractor
- `analysis.py`: Quantitative analysis tools
- `visualizer.py`: Visualization capabilities
- `chaos_reporter.py`: Automated comprehensive reporting

## Authors

Created as part of the Alice & Bob Chaotic Attractor Toolkit collaboration, January 2026.

---

**The trinity is complete: Lorenz, Rössler, and Aizawa.** 🦋
