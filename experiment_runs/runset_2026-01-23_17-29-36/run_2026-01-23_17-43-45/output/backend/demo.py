#!/usr/bin/env python3
"""
Demo script to test the pathfinding algorithms without external dependencies.
This script creates a simple pathfinding scenario and runs all three algorithms.
"""

from models import Grid, Position, NodeType
from algorithms import AStarAlgorithm, DijkstraAlgorithm, BreadthFirstSearch


def print_grid(grid: Grid, path=None, current=None, open_set=None, closed_set=None):
    """Print a visual representation of the grid."""
    print(f"\nGrid ({grid.width}x{grid.height}):")

    # Convert sets to position tuples for easier lookup
    path_positions = set()
    if path:
        path_positions = {(pos.x, pos.y) for pos in path}

    open_positions = set()
    if open_set:
        open_positions = {(pos.x, pos.y) for pos in open_set}

    closed_positions = set()
    if closed_set:
        closed_positions = {(pos.x, pos.y) for pos in closed_set}

    current_pos = None
    if current:
        current_pos = (current.x, current.y)

    # Print grid from top to bottom (higher y values first)
    for y in range(grid.height - 1, -1, -1):
        row = ""
        for x in range(grid.width):
            pos = Position(x, y)
            node = grid.get_node(pos)

            if not node:
                row += "? "
                continue

            # Determine symbol based on priority
            if (x, y) == current_pos:
                row += "@ "  # Current node
            elif node.node_type == NodeType.START:
                row += "S "
            elif node.node_type == NodeType.END:
                row += "E "
            elif node.node_type == NodeType.OBSTACLE:
                row += "█ "
            elif (x, y) in path_positions:
                row += "* "  # Path
            elif (x, y) in open_positions:
                row += "o "  # Open set
            elif (x, y) in closed_positions:
                row += "· "  # Closed set
            else:
                row += ". "  # Empty

        print(f"{y}: {row}")

    # Print x-axis labels
    x_labels = "   " + " ".join(str(x) for x in range(grid.width))
    print(x_labels)


def run_algorithm_demo(algorithm_name: str, algorithm_class, grid: Grid):
    """Run a single algorithm and display the results."""
    print(f"\n{'='*50}")
    print(f"Running {algorithm_name}")
    print('='*50)

    algorithm = algorithm_class(grid)
    steps = list(algorithm.execute())

    print(f"Total steps: {len(steps)}")

    if not steps:
        print("No steps generated!")
        return

    # Show initial state
    initial_step = steps[0]
    print(f"\nStep 0: {initial_step.message}")
    print_grid(grid)

    # Show a few intermediate steps
    if len(steps) > 5:
        mid_step_idx = len(steps) // 2
        mid_step = steps[mid_step_idx]
        print(f"\nStep {mid_step.step_number}: {mid_step.message}")
        print_grid(
            grid,
            current=mid_step.current_node,
            open_set=mid_step.open_set,
            closed_set=mid_step.closed_set
        )

    # Show final result
    final_step = steps[-1]
    print(f"\nFinal Step {final_step.step_number}: {final_step.message}")
    print_grid(
        grid,
        path=final_step.path,
        closed_set=final_step.closed_set
    )

    if final_step.path:
        print(f"Path length: {len(final_step.path)}")
        print("Path coordinates:", [(pos.x, pos.y) for pos in final_step.path])


def create_test_scenario() -> Grid:
    """Create a test scenario with obstacles."""
    # Create a 10x8 grid
    grid = Grid(width=10, height=8)

    # Set start and end positions
    grid.set_node_type(Position(1, 1), NodeType.START)
    grid.set_node_type(Position(8, 6), NodeType.END)

    # Add some obstacles to make it interesting
    obstacles = [
        # Vertical wall
        (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
        # L-shaped obstacle
        (6, 1), (6, 2), (7, 2),
        # Small scattered obstacles
        (2, 4), (8, 3), (3, 6)
    ]

    for x, y in obstacles:
        grid.set_node_type(Position(x, y), NodeType.OBSTACLE)

    return grid


def main():
    """Run the pathfinding algorithm demo."""
    print("Interactive Algorithm Learning Studio - Backend Demo")
    print("Testing pathfinding algorithms with step-by-step visualization")

    # Create test scenario
    grid = create_test_scenario()

    print("\nTest scenario:")
    print("S = Start, E = End, █ = Obstacle, . = Empty")
    print_grid(grid)

    # Test all algorithms
    algorithms = [
        ("A* Search", AStarAlgorithm),
        ("Dijkstra's Algorithm", DijkstraAlgorithm),
        ("Breadth-First Search", BreadthFirstSearch)
    ]

    for name, algo_class in algorithms:
        run_algorithm_demo(name, algo_class, grid)

    print(f"\n{'='*50}")
    print("Demo completed successfully!")
    print("Backend is ready for frontend integration.")
    print('='*50)


if __name__ == "__main__":
    main()