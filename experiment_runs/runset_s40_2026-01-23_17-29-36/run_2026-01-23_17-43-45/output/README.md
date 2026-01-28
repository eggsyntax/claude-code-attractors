# Interactive Algorithm Learning Studio

An educational web application for visualizing pathfinding algorithms like A*, Dijkstra's, and Breadth-First Search. This project demonstrates real-time algorithm execution with step-by-step visualization to help users understand how these algorithms work internally.

## Architecture

### Backend (Python/FastAPI)
Located in `/backend/` directory:

- **`models.py`**: Core data structures (Grid, Node, Position, AlgorithmStep)
- **`algorithms.py`**: Pathfinding algorithm implementations with step-by-step tracking
- **`main.py`**: FastAPI REST API server
- **`test_pathfinding.py`**: Comprehensive test suite
- **`demo.py`**: Standalone demo script for testing algorithms

### Frontend (JavaScript/HTML5 Canvas)
Complete interactive visualization system:

- **`index.html`**: Main application interface with responsive layout
- **`grid.js`**: Interactive grid system with mouse controls and canvas rendering
- **`visualization.js`**: Algorithm visualization engine with step-by-step playback
- **`app.js`**: Main application controller connecting frontend to backend API
- **`styles.css`**: Modern responsive styling with algorithm state indicators
- **`demo.html`**: Demo presentation with sample scenarios

#### Interactive Features:
- **Mouse Controls**: Left-click to set start/goal, right-click+drag for obstacles, middle-click to clear
- **Real-time Visualization**: Open sets, closed sets, current node, and final path with color coding
- **Playback Controls**: Play/pause, step forward/back, variable speed control
- **Algorithm State Display**: Live cost calculations (F/G/H), node counts, execution metrics
- **Sample Scenarios**: Pre-built demos for quick testing and education

## Features

### Algorithms Implemented
1. **A* Search**: Optimal pathfinding with heuristic guidance
2. **Dijkstra's Algorithm**: Uniform cost search (optimal)
3. **Breadth-First Search**: Level-by-level exploration (unweighted optimal)

### Key Capabilities
- **Step-by-step execution**: Each algorithm yields intermediate states
- **Real-time visualization**: Track open sets, closed sets, and current exploration
- **Multiple heuristics**: Manhattan and Euclidean distance for A*
- **Obstacle support**: Dynamic grid modification with obstacle placement
- **Path reconstruction**: Shows final optimal path when found
- **Performance metrics**: Step counts and cost tracking

## API Endpoints

### Grid Management
- `POST /grid/setup`: Initialize grid with dimensions and obstacles
- `GET /grid/info`: Get current grid state
- `POST /grid/update`: Update individual grid cells

### Algorithm Execution
- `POST /algorithm/run`: Execute pathfinding algorithm with step tracking
- `GET /algorithms/info`: Get available algorithms and their properties

### Example API Usage

```python
# Setup a 10x10 grid with obstacles
grid_request = {
    "width": 10,
    "height": 10,
    "obstacles": [{"x": 3, "y": 3}, {"x": 3, "y": 4}],
    "start": {"x": 0, "y": 0},
    "end": {"x": 9, "y": 9}
}

# Run A* algorithm
algorithm_request = {
    "algorithm": "astar",
    "heuristic": "manhattan"
}
```

## Installation & Setup

### Prerequisites
- Python 3.8+ with pip
- Modern web browser with HTML5 Canvas support
- FastAPI and Uvicorn dependencies

### Backend Setup
```bash
cd backend/
pip install fastapi uvicorn python-multipart
uvicorn main:app --reload --port 8000
# Server runs on http://localhost:8000
```

### Frontend Setup
```bash
# Open any of these files in your browser:
# 1. demo.html - Full demo presentation with sample scenarios
# 2. index.html - Main application interface
# Ensure backend is running for full functionality
```

### Testing
```bash
cd backend/
python test_pathfinding.py  # Run comprehensive tests
python demo.py             # Run visual demo
```

## Algorithm Details

### A* Search
- **Optimality**: Yes (with admissible heuristic)
- **Completeness**: Yes
- **Time Complexity**: O(b^d) where b is branching factor, d is depth
- **Space Complexity**: O(b^d)
- **Heuristics**: Manhattan distance (4-directional), Euclidean distance

### Dijkstra's Algorithm
- **Optimality**: Yes
- **Completeness**: Yes
- **Time Complexity**: O((V + E) log V)
- **Space Complexity**: O(V)
- **Use Case**: When all edges have uniform weight, or when optimal path to ALL nodes is needed

### Breadth-First Search
- **Optimality**: Yes (for unweighted graphs)
- **Completeness**: Yes
- **Time Complexity**: O(V + E)
- **Space Complexity**: O(V)
- **Use Case**: Shortest path in unweighted graphs, level-by-level exploration

## Data Models

### Core Classes
- **Position**: 2D coordinates with distance calculations
- **Node**: Grid cell with pathfinding metadata (g_cost, h_cost, parent)
- **Grid**: 2D array of nodes with neighbor detection
- **AlgorithmStep**: Single step in algorithm execution with visualization data

### Algorithm Flow
1. Initialize grid with start/end positions and obstacles
2. Reset all pathfinding metadata
3. Execute algorithm step-by-step, yielding intermediate states
4. Track open set (nodes to explore) and closed set (explored nodes)
5. Reconstruct path when goal is reached

## Educational Value

This tool helps students understand:

1. **How algorithms make decisions**: See exactly which nodes are considered and why
2. **Impact of heuristics**: Compare A* with different heuristics vs Dijkstra
3. **Trade-offs**: Optimal vs fast, memory usage, step counts
4. **Problem-solving patterns**: How obstacles affect pathfinding strategies
5. **Algorithm internals**: Open/closed sets, cost calculations, parent pointers

## Future Enhancements

### Backend Extensions
- Weighted edges support
- More heuristic functions
- Additional algorithms (D*, Jump Point Search)
- Performance profiling and metrics
- Multi-goal pathfinding

### Integration Points
The backend is designed to integrate seamlessly with a JavaScript frontend through clean REST APIs and detailed step data that supports rich visualization.

## Testing

The test suite covers:
- Unit tests for all core classes
- Algorithm correctness verification
- Edge cases (no path, obstacles, boundary conditions)
- API endpoint validation
- Path optimality verification

Run tests with: `python test_pathfinding.py`

## Contributing

The codebase follows clean architecture principles:
- Separation of concerns (models, algorithms, API)
- Comprehensive documentation
- Test-driven development
- Extensible design for new algorithms