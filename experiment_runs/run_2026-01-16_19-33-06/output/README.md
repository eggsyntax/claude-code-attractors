# Strange Attractors Explorer

A Python toolkit for exploring and visualizing strange attractors - deterministic chaotic systems that produce beautiful, never-repeating trajectories in phase space.

## What Are Strange Attractors?

Strange attractors are fascinating mathematical objects that sit at the intersection of order and chaos. They arise from simple deterministic differential equations, yet produce trajectories that never repeat and are highly sensitive to initial conditions. Despite this apparent randomness, the trajectories are confined to specific regions of phase space, creating intricate geometric structures.

Three beautiful examples are:

- **Lorenz Attractor**: Discovered by Edward Lorenz in 1963 while studying atmospheric convection. Its iconic butterfly shape has become synonymous with chaos theory.

- **Rössler Attractor**: Introduced by Otto Rössler in 1976 as a simpler system that still exhibits chaotic behavior with beautiful spiral dynamics.

- **Thomas Attractor**: Introduced by René Thomas as a model with elegant cyclical symmetry. Its distinctive circular flow pattern and rotational balance make it visually unique among strange attractors.

## Features

- **🌐 Standalone Web Explorer** - zero-installation browser-based interface for instant exploration
- **Clean, modular implementation** of classic strange attractors
- **Unified Dashboard** - integrated interface bringing all tools together
- **Static visualizations** using matplotlib for publication-quality figures
- **Interactive 3D visualizations** using plotly for exploration
- **Parameter exploration** - see how attractors morph as parameters change
- **Temporal animations** - watch trajectories evolve and demonstrate the butterfly effect
- **Bifurcation analysis** - systematic study of transitions from order to chaos
- **Lyapunov exponents** - quantify chaos and compute predictability horizons
- **Poincaré sections** - reveal hidden fractal structure through 2D slices
- **Combined visualizations** - connect qualitative behavior with quantitative measures
- **Art Gallery** - publication-quality artistic renderings with advanced aesthetics
- **Project Visualization** - meta-maps showing the structure of the project itself
- **Extensible design** - easy to add new attractor systems
- **Comprehensive test suite** - verify mathematical correctness

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 🌐 Instant Web Explorer (No Installation Required!)

The fastest way to explore strange attractors is through our **standalone web interface**:

Simply open `standalone_web_explorer.html` in any modern web browser (Chrome, Firefox, Safari, Edge). No Python, no installation, no dependencies—just double-click and explore!

**Features:**
- ✨ All three attractors (Lorenz, Rössler, Thomas) with instant switching
- 🎛️ Real-time parameter adjustment with interactive sliders
- 🦋 Butterfly effect demonstration showing trajectory divergence
- 🔄 Rotate, zoom, and explore from any angle
- 💾 Export trajectory data to CSV
- 📱 Mobile-responsive design
- 🎨 Beautiful, modern interface with gradient backgrounds

**Perfect for:**
- Quick exploration without technical setup
- Sharing with students or colleagues via email
- Presentations and demonstrations
- Mobile/tablet exploration
- Anyone curious about chaos theory

This was created as the final contribution of our collaboration—a bridge between technical rigor and universal accessibility.

---

### Basic Usage (Python API)

```python
from attractors import LorenzAttractor, RosslerAttractor

# Create and simulate a Lorenz attractor
lorenz = LorenzAttractor(sigma=10.0, rho=28.0, beta=8/3)
trajectory = lorenz.simulate(duration=50.0, dt=0.01)

# Create a static matplotlib plot
fig, ax = lorenz.plot_3d_matplotlib(trajectory, title="Lorenz Attractor")

# Or create an interactive plotly visualization
fig = lorenz.plot_3d_interactive(trajectory)
fig.show()
```

### Generate Static Images

```bash
python attractors.py
```

This will generate PNG files of both the Lorenz and Rössler attractors with their classic parameter values.

### Interactive Exploration

```bash
python interactive_explorer.py
```

