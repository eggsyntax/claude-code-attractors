/**
 * Graph data structure for visualization
 */
class Graph {
    constructor() {
        this.nodes = {};
        this.edges = [];
    }

    addNode(id, x, y) {
        this.nodes[id] = { x, y, connections: [] };
    }

    addEdge(from, to, weight = 1) {
        if (!this.nodes[from] || !this.nodes[to]) {
            throw new Error('Both nodes must exist before adding edge');
        }

        this.nodes[from].connections.push(to);
        this.nodes[to].connections.push(from);
        this.edges.push({ from, to, weight });
    }

    getNodes() {
        return Object.keys(this.nodes);
    }

    getEdges() {
        return this.edges;
    }

    getNeighbors(node) {
        return this.nodes[node]?.connections || [];
    }

    getEdgeWeight(from, to) {
        const edge = this.edges.find(e =>
            (e.from === from && e.to === to) || (e.from === to && e.to === from)
        );
        return edge ? edge.weight : Infinity;
    }
}

/**
 * Graph Algorithm Implementations
 * Provides step-by-step implementations of popular graph algorithms for educational visualization
 */

class GraphAlgorithms {
    /**
     * Creates a sample graph for demonstration purposes
     * Returns a Graph instance with nodes and weighted edges
     */
    static createSampleGraph() {
        const graph = new Graph();

        // Add nodes with positions
        graph.addNode('A', 100, 100);
        graph.addNode('B', 250, 50);
        graph.addNode('C', 250, 150);
        graph.addNode('D', 400, 50);
        graph.addNode('E', 400, 100);
        graph.addNode('F', 400, 200);
        graph.addNode('G', 550, 100);

        // Add weighted edges
        graph.addEdge('A', 'B', 4);
        graph.addEdge('A', 'C', 2);
        graph.addEdge('B', 'D', 5);
        graph.addEdge('B', 'E', 3);
        graph.addEdge('C', 'F', 7);
        graph.addEdge('D', 'G', 2);
        graph.addEdge('E', 'F', 1);
        graph.addEdge('E', 'G', 4);

        return graph;
    }

    /**
     * Breadth-First Search (BFS) implementation
     * Returns steps for visualization showing the exploration process
     */
    static* breadthFirstSearch(graph, startNode) {
        const visited = new Set();
        const queue = [startNode];
        const steps = [];
        let stepCount = 0;

        yield {
            step: stepCount++,
            type: 'start',
            description: `Starting BFS from node ${startNode}`,
            currentNode: startNode,
            queue: [...queue],
            visited: [...visited],
            action: 'initialize'
        };

        while (queue.length > 0) {
            const currentNode = queue.shift();

            if (visited.has(currentNode)) {
                continue;
            }

            // Mark as visited
            visited.add(currentNode);

            yield {
                step: stepCount++,
                type: 'visit',
                description: `Visiting node ${currentNode}`,
                currentNode,
                queue: [...queue],
                visited: [...visited],
                action: 'visit'
            };

            // Add neighbors to queue
            const neighbors = graph.getNeighbors(currentNode).filter(neighbor => !visited.has(neighbor));

            for (const neighbor of neighbors) {
                if (!queue.includes(neighbor)) {
                    queue.push(neighbor);

                    yield {
                        step: stepCount++,
                        type: 'discover',
                        description: `Discovered node ${neighbor}, added to queue`,
                        currentNode,
                        discoveredNode: neighbor,
                        queue: [...queue],
                        visited: [...visited],
                        action: 'discover'
                    };
                }
            }
        }

        yield {
            step: stepCount++,
            type: 'complete',
            description: 'BFS traversal complete!',
            visited: [...visited],
            queue: [],
            action: 'complete'
        };
    }

