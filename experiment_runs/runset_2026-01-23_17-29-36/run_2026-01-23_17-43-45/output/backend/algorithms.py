"""
Pathfinding algorithm implementations with step-by-step execution tracking.
"""
import heapq
from typing import List, Optional, Generator, Callable
from abc import ABC, abstractmethod

from models import Grid, Node, Position, AlgorithmStep, AlgorithmState, NodeType


class PathfindingAlgorithm(ABC):
    """Abstract base class for pathfinding algorithms."""

    def __init__(self, grid: Grid):
        self.grid = grid
        self.steps: List[AlgorithmStep] = []
        self.state = AlgorithmState.NOT_STARTED
        self.step_count = 0

    @abstractmethod
    def execute(self) -> Generator[AlgorithmStep, None, None]:
        """Execute the algorithm and yield steps."""
        pass

    def heuristic(self, pos1: Position, pos2: Position) -> float:
        """Default heuristic function (Manhattan distance)."""
        return pos1.manhattan_distance(pos2)

    def reconstruct_path(self, end_node: Node) -> List[Position]:
        """Reconstruct path from end node to start using parent pointers."""
        path = []
        current = end_node

        while current:
            path.append(current.position)
            current = current.parent

        return list(reversed(path))


class AStarAlgorithm(PathfindingAlgorithm):
    """A* pathfinding algorithm implementation with step tracking."""

    def __init__(self, grid: Grid, heuristic_func: Optional[Callable] = None):
        super().__init__(grid)
        if heuristic_func:
            self.heuristic = heuristic_func

    def execute(self) -> Generator[AlgorithmStep, None, None]:
        """Execute A* algorithm with step-by-step tracking."""
        self.grid.reset_pathfinding()
        self.state = AlgorithmState.RUNNING
        self.step_count = 0

        if not self.grid.start_pos or not self.grid.end_pos:
            yield AlgorithmStep(
                step_number=0,
                current_node=Position(0, 0),
                open_set=[],
                closed_set=[],
                path=[],
                message="Error: Start or end position not set"
            )
            return

        start_node = self.grid.get_node(self.grid.start_pos)
        end_node = self.grid.get_node(self.grid.end_pos)

        if not start_node or not end_node:
            yield AlgorithmStep(
                step_number=0,
                current_node=Position(0, 0),
                open_set=[],
                closed_set=[],
                path=[],
                message="Error: Invalid start or end position"
            )
            return

        # Initialize start node
        start_node.g_cost = 0
        start_node.h_cost = self.heuristic(self.grid.start_pos, self.grid.end_pos)
        start_node.f_cost = start_node.g_cost + start_node.h_cost

        # Open set (priority queue) and closed set
        open_set = [start_node]
        heapq.heapify(open_set)
        closed_set = set()

        start_node.in_open_set = True

        # Initial step
        yield AlgorithmStep(
            step_number=self.step_count,
            current_node=self.grid.start_pos,
            open_set=[self.grid.start_pos],
            closed_set=[],
            path=[],
            message="Starting A* search",
            costs={'g': start_node.g_cost, 'h': start_node.h_cost, 'f': start_node.f_cost}
        )

        while open_set:
            self.step_count += 1

            # Get node with lowest f_cost
            current_node = heapq.heappop(open_set)
            current_node.in_open_set = False
            current_node.visited = True
            closed_set.add(current_node.position)

            # Check if we reached the goal
            if current_node.position == self.grid.end_pos:
                path = self.reconstruct_path(current_node)
                self.state = AlgorithmState.FOUND_PATH

                yield AlgorithmStep(
                    step_number=self.step_count,
                    current_node=current_node.position,
                    open_set=[node.position for node in open_set],
                    closed_set=list(closed_set),
                    path=path,
                    message=f"Path found! Length: {len(path)}",
                    costs={'g': current_node.g_cost, 'h': current_node.h_cost, 'f': current_node.f_cost}
                )
                return

            # Examine neighbors
            neighbors_examined = 0
            for neighbor in self.grid.get_neighbors(current_node.position):
                if neighbor.position in closed_set:
                    continue

                tentative_g_cost = current_node.g_cost + 1  # Assuming uniform cost

                if tentative_g_cost < neighbor.g_cost:
                    # Better path found
                    neighbor.parent = current_node
                    neighbor.g_cost = tentative_g_cost
                    neighbor.h_cost = self.heuristic(neighbor.position, self.grid.end_pos)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost

                    if not neighbor.in_open_set:
                        heapq.heappush(open_set, neighbor)
                        neighbor.in_open_set = True
                        neighbors_examined += 1

            # Yield current step
            yield AlgorithmStep(
                step_number=self.step_count,
                current_node=current_node.position,
                open_set=[node.position for node in open_set],
                closed_set=list(closed_set),
                path=[],
                message=f"Exploring node ({current_node.position.x}, {current_node.position.y}), examined {neighbors_examined} neighbors",
                costs={'g': current_node.g_cost, 'h': current_node.h_cost, 'f': current_node.f_cost}
            )

        # No path found
        self.state = AlgorithmState.NO_PATH
        yield AlgorithmStep(
            step_number=self.step_count,
            current_node=current_node.position if 'current_node' in locals() else Position(0, 0),
            open_set=[],
            closed_set=list(closed_set),
            path=[],
            message="No path found to the goal"
        )


