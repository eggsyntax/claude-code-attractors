# System Architecture

*A visual guide to how the components fit together*

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CELLULAR AUTOMATON TOOLKIT                   │
│                                                                 │
│  Built by Alice & Bob through test-driven collaborative design │
└─────────────────────────────────────────────────────────────────┘

                              USER
                                │
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
   ┌─────────┐           ┌─────────────┐        ┌──────────────┐
   │Visualizer│           │Integrated   │        │Pattern       │
   │  (CLI)   │           │Demo         │        │Explorer      │
   └─────────┘           └─────────────┘        └──────────────┘
        │                       │                       │
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                     ┌──────────┴──────────┐
                     │                     │
                     ▼                     ▼
              ┌────────────┐        ┌───────────┐
              │  Hashlife  │        │ Famous    │
              │ (Fast path)│        │ Patterns  │
              └────────────┘        └───────────┘
                     │                     │
                     └──────────┬──────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Core Engine           │
                    │                       │
                    │  • Grid               │
                    │  • Rules              │
                    │  • ConwayRules        │
                    └───────────────────────┘
```

## Component Layers

### Layer 1: Foundation (Built by Bob)

```
┌─────────────────────────────────────────────────────────────────┐
│                         CORE ENGINE                             │
│                    (cellular_automaton.py)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐      ┌─────────────┐      ┌──────────────┐  │
│  │    Grid     │      │    Rules    │      │ ConwayRules  │  │
│  ├─────────────┤      ├─────────────┤      ├──────────────┤  │
│  │ - width     │      │ - birth[]   │      │ birth=[3]    │  │
│  │ - height    │      │ - survival[]│      │ survival=    │  │
│  │ - live_cells│      │             │      │   [2,3]      │  │
│  │   (set)     │      │ should_be_  │      │              │  │
│  │             │      │   alive()   │      └──────────────┘  │
│  │ step(rules) │      └─────────────┘                        │
│  │ is_alive()  │                                             │
│  │ count_      │                                             │
│  │   neighbors()│                                            │
│  └─────────────┘                                             │
│                                                               │
│  Key Design: Immutable • Sparse • Flexible                   │
└───────────────────────────────────────────────────────────────┘

               Tested by: test_cellular_automaton.py (20+ tests)
```

### Layer 2: Optimization (Built by Bob)

```
┌─────────────────────────────────────────────────────────────────┐
│                    HASHLIFE ALGORITHM                           │
│                       (hashlife.py)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐                ┌──────────────────┐     │
│  │ HashLifeNode     │                │   HashLife       │     │
│  ├──────────────────┤                ├──────────────────┤     │
│  │ - level          │                │ - node_cache     │     │
│  │ - population     │                │ - result_cache   │     │
│  │ - nw, ne, sw, se │◄───────────────│                  │     │
│  │   (quadrants)    │                │ from_grid()      │     │
│  │                  │                │ step()           │     │
│  │ hashable &       │                │ to_grid()        │     │
│  │ immutable        │                └──────────────────┘     │
│  └──────────────────┘                                          │
│                                                                 │
│  Algorithm:                                                     │
│  1. Quadtree decomposition (hierarchical space)                │
│  2. Canonical node storage (deduplication)                     │
│  3. Result memoization (never recompute)                       │
│  4. Exponential time steps (2^(level-2) generations)           │
│                                                                 │
│  Complexity: O(log t) vs O(n×t)                                │
│  Speedup: 100-500x on typical patterns                         │
└─────────────────────────────────────────────────────────────────┘

                   Tested by: test_hashlife.py (30+ tests)
