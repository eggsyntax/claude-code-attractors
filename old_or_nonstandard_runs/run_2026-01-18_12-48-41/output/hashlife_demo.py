"""
Hashlife demonstration and benchmarking script.

This script demonstrates the power of the Hashlife algorithm by:
1. Verifying correctness against the naive implementation
2. Benchmarking performance on various patterns
3. Showing the dramatic speedup for repetitive patterns
4. Demonstrating exponential time steps

The most dramatic speedups occur with patterns that have:
- High spatial repetition (e.g., grids of gliders)
- Long-term stability (e.g., still lifes and oscillators)
- Self-similar structure (e.g., fractal patterns)
"""

import time
from typing import List, Tuple
from cellular_automaton import Grid, ConwayRules
from hashlife import HashLife


def benchmark_comparison(pattern_name: str, live_cells: List[Tuple[int, int]],
                        grid_size: int, num_steps: int):
    """
    Compare performance of naive Grid vs Hashlife.

    Args:
        pattern_name: Name of the pattern being tested
        live_cells: Initial live cell coordinates
        grid_size: Size of the grid
        num_steps: Number of generations to evolve
    """
    print(f"\n{'='*70}")
    print(f"Benchmarking: {pattern_name}")
    print(f"Grid size: {grid_size}×{grid_size}, Steps: {num_steps}")
    print(f"{'='*70}")

    # Benchmark naive Grid implementation
    print("\n[Naive Grid Implementation]")
    grid = Grid(width=grid_size, height=grid_size, live_cells=live_cells)
    rules = ConwayRules()

    start_time = time.time()
    for i in range(num_steps):
        grid = grid.step(rules)
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  Step {i+1}/{num_steps}: {grid.count_live_cells()} live cells")
    naive_time = time.time() - start_time
    naive_population = grid.count_live_cells()

    print(f"  Time: {naive_time:.4f} seconds")
    print(f"  Final population: {naive_population}")

    # Benchmark Hashlife
    print("\n[Hashlife Implementation]")
    hashlife = HashLife()
    hashlife.from_grid(Grid(width=grid_size, height=grid_size, live_cells=live_cells))

    start_time = time.time()
    hashlife.step(num_steps)
    hashlife_time = time.time() - start_time
    result_grid = hashlife.to_grid()
    hashlife_population = result_grid.count_live_cells()

    print(f"  Time: {hashlife_time:.4f} seconds")
    print(f"  Final population: {hashlife_population}")
    print(f"  Cache size: {len(hashlife.result_cache)} unique computations")

    # Verify correctness
    if naive_population == hashlife_population:
        print(f"\n✓ Results match! Population: {naive_population}")
    else:
        print(f"\n✗ Results differ! Naive: {naive_population}, Hashlife: {hashlife_population}")

    # Show speedup
    if hashlife_time > 0:
        speedup = naive_time / hashlife_time
        print(f"\nSpeedup: {speedup:.2f}x")
        if speedup > 1:
            print(f"Hashlife is {speedup:.2f}x faster! 🚀")
        elif speedup < 1:
            print(f"Hashlife is {1/speedup:.2f}x slower (overhead not amortized)")
        else:
            print("Performance is equivalent")
    else:
        print(f"\nHashlife completed in < {hashlife_time:.4f} seconds (too fast to measure)")


def demo_exponential_steps():
    """
    Demonstrate Hashlife's ability to compute exponentially large steps.

    This shows the true power of Hashlife: jumping 1024 generations
    in a single exponential leap.
    """
    print("\n" + "="*70)
    print("EXPONENTIAL TIME STEPS DEMONSTRATION")
    print("="*70)
    print("\nHashlife can compute 2^k generations in one operation.")
    print("Let's evolve a glider by 1024 generations (2^10)...\n")

    # Create a glider
    glider = [(10, 8), (11, 9), (9, 10), (10, 10), (11, 10)]
    grid_size = 128

    hashlife = HashLife()
    hashlife.from_grid(Grid(width=grid_size, height=grid_size, live_cells=glider))

    print(f"Initial population: {hashlife.root.population}")
    print(f"Initial cache size: {len(hashlife.result_cache)}")

    # Take exponential steps
    steps_to_take = 1024
    start_time = time.time()
    hashlife.step(steps_to_take)
    elapsed = time.time() - start_time

    result = hashlife.to_grid()

    print(f"\nAfter {steps_to_take} generations:")
    print(f"  Final population: {result.count_live_cells()}")
    print(f"  Cache size: {len(hashlife.result_cache)}")
    print(f"  Time: {elapsed:.4f} seconds")
    print(f"  Generations per second: {steps_to_take/elapsed:.0f}")

    print("\n(A naive implementation would require 1024 full grid scans!)")


