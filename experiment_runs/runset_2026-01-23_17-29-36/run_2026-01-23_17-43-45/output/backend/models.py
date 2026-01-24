"""
Core data models for the pathfinding algorithm visualization system.
"""
from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict, Any, Tuple
from enum import Enum
import heapq

class NodeType(Enum):
    """Types of nodes in the grid."""
    EMPTY = "empty"
    OBSTACLE = "obstacle"
    START = "start"
    END = "end"

class AlgorithmState(Enum):
    """Current state of algorithm execution."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    FOUND_PATH = "found_path"
    NO_PATH = "no_path"

@dataclass
class Position:
    """Represents a 2D coordinate position."""
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return isinstance(other, Position) and self.x == other.x and self.y == other.y

    def manhattan_distance(self, other: 'Position') -> int:
        """Calculate Manhattan distance to another position."""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def euclidean_distance(self, other: 'Position') -> float:
        """Calculate Euclidean distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

@dataclass
class Node:
    """Represents a node in the pathfinding grid."""
    position: Position
    node_type: NodeType = NodeType.EMPTY
    g_cost: float = float('inf')  # Distance from start
    h_cost: float = 0.0  # Heuristic distance to goal
    f_cost: float = float('inf')  # Total cost (g + h)
    parent: Optional['Node'] = None
    visited: bool = False
    in_open_set: bool = False

    def __post_init__(self):
        self.f_cost = self.g_cost + self.h_cost

    def __lt__(self, other):
        """For priority queue comparison."""
        return self.f_cost < other.f_cost

    def reset_pathfinding_data(self):
        """Reset all pathfinding-related data for a new search."""
        self.g_cost = float('inf')
        self.h_cost = 0.0
        self.f_cost = float('inf')
        self.parent = None
        self.visited = False
        self.in_open_set = False

@dataclass
class AlgorithmStep:
    """Represents a single step in the algorithm execution."""
    step_number: int
    current_node: Position
    open_set: List[Position]
    closed_set: List[Position]
    path: List[Position]
    message: str
    costs: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'step_number': self.step_number,
            'current_node': {'x': self.current_node.x, 'y': self.current_node.y},
            'open_set': [{'x': pos.x, 'y': pos.y} for pos in self.open_set],
            'closed_set': [{'x': pos.x, 'y': pos.y} for pos in self.closed_set],
            'path': [{'x': pos.x, 'y': pos.y} for pos in self.path],
            'message': self.message,
            'costs': self.costs
        }

@dataclass
class Grid:
    """Represents the 2D grid for pathfinding."""
    width: int
    height: int
    nodes: Dict[Position, Node] = field(default_factory=dict)
    start_pos: Optional[Position] = None
    end_pos: Optional[Position] = None

    def __post_init__(self):
        """Initialize the grid with empty nodes."""
        for x in range(self.width):
            for y in range(self.height):
                pos = Position(x, y)
                self.nodes[pos] = Node(position=pos)

    def get_node(self, position: Position) -> Optional[Node]:
        """Get node at given position."""
        return self.nodes.get(position)

    def set_node_type(self, position: Position, node_type: NodeType):
        """Set the type of node at given position."""
        if node := self.get_node(position):
            node.node_type = node_type

            # Update start/end positions
            if node_type == NodeType.START:
                self.start_pos = position
            elif node_type == NodeType.END:
                self.end_pos = position

    def get_neighbors(self, position: Position) -> List[Node]:
        """Get valid neighboring nodes (4-directional movement)."""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Up, Right, Down, Left

        for dx, dy in directions:
            new_pos = Position(position.x + dx, position.y + dy)

            if (0 <= new_pos.x < self.width and
                0 <= new_pos.y < self.height):
                if node := self.get_node(new_pos):
                    if node.node_type != NodeType.OBSTACLE:
                        neighbors.append(node)

        return neighbors

    def reset_pathfinding(self):
        """Reset all pathfinding data for all nodes."""
        for node in self.nodes.values():
            node.reset_pathfinding_data()

    def to_dict(self) -> Dict[str, Any]:
        """Convert grid to dictionary for JSON serialization."""
        return {
            'width': self.width,
            'height': self.height,
            'start_pos': {'x': self.start_pos.x, 'y': self.start_pos.y} if self.start_pos else None,
            'end_pos': {'x': self.end_pos.x, 'y': self.end_pos.y} if self.end_pos else None,
            'obstacles': [
                {'x': pos.x, 'y': pos.y}
                for pos, node in self.nodes.items()
                if node.node_type == NodeType.OBSTACLE
            ]
        }