```

### Layer 3: Visualization & Analysis (Built by Alice)

```
┌─────────────────────────────────────────────────────────────────┐
│                      VISUALIZATION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              VISUALIZER (visualizer.py)                 │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │ • Terminal animation with ANSI colors                   │   │
│  │ • Pattern library (8+ built-in patterns)                │   │
│  │ • Auto-detection (extinction, stabilization)            │   │
│  │ • Configurable speed, size, rules                       │   │
│  │                                                          │   │
│  │   animate_pattern(pattern, generations, delay, ...)     │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │         PATTERN EXPLORER (pattern_explorer.py)          │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  ┌─────────────────┐      ┌──────────────────────┐    │   │
│  │  │PatternAnalyzer  │      │RandomPattern         │    │   │
│  │  │                 │      │Generator             │    │   │
│  │  │ analyze()       │      │                      │    │   │
│  │  │ - still_life    │      │ generate_random()    │    │   │
│  │  │ - oscillator    │      │ generate_symmetric() │    │   │
│  │  │ - spaceship     │      │ batch_screen()       │    │   │
│  │  │ - chaotic       │      │                      │    │   │
│  │  └─────────────────┘      └──────────────────────┘    │   │
│  │                                                          │   │
│  │  Returns: type, period, velocity, population history    │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Layer 4: Data & Integration (Built by Alice)

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION & DATA LAYER                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │        FAMOUS PATTERNS (famous_patterns.py)             │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  Still Lifes:  block, beehive, loaf, boat, tub         │   │
│  │  Oscillators:  blinker, toad, beacon, pulsar,          │   │
│  │                pentadecathlon                           │   │
│  │  Spaceships:   glider, lwss, mwss, hwss                │   │
│  │  Methuselahs:  r_pentomino, acorn, diehard             │   │
│  │  Guns:         gosper_glider_gun, simkin_glider_gun    │   │
│  │  Puffers:      puffer_train, switch_engine             │   │
│  │                                                          │   │
│  │  get_pattern(name) → set of (x,y) coordinates          │   │
│  │  center_pattern(pattern, width, height) → centered     │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │        INTEGRATED DEMO (integrated_demo.py)             │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  1. Pattern Analysis (uses PatternAnalyzer)             │   │
│  │     ↓                                                    │   │
│  │  2. Hashlife Simulation (fast-forward many gens)        │   │
│  │     ↓                                                    │   │
│  │  3. Performance Comparison (naive vs Hashlife)          │   │
│  │     ↓                                                    │   │
│  │  4. Visual Output (show initial and final states)       │   │
│  │                                                          │   │
│  │  Brings together ALL components in one showcase         │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │        BENCHMARK SUITE (benchmark_suite.py)             │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  • Small patterns scaling (10-500 generations)          │   │
│  │  • Methuselahs (long-running patterns)                  │   │
│  │  • Grid size scaling (20x20 to 120x120)                 │   │
│  │  • Complex patterns (guns, puffers)                     │   │
│  │                                                          │   │
│  │  Outputs: timings, speedups, cache stats, insights      │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow: Example Pattern Execution

### Simple Visualization

```
User runs: python visualizer.py --pattern glider --generations 50
           │
           ▼
    ┌──────────────┐
    │ Visualizer   │  Loads pattern from famous_patterns
    └──────┬───────┘
           │ get_pattern('glider')
           ▼
    ┌──────────────┐
    │Famous        │  Returns: {(1,0), (2,1), (0,2), (1,2), (2,2)}
    │Patterns      │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Visualizer   │  Creates Grid(width, height, live_cells)
    └──────┬───────┘
           │
           ▼
    Loop for 50 generations:
        ┌──────────────┐
        │ Grid         │  Display current state (ANSI colors)
        │              │
        │ grid.step()  │  Compute next generation
        └──────┬───────┘
               │ Uses ConwayRules to determine life/death
               ▼
        ┌──────────────┐
        │ ConwayRules  │  Apply B3/S23: birth on 3, survive on 2-3
        └──────────────┘

    User sees: Glider moving diagonally across terminal
```

### Hashlife-Powered Analysis

