# Chaos Reporter - Automated Analysis of Chaotic Systems

**Author:** Bob (with visualizations by Alice)

## Overview

The Chaos Reporter is a comprehensive automated analysis tool that combines all the components Alice and I built together into a single, easy-to-use interface for analyzing chaotic dynamical systems. It generates both quantitative metrics and publication-ready visualizations.

## What It Does

The Chaos Reporter takes any `AttractorBase` instance and automatically:

1. **Generates trajectories** in phase space
2. **Computes Poincaré sections** to reveal attractor structure
3. **Estimates Lyapunov exponents** to quantify chaos strength
4. **Measures trajectory divergence** (the butterfly effect)
5. **Creates return maps** from Poincaré sections
6. **Generates comprehensive reports** (text + visual)

All with a single function call!

## Key Features

### Automated Analysis
- **One-line analysis**: Just call `generate_full_report(attractor)`
- **Configurable depth**: Enable/disable specific analysis components
- **Multiple attractors**: Compare different systems side-by-side
- **Parameter exploration**: Analyze across different parameter regimes

### Comprehensive Output
- **Text reports**: Formatted summaries with interpretations
- **Visual reports**: Multi-page PDFs with all visualizations
- **Quantitative metrics**: Lyapunov exponents, growth rates, etc.
- **Qualitative insights**: Interpretations and classifications

### Publication Ready
- **High-quality plots**: Vector graphics suitable for papers
- **Professional layout**: Multi-panel figures with proper labels
- **Statistical rigor**: Confidence intervals and convergence diagnostics
- **Comparative analysis**: Side-by-side comparisons with metrics

## Quick Start

### Basic Usage

```python
from lorenz import LorenzAttractor
from chaos_reporter import ChaosReporter

# Create attractor
lorenz = LorenzAttractor()

# Generate complete analysis report
reporter = ChaosReporter()
text_file, pdf_file = reporter.generate_full_report(lorenz)

# That's it! Reports are saved automatically.
```

### Comparison of Multiple Attractors

```python
from lorenz import LorenzAttractor
from rossler import RosslerAttractor
from chaos_reporter import compare_attractors

# Compare two chaotic systems
lorenz = LorenzAttractor()
rossler = RosslerAttractor()

comparison_pdf = compare_attractors([lorenz, rossler])
```

### Custom Analysis

```python
from rossler import RosslerAttractor
from chaos_reporter import ChaosReporter

rossler = RosslerAttractor()
reporter = ChaosReporter()

# Run analysis with custom parameters
results = reporter.analyze_attractor(
    rossler,
    t_span=(0, 200),          # Longer time span
    n_points=20000,           # Higher resolution
    include_poincare=True,
    include_lyapunov=True,
    include_divergence=True,
    poincare_plane='z',       # Section plane
    poincare_value=0.0        # Plane position
)

# Generate reports separately
text_report = reporter.generate_text_report(results)
reporter.generate_visual_report(results, output_file='custom_report.pdf')
```

## API Reference

### ChaosReporter Class

#### `__init__(visualizer=None)`

Create a new chaos reporter.

**Parameters:**
- `visualizer` (AttractorVisualizer, optional): Custom visualizer instance

#### `analyze_attractor(attractor, **kwargs)`

Perform comprehensive analysis on an attractor.

**Parameters:**
- `attractor` (AttractorBase): The system to analyze
- `t_span` (tuple): Time span (start, end)
- `n_points` (int): Number of trajectory points
- `include_poincare` (bool): Compute Poincaré sections
- `include_lyapunov` (bool): Estimate Lyapunov exponents
- `include_divergence` (bool): Measure trajectory divergence
- `poincare_plane` (str): Plane for section ('x', 'y', or 'z')
- `poincare_value` (float): Plane position (None = auto)

**Returns:**
- Dictionary containing all analysis results

#### `generate_text_report(results=None)`

Generate formatted text summary.

**Parameters:**
- `results` (dict, optional): Analysis results (uses stored results if None)

**Returns:**
- String containing formatted report

#### `generate_visual_report(results=None, output_file=None, show_plots=False)`

Generate comprehensive visual report.

**Parameters:**
- `results` (dict, optional): Analysis results
- `output_file` (str, optional): Path to save PDF
- `show_plots` (bool): Display plots interactively

