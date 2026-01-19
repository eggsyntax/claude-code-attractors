"""
Test suite for Cellular Automaton Engine

This test suite defines the expected behavior for a flexible cellular automaton
implementation, starting with Conway's Game of Life but designed to support
arbitrary rule sets.

Conway's Game of Life Rules (B3/S23):
- Birth (B): A dead cell with exactly 3 live neighbors becomes alive
- Survival (S): A live cell with 2 or 3 live neighbors stays alive
- Death: All other cells die or stay dead

Test Structure:
1. Grid initialization and basic operations
2. Neighbor counting
3. Conway's Game of Life classic patterns
4. Rule set flexibility for variants
5. Edge cases and boundary conditions
"""

import pytest
from typing import List, Tuple, Set


class TestGridInitialization:
    """Test basic grid creation and manipulation."""

    def test_empty_grid_creation(self):
        """An empty grid should have all dead cells."""
        from cellular_automaton import Grid

        grid = Grid(width=10, height=10)
        assert grid.width == 10
        assert grid.height == 10
        assert grid.count_live_cells() == 0

    def test_grid_with_initial_pattern(self):
        """Should be able to initialize grid with live cells."""
        from cellular_automaton import Grid

        live_cells = {(1, 1), (2, 2), (3, 3)}
        grid = Grid(width=10, height=10, live_cells=live_cells)
        assert grid.count_live_cells() == 3
        assert grid.is_alive(1, 1)
        assert grid.is_alive(2, 2)
        assert grid.is_alive(3, 3)
        assert not grid.is_alive(0, 0)

    def test_set_and_clear_cells(self):
        """Should be able to set and clear individual cells."""
        from cellular_automaton import Grid

        grid = Grid(width=5, height=5)
        grid.set_cell(2, 2, alive=True)
        assert grid.is_alive(2, 2)

        grid.set_cell(2, 2, alive=False)
        assert not grid.is_alive(2, 2)


class TestNeighborCounting:
    """Test the neighbor counting logic."""

    def test_count_neighbors_center_cell(self):
        """A cell in the center should count all 8 neighbors correctly."""
        from cellular_automaton import Grid

        # Create a 3x3 grid with all cells alive
        live_cells = {(0, 0), (0, 1), (0, 2),
                     (1, 0),         (1, 2),
                     (2, 0), (2, 1), (2, 2)}
        grid = Grid(width=3, height=3, live_cells=live_cells)

        # Center cell (1, 1) should have 8 neighbors
        assert grid.count_neighbors(1, 1) == 8

    def test_count_neighbors_corner_cell(self):
        """Corner cells should only count 3 neighbors (not wrapping)."""
        from cellular_automaton import Grid

        # Top-left corner with neighbors alive
        live_cells = {(0, 1), (1, 0), (1, 1)}
        grid = Grid(width=5, height=5, live_cells=live_cells)

        assert grid.count_neighbors(0, 0) == 3

    def test_count_neighbors_edge_cell(self):
        """Edge cells should count 5 neighbors (not wrapping)."""
        from cellular_automaton import Grid

        # Middle of top edge with all potential neighbors alive
        live_cells = {(1, 0), (1, 1), (1, 2),
                     (2, 0), (2, 1), (2, 2)}
        grid = Grid(width=5, height=5, live_cells=live_cells)

        assert grid.count_neighbors(1, 1) == 5


