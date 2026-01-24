/**
 * Visualization engine for the Algorithm Explorer
 * Handles array rendering, animations, and step-by-step execution
 */

class AlgorithmVisualizer {
    constructor() {
        this.array = [];
        this.currentStep = 0;
        this.steps = [];
        this.isPlaying = false;
        this.animationSpeed = 500; // milliseconds
        this.maxValue = 100;
        this.container = null;
        this.sortedIndices = new Set();

        this.initializeElements();
    }

    /**
     * Initialize DOM element references
     */
    initializeElements() {
        this.container = document.getElementById('array-container');
        this.comparisonsDisplay = document.getElementById('comparisons');
        this.swapsDisplay = document.getElementById('swaps');
        this.timeComplexityDisplay = document.getElementById('time-complexity');
    }

    /**
     * Generate a random array of specified size
     */
    generateRandomArray(size = 20) {
        this.array = Array.from({ length: size }, () =>
            Math.floor(Math.random() * 90) + 10
        );
        this.maxValue = Math.max(...this.array);
        this.sortedIndices.clear();
        this.renderArray();
        this.resetMetrics();
        return this.array;
    }

    /**
     * Set a custom array
     */
    setArray(newArray) {
        this.array = [...newArray];
        this.maxValue = Math.max(...this.array);
        this.sortedIndices.clear();
        this.renderArray();
        this.resetMetrics();
    }

    /**
     * Reset all metrics to zero
     */
    resetMetrics() {
        this.updateMetrics({ comparisons: 0, swaps: 0 });
    }

    /**
     * Update metrics display
     */
    updateMetrics(metrics) {
        if (this.comparisonsDisplay) {
            this.comparisonsDisplay.textContent = metrics.comparisons || 0;
        }
        if (this.swapsDisplay) {
            this.swapsDisplay.textContent = metrics.swaps || 0;
        }
    }

    /**
     * Update time complexity display
     */
    updateTimeComplexity(complexity) {
        if (this.timeComplexityDisplay) {
            this.timeComplexityDisplay.textContent = complexity;
        }
    }

    /**
     * Render the array as visual bars
     */
    renderArray(highlightIndices = [], highlightType = 'comparing') {
        if (!this.container) return;

        this.container.innerHTML = '';

        const containerWidth = this.container.clientWidth || 800;
        const barWidth = Math.max(15, Math.floor((containerWidth - (this.array.length * 2)) / this.array.length));
        const maxHeight = 250;

        this.array.forEach((value, index) => {
            const bar = document.createElement('div');
            bar.className = 'array-bar';
            bar.style.width = `${barWidth}px`;
            bar.style.height = `${(value / this.maxValue) * maxHeight}px`;
            bar.textContent = value;
            bar.setAttribute('data-index', index);
            bar.setAttribute('data-value', value);

            // Apply highlighting based on current step
            if (highlightIndices.includes(index)) {
                bar.classList.add(highlightType);
            } else if (this.sortedIndices.has(index)) {
                bar.classList.add('sorted');
            }

            this.container.appendChild(bar);
        });
    }

    /**
     * Load algorithm steps for visualization
     */
    loadSteps(algorithmResult) {
        this.steps = algorithmResult.steps;
        this.currentStep = 0;
        this.updateTimeComplexity(algorithmResult.timeComplexity);

        // Reset to initial state
        this.sortedIndices.clear();
        this.renderArray();
        this.resetMetrics();

        console.log(`Loaded ${this.steps.length} steps for visualization`);
    }

    /**
     * Execute a single step of the algorithm
     */
    executeStep(stepIndex = null) {
        const step = this.steps[stepIndex ?? this.currentStep];
        if (!step) return false;

        // Update metrics
        this.updateMetrics({
            comparisons: step.comparisons,
            swaps: step.swaps
        });

        // Update array state
        this.array = [...step.array];

        // Handle different step types
        let highlightIndices = step.indices || [];
        let highlightType = 'comparing';

        switch (step.type) {
            case 'compare':
                highlightType = 'comparing';
                break;
            case 'swap':
            case 'shift':
                highlightType = 'swapping';
                break;
            case 'mark_sorted':
            case 'partition_complete':
            case 'place_pivot':
                step.indices.forEach(idx => this.sortedIndices.add(idx));
                highlightType = 'sorted';
                break;
            case 'complete':
                step.indices.forEach(idx => this.sortedIndices.add(idx));
                highlightIndices = [];
                break;
            case 'select':
            case 'select_pivot':
                highlightType = 'comparing';
                break;
            case 'insert':
            case 'place':
                highlightType = 'swapping';
                break;
            default:
                highlightType = 'comparing';
        }

        // Render the updated array
        this.renderArray(highlightIndices, highlightType);

        // Update step description if element exists
        const descriptionElement = document.getElementById('step-description');
        if (descriptionElement && step.description) {
            descriptionElement.textContent = step.description;
        }

        if (stepIndex === null) {
            this.currentStep++;
        }

        return this.currentStep < this.steps.length;
    }