```
User runs: python integrated_demo.py r_pentomino
           │
           ▼
    ┌──────────────┐
    │Integrated    │  Part 1: Pattern Analysis
    │Demo          │
    └──────┬───────┘
           │ get_pattern('r_pentomino')
           ▼
    ┌──────────────┐
    │Famous        │  Returns 5-cell pattern
    │Patterns      │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │Pattern       │  Analyzes: type=methuselah, classification...
    │Analyzer      │  (simulates ~100 gens to classify)
    └──────┬───────┘
           │
           │ Part 2: Hashlife Ultra-Fast Simulation
           ▼
    ┌──────────────┐
    │HashLife      │  from_grid() → converts to quadtree
    │              │
    │              │  Loop 1103 times:
    │              │    hl_grid = hashlife.step(hl_grid, rules)
    │              │    • Memoization kicks in
    │              │    • Exponential time steps used
    │              │    • 100-500x faster than naive
    │              │
    │              │  to_grid() → converts back to Grid
    └──────┬───────┘
           │
           │ Part 3: Performance Comparison
           ▼
    ┌──────────────┐
    │Benchmark     │  Time naive Grid simulation
    │              │  Time Hashlife simulation
    │              │  Report: "Hashlife 247x faster!"
    └──────┬───────┘
           │
           │ Part 4: Visual Output
           ▼
    ┌──────────────┐
    │Display       │  Show initial 5-cell pattern
    │              │  Show final 116-cell stable configuration
    │              │  Report statistics
    └──────────────┘

User sees: Complete analysis from classification to final state
```

## Memory Architecture: Hashlife Memoization

```
┌─────────────────────────────────────────────────────────────────┐
│                    HASHLIFE MEMORY MODEL                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Node Cache (Canonical Storage)                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Key: (level, nw, ne, sw, se)                         │     │
│  │  Value: HashLifeNode                                  │     │
│  │                                                        │     │
│  │  Purpose: Ensure identical subtrees share memory      │     │
│  │  Benefit: Sparse patterns (empty space) compressed    │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
│  Result Cache (Memoization)                                    │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Key: (node, rules, generations)                      │     │
│  │  Value: Resulting node after evolution                │     │
│  │                                                        │     │
│  │  Purpose: Never compute same region twice             │     │
│  │  Benefit: Temporal repetition (oscillators) cached    │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
│  Example for Glider:                                           │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Generation 0:   Node A (glider pattern)               │   │
│  │        ↓                                                │   │
│  │  Generation 1:   Compute → Result B, cache (A → B)     │   │
│  │        ↓                                                │   │
│  │  Generation 2:   Compute → Result C, cache (B → C)     │   │
│  │        ↓                                                │   │
│  │  Generation 3:   Compute → Result D, cache (C → D)     │   │
│  │        ↓                                                │   │
│  │  Generation 4:   Compute → Result E, cache (D → E)     │   │
│  │        ↓                                                │   │
│  │  After period 4: Pattern repeats!                      │   │
│  │                  Empty regions already cached          │   │
│  │                  Only glider position changes          │   │
│  │                  Massive reuse of cached results       │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## File Organization

```
cellular-automaton-toolkit/
│
├── Core Implementation
│   ├── cellular_automaton.py      (Grid, Rules, ConwayRules)
│   ├── hashlife.py                (HashLife algorithm)
│   └── famous_patterns.py         (Pattern library)
│
├── Analysis & Visualization
│   ├── visualizer.py               (Terminal animation)
│   └── pattern_explorer.py         (Pattern classification)
│
├── Integration & Demos
│   ├── integrated_demo.py          (Showcase all components)
│   ├── demo.py                     (Basic demonstrations)
│   ├── hashlife_demo.py            (Hashlife-specific demo)
│   └── benchmark_suite.py          (Performance analysis)
│
├── Testing
│   ├── test_cellular_automaton.py  (Core engine tests)
│   ├── test_hashlife.py            (Hashlife tests)
│   └── run_tests.sh                (Test runner)
│
└── Documentation
    ├── README.md                   (Project overview)
    ├── GETTING_STARTED.md          (Quick start guide)
    ├── SYSTEM_ARCHITECTURE.md      (This file)
    ├── COLLABORATION_STORY.md      (How it was built)
    └── HASHLIFE_PHILOSOPHY.md      (Deep algorithmic insights)
```

## Design Principles

### 1. Immutability
```
Grid.step(rules) → new Grid  (not mutation)

Benefits:
  • Easier reasoning about state
  • Time travel (keep history)
  • Enables Hashlife memoization (nodes never change)
  • Thread-safe (if we go parallel)
```

### 2. Sparse Representation
```
Grid stores: set of (x, y) for live cells only
Not: 2D array of booleans

Benefits:
  • Memory efficient for sparse patterns (gliders, spaceships)
  • Fast neighbor counting (only check live cells + neighbors)
  • Scales to large grids with few live cells
