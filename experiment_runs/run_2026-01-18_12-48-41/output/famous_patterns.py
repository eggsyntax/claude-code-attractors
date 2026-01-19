"""
Famous Conway's Game of Life Patterns

A curated collection of historically significant and interesting patterns
from the Game of Life community. Each pattern includes documentation about
its discovery and significance.

Categories:
- Still lifes: Stable patterns that never change
- Oscillators: Patterns that repeat with a period > 1
- Spaceships: Patterns that translate themselves across the grid
- Methuselahs: Small patterns that take many generations to stabilize
- Guns: Patterns that emit spaceships periodically
- Puffers: Patterns that leave debris as they move

Usage:
    from famous_patterns import get_pattern
    from cellular_automaton import Grid, ConwayRules

    cells = get_pattern('gosper_glider_gun')
    grid = Grid(width=40, height=40, live_cells=cells)
"""

from typing import Set, Tuple, Dict


def get_pattern(name: str) -> Set[Tuple[int, int]]:
    """
    Get a famous pattern by name.

    Args:
        name: Pattern name (lowercase, underscores for spaces)

    Returns:
        Set of (x, y) coordinates for live cells

    Raises:
        KeyError: If pattern name is not found
    """
    patterns = {
        'block': block(),
        'beehive': beehive(),
        'loaf': loaf(),
        'boat': boat(),
        'tub': tub(),
        'blinker': blinker(),
        'toad': toad(),
        'beacon': beacon(),
        'pulsar': pulsar(),
        'pentadecathlon': pentadecathlon(),
        'glider': glider(),
        'lwss': lwss(),
        'mwss': mwss(),
        'hwss': hwss(),
        'r_pentomino': r_pentomino(),
        'diehard': diehard(),
        'acorn': acorn(),
        'gosper_glider_gun': gosper_glider_gun(),
        'simkin_glider_gun': simkin_glider_gun(),
        'puffer_train': puffer_train(),
        'switch_engine': switch_engine(),
    }

    if name not in patterns:
        available = ', '.join(sorted(patterns.keys()))
        raise KeyError(f"Pattern '{name}' not found. Available patterns: {available}")

    return patterns[name]


def list_patterns() -> Dict[str, str]:
    """
    Get a dictionary of all available patterns with descriptions.

    Returns:
        Dict mapping pattern names to descriptions
    """
    return {
        # Still lifes (period 1)
        'block': 'Still life: 2x2 square, the simplest still life',
        'beehive': 'Still life: Hexagonal shape, very common',
        'loaf': 'Still life: Asymmetric 4x4 pattern',
        'boat': 'Still life: Small asymmetric pattern',
        'tub': 'Still life: Simple 3x3 pattern',

        # Oscillators (period > 1)
        'blinker': 'Oscillator: Period 2, simplest oscillator',
        'toad': 'Oscillator: Period 2, 6-cell pattern',
        'beacon': 'Oscillator: Period 2, two blocks',
        'pulsar': 'Oscillator: Period 3, large and symmetric',
        'pentadecathlon': 'Oscillator: Period 15, discovered in 1970',

        # Spaceships
        'glider': 'Spaceship: Smallest, moves diagonally at c/4',
        'lwss': 'Spaceship: Lightweight spaceship, orthogonal at c/2',
        'mwss': 'Spaceship: Middleweight spaceship, orthogonal at c/2',
        'hwss': 'Spaceship: Heavyweight spaceship, orthogonal at c/2',

        # Methuselahs
        'r_pentomino': 'Methuselah: Stabilizes after 1103 generations',
        'diehard': 'Methuselah: Dies after 130 generations',
        'acorn': 'Methuselah: Stabilizes after 5206 generations!',

        # Guns and puffers
        'gosper_glider_gun': 'Gun: First discovered gun, period 30',
        'simkin_glider_gun': 'Gun: Smaller than Gosper, period 120',
        'puffer_train': 'Puffer: Leaves debris, moves at c/2',
        'switch_engine': 'Puffer: Grows indefinitely at c/12',
    }


# ============================================================================
# STILL LIFES
# ============================================================================

def block() -> Set[Tuple[int, int]]:
    """Block: The simplest still life, a 2x2 square."""
    return {(0, 0), (1, 0), (0, 1), (1, 1)}


def beehive() -> Set[Tuple[int, int]]:
    """Beehive: Common 6-cell still life."""
    return {(1, 0), (2, 0), (0, 1), (3, 1), (1, 2), (2, 2)}


def loaf() -> Set[Tuple[int, int]]:
    """Loaf: 7-cell still life with asymmetric structure."""
    return {(1, 0), (2, 0), (0, 1), (3, 1), (1, 2), (3, 2), (2, 3)}


def boat() -> Set[Tuple[int, int]]:
    """Boat: Small 5-cell still life."""
    return {(0, 0), (1, 0), (0, 1), (2, 1), (1, 2)}


