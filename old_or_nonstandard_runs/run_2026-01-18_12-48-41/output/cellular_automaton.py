"""
Cellular Automaton Engine

A flexible cellular automaton implementation supporting Conway's Game of Life
and custom rule sets.

This module provides:
- Grid: Manages the cellular automaton state
- Rules: Base class for rule definitions
- ConwayRules: Classic Game of Life rules (B3/S23)

Example:
    >>> from cellular_automaton import Grid, ConwayRules
    >>> glider = {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    >>> grid = Grid(width=10, height=10, live_cells=glider)
    >>> rules = ConwayRules()
    >>> next_gen = grid.step(rules)
"""

from typing import Set, Tuple, List


class Rules:
    """
    Defines birth and survival rules for cellular automata.

    Uses standard B/S notation:
    - Birth: List of neighbor counts that cause a dead cell to become alive
    - Survival: List of neighbor counts that keep a live cell alive

    Example:
        Conway's Game of Life is B3/S23:
        >>> rules = Rules(birth=[3], survival=[2, 3])
    """

    def __init__(self, birth: List[int], survival: List[int]):
        """
        Initialize rules with birth and survival conditions.

        Args:
            birth: List of neighbor counts that cause birth
            survival: List of neighbor counts that allow survival
        """
        self.birth = set(birth)
        self.survival = set(survival)

    def should_be_alive(self, currently_alive: bool, neighbor_count: int) -> bool:
        """
        Determine if a cell should be alive in the next generation.

        Args:
            currently_alive: Whether the cell is currently alive
            neighbor_count: Number of live neighbors

        Returns:
            True if the cell should be alive in the next generation
        """
        if currently_alive:
            return neighbor_count in self.survival
        else:
            return neighbor_count in self.birth


class ConwayRules(Rules):
    """
    Classic Conway's Game of Life rules (B3/S23).

    - Birth: A dead cell with exactly 3 neighbors becomes alive
    - Survival: A live cell with 2 or 3 neighbors stays alive
    - Death: All other cells die or stay dead
    """

    def __init__(self):
        """Initialize with Conway's classic B3/S23 rules."""
        super().__init__(birth=[3], survival=[2, 3])


class Grid:
    """
    Represents the state of a cellular automaton grid.

    The grid uses a finite boundary (no wrapping). Cells are indexed as (x, y)
    where (0, 0) is the top-left corner.

    Internally uses a set of live cell coordinates for efficient sparse representation.
    """

    def __init__(self, width: int, height: int, live_cells: Set[Tuple[int, int]] = None):
        """
        Initialize a grid with specified dimensions and optional live cells.

        Args:
            width: Grid width
            height: Grid height
            live_cells: Set of (x, y) coordinates for initially alive cells
        """
        self.width = width
        self.height = height
        self._live_cells = set(live_cells) if live_cells else set()

        # Validate that all live cells are within bounds
        for x, y in self._live_cells:
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"Cell ({x}, {y}) is out of bounds for {width}x{height} grid")

    def is_alive(self, x: int, y: int) -> bool:
        """
        Check if a cell is alive.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if the cell is alive, False otherwise
        """
        return (x, y) in self._live_cells

    def set_cell(self, x: int, y: int, alive: bool) -> None:
        """
        Set the state of a cell.

        Args:
            x: X coordinate
            y: Y coordinate
            alive: True to make the cell alive, False to kill it
        """
        if alive:
            self._live_cells.add((x, y))
        else:
            self._live_cells.discard((x, y))

    def count_live_cells(self) -> int:
        """
        Count the total number of live cells.

        Returns:
            Number of live cells in the grid
        """
        return len(self._live_cells)

    def get_live_cells(self) -> Set[Tuple[int, int]]:
        """
        Get all live cell coordinates.

        Returns:
            Set of (x, y) tuples representing live cells
        """
        return self._live_cells.copy()

    def count_neighbors(self, x: int, y: int) -> int:
        """
        Count the number of live neighbors for a cell.

        A neighbor is any of the 8 adjacent cells (horizontal, vertical, diagonal).
        Cells outside the grid boundary are not counted.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Number of live neighbors (0-8)
        """
        count = 0

        # Check all 8 adjacent positions
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                # Skip the cell itself
                if dx == 0 and dy == 0:
                    continue

                nx, ny = x + dx, y + dy

                # Check if neighbor is within bounds and alive
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.is_alive(nx, ny):
                        count += 1

        return count

    def step(self, rules: Rules) -> 'Grid':
        """
        Evolve the grid one generation according to the given rules.

        This method:
        1. Examines all live cells and their neighbors
        2. Applies the rules to determine the next generation
        3. Returns a new Grid with the updated state

        Args:
            rules: The rules to apply for this step

        Returns:
            A new Grid representing the next generation
        """
        # To determine next state, we need to check:
        # 1. All currently live cells (might die)
        # 2. All neighbors of live cells (might be born)
        cells_to_check = set()

        # Add all live cells
        cells_to_check.update(self._live_cells)

        # Add all neighbors of live cells
        for x, y in self._live_cells:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        cells_to_check.add((nx, ny))

        # Determine which cells should be alive in the next generation
        next_live_cells = set()

        for x, y in cells_to_check:
            currently_alive = self.is_alive(x, y)
            neighbor_count = self.count_neighbors(x, y)

            if rules.should_be_alive(currently_alive, neighbor_count):
                next_live_cells.add((x, y))

        # Create and return new grid with next generation
        return Grid(width=self.width, height=self.height, live_cells=next_live_cells)

    def __str__(self) -> str:
        """
        Create a string representation of the grid.

        Returns:
            A multi-line string showing the grid with 'O' for live cells and '.' for dead cells
        """
        lines = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append('O' if self.is_alive(x, y) else '.')
            lines.append(''.join(row))
        return '\n'.join(lines)

    def __repr__(self) -> str:
        """Return a detailed representation of the grid."""
        return f"Grid(width={self.width}, height={self.height}, live_cells={len(self._live_cells)})"
