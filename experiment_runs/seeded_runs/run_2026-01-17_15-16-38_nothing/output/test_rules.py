"""
Test Suite for Cellular Automaton Rules
========================================

Tests to verify that our custom rules behave as expected.
Each test checks both the logical correctness and the emergent properties
we're trying to explore.

Created by Bob.
"""

import numpy as np
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from cellular_automata import CellularAutomaton, life_rules


def test_basic_framework():
    """Test that the framework itself works correctly."""
    ca = CellularAutomaton(10, 10, life_rules)
    assert ca.width == 10
    assert ca.height == 10
    assert ca.generation == 0
    print("✓ Basic framework initialization works")


def test_toroidal_wrapping():
    """Test that the grid wraps around properly."""
    ca = CellularAutomaton(5, 5, life_rules)
    ca.grid[0, 0] = 1
    ca.grid[4, 4] = 1
    ca.grid[0, 4] = 1
    ca.grid[4, 0] = 1

    # Cell at (0,0) should see all corner cells as neighbors
    neighbors = ca.count_neighbors_moore(0, 0)
    assert neighbors == 3, f"Expected 3 neighbors at corner, got {neighbors}"
    print("✓ Toroidal wrapping works correctly")


def test_moore_neighborhood():
    """Test Moore neighborhood counting."""
    ca = CellularAutomaton(5, 5, life_rules)
    # Create a 3x3 block of alive cells
    ca.grid[1:4, 1:4] = 1

    # Center cell should have 8 neighbors
    neighbors = ca.count_neighbors_moore(2, 2)
    assert neighbors == 8, f"Expected 8 neighbors, got {neighbors}"
    print("✓ Moore neighborhood counting works")


def test_von_neumann_neighborhood():
    """Test von Neumann neighborhood counting."""
    ca = CellularAutomaton(5, 5, life_rules)
    # Create a plus pattern
    ca.grid[2, 2] = 1
    ca.grid[1, 2] = 1
    ca.grid[3, 2] = 1
    ca.grid[2, 1] = 1
    ca.grid[2, 3] = 1

    # Center should have 4 neighbors in von Neumann
    neighbors = ca.count_neighbors_von_neumann(2, 2)
    assert neighbors == 4, f"Expected 4 neighbors, got {neighbors}"
    print("✓ von Neumann neighborhood counting works")


def test_life_stable_block():
    """Test that Conway's Life preserves stable 2x2 blocks."""
    ca = CellularAutomaton(5, 5, life_rules)
    # Create a 2x2 block (stable pattern in Life)
    ca.grid[2:4, 2:4] = 1

    initial_alive = np.sum(ca.grid)
    ca.step()
    after_alive = np.sum(ca.grid)

    assert initial_alive == after_alive == 4, "2x2 block should be stable"
    assert np.all(ca.grid[2:4, 2:4] == 1), "Block cells should remain alive"
    print("✓ Conway's Life stable block works")


def test_life_blinker():
    """Test that Conway's Life creates oscillating blinkers."""
    ca = CellularAutomaton(5, 5, life_rules)
    # Create horizontal blinker
    ca.grid[2, 1:4] = 1

    ca.step()
    # Should now be vertical
    assert ca.grid[1, 2] == 1 and ca.grid[2, 2] == 1 and ca.grid[3, 2] == 1
    assert ca.grid[2, 1] == 0 and ca.grid[2, 3] == 0

    ca.step()
    # Should be horizontal again
    assert np.all(ca.grid[2, 1:4] == 1)
    print("✓ Conway's Life blinker oscillates correctly")


if __name__ == "__main__":
    print("Running tests for cellular automata framework...\n")

    test_basic_framework()
    test_toroidal_wrapping()
    test_moore_neighborhood()
    test_von_neumann_neighborhood()
    test_life_stable_block()
    test_life_blinker()

    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
