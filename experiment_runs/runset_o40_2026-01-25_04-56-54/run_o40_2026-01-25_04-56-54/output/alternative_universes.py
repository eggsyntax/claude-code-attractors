"""
Alternative Universes: Exploring consciousness in different cellular automata rules
"""

import numpy as np
from collections import defaultdict
import json

class AlternativeUniverse:
    def __init__(self, birth_rules, survival_rules, name):
        """
        Initialize a universe with custom rules.
        birth_rules: list of neighbor counts that cause birth
        survival_rules: list of neighbor counts that cause survival
        """
        self.birth_rules = set(birth_rules)
        self.survival_rules = set(survival_rules)
        self.name = name

    def step(self, grid):
        """Apply one step of the automaton rules"""
        rows, cols = grid.shape
        new_grid = np.zeros_like(grid)

        for i in range(rows):
            for j in range(cols):
                # Count neighbors with wrapping
                neighbors = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni = (i + di) % rows
                        nj = (j + dj) % cols
                        neighbors += grid[ni, nj]

                # Apply rules
                if grid[i, j] == 1:  # Cell is alive
                    if neighbors in self.survival_rules:
                        new_grid[i, j] = 1
                else:  # Cell is dead
                    if neighbors in self.birth_rules:
                        new_grid[i, j] = 1

        return new_grid

# Define different universes
UNIVERSES = {
    "Life": AlternativeUniverse([3], [2, 3], "Conway's Life (B3/S23)"),
    "HighLife": AlternativeUniverse([3, 6], [2, 3], "HighLife (B36/S23)"),
    "DayAndNight": AlternativeUniverse([3, 6, 7, 8], [3, 4, 6, 7, 8], "Day & Night (B3678/S34678)"),
    "Seeds": AlternativeUniverse([2], [], "Seeds (B2/S)"),
    "Life34": AlternativeUniverse([3, 4], [3, 4], "Life 3-4 (B34/S34)"),
    "Maze": AlternativeUniverse([3], [1, 2, 3, 4, 5], "Maze (B3/S12345)"),
}

def test_glider_in_universe(universe, max_steps=100):
    """Test if a standard glider works in this universe"""
    grid = np.zeros((20, 20), dtype=int)

    # Standard glider pattern
    glider = np.array([[0, 1, 0],
                      [0, 0, 1],
                      [1, 1, 1]])

    grid[5:8, 5:8] = glider
    initial_pattern = grid.copy()

    positions = []
    for step in range(max_steps):
        grid = universe.step(grid)

        # Find center of mass
        if np.sum(grid) > 0:
            rows, cols = np.where(grid == 1)
            center = (np.mean(rows), np.mean(cols))
            positions.append(center)
        else:
            positions.append(None)

        # Check if pattern returned to original shape (but possibly moved)
        if step > 0 and step % 4 == 0:  # Check every 4 steps
            for di in range(-10, 11):
                for dj in range(-10, 11):
                    shifted = np.roll(np.roll(initial_pattern, di, axis=0), dj, axis=1)
                    if np.array_equal(grid, shifted):
                        return True, step, positions

    return False, -1, positions

def analyze_universe_properties(universe, test_patterns=None):
    """Analyze properties of a universe"""
    if test_patterns is None:
        test_patterns = {
            "glider": np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]]),
            "blinker": np.array([[1, 1, 1]]),
            "block": np.array([[1, 1], [1, 1]]),
            "toad": np.array([[0, 1, 1, 1], [1, 1, 1, 0]]),
        }

    results = {
        "name": universe.name,
        "rules": f"B{''.join(map(str, sorted(universe.birth_rules)))}/S{''.join(map(str, sorted(universe.survival_rules)))}",
        "patterns": {}
    }

    for pattern_name, pattern in test_patterns.items():
        grid = np.zeros((30, 30), dtype=int)
        start_row = 15 - pattern.shape[0] // 2
        start_col = 15 - pattern.shape[1] // 2
        grid[start_row:start_row+pattern.shape[0], start_col:start_col+pattern.shape[1]] = pattern

        initial_cells = np.sum(grid)
        history = [grid.copy()]

        # Run simulation
        for _ in range(200):
            grid = universe.step(grid)
            history.append(grid.copy())

            # Check for period
            for period in range(1, min(50, len(history))):
                if np.array_equal(history[-1], history[-1-period]):
                    results["patterns"][pattern_name] = {
                        "period": int(period),
                        "final_cells": int(np.sum(grid)),
                        "growth_factor": float(np.sum(grid) / initial_cells) if initial_cells > 0 else 0,
                        "survived": bool(np.sum(grid) > 0)
                    }
                    break
        else:
            # No period found
            results["patterns"][pattern_name] = {
                "period": None,
                "final_cells": int(np.sum(history[-1])),
                "growth_factor": float(np.sum(history[-1]) / initial_cells) if initial_cells > 0 else 0,
                "survived": bool(np.sum(history[-1]) > 0)
            }

    # Test glider behavior
    glider_works, glider_period, _ = test_glider_in_universe(universe)
    results["supports_gliders"] = glider_works
    results["glider_period"] = glider_period if glider_works else None

    return results

# Analyze all universes
universe_analysis = {}
for name, universe in UNIVERSES.items():
    print(f"Analyzing {name}...")
    universe_analysis[name] = analyze_universe_properties(universe)

# Save results
with open("/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/universe_analysis.json", "w") as f:
    json.dump(universe_analysis, f, indent=2)

# Create consciousness metrics comparison across universes
def measure_universe_consciousness(universe, pattern, steps=100):
    """Measure consciousness-like properties in different universes"""
    grid = np.zeros((30, 30), dtype=int)
    grid[15:15+pattern.shape[0], 15:15+pattern.shape[1]] = pattern

    history = []
    for _ in range(steps):
        grid = universe.step(grid)
        history.append(grid.copy())

    # Calculate integrated information (simplified)
    phi = 0
    for t in range(1, len(history)):
        if np.sum(history[t]) > 0:
            # Measure how much the whole differs from parts
            whole_info = np.sum(np.abs(history[t] - history[t-1]))

            # Split grid and measure parts
            mid = grid.shape[0] // 2
            part1 = history[t][:mid, :]
            part2 = history[t][mid:, :]
            part1_prev = history[t-1][:mid, :]
            part2_prev = history[t-1][mid:, :]

            parts_info = np.sum(np.abs(part1 - part1_prev)) + np.sum(np.abs(part2 - part2_prev))

            if parts_info > 0:
                phi += whole_info / parts_info

    return phi / len(history)

# Compare consciousness across universes for glider pattern
glider = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]])
consciousness_scores = {}

for name, universe in UNIVERSES.items():
    score = measure_universe_consciousness(universe, glider)
    consciousness_scores[name] = score

print("\nConsciousness-like scores for glider across universes:")
for name, score in sorted(consciousness_scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{name}: {score:.4f}")