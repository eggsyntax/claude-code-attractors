"""
Pattern Explorer for Cellular Automata

Tools for analyzing and discovering interesting patterns in cellular automata.
Helps identify oscillators, spaceships, still lifes, and chaotic patterns.

Features:
- Pattern classification (still life, oscillator, spaceship, etc.)
- Period detection for oscillators
- Velocity calculation for spaceships
- Chaos metrics and entropy analysis
- Random pattern generation and screening

Usage:
    from pattern_explorer import PatternAnalyzer
    analyzer = PatternAnalyzer(grid, rules)
    result = analyzer.analyze(max_generations=100)
"""

import random
from typing import Set, Tuple, Optional, List, Dict
from dataclasses import dataclass
from cellular_automaton import Grid, Rules, ConwayRules


@dataclass
class AnalysisResult:
    """
    Results from pattern analysis.

    Attributes:
        pattern_type: Classification (still_life, oscillator, spaceship, extinct, chaotic)
        period: Period for oscillators (None if not periodic)
        velocity: (dx, dy) per generation for spaceships (None if not a spaceship)
        stabilization_time: Generations until pattern stabilized
        max_population: Maximum population reached
        final_population: Final population count
        population_history: List of population counts per generation
    """
    pattern_type: str
    period: Optional[int] = None
    velocity: Optional[Tuple[float, float]] = None
    stabilization_time: Optional[int] = None
    max_population: int = 0
    final_population: int = 0
    population_history: List[int] = None

    def __str__(self) -> str:
        """Create a human-readable summary."""
        lines = [f"Pattern Type: {self.pattern_type.upper()}"]

        if self.period:
            lines.append(f"Period: {self.period}")

        if self.velocity:
            lines.append(f"Velocity: ({self.velocity[0]:.2f}, {self.velocity[1]:.2f}) cells/gen")

        if self.stabilization_time is not None:
            lines.append(f"Stabilization Time: {self.stabilization_time} generations")

        lines.append(f"Max Population: {self.max_population}")
        lines.append(f"Final Population: {self.final_population}")

        return "\n".join(lines)


