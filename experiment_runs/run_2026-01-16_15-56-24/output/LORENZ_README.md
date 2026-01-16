# Lorenz Attractor Implementation

## Overview

This module provides a complete implementation of the **Lorenz attractor** - one of the most famous examples of deterministic chaos in dynamical systems. The Lorenz system was discovered by Edward Lorenz in 1963 while studying atmospheric convection, and it became the canonical example of the "butterfly effect."

## Components

### Core Framework

#### `attractor_base.py`
Abstract base class for all dynamical system attractors. Provides:
- Numerical integration using scipy's `solve_ivp` with RK45 adaptive step size
- Parameter management and validation
- Initial state configuration
- Trajectory generation interface
- System information retrieval

All specific attractors (Lorenz, Rössler, Aizawa, etc.) inherit from this base class.

#### `lorenz.py`
Implementation of the Lorenz attractor system:

**System equations:**
```
dx/dt = σ(y - x)
dy/dt = x(ρ - z) - y
dz/dt = xy - βz
```

**Parameters:**
- **σ (sigma)**: Prandtl number - relates viscosity to thermal conductivity
- **ρ (rho)**: Rayleigh number - relates buoyancy to viscosity
- **β (beta)**: Geometric factor

**Default chaotic parameters:** σ=10, ρ=28, β=8/3

### Testing

#### `test_attractor_base.py`
Comprehensive test suite for the base attractor framework:
- Initialization and configuration
- Trajectory generation with different methods
- Parameter management
- Edge cases and error handling
- Reproducibility verification

#### `test_lorenz.py`
Tests specific to the Lorenz system:
- Differential equation correctness
- Trajectory boundedness
- Butterfly effect verification
- Parameter regime exploration
- Physical behavior validation

### Demonstrations

#### `demo_lorenz.py`
Complete demonstration script showing:
1. **Basic Lorenz attractor** - Classic butterfly shape
2. **Butterfly effect** - Sensitive dependence on initial conditions
3. **Phase space projections** - 2D views of the 3D attractor
4. **Parameter exploration** - Different dynamical regimes
5. **Time evolution animation** - Watch the trajectory evolve

## Quick Start

### Basic Usage

```python
from lorenz import LorenzAttractor
from visualizer import AttractorVisualizer

# Create attractor with default chaotic parameters
lorenz = LorenzAttractor()

# Generate a trajectory
trajectory = lorenz.generate_trajectory(
    t_span=(0, 50),    # Integrate from t=0 to t=50
    n_points=10000     # Return 10000 points
)

# Visualize the beautiful butterfly
vis = AttractorVisualizer()
vis.plot_trajectory_3d(trajectory, title="Lorenz Attractor")
```

### Demonstrating the Butterfly Effect

```python
from lorenz import LorenzAttractor

lorenz = LorenzAttractor()

# Generate two trajectories with initial conditions differing by 10^-8
traj1, traj2 = lorenz.generate_butterfly_effect_demo(epsilon=1e-8)

# They start nearly identical but diverge dramatically
import numpy as np
print(f"Initial separation: {np.linalg.norm(traj1[0] - traj2[0]):.2e}")
print(f"Final separation: {np.linalg.norm(traj1[-1] - traj2[-1]):.2f}")
```

### Exploring Parameter Space

```python
from lorenz import LorenzAttractor

# Get recommended parameter sets
recommendations = LorenzAttractor.get_parameter_recommendations()

for name, rec in recommendations.items():
    print(f"{name}: {rec['description']}")

    lorenz = LorenzAttractor(parameters=rec['params'])
    trajectory = lorenz.generate_trajectory(t_span=(0, 50), n_points=5000)
    # Visualize or analyze...
```

## Parameter Regimes

The Lorenz system exhibits different behaviors depending on the ρ parameter:

| ρ range | Behavior | Description |
|---------|----------|-------------|
| ρ < 1 | **Converging** | All trajectories converge to origin |
| 1 < ρ < 13.926 | **Fixed points** | Converges to stable equilibria |
| 13.926 < ρ < 24.74 | **Oscillating** | Periodic oscillations between fixed points |
| ρ ≈ 24.74 | **Onset of chaos** | Transition to chaotic behavior |
| **ρ = 28** | **Classic chaos** | The famous butterfly attractor |
| ρ ≈ 99.96 | **Pre-turbulent** | More complex chaotic structure |
| ρ = 160 | **Periodic** | Returns to periodic behavior |

## API Reference

### LorenzAttractor

```python
class LorenzAttractor(AttractorBase):
    """The Lorenz attractor implementation."""
```

#### Constructor

```python
LorenzAttractor(
    initial_state: Optional[np.ndarray] = None,
    parameters: Optional[Dict[str, float]] = None
)
```

**Args:**
- `initial_state`: Initial [x, y, z]. Default: [1.0, 1.0, 1.0]
- `parameters`: Dict with 'sigma', 'rho', 'beta'. Default: {σ=10, ρ=28, β=8/3}

#### Methods

**`generate_trajectory(t_span, n_points, method='RK45')`**

Generate a trajectory through phase space.

**Args:**
- `t_span`: Tuple (t_start, t_end) for time interval
- `n_points`: Number of points to return
- `method`: Integration method (RK45, RK23, DOP853, etc.)