def tub() -> Set[Tuple[int, int]]:
    """Tub: Simple 4-cell still life."""
    return {(1, 0), (0, 1), (2, 1), (1, 2)}


# ============================================================================
# OSCILLATORS
# ============================================================================

def blinker() -> Set[Tuple[int, int]]:
    """Blinker: Period 2, the simplest and most common oscillator."""
    return {(0, 1), (1, 1), (2, 1)}


def toad() -> Set[Tuple[int, int]]:
    """Toad: Period 2 oscillator, 6 cells."""
    return {(1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1)}


def beacon() -> Set[Tuple[int, int]]:
    """Beacon: Period 2 oscillator formed by two blocks."""
    return {(0, 0), (1, 0), (0, 1), (3, 2), (2, 3), (3, 3)}


def pulsar() -> Set[Tuple[int, int]]:
    """
    Pulsar: Period 3 oscillator, one of the most beautiful patterns.
    Discovered by John Conway in 1970.
    """
    cells = set()

    # The pulsar has 4-fold rotational symmetry
    # Define one quadrant and rotate it
    quadrant = [
        (2, 0), (3, 0), (4, 0),
        (0, 2), (5, 2),
        (0, 3), (5, 3),
        (0, 4), (5, 4),
        (2, 5), (3, 5), (4, 5)
    ]

    # Add all four quadrants with proper offsets
    for x, y in quadrant:
        cells.add((x, y))          # Top-left
        cells.add((12-x, y))       # Top-right
        cells.add((x, 12-y))       # Bottom-left
        cells.add((12-x, 12-y))    # Bottom-right

    return cells


def pentadecathlon() -> Set[Tuple[int, int]]:
    """
    Pentadecathlon: Period 15 oscillator.
    Discovered by John Conway in 1970.
    """
    return {
        (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1),
        (1, 2), (4, 2), (7, 2), (10, 2),
        (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3)
    }


# ============================================================================
# SPACESHIPS
# ============================================================================

def glider() -> Set[Tuple[int, int]]:
    """
    Glider: The smallest, most common, and first discovered spaceship.
    Moves diagonally at speed c/4 with period 4.
    Discovered by Richard K. Guy in 1970.
    """
    return {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}


def lwss() -> Set[Tuple[int, int]]:
    """
    LWSS: Lightweight Spaceship.
    Moves orthogonally at speed c/2 with period 4.
    Smallest orthogonal spaceship.
    """
    return {
        (1, 0), (4, 0),
        (0, 1),
        (0, 2), (4, 2),
        (0, 3), (1, 3), (2, 3), (3, 3)
    }


def mwss() -> Set[Tuple[int, int]]:
    """
    MWSS: Middleweight Spaceship.
    Moves orthogonally at speed c/2 with period 4.
    """
    return {
        (2, 0),
        (0, 1), (4, 1),
        (0, 2), (5, 2),
        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3)
    }


def hwss() -> Set[Tuple[int, int]]:
    """
    HWSS: Heavyweight Spaceship.
    Moves orthogonally at speed c/2 with period 4.
    """
    return {
        (2, 0), (3, 0),
        (0, 1), (5, 1),
        (0, 2), (6, 2),
        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3)
    }


# ============================================================================
# METHUSELAHS
# ============================================================================

def r_pentomino() -> Set[Tuple[int, int]]:
    """
    R-pentomino: Famous methuselah that stabilizes after 1103 generations.
    Final population: 116 cells.
    Discovered by John Conway in 1970.

    Named because it looks like the letter 'R' (if you squint).
    """
    return {(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)}


def diehard() -> Set[Tuple[int, int]]:
    """
    Diehard: Methuselah that dies after exactly 130 generations.
    Discovered by Achim Flammenkamp in 1997.

    One of the longest-lived patterns that eventually dies completely.
    """
    return {
        (6, 0),
        (0, 1), (1, 1),
        (1, 2), (5, 2), (6, 2), (7, 2)
    }


def acorn() -> Set[Tuple[int, int]]:
    """
    Acorn: Spectacular methuselah that stabilizes after 5206 generations.
    Final population: 633 cells.
    Discovered by Charles Corderman in 1970.

    From just 7 cells, it grows into a complex pattern with gliders,
    oscillators, and still lifes.
    """
    return {
        (1, 0),
        (3, 1),
        (0, 2), (1, 2), (4, 2), (5, 2), (6, 2)
    }


# ============================================================================
# GUNS
# ============================================================================

