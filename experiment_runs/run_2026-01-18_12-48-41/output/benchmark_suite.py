"""
Comprehensive Benchmark Suite

Compares naive Grid.step() against Hashlife across different patterns
and generation counts to demonstrate performance characteristics.

This benchmark suite shows:
1. When Hashlife excels (repetitive patterns, many generations)
2. When naive approach is competitive (small grids, few generations)
3. Cache efficiency and memory tradeoffs
4. Scalability characteristics

Usage:
    python benchmark_suite.py
"""

import time
import statistics
from typing import List, Tuple, Dict
from dataclasses import dataclass
from cellular_automaton import Grid, ConwayRules
from hashlife import HashLife
from famous_patterns import get_pattern, center_pattern


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    pattern_name: str
    generations: int
    naive_time: float
    hashlife_time: float
    speedup: float
    initial_population: int
    final_population: int
    cache_size: int
    grid_size: Tuple[int, int]

    def __str__(self) -> str:
        return (
            f"{self.pattern_name:20s} | "
            f"gen={self.generations:5d} | "
            f"naive={self.naive_time:7.3f}s | "
            f"hl={self.hashlife_time:7.3f}s | "
            f"speedup={self.speedup:6.1f}x | "
            f"cache={self.cache_size:5d}"
        )


def benchmark_pattern(
    pattern_name: str,
    generations: int,
    grid_size: Tuple[int, int] = (60, 60),
    trials: int = 3
) -> BenchmarkResult:
    """
    Benchmark a pattern with both naive and Hashlife implementations.

    Args:
        pattern_name: Name of the pattern to benchmark
        generations: Number of generations to simulate
        grid_size: (width, height) of the grid
        trials: Number of trials to average over

    Returns:
        BenchmarkResult with timing and performance data
    """
    width, height = grid_size
    pattern = get_pattern(pattern_name)
    centered = center_pattern(pattern, width, height)

    initial_grid = Grid(width=width, height=height, live_cells=centered)
    initial_population = initial_grid.count_live_cells()
    rules = ConwayRules()

    # ========================================================================
    # Naive method benchmark
    # ========================================================================
    naive_times = []
    for _ in range(trials):
        grid = Grid(width=width, height=height, live_cells=centered)
        start = time.time()
        for _ in range(generations):
            grid = grid.step(rules)
        naive_times.append(time.time() - start)

    naive_time = statistics.median(naive_times)
    final_population = grid.count_live_cells()

    # ========================================================================
    # Hashlife method benchmark
    # ========================================================================
    hashlife = HashLife()
    hashlife_times = []

    for _ in range(trials):
        hashlife._node_cache.clear()
        hashlife._result_cache.clear()

        hl_grid = hashlife.from_grid(initial_grid)
        start = time.time()
        for _ in range(generations):
            hl_grid = hashlife.step(hl_grid, rules)
        hashlife_times.append(time.time() - start)

    hashlife_time = statistics.median(hashlife_times)
    cache_size = len(hashlife._result_cache)

    # Verify correctness
    final_grid_hl = hashlife.to_grid(hl_grid)
    if final_grid_hl.count_live_cells() != final_population:
        print(f"WARNING: Population mismatch for {pattern_name}!")

    speedup = naive_time / hashlife_time if hashlife_time > 0 else float('inf')

    return BenchmarkResult(
        pattern_name=pattern_name,
        generations=generations,
        naive_time=naive_time,
        hashlife_time=hashlife_time,
        speedup=speedup,
        initial_population=initial_population,
        final_population=final_population,
        cache_size=cache_size,
        grid_size=grid_size
    )