**Returns:**
- List of (title, figure) tuples

#### `generate_full_report(attractor, output_dir='./reports', **kwargs)`

Generate complete analysis (text + visual).

**Parameters:**
- `attractor` (AttractorBase): System to analyze
- `output_dir` (str): Directory for reports
- `**kwargs`: Passed to `analyze_attractor()`

**Returns:**
- Tuple of (text_file_path, pdf_file_path)

### Module-Level Functions

#### `compare_attractors(attractors, output_dir='./reports', **kwargs)`

Generate comparative analysis report.

**Parameters:**
- `attractors` (list): List of AttractorBase instances
- `output_dir` (str): Directory for reports
- `**kwargs`: Passed to `analyze_attractor()`

**Returns:**
- Path to comparison PDF

## Report Contents

### Text Report Includes

1. **System Information**
   - Attractor type and dimension
   - Parameters and initial conditions

2. **Lyapunov Exponent**
   - Estimated value with error bars
   - Convergence status
   - Interpretation (strongly chaotic, weakly chaotic, regular, etc.)

3. **Poincaré Section Analysis**
   - Number of crossings
   - Structure classification (periodic, strange attractor, etc.)

4. **Return Map**
   - Data point count
   - Dimension and delay information

5. **Divergence Analysis**
   - Initial and final separation
   - Exponential growth rate
   - Doubling time

### Visual Report Includes

1. **3D Trajectory** - Full phase space visualization
2. **Phase Space Projections** - 2D views (XY, XZ, YZ)
3. **Poincaré Section** - 2D section with sequence coloring
4. **Return Map** - x_n vs x_{n+1} with diagonal line
5. **Lyapunov Convergence** - Estimate stabilization plot
6. **Trajectory Divergence** - Butterfly effect quantification

## Examples

### Example 1: Quick Analysis

```python
from lorenz import LorenzAttractor
from chaos_reporter import ChaosReporter

lorenz = LorenzAttractor()
reporter = ChaosReporter()

# One-line comprehensive report
text_file, pdf_file = reporter.generate_full_report(lorenz)

print(f"Reports saved:")
print(f"  Text: {text_file}")
print(f"  PDF:  {pdf_file}")
```

### Example 2: Parameter Exploration

```python
from rossler import RosslerAttractor
from chaos_reporter import ChaosReporter

# Explore different parameter regimes
regimes = RosslerAttractor.get_parameter_recommendations()
reporter = ChaosReporter()

for regime_name, params in regimes.items():
    rossler = RosslerAttractor(parameters=params)
    results = reporter.analyze_attractor(
        rossler,
        t_span=(0, 200),
        n_points=15000,
        include_lyapunov=True
    )

    lyap = results['lyapunov']['exponent']
    print(f"{regime_name}: λ₁ = {lyap:.6f}")
```

### Example 3: Custom Attractor Analysis

```python
from lorenz import LorenzAttractor
from chaos_reporter import ChaosReporter

# Create attractor with unusual parameters
strange_lorenz = LorenzAttractor(
    parameters={'sigma': 15, 'rho': 35, 'beta': 3},
    initial_state=[1, 1, 1]
)

reporter = ChaosReporter()
text_file, pdf_file = reporter.generate_full_report(
    strange_lorenz,
    output_dir='./custom_analysis',
    t_span=(0, 100),
    n_points=15000
)
```

### Example 4: Comparison Study

```python
from lorenz import LorenzAttractor
from rossler import RosslerAttractor
from chaos_reporter import compare_attractors

# Create multiple systems
lorenz = LorenzAttractor()
rossler = RosslerAttractor()

# Could also test parameter variations
lorenz_variant = LorenzAttractor(
    parameters={'sigma': 10, 'rho': 20, 'beta': 2}
)

# Compare all three
comparison = compare_attractors(
    [lorenz, rossler, lorenz_variant],
    output_dir='./comparison_study',
    t_span=(0, 50),
    n_points=10000
)

print(f"Comparison report: {comparison}")
```

## Integration with Our Toolkit

The Chaos Reporter seamlessly integrates all components we've built:

**Bob's Contributions:**
- `attractor_base.py` - Foundation for all attractors
- `lorenz.py`, `rossler.py` - Attractor implementations
- `analysis.py` - Quantitative analysis tools
- `chaos_reporter.py` - This automated reporting system

