/**
 * Graph Visualization System
 * Handles rendering and animating graph algorithms for educational purposes
 */

class GraphVisualizer {
    constructor(canvasId, width = 800, height = 600) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = width;
        this.canvas.height = height;

        this.graph = null;
        this.currentStep = 0;
        this.animationSteps = [];
        this.isAnimating = false;

        // Visual constants
        this.NODE_RADIUS = 15;
        this.NODE_COLORS = {
            default: '#e3f2fd',
            start: '#4caf50',
            end: '#f44336',
            visited: '#2196f3',
            current: '#ff9800',
            path: '#9c27b0',
            frontier: '#ffeb3b'
        };
        this.EDGE_COLOR = '#666';
        this.PATH_COLOR = '#9c27b0';
        this.TEXT_COLOR = '#333';

        // Interaction state
        this.selectedNodes = { start: null, end: null };
        this.setupInteraction();
    }

    /**
     * Set the graph to visualize
     * @param {Graph} graph - Graph instance to visualize
     */
    setGraph(graph) {
        this.graph = graph;
        this.selectedNodes = { start: null, end: null };
        this.currentStep = 0;
        this.animationSteps = [];
        this.draw();
    }

    /**
     * Set animation steps from algorithm execution
     * @param {Array} steps - Steps array from pathfinding algorithm
     */
    setAnimationSteps(steps) {
        this.animationSteps = steps;
        this.currentStep = 0;
    }

    /**
     * Setup mouse interaction for selecting start/end nodes
     */
    setupInteraction() {
        this.canvas.addEventListener('click', (event) => {
            if (this.isAnimating) return;

            const rect = this.canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            // Find clicked node
            const clickedNode = this.findNodeAt(x, y);
            if (clickedNode) {
                this.handleNodeClick(clickedNode);
                this.draw();
            }
        });

        // Visual feedback on hover
        this.canvas.addEventListener('mousemove', (event) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            const hoveredNode = this.findNodeAt(x, y);
            this.canvas.style.cursor = hoveredNode ? 'pointer' : 'default';
        });
    }

    /**
     * Find node at given coordinates
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @returns {string|null} Node ID if found, null otherwise
     */
    findNodeAt(x, y) {
        if (!this.graph) return null;

        for (const [nodeId, node] of this.graph.nodes) {
            const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
            if (distance <= this.NODE_RADIUS) {
                return nodeId;
            }
        }
        return null;
    }

    /**
     * Handle node click for start/end selection
     * @param {string} nodeId - ID of clicked node
     */
    handleNodeClick(nodeId) {
        if (!this.selectedNodes.start) {
            this.selectedNodes.start = nodeId;
        } else if (!this.selectedNodes.end && nodeId !== this.selectedNodes.start) {
            this.selectedNodes.end = nodeId;
        } else {
            // Reset selection
            this.selectedNodes = { start: null, end: null };
            this.selectedNodes.start = nodeId;
        }
    }

    /**
     * Main drawing function
     */
    draw() {
        if (!this.graph) return;

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw edges first (so they appear behind nodes)
        this.drawEdges();

        // Draw nodes
        this.drawNodes();

        // Draw step information if animating
        if (this.animationSteps.length > 0 && this.currentStep < this.animationSteps.length) {
            this.drawStepInfo();
        }
    }

    /**
     * Draw all edges
     */
    drawEdges() {
        const drawnEdges = new Set();

        for (const [edgeKey, edge] of this.graph.edges) {
            // Avoid drawing duplicate edges in undirected graphs
            const reverseKey = `${edge.to}-${edge.from}`;
            if (drawnEdges.has(reverseKey)) continue;
            drawnEdges.add(edgeKey);

            const fromNode = this.graph.nodes.get(edge.from);
            const toNode = this.graph.nodes.get(edge.to);

            if (fromNode && toNode) {
                this.drawEdge(fromNode, toNode, edge.weight);
            }
        }
    }

    /**
     * Draw a single edge
     * @param {Object} fromNode - Source node
     * @param {Object} toNode - Target node
     * @param {number} weight - Edge weight
     */
    drawEdge(fromNode, toNode, weight) {
        this.ctx.strokeStyle = this.EDGE_COLOR;
        this.ctx.lineWidth = 1;

        this.ctx.beginPath();
        this.ctx.moveTo(fromNode.x, fromNode.y);
        this.ctx.lineTo(toNode.x, toNode.y);
        this.ctx.stroke();

        // Draw weight if > 1
        if (weight > 1) {
            const midX = (fromNode.x + toNode.x) / 2;
            const midY = (fromNode.y + toNode.y) / 2;

            this.ctx.fillStyle = '#fff';
            this.ctx.fillRect(midX - 8, midY - 8, 16, 16);

            this.ctx.fillStyle = this.TEXT_COLOR;
            this.ctx.font = '12px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(weight.toString(), midX, midY + 4);
        }
    }

    /**
     * Draw all nodes with appropriate colors based on algorithm state
     */
    drawNodes() {
        const currentStep = this.animationSteps[this.currentStep];

        for (const [nodeId, node] of this.graph.nodes) {
            let color = this.NODE_COLORS.default;

            // Determine node color based on algorithm state
            if (nodeId === this.selectedNodes.start) {
                color = this.NODE_COLORS.start;
            } else if (nodeId === this.selectedNodes.end) {
                color = this.NODE_COLORS.end;
            } else if (currentStep) {
                if (currentStep.finalPath && currentStep.finalPath.includes(nodeId)) {
                    color = this.NODE_COLORS.path;
                } else if (currentStep.nodeId === nodeId) {
                    color = this.NODE_COLORS.current;
                } else if (currentStep.visitedNodes && currentStep.visitedNodes.includes(nodeId)) {
                    color = this.NODE_COLORS.visited;
                } else if (currentStep.queueState && currentStep.queueState.includes(nodeId)) {
                    color = this.NODE_COLORS.frontier;
                } else if (currentStep.stackState && currentStep.stackState.includes(nodeId)) {
                    color = this.NODE_COLORS.frontier;
                }
            }

            this.drawNode(node, color);
        }
    }

    /**
     * Draw a single node
     * @param {Object} node - Node to draw
     * @param {string} color - Fill color
     */
    drawNode(node, color) {
        // Draw node circle
        this.ctx.fillStyle = color;
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 2;

        this.ctx.beginPath();
        this.ctx.arc(node.x, node.y, this.NODE_RADIUS, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.stroke();

        // Draw node label
        this.ctx.fillStyle = this.TEXT_COLOR;
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(node.label, node.x, node.y + 4);
    }

    /**
     * Draw step information panel
     */
    drawStepInfo() {
        const step = this.animationSteps[this.currentStep];
        if (!step) return;

        // Draw info panel background
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        this.ctx.fillRect(10, 10, 300, 120);
        this.ctx.strokeStyle = '#ddd';
        this.ctx.strokeRect(10, 10, 300, 120);

        // Draw step information
        this.ctx.fillStyle = this.TEXT_COLOR;
        this.ctx.font = '14px Arial';
        this.ctx.textAlign = 'left';

        let y = 30;
        this.ctx.fillText(`Step: ${this.currentStep + 1}/${this.animationSteps.length}`, 20, y);

        y += 20;
        if (step.type === 'visit') {
            this.ctx.fillText(`Visiting node: ${step.nodeId}`, 20, y);
            y += 15;
            if (step.queueState) {
                this.ctx.fillText(`Queue: [${step.queueState.join(', ')}]`, 20, y);
            } else if (step.stackState) {
                this.ctx.fillText(`Stack: [${step.stackState.join(', ')}]`, 20, y);
            }
            y += 15;
            this.ctx.fillText(`Visited: ${step.visitedNodes.length} nodes`, 20, y);
        } else if (step.type === 'found') {
            this.ctx.fillText(`✓ Path found!`, 20, y);
            y += 15;
            this.ctx.fillText(`Path length: ${step.finalPath.length - 1}`, 20, y);
            y += 15;
            this.ctx.fillText(`Nodes explored: ${step.nodesExplored}`, 20, y);
        } else if (step.type === 'no_path') {
            this.ctx.fillText(`✗ No path exists`, 20, y);
            y += 15;
            this.ctx.fillText(`Nodes explored: ${step.nodesExplored}`, 20, y);
        }
    }

    /**
     * Animation control methods
     */
    nextStep() {
        if (this.currentStep < this.animationSteps.length - 1) {
            this.currentStep++;
            this.draw();
        }
    }

    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.draw();
        }
    }

    resetAnimation() {
        this.currentStep = 0;
        this.draw();
    }

    /**
     * Auto-play animation
     * @param {number} interval - Delay between steps in milliseconds
     */
    playAnimation(interval = 1000) {
        if (this.isAnimating) return;

        this.isAnimating = true;
        const playStep = () => {
            if (this.currentStep < this.animationSteps.length - 1 && this.isAnimating) {
                this.nextStep();
                setTimeout(playStep, interval);
            } else {
                this.isAnimating = false;
            }
        };
        playStep();
    }

    pauseAnimation() {
        this.isAnimating = false;
    }

    /**
     * Check if start and end nodes are selected
     * @returns {boolean} True if both start and end nodes are selected
     */
    isReadyForPathfinding() {
        return this.selectedNodes.start && this.selectedNodes.end;
    }

    /**
     * Get selected start and end nodes
     * @returns {Object} Object with start and end node IDs
     */
    getSelectedNodes() {
        return { ...this.selectedNodes };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GraphVisualizer };
}