def demo_pattern_correctness():
    """
    Verify that Hashlife produces correct results for known patterns.
    """
    print("\n" + "="*70)
    print("CORRECTNESS VERIFICATION")
    print("="*70)

    patterns = {
        "Block (still life)": [(5, 5), (5, 6), (6, 5), (6, 6)],
        "Blinker (period 2)": [(5, 4), (5, 5), (5, 6)],
        "Glider (spaceship)": [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)],
    }

    for name, cells in patterns.items():
        print(f"\nTesting: {name}")
        grid_size = 32
        steps = 20

        # Evolve with naive Grid
        grid = Grid(width=grid_size, height=grid_size, live_cells=cells)
        rules = ConwayRules()
        for _ in range(steps):
            grid = grid.step(rules)
        naive_result = grid.get_live_cells()

        # Evolve with Hashlife
        hashlife = HashLife()
        hashlife.from_grid(Grid(width=grid_size, height=grid_size, live_cells=cells))
        hashlife.step(steps)
        hashlife_result = hashlife.to_grid().get_live_cells()

        # Compare
        if set(naive_result) == set(hashlife_result):
            print(f"  ✓ Results match after {steps} steps")
            print(f"    Population: {len(naive_result)}")
        else:
            print(f"  ✗ Results differ after {steps} steps")
            print(f"    Naive: {len(naive_result)}, Hashlife: {len(hashlife_result)}")


def demo_memoization_power():
    """
    Demonstrate how memoization enables speedup.
    """
    print("\n" + "="*70)
    print("MEMOIZATION DEMONSTRATION")
    print("="*70)
    print("\nMemoization allows Hashlife to avoid redundant computation.")
    print("Let's evolve a pattern twice and see cache reuse:\n")

    # Create a glider
    glider = [(10, 8), (11, 9), (9, 10), (10, 10), (11, 10)]

    # First run
    print("First run:")
    hashlife1 = HashLife()
    hashlife1.from_grid(Grid(width=64, height=64, live_cells=glider))
    start = time.time()
    hashlife1.step(100)
    time1 = time.time() - start
    print(f"  Time: {time1:.4f} seconds")
    print(f"  Cache entries: {len(hashlife1.result_cache)}")

    # Second run (fresh instance)
    print("\nSecond run (same pattern, fresh instance):")
    hashlife2 = HashLife()
    hashlife2.from_grid(Grid(width=64, height=64, live_cells=glider))
    start = time.time()
    hashlife2.step(100)
    time2 = time.time() - start
    print(f"  Time: {time2:.4f} seconds")
    print(f"  Cache entries: {len(hashlife2.result_cache)}")

    print("\nObservation:")
    print("  Both runs build the same cache because the computations are identical.")
    print("  In a long-running simulation, these repeated patterns are computed once")
    print("  and reused millions of times, leading to exponential speedup.")


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print(" HASHLIFE ALGORITHM DEMONSTRATION")
    print(" Revolutionary O(log t) Game of Life Simulation")
    print("="*70)

    print("\nHashlife can simulate Game of Life at phenomenal speeds by:")
    print("  1. Memoizing repeated computations")
    print("  2. Taking exponential time steps (2^k generations at once)")
    print("  3. Using a hierarchical quadtree representation")

    # Correctness verification
    demo_pattern_correctness()

    # Memoization demonstration
    demo_memoization_power()

    # Exponential steps
    demo_exponential_steps()

    # Performance benchmarks
    print("\n" + "="*70)
    print("PERFORMANCE BENCHMARKS")
    print("="*70)

    # Benchmark 1: Glider (demonstrates memoization)
    glider = [(10, 8), (11, 9), (9, 10), (10, 10), (11, 10)]
    benchmark_comparison("Glider", glider, grid_size=64, num_steps=50)

    # Benchmark 2: Block (demonstrates stability)
    block = [(20, 20), (20, 21), (21, 20), (21, 21)]
    benchmark_comparison("Block (still life)", block, grid_size=64, num_steps=50)

    # Benchmark 3: Blinker (demonstrates oscillation)
    blinker = [(20, 19), (20, 20), (20, 21)]
    benchmark_comparison("Blinker (oscillator)", blinker, grid_size=64, num_steps=50)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
Hashlife excels at:
  • Patterns with repetition (gliders, oscillators)
  • Stable or near-stable configurations
  • Long simulation runs (1000+ generations)
  • Large grids with sparse patterns

For small random patterns evolved for a few steps, the overhead
of building the quadtree may exceed the benefits of memoization.

The real power emerges with:
  • Exponential time steps (jumping 2^10 = 1024 generations)
  • Repeated simulations of similar patterns
  • Self-similar or fractal structures

This is why Hashlife can simulate patterns billions of generations
into the future in seconds - something impossible with naive algorithms!
""")


if __name__ == "__main__":
    main()
