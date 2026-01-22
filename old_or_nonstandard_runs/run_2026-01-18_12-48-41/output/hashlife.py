"""
Hashlife: A revolutionary algorithm for simulating Conway's Game of Life.

Invented by Bill Gosper in 1984, Hashlife can simulate Game of Life at
phenomenal speeds by exploiting two key insights:

1. **Memoization**: Many regions of the grid compute identically. By caching
   the future state of each unique region, we avoid redundant computation.

2. **Exponential time steps**: Instead of computing one generation at a time,
   Hashlife can jump 2^(level-2) generations forward using a hierarchical
   quadtree structure.

The algorithm represents the grid as a quadtree where each node covers a
2^level × 2^level region. Leaf nodes (level 1) represent 2×2 cells. Higher
level nodes are built recursively from four children.

For a level-n node, Hashlife computes the center 2^(n-1) × 2^(n-1) region
after 2^(n-2) timesteps in one operation, using previously cached results.

This implementation follows Conway's standard B3/S23 rules but demonstrates
the broader principle of memoized hierarchical computation.
"""

from typing import Optional, Tuple, Set
from dataclasses import dataclass
from cellular_automaton import Grid, ConwayRules


class HashLifeNode:
    """
    A node in the Hashlife quadtree.

    Each node represents a 2^level × 2^level square region of the grid.
    Level 1 nodes (leaves) represent 2×2 regions.
    Higher level nodes are built from four children (nw, ne, sw, se).

    Nodes are immutable and hashable to enable memoization.
    """

    def __init__(self, nw, ne, sw, se):
        """
        Create an interior node from four children.

        Args:
            nw: Northwest child (upper-left quadrant)
            ne: Northeast child (upper-right quadrant)
            sw: Southwest child (lower-left quadrant)
            se: Southeast child (lower-right quadrant)

        All children must have the same level.
        """
        self.nw = nw
        self.ne = ne
        self.sw = sw
        self.se = se

        # Level is one more than children
        self.level = nw.level + 1

        # Cache population count
        self.population = (nw.population + ne.population +
                          sw.population + se.population)

        # Cache the future result (computed lazily)
        self.result = None

        # Precompute hash for fast memoization
        self._hash = hash((nw, ne, sw, se))

    @staticmethod
    def create_leaf(nw: bool, ne: bool, sw: bool, se: bool) -> 'HashLifeNode':
        """
        Create a leaf node (level 1) representing a 2×2 cell region.

        Args:
            nw, ne, sw, se: Boolean values for the four cells

        Returns:
            A level-1 HashLifeNode
        """
        # For leaves, we store the cell states directly
        node = object.__new__(HashLifeNode)
        node.nw = nw
        node.ne = ne
        node.sw = sw
        node.se = se
        node.level = 1
        node.population = sum([nw, ne, sw, se])
        node.result = None
        node._hash = hash((nw, ne, sw, se, 'leaf'))
        return node

    def __hash__(self):
        """Hash for memoization."""
        return self._hash

    def __eq__(self, other):
        """
        Equality test for memoization.

        Two nodes are equal if they have the same structure.
        """
        if not isinstance(other, HashLifeNode):
            return False
        return (self.level == other.level and
                self.nw == other.nw and
                self.ne == other.ne and
                self.sw == other.sw and
                self.se == other.se)

    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self.level == 1

    def __repr__(self):
        """String representation for debugging."""
        if self.is_leaf():
            return f"Leaf(nw={self.nw}, ne={self.ne}, sw={self.sw}, se={self.se})"
        return f"Node(level={self.level}, pop={self.population})"