    /**
     * Depth-First Search (DFS) implementation
     * Returns steps for visualization showing the exploration process
     */
    static* depthFirstSearch(graph, startNode) {
        const visited = new Set();
        const stack = [startNode];
        let stepCount = 0;

        yield {
            step: stepCount++,
            type: 'start',
            description: `Starting DFS from node ${startNode}`,
            currentNode: startNode,
            stack: [...stack],
            visited: [...visited],
            action: 'initialize'
        };

        while (stack.length > 0) {
            const currentNode = stack.pop();

            if (visited.has(currentNode)) {
                continue;
            }

            // Mark as visited
            visited.add(currentNode);

            yield {
                step: stepCount++,
                type: 'visit',
                description: `Visiting node ${currentNode}`,
                currentNode,
                stack: [...stack],
                visited: [...visited],
                action: 'visit'
            };

            // Add neighbors to stack (in reverse order for consistent traversal)
            const neighbors = graph.getNeighbors(currentNode)
                .filter(neighbor => !visited.has(neighbor))
                .reverse();

            for (const neighbor of neighbors) {
                if (!stack.includes(neighbor)) {
                    stack.push(neighbor);

                    yield {
                        step: stepCount++,
                        type: 'discover',
                        description: `Discovered node ${neighbor}, added to stack`,
                        currentNode,
                        discoveredNode: neighbor,
                        stack: [...stack],
                        visited: [...visited],
                        action: 'discover'
                    };
                }
            }
        }

        yield {
            step: stepCount++,
            type: 'complete',
            description: 'DFS traversal complete!',
            visited: [...visited],
            stack: [],
            action: 'complete'
        };
    }

    /**
     * Dijkstra's Shortest Path Algorithm
     * Finds shortest path between start and end nodes
     */
    static* dijkstraShortestPath(graph, startNode, endNode) {
        const distances = {};
        const previous = {};
        const unvisited = new Set();
        let stepCount = 0;

        // Initialize distances
        for (const node of graph.getNodes()) {
            distances[node] = node === startNode ? 0 : Infinity;
            previous[node] = null;
            unvisited.add(node);
        }

        yield {
            step: stepCount++,
            type: 'start',
            description: `Starting Dijkstra's algorithm from ${startNode} to ${endNode}`,
            distances: {...distances},
            unvisited: [...unvisited],
            currentNode: startNode,
            action: 'initialize'
        };

        while (unvisited.size > 0) {
            // Find unvisited node with minimum distance
            let currentNode = null;
            let minDistance = Infinity;

            for (const node of unvisited) {
                if (distances[node] < minDistance) {
                    minDistance = distances[node];
                    currentNode = node;
                }
            }

            if (currentNode === null || distances[currentNode] === Infinity) {
                break; // No more reachable nodes
            }

            unvisited.delete(currentNode);

            yield {
                step: stepCount++,
                type: 'visit',
                description: `Processing node ${currentNode} with distance ${distances[currentNode]}`,
                currentNode,
                distances: {...distances},
                unvisited: [...unvisited],
                action: 'visit'
            };

            // Update distances to neighbors
            const currentDistance = distances[currentNode];
            const neighbors = graph.getNeighbors(currentNode);

            for (const neighbor of neighbors) {
                if (unvisited.has(neighbor)) {
                    const weight = graph.getEdgeWeight(currentNode, neighbor);
                    const newDistance = currentDistance + weight;

                    if (newDistance < distances[neighbor]) {
                        const oldDistance = distances[neighbor];
                        distances[neighbor] = newDistance;
                        previous[neighbor] = currentNode;

                        yield {
                            step: stepCount++,
                            type: 'update',
                            description: `Updated distance to ${neighbor}: ${newDistance}`,
                            currentNode,
                            updatedNode: neighbor,
                            oldDistance,
                            newDistance,
                            distances: {...distances},
                            unvisited: [...unvisited],
                            action: 'update'
                        };
                    }
                }
            }

            // Check if we reached the target
            if (currentNode === endNode) {
                break;
            }
        }

        // Reconstruct path
        const path = [];
        let currentNode = endNode;

        while (currentNode !== null) {
            path.unshift(currentNode);
            currentNode = previous[currentNode];
        }

        yield {
            step: stepCount++,
            type: 'complete',
            description: `Shortest path found! Distance: ${distances[endNode]}`,
            path,
            totalDistance: distances[endNode],
            distances: {...distances},
            action: 'complete'
        };
    }

