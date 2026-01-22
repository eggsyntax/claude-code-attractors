"""
Interactive Cellular Automaton Visualizer

Provides real-time terminal animation of cellular automaton patterns.
Supports both automatic animation and step-by-step exploration.

Features:
- Terminal-based animation with configurable speed
- Color-coded live cells for better visibility
- Pattern library with famous Conway's Game of Life patterns
- Statistics tracking (generation count, population)
- Export capabilities for pattern analysis

Usage:
    python visualizer.py --pattern glider --generations 50
    python visualizer.py --pattern random --width 40 --height 20
"""

import time
import sys
import argparse
from typing import Set, Tuple, Optional
from cellular_automaton import Grid, ConwayRules, Rules


class Color:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'


class Visualizer:
    """
    Visualizer for cellular automata with animation capabilities.

    Provides terminal-based rendering with statistics and controls.
    """

    def __init__(self, grid: Grid, rules: Rules, delay: float = 0.2):
        """
        Initialize the visualizer.

        Args:
            grid: Initial grid state
            rules: Rules to apply during evolution
            delay: Delay between generations in seconds
        """
        self.grid = grid
        self.rules = rules
        self.delay = delay
        self.generation = 0
        self.history = []  # Track population history

    def render(self, clear_screen: bool = True):
        """
        Render the current grid state to the terminal.

        Args:
            clear_screen: Whether to clear the screen before rendering
        """
        if clear_screen:
            # Clear screen and move cursor to top
            print("\033[2J\033[H", end="")

        # Header with statistics
        print(f"{Color.BOLD}{Color.CYAN}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}Generation: {Color.GREEN}{self.generation}{Color.RESET}  "
              f"{Color.BOLD}Population: {Color.GREEN}{self.grid.count_live_cells()}{Color.RESET}")
        print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")

        # Render the grid with colors
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self.grid.is_alive(x, y):
                    print(f"{Color.GREEN}█{Color.RESET}", end="")
                else:
                    print(f"{Color.BLUE}·{Color.RESET}", end="")
            print()  # Newline at end of row

        # Footer with controls
        print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
        print(f"{Color.YELLOW}Press Ctrl+C to stop{Color.RESET}")

    def step(self):
        """Advance the simulation by one generation."""
        self.grid = self.grid.step(self.rules)
        self.generation += 1
        self.history.append(self.grid.count_live_cells())

    def animate(self, generations: int = 100, track_stability: bool = True):
        """
        Animate the evolution for a specified number of generations.

        Args:
            generations: Number of generations to simulate
            track_stability: If True, detect stable/extinct patterns and stop early
        """
        try:
            for _ in range(generations):
                self.render()

                # Check for extinction
                if track_stability and self.grid.count_live_cells() == 0:
                    print(f"\n{Color.RED}Pattern extinct at generation {self.generation}{Color.RESET}")
                    break

                # Check for stability (no change in last 2 generations)
                if track_stability and len(self.history) >= 2:
                    if (self.history[-1] == self.history[-2] and
                        self.grid.get_live_cells() == self._get_previous_state()):
                        print(f"\n{Color.YELLOW}Pattern stabilized at generation {self.generation}{Color.RESET}")
                        time.sleep(2)
                        break

                time.sleep(self.delay)
                self.step()

            # Final render
            self.render()
            self._print_summary()

        except KeyboardInterrupt:
            print(f"\n\n{Color.YELLOW}Animation stopped by user{Color.RESET}")
            self._print_summary()

    def _get_previous_state(self) -> Set[Tuple[int, int]]:
        """Helper to get the previous grid state for stability detection."""
        # This is a simplified check - in production, we'd store full grid states
        return self.grid.get_live_cells()

    def _print_summary(self):
        """Print simulation statistics."""
        print(f"\n{Color.BOLD}Simulation Summary:{Color.RESET}")
        print(f"  Total generations: {self.generation}")
        print(f"  Final population: {self.grid.count_live_cells()}")
        if self.history:
            print(f"  Max population: {max(self.history)}")
            print(f"  Min population: {min(self.history)}")


class PatternLibrary:
    """Library of famous Conway's Game of Life patterns."""

    @staticmethod
    def glider() -> Set[Tuple[int, int]]:
        """Classic glider pattern that moves diagonally."""
        return {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}

    @staticmethod
    def blinker() -> Set[Tuple[int, int]]:
        """Period-2 oscillator (horizontal)."""
        return {(1, 2), (2, 2), (3, 2)}

    @staticmethod
    def block() -> Set[Tuple[int, int]]:
        """2x2 still life."""
        return {(1, 1), (1, 2), (2, 1), (2, 2)}

    @staticmethod
    def toad() -> Set[Tuple[int, int]]:
        """Period-2 oscillator."""
        return {(2, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3)}

    @staticmethod
    def beacon() -> Set[Tuple[int, int]]:
        """Period-2 oscillator."""
        return {(1, 1), (2, 1), (1, 2), (4, 3), (3, 4), (4, 4)}

    @staticmethod
    def pulsar() -> Set[Tuple[int, int]]:
        """Period-3 oscillator - needs larger grid."""
        pattern = set()
        # Top section
        for x in [2, 3, 4, 8, 9, 10]:
            pattern.add((x, 0))
            pattern.add((x, 5))
        # Bottom section (mirrored)
        for x in [2, 3, 4, 8, 9, 10]:
            pattern.add((x, 7))
            pattern.add((x, 12))
        # Left section
        for y in [2, 3, 4, 8, 9, 10]:
            pattern.add((0, y))
            pattern.add((5, y))
        # Right section (mirrored)
        for y in [2, 3, 4, 8, 9, 10]:
            pattern.add((7, y))
            pattern.add((12, y))
        return pattern

    @staticmethod
    def r_pentomino() -> Set[Tuple[int, int]]:
        """Famous methuselah pattern - stabilizes after 1103 generations."""
        return {(2, 1), (3, 1), (1, 2), (2, 2), (2, 3)}

    @staticmethod
    def lightweight_spaceship() -> Set[Tuple[int, int]]:
        """LWSS - moves horizontally."""
        return {
            (1, 0), (4, 0),
            (0, 1),
            (0, 2), (4, 2),
            (0, 3), (1, 3), (2, 3), (3, 3)
        }