class DijkstraAlgorithm(PathfindingAlgorithm):
    """Dijkstra's algorithm implementation (A* with zero heuristic)."""

    def heuristic(self, pos1: Position, pos2: Position) -> float:
        """Dijkstra uses zero heuristic (uniform cost search)."""
        return 0.0

    def execute(self) -> Generator[AlgorithmStep, None, None]:
        """Execute Dijkstra's algorithm (reuse A* with zero heuristic)."""
        astar = AStarAlgorithm(self.grid, lambda p1, p2: 0.0)

        # Update messages to reflect Dijkstra
        for step in astar.execute():
            if "A*" in step.message:
                step.message = step.message.replace("A*", "Dijkstra's")
            yield step


class BreadthFirstSearch(PathfindingAlgorithm):
    """Breadth-First Search algorithm implementation."""

    def execute(self) -> Generator[AlgorithmStep, None, None]:
        """Execute BFS algorithm with step-by-step tracking."""
        from collections import deque

        self.grid.reset_pathfinding()
        self.state = AlgorithmState.RUNNING
        self.step_count = 0

        if not self.grid.start_pos or not self.grid.end_pos:
            yield AlgorithmStep(
                step_number=0,
                current_node=Position(0, 0),
                open_set=[],
                closed_set=[],
                path=[],
                message="Error: Start or end position not set"
            )
            return

        start_node = self.grid.get_node(self.grid.start_pos)
        end_node = self.grid.get_node(self.grid.end_pos)

        if not start_node or not end_node:
            yield AlgorithmStep(
                step_number=0,
                current_node=Position(0, 0),
                open_set=[],
                closed_set=[],
                path=[],
                message="Error: Invalid start or end position"
            )
            return

        # Initialize BFS
        queue = deque([start_node])
        visited = set([start_node.position])
        start_node.visited = True
        start_node.g_cost = 0

        # Initial step
        yield AlgorithmStep(
            step_number=self.step_count,
            current_node=self.grid.start_pos,
            open_set=[self.grid.start_pos],
            closed_set=[],
            path=[],
            message="Starting Breadth-First Search",
            costs={'distance': 0}
        )

        while queue:
            self.step_count += 1
            current_node = queue.popleft()

            # Check if we reached the goal
            if current_node.position == self.grid.end_pos:
                path = self.reconstruct_path(current_node)
                self.state = AlgorithmState.FOUND_PATH

                yield AlgorithmStep(
                    step_number=self.step_count,
                    current_node=current_node.position,
                    open_set=[node.position for node in queue],
                    closed_set=list(visited),
                    path=path,
                    message=f"Path found! Length: {len(path)}",
                    costs={'distance': current_node.g_cost}
                )
                return

            # Examine neighbors
            neighbors_added = 0
            for neighbor in self.grid.get_neighbors(current_node.position):
                if neighbor.position not in visited:
                    neighbor.parent = current_node
                    neighbor.g_cost = current_node.g_cost + 1
                    neighbor.visited = True
                    queue.append(neighbor)
                    visited.add(neighbor.position)
                    neighbors_added += 1

            # Yield current step
            yield AlgorithmStep(
                step_number=self.step_count,
                current_node=current_node.position,
                open_set=[node.position for node in queue],
                closed_set=list(visited),
                path=[],
                message=f"Exploring node ({current_node.position.x}, {current_node.position.y}), added {neighbors_added} neighbors",
                costs={'distance': current_node.g_cost}
            )

        # No path found
        self.state = AlgorithmState.NO_PATH
        yield AlgorithmStep(
            step_number=self.step_count,
            current_node=current_node.position if 'current_node' in locals() else Position(0, 0),
            open_set=[],
            closed_set=list(visited),
            path=[],
            message="No path found to the goal"
        )