This creates three interactive HTML visualizations:
- `lorenz_explorer.html` - Explore how the Lorenz attractor changes with the Rayleigh number (ρ)
- `rossler_explorer.html` - Explore how the Rössler attractor changes with parameter c
- `comparison.html` - Side-by-side comparison of both attractors

Open these files in any web browser to interact with them.

### Unified Dashboard

```bash
python chaos_dashboard.py
```

This generates a comprehensive suite of interactive HTML visualizations:
- `dashboard_*_3d.html` - Interactive 3D exploration of each attractor
- `dashboard_comparison.html` - Side-by-side comparison of all three systems
- `dashboard_*_butterfly.html` - Butterfly effect demonstrations
- `dashboard_*_sensitivity.html` - Parameter sensitivity analysis
- `dashboard_summary.md` - Complete system summary

The dashboard provides a unified entry point for exploring all visualization and analysis tools. See [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) for detailed usage.

## The Mathematics

### Lorenz Attractor

The Lorenz system models simplified atmospheric convection:

```
dx/dt = σ(y - x)
dy/dt = x(ρ - z) - y
dz/dt = xy - βz
```

**Parameters:**
- σ (sigma): Prandtl number - ratio of momentum diffusivity to thermal diffusivity
- ρ (rho): Rayleigh number - relates to temperature difference
- β (beta): Geometric factor

**Classic values:** σ=10, ρ=28, β=8/3

The butterfly shape emerges when ρ > 24.74 (approximately). Below this, the system settles into fixed points.

### Rössler Attractor

A simpler system with rich dynamics:

```
dx/dt = -y - z
dy/dt = x + ay
dz/dt = b + z(x - c)
```

**Classic values:** a=0.2, b=0.2, c=5.7

Parameter c is particularly interesting - varying it shows transitions from periodic to chaotic behavior.

### Thomas Attractor

A system with elegant cyclical symmetry:

```
dx/dt = sin(y) - b·x
dy/dt = sin(z) - b·y
dz/dt = sin(x) - b·z
```

**Classic value:** b=0.208186

The Thomas attractor has distinctive circular flow with rotational symmetry. Unlike the asymmetric Lorenz butterfly or single-lobed Rössler spiral, Thomas creates balanced, interconnected loops. The trigonometric coupling (each variable depending on the sine of the next in a cycle) produces smooth, flowing dynamics.

**To explore:**

```bash
python thomas_attractor.py
```

This generates static visualizations, interactive 3D plots, and multi-view projections showing the attractor's symmetrical structure.

## Exploring Parameter Space

One of the most fascinating aspects of strange attractors is how dramatically they change with parameters:

**Lorenz System (varying ρ):**
- ρ < 1: All trajectories decay to origin
- 1 < ρ < 13.926: Trajectories converge to fixed points
- 13.926 < ρ < 24.74: Complex periodic behavior
- ρ > 24.74: Chaotic attractor emerges
- ρ = 28: Classic butterfly shape

**Rössler System (varying c):**
- Small c: Simple periodic orbits
- c ≈ 2-4: Period-doubling cascade
- c ≈ 5.7: Chaotic attractor
- Larger c: More complex chaotic behavior

**Thomas System (varying b):**
- b < 0.15: More spread out, complex multi-loop structure
- b ≈ 0.208186: Classic compact attractor with clear loops
- b > 0.3: More compressed, simpler trajectories
- Sweet spot: b ≈ 0.208186 for most interesting behavior

Use the interactive explorers to see these transitions yourself!

## Code Structure

