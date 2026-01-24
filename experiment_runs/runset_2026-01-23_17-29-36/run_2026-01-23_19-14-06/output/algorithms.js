/**
 * Algorithm implementations for the Visual Algorithm Explorer
 * Each algorithm returns steps for visualization and final metrics
 */

class SortingAlgorithms {
    /**
     * Creates a deep copy of an array
     */
    static copyArray(arr) {
        return [...arr];
    }

    /**
     * Bubble Sort: Repeatedly swap adjacent elements if they're in wrong order
     * Time Complexity: O(n²) average and worst case, O(n) best case
     * Space Complexity: O(1)
     */
    static bubbleSort(array) {
        const arr = this.copyArray(array);
        const steps = [];
        const n = arr.length;
        let comparisons = 0;
        let swaps = 0;

        for (let i = 0; i < n - 1; i++) {
            let swappedInThisPass = false;

            for (let j = 0; j < n - i - 1; j++) {
                comparisons++;

                // Add comparison step
                steps.push({
                    type: 'compare',
                    indices: [j, j + 1],
                    array: this.copyArray(arr),
                    comparisons,
                    swaps,
                    description: `Comparing elements at positions ${j} and ${j + 1}: ${arr[j]} vs ${arr[j + 1]}`
                });

                if (arr[j] > arr[j + 1]) {
                    // Swap elements
                    [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
                    swaps++;
                    swappedInThisPass = true;

                    // Add swap step
                    steps.push({
                        type: 'swap',
                        indices: [j, j + 1],
                        array: this.copyArray(arr),
                        comparisons,
                        swaps,
                        description: `Swapping ${arr[j + 1]} and ${arr[j]} (positions ${j} and ${j + 1})`
                    });
                }
            }

            // Mark the last i elements as sorted
            steps.push({
                type: 'mark_sorted',
                indices: [n - i - 1],
                array: this.copyArray(arr),
                comparisons,
                swaps,
                description: `Element at position ${n - i - 1} is now in its final sorted position`
            });

            // Early termination if no swaps were made
            if (!swappedInThisPass) {
                break;
            }
        }

        // Mark all elements as sorted
        steps.push({
            type: 'complete',
            indices: Array.from({length: n}, (_, i) => i),
            array: this.copyArray(arr),
            comparisons,
            swaps,
            description: 'Bubble sort complete! All elements are now sorted.'
        });

        return {
            steps,
            finalArray: arr,
            metrics: { comparisons, swaps },
            timeComplexity: 'O(n²)',
            spaceComplexity: 'O(1)'
        };
    }

    /**
     * Insertion Sort: Build sorted array one item at a time
     * Time Complexity: O(n²) average and worst case, O(n) best case
     * Space Complexity: O(1)
     */
    static insertionSort(array) {
        const arr = this.copyArray(array);
        const steps = [];
        const n = arr.length;
        let comparisons = 0;
        let swaps = 0;

        // First element is considered sorted
        steps.push({
            type: 'mark_sorted',
            indices: [0],
            array: this.copyArray(arr),
            comparisons,
            swaps,
            description: 'First element is trivially sorted'
        });

        for (let i = 1; i < n; i++) {
            const key = arr[i];
            let j = i - 1;

            steps.push({
                type: 'select',
                indices: [i],
                array: this.copyArray(arr),
                comparisons,
                swaps,
                description: `Selecting element ${key} at position ${i} to insert into sorted portion`
            });

            // Move elements that are greater than key one position ahead
            while (j >= 0) {
                comparisons++;

                steps.push({
                    type: 'compare',
                    indices: [j, i],
                    array: this.copyArray(arr),
                    comparisons,
                    swaps,
                    description: `Comparing ${arr[j]} with ${key}`
                });

                if (arr[j] <= key) {
                    break;
                }

                arr[j + 1] = arr[j];
                swaps++;

                steps.push({
                    type: 'shift',
                    indices: [j, j + 1],
                    array: this.copyArray(arr),
                    comparisons,
                    swaps,
                    description: `Shifting ${arr[j]} one position right`
                });

                j--;
            }

            arr[j + 1] = key;

            steps.push({
                type: 'insert',
                indices: [j + 1],
                array: this.copyArray(arr),
                comparisons,
                swaps,
                description: `Inserting ${key} at position ${j + 1}`
            });

            // Mark the expanded sorted portion
            steps.push({
                type: 'mark_sorted',
                indices: Array.from({length: i + 1}, (_, idx) => idx),
                array: this.copyArray(arr),
                comparisons,
                swaps,
                description: `First ${i + 1} elements are now sorted`
            });
        }

        steps.push({
            type: 'complete',
            indices: Array.from({length: n}, (_, i) => i),
            array: this.copyArray(arr),
            comparisons,
            swaps,
            description: 'Insertion sort complete!'
        });

        return {
            steps,
            finalArray: arr,
            metrics: { comparisons, swaps },
            timeComplexity: 'O(n²)',
            spaceComplexity: 'O(1)'
        };
    }

    /**
     * Quick Sort: Divide-and-conquer algorithm using pivot partitioning
     * Time Complexity: O(n log n) average, O(n²) worst case
     * Space Complexity: O(log n) due to recursion
     */
    static quickSort(array) {
        const arr = this.copyArray(array);
        const steps = [];
        let comparisons = 0;
        let swaps = 0;

        function partition(low, high) {
            const pivot = arr[high];
            let i = low - 1;

            steps.push({
                type: 'select_pivot',
                indices: [high],
                array: SortingAlgorithms.copyArray(arr),
                comparisons,
                swaps,
                description: `Selected pivot: ${pivot} at position ${high}`
            });

            for (let j = low; j < high; j++) {
                comparisons++;

                steps.push({
                    type: 'compare',
                    indices: [j, high],
                    array: SortingAlgorithms.copyArray(arr),
                    comparisons,
                    swaps,
                    description: `Comparing ${arr[j]} with pivot ${pivot}`
                });

                if (arr[j] < pivot) {
                    i++;
                    if (i !== j) {
                        [arr[i], arr[j]] = [arr[j], arr[i]];
                        swaps++;

                        steps.push({
                            type: 'swap',
                            indices: [i, j],
                            array: SortingAlgorithms.copyArray(arr),
                            comparisons,
                            swaps,
                            description: `Swapping ${arr[j]} and ${arr[i]} (elements smaller than pivot go left)`
                        });
                    }
                }
            }

            [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
            swaps++;

            steps.push({
                type: 'place_pivot',
                indices: [i + 1],
                array: SortingAlgorithms.copyArray(arr),
                comparisons,
                swaps,
                description: `Placing pivot ${pivot} at its final position ${i + 1}`
            });

            return i + 1;
        }

        function quickSortRecursive(low, high) {
            if (low < high) {
                const pi = partition(low, high);

                steps.push({
                    type: 'partition_complete',
                    indices: [pi],
                    array: SortingAlgorithms.copyArray(arr),
                    comparisons,
                    swaps,
                    description: `Partition complete. Element ${arr[pi]} is in its final position.`
                });

                quickSortRecursive(low, pi - 1);
                quickSortRecursive(pi + 1, high);
            }
        }

        quickSortRecursive(0, arr.length - 1);

        steps.push({
            type: 'complete',
            indices: Array.from({length: arr.length}, (_, i) => i),
            array: SortingAlgorithms.copyArray(arr),
            comparisons,
            swaps,
            description: 'Quick sort complete!'
        });

        return {
            steps,
            finalArray: arr,
            metrics: { comparisons, swaps },
            timeComplexity: 'O(n log n)',
            spaceComplexity: 'O(log n)'
        };
    }

    /**
     * Merge Sort: Divide-and-conquer algorithm that divides array into halves
     * Time Complexity: O(n log n) in all cases
     * Space Complexity: O(n)
     */
    static mergeSort(array) {
        const arr = this.copyArray(array);
        const steps = [];
        let comparisons = 0;
        let swaps = 0;

        function merge(left, mid, right) {
            const leftArr = arr.slice(left, mid + 1);
            const rightArr = arr.slice(mid + 1, right + 1);

            let i = 0, j = 0, k = left;

            steps.push({
                type: 'merge_start',
                indices: Array.from({length: right - left + 1}, (_, idx) => left + idx),
                array: SortingAlgorithms.copyArray(arr),
                comparisons,
                swaps,
                description: `Merging subarrays [${left}..${mid}] and [${mid + 1}..${right}]`
            });

            while (i < leftArr.length && j < rightArr.length) {
                comparisons++;

                steps.push({
                    type: 'compare',
                    indices: [left + i, mid + 1 + j],
                    array: SortingAlgorithms.copyArray(arr),
                    comparisons,
                    swaps,
                    description: `Comparing ${leftArr[i]} and ${rightArr[j]}`
                });

                if (leftArr[i] <= rightArr[j]) {
                    arr[k] = leftArr[i];
                    i++;
                } else {
                    arr[k] = rightArr[j];
                    j++;
                }

                steps.push({
                    type: 'place',
                    indices: [k],
                    array: SortingAlgorithms.copyArray(arr),
                    comparisons,
                    swaps,
                    description: `Placing ${arr[k]} at position ${k}`
                });

                k++;
            }

            // Copy remaining elements
            while (i < leftArr.length) {
                arr[k] = leftArr[i];
                steps.push({
                    type: 'place',
                    indices: [k],
                    array: SortingAlgorithms.copyArray(arr),
                    comparisons,
                    swaps,
                    description: `Copying remaining element ${arr[k]} to position ${k}`
                });
                i++;
                k++;
            }

            while (j < rightArr.length) {
                arr[k] = rightArr[j];
                steps.push({
                    type: 'place',
                    indices: [k],
                    array: SortingAlgorithms.copyArray(arr),
                    comparisons,
                    swaps,
                    description: `Copying remaining element ${arr[k]} to position ${k}`
                });
                j++;
                k++;
            }

            steps.push({
                type: 'merge_complete',
                indices: Array.from({length: right - left + 1}, (_, idx) => left + idx),
                array: SortingAlgorithms.copyArray(arr),
                comparisons,
                swaps,
                description: `Merge complete for range [${left}..${right}]`
            });
        }

        function mergeSortRecursive(left, right) {
            if (left < right) {
                const mid = Math.floor((left + right) / 2);

                steps.push({
                    type: 'divide',
                    indices: Array.from({length: right - left + 1}, (_, idx) => left + idx),
                    array: SortingAlgorithms.copyArray(arr),
                    comparisons,
                    swaps,
                    description: `Dividing array at position ${mid}. Left: [${left}..${mid}], Right: [${mid + 1}..${right}]`
                });

                mergeSortRecursive(left, mid);
                mergeSortRecursive(mid + 1, right);
                merge(left, mid, right);
            }
        }

        mergeSortRecursive(0, arr.length - 1);

        steps.push({
            type: 'complete',
            indices: Array.from({length: arr.length}, (_, i) => i),
            array: SortingAlgorithms.copyArray(arr),
            comparisons,
            swaps,
            description: 'Merge sort complete!'
        });

        return {
            steps,
            finalArray: arr,
            metrics: { comparisons, swaps },
            timeComplexity: 'O(n log n)',
            spaceComplexity: 'O(n)'
        };
    }
}

/**
 * Graph class for representing and manipulating graphs
 */
class Graph {
    constructor() {
        this.adjacencyList = new Map();
        this.nodes = new Set();
        this.edges = [];
    }

    /**
     * Add a node to the graph
     */
    addNode(node) {
        if (!this.adjacencyList.has(node)) {
            this.adjacencyList.set(node, []);
            this.nodes.add(node);
        }
    }

    /**
     * Add an edge between two nodes
     */
    addEdge(node1, node2, weight = 1) {
        this.addNode(node1);
        this.addNode(node2);

        this.adjacencyList.get(node1).push({ node: node2, weight });
        this.adjacencyList.get(node2).push({ node: node1, weight }); // Undirected graph

        this.edges.push({ from: node1, to: node2, weight });
    }

    /**
     * Get neighbors of a node
     */
    getNeighbors(node) {
        return this.adjacencyList.get(node) || [];
    }

    /**
     * Get all nodes
     */
    getNodes() {
        return Array.from(this.nodes);
    }

    /**
     * Get all edges
     */
    getEdges() {
        return this.edges;
    }
}

/**
 * Graph Algorithms class for educational visualization
 */
class GraphAlgorithms {
    /**
     * Creates a sample graph for demonstration
     */
    static createSampleGraph() {
        const graph = new Graph();

        // Create a connected graph with labeled nodes
        graph.addEdge('A', 'B');
        graph.addEdge('A', 'C');
        graph.addEdge('B', 'D');
        graph.addEdge('B', 'E');
        graph.addEdge('C', 'F');
        graph.addEdge('D', 'G');
        graph.addEdge('E', 'G');
        graph.addEdge('F', 'G');

        return graph;
    }

    /**
     * Breadth-First Search (BFS): Explores nodes level by level
     * Time Complexity: O(V + E) where V is vertices and E is edges
     * Space Complexity: O(V) for the queue and visited set
     */
    static breadthFirstSearch(graph, startNode) {
        const steps = [];
        const visited = new Set();
        const queue = [startNode];
        const distances = new Map();
        const parents = new Map();
        let nodeVisitCount = 0;

        // Initialize distances and parents
        distances.set(startNode, 0);
        parents.set(startNode, null);

        steps.push({
            type: 'initialize',
            currentNode: startNode,
            queue: [...queue],
            visited: new Set(visited),
            distances: new Map(distances),
            description: `Starting BFS from node ${startNode}. Adding to queue.`
        });

        while (queue.length > 0) {
            const currentNode = queue.shift();

            if (visited.has(currentNode)) {
                continue;
            }

            visited.add(currentNode);
            nodeVisitCount++;

            steps.push({
                type: 'visit',
                currentNode: currentNode,
                queue: [...queue],
                visited: new Set(visited),
                distances: new Map(distances),
                description: `Visiting node ${currentNode} (distance: ${distances.get(currentNode)})`
            });

            const neighbors = graph.getNeighbors(currentNode);

            for (const neighborInfo of neighbors) {
                const neighbor = neighborInfo.node;

                if (!visited.has(neighbor) && !queue.includes(neighbor)) {
                    queue.push(neighbor);
                    distances.set(neighbor, distances.get(currentNode) + 1);
                    parents.set(neighbor, currentNode);

                    steps.push({
                        type: 'discover',
                        currentNode: currentNode,
                        discoveredNode: neighbor,
                        queue: [...queue],
                        visited: new Set(visited),
                        distances: new Map(distances),
                        description: `Discovered ${neighbor} via ${currentNode}. Distance: ${distances.get(neighbor)}. Added to queue.`
                    });
                }
            }

            steps.push({
                type: 'explore_complete',
                currentNode: currentNode,
                queue: [...queue],
                visited: new Set(visited),
                distances: new Map(distances),
                description: `Finished exploring neighbors of ${currentNode}`
            });
        }

        steps.push({
            type: 'complete',
            visited: new Set(visited),
            distances: new Map(distances),
            parents: new Map(parents),
            description: `BFS complete! Visited ${nodeVisitCount} nodes.`
        });

        return {
            steps,
            visited: Array.from(visited),
            distances: Object.fromEntries(distances),
            parents: Object.fromEntries(parents),
            metrics: { nodesVisited: nodeVisitCount, edgesExplored: graph.getEdges().length },
            timeComplexity: 'O(V + E)',
            spaceComplexity: 'O(V)'
        };
    }

    /**
     * Dijkstra's Shortest Path Algorithm
     * Time Complexity: O((V + E) log V) with priority queue
     * Space Complexity: O(V)
     */
    static dijkstraShortestPath(graph, startNode, endNode) {
        const steps = [];
        const distances = new Map();
        const parents = new Map();
        const visited = new Set();
        const priorityQueue = [];

        // Initialize distances
        for (const node of graph.getNodes()) {
            distances.set(node, node === startNode ? 0 : Infinity);
            parents.set(node, null);
        }

        priorityQueue.push({ node: startNode, distance: 0 });

        steps.push({
            type: 'initialize',
            currentNode: startNode,
            distances: new Map(distances),
            visited: new Set(visited),
            description: `Starting Dijkstra's algorithm from ${startNode} to find shortest path to ${endNode}`
        });

        while (priorityQueue.length > 0) {
            // Find node with minimum distance
            priorityQueue.sort((a, b) => a.distance - b.distance);
            const { node: currentNode, distance: currentDistance } = priorityQueue.shift();

            if (visited.has(currentNode)) {
                continue;
            }

            visited.add(currentNode);

            steps.push({
                type: 'visit',
                currentNode: currentNode,
                distances: new Map(distances),
                visited: new Set(visited),
                description: `Visiting ${currentNode} with distance ${currentDistance}`
            });

            if (currentNode === endNode) {
                steps.push({
                    type: 'target_reached',
                    currentNode: currentNode,
                    distances: new Map(distances),
                    description: `Target ${endNode} reached! Shortest path found.`
                });
                break;
            }

            const neighbors = graph.getNeighbors(currentNode);

            for (const neighborInfo of neighbors) {
                const neighbor = neighborInfo.node;
                const weight = neighborInfo.weight;

                if (!visited.has(neighbor)) {
                    const newDistance = distances.get(currentNode) + weight;

                    if (newDistance < distances.get(neighbor)) {
                        distances.set(neighbor, newDistance);
                        parents.set(neighbor, currentNode);
                        priorityQueue.push({ node: neighbor, distance: newDistance });

                        steps.push({
                            type: 'relax',
                            currentNode: currentNode,
                            neighbor: neighbor,
                            oldDistance: distances.get(neighbor) === Infinity ? '∞' : distances.get(neighbor),
                            newDistance: newDistance,
                            distances: new Map(distances),
                            description: `Relaxing edge ${currentNode} → ${neighbor}. Distance updated to ${newDistance}`
                        });
                    }
                }
            }
        }

        // Reconstruct path
        const path = [];
        let current = endNode;
        while (current !== null) {
            path.unshift(current);
            current = parents.get(current);
        }

        steps.push({
            type: 'complete',
            path: path,
            shortestDistance: distances.get(endNode),
            distances: new Map(distances),
            description: `Shortest path from ${startNode} to ${endNode}: ${path.join(' → ')} (distance: ${distances.get(endNode)})`
        });

        return {
            steps,
            shortestPath: path,
            shortestDistance: distances.get(endNode),
            distances: Object.fromEntries(distances),
            metrics: { nodesVisited: visited.size },
            timeComplexity: 'O((V + E) log V)',
            spaceComplexity: 'O(V)'
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SortingAlgorithms, GraphAlgorithms, Graph };
}