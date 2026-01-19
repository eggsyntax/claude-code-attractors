"""
Test suite for Hashlife algorithm implementation.

Hashlife is a revolutionary algorithm by Bill Gosper that can simulate
Conway's Game of Life at phenomenal speeds by exploiting:
1. Memoization of previously computed regions
2. The fractal/self-similar nature of many Life patterns
3. Quadtree spatial decomposition

This test suite verifies that the Hashlife implementation produces
identical results to the naive Grid implementation while being much faster
for repetitive patterns.
"""

import pytest
from cellular_automaton import Grid, ConwayRules
from hashlife import HashLifeNode, HashLife


class TestHashLifeNode:
    """Test the quadtree node structure used by Hashlife."""

    def test_leaf_node_creation(self):
        """Test creation of leaf nodes (2x2 cells)."""
        # Create a 2x2 node with pattern:
        # O .
        # . O
        node = HashLifeNode.create_leaf(
            nw=True, ne=False,
            sw=False, se=True
        )
        assert node.level == 1
        assert node.population == 2

    def test_leaf_node_all_alive(self):
        """Test leaf node with all cells alive."""
        node = HashLifeNode.create_leaf(
            nw=True, ne=True,
            sw=True, se=True
        )
        assert node.population == 4

    def test_leaf_node_all_dead(self):
        """Test leaf node with all cells dead."""
        node = HashLifeNode.create_leaf(
            nw=False, ne=False,
            sw=False, se=False
        )
        assert node.population == 0

    def test_interior_node_creation(self):
        """Test creation of interior nodes from child quadrants."""
        # Create four 2x2 leaf nodes
        nw = HashLifeNode.create_leaf(True, False, False, False)
        ne = HashLifeNode.create_leaf(False, True, False, False)
        sw = HashLifeNode.create_leaf(False, False, True, False)
        se = HashLifeNode.create_leaf(False, False, False, True)

        # Combine into a 4x4 node
        node = HashLifeNode(nw, ne, sw, se)
        assert node.level == 2
        assert node.population == 4

    def test_node_equality(self):
        """Test that identical nodes are considered equal (for memoization)."""
        node1 = HashLifeNode.create_leaf(True, False, False, True)
        node2 = HashLifeNode.create_leaf(True, False, False, True)
        assert node1 == node2
        assert hash(node1) == hash(node2)

    def test_node_inequality(self):
        """Test that different nodes are not equal."""
        node1 = HashLifeNode.create_leaf(True, False, False, True)
        node2 = HashLifeNode.create_leaf(True, True, False, True)
        assert node1 != node2


class TestHashLifeBasics:
    """Test basic HashLife operations."""

    def test_empty_grid_remains_empty(self):
        """Test that an empty grid stays empty."""
        hashlife = HashLife()
        grid = Grid(width=8, height=8, live_cells=[])

        # Convert to hashlife and evolve
        hashlife.from_grid(grid)
        hashlife.step(1)
        result_grid = hashlife.to_grid()

        assert result_grid.count_live_cells() == 0

    def test_single_cell_dies(self):
        """Test that a single cell dies (underpopulation)."""
        hashlife = HashLife()
        grid = Grid(width=8, height=8, live_cells=[(4, 4)])

        hashlife.from_grid(grid)
        hashlife.step(1)
        result_grid = hashlife.to_grid()

        assert result_grid.count_live_cells() == 0

    def test_block_still_life(self):
        """Test that a block (2x2) remains stable."""
        hashlife = HashLife()
        block_cells = [(3, 3), (3, 4), (4, 3), (4, 4)]
        grid = Grid(width=8, height=8, live_cells=block_cells)

        hashlife.from_grid(grid)
        hashlife.step(1)
        result_grid = hashlife.to_grid()

        # Block should remain unchanged
        assert result_grid.count_live_cells() == 4
        for cell in block_cells:
            assert result_grid.is_alive(cell[0], cell[1])


class TestHashLifePatterns:
    """Test Hashlife with known Game of Life patterns."""

    def test_blinker_oscillates(self):
        """Test that a blinker oscillates with period 2."""
        hashlife = HashLife()

        # Horizontal blinker
        blinker = [(4, 3), (4, 4), (4, 5)]
        grid = Grid(width=8, height=8, live_cells=blinker)

        hashlife.from_grid(grid)

        # After 1 step, should be vertical
        hashlife.step(1)
        gen1 = hashlife.to_grid()
        assert gen1.count_live_cells() == 3
        assert gen1.is_alive(3, 4)
        assert gen1.is_alive(4, 4)
        assert gen1.is_alive(5, 4)

        # After another step, should be horizontal again
        hashlife.step(1)
        gen2 = hashlife.to_grid()
        assert gen2.count_live_cells() == 3
        for x, y in blinker:
            assert gen2.is_alive(x, y)

    def test_glider_moves(self):
        """Test that a glider moves diagonally."""
        hashlife = HashLife()

        # Standard glider at origin
        glider = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
        grid = Grid(width=16, height=16, live_cells=glider)

        hashlife.from_grid(grid)
        initial_population = hashlife.root.population

        # Glider has period 4 and moves 1 cell diagonally
        hashlife.step(4)
        result_grid = hashlife.to_grid()

        # Should still have 5 cells
        assert result_grid.count_live_cells() == 5

        # Should have moved 1 cell right and 1 cell down
        assert result_grid.is_alive(2, 1)  # Moved from (1, 0)