```
chaos_dashboard.py          - Unified interactive dashboard (all tools integrated)
attractors.py                - Core attractor classes and visualization methods
thomas_attractor.py         - Thomas attractor implementation with cyclical symmetry
interactive_explorer.py      - Interactive visualizations with parameter sliders
temporal_viz.py              - Trajectory animations and butterfly effect demos
bifurcation.py              - Bifurcation diagram generation
thomas_bifurcation.py       - Thomas-specific bifurcation analysis
lyapunov.py                 - Lyapunov exponent calculations
bifurcation_lyapunov.py     - Combined bifurcation and Lyapunov visualizations
poincare.py                 - Poincaré section analysis and visualization
demo_poincare.py            - Quick Poincaré section demonstration
comparative_analysis.py      - Side-by-side comparison of all three attractors
art_gallery.py              - Publication-quality artistic renderings
run_all.py                  - Convenience script to generate all analyses
test_dashboard.py           - Test suite for unified dashboard
test_attractors.py          - Test suite for core attractor functionality
test_thomas.py              - Test suite for Thomas attractor
test_bifurcation.py         - Test suite for bifurcation analysis
test_thomas_bifurcation.py  - Test suite for Thomas bifurcation analysis
test_lyapunov.py            - Test suite for Lyapunov exponent calculations
test_poincare.py            - Test suite for Poincaré section analysis
test_art_gallery.py         - Test suite for artistic rendering
DASHBOARD_GUIDE.md          - Complete guide to unified dashboard
VISUALIZATION_GUIDE.md      - Guide to understanding visualizations
BIFURCATION_GUIDE.md        - Deep dive into bifurcation analysis
LYAPUNOV_GUIDE.md           - Complete guide to Lyapunov exponents
POINCARE_GUIDE.md           - Complete guide to Poincaré sections
THOMAS_GUIDE.md             - Complete guide to Thomas attractor
ART_GALLERY_GUIDE.md        - Complete guide to publication-quality visualizations
COLLABORATION_SUMMARY.md    - Story of our collaborative journey
requirements.txt            - Python package dependencies
README.md                   - This file
```

The `Attractor` base class provides a common interface, making it easy to add new systems. Each specific attractor (Lorenz, Rössler) inherits from this base and implements its differential equations.

## Adding New Attractors

To add a new attractor system:

1. Create a new class inheriting from `Attractor`
2. Implement the `equations()` method with your differential equations
3. Optionally override `default_initial_state()` for sensible defaults
4. That's it! All visualization methods work automatically.

Example:

```python
class MyAttractor(Attractor):
    def __init__(self, param1=1.0, param2=2.0):
        self.param1 = param1
        self.param2 = param2
        super().__init__()

    def equations(self, t, state):
        x, y, z = state
        # Your differential equations here
        dx_dt = ...
        dy_dt = ...
        dz_dt = ...
        return np.array([dx_dt, dy_dt, dz_dt])
```

## Temporal Visualizations

The `temporal_viz.py` module extends our exploration to show how attractors evolve through time:

### Trajectory Animation

Watch as a trajectory is drawn through phase space in real-time:

```bash
python temporal_viz.py
```

This creates animated visualizations showing:
- A point moving through the attractor, leaving a trail
- The aperiodic (never-repeating) nature of the trajectory
- The intricate path through 3D phase space

### The Butterfly Effect

The hallmark of chaos: infinitesimal differences in initial conditions lead to completely different outcomes.

Our butterfly effect visualizations show:
- Multiple trajectories from nearly identical starting points (within 1e-6)
- Exponential divergence over time
- Quantitative plots showing the rate of separation
- Dual views combining spatial and temporal perspectives

**Key insight**: Despite the equations being fully deterministic, long-term prediction is impossible. This is the essence of deterministic chaos.

## Bifurcation Analysis

Understanding how chaos emerges as parameters change:

```bash
python bifurcation.py
```

Creates bifurcation diagrams showing:
- **Lorenz (ρ)**: Transition from fixed points → periodic → chaotic around ρ ≈ 24.74
- **Rössler (c)**: Beautiful period-doubling cascade (1 → 2 → 4 → 8 → chaos)
- Periodic windows within chaos
- The complete route from order to chaos

See `BIFURCATION_GUIDE.md` for detailed explanation.

## Lyapunov Exponents

Quantifying chaos with mathematical precision:

```bash
python lyapunov.py
```

Computes:
- **Largest Lyapunov exponent λ_max**: Rate of exponential divergence
- **Full spectrum**: Complete characterization of expansion/contraction
- **Predictability horizons**: How long before forecasts become useless
- **λ vs parameter plots**: Shows exactly where chaos emerges

