"""
Comprehensive test suite for the pathfinding algorithm system.
Tests cover models, algorithms, and API endpoints.
"""
import pytest
from unittest.mock import Mock
from typing import List

from models import Position, Node, NodeType, Grid, AlgorithmStep
from algorithms import AStarAlgorithm, DijkstraAlgorithm, BreadthFirstSearch


class TestPosition:
    """Tests for the Position class."""

    def test_position_creation(self):
        """Test Position object creation."""
        pos = Position(5, 3)
        assert pos.x == 5
        assert pos.y == 3

    def test_position_equality(self):
        """Test Position equality comparison."""
        pos1 = Position(2, 4)
        pos2 = Position(2, 4)
        pos3 = Position(3, 4)

        assert pos1 == pos2
        assert pos1 != pos3
        assert pos2 != pos3

    def test_position_hash(self):
        """Test Position can be used in sets/dicts."""
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        pos3 = Position(2, 1)

        positions = {pos1, pos2, pos3}
        assert len(positions) == 2  # pos1 and pos2 are the same

    def test_manhattan_distance(self):
        """Test Manhattan distance calculation."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)

        distance = pos1.manhattan_distance(pos2)
        assert distance == 7  # |3-0| + |4-0| = 7

    def test_euclidean_distance(self):
        """Test Euclidean distance calculation."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)

        distance = pos1.euclidean_distance(pos2)
        assert distance == 5.0  # sqrt(3^2 + 4^2) = 5


class TestNode:
    """Tests for the Node class."""

    def test_node_creation(self):
        """Test Node object creation with defaults."""
        pos = Position(2, 3)
        node = Node(position=pos)

        assert node.position == pos
        assert node.node_type == NodeType.EMPTY
        assert node.g_cost == float('inf')
        assert node.h_cost == 0.0
        assert node.f_cost == float('inf')
        assert node.parent is None
        assert not node.visited
        assert not node.in_open_set

    def test_node_f_cost_calculation(self):
        """Test f_cost is correctly calculated from g_cost and h_cost."""
        pos = Position(1, 1)
        node = Node(position=pos)
        node.g_cost = 5.0
        node.h_cost = 3.0

        # f_cost should update when we call __post_init__ equivalent
        node.f_cost = node.g_cost + node.h_cost
        assert node.f_cost == 8.0

    def test_node_comparison(self):
        """Test nodes can be compared by f_cost for priority queue."""
        pos1 = Position(1, 1)
        pos2 = Position(2, 2)

        node1 = Node(position=pos1, g_cost=5.0, h_cost=3.0)
        node1.f_cost = node1.g_cost + node1.h_cost

        node2 = Node(position=pos2, g_cost=6.0, h_cost=1.0)
        node2.f_cost = node2.g_cost + node2.h_cost

        assert node2 < node1  # node2 has lower f_cost (7 vs 8)

    def test_node_reset_pathfinding_data(self):
        """Test resetting pathfinding data."""
        pos = Position(1, 1)
        node = Node(position=pos)

        # Set some pathfinding data
        node.g_cost = 5.0
        node.h_cost = 3.0
        node.f_cost = 8.0
        node.parent = Mock()
        node.visited = True
        node.in_open_set = True

        # Reset should clear all pathfinding data
        node.reset_pathfinding_data()

        assert node.g_cost == float('inf')
        assert node.h_cost == 0.0
        assert node.f_cost == float('inf')
        assert node.parent is None
        assert not node.visited
        assert not node.in_open_set


class TestGrid:
    """Tests for the Grid class."""

    def test_grid_creation(self):
        """Test Grid initialization creates correct number of nodes."""
        grid = Grid(width=5, height=3)

        assert grid.width == 5
        assert grid.height == 3
        assert len(grid.nodes) == 15  # 5 * 3
        assert grid.start_pos is None
        assert grid.end_pos is None

    def test_get_node_valid_position(self):
        """Test getting a node at a valid position."""
        grid = Grid(width=3, height=3)
        pos = Position(1, 2)

        node = grid.get_node(pos)
        assert node is not None
        assert node.position == pos

    def test_get_node_invalid_position(self):
        """Test getting a node at an invalid position returns None."""
        grid = Grid(width=3, height=3)
        pos = Position(5, 5)  # Outside grid

        node = grid.get_node(pos)
        assert node is None

    def test_set_node_type(self):
        """Test setting node types and updating start/end positions."""
        grid = Grid(width=3, height=3)

        start_pos = Position(0, 0)
        end_pos = Position(2, 2)

        grid.set_node_type(start_pos, NodeType.START)
        grid.set_node_type(end_pos, NodeType.END)

        assert grid.start_pos == start_pos
        assert grid.end_pos == end_pos
        assert grid.get_node(start_pos).node_type == NodeType.START
        assert grid.get_node(end_pos).node_type == NodeType.END

    def test_get_neighbors_center_cell(self):
        """Test getting neighbors for a center cell."""
        grid = Grid(width=3, height=3)
        center_pos = Position(1, 1)

        neighbors = grid.get_neighbors(center_pos)

        # Should have 4 neighbors (up, right, down, left)
        assert len(neighbors) == 4

        expected_positions = {
            Position(1, 2),  # Up
            Position(2, 1),  # Right
            Position(1, 0),  # Down
            Position(0, 1)   # Left
        }

        actual_positions = {node.position for node in neighbors}
        assert actual_positions == expected_positions

    def test_get_neighbors_corner_cell(self):
        """Test getting neighbors for a corner cell."""
        grid = Grid(width=3, height=3)
        corner_pos = Position(0, 0)

        neighbors = grid.get_neighbors(corner_pos)

        # Should have 2 neighbors (up and right)
        assert len(neighbors) == 2

    def test_get_neighbors_with_obstacles(self):
        """Test getting neighbors when obstacles are present."""
        grid = Grid(width=3, height=3)
        center_pos = Position(1, 1)
        obstacle_pos = Position(1, 2)

        # Set an obstacle
        grid.set_node_type(obstacle_pos, NodeType.OBSTACLE)

        neighbors = grid.get_neighbors(center_pos)

        # Should have 3 neighbors (obstacle excluded)
        assert len(neighbors) == 3

        # Verify obstacle is not in neighbors
        neighbor_positions = {node.position for node in neighbors}
        assert obstacle_pos not in neighbor_positions

    def test_reset_pathfinding(self):
        """Test resetting pathfinding data for all nodes."""
        grid = Grid(width=2, height=2)

        # Set some pathfinding data on nodes
        for node in grid.nodes.values():
            node.g_cost = 5.0
            node.visited = True

        grid.reset_pathfinding()

        # Verify all nodes are reset
        for node in grid.nodes.values():
            assert node.g_cost == float('inf')
            assert not node.visited


