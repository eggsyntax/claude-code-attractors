// Pathfinding Algorithm Implementations
// Created by Dave for collaborative visualization with Tara

// Utility functions
class PriorityQueue {
    constructor() {
        this.items = [];
    }

    enqueue(element, priority) {
        this.items.push({ element, priority });
        this.items.sort((a, b) => a.priority - b.priority);
    }

    dequeue() {
        return this.items.shift()?.element;
    }

    isEmpty() {
        return this.items.length === 0;
    }
}

class Queue {
    constructor() {
        this.items = [];
    }

    enqueue(element) {
        this.items.push(element);
    }

    dequeue() {
        return this.items.shift();
    }

    isEmpty() {
        return this.items.length === 0;
    }
}

class Stack {
    constructor() {
        this.items = [];
    }

    push(element) {
        this.items.push(element);
    }

    pop() {
        return this.items.pop();
    }

    isEmpty() {
        return this.items.length === 0;
    }
}

// Helper functions
function getNeighbors(x, y, width, height) {
    const neighbors = [];
    const directions = [
        [-1, 0], [1, 0], [0, -1], [0, 1] // up, down, left, right
    ];

    for (const [dx, dy] of directions) {
        const newX = x + dx;
        const newY = y + dy;
        if (newX >= 0 && newX < width && newY >= 0 && newY < height) {
            neighbors.push({ x: newX, y: newY });
        }
    }
    return neighbors;
}

function manhattanDistance(a, b) {
    return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}

function reconstructPath(cameFrom, current) {
    const path = [];
    while (current) {
        path.unshift(current);
        current = cameFrom.get(`${current.x},${current.y}`);
    }
    return path;
}

// A* Algorithm
async function astar(visualizer, algorithmName) {
    const start = visualizer.getStartPosition();
    const end = visualizer.getEndPosition();
    const delay = () => new Promise(resolve => setTimeout(resolve, visualizer.getAnimationSpeed()));

    if (!start || !end) {
        return { path: [], nodesExplored: 0, success: false };
    }

    const openSet = new PriorityQueue();
    const closedSet = new Set();
    const cameFrom = new Map();
    const gScore = new Map();
    const fScore = new Map();

    const startKey = `${start.x},${start.y}`;
    const endKey = `${end.x},${end.y}`;

    gScore.set(startKey, 0);
    fScore.set(startKey, manhattanDistance(start, end));
    openSet.enqueue(start, fScore.get(startKey));

    let nodesExplored = 0;

    while (!openSet.isEmpty()) {
        const current = openSet.dequeue();
        const currentKey = `${current.x},${current.y}`;

        if (currentKey === endKey) {
            const path = reconstructPath(cameFrom, current);
            // Mark the final path
            for (const cell of path) {
                await visualizer.markCellAsPath(cell.x, cell.y, algorithmName);
                await delay();
            }
            return { path, nodesExplored, success: true };
        }

        closedSet.add(currentKey);
        await visualizer.markCellAsExplored(current.x, current.y, algorithmName);
        await visualizer.markCellAsCurrent(current.x, current.y, algorithmName);
        await delay();
        nodesExplored++;

        const neighbors = getNeighbors(current.x, current.y, visualizer.width, visualizer.height);

        for (const neighbor of neighbors) {
            const neighborKey = `${neighbor.x},${neighbor.y}`;

            if (!visualizer.isValidCell(neighbor.x, neighbor.y) || closedSet.has(neighborKey)) {
                continue;
            }

            const tentativeGScore = gScore.get(currentKey) + 1;

            if (!gScore.has(neighborKey) || tentativeGScore < gScore.get(neighborKey)) {
                cameFrom.set(neighborKey, current);
                gScore.set(neighborKey, tentativeGScore);
                fScore.set(neighborKey, tentativeGScore + manhattanDistance(neighbor, end));
                openSet.enqueue(neighbor, fScore.get(neighborKey));
            }
        }
    }

    return { path: [], nodesExplored, success: false };
}