For the Lorenz system at ρ=28: λ ≈ 0.9, giving a predictability horizon of ~1.1 time units.

### Combined Analysis

See how bifurcation structure relates to Lyapunov exponents:

```bash
python bifurcation_lyapunov.py
```

Creates dual-panel plots showing:
- Top: Bifurcation diagram (what happens)
- Bottom: Lyapunov exponent (how chaotic it is)
- The λ=0 crossing marks the precise transition to chaos

This beautifully connects qualitative behavior with quantitative measures.

See `LYAPUNOV_GUIDE.md` for complete mathematical background.

## Poincaré Sections

Revealing the hidden fractal structure of strange attractors:

```bash
python poincare.py
```

Creates Poincaré sections - 2D slices through 3D phase space that show:
- **Lorenz**: Two-lobed butterfly structure with fractal folding
- **Rössler**: Spiral patterns showing rotational dynamics
- **Parameter comparison**: How structure changes from order to chaos
- **Fractal geometry**: Self-similar patterns at multiple scales

**What is a Poincaré section?**

Instead of viewing the full 3D trajectory, we record points where it crosses a chosen plane (e.g., z=27 for Lorenz). This reduces the continuous flow to a discrete map, revealing:
- Fractal structure invisible in 3D views
- The folding mechanism that creates chaos
- Clear distinction between periodic and chaotic regimes

**Quick demo:**

```bash
python demo_poincare.py
```

See `POINCARE_GUIDE.md` for complete mathematical background and interpretation guide.

## Comparative Analysis

Understanding the spectrum of chaos across different systems:

```bash
python comparative_analysis.py
```

Creates comprehensive comparisons showing:
- **Attractor Gallery**: All three attractors visualized side-by-side with consistent viewing angles
- **Characteristics Table**: Detailed comparison of mathematical properties, symmetries, and behavior
- **Butterfly Effect Comparison**: How sensitive dependence manifests differently in each system

**Key findings:**
- **Lorenz**: Highly chaotic (λ ≈ 0.9), short predictability (τ ≈ 1.1), asymmetric butterfly structure
- **Rössler**: Moderately chaotic (λ ≈ 0.2-0.4), medium predictability (τ ≈ 3-5), single spiral
- **Thomas**: Gentler chaos (λ ≈ 0.05-0.1), longer predictability (τ ≈ 14), threefold rotational symmetry

All three are chaotic (positive Lyapunov exponents), but each has its own distinct personality!

**Thomas-specific bifurcation:**

```bash
python thomas_bifurcation.py
```

Analyzes how the Thomas attractor transitions to chaos:
- Individual bifurcation diagram varying parameter b
- Comparative diagram showing all three routes to chaos:
  - Thomas: Gradual transition as b decreases
  - Lorenz: Sharp bifurcation at ρ ≈ 24.74
  - Rössler: Period-doubling cascade

This shows that chaos emerges through different mechanisms in different systems!

## Art Gallery: Publication-Quality Visualizations

For presentations, papers, or display:

```bash
python art_gallery.py
```

Creates high-resolution (300 DPI), publication-quality artistic renderings:

**Outputs:**
- `attractor_triptych.png` - Three-panel comparison with fire/ice/gradient color schemes
- `lorenz_perspectives.png` - Four viewing angles showing structure from all sides
- `lorenz_highres.png` - Single high-res render with fire colormap
- `rossler_highres.png` - Single high-res render with ice colormap
- `thomas_highres.png` - Single high-res render with gradient colormap

**Key features:**
- **300 DPI resolution** suitable for publication and printing
- **Density-based alpha blending** creates fade-in effect along trajectories
- **Custom color schemes**: Fire (warm), Ice (cool), Gradient (subtle), Monochrome, Rainbow
- **Minimalist aesthetic**: Clean design emphasizing the attractor's natural beauty
- **Temporal color mapping**: Colors progress along trajectory to show flow

**Advanced usage:**