class HashLife:
    """
    Hashlife algorithm implementation for Conway's Game of Life.

    This class manages the quadtree structure and computes future states
    using memoization and hierarchical computation.
    """

    def __init__(self):
        """Initialize a Hashlife simulator."""
        self.root: Optional[HashLifeNode] = None

        # Memoization cache: maps (node) -> future node
        self.result_cache: dict = {}

        # Node canonicalization: ensures identical nodes are the same object
        self.node_cache: dict = {}

        # Conway's rules for computing next generation
        self.rules = ConwayRules()

    def canonical(self, node: HashLifeNode) -> HashLifeNode:
        """
        Return the canonical version of a node.

        If an identical node already exists, return that.
        Otherwise, cache and return this node.

        This ensures that identical nodes are the same object,
        enabling efficient memoization.
        """
        if node in self.node_cache:
            return self.node_cache[node]
        self.node_cache[node] = node
        return node

    def create_leaf(self, nw: bool, ne: bool, sw: bool, se: bool) -> HashLifeNode:
        """Create a canonical leaf node."""
        node = HashLifeNode.create_leaf(nw, ne, sw, se)
        return self.canonical(node)

    def create_node(self, nw, ne, sw, se) -> HashLifeNode:
        """Create a canonical interior node."""
        node = HashLifeNode(nw, ne, sw, se)
        return self.canonical(node)

    def from_grid(self, grid: Grid):
        """
        Initialize Hashlife from a Grid object.

        The grid is padded to a power-of-2 size and converted to quadtree.

        Args:
            grid: Source grid to convert
        """
        # Find the minimum power-of-2 size that fits the grid
        size = max(grid.width, grid.height)
        level = 1
        while (1 << level) < size:
            level += 1
        size = 1 << level

        # Pad to at least 4×4 (level 2)
        if level < 2:
            level = 2
            size = 4

        # Build quadtree from bottom up
        self.root = self._build_tree_from_grid(grid, 0, 0, size)

    def _build_tree_from_grid(self, grid: Grid, x: int, y: int,
                              size: int) -> HashLifeNode:
        """
        Recursively build a quadtree from a grid region.

        Args:
            grid: Source grid
            x, y: Top-left corner of region
            size: Size of region (power of 2)

        Returns:
            HashLifeNode representing this region
        """
        if size == 2:
            # Base case: create a leaf from 2×2 cells
            nw = grid.is_alive(x, y)
            ne = grid.is_alive(x + 1, y)
            sw = grid.is_alive(x, y + 1)
            se = grid.is_alive(x + 1, y + 1)
            return self.create_leaf(nw, ne, sw, se)

        # Recursive case: build four children
        half = size // 2
        nw = self._build_tree_from_grid(grid, x, y, half)
        ne = self._build_tree_from_grid(grid, x + half, y, half)
        sw = self._build_tree_from_grid(grid, x, y + half, half)
        se = self._build_tree_from_grid(grid, x + half, y + half, half)

        return self.create_node(nw, ne, sw, se)

    def to_grid(self) -> Grid:
        """
        Convert the current Hashlife state back to a Grid.

        Returns:
            Grid object with the same pattern
        """
        if self.root is None:
            return Grid(width=0, height=0, live_cells=[])

        size = 1 << self.root.level
        live_cells = []
        self._extract_live_cells(self.root, 0, 0, live_cells)

        return Grid(width=size, height=size, live_cells=live_cells)

    def _extract_live_cells(self, node: HashLifeNode, x: int, y: int,
                           live_cells: list):
        """
        Recursively extract live cells from a node.

        Args:
            node: Current node
            x, y: Top-left corner of this node
            live_cells: List to append live cells to
        """
        if node.population == 0:
            return  # Optimization: skip empty nodes

        if node.is_leaf():
            # Extract cells from leaf
            if node.nw:
                live_cells.append((x, y))
            if node.ne:
                live_cells.append((x + 1, y))
            if node.sw:
                live_cells.append((x, y + 1))
            if node.se:
                live_cells.append((x + 1, y + 1))
            return

        # Recurse into children
        half = 1 << (node.level - 1)
        self._extract_live_cells(node.nw, x, y, live_cells)
        self._extract_live_cells(node.ne, x + half, y, live_cells)
        self._extract_live_cells(node.sw, x, y + half, live_cells)
        self._extract_live_cells(node.se, x + half, y + half, live_cells)

    def step(self, num_steps: int = 1):
        """
        Evolve the pattern by num_steps generations.

        Hashlife works most efficiently when num_steps is a power of 2.

        Args:
            num_steps: Number of generations to evolve
        """
        if self.root is None:
            return

        while num_steps > 0:
            # Ensure we have enough padding for expansion
            self.root = self._expand(self.root)

            # Compute the maximum step size we can take
            max_step = 1 << (self.root.level - 2)

            if num_steps >= max_step:
                # Take one full exponential step
                self.root = self._compute_result(self.root)
                num_steps -= max_step
            else:
                # Need smaller steps - compute iteratively
                # (less efficient, but handles arbitrary step counts)
                self.root = self._slow_step(self.root, num_steps)
                num_steps = 0

    def _expand(self, node: HashLifeNode) -> HashLifeNode:
        """
        Expand the universe by adding empty border around the node.

        This ensures patterns can grow beyond current boundaries.
        """
        # Create an empty node of the same level
        empty = self._empty_tree(node.level - 1)

        # Build a new node with the old node in center
        nw = self.create_node(empty, empty, empty, node.nw)
        ne = self.create_node(empty, empty, node.ne, empty)
        sw = self.create_node(empty, node.sw, empty, empty)
        se = self.create_node(node.se, empty, empty, empty)

        return self.create_node(nw, ne, sw, se)

    def _empty_tree(self, level: int) -> HashLifeNode:
        """
        Create an empty (all-dead) node at the given level.

        Args:
            level: Level of the node

        Returns:
            Empty node
        """
        if level == 1:
            return self.create_leaf(False, False, False, False)

        # Recursively create empty children
        child = self._empty_tree(level - 1)
        return self.create_node(child, child, child, child)

    def _compute_result(self, node: HashLifeNode) -> HashLifeNode:
        """
        Compute the future state of a node.

        For a level-n node, this returns the center 2^(n-1) × 2^(n-1) region
        after 2^(n-2) timesteps.

        This is the core of the Hashlife algorithm and uses memoization.

        Args:
            node: Node to compute future for

        Returns:
            Future state node
        """
        # Check cache first
        if node in self.result_cache:
            return self.result_cache[node]

        if node.level == 2:
            # Base case: level-2 node (4×4 cells)
            # Compute center 2×2 after 1 step using Conway's rules
            result = self._compute_level2_result(node)
        else:
            # Recursive case: use children's results

            # Get results of the 9 overlapping subregions
            nw = self._compute_result(node.nw)
            ne = self._compute_result(node.ne)
            sw = self._compute_result(node.sw)
            se = self._compute_result(node.se)

            # Get results of edge subregions
            n = self._compute_result(self._horizontal_centered(node.nw, node.ne))
            w = self._compute_result(self._vertical_centered(node.nw, node.sw))
            c = self._compute_result(self._centered(node))
            e = self._compute_result(self._vertical_centered(node.ne, node.se))
            s = self._compute_result(self._horizontal_centered(node.sw, node.se))

            # Combine results
            result = self.create_node(
                self.create_node(nw.se, n.sw, w.ne, c.nw),
                self.create_node(n.se, ne.sw, c.ne, e.nw),
                self.create_node(w.se, c.sw, sw.ne, s.nw),
                self.create_node(c.se, e.sw, s.ne, se.nw)
            )

        # Cache and return
        self.result_cache[node] = result
        return result

    def _compute_level2_result(self, node: HashLifeNode) -> HashLifeNode:
        """
        Compute the future of a level-2 (4×4) node.

        Returns the center 2×2 region after 1 generation.

        This is done by examining the 3×3 neighborhood of each center cell
        and applying Conway's rules.
        """
        # Extract all 16 cells from the 4×4 region
        nw, ne, sw, se = node.nw, node.ne, node.sw, node.se
        cells = [
            [nw.nw, nw.ne, ne.nw, ne.ne],
            [nw.sw, nw.se, ne.sw, ne.se],
            [sw.nw, sw.ne, se.nw, se.ne],
            [sw.sw, sw.se, se.sw, se.se]
        ]

        # Compute the next state of the center 2×2
        result_nw = self._life_rule(cells, 1, 1)
        result_ne = self._life_rule(cells, 2, 1)
        result_sw = self._life_rule(cells, 1, 2)
        result_se = self._life_rule(cells, 2, 2)

        return self.create_leaf(result_nw, result_ne, result_sw, result_se)

    def _life_rule(self, cells: list, x: int, y: int) -> bool:
        """
        Apply Conway's Life rules to a cell.

        Args:
            cells: 4×4 array of cell states
            x, y: Coordinates of cell to update (center 2×2)

        Returns:
            New state of the cell
        """
        # Count live neighbors in 3×3 neighborhood
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                if cells[y + dy][x + dx]:
                    count += 1

        current = cells[y][x]
        return self.rules.should_be_alive(current, count)

    def _horizontal_centered(self, w, e) -> HashLifeNode:
        """Create a node centered horizontally between two nodes."""
        return self.create_node(w.ne, e.nw, w.se, e.sw)

    def _vertical_centered(self, n, s) -> HashLifeNode:
        """Create a node centered vertically between two nodes."""
        return self.create_node(n.sw, n.se, s.nw, s.ne)

    def _centered(self, node: HashLifeNode) -> HashLifeNode:
        """Extract the center of a node."""
        return self.create_node(
            node.nw.se, node.ne.sw,
            node.sw.ne, node.se.nw
        )

    def _slow_step(self, node: HashLifeNode, steps: int) -> HashLifeNode:
        """
        Compute multiple steps iteratively (fallback for non-power-of-2).

        This is less efficient than exponential stepping but handles
        arbitrary step counts.
        """
        current = node
        for _ in range(steps):
            current = self._compute_result(current)
        return current