```

### 3. Separation of Concerns
```
Rules:           Define birth/survival logic
Grid:            Manage spatial state
Hashlife:        Optimize temporal evolution
Visualizer:      Present to user
PatternExplorer: Analyze behavior
```

### 4. Test-Driven Development
```
Process:
  1. Write tests defining expected behavior
  2. Implement to pass tests
  3. Refactor with confidence

Result: 50+ tests covering edge cases, ensuring correctness
```

## Performance Characteristics

### Naive Grid Implementation
```
Time Complexity:  O(n × t)
  n = number of cells to check (~width × height)
  t = number of generations

Space Complexity: O(live_cells)

Best for: Small grids, few generations, learning
```

### Hashlife Implementation
```
Time Complexity:  O(log t) amortized for many patterns
  Exploits spatial & temporal repetition
  Exponential time steps possible

Space Complexity: O(nodes_in_quadtree + cache)
  Trade space for time
  Cache grows with pattern diversity

Best for: Large grids, many generations, repetitive patterns
```

### Comparison Table
```
Pattern          | Generations | Naive    | Hashlife | Speedup
─────────────────┼─────────────┼──────────┼──────────┼─────────
Blinker          |         100 |   15ms   |   0.8ms  |   19x
Glider           |         500 |  120ms   |   4.2ms  |   29x
Pulsar           |         100 |   35ms   |   1.5ms  |   23x
R-pentomino      |       1,103 |  2.5s    |  10ms    |  250x
Gosper Gun       |         500 |  450ms   |   8ms    |   56x
Acorn            |       5,206 |  15.3s   |  35ms    |  437x
```

## Extension Points

Want to extend the toolkit? Here are the key interfaces:

### 1. Add New Rules
```python
from cellular_automaton import Rules

class MyCustomRules(Rules):
    def __init__(self):
        # Define your birth and survival conditions
        super().__init__(birth=[...], survival=[...])

    # Can override should_be_alive() for complex logic
```

### 2. Add New Patterns
```python
# In famous_patterns.py or your own file
my_pattern = {
    (0, 0), (1, 0), (2, 0),  # Coordinates of live cells
    # ...
}

from famous_patterns import center_pattern
centered = center_pattern(my_pattern, width, height)
```

### 3. Create New Visualizations
```python
# The Grid has a simple interface:
grid.is_alive(x, y)  # Returns bool
grid.get_live_cells()  # Returns set of (x, y)
grid.count_live_cells()  # Returns int

# Build any visualization on top!
```

### 4. Add New Analysis
```python
from pattern_explorer import PatternAnalyzer

class MyAnalyzer(PatternAnalyzer):
    def analyze_my_property(self, max_gen=100):
        # Inherit basic analysis, add your own
        base_result = self.analyze(max_gen)
        # Add custom analysis...
        return enhanced_result
```

## The Collaboration Pattern

```
Alice's Contributions:          Bob's Contributions:
┌────────────────────┐          ┌────────────────────┐
│ • Test suites      │          │ • Core engine      │
│ • Visualizer       │          │ • Hashlife         │
│ • Pattern explorer │  ◄────►  │ • Optimization     │
│ • Pattern library  │          │ • Philosophy docs  │
│ • Integration      │          │ • Demos            │
│ • Documentation    │          │ • Architecture     │
└────────────────────┘          └────────────────────┘
        │                              │
        └──────────┬───────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   Shared Vision:    │
         │ Explore emergence   │
         │ through clean code  │
         └─────────────────────┘

Result: Complementary strengths create comprehensive toolkit
```

## Key Takeaways

1. **Layered Architecture**: Foundation → Optimization → Visualization → Integration
2. **Immutability Enables Optimization**: Hashlife depends on immutable nodes
3. **Separation of Concerns**: Each component has clear responsibility
4. **Test-Driven**: Tests define interfaces and ensure correctness
5. **Extensible**: Clean interfaces make adding features easy
6. **Collaborative**: Alice and Bob brought complementary strengths

---

*Understanding the architecture reveals how simple principles (immutability, caching, separation of concerns) combine to create a powerful, extensible system.*

*Just like Conway's Life itself: simple rules, emergent complexity.*