```python
from art_gallery import ArtisticRenderer

renderer = ArtisticRenderer(dpi=300, figsize=(12, 8))

# High-res Lorenz with monochrome for publication
renderer.render_high_res_single('lorenz', 'monochrome', 'figure1.png')

# Four perspectives of Thomas
renderer.render_multi_perspective('thomas', 'thomas_4views.png')

# Custom triptych at lower DPI for web
web_renderer = ArtisticRenderer(dpi=150)
web_renderer.render_triptych('attractors_web.png')
```

See `ART_GALLERY_GUIDE.md` for complete documentation on color schemes, viewing angles, rendering techniques, and integration with publication workflows.

## Testing

Comprehensive test suites verify mathematical correctness:

```bash
python test_attractors.py           # Core functionality
python test_thomas.py               # Thomas attractor
python test_bifurcation.py          # Bifurcation analysis
python test_thomas_bifurcation.py   # Thomas bifurcation analysis
python test_lyapunov.py             # Lyapunov calculations
python test_poincare.py             # Poincaré sections
python test_art_gallery.py          # Art Gallery rendering
```

Tests include:
- Correctness of differential equations
- Mathematical symmetries (cyclical, mirror, rotational)
- Trajectory properties (continuity, boundedness)
- Bifurcation structure (period-doubling, chaos transitions)
- Lyapunov exponent signatures (+, 0, -) for strange attractors
- Poincaré crossing detection and section properties
- Phase volume dissipation
- The butterfly effect (sensitivity to initial conditions)
- Comparative chaos analysis across systems

## Project Meta-Visualization

Want to see the structure of this project itself?

```bash
python project_map.py
```

This generates meta-visualizations showing:
- How components relate to each other
- The evolution of contributions over 10 collaborative turns
- The architecture and dependency graph
- Key insights discovered along the way

A fitting conclusion to a project about emergence - visualizing the emergent structure of our collaboration using the tools we built to study emergence itself.

## Future Directions

Some ideas for extending this project:

- **More attractors**: Dadras, Chen, Aizawa, and many others
- **Interactive bifurcation explorer**: Click on diagram to see corresponding attractor
- **Return maps**: From Poincaré sections, analyze x_n vs x_{n+1}
- **Higher dimensions**: Attractors in 4D+ with dimensional reduction for visualization
- **Kaplan-Yorke dimension**: Calculate fractal dimensionality from Lyapunov spectrum
- **Local Lyapunov exponents**: Map chaos strength across phase space
- **Interactive Poincaré explorer**: Animate how sections change with parameters

## References

- Lorenz, E. N. (1963). "Deterministic nonperiodic flow". Journal of the Atmospheric Sciences.
- Rössler, O. E. (1976). "An equation for continuous chaos". Physics Letters A.
- Strogatz, S. H. (2015). "Nonlinear Dynamics and Chaos". Westview Press.

## About This Project

This is a collaborative exploration between Alice and Bob over 10 turns of dialogue. What started as a simple idea to visualize strange attractors evolved into a comprehensive toolkit that's simultaneously:

- **Rigorous**: Comprehensive testing, verified mathematics, quantitative analysis
- **Beautiful**: Artistic visualizations, elegant code, aesthetic sensitivity
- **Educational**: Complete learning path from beginner to advanced
- **Extensible**: Modular architecture ready for new systems and analyses

The project itself demonstrates emergence - simple contributions building iteratively into something richer than either contributor could have designed alone. We studied chaos and experienced emergence firsthand through our collaboration.

See [CLOSING_REFLECTION.md](CLOSING_REFLECTION.md) for the full story of how this evolved.

## Contributing

This project is complete as a demonstration, but the architecture is designed for extension. Feel free to:
- Add new attractors (the base class makes this straightforward)
- Implement additional analysis methods
- Create new visualization approaches
- Extend the comparative framework
- Use these tools in your own research or education

The code is well-documented, thoroughly tested, and built with extension in mind.

---

*"The most beautiful thing we can experience is the mysterious." - Albert Einstein*

*"In the end, chaos has structure, determinism doesn't mean predictability, simple rules create infinite complexity, and two perspectives together see more than either alone." - Alice & Bob*
