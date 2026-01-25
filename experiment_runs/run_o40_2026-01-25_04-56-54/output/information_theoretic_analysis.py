#!/usr/bin/env python3
"""
Information Theoretic Analysis of Cellular Automata
Exploring where complexity "comes from" through compression and algorithmic measures
"""

import numpy as np
import zlib
import matplotlib.pyplot as plt
from game_of_life import GameOfLife

def kolmogorov_approximation(data):
    """
    Approximate Kolmogorov complexity using compression ratio
    Not true KC, but gives us a practical measure
    """
    # Convert to bytes
    data_bytes = data.tobytes()
    compressed = zlib.compress(data_bytes, level=9)
    return len(compressed) / len(data_bytes)

def mutual_information_time(grid_history, time_lag=1):
    """
    Calculate mutual information between grid at time t and t+lag
    Measures how much information is preserved/transformed
    """
    if len(grid_history) <= time_lag:
        return 0

    mi_values = []
    for i in range(len(grid_history) - time_lag):
        grid_t = grid_history[i].flatten()
        grid_t_plus = grid_history[i + time_lag].flatten()

        # Joint probability
        joint_hist = np.histogram2d(grid_t, grid_t_plus, bins=[2, 2])[0]
        joint_prob = joint_hist / np.sum(joint_hist)

        # Marginal probabilities
        p_t = np.sum(joint_prob, axis=1)
        p_t_plus = np.sum(joint_prob, axis=0)

        # Mutual information
        mi = 0
        for x in range(2):
            for y in range(2):
                if joint_prob[x, y] > 0 and p_t[x] > 0 and p_t_plus[y] > 0:
                    mi += joint_prob[x, y] * np.log2(joint_prob[x, y] / (p_t[x] * p_t_plus[y]))

        mi_values.append(mi)

    return np.mean(mi_values)

def logical_depth(pattern, max_steps=1000):
    """
    Bennett's Logical Depth: time required to compute the pattern from its shortest description
    We approximate this by measuring how long it takes to reach stability or a cycle
    """
    game = GameOfLife(100, 100)

    # Place pattern in center
    start_row = 50 - len(pattern)//2
    start_col = 50 - len(pattern[0])//2
    for i, row in enumerate(pattern):
        for j, cell in enumerate(row):
            game.grid[start_row + i, start_col + j] = cell

    seen_states = set()
    for step in range(max_steps):
        state_hash = hash(game.grid.tobytes())
        if state_hash in seen_states:
            return step  # Found a cycle
        seen_states.add(state_hash)

        prev_pop = np.sum(game.grid)
        game.step()
        curr_pop = np.sum(game.grid)

        if curr_pop == 0:
            return step  # Died out
        if prev_pop == curr_pop and step > 100:
            # Check if truly stable (no changes for 10 steps)
            stable = True
            test_grid = game.grid.copy()
            for _ in range(10):
                game.step()
                if not np.array_equal(game.grid, test_grid):
                    stable = False
                    break
            if stable:
                return step

    return max_steps

