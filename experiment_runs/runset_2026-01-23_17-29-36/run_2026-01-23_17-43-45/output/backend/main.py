"""
FastAPI backend for the Interactive Algorithm Learning Studio.
Provides REST endpoints for pathfinding algorithm visualization.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

from models import Grid, Position, NodeType, AlgorithmStep
from algorithms import AStarAlgorithm, DijkstraAlgorithm, BreadthFirstSearch

app = FastAPI(title="Algorithm Learning Studio API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class GridSetupRequest(BaseModel):
    """Request model for setting up a new grid."""
    width: int
    height: int
    obstacles: List[Dict[str, int]] = []
    start: Optional[Dict[str, int]] = None
    end: Optional[Dict[str, int]] = None

class AlgorithmRequest(BaseModel):
    """Request model for running an algorithm."""
    algorithm: str  # "astar", "dijkstra", "bfs"
    heuristic: str = "manhattan"  # "manhattan", "euclidean"

class AlgorithmResponse(BaseModel):
    """Response model for algorithm execution."""
    success: bool
    steps: List[Dict[str, Any]]
    total_steps: int
    message: str

# Global grid instance (in production, use proper session management)
current_grid: Optional[Grid] = None

@app.get("/")
async def root():
    """API health check."""
    return {"message": "Algorithm Learning Studio API is running"}

@app.post("/grid/setup")
async def setup_grid(request: GridSetupRequest):
    """Set up a new grid with obstacles and start/end points."""
    global current_grid

    try:
        # Create new grid
        current_grid = Grid(width=request.width, height=request.height)

        # Add obstacles
        for obstacle in request.obstacles:
            pos = Position(obstacle["x"], obstacle["y"])
            current_grid.set_node_type(pos, NodeType.OBSTACLE)

        # Set start position
        if request.start:
            start_pos = Position(request.start["x"], request.start["y"])
            current_grid.set_node_type(start_pos, NodeType.START)

        # Set end position
        if request.end:
            end_pos = Position(request.end["x"], request.end["y"])
            current_grid.set_node_type(end_pos, NodeType.END)

        return {
            "success": True,
            "message": f"Grid setup complete ({request.width}x{request.height})",
            "grid": current_grid.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Grid setup failed: {str(e)}")

@app.get("/grid/info")
async def get_grid_info():
    """Get current grid information."""
    if not current_grid:
        raise HTTPException(status_code=404, detail="No grid has been set up")

    return {
        "success": True,
        "grid": current_grid.to_dict()
    }

@app.post("/algorithm/run")
async def run_algorithm(request: AlgorithmRequest) -> AlgorithmResponse:
    """Run a pathfinding algorithm and return all steps."""
    if not current_grid:
        raise HTTPException(status_code=404, detail="No grid has been set up")

    if not current_grid.start_pos or not current_grid.end_pos:
        raise HTTPException(status_code=400, detail="Start and end positions must be set")

    try:
        # Select algorithm
        if request.algorithm.lower() == "astar":
            # Select heuristic function
            if request.heuristic == "euclidean":
                heuristic_func = lambda p1, p2: p1.euclidean_distance(p2)
            else:  # Default to Manhattan
                heuristic_func = lambda p1, p2: p1.manhattan_distance(p2)
            algorithm = AStarAlgorithm(current_grid, heuristic_func)
        elif request.algorithm.lower() == "dijkstra":
            algorithm = DijkstraAlgorithm(current_grid)
        elif request.algorithm.lower() == "bfs":
            algorithm = BreadthFirstSearch(current_grid)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown algorithm: {request.algorithm}")

        # Execute algorithm and collect all steps
        steps = []
        for step in algorithm.execute():
            steps.append(step.to_dict())

        return AlgorithmResponse(
            success=True,
            steps=steps,
            total_steps=len(steps),
            message=f"{request.algorithm} execution completed with {len(steps)} steps"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm execution failed: {str(e)}")

@app.post("/grid/update")
async def update_grid_cell(position: Dict[str, int], cell_type: str):
    """Update a single cell in the grid."""
    if not current_grid:
        raise HTTPException(status_code=404, detail="No grid has been set up")

    try:
        pos = Position(position["x"], position["y"])

        # Convert string to NodeType
        type_mapping = {
            "empty": NodeType.EMPTY,
            "obstacle": NodeType.OBSTACLE,
            "start": NodeType.START,
            "end": NodeType.END
        }

        if cell_type not in type_mapping:
            raise HTTPException(status_code=400, detail=f"Invalid cell type: {cell_type}")

        # Clear previous start/end if setting new ones
        if cell_type == "start" and current_grid.start_pos:
            current_grid.set_node_type(current_grid.start_pos, NodeType.EMPTY)
        elif cell_type == "end" and current_grid.end_pos:
            current_grid.set_node_type(current_grid.end_pos, NodeType.EMPTY)

        current_grid.set_node_type(pos, type_mapping[cell_type])

        return {
            "success": True,
            "message": f"Cell ({pos.x}, {pos.y}) updated to {cell_type}",
            "grid": current_grid.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Grid update failed: {str(e)}")

@app.get("/algorithms/info")
async def get_algorithm_info():
    """Get information about available algorithms."""
    return {
        "algorithms": {
            "astar": {
                "name": "A* Search",
                "description": "Optimal pathfinding using heuristic to guide search",
                "optimal": True,
                "complete": True,
                "heuristics": ["manhattan", "euclidean"]
            },
            "dijkstra": {
                "name": "Dijkstra's Algorithm",
                "description": "Optimal pathfinding using uniform cost search",
                "optimal": True,
                "complete": True,
                "heuristics": []
            },
            "bfs": {
                "name": "Breadth-First Search",
                "description": "Explores nodes level by level, guarantees shortest path",
                "optimal": True,
                "complete": True,
                "heuristics": []
            }
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)