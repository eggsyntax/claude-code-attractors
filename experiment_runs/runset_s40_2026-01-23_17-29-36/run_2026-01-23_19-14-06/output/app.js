/**
 * Main application logic for the Visual Algorithm Explorer
 * Handles user interactions and coordinates between algorithms and visualization
 */

class AlgorithmExplorer {
    constructor() {
        this.currentAlgorithm = 'bubble-sort';
        this.currentCategory = 'sorting'; // 'sorting' or 'graph'
        this.sampleGraph = null;
        this.algorithms = {
            'bubble-sort': {
                name: 'Bubble Sort',
                implementation: SortingAlgorithms.bubbleSort,
                description: 'Bubble Sort repeatedly steps through the list, compares adjacent elements and swaps them if they\'re in the wrong order. The pass through the list is repeated until the list is sorted.',
                timeComplexity: 'O(n²)',
                spaceComplexity: 'O(1)',
                code: {
                    javascript: `// Bubble Sort Implementation
function bubbleSort(arr) {
    const n = arr.length;
    let comparisons = 0;
    let swaps = 0;

    for (let i = 0; i < n - 1; i++) {
        let swappedInThisPass = false;

        for (let j = 0; j < n - i - 1; j++) {
            comparisons++;
            if (arr[j] > arr[j + 1]) {
                // Swap elements
                [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
                swaps++;
                swappedInThisPass = true;
            }
        }

        // Early termination optimization
        if (!swappedInThisPass) {
            break;
        }
    }

    return { sortedArray: arr, comparisons, swaps };
}`,
                    python: `# Bubble Sort Implementation
def bubble_sort(arr):
    n = len(arr)
    comparisons = 0
    swaps = 0

    for i in range(n - 1):
        swapped_in_pass = False

        for j in range(n - i - 1):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                # Swap elements
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped_in_pass = True

        # Early termination optimization
        if not swapped_in_pass:
            break

    return {
        'sorted_array': arr,
        'comparisons': comparisons,
        'swaps': swaps
    }`
                }
            },
            'insertion-sort': {
                name: 'Insertion Sort',
                implementation: SortingAlgorithms.insertionSort,
                description: 'Insertion Sort builds the sorted array one item at a time. It is much less efficient on large lists than more advanced algorithms, but performs well for small datasets.',
                timeComplexity: 'O(n²)',
                spaceComplexity: 'O(1)',
                code: {
                    javascript: `// Insertion Sort Implementation
function insertionSort(arr) {
    const n = arr.length;
    let comparisons = 0;
    let swaps = 0;

    for (let i = 1; i < n; i++) {
        let key = arr[i];
        let j = i - 1;

        while (j >= 0) {
            comparisons++;
            if (arr[j] <= key) break;

            arr[j + 1] = arr[j];
            swaps++;
            j--;
        }

        arr[j + 1] = key;
    }

    return { sortedArray: arr, comparisons, swaps };
}`,
                    python: `# Insertion Sort Implementation
def insertion_sort(arr):
    n = len(arr)
    comparisons = 0
    swaps = 0

    for i in range(1, n):
        key = arr[i]
        j = i - 1

        while j >= 0:
            comparisons += 1
            if arr[j] <= key:
                break

            arr[j + 1] = arr[j]
            swaps += 1
            j -= 1

        arr[j + 1] = key

    return {
        'sorted_array': arr,
        'comparisons': comparisons,
        'swaps': swaps
    }`
                }
            },
            'quick-sort': {
                name: 'Quick Sort',
                implementation: SortingAlgorithms.quickSort,
                description: 'Quick Sort is a divide-and-conquer algorithm. It picks an element as pivot and partitions the array around the pivot, then recursively sorts the sub-arrays.',
                timeComplexity: 'O(n log n)',
                spaceComplexity: 'O(log n)',
                code: {
                    javascript: `// Quick Sort Implementation
function quickSort(arr, low = 0, high = arr.length - 1) {
    if (low < high) {
        const pivotIndex = partition(arr, low, high);
        quickSort(arr, low, pivotIndex - 1);
        quickSort(arr, pivotIndex + 1, high);
    }
    return arr;
}

function partition(arr, low, high) {
    const pivot = arr[high];
    let i = low - 1;

    for (let j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
    }

    [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
    return i + 1;
}`,
                    python: `# Quick Sort Implementation
def quick_sort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1

    if low < high:
        pivot_index = partition(arr, low, high)
        quick_sort(arr, low, pivot_index - 1)
        quick_sort(arr, pivot_index + 1, high)

    return arr

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1`
                }
            },
            'merge-sort': {
                name: 'Merge Sort',
                implementation: SortingAlgorithms.mergeSort,
                description: 'Merge Sort is a divide-and-conquer algorithm that divides the array into halves, sorts them, and then merges them back together. It guarantees O(n log n) time complexity.',
                timeComplexity: 'O(n log n)',
                spaceComplexity: 'O(n)',
                code: {
                    javascript: `// Merge Sort Implementation
function mergeSort(arr) {
    if (arr.length <= 1) return arr;

    const mid = Math.floor(arr.length / 2);
    const left = mergeSort(arr.slice(0, mid));
    const right = mergeSort(arr.slice(mid));

    return merge(left, right);
}

function merge(left, right) {
    let result = [];
    let i = 0, j = 0;

    while (i < left.length && j < right.length) {
        if (left[i] <= right[j]) {
            result.push(left[i]);
            i++;
        } else {
            result.push(right[j]);
            j++;
        }
    }

    return result.concat(left.slice(i)).concat(right.slice(j));
}`,
                    python: `# Merge Sort Implementation
def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result`
                }
            },

            // Graph Algorithms
            'bfs-search': {
                name: 'BFS (Breadth-First Search)',
                implementation: (graph) => GraphAlgorithms.breadthFirstSearch(graph, 'A'),
                description: 'BFS explores nodes level by level, starting from a source node. It uses a queue to visit nodes in the order they were discovered, making it perfect for finding shortest paths in unweighted graphs.',
                timeComplexity: 'O(V + E)',
                spaceComplexity: 'O(V)',
                isGraphAlgorithm: true,
                code: {
                    javascript: `// BFS Implementation
function breadthFirstSearch(graph, startNode) {
    const visited = new Set();
    const queue = [startNode];
    const result = [];

    while (queue.length > 0) {
        const currentNode = queue.shift();

        if (!visited.has(currentNode)) {
            visited.add(currentNode);
            result.push(currentNode);

            // Add neighbors to queue
            const neighbors = graph.getNeighbors(currentNode);
            for (const neighbor of neighbors) {
                if (!visited.has(neighbor.node)) {
                    queue.push(neighbor.node);
                }
            }
        }
    }

    return result;
}`,
                    python: `# BFS Implementation
def breadth_first_search(graph, start_node):
    visited = set()
    queue = [start_node]
    result = []

    while queue:
        current_node = queue.pop(0)

        if current_node not in visited:
            visited.add(current_node)
            result.append(current_node)

            # Add neighbors to queue
            neighbors = graph.get_neighbors(current_node)
            for neighbor in neighbors:
                if neighbor['node'] not in visited:
                    queue.append(neighbor['node'])

    return result`
                }
            },

            'dfs-search': {
                name: 'DFS (Depth-First Search)',
                implementation: (graph) => GraphAlgorithms.depthFirstSearch(graph, 'A'),
                description: 'DFS explores nodes by going as deep as possible along each branch before backtracking. It uses a stack (or recursion) to visit nodes, making it useful for detecting cycles and finding connected components.',
                timeComplexity: 'O(V + E)',
                spaceComplexity: 'O(V)',
                isGraphAlgorithm: true,
                code: {
                    javascript: `// DFS Implementation
function depthFirstSearch(graph, startNode) {
    const visited = new Set();
    const stack = [startNode];
    const result = [];

    while (stack.length > 0) {
        const currentNode = stack.pop();

        if (!visited.has(currentNode)) {
            visited.add(currentNode);
            result.push(currentNode);

            // Add neighbors to stack (in reverse order)
            const neighbors = graph.getNeighbors(currentNode).reverse();
            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    stack.push(neighbor);
                }
            }
        }
    }

    return result;
}`,
                    python: `# DFS Implementation
def depth_first_search(graph, start_node):
    visited = set()
    stack = [start_node]
    result = []

    while stack:
        current_node = stack.pop()

        if current_node not in visited:
            visited.add(current_node)
            result.append(current_node)

            # Add neighbors to stack (in reverse order)
            neighbors = graph.get_neighbors(current_node)[::-1]
            for neighbor in neighbors:
                if neighbor not in visited:
                    stack.append(neighbor)

    return result`
                }
            },

            'dijkstra-path': {
                name: "Dijkstra's Shortest Path",
                implementation: (graph) => GraphAlgorithms.dijkstraShortestPath(graph, 'A', 'G'),
                description: "Dijkstra's algorithm finds the shortest path between nodes in a weighted graph. It maintains a priority queue of nodes and their distances, always processing the node with the smallest known distance first.",
                timeComplexity: 'O((V + E) log V)',
                spaceComplexity: 'O(V)',
                isGraphAlgorithm: true,
                hasEndNode: true,
                code: {
                    javascript: `// Dijkstra's Algorithm Implementation
function dijkstraShortestPath(graph, startNode, endNode) {
    const distances = new Map();
    const previous = new Map();
    const unvisited = new Set();

    // Initialize distances
    for (const node of graph.getNodes()) {
        distances.set(node, node === startNode ? 0 : Infinity);
        previous.set(node, null);
        unvisited.add(node);
    }

    while (unvisited.size > 0) {
        // Find unvisited node with minimum distance
        let currentNode = null;
        let minDistance = Infinity;

        for (const node of unvisited) {
            if (distances.get(node) < minDistance) {
                minDistance = distances.get(node);
                currentNode = node;
            }
        }

        if (currentNode === null || currentNode === endNode) {
            break;
        }

        unvisited.delete(currentNode);

        // Update distances to neighbors
        const neighbors = graph.getNeighbors(currentNode);
        for (const neighbor of neighbors) {
            if (unvisited.has(neighbor.node)) {
                const newDistance = distances.get(currentNode) + neighbor.weight;
                if (newDistance < distances.get(neighbor.node)) {
                    distances.set(neighbor.node, newDistance);
                    previous.set(neighbor.node, currentNode);
                }
            }
        }
    }

    return { distances, previous };
}`,
                    python: `# Dijkstra's Algorithm Implementation
def dijkstra_shortest_path(graph, start_node, end_node):
    import heapq

    distances = {node: float('inf') for node in graph.get_nodes()}
    distances[start_node] = 0
    previous = {node: None for node in graph.get_nodes()}
    pq = [(0, start_node)]
    visited = set()

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == end_node:
            break

        neighbors = graph.get_neighbors(current_node)
        for neighbor in neighbors:
            node = neighbor['node']
            weight = neighbor['weight']

            if node not in visited:
                new_distance = current_distance + weight
                if new_distance < distances[node]:
                    distances[node] = new_distance
                    previous[node] = current_node
                    heapq.heappush(pq, (new_distance, node))

    return {'distances': distances, 'previous': previous}`
                }
            },

            'astar-path': {
                name: 'A* Pathfinding',
                implementation: (graph) => GraphAlgorithms.aStarPathfinding(graph, 'A', 'G'),
                description: "A* is an extension of Dijkstra's algorithm that uses heuristics to find optimal paths more efficiently. It combines the actual distance from start (g-score) with a heuristic estimate to the goal (h-score) to guide the search.",
                timeComplexity: 'O(b^d)',
                spaceComplexity: 'O(b^d)',
                isGraphAlgorithm: true,
                hasEndNode: true,
                code: {
                    javascript: `// A* Pathfinding Implementation
function aStarPathfinding(graph, startNode, endNode) {
    const openSet = [startNode];
    const closedSet = new Set();
    const gScore = new Map();
    const fScore = new Map();
    const cameFrom = new Map();

    // Initialize scores
    graph.getNodes().forEach(node => {
        gScore.set(node, node === startNode ? 0 : Infinity);
        fScore.set(node, node === startNode ? heuristic(node, endNode) : Infinity);
    });

    while (openSet.length > 0) {
        // Get node with lowest fScore
        let current = openSet[0];
        for (const node of openSet) {
            if (fScore.get(node) < fScore.get(current)) {
                current = node;
            }
        }

        if (current === endNode) {
            return reconstructPath(cameFrom, current);
        }

        openSet.splice(openSet.indexOf(current), 1);
        closedSet.add(current);

        const neighbors = graph.getNeighbors(current);
        for (const neighbor of neighbors) {
            if (closedSet.has(neighbor)) continue;

            const tentativeGScore = gScore.get(current) + graph.getEdgeWeight(current, neighbor);

            if (!openSet.includes(neighbor)) {
                openSet.push(neighbor);
            } else if (tentativeGScore >= gScore.get(neighbor)) {
                continue;
            }

            cameFrom.set(neighbor, current);
            gScore.set(neighbor, tentativeGScore);
            fScore.set(neighbor, gScore.get(neighbor) + heuristic(neighbor, endNode));
        }
    }

    return []; // No path found
}`,
                    python: `# A* Pathfinding Implementation
def a_star_pathfinding(graph, start_node, end_node):
    import heapq

    open_set = [(0, start_node)]
    closed_set = set()
    g_score = {node: float('inf') for node in graph.get_nodes()}
    g_score[start_node] = 0
    f_score = {node: float('inf') for node in graph.get_nodes()}
    f_score[start_node] = heuristic(start_node, end_node)
    came_from = {}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end_node:
            return reconstruct_path(came_from, current)

        closed_set.add(current)

        neighbors = graph.get_neighbors(current)
        for neighbor in neighbors:
            if neighbor in closed_set:
                continue

            tentative_g_score = g_score[current] + graph.get_edge_weight(current, neighbor)

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, end_node)

                if (f_score[neighbor], neighbor) not in open_set:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # No path found`
                }
            }
        };

        this.currentCodeLanguage = 'javascript';

        this.initializeEventListeners();
        this.updateAlgorithmInfo();
        this.initializeSampleGraph();
    }