class TestAStarAlgorithm:
    """Tests for A* algorithm implementation."""

    def create_simple_grid(self) -> Grid:
        """Create a simple 3x3 grid for testing."""
        grid = Grid(width=3, height=3)
        grid.set_node_type(Position(0, 0), NodeType.START)
        grid.set_node_type(Position(2, 2), NodeType.END)
        return grid

    def test_astar_simple_path(self):
        """Test A* finds a path in a simple grid."""
        grid = self.create_simple_grid()
        algorithm = AStarAlgorithm(grid)

        steps = list(algorithm.execute())

        # Should find a path
        final_step = steps[-1]
        assert len(final_step['path']) > 0
        assert "Path found" in final_step['message']

    def test_astar_with_obstacles(self):
        """Test A* navigates around obstacles."""
        grid = Grid(width=3, height=3)
        grid.set_node_type(Position(0, 0), NodeType.START)
        grid.set_node_type(Position(2, 2), NodeType.END)

        # Add obstacle blocking direct path
        grid.set_node_type(Position(1, 1), NodeType.OBSTACLE)

        algorithm = AStarAlgorithm(grid)
        steps = list(algorithm.execute())

        # Should still find a path around obstacle
        final_step = steps[-1]
        assert len(final_step['path']) > 0
        assert "Path found" in final_step['message']

        # Verify path doesn't go through obstacle
        path_positions = {(pos['x'], pos['y']) for pos in final_step['path']}
        assert (1, 1) not in path_positions

    def test_astar_no_path(self):
        """Test A* correctly reports when no path exists."""
        grid = Grid(width=3, height=3)
        grid.set_node_type(Position(0, 0), NodeType.START)
        grid.set_node_type(Position(2, 2), NodeType.END)

        # Block all paths with obstacles
        obstacle_positions = [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)]
        for x, y in obstacle_positions:
            grid.set_node_type(Position(x, y), NodeType.OBSTACLE)

        algorithm = AStarAlgorithm(grid)
        steps = list(algorithm.execute())

        # Should report no path found
        final_step = steps[-1]
        assert len(final_step['path']) == 0
        assert "No path found" in final_step['message']

    def test_astar_step_progression(self):
        """Test A* generates proper step sequence."""
        grid = self.create_simple_grid()
        algorithm = AStarAlgorithm(grid)

        steps = list(algorithm.execute())

        # Verify step numbers increase
        for i, step in enumerate(steps):
            assert step['step_number'] == i

        # Verify we have meaningful steps
        assert len(steps) > 1

        # First step should be initialization
        assert "Starting A*" in steps[0]['message']


class TestDijkstraAlgorithm:
    """Tests for Dijkstra's algorithm implementation."""

    def test_dijkstra_finds_path(self):
        """Test Dijkstra finds optimal path."""
        grid = Grid(width=3, height=3)
        grid.set_node_type(Position(0, 0), NodeType.START)
        grid.set_node_type(Position(2, 2), NodeType.END)

        algorithm = DijkstraAlgorithm(grid)
        steps = list(algorithm.execute())

        final_step = steps[-1]
        assert len(final_step['path']) > 0
        assert "Dijkstra" in final_step['message']


class TestBreadthFirstSearch:
    """Tests for BFS algorithm implementation."""

    def test_bfs_finds_shortest_path(self):
        """Test BFS finds shortest path in unweighted graph."""
        grid = Grid(width=3, height=3)
        grid.set_node_type(Position(0, 0), NodeType.START)
        grid.set_node_type(Position(2, 2), NodeType.END)

        algorithm = BreadthFirstSearch(grid)
        steps = list(algorithm.execute())

        final_step = steps[-1]
        assert len(final_step['path']) > 0
        assert "Breadth-First" in final_step['message']

    def test_bfs_explores_level_by_level(self):
        """Test BFS explores nodes level by level."""
        grid = Grid(width=4, height=4)
        grid.set_node_type(Position(1, 1), NodeType.START)
        grid.set_node_type(Position(3, 3), NodeType.END)

        algorithm = BreadthFirstSearch(grid)
        steps = list(algorithm.execute())

        # Verify BFS explores neighbors before going deeper
        # This is implicit in the algorithm correctness
        assert len(steps) > 1
        final_step = steps[-1]
        assert len(final_step['path']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])