    /**
     * Play the algorithm animation automatically
     */
    async play() {
        if (this.isPlaying) return;

        this.isPlaying = true;

        while (this.currentStep < this.steps.length && this.isPlaying) {
            const hasMoreSteps = this.executeStep();

            if (!hasMoreSteps) {
                this.isPlaying = false;
                break;
            }

            // Wait for animation speed delay
            await this.delay(this.animationSpeed);
        }

        this.isPlaying = false;
    }

    /**
     * Pause the animation
     */
    pause() {
        this.isPlaying = false;
    }

    /**
     * Step forward one step
     */
    stepForward() {
        if (this.currentStep < this.steps.length) {
            this.executeStep();
        }
    }

    /**
     * Step backward one step
     */
    stepBackward() {
        if (this.currentStep > 0) {
            this.currentStep--;
            // Need to rebuild state up to this point
            this.rebuildState(this.currentStep - 1);
        }
    }

    /**
     * Reset to the beginning
     */
    reset() {
        this.pause();
        this.currentStep = 0;
        this.sortedIndices.clear();

        if (this.steps.length > 0) {
            // Reset to initial state
            this.array = [...this.steps[0].array];
            this.renderArray();
            this.resetMetrics();
        }
    }

    /**
     * Jump to a specific step
     */
    jumpToStep(stepNumber) {
        this.pause();
        this.currentStep = Math.max(0, Math.min(stepNumber, this.steps.length));
        this.rebuildState(this.currentStep - 1);
    }

    /**
     * Rebuild the visualization state up to a specific step
     */
    rebuildState(upToStep) {
        this.sortedIndices.clear();

        if (upToStep < 0) {
            // Reset to initial state
            if (this.steps.length > 0) {
                this.array = [...this.steps[0].array];
                this.resetMetrics();
            }
        } else {
            // Replay all steps up to the target step
            for (let i = 0; i <= upToStep && i < this.steps.length; i++) {
                const step = this.steps[i];

                // Update sorted indices for display
                if (['mark_sorted', 'partition_complete', 'place_pivot', 'complete'].includes(step.type)) {
                    step.indices.forEach(idx => this.sortedIndices.add(idx));
                }
            }

            const targetStep = this.steps[upToStep];
            if (targetStep) {
                this.array = [...targetStep.array];
                this.updateMetrics({
                    comparisons: targetStep.comparisons,
                    swaps: targetStep.swaps
                });
            }
        }

        this.renderArray();
    }

    /**
     * Set animation speed (1-10 scale)
     */
    setSpeed(speed) {
        // Convert 1-10 scale to milliseconds (higher number = faster)
        this.animationSpeed = Math.max(50, 1100 - (speed * 100));
    }

    /**
     * Get current progress as percentage
     */
    getProgress() {
        if (this.steps.length === 0) return 0;
        return (this.currentStep / this.steps.length) * 100;
    }

    /**
     * Check if algorithm is complete
     */
    isComplete() {
        return this.currentStep >= this.steps.length;
    }

    /**
     * Utility function to create delays
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get algorithm statistics
     */
    getStats() {
        if (this.steps.length === 0) return null;

        const lastStep = this.steps[this.steps.length - 1];
        return {
            totalSteps: this.steps.length,
            comparisons: lastStep.comparisons,
            swaps: lastStep.swaps,
            arraySize: this.array.length
        };
    }
}

/**
 * Graph Visualizer class for graph algorithm visualization
 */
class GraphVisualizer {
    constructor() {
        this.graph = null;
        this.currentStep = 0;
        this.steps = [];
        this.isPlaying = false;
        this.animationSpeed = 800; // Slower for graph algorithms
        this.container = null;
        this.nodePositions = new Map();
        this.visitedNodes = new Set();
        this.queueNodes = new Set();
        this.currentNode = null;

        this.initializeElements();
    }