def gosper_glider_gun() -> Set[Tuple[int, int]]:
    """
    Gosper Glider Gun: The first discovered gun pattern.
    Discovered by Bill Gosper in 1970, winning a $50 prize from John Conway.

    Period 30, emits a glider every 30 generations.
    This pattern proved that infinite growth was possible in Life.
    """
    return {
        # Left square
        (0, 4), (1, 4),
        (0, 5), (1, 5),

        # Left component
        (10, 4), (10, 5), (10, 6),
        (11, 3), (11, 7),
        (12, 2), (12, 8),
        (13, 2), (13, 8),
        (14, 5),
        (15, 3), (15, 7),
        (16, 4), (16, 5), (16, 6),
        (17, 5),

        # Right component
        (20, 2), (20, 3), (20, 4),
        (21, 2), (21, 3), (21, 4),
        (22, 1), (22, 5),
        (24, 0), (24, 1), (24, 5), (24, 6),

        # Right square
        (34, 2), (35, 2),
        (34, 3), (35, 3)
    }


def simkin_glider_gun() -> Set[Tuple[int, int]]:
    """
    Simkin Glider Gun: A smaller gun with period 120.
    Discovered by Michael Simkin in 1971.

    More compact than the Gosper gun but with a longer period.
    """
    return {
        # Top-left blocks
        (0, 0), (1, 0),
        (0, 1), (1, 1),

        # Middle structure
        (7, 0), (8, 0),
        (7, 1), (9, 1),
        (7, 2), (8, 2),

        # Bottom structure
        (19, 10), (20, 10),
        (19, 11), (21, 11),
        (19, 12), (20, 12),

        # Right blocks
        (26, 10), (27, 10),
        (26, 11), (27, 11),

        # Stabilizing blocks
        (33, 0), (34, 0),
        (33, 1), (34, 1)
    }


# ============================================================================
# PUFFERS
# ============================================================================

def puffer_train() -> Set[Tuple[int, int]]:
    """
    Puffer Train: A pattern that moves and leaves debris behind.
    Moves at c/2 orthogonally.

    The debris consists of smoke (ash), hence the name "puffer".
    """
    return {
        # Front engine
        (0, 0), (2, 0), (3, 0),
        (4, 1),
        (0, 2), (4, 2),
        (1, 3), (2, 3), (3, 3), (4, 3),

        # Spacer
        (8, 1), (8, 2),

        # Rear engine
        (12, 0), (14, 0), (15, 0),
        (16, 1),
        (12, 2), (16, 2),
        (13, 3), (14, 3), (15, 3), (16, 3)
    }


def switch_engine() -> Set[Tuple[int, int]]:
    """
    Switch Engine: An infinitely growing pattern.
    Discovered by Charles Corderman in 1971.

    Creates gliders and grows indefinitely in a chaotic manner.
    One of the smallest infinite growth patterns.
    """
    return {
        (0, 0), (1, 0), (2, 0),
        (0, 1), (2, 1),
        (2, 2),
        (1, 3)
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def center_pattern(pattern: Set[Tuple[int, int]], width: int, height: int) -> Set[Tuple[int, int]]:
    """
    Center a pattern in a grid of given dimensions.

    Args:
        pattern: Set of (x, y) coordinates
        width: Target grid width
        height: Target grid height

    Returns:
        New pattern centered in the grid
    """
    if not pattern:
        return pattern

    # Find pattern bounds
    min_x = min(x for x, y in pattern)
    max_x = max(x for x, y in pattern)
    min_y = min(y for x, y in pattern)
    max_y = max(y for x, y in pattern)

    # Calculate pattern dimensions
    pattern_width = max_x - min_x + 1
    pattern_height = max_y - min_y + 1

    # Calculate offset to center
    offset_x = (width - pattern_width) // 2 - min_x
    offset_y = (height - pattern_height) // 2 - min_y

    # Apply offset
    return {(x + offset_x, y + offset_y) for x, y in pattern}


def print_pattern_catalog():
    """Print a formatted catalog of all available patterns."""
    patterns = list_patterns()

    print("=" * 70)
    print("Conway's Game of Life - Famous Patterns Catalog")
    print("=" * 70)
    print()

    categories = {
        'Still Lifes': ['block', 'beehive', 'loaf', 'boat', 'tub'],
        'Oscillators': ['blinker', 'toad', 'beacon', 'pulsar', 'pentadecathlon'],
        'Spaceships': ['glider', 'lwss', 'mwss', 'hwss'],
        'Methuselahs': ['r_pentomino', 'diehard', 'acorn'],
        'Guns': ['gosper_glider_gun', 'simkin_glider_gun'],
        'Puffers': ['puffer_train', 'switch_engine']
    }

    for category, pattern_names in categories.items():
        print(f"\n{category}:")
        print("-" * 70)
        for name in pattern_names:
            print(f"  {name:25s} - {patterns[name]}")

    print("\n" + "=" * 70)
    print(f"Total patterns: {len(patterns)}")
    print("=" * 70)


if __name__ == '__main__':
    # Print the catalog when run directly
    print_pattern_catalog()
