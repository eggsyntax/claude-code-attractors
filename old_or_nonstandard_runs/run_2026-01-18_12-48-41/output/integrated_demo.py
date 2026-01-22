"""
Integrated Demo: Bringing It All Together

This demo showcases the complete cellular automaton toolkit:
- Famous patterns from the pattern library
- Hashlife algorithm for ultra-fast simulation
- Pattern explorer for analysis
- Performance comparisons

Usage:
    python integrated_demo.py [pattern_name]

Examples:
    python integrated_demo.py r_pentomino
    python integrated_demo.py gosper_glider_gun
    python integrated_demo.py acorn

If no pattern is specified, runs a showcase of interesting patterns.
"""

import sys
import time
from typing import Set, Tuple
from cellular_automaton import Grid, ConwayRules
from hashlife import HashLife
from pattern_explorer import PatternAnalyzer
from famous_patterns import get_pattern, list_patterns, center_pattern


def analyze_with_hashlife(pattern_name: str, generations: int = 1000):
    """
    Analyze a pattern using Hashlife and the pattern explorer.

    Args:
        pattern_name: Name of the pattern to analyze
        generations: Number of generations to simulate
    """
    print("=" * 80)
    print(f"Analyzing: {pattern_name.upper()}")
    print("=" * 80)

    # Get the pattern
    try:
        pattern = get_pattern(pattern_name)
    except KeyError as e:
        print(f"Error: {e}")
        return

    # Center it in a reasonably sized grid
    centered = center_pattern(pattern, 60, 60)
    grid = Grid(width=60, height=60, live_cells=centered)
    rules = ConwayRules()

    print(f"\nInitial state:")
    print(f"  Population: {grid.count_live_cells()} cells")
    print(f"  Grid size: {grid.width} x {grid.height}")
    print()

    # Show initial pattern
    print("Initial configuration:")
    print_grid_compact(grid)
    print()

    # ========================================================================
    # Part 1: Pattern Analysis
    # ========================================================================
    print("-" * 80)
    print("PART 1: Pattern Analysis")
    print("-" * 80)

    analyzer = PatternAnalyzer(grid, rules)
    start_time = time.time()
    result = analyzer.analyze(max_generations=min(100, generations))
    analysis_time = time.time() - start_time

    print(f"\nAnalysis completed in {analysis_time:.3f} seconds")
    print(result)
    print()

    # ========================================================================
    # Part 2: Hashlife Simulation
    # ========================================================================
    print("-" * 80)
    print("PART 2: Hashlife Ultra-Fast Simulation")
    print("-" * 80)

    hashlife = HashLife()
    hl_grid = hashlife.from_grid(grid)

    print(f"\nSimulating {generations} generations with Hashlife...")
    start_time = time.time()

    # Simulate in chunks to show progress
    checkpoints = [10, 100, 500, generations]
    for checkpoint in checkpoints:
        if checkpoint > generations:
            break

        steps_needed = checkpoint - (checkpoints[checkpoints.index(checkpoint) - 1] if checkpoints.index(checkpoint) > 0 else 0)
        for _ in range(steps_needed):
            hl_grid = hashlife.step(hl_grid, ConwayRules())

        current_grid = hashlife.to_grid(hl_grid)
        pop = current_grid.count_live_cells()
        elapsed = time.time() - start_time

        print(f"  Generation {checkpoint:5d}: population = {pop:5d}  "
              f"(elapsed: {elapsed:.3f}s, {checkpoint/elapsed:.0f} gen/sec)")

    hashlife_time = time.time() - start_time

    print(f"\nHashlife simulation completed!")
    print(f"  Total time: {hashlife_time:.3f} seconds")
    print(f"  Speed: {generations / hashlife_time:.0f} generations/second")
    print(f"  Cache size: {len(hashlife._result_cache)} memoized nodes")
    print()

    # Show final state
    final_grid = hashlife.to_grid(hl_grid)
    print(f"Final state after {generations} generations:")
    print(f"  Population: {final_grid.count_live_cells()} cells")
    print()
    print("Final configuration (center region):")
    print_grid_compact(final_grid, show_region=(20, 20, 40, 40))
    print()

    # ========================================================================
    # Part 3: Performance Comparison
    # ========================================================================
    print("-" * 80)
    print("PART 3: Performance Comparison")
    print("-" * 80)

    # For fair comparison, simulate fewer generations with naive method
    comparison_gens = min(100, generations)

    print(f"\nComparing naive vs Hashlife for {comparison_gens} generations...")

    # Naive method
    print("\nNaive simulation (Grid.step() in a loop):")
    naive_grid = Grid(width=60, height=60, live_cells=centered)
    start_time = time.time()
    for _ in range(comparison_gens):
        naive_grid = naive_grid.step(rules)
    naive_time = time.time() - start_time
    print(f"  Time: {naive_time:.3f} seconds ({comparison_gens/naive_time:.0f} gen/sec)")

    # Hashlife method
    print("\nHashlife simulation:")
    hl_grid = hashlife.from_grid(Grid(width=60, height=60, live_cells=centered))
    hashlife._result_cache.clear()  # Clear cache for fair comparison
    start_time = time.time()
    for _ in range(comparison_gens):
        hl_grid = hashlife.step(hl_grid, rules)
    hl_time = time.time() - start_time
    print(f"  Time: {hl_time:.3f} seconds ({comparison_gens/hl_time:.0f} gen/sec)")

    speedup = naive_time / hl_time if hl_time > 0 else float('inf')
    print(f"\nSpeedup: {speedup:.1f}x faster with Hashlife!")
    print(f"Cache efficiency: {len(hashlife._result_cache)} unique nodes memoized")
    print()

    # ========================================================================
    # Summary
    # ========================================================================
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Pattern: {pattern_name}")
    print(f"Classification: {result.pattern_type}")
    if result.period:
        print(f"Period: {result.period}")
    if result.velocity:
        print(f"Velocity: {result.velocity}")
    print(f"Initial population: {grid.count_live_cells()}")
    print(f"Final population: {final_grid.count_live_cells()}")
    print(f"Generations simulated: {generations}")
    print(f"Hashlife speedup: {speedup:.1f}x")
    print("=" * 80)
    print()