    /**
     * Initialize DOM element references
     */
    initializeElements() {
        this.container = document.getElementById('graph-container');
        this.comparisonsDisplay = document.getElementById('comparisons');
        this.swapsDisplay = document.getElementById('swaps');
        this.timeComplexityDisplay = document.getElementById('time-complexity');
    }

    /**
     * Set up a graph for visualization
     */
    setGraph(graph) {
        this.graph = graph;
        this.calculateNodePositions();
        this.renderGraph();
        this.resetMetrics();
    }

    /**
     * Calculate positions for graph nodes using existing coordinates or circular layout
     */
    calculateNodePositions() {
        if (!this.graph) return;

        const nodes = this.graph.getNodes();

        // Use existing node positions if available
        nodes.forEach(nodeId => {
            const nodeData = this.graph.nodes[nodeId];
            if (nodeData && nodeData.x !== undefined && nodeData.y !== undefined) {
                this.nodePositions.set(nodeId, { x: nodeData.x, y: nodeData.y });
            }
        });

        // If no positions were set, use circular layout
        if (this.nodePositions.size === 0) {
            const centerX = 300;
            const centerY = 200;
            const radius = 120;

            nodes.forEach((node, index) => {
                const angle = (2 * Math.PI * index) / nodes.length;
                const x = centerX + radius * Math.cos(angle);
                const y = centerY + radius * Math.sin(angle);
                this.nodePositions.set(node, { x, y });
            });
        }
    }

    /**
     * Render the graph visualization
     */
    renderGraph(highlightedNodes = [], highlightedEdges = []) {
        if (!this.container || !this.graph) return;

        this.container.innerHTML = '';

        // Create SVG element
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '600');
        svg.setAttribute('height', '400');
        svg.setAttribute('class', 'graph-svg');

        // Draw edges first (so they appear behind nodes)
        const edges = this.graph.getEdges();
        edges.forEach(edge => {
            const fromPos = this.nodePositions.get(edge.from);
            const toPos = this.nodePositions.get(edge.to);

            if (fromPos && toPos) {
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', fromPos.x);
                line.setAttribute('y1', fromPos.y);
                line.setAttribute('x2', toPos.x);
                line.setAttribute('y2', toPos.y);
                line.setAttribute('class', 'graph-edge');

                // Highlight specific edges
                if (highlightedEdges.some(hEdge =>
                    (hEdge.from === edge.from && hEdge.to === edge.to) ||
                    (hEdge.from === edge.to && hEdge.to === edge.from)
                )) {
                    line.classList.add('highlighted');
                }

                svg.appendChild(line);

                // Add edge weight if it exists and is not 1
                if (edge.weight && edge.weight !== 1) {
                    const midX = (fromPos.x + toPos.x) / 2;
                    const midY = (fromPos.y + toPos.y) / 2;

                    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    text.setAttribute('x', midX);
                    text.setAttribute('y', midY - 5);
                    text.setAttribute('class', 'edge-weight');
                    text.setAttribute('text-anchor', 'middle');
                    text.textContent = edge.weight;
                    svg.appendChild(text);
                }
            }
        });

        // Draw nodes
        const nodes = this.graph.getNodes();
        nodes.forEach(node => {
            const pos = this.nodePositions.get(node);
            if (!pos) return;

            // Node circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', pos.x);
            circle.setAttribute('cy', pos.y);
            circle.setAttribute('r', '25');
            circle.setAttribute('class', 'graph-node');

            // Apply node states
            if (this.currentNode === node) {
                circle.classList.add('current');
            } else if (this.visitedNodes.has(node)) {
                circle.classList.add('visited');
            } else if (this.queueNodes.has(node)) {
                circle.classList.add('queued');
            }

            if (highlightedNodes.includes(node)) {
                circle.classList.add('highlighted');
            }

            svg.appendChild(circle);

            // Node label
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', pos.x);
            text.setAttribute('y', pos.y + 5);
            text.setAttribute('class', 'graph-node-label');
            text.setAttribute('text-anchor', 'middle');
            text.textContent = node;
            svg.appendChild(text);
        });