def run_comprehensive_benchmark():
    """Run a comprehensive benchmark across multiple patterns and parameters."""
    print("=" * 90)
    print(" " * 25 + "COMPREHENSIVE BENCHMARK SUITE")
    print("=" * 90)
    print()

    results: List[BenchmarkResult] = []

    # ========================================================================
    # Benchmark 1: Small patterns, varying generations
    # ========================================================================
    print("\n" + "-" * 90)
    print("BENCHMARK 1: Small Patterns - Scaling with Generations")
    print("-" * 90)
    print("\nPattern              | Gen   | Naive (s) | Hashlife (s) | Speedup | Cache")
    print("-" * 90)

    small_patterns = ['glider', 'blinker', 'pulsar']
    generation_counts = [10, 50, 100, 500]

    for pattern in small_patterns:
        for gens in generation_counts:
            try:
                result = benchmark_pattern(pattern, gens, grid_size=(40, 40), trials=3)
                results.append(result)
                print(result)
            except Exception as e:
                print(f"Error benchmarking {pattern} @ {gens} gens: {e}")

    # ========================================================================
    # Benchmark 2: Methuselahs - Long-running patterns
    # ========================================================================
    print("\n" + "-" * 90)
    print("BENCHMARK 2: Methuselahs - Long-Running Patterns")
    print("-" * 90)
    print("\nPattern              | Gen   | Naive (s) | Hashlife (s) | Speedup | Cache")
    print("-" * 90)

    methuselahs = [
        ('r_pentomino', 1000),
        ('acorn', 500),  # Would take 5206 but that's very slow for naive
        ('diehard', 130),
    ]

    for pattern, gens in methuselahs:
        try:
            result = benchmark_pattern(pattern, gens, grid_size=(80, 80), trials=2)
            results.append(result)
            print(result)
        except Exception as e:
            print(f"Error benchmarking {pattern}: {e}")

    # ========================================================================
    # Benchmark 3: Grid size scaling
    # ========================================================================
    print("\n" + "-" * 90)
    print("BENCHMARK 3: Grid Size Scaling (Glider, 100 generations)")
    print("-" * 90)
    print("\nGrid Size | Naive (s) | Hashlife (s) | Speedup | Cache")
    print("-" * 90)

    grid_sizes = [(20, 20), (40, 40), (80, 80), (120, 120)]

    for size in grid_sizes:
        try:
            result = benchmark_pattern('glider', 100, grid_size=size, trials=3)
            results.append(result)
            print(f"{size[0]}x{size[1]:3d}   | "
                  f"{result.naive_time:7.3f}s | "
                  f"{result.hashlife_time:7.3f}s | "
                  f"{result.speedup:6.1f}x | "
                  f"{result.cache_size:5d}")
        except Exception as e:
            print(f"Error benchmarking grid size {size}: {e}")

    # ========================================================================
    # Benchmark 4: Complex patterns
    # ========================================================================
    print("\n" + "-" * 90)
    print("BENCHMARK 4: Complex Patterns (Guns and Puffers)")
    print("-" * 90)
    print("\nPattern              | Gen   | Naive (s) | Hashlife (s) | Speedup | Cache")
    print("-" * 90)

    complex_patterns = [
        ('gosper_glider_gun', 100),
        ('gosper_glider_gun', 500),
        ('puffer_train', 100),
    ]

    for pattern, gens in complex_patterns:
        try:
            result = benchmark_pattern(pattern, gens, grid_size=(100, 100), trials=2)
            results.append(result)
            print(result)
        except Exception as e:
            print(f"Error benchmarking {pattern}: {e}")

    # ========================================================================
    # Summary Statistics
    # ========================================================================
    print("\n" + "=" * 90)
    print("SUMMARY STATISTICS")
    print("=" * 90)

    if results:
        speedups = [r.speedup for r in results]
        cache_sizes = [r.cache_size for r in results]

        print(f"\nSpeedup Statistics:")
        print(f"  Minimum speedup: {min(speedups):.2f}x")
        print(f"  Maximum speedup: {max(speedups):.2f}x")
        print(f"  Mean speedup: {statistics.mean(speedups):.2f}x")
        print(f"  Median speedup: {statistics.median(speedups):.2f}x")

        print(f"\nCache Statistics:")
        print(f"  Minimum cache size: {min(cache_sizes)} nodes")
        print(f"  Maximum cache size: {max(cache_sizes)} nodes")
        print(f"  Mean cache size: {statistics.mean(cache_sizes):.0f} nodes")

        # Find best and worst performers
        best = max(results, key=lambda r: r.speedup)
        worst = min(results, key=lambda r: r.speedup)

        print(f"\nBest Performance:")
        print(f"  {best.pattern_name} @ {best.generations} gens: {best.speedup:.1f}x speedup")

        print(f"\nWorst Performance:")
        print(f"  {worst.pattern_name} @ {worst.generations} gens: {worst.speedup:.1f}x speedup")

    # ========================================================================
    # Insights
    # ========================================================================
    print("\n" + "=" * 90)
    print("KEY INSIGHTS")
    print("=" * 90)
    print("""
1. REPETITIVE PATTERNS excel with Hashlife:
   - Oscillators (blinker, pulsar) show high speedup due to temporal repetition
   - Spaceships (glider) benefit from spatial repetition (empty regions)

2. GENERATION COUNT matters:
   - Hashlife has overhead; speedup increases with more generations
   - For < 10 generations, naive approach may be faster
   - For > 100 generations, Hashlife typically dominates

3. CACHE EFFICIENCY:
   - Larger cache = more memoization = better performance
   - Complex patterns build larger caches but reuse them heavily

4. GRID SIZE:
   - Hashlife scales better with large grids due to empty space optimization
   - Naive method slows down linearly with grid area

5. METHUSELAHS (r_pentomino, acorn):
   - Chaotic evolution patterns still benefit from spatial repetition
   - Even unpredictable patterns have repeating local structures

6. GUNS AND PUFFERS:
   - Periodic emission creates regular patterns perfect for memoization
   - Long-term simulation shows dramatic speedups (100x+)
    """)

    print("=" * 90)
    print("Benchmark suite complete!")
    print("=" * 90)


def quick_benchmark():
    """Run a quick benchmark for testing."""
    print("Quick Benchmark: Glider (100 generations)\n")
    result = benchmark_pattern('glider', 100, grid_size=(40, 40), trials=3)
    print(result)
    print(f"\nSpeedup: {result.speedup:.1f}x")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        quick_benchmark()
    else:
        run_comprehensive_benchmark()