// Dijkstra's Algorithm
async function dijkstra(visualizer, algorithmName) {
    const start = visualizer.getStartPosition();
    const end = visualizer.getEndPosition();
    const delay = () => new Promise(resolve => setTimeout(resolve, visualizer.getAnimationSpeed()));

    if (!start || !end) {
        return { path: [], nodesExplored: 0, success: false };
    }

    const distances = new Map();
    const previous = new Map();
    const unvisited = new PriorityQueue();
    const visited = new Set();

    const startKey = `${start.x},${start.y}`;
    const endKey = `${end.x},${end.y}`;

    distances.set(startKey, 0);
    unvisited.enqueue(start, 0);

    let nodesExplored = 0;

    while (!unvisited.isEmpty()) {
        const current = unvisited.dequeue();
        const currentKey = `${current.x},${current.y}`;

        if (visited.has(currentKey)) continue;
        visited.add(currentKey);

        if (currentKey === endKey) {
            const path = reconstructPath(previous, current);
            // Mark the final path
            for (const cell of path) {
                await visualizer.markCellAsPath(cell.x, cell.y, algorithmName);
                await delay();
            }
            return { path, nodesExplored, success: true };
        }

        await visualizer.markCellAsExplored(current.x, current.y, algorithmName);
        await visualizer.markCellAsCurrent(current.x, current.y, algorithmName);
        await delay();
        nodesExplored++;

        const neighbors = getNeighbors(current.x, current.y, visualizer.width, visualizer.height);

        for (const neighbor of neighbors) {
            const neighborKey = `${neighbor.x},${neighbor.y}`;

            if (!visualizer.isValidCell(neighbor.x, neighbor.y) || visited.has(neighborKey)) {
                continue;
            }

            const newDistance = distances.get(currentKey) + 1;

            if (!distances.has(neighborKey) || newDistance < distances.get(neighborKey)) {
                distances.set(neighborKey, newDistance);
                previous.set(neighborKey, current);
                unvisited.enqueue(neighbor, newDistance);
            }
        }
    }

    return { path: [], nodesExplored, success: false };
}

// Breadth-First Search (BFS)
async function bfs(visualizer, algorithmName) {
    const start = visualizer.getStartPosition();
    const end = visualizer.getEndPosition();
    const delay = () => new Promise(resolve => setTimeout(resolve, visualizer.getAnimationSpeed()));

    if (!start || !end) {
        return { path: [], nodesExplored: 0, success: false };
    }

    const queue = new Queue();
    const visited = new Set();
    const previous = new Map();

    const startKey = `${start.x},${start.y}`;
    const endKey = `${end.x},${end.y}`;

    queue.enqueue(start);
    visited.add(startKey);

    let nodesExplored = 0;

    while (!queue.isEmpty()) {
        const current = queue.dequeue();
        const currentKey = `${current.x},${current.y}`;

        if (currentKey === endKey) {
            const path = reconstructPath(previous, current);
            // Mark the final path
            for (const cell of path) {
                await visualizer.markCellAsPath(cell.x, cell.y, algorithmName);
                await delay();
            }
            return { path, nodesExplored, success: true };
        }

        await visualizer.markCellAsExplored(current.x, current.y, algorithmName);
        await visualizer.markCellAsCurrent(current.x, current.y, algorithmName);
        await delay();
        nodesExplored++;

        const neighbors = getNeighbors(current.x, current.y, visualizer.width, visualizer.height);

        for (const neighbor of neighbors) {
            const neighborKey = `${neighbor.x},${neighbor.y}`;

            if (!visualizer.isValidCell(neighbor.x, neighbor.y) || visited.has(neighborKey)) {
                continue;
            }

            visited.add(neighborKey);
            previous.set(neighborKey, current);
            queue.enqueue(neighbor);
        }
    }

    return { path: [], nodesExplored, success: false };
}

// Depth-First Search (DFS)
async function dfs(visualizer, algorithmName) {
    const start = visualizer.getStartPosition();
    const end = visualizer.getEndPosition();
    const delay = () => new Promise(resolve => setTimeout(resolve, visualizer.getAnimationSpeed()));

    if (!start || !end) {
        return { path: [], nodesExplored: 0, success: false };
    }

    const stack = new Stack();
    const visited = new Set();
    const previous = new Map();

    const startKey = `${start.x},${start.y}`;
    const endKey = `${end.x},${end.y}`;

    stack.push(start);

    let nodesExplored = 0;

    while (!stack.isEmpty()) {
        const current = stack.pop();
        const currentKey = `${current.x},${current.y}`;

        if (visited.has(currentKey)) continue;
        visited.add(currentKey);

        if (currentKey === endKey) {
            const path = reconstructPath(previous, current);
            // Mark the final path
            for (const cell of path) {
                await visualizer.markCellAsPath(cell.x, cell.y, algorithmName);
                await delay();
            }
            return { path, nodesExplored, success: true };
        }

        await visualizer.markCellAsExplored(current.x, current.y, algorithmName);
        await visualizer.markCellAsCurrent(current.x, current.y, algorithmName);
        await delay();
        nodesExplored++;

        const neighbors = getNeighbors(current.x, current.y, visualizer.width, visualizer.height);

        // Shuffle neighbors for more interesting DFS visualization
        for (let i = neighbors.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [neighbors[i], neighbors[j]] = [neighbors[j], neighbors[i]];
        }

        for (const neighbor of neighbors) {
            const neighborKey = `${neighbor.x},${neighbor.y}`;

            if (!visualizer.isValidCell(neighbor.x, neighbor.y) || visited.has(neighborKey)) {
                continue;
            }

            previous.set(neighborKey, current);
            stack.push(neighbor);
        }
    }

    return { path: [], nodesExplored, success: false };
}

// Export all algorithms
window.pathfindingAlgorithms = {
    astar,
    dijkstra,
    bfs,
    dfs
};

console.log('🚀 Pathfinding algorithms loaded! Ready for visualization racing!');