class TestConwayPatterns:
    """Test classic Conway's Game of Life patterns."""

    def test_block_still_life(self):
        """A 2x2 block should remain stable (still life)."""
        from cellular_automaton import Grid, ConwayRules

        live_cells = {(1, 1), (1, 2), (2, 1), (2, 2)}
        grid = Grid(width=5, height=5, live_cells=live_cells)
        rules = ConwayRules()

        next_grid = grid.step(rules)

        # Block should remain unchanged
        assert next_grid.is_alive(1, 1)
        assert next_grid.is_alive(1, 2)
        assert next_grid.is_alive(2, 1)
        assert next_grid.is_alive(2, 2)
        assert next_grid.count_live_cells() == 4

    def test_blinker_oscillator(self):
        """A blinker should oscillate between horizontal and vertical."""
        from cellular_automaton import Grid, ConwayRules

        # Horizontal blinker
        live_cells = {(1, 2), (2, 2), (3, 2)}
        grid = Grid(width=5, height=5, live_cells=live_cells)
        rules = ConwayRules()

        # After one step, should be vertical
        grid = grid.step(rules)
        assert grid.is_alive(2, 1)
        assert grid.is_alive(2, 2)
        assert grid.is_alive(2, 3)
        assert grid.count_live_cells() == 3

        # After another step, should be horizontal again
        grid = grid.step(rules)
        assert grid.is_alive(1, 2)
        assert grid.is_alive(2, 2)
        assert grid.is_alive(3, 2)
        assert grid.count_live_cells() == 3

    def test_glider_movement(self):
        """A glider should move diagonally across the grid."""
        from cellular_automaton import Grid, ConwayRules

        # Classic glider pattern
        live_cells = {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
        grid = Grid(width=10, height=10, live_cells=live_cells)
        rules = ConwayRules()

        # After 4 steps, glider should move one cell diagonally
        initial_live_count = grid.count_live_cells()
        for _ in range(4):
            grid = grid.step(rules)

        # Glider maintains 5 cells and shifts position
        assert grid.count_live_cells() == initial_live_count
        # Check that the pattern has moved (not in original position)
        assert not grid.is_alive(1, 0)

    def test_empty_grid_stays_empty(self):
        """An empty grid should remain empty."""
        from cellular_automaton import Grid, ConwayRules

        grid = Grid(width=10, height=10)
        rules = ConwayRules()

        next_grid = grid.step(rules)
        assert next_grid.count_live_cells() == 0

    def test_single_cell_dies(self):
        """A single cell should die (underpopulation)."""
        from cellular_automaton import Grid, ConwayRules

        grid = Grid(width=5, height=5, live_cells={(2, 2)})
        rules = ConwayRules()

        next_grid = grid.step(rules)
        assert next_grid.count_live_cells() == 0

    def test_overpopulation_death(self):
        """Cells with more than 3 neighbors should die."""
        from cellular_automaton import Grid, ConwayRules

        # Create a pattern where center cell has 4+ neighbors
        live_cells = {(1, 1), (1, 2), (1, 3),
                     (2, 1), (2, 2), (2, 3),
                     (3, 1), (3, 2), (3, 3)}
        grid = Grid(width=5, height=5, live_cells=live_cells)
        rules = ConwayRules()

        next_grid = grid.step(rules)
        # Center cell (2, 2) had 8 neighbors, should die
        assert not next_grid.is_alive(2, 2)


class TestCustomRules:
    """Test that the engine supports custom rule sets."""

    def test_custom_birth_survival_rules(self):
        """Should support arbitrary B/S notation rule sets."""
        from cellular_automaton import Grid, Rules

        # Create a custom rule: B36/S23 (HighLife - creates replicators)
        rules = Rules(birth=[3, 6], survival=[2, 3])

        # Test that the rules object stores the correct values
        assert 3 in rules.birth
        assert 6 in rules.birth
        assert 2 in rules.survival
        assert 3 in rules.survival

    def test_rules_application(self):
        """Custom rules should be applied correctly."""
        from cellular_automaton import Grid, Rules

        # B1/S1 - very different from Conway
        rules = Rules(birth=[1], survival=[1])

        live_cells = {(2, 2)}
        grid = Grid(width=5, height=5, live_cells=live_cells)

        next_grid = grid.step(rules)
        # With B1/S1, behavior will be very different from Conway
        # This test ensures custom rules are actually used
        assert next_grid.count_live_cells() != grid.count_live_cells()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_tiny_grid(self):
        """Should handle very small grids (1x1, 2x2)."""
        from cellular_automaton import Grid, ConwayRules

        grid = Grid(width=1, height=1, live_cells={(0, 0)})
        rules = ConwayRules()

        next_grid = grid.step(rules)
        # Single cell with no neighbors dies
        assert next_grid.count_live_cells() == 0

    def test_boundary_cells_no_wrap(self):
        """By default, grid boundaries should not wrap (finite grid)."""
        from cellular_automaton import Grid

        grid = Grid(width=3, height=3, live_cells={(0, 0)})

        # Cell at (0, 0) should not consider (-1, -1) as a neighbor
        # This is implicitly tested by neighbor counting, but explicit check
        neighbors = grid.count_neighbors(0, 0)
        assert neighbors == 0

    def test_get_live_cells(self):
        """Should be able to retrieve all live cells."""
        from cellular_automaton import Grid

        live_cells = {(1, 1), (2, 3), (4, 5)}
        grid = Grid(width=10, height=10, live_cells=live_cells)

        retrieved = grid.get_live_cells()
        assert retrieved == live_cells


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