def print_grid_compact(grid: Grid, show_region: Tuple[int, int, int, int] = None):
    """
    Print a compact representation of the grid.

    Args:
        grid: The grid to print
        show_region: Optional (x1, y1, x2, y2) tuple to show only a region
    """
    if show_region:
        x1, y1, x2, y2 = show_region
    else:
        x1, y1, x2, y2 = 0, 0, grid.width, grid.height

    # Limit size for display
    max_width = 60
    max_height = 30

    x2 = min(x2, x1 + max_width)
    y2 = min(y2, y1 + max_height)

    for y in range(y1, y2):
        line = ""
        for x in range(x1, x2):
            line += "█" if grid.is_alive(x, y) else "·"
        print(line)


def run_showcase():
    """
    Run a showcase of interesting patterns with brief analysis.
    """
    print("\n")
    print("=" * 80)
    print(" " * 20 + "CELLULAR AUTOMATON SHOWCASE")
    print(" " * 15 + "Famous Patterns from Conway's Game of Life")
    print("=" * 80)
    print()

    showcase_patterns = [
        ('glider', 50, 'The smallest spaceship'),
        ('pulsar', 20, 'Beautiful period-3 oscillator'),
        ('gosper_glider_gun', 200, 'First discovered gun - emits gliders'),
        ('r_pentomino', 1200, 'Famous methuselah - 1103 generations'),
    ]

    for pattern_name, gens, description in showcase_patterns:
        print("\n" + "=" * 80)
        print(f"Pattern: {pattern_name.upper()}")
        print(f"Description: {description}")
        print("=" * 80)
        print()

        try:
            pattern = get_pattern(pattern_name)
            centered = center_pattern(pattern, 60, 60)
            grid = Grid(width=60, height=60, live_cells=centered)

            print("Initial configuration:")
            print_grid_compact(grid)
            print()

            # Quick analysis
            analyzer = PatternAnalyzer(grid, ConwayRules())
            result = analyzer.analyze(max_generations=min(50, gens))

            print(f"Classification: {result.pattern_type}")
            if result.period:
                print(f"Period: {result.period}")
            if result.velocity:
                print(f"Velocity: {result.velocity} cells/generation")

            # Simulate with Hashlife
            hashlife = HashLife()
            hl_grid = hashlife.from_grid(grid)

            start_time = time.time()
            for _ in range(gens):
                hl_grid = hashlife.step(hl_grid, ConwayRules())
            elapsed = time.time() - start_time

            final_grid = hashlife.to_grid(hl_grid)
            print(f"\nSimulated {gens} generations in {elapsed:.3f} seconds")
            print(f"Initial population: {grid.count_live_cells()}")
            print(f"Final population: {final_grid.count_live_cells()}")

            if gens >= 100:
                print(f"\nFinal state (center region):")
                print_grid_compact(final_grid, show_region=(20, 20, 40, 40))

        except Exception as e:
            print(f"Error analyzing {pattern_name}: {e}")
            continue

        print()
        input("Press Enter to continue to next pattern...")

    print("\n" + "=" * 80)
    print("Showcase complete!")
    print("=" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        pattern_name = sys.argv[1].lower()

        # Check if it's a special command
        if pattern_name in ['list', 'ls', 'catalog']:
            patterns = list_patterns()
            print("\nAvailable patterns:")
            for name, desc in sorted(patterns.items()):
                print(f"  {name:25s} - {desc}")
            print()
            return

        # Try to analyze the requested pattern
        generations = 1000
        if len(sys.argv) > 2:
            try:
                generations = int(sys.argv[2])
            except ValueError:
                print(f"Invalid generation count: {sys.argv[2]}")
                return

        analyze_with_hashlife(pattern_name, generations)
    else:
        # Run showcase
        run_showcase()


if __name__ == '__main__':
    main()