**Returns:** numpy array of shape (n_points, 3)

---

**`generate_butterfly_effect_demo(epsilon=1e-8, t_span=(0, 40), n_points=10000)`**

Generate two trajectories with nearly identical initial conditions to demonstrate sensitive dependence.

**Args:**
- `epsilon`: Small perturbation to initial conditions
- `t_span`: Time interval
- `n_points`: Number of points

**Returns:** Tuple (trajectory1, trajectory2)

---

**`update_parameters(**kwargs)`**

Update system parameters.

**Example:** `lorenz.update_parameters(rho=99.96, sigma=10.0)`

---

**`set_initial_state(state)`**

Set new initial conditions.

**Args:** `state` - numpy array [x, y, z]

---

**`get_parameter_recommendations()`** (static method)

Get recommended parameter sets for exploring different behaviors.

**Returns:** Dictionary of named parameter sets with descriptions

---

**`get_info()`**

Get current configuration information.

**Returns:** Dict with type, dimension, parameters, initial_state

## Integration with Visualizer

The Lorenz attractor integrates seamlessly with the visualizer component:

```python
from lorenz import LorenzAttractor
from visualizer import AttractorVisualizer

lorenz = LorenzAttractor()
trajectory = lorenz.generate_trajectory(t_span=(0, 50), n_points=10000)

vis = AttractorVisualizer()

# 3D trajectory
vis.plot_trajectory_3d(trajectory, title="Lorenz Attractor")

# Phase space projections
vis.plot_phase_space_projections(trajectory, title="Phase Space Views")

# Multiple trajectories (butterfly effect)
traj1, traj2 = lorenz.generate_butterfly_effect_demo()
vis.plot_multiple_trajectories(
    [traj1, traj2],
    colors=['red', 'blue'],
    labels=['Trajectory 1', 'Trajectory 2']
)

# Animation
anim = vis.animate_trajectory(trajectory, interval=20, trail_length=500)
```

## Mathematical Background

### The Lorenz Equations

The Lorenz system is a 3D autonomous ODE system:

```
dx/dt = σ(y - x)
dy/dt = x(ρ - z) - y
dz/dt = xy - βz
```

### Physical Interpretation

Originally derived from simplified Rayleigh-Bénard convection:
- **x**: Convective flow intensity
- **y**: Horizontal temperature variation
- **z**: Vertical temperature variation
- **σ**: Prandtl number (fluid property)
- **ρ**: Rayleigh number (driving force)
- **β**: Geometric aspect ratio

### Chaotic Behavior

The Lorenz attractor exhibits:
- **Sensitive dependence on initial conditions**: Nearby trajectories diverge exponentially
- **Boundedness**: All trajectories stay in a bounded region
- **Mixing**: Trajectories explore the attractor densely
- **Strange attractor**: Fractal structure with non-integer dimension (~2.06)

### Lyapunov Exponents

For classic parameters (σ=10, ρ=28, β=8/3):
- λ₁ ≈ 0.906 (positive - indicates chaos)
- λ₂ ≈ 0 (zero - volume preservation direction)
- λ₃ ≈ -14.57 (negative - contracting direction)

## Running Tests

```bash
# Test base framework
pytest test_attractor_base.py -v

# Test Lorenz implementation
pytest test_lorenz.py -v

# Run all tests
pytest -v
```

## Running Demos

```bash
python demo_lorenz.py
```

This generates:
- `lorenz_basic.png` - Classic butterfly attractor
- `lorenz_butterfly_effect.png` - Diverging trajectories
- `lorenz_phase_space.png` - Phase space projections
- `lorenz_parameter_exploration.png` - Different parameter regimes
- `lorenz_evolution.gif` - Animated trajectory

## Design Decisions

1. **scipy.integrate.solve_ivp**: Used for robust, adaptive step-size integration
2. **RK45 by default**: Good balance of accuracy and speed
3. **Modular architecture**: Base class makes it easy to add new attractors
4. **Return format**: Trajectories are (n_points, dimension) numpy arrays for easy visualization
5. **Parameter dictionaries**: Flexible parameter management
6. **Comprehensive testing**: Both unit and integration tests ensure correctness

## Future Extensions

This framework is designed to easily support additional attractors:
- **Rössler attractor**: Simpler chaotic system, good for pedagogy
- **Aizawa attractor**: Beautiful multi-lobed structure
- **Chua's circuit**: Electronic chaos
- **Rabinovich-Fabrikant**: Complex 3D chaos
- And many more...

Each new attractor just needs to inherit from `AttractorBase` and implement:
- `derivatives(t, state)` - The differential equations
- `default_parameters()` - Default parameter values
- `default_initial_state()` - Default initial conditions

## References

1. Lorenz, E. N. (1963). "Deterministic Nonperiodic Flow". *Journal of the Atmospheric Sciences*, 20(2): 130-141.
2. Strogatz, S. H. (2015). *Nonlinear Dynamics and Chaos*. Westview Press.
3. Gleick, J. (1987). *Chaos: Making a New Science*. Viking.

## Authors

Developed collaboratively by Alice and Bob as part of the strange attractors exploration project.

## License

This implementation is provided for educational and research purposes.