class PatternAnalyzer:
    """
    Analyzes cellular automaton patterns to identify their behavior.

    Can detect still lifes, oscillators, spaceships, and chaotic patterns.
    """

    def __init__(self, grid: Grid, rules: Rules):
        """
        Initialize the analyzer.

        Args:
            grid: Initial grid state
            rules: Rules to apply during evolution
        """
        self.initial_grid = grid
        self.rules = rules

    def analyze(self, max_generations: int = 200) -> AnalysisResult:
        """
        Analyze a pattern to determine its behavior.

        Args:
            max_generations: Maximum generations to simulate

        Returns:
            AnalysisResult with pattern classification and statistics
        """
        grid = self.initial_grid
        population_history = [grid.count_live_cells()]
        state_history = [grid.get_live_cells()]

        for gen in range(1, max_generations + 1):
            grid = grid.step(self.rules)
            current_cells = grid.get_live_cells()
            population = len(current_cells)

            population_history.append(population)
            state_history.append(current_cells)

            # Check for extinction
            if population == 0:
                return AnalysisResult(
                    pattern_type="extinct",
                    stabilization_time=gen,
                    max_population=max(population_history),
                    final_population=0,
                    population_history=population_history
                )

            # Check for still life (no change)
            if current_cells == state_history[-2]:
                return AnalysisResult(
                    pattern_type="still_life",
                    period=1,
                    stabilization_time=gen - 1,
                    max_population=max(population_history),
                    final_population=population,
                    population_history=population_history
                )

            # Check for oscillator (repeating pattern)
            period = self._detect_period(state_history, max_period=50)
            if period and period > 1:
                return AnalysisResult(
                    pattern_type="oscillator",
                    period=period,
                    stabilization_time=gen - period,
                    max_population=max(population_history),
                    final_population=population,
                    population_history=population_history
                )

            # Check for spaceship (translated pattern)
            spaceship_result = self._detect_spaceship(state_history, gen)
            if spaceship_result:
                period, velocity = spaceship_result
                return AnalysisResult(
                    pattern_type="spaceship",
                    period=period,
                    velocity=velocity,
                    stabilization_time=gen - period,
                    max_population=max(population_history),
                    final_population=population,
                    population_history=population_history
                )

        # If we got here, pattern is still evolving (chaotic or slow-moving)
        return AnalysisResult(
            pattern_type="chaotic",
            max_population=max(population_history),
            final_population=population_history[-1],
            population_history=population_history
        )

    def _detect_period(self, state_history: List[Set[Tuple[int, int]]],
                       max_period: int = 50) -> Optional[int]:
        """
        Detect if the pattern is periodic.

        Args:
            state_history: List of grid states
            max_period: Maximum period to check

        Returns:
            Period if detected, None otherwise
        """
        if len(state_history) < 4:
            return None

        current_state = state_history[-1]

        # Check for periods from 2 to max_period
        for period in range(2, min(max_period, len(state_history) // 2) + 1):
            if (len(state_history) >= period * 2 and
                current_state == state_history[-1 - period]):
                # Verify period is consistent
                if (len(state_history) >= period * 3 and
                    current_state == state_history[-1 - period * 2]):
                    return period

        return None

    def _detect_spaceship(self, state_history: List[Set[Tuple[int, int]]],
                          current_gen: int) -> Optional[Tuple[int, Tuple[float, float]]]:
        """
        Detect if the pattern is a spaceship (moving pattern).

        Args:
            state_history: List of grid states
            current_gen: Current generation number

        Returns:
            Tuple of (period, (velocity_x, velocity_y)) if spaceship, None otherwise
        """
        if len(state_history) < 10:
            return None

        current_state = state_history[-1]

        # Check for translated versions with different periods
        for period in range(2, min(30, len(state_history) // 2) + 1):
            if len(state_history) < period * 2:
                continue

            past_state = state_history[-1 - period]

            # Calculate translation vector
            if not current_state or not past_state:
                continue

            # Find center of mass for both states
            current_com = self._center_of_mass(current_state)
            past_com = self._center_of_mass(past_state)

            dx = current_com[0] - past_com[0]
            dy = current_com[1] - past_com[1]

            # Check if translating the past state gives us the current state
            translated = {(x + dx, y + dy) for x, y in past_state}

            if translated == current_state:
                # Verify with one more period back if possible
                if len(state_history) >= period * 3:
                    older_state = state_history[-1 - period * 2]
                    older_com = self._center_of_mass(older_state)
                    expected_dx = past_com[0] - older_com[0]
                    expected_dy = past_com[1] - older_com[1]

                    if abs(dx - expected_dx) < 0.1 and abs(dy - expected_dy) < 0.1:
                        velocity = (dx / period, dy / period)
                        return (period, velocity)

        return None

    def _center_of_mass(self, cells: Set[Tuple[int, int]]) -> Tuple[float, float]:
        """
        Calculate the center of mass for a set of cells.

        Args:
            cells: Set of live cell coordinates

        Returns:
            (x, y) center of mass
        """
        if not cells:
            return (0.0, 0.0)

        total_x = sum(x for x, y in cells)
        total_y = sum(y for x, y in cells)
        count = len(cells)

        return (total_x / count, total_y / count)


class RandomPatternGenerator:
    """
    Generates random patterns for exploration and screening.

    Useful for discovering new interesting patterns.
    """

    @staticmethod
    def generate_random(width: int, height: int, density: float = 0.3) -> Grid:
        """
        Generate a random grid with specified density.

        Args:
            width: Grid width
            height: Grid height
            density: Proportion of cells that should be alive (0.0 to 1.0)

        Returns:
            Grid with random pattern
        """
        live_cells = set()

        for x in range(width):
            for y in range(height):
                if random.random() < density:
                    live_cells.add((x, y))

        return Grid(width=width, height=height, live_cells=live_cells)

    @staticmethod
    def generate_symmetrical(width: int, height: int, density: float = 0.3,
                           symmetry: str = 'horizontal') -> Grid:
        """
        Generate a random pattern with symmetry.

        Args:
            width: Grid width
            height: Grid height
            density: Proportion of cells that should be alive
            symmetry: Type of symmetry ('horizontal', 'vertical', 'both', 'rotational')

        Returns:
            Grid with symmetrical random pattern
        """
        live_cells = set()

        if symmetry in ['horizontal', 'both']:
            # Generate for half the height
            for x in range(width):
                for y in range(height // 2):
                    if random.random() < density:
                        live_cells.add((x, y))
                        live_cells.add((x, height - 1 - y))

        if symmetry in ['vertical', 'both']:
            # Generate for half the width
            for x in range(width // 2):
                for y in range(height):
                    if random.random() < density:
                        live_cells.add((x, y))
                        live_cells.add((width - 1 - x, y))

        if symmetry == 'rotational':
            # 4-fold rotational symmetry
            center_x, center_y = width // 2, height // 2
            for x in range(width // 2):
                for y in range(height // 2):
                    if random.random() < density:
                        # Add all 4 rotational positions
                        live_cells.add((center_x + x, center_y + y))
                        live_cells.add((center_x - x, center_y + y))
                        live_cells.add((center_x + x, center_y - y))
                        live_cells.add((center_x - x, center_y - y))

        return Grid(width=width, height=height, live_cells=live_cells)


def batch_screen_patterns(num_patterns: int = 100, width: int = 20, height: int = 20,
                          density: float = 0.3) -> Dict[str, List[AnalysisResult]]:
    """
    Screen many random patterns to find interesting behaviors.

    Args:
        num_patterns: Number of random patterns to test
        width: Grid width
        height: Grid height
        density: Density of random patterns

    Returns:
        Dictionary mapping pattern types to lists of results
    """
    results_by_type = {
        'oscillator': [],
        'spaceship': [],
        'still_life': [],
        'chaotic': [],
        'extinct': []
    }

    rules = ConwayRules()

    print(f"Screening {num_patterns} random patterns...")

    for i in range(num_patterns):
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{num_patterns}")

        # Generate random pattern
        grid = RandomPatternGenerator.generate_random(width, height, density)

        # Analyze it
        analyzer = PatternAnalyzer(grid, rules)
        result = analyzer.analyze(max_generations=100)

        # Store result
        results_by_type[result.pattern_type].append(result)

    # Print summary
    print("\nScreening Results:")
    print("=" * 50)
    for pattern_type, results in results_by_type.items():
        print(f"{pattern_type.capitalize()}: {len(results)}")

        if pattern_type == 'oscillator' and results:
            periods = [r.period for r in results]
            print(f"  Periods found: {sorted(set(periods))}")

        if pattern_type == 'spaceship' and results:
            print(f"  {len(results)} spaceships discovered!")

    return results_by_type


if __name__ == "__main__":
    # Demo: Analyze some known patterns
    from cellular_automaton import Grid, ConwayRules

    print("Pattern Explorer Demo")
    print("=" * 60)

    # Test 1: Blinker (oscillator)
    print("\n1. Analyzing Blinker (should be period-2 oscillator):")
    live_cells = {(1, 2), (2, 2), (3, 2)}
    grid = Grid(width=5, height=5, live_cells=live_cells)
    analyzer = PatternAnalyzer(grid, ConwayRules())
    result = analyzer.analyze()
    print(result)

    # Test 2: Glider (spaceship)
    print("\n2. Analyzing Glider (should be spaceship):")
    live_cells = {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    grid = Grid(width=20, height=20, live_cells=live_cells)
    analyzer = PatternAnalyzer(grid, ConwayRules())
    result = analyzer.analyze()
    print(result)

    # Test 3: Block (still life)
    print("\n3. Analyzing Block (should be still life):")
    live_cells = {(1, 1), (1, 2), (2, 1), (2, 2)}
    grid = Grid(width=5, height=5, live_cells=live_cells)
    analyzer = PatternAnalyzer(grid, ConwayRules())
    result = analyzer.analyze()
    print(result)

    # Test 4: Random screening
    print("\n4. Screening random patterns:")
    print("=" * 60)
    batch_screen_patterns(num_patterns=50, width=15, height=15, density=0.35)