    /**
     * A* Pathfinding Algorithm
     * Uses heuristics to find optimal path more efficiently
     */
    static* aStarPathfinding(graph, startNode, endNode) {
        const openSet = [startNode];
        const closedSet = new Set();
        const gScore = {}; // Cost from start
        const fScore = {}; // g + heuristic
        const cameFrom = {};
        let stepCount = 0;

        // Initialize scores
        for (const node of graph.getNodes()) {
            gScore[node] = node === startNode ? 0 : Infinity;
            fScore[node] = node === startNode ? this.heuristic(graph, startNode, endNode) : Infinity;
        }

        yield {
            step: stepCount++,
            type: 'start',
            description: `Starting A* pathfinding from ${startNode} to ${endNode}`,
            openSet: [...openSet],
            closedSet: [...closedSet],
            gScore: {...gScore},
            fScore: {...fScore},
            currentNode: startNode,
            action: 'initialize'
        };

        while (openSet.length > 0) {
            // Get node with lowest fScore
            let currentNode = openSet[0];
            for (const node of openSet) {
                if (fScore[node] < fScore[currentNode]) {
                    currentNode = node;
                }
            }

            // Remove current from openSet
            const currentIndex = openSet.indexOf(currentNode);
            openSet.splice(currentIndex, 1);
            closedSet.add(currentNode);

            yield {
                step: stepCount++,
                type: 'visit',
                description: `Processing node ${currentNode} (f=${fScore[currentNode].toFixed(1)})`,
                currentNode,
                openSet: [...openSet],
                closedSet: [...closedSet],
                gScore: {...gScore},
                fScore: {...fScore},
                action: 'visit'
            };

            // Check if we reached the goal
            if (currentNode === endNode) {
                const path = this.reconstructPath(cameFrom, currentNode);
                yield {
                    step: stepCount++,
                    type: 'complete',
                    description: `Path found! Total cost: ${gScore[endNode].toFixed(1)}`,
                    path,
                    totalCost: gScore[endNode],
                    action: 'complete'
                };
                return;
            }

            // Check neighbors
            const neighbors = graph.getNeighbors(currentNode);
            for (const neighbor of neighbors) {
                if (!closedSet.has(neighbor)) {
                    const weight = graph.getEdgeWeight(currentNode, neighbor);
                    const tentativeGScore = gScore[currentNode] + weight;

                    if (!openSet.includes(neighbor)) {
                        openSet.push(neighbor);
                    } else if (tentativeGScore >= gScore[neighbor]) {
                        continue;
                    }

                    cameFrom[neighbor] = currentNode;
                    gScore[neighbor] = tentativeGScore;
                    fScore[neighbor] = gScore[neighbor] + this.heuristic(graph, neighbor, endNode);

                    yield {
                        step: stepCount++,
                        type: 'update',
                        description: `Updated node ${neighbor} (g=${gScore[neighbor].toFixed(1)}, f=${fScore[neighbor].toFixed(1)})`,
                        currentNode,
                        updatedNode: neighbor,
                        openSet: [...openSet],
                        closedSet: [...closedSet],
                        gScore: {...gScore},
                        fScore: {...fScore},
                        action: 'update'
                    };
                }
            }
        }

        yield {
            step: stepCount++,
            type: 'complete',
            description: 'No path found!',
            action: 'complete'
        };
    }

    /**
     * Simple heuristic function (Euclidean distance)
     * Used by A* algorithm
     */
    static heuristic(graph, nodeA, nodeB) {
        const posA = graph.nodes[nodeA];
        const posB = graph.nodes[nodeB];
        const dx = posA.x - posB.x;
        const dy = posA.y - posB.y;
        return Math.sqrt(dx * dx + dy * dy) / 50; // Scale down for reasonable values
    }

    /**
     * Reconstructs path from the cameFrom array
     * Used by A* algorithm
     */
    static reconstructPath(cameFrom, current) {
        const path = [current];
        while (cameFrom[current] !== undefined) {
            current = cameFrom[current];
            path.unshift(current);
        }
        return path;
    }
}

// Export for Node.js testing environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Graph, GraphAlgorithms };
}