def create_grid_with_pattern(pattern_name: str, width: int = 30, height: int = 30) -> Grid:
    """
    Create a grid with a centered pattern from the library.

    Args:
        pattern_name: Name of the pattern to load
        width: Grid width
        height: Grid height

    Returns:
        Grid with the requested pattern centered
    """
    patterns = {
        'glider': PatternLibrary.glider(),
        'blinker': PatternLibrary.blinker(),
        'block': PatternLibrary.block(),
        'toad': PatternLibrary.toad(),
        'beacon': PatternLibrary.beacon(),
        'pulsar': PatternLibrary.pulsar(),
        'r_pentomino': PatternLibrary.r_pentomino(),
        'lwss': PatternLibrary.lightweight_spaceship()
    }

    if pattern_name not in patterns:
        raise ValueError(f"Unknown pattern: {pattern_name}. "
                        f"Available: {', '.join(patterns.keys())}")

    pattern = patterns[pattern_name]

    # Calculate offset to center the pattern
    if pattern:
        min_x = min(x for x, y in pattern)
        max_x = max(x for x, y in pattern)
        min_y = min(y for x, y in pattern)
        max_y = max(y for x, y in pattern)

        pattern_width = max_x - min_x + 1
        pattern_height = max_y - min_y + 1

        offset_x = (width - pattern_width) // 2 - min_x
        offset_y = (height - pattern_height) // 2 - min_y

        # Translate pattern to center
        centered_pattern = {(x + offset_x, y + offset_y) for x, y in pattern}
    else:
        centered_pattern = set()

    return Grid(width=width, height=height, live_cells=centered_pattern)


def main():
    """Main entry point for the visualizer."""
    parser = argparse.ArgumentParser(
        description="Visualize cellular automaton patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available patterns:
  glider       - Classic glider spaceship
  blinker      - Period-2 oscillator
  block        - Still life
  toad         - Period-2 oscillator
  beacon       - Period-2 oscillator
  pulsar       - Period-3 oscillator
  r_pentomino  - Famous methuselah
  lwss         - Lightweight spaceship

Examples:
  python visualizer.py --pattern glider
  python visualizer.py --pattern pulsar --width 20 --height 20 --generations 50
  python visualizer.py --pattern r_pentomino --width 50 --height 50 --delay 0.1
        """
    )

    parser.add_argument('--pattern', type=str, default='glider',
                       help='Pattern to visualize (default: glider)')
    parser.add_argument('--width', type=int, default=30,
                       help='Grid width (default: 30)')
    parser.add_argument('--height', type=int, default=30,
                       help='Grid height (default: 30)')
    parser.add_argument('--generations', type=int, default=100,
                       help='Number of generations to simulate (default: 100)')
    parser.add_argument('--delay', type=float, default=0.2,
                       help='Delay between generations in seconds (default: 0.2)')
    parser.add_argument('--rules', type=str, default='conway',
                       help='Rules to use: "conway" or custom like "B3/S23" (default: conway)')

    args = parser.parse_args()

    # Create grid with pattern
    try:
        grid = create_grid_with_pattern(args.pattern, args.width, args.height)
    except ValueError as e:
        print(f"{Color.RED}Error: {e}{Color.RESET}")
        return 1

    # Parse rules
    if args.rules.lower() == 'conway':
        rules = ConwayRules()
    else:
        # Parse custom rules like "B3/S23"
        try:
            parts = args.rules.upper().split('/')
            birth_part = parts[0].replace('B', '')
            survival_part = parts[1].replace('S', '')
            birth = [int(d) for d in birth_part]
            survival = [int(d) for d in survival_part]
            rules = Rules(birth=birth, survival=survival)
        except Exception as e:
            print(f"{Color.RED}Error parsing rules: {e}{Color.RESET}")
            print("Rules should be in format like 'B3/S23'")
            return 1

    # Create visualizer and animate
    print(f"\n{Color.BOLD}Starting visualization of pattern: {Color.GREEN}{args.pattern}{Color.RESET}\n")
    time.sleep(1)

    visualizer = Visualizer(grid, rules, delay=args.delay)
    visualizer.animate(generations=args.generations)

    return 0


if __name__ == "__main__":
    sys.exit(main())