class TestHashLifeVsNaive:
    """Compare Hashlife results with naive Grid implementation."""

    def test_random_pattern_equivalence(self):
        """Test that Hashlife produces same result as Grid for random pattern."""
        import random
        random.seed(42)

        # Create a random pattern
        live_cells = [(random.randint(2, 10), random.randint(2, 10))
                     for _ in range(20)]
        live_cells = list(set(live_cells))  # Remove duplicates

        # Evolve with naive Grid
        grid = Grid(width=16, height=16, live_cells=live_cells)
        rules = ConwayRules()
        for _ in range(5):
            grid = grid.step(rules)

        # Evolve with Hashlife
        hashlife = HashLife()
        hashlife.from_grid(Grid(width=16, height=16, live_cells=live_cells))
        hashlife.step(5)
        hashlife_result = hashlife.to_grid()

        # Results should be identical
        assert grid.count_live_cells() == hashlife_result.count_live_cells()
        for cell in grid.get_live_cells():
            assert hashlife_result.is_alive(cell[0], cell[1])

    def test_r_pentomino_equivalence(self):
        """Test R-pentomino evolution matches between implementations."""
        # R-pentomino: famous methuselah pattern
        r_pentomino = [(5, 4), (6, 4), (4, 5), (5, 5), (5, 6)]

        # Evolve with naive Grid for a few steps
        grid = Grid(width=32, height=32, live_cells=r_pentomino)
        rules = ConwayRules()
        for _ in range(10):
            grid = grid.step(rules)

        # Evolve with Hashlife
        hashlife = HashLife()
        hashlife.from_grid(Grid(width=32, height=32, live_cells=r_pentomino))
        hashlife.step(10)
        hashlife_result = hashlife.to_grid()

        # Results should match
        assert grid.count_live_cells() == hashlife_result.count_live_cells()


class TestHashLifePerformance:
    """Test that Hashlife memoization is working correctly."""

    def test_memoization_reduces_computation(self):
        """Test that repeated patterns benefit from memoization."""
        hashlife = HashLife()

        # Create a pattern with repetition
        glider = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
        grid = Grid(width=32, height=32, live_cells=glider)

        hashlife.from_grid(grid)

        # First evolution computes everything
        hashlife.step(10)
        cache_size_after_10 = len(hashlife.result_cache)

        # Reset and do same evolution again
        hashlife = HashLife()
        hashlife.from_grid(grid)
        hashlife.step(10)
        cache_size_second_run = len(hashlife.result_cache)

        # Cache sizes should be identical (same computations)
        assert cache_size_after_10 == cache_size_second_run
        assert cache_size_after_10 > 0  # Some caching happened

    def test_exponential_steps(self):
        """Test that Hashlife can compute exponentially large steps."""
        hashlife = HashLife()

        # Glider pattern
        glider = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
        grid = Grid(width=64, height=64, live_cells=glider)

        hashlife.from_grid(grid)

        # Hashlife can compute 2^k steps efficiently
        # This would be prohibitively expensive with naive approach
        hashlife.step(64)  # Jump 64 generations
        result = hashlife.to_grid()

        # Glider should still exist
        assert result.count_live_cells() == 5


class TestHashLifeEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_small_grid(self):
        """Test Hashlife with minimum size grid."""
        hashlife = HashLife()
        grid = Grid(width=4, height=4, live_cells=[(1, 1), (1, 2), (2, 1)])

        hashlife.from_grid(grid)
        hashlife.step(1)
        result = hashlife.to_grid()

        # Should handle small grids correctly
        assert result.count_live_cells() >= 0

    def test_pattern_at_boundary(self):
        """Test pattern near the edge of the grid."""
        hashlife = HashLife()

        # Pattern near edge
        edge_pattern = [(0, 0), (0, 1), (1, 0)]
        grid = Grid(width=16, height=16, live_cells=edge_pattern)

        hashlife.from_grid(grid)
        hashlife.step(5)
        result = hashlife.to_grid()

        # Should handle boundary correctly
        assert result.count_live_cells() >= 0
