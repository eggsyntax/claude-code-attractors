/**
 * Graph Algorithms Implementation
 * Provides graph data structures and pathfinding algorithms for educational visualization
 */

class Graph {
    constructor() {
        this.nodes = new Map(); // id -> {id, x, y, label}
        this.edges = new Map(); // "nodeId1-nodeId2" -> {from, to, weight}
        this.adjacencyList = new Map(); // nodeId -> [neighborIds]
    }

    /**
     * Add a node to the graph
     * @param {string} id - Unique identifier for the node
     * @param {number} x - X coordinate for visualization
     * @param {number} y - Y coordinate for visualization
     * @param {string} label - Display label for the node
     */
    addNode(id, x, y, label = id) {
        this.nodes.set(id, { id, x, y, label });
        this.adjacencyList.set(id, []);
    }

    /**
     * Add an edge between two nodes
     * @param {string} from - Source node id
     * @param {string} to - Target node id
     * @param {number} weight - Edge weight (default: 1)
     * @param {boolean} directed - Whether edge is directed (default: false)
     */
    addEdge(from, to, weight = 1, directed = false) {
        const edgeKey = `${from}-${to}`;
        this.edges.set(edgeKey, { from, to, weight });

        // Add to adjacency list
        if (!this.adjacencyList.has(from)) this.adjacencyList.set(from, []);
        if (!this.adjacencyList.has(to)) this.adjacencyList.set(to, []);

        this.adjacencyList.get(from).push(to);
        if (!directed) {
            this.adjacencyList.get(to).push(from);
            // Also store reverse edge for visualization
            const reverseKey = `${to}-${from}`;
            this.edges.set(reverseKey, { from: to, to: from, weight });
        }
    }

    /**
     * Get neighbors of a node
     * @param {string} nodeId - Node to get neighbors for
     * @returns {string[]} Array of neighbor node ids
     */
    getNeighbors(nodeId) {
        return this.adjacencyList.get(nodeId) || [];
    }

    /**
     * Get edge weight between two nodes
     * @param {string} from - Source node
     * @param {string} to - Target node
     * @returns {number} Edge weight, or Infinity if no edge exists
     */
    getEdgeWeight(from, to) {
        const edgeKey = `${from}-${to}`;
        const edge = this.edges.get(edgeKey);
        return edge ? edge.weight : Infinity;
    }

    /**
     * Create a grid-based maze graph
     * @param {number} rows - Number of rows
     * @param {number} cols - Number of columns
     * @param {number} cellSize - Size of each cell for visualization
     * @returns {Graph} Grid graph instance
     */
    static createGrid(rows, cols, cellSize = 40) {
        const graph = new Graph();

        // Add nodes
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const id = `${row}-${col}`;
                const x = col * cellSize + cellSize / 2;
                const y = row * cellSize + cellSize / 2;
                graph.addNode(id, x, y);
            }
        }

        // Add edges (4-connected grid)
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const currentId = `${row}-${col}`;

                // Connect to right neighbor
                if (col < cols - 1) {
                    const rightId = `${row}-${col + 1}`;
                    graph.addEdge(currentId, rightId);
                }

                // Connect to bottom neighbor
                if (row < rows - 1) {
                    const bottomId = `${row + 1}-${col}`;
                    graph.addEdge(currentId, bottomId);
                }
            }
        }

        return graph;
    }
}

/**
 * Breadth-First Search implementation with step tracking
 */
class BFSPathfinder {
    constructor(graph) {
        this.graph = graph;
        this.steps = [];
    }

    /**
     * Find path from start to end using BFS
     * @param {string} startId - Starting node id
     * @param {string} endId - Target node id
     * @returns {Object} Result containing path, steps, and statistics
     */
    findPath(startId, endId) {
        this.steps = [];
        const visited = new Set();
        const queue = [{ nodeId: startId, path: [startId] }];
        const parent = new Map();

        let nodesExplored = 0;

        while (queue.length > 0) {
            const { nodeId, path } = queue.shift();

            // Record step for visualization
            this.steps.push({
                type: 'visit',
                nodeId,
                queueState: [...queue.map(item => item.nodeId)],
                visitedNodes: [...visited],
                currentPath: [...path]
            });

            if (visited.has(nodeId)) continue;

            visited.add(nodeId);
            nodesExplored++;

            // Check if we reached the target
            if (nodeId === endId) {
                this.steps.push({
                    type: 'found',
                    nodeId,
                    finalPath: path,
                    nodesExplored
                });

                return {
                    path,
                    found: true,
                    steps: this.steps,
                    nodesExplored,
                    pathLength: path.length - 1
                };
            }

            // Add neighbors to queue
            const neighbors = this.graph.getNeighbors(nodeId);
            for (const neighborId of neighbors) {
                if (!visited.has(neighborId)) {
                    const newPath = [...path, neighborId];
                    queue.push({ nodeId: neighborId, path: newPath });
                    parent.set(neighborId, nodeId);
                }
            }
        }

        // No path found
        this.steps.push({
            type: 'no_path',
            nodesExplored
        });

        return {
            path: [],
            found: false,
            steps: this.steps,
            nodesExplored,
            pathLength: -1
        };
    }
}

/**
 * Depth-First Search implementation with step tracking
 */
class DFSPathfinder {
    constructor(graph) {
        this.graph = graph;
        this.steps = [];
    }

    /**
     * Find path from start to end using DFS
     * @param {string} startId - Starting node id
     * @param {string} endId - Target node id
     * @returns {Object} Result containing path, steps, and statistics
     */
    findPath(startId, endId) {
        this.steps = [];
        const visited = new Set();
        const stack = [{ nodeId: startId, path: [startId] }];

        let nodesExplored = 0;

        while (stack.length > 0) {
            const { nodeId, path } = stack.pop();

            // Record step for visualization
            this.steps.push({
                type: 'visit',
                nodeId,
                stackState: [...stack.map(item => item.nodeId)],
                visitedNodes: [...visited],
                currentPath: [...path]
            });

            if (visited.has(nodeId)) continue;

            visited.add(nodeId);
            nodesExplored++;

            // Check if we reached the target
            if (nodeId === endId) {
                this.steps.push({
                    type: 'found',
                    nodeId,
                    finalPath: path,
                    nodesExplored
                });

                return {
                    path,
                    found: true,
                    steps: this.steps,
                    nodesExplored,
                    pathLength: path.length - 1
                };
            }

            // Add neighbors to stack (in reverse order for consistent left-to-right exploration)
            const neighbors = this.graph.getNeighbors(nodeId).reverse();
            for (const neighborId of neighbors) {
                if (!visited.has(neighborId)) {
                    const newPath = [...path, neighborId];
                    stack.push({ nodeId: neighborId, path: newPath });
                }
            }
        }

        // No path found
        this.steps.push({
            type: 'no_path',
            nodesExplored
        });

        return {
            path: [],
            found: false,
            steps: this.steps,
            nodesExplored,
            pathLength: -1
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Graph, BFSPathfinder, DFSPathfinder };
}