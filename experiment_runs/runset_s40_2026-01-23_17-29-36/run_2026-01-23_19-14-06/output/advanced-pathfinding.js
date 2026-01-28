/**
 * Advanced Pathfinding Algorithms Implementation
 * Provides Dijkstra's and A* algorithms with comprehensive step tracking
 * Integrates with the existing Graph class from graph-algorithms.js
 */

/**
 * Dijkstra's Shortest Path Algorithm with Educational Step Tracking
 */
class DijkstraPathfinder {
    constructor(graph) {
        this.graph = graph;
        this.steps = [];
    }

    /**
     * Find shortest path using Dijkstra's algorithm
     * @param {string} startId - Starting node id
     * @param {string} endId - Target node id
     * @returns {Object} Result containing path, steps, and statistics
     */
    findPath(startId, endId) {
        this.steps = [];
        const distances = new Map();
        const previous = new Map();
        const unvisited = new Set();
        const priorityQueue = [];

        let nodesExplored = 0;

        // Initialize distances and unvisited set
        for (const [nodeId] of this.graph.nodes) {
            distances.set(nodeId, nodeId === startId ? 0 : Infinity);
            previous.set(nodeId, null);
            unvisited.add(nodeId);
        }

        // Add initial step
        this.steps.push({
            type: 'initialize',
            description: `Initializing Dijkstra's algorithm from ${startId} to ${endId}`,
            distances: new Map(distances),
            unvisited: new Set(unvisited),
            currentNode: startId,
            priorityQueue: []
        });

        // Add start node to priority queue
        priorityQueue.push({ nodeId: startId, distance: 0 });

        while (unvisited.size > 0 && priorityQueue.length > 0) {
            // Sort priority queue and get node with minimum distance
            priorityQueue.sort((a, b) => a.distance - b.distance);
            const current = priorityQueue.shift();

            if (!current || !unvisited.has(current.nodeId)) continue;

            const currentNode = current.nodeId;
            const currentDistance = distances.get(currentNode);

            // Mark as visited
            unvisited.delete(currentNode);
            nodesExplored++;

            this.steps.push({
                type: 'visit',
                description: `Visiting node ${currentNode} with distance ${currentDistance}`,
                currentNode,
                distances: new Map(distances),
                unvisited: new Set(unvisited),
                priorityQueue: [...priorityQueue]
            });

            // If we reached the target, we can stop
            if (currentNode === endId) {
                break;
            }

            // Update distances to neighbors
            const neighbors = this.graph.getNeighbors(currentNode);

            for (const neighborId of neighbors) {
                if (unvisited.has(neighborId)) {
                    const weight = this.graph.getEdgeWeight(currentNode, neighborId);
                    const newDistance = currentDistance + weight;
                    const oldDistance = distances.get(neighborId);

                    if (newDistance < oldDistance) {
                        distances.set(neighborId, newDistance);
                        previous.set(neighborId, currentNode);

                        // Update priority queue
                        const existingIndex = priorityQueue.findIndex(item => item.nodeId === neighborId);
                        if (existingIndex !== -1) {
                            priorityQueue[existingIndex].distance = newDistance;
                        } else {
                            priorityQueue.push({ nodeId: neighborId, distance: newDistance });
                        }

                        this.steps.push({
                            type: 'update',
                            description: `Updated distance to ${neighborId}: ${oldDistance} → ${newDistance}`,
                            currentNode,
                            updatedNode: neighborId,
                            oldDistance: oldDistance === Infinity ? '∞' : oldDistance,
                            newDistance,
                            weight,
                            distances: new Map(distances),
                            priorityQueue: [...priorityQueue]
                        });
                    }
                }
            }
        }

        // Reconstruct path
        const path = this.reconstructPath(previous, endId);
        const totalDistance = distances.get(endId);
        const pathFound = totalDistance !== Infinity;

        this.steps.push({
            type: 'complete',
            description: pathFound
                ? `Shortest path found! Total distance: ${totalDistance}`
                : 'No path exists between these nodes',
            finalPath: path,
            totalDistance: pathFound ? totalDistance : -1,
            nodesExplored,
            pathFound
        });

        return {
            path: pathFound ? path : [],
            found: pathFound,
            steps: this.steps,
            nodesExplored,
            pathLength: pathFound ? path.length - 1 : -1,
            totalDistance: pathFound ? totalDistance : -1
        };
    }