        this.container.appendChild(svg);
    }

    /**
     * Reset all metrics and visual states
     */
    resetMetrics() {
        this.visitedNodes.clear();
        this.queueNodes.clear();
        this.currentNode = null;
        this.updateMetrics({ nodesVisited: 0, edgesExplored: 0 });
    }

    /**
     * Update metrics display for graph algorithms
     */
    updateMetrics(metrics) {
        if (this.comparisonsDisplay) {
            this.comparisonsDisplay.textContent = metrics.nodesVisited || 0;
        }
        if (this.swapsDisplay) {
            this.swapsDisplay.textContent = metrics.edgesExplored || 0;
        }
    }

    /**
     * Update time complexity display
     */
    updateTimeComplexity(complexity) {
        if (this.timeComplexityDisplay) {
            this.timeComplexityDisplay.textContent = complexity;
        }
    }

    /**
     * Load algorithm steps for visualization
     */
    loadSteps(algorithmResult) {
        this.steps = algorithmResult.steps;
        this.currentStep = 0;
        this.updateTimeComplexity(algorithmResult.timeComplexity);

        // Reset to initial state
        this.resetMetrics();
        this.renderGraph();

        console.log(`Loaded ${this.steps.length} graph algorithm steps for visualization`);
    }

    /**
     * Execute a single step of the graph algorithm
     */
    executeStep(stepIndex = null) {
        const step = this.steps[stepIndex ?? this.currentStep];
        if (!step) return false;

        // Update metrics
        this.updateMetrics({
            nodesVisited: step.visited ? step.visited.size : 0,
            edgesExplored: step.edgesExplored || 0
        });

        // Handle different step types
        let highlightedNodes = [];
        let highlightedEdges = [];

        switch (step.type) {
            case 'initialize':
                this.currentNode = step.currentNode;
                this.queueNodes = new Set(step.queue);
                highlightedNodes = [step.currentNode];
                break;

            case 'visit':
                this.currentNode = step.currentNode;
                this.visitedNodes = new Set(step.visited);
                this.queueNodes = new Set(step.queue);
                highlightedNodes = [step.currentNode];
                break;

            case 'discover':
                this.currentNode = step.currentNode;
                this.queueNodes = new Set(step.queue);
                highlightedNodes = [step.currentNode, step.discoveredNode];
                highlightedEdges = [{ from: step.currentNode, to: step.discoveredNode }];
                break;

            case 'explore_complete':
                this.currentNode = step.currentNode;
                this.visitedNodes = new Set(step.visited);
                this.queueNodes = new Set(step.queue);
                break;

            case 'relax':
                this.currentNode = step.currentNode;
                highlightedNodes = [step.currentNode, step.neighbor];
                highlightedEdges = [{ from: step.currentNode, to: step.neighbor }];
                break;

            case 'target_reached':
                this.currentNode = step.currentNode;
                highlightedNodes = [step.currentNode];
                break;

            case 'complete':
                this.visitedNodes = new Set(step.visited || []);
                this.currentNode = null;
                this.queueNodes.clear();
                break;
        }

        // Render the updated graph
        this.renderGraph(highlightedNodes, highlightedEdges);

        // Update step description if element exists
        const descriptionElement = document.getElementById('step-description');
        if (descriptionElement && step.description) {
            descriptionElement.textContent = step.description;
        }

        if (stepIndex === null) {
            this.currentStep++;
        }

        return this.currentStep < this.steps.length;
    }

    /**
     * Play the algorithm animation automatically
     */
    async play() {
        if (this.isPlaying) return;

        this.isPlaying = true;

        while (this.currentStep < this.steps.length && this.isPlaying) {
            const hasMoreSteps = this.executeStep();

            if (!hasMoreSteps) {
                this.isPlaying = false;
                break;
            }

            // Wait for animation speed delay
            await this.delay(this.animationSpeed);
        }

        this.isPlaying = false;
    }

    /**
     * Pause the animation
     */
    pause() {
        this.isPlaying = false;
    }

    /**
     * Step forward one step
     */
    stepForward() {
        if (this.currentStep < this.steps.length) {
            this.executeStep();
        }
    }

    /**
     * Reset to the beginning
     */
    reset() {
        this.pause();
        this.currentStep = 0;
        this.resetMetrics();

        if (this.steps.length > 0) {
            this.renderGraph();
        }
    }

    /**
     * Set animation speed (1-10 scale)
     */
    setSpeed(speed) {
        // Convert 1-10 scale to milliseconds (higher number = faster)
        this.animationSpeed = Math.max(100, 1200 - (speed * 100));
    }

    /**
     * Utility function to create delays
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Check if algorithm is complete
     */
    isComplete() {
        return this.currentStep >= this.steps.length;
    }
}

// Create global visualizer instances
let visualizer = null;
let graphVisualizer = null;
let currentVisualizationType = 'array'; // 'array' or 'graph'

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    visualizer = new AlgorithmVisualizer();
    graphVisualizer = new GraphVisualizer();

    // Generate initial random array
    visualizer.generateRandomArray(20);
});