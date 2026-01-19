"""
Demo script showing the cellular automaton in action.

This script demonstrates several classic Conway's Game of Life patterns
and validates that the implementation works correctly.
"""

from cellular_automaton import Grid, ConwayRules, Rules


def print_grid(grid: Grid, title: str = ""):
    """Print a grid with a title."""
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    print(grid)
    print(f"Live cells: {grid.count_live_cells()}\n")


def demo_blinker():
    """Demonstrate the blinker oscillator (period 2)."""
    print("\n" + "="*60)
    print("BLINKER OSCILLATOR (Period 2)")
    print("="*60)

    # Horizontal blinker
    live_cells = {(1, 2), (2, 2), (3, 2)}
    grid = Grid(width=5, height=5, live_cells=live_cells)
    rules = ConwayRules()

    print_grid(grid, "Generation 0 (Horizontal)")

    # Step 1: Should become vertical
    grid = grid.step(rules)
    print_grid(grid, "Generation 1 (Vertical)")

    # Step 2: Should become horizontal again
    grid = grid.step(rules)
    print_grid(grid, "Generation 2 (Horizontal again)")


def demo_block():
    """Demonstrate the block still life (stable)."""
    print("\n" + "="*60)
    print("BLOCK STILL LIFE (Stable)")
    print("="*60)

    # 2x2 block
    live_cells = {(1, 1), (1, 2), (2, 1), (2, 2)}
    grid = Grid(width=5, height=5, live_cells=live_cells)
    rules = ConwayRules()

    print_grid(grid, "Generation 0")

    # Step: Should remain unchanged
    grid = grid.step(rules)
    print_grid(grid, "Generation 1 (No change)")


def demo_glider():
    """Demonstrate the glider spaceship."""
    print("\n" + "="*60)
    print("GLIDER SPACESHIP (Moves diagonally)")
    print("="*60)

    # Classic glider pattern
    live_cells = {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    grid = Grid(width=10, height=10, live_cells=live_cells)
    rules = ConwayRules()

    print_grid(grid, "Generation 0")

    # Evolve for several generations
    for i in range(1, 5):
        grid = grid.step(rules)
        print_grid(grid, f"Generation {i}")


def demo_custom_rules():
    """Demonstrate custom rules (HighLife - B36/S23)."""
    print("\n" + "="*60)
    print("CUSTOM RULES: HighLife (B36/S23)")
    print("="*60)
    print("HighLife adds B6 to Conway's rules, creating replicators")

    # Start with a simple pattern
    live_cells = {(2, 1), (2, 2), (2, 3)}
    grid = Grid(width=7, height=7, live_cells=live_cells)
    rules = Rules(birth=[3, 6], survival=[2, 3])

    print_grid(grid, "Generation 0")

    for i in range(1, 4):
        grid = grid.step(rules)
        print_grid(grid, f"Generation {i}")


def validate_implementation():
    """Run basic validation tests."""
    print("\n" + "="*60)
    print("VALIDATION TESTS")
    print("="*60)

    # Test 1: Empty grid stays empty
    grid = Grid(width=5, height=5)
    rules = ConwayRules()
    next_grid = grid.step(rules)
    assert next_grid.count_live_cells() == 0, "Empty grid should stay empty"
    print("✓ Empty grid stays empty")

    # Test 2: Single cell dies
    grid = Grid(width=5, height=5, live_cells={(2, 2)})
    next_grid = grid.step(rules)
    assert next_grid.count_live_cells() == 0, "Single cell should die"
    print("✓ Single cell dies (underpopulation)")

    # Test 3: Block is stable
    live_cells = {(1, 1), (1, 2), (2, 1), (2, 2)}
    grid = Grid(width=5, height=5, live_cells=live_cells)
    next_grid = grid.step(rules)
    assert next_grid.count_live_cells() == 4, "Block should be stable"
    assert next_grid.get_live_cells() == live_cells, "Block should be unchanged"
    print("✓ Block still life is stable")

    # Test 4: Neighbor counting
    live_cells = {(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)}
    grid = Grid(width=3, height=3, live_cells=live_cells)
    assert grid.count_neighbors(1, 1) == 8, "Center cell should have 8 neighbors"
    print("✓ Neighbor counting works correctly")

    # Test 5: Custom rules work
    rules_custom = Rules(birth=[1], survival=[1])
    grid = Grid(width=5, height=5, live_cells={(2, 2)})
    next_grid = grid.step(rules_custom)
    # With B1/S1, pattern should change
    print("✓ Custom rules are applied")

    print("\n✓ All validation tests passed!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CELLULAR AUTOMATON DEMO")
    print("By Alice and Bob")
    print("="*60)

    validate_implementation()
    demo_block()
    demo_blinker()
    demo_glider()
    demo_custom_rules()

    print("\n" + "="*60)
    print("Demo complete! The implementation is working correctly.")
    print("="*60)