    /**
     * Initialize the sample graph for graph algorithms
     */
    initializeSampleGraph() {
        this.sampleGraph = GraphAlgorithms.createSampleGraph();
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Category selection buttons
        document.querySelectorAll('.category-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                this.selectCategory(e.target.id.replace('-category', ''));
            });
        });

        // Algorithm selection buttons
        document.querySelectorAll('.algorithm-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectAlgorithm(e.target.id);
            });
        });

        // Array size control
        const arraySizeSlider = document.getElementById('array-size');
        const sizeDisplay = document.getElementById('size-display');

        if (arraySizeSlider && sizeDisplay) {
            arraySizeSlider.addEventListener('input', (e) => {
                const size = parseInt(e.target.value);
                sizeDisplay.textContent = size;
                if (visualizer) {
                    visualizer.generateRandomArray(size);
                }
            });
        }

        // Animation speed control
        const speedSlider = document.getElementById('animation-speed');
        if (speedSlider) {
            speedSlider.addEventListener('input', (e) => {
                const speed = parseInt(e.target.value);
                if (visualizer) visualizer.setSpeed(speed);
                if (graphVisualizer) graphVisualizer.setSpeed(speed);
            });
        }

        // Control buttons
        const playPauseBtn = document.getElementById('play-pause');
        const stepBtn = document.getElementById('step-forward');
        const resetBtn = document.getElementById('reset');
        const randomizeBtn = document.getElementById('randomize-array');

        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => {
                const currentVisualizer = this.getCurrentVisualizer();
                if (currentVisualizer) {
                    if (currentVisualizer.isPlaying) {
                        currentVisualizer.pause();
                        playPauseBtn.textContent = '▶ Play';
                    } else {
                        this.runCurrentAlgorithm();
                        currentVisualizer.play();
                        playPauseBtn.textContent = '⏸ Pause';
                    }
                }
            });
        }

        if (stepBtn) {
            stepBtn.addEventListener('click', () => {
                const currentVisualizer = this.getCurrentVisualizer();
                if (currentVisualizer) {
                    this.runCurrentAlgorithm();
                    currentVisualizer.stepForward();
                }
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                const currentVisualizer = this.getCurrentVisualizer();
                if (currentVisualizer) {
                    currentVisualizer.reset();
                    if (playPauseBtn) playPauseBtn.textContent = '▶ Play';
                }
            });
        }

        if (randomizeBtn) {
            randomizeBtn.addEventListener('click', () => {
                const size = parseInt(document.getElementById('array-size')?.value || 20);
                if (visualizer) {
                    visualizer.generateRandomArray(size);
                    if (playPauseBtn) playPauseBtn.textContent = '▶ Play';
                }
            });
        }

        // Code language tabs
        document.querySelectorAll('.code-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.selectCodeLanguage(e.target.dataset.language);
            });
        });

        // Run code button
        const runCodeBtn = document.getElementById('run-code');
        if (runCodeBtn) {
            runCodeBtn.addEventListener('click', () => {
                this.runCodeInConsole();
            });
        }
    }

    /**
     * Select and activate an algorithm
     */
    selectAlgorithm(algorithmId) {
        // Update active button
        document.querySelectorAll('.algorithm-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(algorithmId)?.classList.add('active');

        this.currentAlgorithm = algorithmId;
        this.updateAlgorithmInfo();

        // Reset visualization
        const currentVisualizer = this.getCurrentVisualizer();
        if (currentVisualizer) {
            currentVisualizer.reset();
            const playPauseBtn = document.getElementById('play-pause');
            if (playPauseBtn) playPauseBtn.textContent = '▶ Play';
        }
    }

    /**
     * Select and activate a category (sorting or graph)
     */
    selectCategory(categoryType) {
        // Update active category button
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(categoryType + '-category')?.classList.add('active');

        this.currentCategory = categoryType;

        // Show/hide appropriate algorithm groups
        const sortingGroup = document.getElementById('sorting-algorithms');
        const graphGroup = document.getElementById('graph-algorithms');
        const arrayControls = document.getElementById('array-controls');
        const graphControls = document.getElementById('graph-controls');
        const arrayContainer = document.getElementById('array-container');
        const graphContainer = document.getElementById('graph-container');

        if (categoryType === 'sorting') {
            sortingGroup?.classList.remove('hidden');
            graphGroup?.classList.add('hidden');
            arrayControls?.classList.remove('hidden');
            graphControls?.classList.add('hidden');
            arrayContainer?.classList.remove('hidden');
            graphContainer?.classList.add('hidden');
            currentVisualizationType = 'array';

            // Update metrics labels for sorting
            document.getElementById('metric1-label').textContent = 'Comparisons:';
            document.getElementById('metric2-label').textContent = 'Swaps:';

            // Select first sorting algorithm
            this.selectAlgorithm('bubble-sort');
        } else if (categoryType === 'graph') {
            sortingGroup?.classList.add('hidden');
            graphGroup?.classList.remove('hidden');
            arrayControls?.classList.add('hidden');
            graphControls?.classList.remove('hidden');
            arrayContainer?.classList.add('hidden');
            graphContainer?.classList.remove('hidden');
            currentVisualizationType = 'graph';

            // Update metrics labels for graphs
            document.getElementById('metric1-label').textContent = 'Nodes Visited:';
            document.getElementById('metric2-label').textContent = 'Edges Explored:';

            // Set up graph
            if (graphVisualizer) {
                graphVisualizer.setGraph(this.sampleGraph);
            }

            // Select first graph algorithm
            this.selectAlgorithm('bfs-search');
        }
    }

    /**
     * Get the current visualizer based on category
     */
    getCurrentVisualizer() {
        return this.currentCategory === 'graph' ? graphVisualizer : visualizer;
    }

    /**
     * Update algorithm information display
     */
    updateAlgorithmInfo() {
        const algorithm = this.algorithms[this.currentAlgorithm];
        if (!algorithm) return;

        // Update title and description
        const titleElement = document.getElementById('algorithm-title');
        const explanationElement = document.getElementById('algorithm-explanation');
        const complexityElement = document.getElementById('time-complexity');

        if (titleElement) titleElement.textContent = algorithm.name;
        if (explanationElement) explanationElement.textContent = algorithm.description;
        if (complexityElement) complexityElement.textContent = algorithm.timeComplexity;

        // Show/hide end node selector for algorithms that need it
        const endNodeLabel = document.getElementById('end-node-label');
        const endNodeSelect = document.getElementById('end-node');
        if (algorithm.hasEndNode) {
            endNodeLabel?.classList.remove('hidden');
            endNodeSelect?.classList.remove('hidden');
        } else {
            endNodeLabel?.classList.add('hidden');
            endNodeSelect?.classList.add('hidden');
        }

        // Update code display
        this.updateCodeDisplay();
    }

    /**
     * Select code language tab
     */
    selectCodeLanguage(language) {
        document.querySelectorAll('.code-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-language="${language}"]`)?.classList.add('active');

        this.currentCodeLanguage = language;
        this.updateCodeDisplay();
    }

    /**
     * Update the code display
     */
    updateCodeDisplay() {
        const algorithm = this.algorithms[this.currentAlgorithm];
        const codeElement = document.getElementById('code-content');

        if (algorithm && codeElement) {
            const code = algorithm.code[this.currentCodeLanguage] || algorithm.code.javascript;
            codeElement.textContent = code;

            // Apply basic syntax highlighting
            this.applySyntaxHighlighting(codeElement);
        }
    }

    /**
     * Apply basic syntax highlighting
     */
    applySyntaxHighlighting(element) {
        let html = element.textContent;

        // JavaScript/Python keywords
        const keywords = ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'return', 'def', 'class', 'import', 'from'];
        keywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'g');
            html = html.replace(regex, `<span class="keyword">${keyword}</span>`);
        });

        // String literals
        html = html.replace(/(["'])((?:\\.|(?!\1)[^\\])*?)\1/g, '<span class="string">$1$2$1</span>');

        // Comments
        html = html.replace(/(\/\/.*$|#.*$)/gm, '<span class="comment">$1</span>');

        // Numbers
        html = html.replace(/\b(\d+)\b/g, '<span class="number">$1</span>');

        element.innerHTML = html;
    }

    /**
     * Run the current algorithm and load steps into visualizer
     */
    runCurrentAlgorithm() {
        const currentVisualizer = this.getCurrentVisualizer();
        if (!currentVisualizer || currentVisualizer.steps.length > 0) return;

        const algorithm = this.algorithms[this.currentAlgorithm];
        if (!algorithm) return;

        try {
            let result;

            if (algorithm.isGraphAlgorithm) {
                // Handle graph algorithms
                const startNode = document.getElementById('start-node')?.value || 'A';

                if (this.currentAlgorithm === 'dijkstra-path' || this.currentAlgorithm === 'astar-path') {
                    const endNode = document.getElementById('end-node')?.value || 'G';

                    if (this.currentAlgorithm === 'dijkstra-path') {
                        result = { steps: Array.from(GraphAlgorithms.dijkstraShortestPath(this.sampleGraph, startNode, endNode)), timeComplexity: 'O((V + E) log V)' };
                    } else {
                        result = { steps: Array.from(GraphAlgorithms.aStarPathfinding(this.sampleGraph, startNode, endNode)), timeComplexity: 'O(b^d)' };
                    }
                } else if (this.currentAlgorithm === 'bfs-search') {
                    result = { steps: Array.from(GraphAlgorithms.breadthFirstSearch(this.sampleGraph, startNode)), timeComplexity: 'O(V + E)' };
                } else if (this.currentAlgorithm === 'dfs-search') {
                    result = { steps: Array.from(GraphAlgorithms.depthFirstSearch(this.sampleGraph, startNode)), timeComplexity: 'O(V + E)' };
                } else {
                    result = algorithm.implementation(this.sampleGraph);
                }
            } else {
                // Handle sorting algorithms
                result = algorithm.implementation([...visualizer.array]);
            }

            currentVisualizer.loadSteps(result);
            console.log(`Loaded ${algorithm.name} with ${result.steps.length} steps`);
        } catch (error) {
            console.error('Error running algorithm:', error);
        }
    }

    /**
     * Run the code in the console (for educational purposes)
     */
    runCodeInConsole() {
        const algorithm = this.algorithms[this.currentAlgorithm];
        const testArray = [...visualizer.array];

        console.log(`\n=== Running ${algorithm.name} ===`);
        console.log('Input array:', testArray);

        try {
            const result = algorithm.implementation(testArray);
            console.log('Result:', result);
            console.log('Steps generated:', result.steps.length);
            console.log('Final metrics:', result.metrics);
            console.log('Time complexity:', result.timeComplexity);
            console.log('Space complexity:', result.spaceComplexity);
        } catch (error) {
            console.error('Error running algorithm:', error);
        }
    }

    /**
     * Get algorithm statistics for the current array
     */
    getAlgorithmStats() {
        const results = {};
        const testArray = [...visualizer.array];

        Object.entries(this.algorithms).forEach(([key, algorithm]) => {
            try {
                const result = algorithm.implementation([...testArray]);
                results[key] = {
                    name: algorithm.name,
                    comparisons: result.metrics.comparisons,
                    swaps: result.metrics.swaps,
                    steps: result.steps.length,
                    timeComplexity: result.timeComplexity,
                    spaceComplexity: result.spaceComplexity
                };
            } catch (error) {
                console.error(`Error testing ${algorithm.name}:`, error);
            }
        });

        return results;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.algorithmExplorer = new AlgorithmExplorer();

    console.log('Visual Algorithm Explorer initialized!');
    console.log('Use algorithmExplorer.getAlgorithmStats() to compare all algorithms on the current array.');
});