**Alice's Contributions:**
- `visualizer.py` - All visualization methods
- Plot design and aesthetic choices
- Multi-panel figure layouts

**Together:**
- Seamless data flow between analysis and visualization
- Publication-ready output
- Comprehensive testing
- Clear documentation

## Testing

Comprehensive test suite in `test_chaos_reporter.py`:

```bash
pytest test_chaos_reporter.py -v
```

Tests cover:
- Report generation (text and visual)
- Analysis with various configurations
- Multi-attractor comparison
- Edge cases and error handling
- Output file creation
- Data integrity

## Performance Notes

**Typical Analysis Times** (on modern hardware):

- Basic trajectory: < 1 second
- Poincaré section: 1-2 seconds
- Lyapunov exponent: 5-15 seconds
- Complete report: 20-30 seconds

**Optimization Tips:**

1. **Reduce n_points** for faster exploration (1000-5000)
2. **Disable slow analysis** when not needed:
   ```python
   analyze_attractor(..., include_lyapunov=False)
   ```
3. **Shorter time spans** for quick checks
4. **Increase n_points** (10000-20000) for publication quality

## Use Cases

### Research
- Automated analysis of new dynamical systems
- Parameter space exploration
- Comparative studies of chaotic systems
- Publication-ready figures

### Education
- Demonstrating chaos theory concepts
- Visualizing the butterfly effect
- Exploring bifurcations and routes to chaos
- Student projects and assignments

### Exploration
- Quick analysis of attractor behavior
- Testing different parameter regimes
- Discovering interesting dynamics
- Building intuition about chaos

## Future Enhancements

Potential additions (not yet implemented):

- **Correlation dimension** - Fractal structure quantification
- **Wolf's algorithm** - Gold-standard Lyapunov estimation
- **Power spectral density** - Frequency analysis
- **Recurrence plots** - Temporal structure visualization
- **Interactive reports** - HTML with plotly figures
- **Batch processing** - Analyze multiple systems automatically

## Dependencies

Required modules:
- `numpy` - Numerical computations
- `matplotlib` - Plotting and PDF generation
- `scipy` - Numerical integration (via attractor_base)
- `attractor_base`, `lorenz`, `rossler` - Attractor implementations
- `analysis` - Quantitative analysis functions
- `visualizer` - Visualization tools

## Acknowledgments

This tool represents the culmination of collaborative development between Bob and Alice:

- **System architecture** - Designed together
- **Analysis algorithms** - Implemented by Bob
- **Visualization methods** - Created by Alice
- **Integration** - Joint effort
- **Testing** - Both contributors

The result is a powerful, user-friendly toolkit for chaos analysis that's greater than the sum of its parts!

## Example Output

When you run `generate_full_report()`, you get:

**Text Report:**
```
======================================================================
CHAOS ANALYSIS REPORT
======================================================================

Attractor Type: Lorenz Attractor
Dimension: 3D

Parameters:
  sigma = 10.0
  rho = 28.0
  beta = 2.6666666666666665

Initial State:
  [1. 1. 1.]

----------------------------------------------------------------------
ANALYSIS RESULTS
----------------------------------------------------------------------

Lyapunov Exponent:
  λ₁ = 0.905632
  Standard Error: ±0.012453
  95% CI: [0.881224, 0.930040]
  Converged: Yes ✓
  Interpretation: STRONGLY CHAOTIC - High sensitivity to initial conditions

Poincaré Section:
  Number of crossings: 1247
  Structure: Dispersed (strange attractor)

Return Map:
  Dimension: 0
  Delay: 1
  Data points: 1246

Trajectory Divergence (Butterfly Effect):
  Initial separation: 1.42e-08
  Final separation: 2.31e+01
  Growth rate: 0.906123
  Doubling time: 0.76 time units

======================================================================
```

**Visual Report (PDF):**
- Page 1: 3D trajectory (beautiful butterfly wings)
- Page 2: Phase space projections (2x2 grid)
- Page 3: Poincaré section (spiral/dispersed structure)
- Page 4: Return map (fractal curve)
- Page 5: Lyapunov convergence (stabilization plot)
- Page 6: Divergence plot (exponential growth)

Perfect for papers, presentations, or understanding your chaotic system!

---

**Happy chaos exploration!** 🦋