    /**
     * Reconstruct path from previous nodes map
     * @param {Map} previous - Previous nodes mapping
     * @param {string} endId - Target node id
     * @returns {string[]} Path from start to end
     */
    reconstructPath(previous, endId) {
        const path = [];
        let currentNode = endId;

        while (currentNode !== null) {
            path.unshift(currentNode);
            currentNode = previous.get(currentNode);
        }

        return path.length > 1 || path[0] === endId ? path : [];
    }
}

/**
 * A* Pathfinding Algorithm with Educational Step Tracking
 */
class AStarPathfinder {
    constructor(graph) {
        this.graph = graph;
        this.steps = [];
    }

    /**
     * Find optimal path using A* algorithm
     * @param {string} startId - Starting node id
     * @param {string} endId - Target node id
     * @returns {Object} Result containing path, steps, and statistics
     */
    findPath(startId, endId) {
        this.steps = [];
        const openSet = [startId];
        const closedSet = new Set();
        const gScore = new Map(); // Cost from start
        const fScore = new Map(); // g + heuristic
        const cameFrom = new Map();

        let nodesExplored = 0;

        // Initialize scores
        for (const [nodeId] of this.graph.nodes) {
            gScore.set(nodeId, nodeId === startId ? 0 : Infinity);
            const heuristic = this.heuristicDistance(nodeId, endId);
            fScore.set(nodeId, nodeId === startId ? heuristic : Infinity);
        }

        this.steps.push({
            type: 'initialize',
            description: `Initializing A* pathfinding from ${startId} to ${endId}`,
            openSet: [...openSet],
            closedSet: new Set(closedSet),
            gScore: new Map(gScore),
            fScore: new Map(fScore),
            currentNode: startId,
            heuristic: this.heuristicDistance(startId, endId)
        });

        while (openSet.length > 0) {
            // Get node with lowest fScore
            let currentNode = openSet.reduce((best, node) =>
                fScore.get(node) < fScore.get(best) ? node : best
            );

            // Remove current from openSet and add to closedSet
            const currentIndex = openSet.indexOf(currentNode);
            openSet.splice(currentIndex, 1);
            closedSet.add(currentNode);
            nodesExplored++;

            const currentG = gScore.get(currentNode);
            const currentF = fScore.get(currentNode);
            const currentH = currentF - currentG;

            this.steps.push({
                type: 'visit',
                description: `Processing ${currentNode}: g=${currentG.toFixed(1)}, h=${currentH.toFixed(1)}, f=${currentF.toFixed(1)}`,
                currentNode,
                openSet: [...openSet],
                closedSet: new Set(closedSet),
                gScore: new Map(gScore),
                fScore: new Map(fScore),
                gValue: currentG,
                hValue: currentH,
                fValue: currentF
            });

            // Check if we reached the goal
            if (currentNode === endId) {
                const path = this.reconstructPath(cameFrom, currentNode);

                this.steps.push({
                    type: 'complete',
                    description: `Optimal path found! Total cost: ${gScore.get(endId).toFixed(1)}`,
                    finalPath: path,
                    totalCost: gScore.get(endId),
                    nodesExplored
                });

                return {
                    path,
                    found: true,
                    steps: this.steps,
                    nodesExplored,
                    pathLength: path.length - 1,
                    totalDistance: gScore.get(endId)
                };
            }

            // Check neighbors
            const neighbors = this.graph.getNeighbors(currentNode);
            for (const neighbor of neighbors) {
                if (closedSet.has(neighbor)) continue;

                const weight = this.graph.getEdgeWeight(currentNode, neighbor);
                const tentativeGScore = gScore.get(currentNode) + weight;

                // If this path to neighbor is better than any previous one
                if (tentativeGScore < gScore.get(neighbor)) {
                    const oldG = gScore.get(neighbor);
                    const oldF = fScore.get(neighbor);

                    cameFrom.set(neighbor, currentNode);
                    gScore.set(neighbor, tentativeGScore);
                    const heuristic = this.heuristicDistance(neighbor, endId);
                    fScore.set(neighbor, tentativeGScore + heuristic);

                    if (!openSet.includes(neighbor)) {
                        openSet.push(neighbor);
                    }

                    this.steps.push({
                        type: 'update',
                        description: `Updated ${neighbor}: g=${oldG === Infinity ? '∞' : oldG.toFixed(1)} → ${tentativeGScore.toFixed(1)}, f=${oldF === Infinity ? '∞' : oldF.toFixed(1)} → ${fScore.get(neighbor).toFixed(1)}`,
                        currentNode,
                        updatedNode: neighbor,
                        oldG: oldG === Infinity ? Infinity : oldG,
                        newG: tentativeGScore,
                        newH: heuristic,
                        newF: fScore.get(neighbor),
                        weight,
                        openSet: [...openSet],
                        closedSet: new Set(closedSet)
                    });
                }
            }
        }

        // No path found
        this.steps.push({
            type: 'complete',
            description: 'No path found!',
            nodesExplored
        });

        return {
            path: [],
            found: false,
            steps: this.steps,
            nodesExplored,
            pathLength: -1,
            totalDistance: -1
        };
    }