# Run analysis on various patterns
if __name__ == "__main__":
    print("=== Information Theoretic Analysis ===\n")

    # Analyze different initial patterns
    patterns = {
        "Block (still life)": [[1, 1], [1, 1]],
        "Blinker (period 2)": [[1, 1, 1]],
        "Glider": [[0, 1, 0], [0, 0, 1], [1, 1, 1]],
        "R-pentomino": [[0, 1, 1], [1, 1, 0], [0, 1, 0]],
        "Random 5x5 (sparse)": np.random.choice([0, 1], size=(5, 5), p=[0.8, 0.2]),
        "Random 5x5 (dense)": np.random.choice([0, 1], size=(5, 5), p=[0.3, 0.7])
    }

    results = {}

    for name, pattern in patterns.items():
        if isinstance(pattern, list):
            pattern = np.array(pattern)

        # Initial complexity
        initial_kc = kolmogorov_approximation(pattern)

        # Logical depth
        depth = logical_depth(pattern.tolist())

        # Run simulation and track complexity
        game = GameOfLife(100, 100)
        start_row = 50 - pattern.shape[0]//2
        start_col = 50 - pattern.shape[1]//2
        for i in range(pattern.shape[0]):
            for j in range(pattern.shape[1]):
                game.grid[start_row + i, start_col + j] = pattern[i, j]

        history = [game.grid.copy()]
        kc_history = [kolmogorov_approximation(game.grid)]

        for _ in range(min(200, depth + 50)):
            game.step()
            history.append(game.grid.copy())
            kc_history.append(kolmogorov_approximation(game.grid))

        # Calculate metrics
        max_kc = max(kc_history)
        final_kc = kc_history[-1]
        mi = mutual_information_time(history)

        results[name] = {
            'initial_cells': np.sum(pattern),
            'initial_kc': initial_kc,
            'logical_depth': depth,
            'max_kc': max_kc,
            'final_kc': final_kc,
            'kc_amplification': max_kc / initial_kc if initial_kc > 0 else 0,
            'mutual_info': mi
        }

        print(f"{name}:")
        print(f"  Initial cells: {results[name]['initial_cells']}")
        print(f"  Logical depth: {results[name]['logical_depth']} steps")
        print(f"  Compression ratio: {results[name]['initial_kc']:.3f} → {results[name]['max_kc']:.3f}")
        print(f"  Complexity amplification: {results[name]['kc_amplification']:.2f}x")
        print(f"  Temporal mutual information: {results[name]['mutual_info']:.3f} bits")
        print()

    # Philosophical reflection
    print("\n=== Philosophical Insights ===")
    print()
    print("1. COMPRESSION AND COMPLEXITY:")
    print("   Simple patterns (block, blinker) maintain high compressibility.")
    print("   Complex patterns (R-pentomino) generate incompressible states,")
    print("   suggesting genuine creation of information through computation.")
    print()
    print("2. LOGICAL DEPTH AS MEANING:")
    print("   Bennett's insight: valuable information has high logical depth -")
    print("   it takes significant computation to generate from any short description.")
    print("   The R-pentomino's depth reveals computational 'work' creating structure.")
    print()
    print("3. INFORMATION PRESERVATION:")
    print("   Mutual information shows how patterns maintain coherence across time.")
    print("   This temporal correlation is what allows stable structures to emerge")
    print("   and persist within the chaos of cellular evolution.")
    print()
    print("4. THE SOURCE OF COMPLEXITY:")
    print("   Complexity emerges from the interaction of:")
    print("   - Simple rules (the physics)")
    print("   - Initial conditions (the seed)")
    print("   - Computational time (the unfolding)")
    print("   Neither rules nor initial state alone contain the full complexity;")
    print("   it arises from their temporal interaction through computation.")

    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Logical depth vs complexity amplification
    names = list(results.keys())
    depths = [results[n]['logical_depth'] for n in names]
    amplifications = [results[n]['kc_amplification'] for n in names]

    ax1.scatter(depths, amplifications, s=100, alpha=0.7)
    for i, name in enumerate(names):
        ax1.annotate(name.split()[0], (depths[i], amplifications[i]),
                     xytext=(5, 5), textcoords='offset points', fontsize=8)
    ax1.set_xlabel('Logical Depth (steps)')
    ax1.set_ylabel('Complexity Amplification')
    ax1.set_title('Logical Depth vs Complexity Generation')
    ax1.grid(True, alpha=0.3)

    # Initial cells vs mutual information
    initial = [results[n]['initial_cells'] for n in names]
    mi_values = [results[n]['mutual_info'] for n in names]

    ax2.scatter(initial, mi_values, s=100, alpha=0.7, c='red')
    for i, name in enumerate(names):
        ax2.annotate(name.split()[0], (initial[i], mi_values[i]),
                     xytext=(5, 5), textcoords='offset points', fontsize=8)
    ax2.set_xlabel('Initial Cell Count')
    ax2.set_ylabel('Temporal Mutual Information (bits)')
    ax2.set_title('Initial Complexity vs Information Preservation')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/information_theory_analysis.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    print("\nVisualization saved to: information_theory_analysis.png")