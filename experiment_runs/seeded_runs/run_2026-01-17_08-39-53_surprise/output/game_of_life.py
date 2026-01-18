"""
Conway's Game of Life - A demonstration of emergent behavior

Simple local rules:
1. Any live cell with 2-3 live neighbors survives
2. Any dead cell with exactly 3 live neighbors becomes alive
3. All other cells die or stay dead

Despite these trivial rules, complex behaviors emerge that feel like they
have agency, intentionality, and physics - none of which exist in the rules.

Run this to see gliders (patterns that move across the grid) emerge from
simple initial conditions.
"""

import time
import os


def create_grid(width, height):
    """Create an empty grid."""
    return [[0 for _ in range(width)] for _ in range(height)]


def count_neighbors(grid, x, y):
    """Count living neighbors for a cell at position (x, y)."""
    height = len(grid)
    width = len(grid[0])
    count = 0

    # Check all 8 neighbors
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue

            # Wrap around edges (toroidal topology)
            nx = (x + dx) % width
            ny = (y + dy) % height
            count += grid[ny][nx]

    return count


def step(grid):
    """Compute the next generation according to Conway's rules."""
    height = len(grid)
    width = len(grid[0])
    new_grid = create_grid(width, height)

    for y in range(height):
        for x in range(width):
            neighbors = count_neighbors(grid, x, y)

            if grid[y][x] == 1:  # Cell is alive
                # Survival: 2 or 3 neighbors
                if neighbors in [2, 3]:
                    new_grid[y][x] = 1
            else:  # Cell is dead
                # Birth: exactly 3 neighbors
                if neighbors == 3:
                    new_grid[y][x] = 1

    return new_grid


def print_grid(grid, generation):
    """Print the grid to terminal."""
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"Generation {generation}")
    print("=" * (len(grid[0]) + 2))

    for row in grid:
        print("|" + "".join("█" if cell else " " for cell in row) + "|")

    print("=" * (len(grid[0]) + 2))


def add_glider(grid, x, y):
    """
    Add a glider pattern at position (x, y).

    A glider is a 5-cell pattern that moves diagonally across the grid.
    Pattern:
      █
       ██
     ██
    """
    pattern = [
        (1, 0),
        (2, 1),
        (0, 2), (1, 2), (2, 2)
    ]

    for dx, dy in pattern:
        if 0 <= y + dy < len(grid) and 0 <= x + dx < len(grid[0]):
            grid[y + dy][x + dx] = 1


def add_lightweight_spaceship(grid, x, y):
    """
    Add a Lightweight Spaceship (LWSS) at position (x, y).

    Pattern:
     █  █
         █
     █   █
      ████
    """
    pattern = [
        (1, 0), (4, 0),
        (5, 1),
        (1, 2), (5, 2),
        (2, 3), (3, 3), (4, 3), (5, 3)
    ]

    for dx, dy in pattern:
        if 0 <= y + dy < len(grid) and 0 <= x + dx < len(grid[0]):
            grid[y + dy][x + dx] = 1


def add_gosper_glider_gun(grid, x, y):
    """
    Add the Gosper Glider Gun - a pattern that creates infinite gliders.

    This pattern demonstrates true emergence: a stationary structure
    that continuously manufactures moving structures, creating unbounded
    complexity from bounded initial conditions.
    """
    pattern = [
        (24, 0),
        (22, 1), (24, 1),
        (12, 2), (13, 2), (20, 2), (21, 2), (34, 2), (35, 2),
        (11, 3), (15, 3), (20, 3), (21, 3), (34, 3), (35, 3),
        (0, 4), (1, 4), (10, 4), (16, 4), (20, 4), (21, 4),
        (0, 5), (1, 5), (10, 5), (14, 5), (16, 5), (17, 5), (22, 5), (24, 5),
        (10, 6), (16, 6), (24, 6),
        (11, 7), (15, 7),
        (12, 8), (13, 8)
    ]

    for dx, dy in pattern:
        if 0 <= y + dy < len(grid) and 0 <= x + dx < len(grid[0]):
            grid[y + dy][x + dx] = 1


def run_simulation(grid, generations=100, delay=0.1):
    """Run the simulation for a specified number of generations."""
    for gen in range(generations):
        print_grid(grid, gen)
        time.sleep(delay)
        grid = step(grid)

    return grid


def main():
    """Run different demonstrations of emergent behavior."""

    print("Conway's Game of Life - Emergence Demonstration\n")
    print("Choose a demo:")
    print("1. Single Glider (moves diagonally)")
    print("2. Two Gliders Colliding (complex interaction)")
    print("3. Lightweight Spaceship (larger moving pattern)")
    print("4. Gosper Glider Gun (creates infinite gliders)")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        grid = create_grid(40, 20)
        add_glider(grid, 5, 5)
        run_simulation(grid, generations=80, delay=0.2)

    elif choice == "2":
        grid = create_grid(40, 20)
        add_glider(grid, 5, 5)
        add_glider(grid, 30, 2)
        run_simulation(grid, generations=100, delay=0.15)

    elif choice == "3":
        grid = create_grid(50, 20)
        add_lightweight_spaceship(grid, 5, 8)
        run_simulation(grid, generations=100, delay=0.15)

    elif choice == "4":
        grid = create_grid(60, 30)
        add_gosper_glider_gun(grid, 2, 10)
        print("\nWatch as a stationary 'gun' continuously creates gliders!")
        print("This demonstrates unbounded growth from finite initial conditions.\n")
        input("Press Enter to start...")
        run_simulation(grid, generations=200, delay=0.1)

    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