    /**
     * Calculate Euclidean distance heuristic
     * @param {string} nodeA - First node id
     * @param {string} nodeB - Second node id
     * @returns {number} Heuristic distance
     */
    heuristicDistance(nodeA, nodeB) {
        const nodeAData = this.graph.nodes.get(nodeA);
        const nodeBData = this.graph.nodes.get(nodeB);

        if (!nodeAData || !nodeBData) return 0;

        const dx = nodeAData.x - nodeBData.x;
        const dy = nodeAData.y - nodeBData.y;
        return Math.sqrt(dx * dx + dy * dy) / 50; // Scale down for reasonable values
    }

    /**
     * Reconstruct path from cameFrom map
     * @param {Map} cameFrom - Parent nodes mapping
     * @param {string} current - Current node
     * @returns {string[]} Path from start to current
     */
    reconstructPath(cameFrom, current) {
        const path = [current];
        while (cameFrom.has(current)) {
            current = cameFrom.get(current);
            path.unshift(current);
        }
        return path;
    }
}

/**
 * Algorithm Performance Analyzer
 * Provides comparative analysis of different pathfinding algorithms
 */
class PathfindingAnalyzer {
    constructor() {
        this.results = new Map();
    }

    /**
     * Analyze and compare algorithm performance
     * @param {string} algorithmName - Name of the algorithm
     * @param {Object} result - Algorithm result object
     */
    addResult(algorithmName, result) {
        this.results.set(algorithmName, {
            ...result,
            timestamp: Date.now()
        });
    }

    /**
     * Get comparative performance summary
     * @returns {Object} Performance comparison data
     */
    getComparison() {
        const algorithms = Array.from(this.results.keys());
        const comparison = {
            algorithms,
            metrics: {
                pathFound: {},
                pathLength: {},
                totalDistance: {},
                nodesExplored: {},
                efficiency: {}
            }
        };

        for (const algo of algorithms) {
            const result = this.results.get(algo);
            comparison.metrics.pathFound[algo] = result.found;
            comparison.metrics.pathLength[algo] = result.pathLength;
            comparison.metrics.totalDistance[algo] = result.totalDistance || -1;
            comparison.metrics.nodesExplored[algo] = result.nodesExplored;
            comparison.metrics.efficiency[algo] = result.found ?
                (result.pathLength / result.nodesExplored * 100).toFixed(1) + '%' : 'N/A';
        }

        return comparison;
    }

    /**
     * Clear all stored results
     */
    clear() {
        this.results.clear();
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DijkstraPathfinder,
        AStarPathfinder,
        PathfindingAnalyzer
    };
}